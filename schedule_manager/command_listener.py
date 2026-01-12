"""
Command listener that subscribes to ntfy.sh for inbound commands
"""

import requests
import json
import time
import logging
import threading
from typing import Optional, Callable
from datetime import datetime
from urllib.parse import unquote

logger = logging.getLogger(__name__)


class CommandListener:
    def __init__(
        self,
        server: str,
        topic: str,
        on_command: Callable[[str, dict], None],
        enabled: bool = True
    ):
        """
        Initialize command listener
        
        Args:
            server: ntfy.sh server URL (e.g., "https://ntfy.sh")
            topic: Topic to subscribe to for commands
            on_command: Callback function(message: str, metadata: dict)
            enabled: Whether listening is enabled
        """
        self.server = server.rstrip('/')
        self.topic = topic
        self.on_command = on_command
        self.enabled = enabled
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # Reconnection settings
        self.reconnect_delay = 1  # Start with 1 second
        self.max_reconnect_delay = 60  # Max 60 seconds
        self.reconnect_backoff = 2  # Exponential backoff multiplier
        
        logger.info(f"Command listener initialized for topic: {topic}")
    
    def start(self):
        """Start listening for commands in a background thread"""
        if not self.enabled:
            logger.info("Command listener is disabled, not starting")
            return
        
        if self.running:
            logger.warning("Command listener already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        
        logger.info(f"Command listener started for topic: {self.topic}")
    
    def stop(self):
        """Stop listening for commands"""
        if not self.running:
            return
        
        logger.info("Stopping command listener...")
        self.running = False
        
        if self.thread:
            # Give it a moment to stop gracefully
            self.thread.join(timeout=5)
        
        logger.info("Command listener stopped")
    
    def _clean_message(self, message: str) -> str:
        """
        Clean up message from various iOS Shortcuts encoding formats
        
        Handles:
        - URL-encoded with '=' prefix: =add%3A+reminder
        - JSON wrapped: {"":"add: reminder"}
        - Plain text: add: reminder (no change)
        """
        # Remove leading '=' (from Form method)
        if message.startswith('='):
            message = message[1:]
        
        # URL decode (Form method encodes special characters)
        if '%' in message or '+' in message:
            message = unquote(message.replace('+', ' '))
        
        # Check if wrapped in JSON object (JSON method)
        if message.startswith('{') and message.endswith('}'):
            try:
                parsed = json.loads(message)
                # If it's {"":"command"}, extract the value
                if isinstance(parsed, dict) and len(parsed) == 1:
                    message = list(parsed.values())[0]
            except json.JSONDecodeError:
                pass  # Not valid JSON, use as-is
        
        return message.strip()
    
    def _listen_loop(self):
        """Main listening loop with automatic reconnection"""
        consecutive_failures = 0
        
        while self.running:
            try:
                logger.info(f"Connecting to ntfy.sh topic: {self.topic}")
                self._listen_stream()
                
                # If we get here, connection closed cleanly
                consecutive_failures = 0
                self.reconnect_delay = 1
                
                if self.running:
                    logger.info("Connection closed, reconnecting in 1 second...")
                    time.sleep(1)
            
            except Exception as e:
                consecutive_failures += 1
                
                if self.running:
                    # Calculate backoff delay
                    delay = min(
                        self.reconnect_delay * (self.reconnect_backoff ** (consecutive_failures - 1)),
                        self.max_reconnect_delay
                    )
                    
                    logger.error(
                        f"Error in command listener (attempt {consecutive_failures}): {e}",
                        exc_info=True if consecutive_failures == 1 else False
                    )
                    logger.info(f"Reconnecting in {delay:.1f} seconds...")
                    
                    time.sleep(delay)
    
    def _listen_stream(self):
        """Listen to the ntfy.sh stream"""
        url = f"{self.server}/{self.topic}/json"
        
        # Use streaming with keepalive
        # ntfy.sh sends keepalive messages every 30s, so timeout at 70s
        with requests.get(url, stream=True, timeout=70) as response:
            response.raise_for_status()
            
            logger.info(f"Connected to ntfy.sh, listening for commands...")
            
            for line in response.iter_lines():
                if not self.running:
                    break
                
                if not line:
                    continue
                
                try:
                    # Parse JSON message
                    data = json.loads(line)
                    
                    # Filter out keepalive messages
                    event_type = data.get('event')
                    if event_type == 'keepalive':
                        logger.debug("Received keepalive")
                        continue
                    
                    if event_type != 'message':
                        logger.debug(f"Ignoring event type: {event_type}")
                        continue
                    
                    # Extract message
                    message = data.get('message', '').strip()
                    
                    if not message:
                        logger.debug("Received empty message, ignoring")
                        continue
                    
                    # Clean up message from various iOS Shortcuts formats
                    raw_message = message
                    message = self._clean_message(message)
                    
                    if message != raw_message:
                        logger.debug(f"Cleaned message: '{raw_message}' -> '{message}'")
                    
                    # Clean up message from various iOS Shortcuts formats
                    message = self._clean_message(message)
                    
                    # Extract metadata
                    metadata = {
                        'id': data.get('id'),
                        'time': data.get('time'),
                        'title': data.get('title'),
                        'tags': data.get('tags', []),
                        'priority': data.get('priority', 3)
                    }
                    
                    logger.info(f"Received command: {message[:50]}... (id: {metadata.get('id')})")
                    
                    # Call the command handler
                    try:
                        self.on_command(message, metadata)
                    except Exception as e:
                        logger.error(f"Error in command handler: {e}", exc_info=True)
                
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON: {e}")
                    logger.debug(f"Raw line: {line}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}", exc_info=True)
    
    def is_running(self) -> bool:
        """Check if listener is running"""
        return bool(self.running and self.thread and self.thread.is_alive())
    
    def get_status(self) -> dict:
        """Get listener status information"""
        return {
            'enabled': self.enabled,
            'running': self.running,
            'alive': self.is_running(),
            'topic': self.topic,
            'server': self.server
        }
