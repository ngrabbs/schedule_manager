"""
AI Agent for intelligent schedule command processing using OpenCode CLI

Uses OpenCode CLI in per-command mode instead of server mode for simplicity
and reliability. Each command spawns a fresh OpenCode process with the
schedule agent and MCP tools.
"""

import subprocess
import re
import logging
from typing import Dict, Any

from .exceptions import AgentCommunicationError

logger = logging.getLogger(__name__)


class ScheduleAgent:
    """
    Manages AI-powered schedule command processing via OpenCode CLI
    
    The agent:
    - Runs OpenCode CLI per-command (no persistent server)
    - Uses the 'schedule' agent with schedule-manager MCP tools
    - Parses natural language commands
    - Returns concise results
    """
    
    # Regex to strip ANSI escape codes from output
    ANSI_PATTERN = re.compile(r'\x1b\[[0-9;]*m')
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Schedule Agent
        
        Args:
            config: Configuration dict with 'agent' section
        """
        self.config = config
        self.agent_config = config.get('agent', {})
        
        # CLI configuration
        self.model = self.agent_config.get('model', 'ollama/gpt-oss:120b-128k')
        self.agent_name = self.agent_config.get('agent_name', 'schedule')
        self.command_timeout = self.agent_config.get('command_timeout_seconds', 90)
        
        logger.info(f"Agent initialized: model={self.model}, agent={self.agent_name}, timeout={self.command_timeout}s")
    
    def process_command(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a command using OpenCode CLI
        
        Args:
            message: The natural language command
            context: Command context (message_id, timestamp, etc.)
        
        Returns:
            Dict with 'success' and 'result' keys
        
        Raises:
            AgentCommunicationError: If the CLI command fails
        """
        logger.debug(f"Processing command via CLI: {message[:50]}...")
        
        # Build the OpenCode CLI command
        cmd = [
            'opencode',
            f'--agent={self.agent_name}',
            f'--model={self.model}',
            'run',
            message
        ]
        
        logger.debug(f"Running: {' '.join(cmd[:4])} '{message[:30]}...'")
        
        try:
            # Run the CLI command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.command_timeout
            )
            
            # Combine stdout and stderr (OpenCode writes to both)
            raw_output = result.stdout + result.stderr
            
            # Strip ANSI codes and extract the result
            clean_output = self._strip_ansi(raw_output)
            result_text = self._extract_result(clean_output)
            
            logger.debug(f"CLI completed, result: {result_text[:100]}...")
            
            return {
                'success': True,
                'result': result_text
            }
        
        except subprocess.TimeoutExpired:
            logger.error(f"CLI command timed out after {self.command_timeout} seconds")
            raise AgentCommunicationError(f"Command timed out after {self.command_timeout}s")
        
        except FileNotFoundError:
            logger.error("OpenCode executable not found in PATH")
            raise AgentCommunicationError("OpenCode not found - is it installed?")
        
        except Exception as e:
            logger.error(f"CLI command failed: {e}", exc_info=True)
            raise AgentCommunicationError(f"Command failed: {e}")
    
    def _strip_ansi(self, text: str) -> str:
        """Remove ANSI escape codes from text"""
        return self.ANSI_PATTERN.sub('', text)
    
    def _extract_result(self, output: str) -> str:
        """
        Extract the user-facing result from CLI output
        
        Removes tool call information lines (start with '|') and
        returns just the actual result text.
        
        Args:
            output: Raw CLI output with ANSI codes already stripped
        
        Returns:
            Clean result text
        """
        lines = output.strip().split('\n')
        result_lines = []
        
        for line in lines:
            stripped = line.strip()
            # Skip tool call lines (e.g., "| schedule-manager_schedule_add {...}")
            if stripped.startswith('|'):
                continue
            # Skip empty lines at the start
            if not result_lines and not stripped:
                continue
            result_lines.append(line)
        
        return '\n'.join(result_lines).strip()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the agent
        
        Returns:
            Dict with status information
        """
        return {
            'mode': 'cli',
            'model': self.model,
            'agent': self.agent_name,
            'timeout': self.command_timeout
        }
