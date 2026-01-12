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
            Dict with result information
        
        Raises:
            AgentUnavailableError: If agent is not healthy
            AgentCommunicationError: If communication with agent fails
        """
        # Pre-flight health check
        self._ensure_healthy()
        
        logger.debug(f"Sending command to agent: {message[:50]}...")
        
        try:
            # Send command to OpenCode agent API
            response = requests.post(
                f"{self.base_url}/command",
                json={
                    'message': message,
                    'context': context
                },
                timeout=30  # AI processing can take time
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.debug(f"Agent response received: {result.get('status', 'unknown')}")
            
            return {
                'success': True,
                'result': result
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
    
    def _spawn_process(self):
        """
        Spawn the OpenCode server subprocess
        
        Raises:
            AgentStartupError: If process fails to spawn
        """
        # Build OpenCode command
        cmd = [
            'opencode',
            '--port', str(self.port),
            '--model', self.model,
            '--agent', self.agent_name,
            'serve'
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
            'pid': self.process.pid if self.process else None
        }
