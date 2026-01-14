"""
AI Agent manager for intelligent schedule command processing

Manages an OpenCode server instance that provides AI-powered natural language
understanding and conversation context for schedule commands.
"""

import subprocess
import time
import logging
import requests
import signal
from typing import Optional, Dict, Any
from pathlib import Path

from .exceptions import (
    AgentStartupError,
    AgentShutdownError,
    AgentUnavailableError,
    AgentCommunicationError
)

logger = logging.getLogger(__name__)


class ScheduleAgent:
    """
    Manages an OpenCode AI agent server for intelligent schedule processing
    
    The agent:
    - Runs as a persistent subprocess (OpenCode server)
    - Maintains conversation context across commands
    - Provides natural language understanding
    - Routes responses back via ntfy.sh automatically
    """
    
    # System prompt to guide the AI's behavior
    SYSTEM_PROMPT = """You are a scheduling assistant with access to schedule management tools.

IMPORTANT: You must USE the available MCP tools (schedule_add, schedule_view, etc.) to perform actions. Do not just explain what to do - actually call the tools.

When the user asks to add a task, call schedule_add immediately.
When the user asks to view tasks, call schedule_view immediately.
When the user asks to update a task, call schedule_update immediately.

After executing tools, provide a brief confirmation of what was done.

Examples:
- "add call mom tomorrow at 3pm" → Call schedule_add with description
- "view today" → Call schedule_view for today
- "update task 5 to high priority" → Call schedule_update with task_id and priority

Be concise. Execute first, confirm second."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Schedule Agent manager
        
        Args:
            config: Configuration dict with 'agent' section
        """
        self.config = config
        self.agent_config = config.get('agent', {})
        
        # OpenCode server configuration
        self.port = self.agent_config.get('port', 5555)
        self.model = self.agent_config.get('model', 'ollama/llama3.2')
        self.agent_name = self.agent_config.get('agent_name', 'schedule')
        self.startup_timeout = self.agent_config.get('startup_timeout_seconds', 30)
        self.health_check_timeout = self.agent_config.get('health_check_timeout_seconds', 5)
        
        # Process state
        self.process: Optional[subprocess.Popen] = None
        self.base_url = f"http://localhost:{self.port}"
        self.is_running = False
        self.session_id: Optional[str] = None  # OpenCode session ID for conversation context
        
        logger.info(f"Agent manager initialized: port={self.port}, model={self.model}")
    
    def start(self):
        """
        Start the OpenCode agent server
        
        Raises:
            AgentStartupError: If the agent fails to start within timeout
        """
        if self.is_running:
            logger.warning("Agent is already running")
            return
        
        logger.info("Starting OpenCode agent server...")
        logger.info(f"  Port: {self.port}")
        logger.info(f"  Model: {self.model}")
        logger.info(f"  Agent: {self.agent_name}")
        
        try:
            self._spawn_process()
            self._wait_for_ready()
            self.session_id = self._create_session()
            self.is_running = True
            logger.info("✓ OpenCode agent started successfully")
        
        except Exception as e:
            self.is_running = False
            logger.error(f"Failed to start OpenCode agent: {e}", exc_info=True)
            
            # Clean up process if it was started
            if self.process:
                try:
                    self.process.terminate()
                    self.process.wait(timeout=5)
                except:
                    pass
                self.process = None
            
            raise AgentStartupError(f"Failed to start OpenCode agent: {e}")
    
    def stop(self):
        """
        Stop the OpenCode agent server gracefully
        
        Raises:
            AgentShutdownError: If the agent fails to stop cleanly
        """
        if not self.is_running:
            logger.info("Agent is not running, nothing to stop")
            return
        
        logger.info("Stopping OpenCode agent...")
        
        try:
            # Delete the session before stopping server
            if self.session_id:
                try:
                    logger.debug(f"Deleting OpenCode session {self.session_id}...")
                    response = requests.delete(
                        f"{self.base_url}/session/{self.session_id}",
                        timeout=5
                    )
                    if response.status_code == 200:
                        logger.info(f"✓ Deleted session: {self.session_id}")
                    else:
                        logger.warning(f"Session deletion returned status {response.status_code}")
                except Exception as e:
                    logger.warning(f"Failed to delete session: {e}")
                finally:
                    self.session_id = None
            
            if self.process:
                # Try graceful shutdown first
                logger.debug("Sending SIGTERM to OpenCode process...")
                self.process.terminate()
                
                # Wait for process to exit
                try:
                    self.process.wait(timeout=10)
                    logger.info("✓ OpenCode agent stopped gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't stop
                    logger.warning("OpenCode didn't stop gracefully, force killing...")
                    self.process.kill()
                    self.process.wait(timeout=5)
                    logger.info("✓ OpenCode agent killed")
                
                self.process = None
            
            self.is_running = False
        
        except Exception as e:
            logger.error(f"Error stopping agent: {e}", exc_info=True)
            raise AgentShutdownError(f"Failed to stop agent: {e}")
    
    def is_healthy(self) -> bool:
        """
        Check if the OpenCode agent is responding
        
        Returns:
            True if agent is healthy, False otherwise
        """
        if not self.is_running:
            return False
        
        try:
            # Try to ping the agent's health endpoint
            response = requests.get(
                f"{self.base_url}/health",
                timeout=self.health_check_timeout
            )
            return response.status_code == 200
        
        except requests.exceptions.RequestException as e:
            logger.debug(f"Health check failed: {e}")
            return False
    
    def process_command(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a command to the OpenCode agent for processing
        
        Args:
            message: The natural language command
            context: Command context (message_id, timestamp, etc.)
        
        Returns:
            Dict with result information containing the AI's response text
        
        Raises:
            AgentUnavailableError: If agent is not healthy or session not created
            AgentCommunicationError: If communication with agent fails
        """
        # Pre-flight checks
        self._ensure_healthy()
        
        if not self.session_id:
            raise AgentUnavailableError("No active session - agent not properly initialized")
        
        logger.debug(f"Sending command to agent session {self.session_id}: {message[:50]}...")
        
        try:
            # Send message to OpenCode session via HTTP API
            # Using /message endpoint with PromptInput schema
            # Split model string into provider and model ID
            model_parts = self.model.split('/', 1)
            model_config = {
                'providerID': model_parts[0] if len(model_parts) > 1 else 'ollama',
                'modelID': model_parts[1] if len(model_parts) > 1 else model_parts[0]
            }
            
            response = requests.post(
                f"{self.base_url}/session/{self.session_id}/message",
                json={
                    'parts': [
                        {
                            'type': 'text',
                            'text': message
                        }
                    ],
                    'model': model_config,
                    'agent': self.agent_name,
                    'system': self.SYSTEM_PROMPT
                },
                timeout=30  # AI processing can take time
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract text from response parts
            # Response format: { "info": {...}, "parts": [...] }
            response_text = self._extract_text_from_parts(result.get('parts', []))
            
            logger.debug(f"Agent response received ({len(response_text)} chars)")
            
            return {
                'success': True,
                'result': response_text,
                'raw_response': result  # Keep full response for debugging
            }
        
        except requests.exceptions.Timeout:
            logger.error("Agent command timed out after 30 seconds")
            raise AgentCommunicationError("Agent command timed out")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with agent: {e}")
            raise AgentCommunicationError(f"Agent communication failed: {e}")
        
        except Exception as e:
            logger.error(f"Unexpected error processing command: {e}", exc_info=True)
            raise AgentCommunicationError(f"Unexpected error: {e}")
    
    def _ensure_healthy(self):
        """
        Ensure agent is healthy, raise exception if not
        
        Raises:
            AgentUnavailableError: If agent is not healthy
        """
        if not self.is_healthy():
            self.is_running = False
            raise AgentUnavailableError("OpenCode agent is not responding")
    
    def _extract_text_from_parts(self, parts: list) -> str:
        """
        Extract text content from OpenCode response parts
        
        Args:
            parts: List of message parts from OpenCode API response
        
        Returns:
            Concatenated text from all text parts
        """
        text_parts = []
        for part in parts:
            if isinstance(part, dict) and part.get('type') == 'text':
                text_parts.append(part.get('text', ''))
        
        return '\n'.join(text_parts).strip()
    
    def _spawn_process(self):
        """
        Spawn the OpenCode server subprocess
        
        Raises:
            AgentStartupError: If process fails to spawn
        """
        # Build OpenCode command
        # Note: Model and agent are now specified per-request, not at server startup
        cmd = [
            'opencode', 'serve',
            '--port', str(self.port),
            '--hostname', '127.0.0.1'
        ]
        
        logger.debug(f"Spawning OpenCode: {' '.join(cmd)}")
        
        try:
            # Spawn process with output redirected to logs
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            
            logger.info(f"OpenCode process started (PID: {self.process.pid})")
        
        except FileNotFoundError:
            raise AgentStartupError(
                "OpenCode executable not found in PATH. "
                "Is OpenCode installed and accessible?"
            )
        
        except Exception as e:
            raise AgentStartupError(f"Failed to spawn OpenCode process: {e}")
    
    def _wait_for_ready(self):
        """
        Wait for OpenCode to be ready to accept requests
        
        Raises:
            AgentStartupError: If agent doesn't become ready within timeout
        """
        logger.debug(f"Waiting for OpenCode to be ready (timeout: {self.startup_timeout}s)...")
        
        start_time = time.time()
        last_error = None
        
        while time.time() - start_time < self.startup_timeout:
            # Check if process died
            if self.process and self.process.poll() is not None:
                # Process exited
                stdout, stderr = self.process.communicate(timeout=1)
                error_msg = f"OpenCode process exited unexpectedly.\nStderr: {stderr}\nStdout: {stdout}"
                logger.error(error_msg)
                raise AgentStartupError(error_msg)
            
            # Try health check
            try:
                response = requests.get(
                    f"{self.base_url}/health",
                    timeout=2
                )
                if response.status_code == 200:
                    logger.info("✓ OpenCode is ready")
                    return
            
            except requests.exceptions.RequestException as e:
                last_error = str(e)
                logger.debug(f"Not ready yet: {e}")
            
            # Wait a bit before next check
            time.sleep(1)
        
        # Timeout reached
        error_msg = f"OpenCode did not become ready within {self.startup_timeout} seconds"
        if last_error:
            error_msg += f". Last error: {last_error}"
        
        logger.error(error_msg)
        raise AgentStartupError(error_msg)
    
    def _create_session(self) -> str:
        """
        Create a new OpenCode session via HTTP API
        
        Returns:
            str: Session ID for maintaining conversation context
        
        Raises:
            AgentStartupError: If session creation fails
        """
        logger.debug("Creating OpenCode session...")
        
        try:
            # Create session with agent, model, and MCP server connections
            session_config = {
                "title": "Schedule Manager Agent",
                "agent": self.agent_name,  # "schedule" agent
                "model": self.model,  # e.g., "ollama/llama3.2:3b"
                "mcpServers": ["schedule-manager"]  # Connect to our MCP server
            }
            
            logger.debug(f"Session config: {session_config}")
            
            response = requests.post(
                f"{self.base_url}/session",
                json=session_config,
                timeout=10
            )
            
            # Log response for debugging
            if response.status_code != 200:
                logger.error(f"Session creation failed: {response.status_code}")
                logger.error(f"Response body: {response.text}")
            
            response.raise_for_status()
            session_info = response.json()
            session_id = session_info['id']
            
            logger.info(f"✓ Created OpenCode session: {session_id}")
            return session_id
        
        except requests.exceptions.RequestException as e:
            raise AgentStartupError(f"Failed to create session: {e}")
        
        except Exception as e:
            raise AgentStartupError(f"Unexpected error creating session: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the agent
        
        Returns:
            Dict with status information
        """
        return {
            'running': self.is_running,
            'healthy': self.is_healthy() if self.is_running else False,
            'port': self.port,
            'model': self.model,
            'agent': self.agent_name,
            'base_url': self.base_url,
            'session_id': self.session_id,
            'pid': self.process.pid if self.process else None
        }
