"""
IP address monitoring module
Checks public IP address and sends notifications on changes
"""

import requests
import logging
from datetime import datetime
from typing import Optional
from .database import Database
from .notifications import NtfyNotifier

logger = logging.getLogger(__name__)


class IPMonitor:
    def __init__(self, database: Database, notifier: NtfyNotifier):
        """
        Initialize IP monitor
        
        Args:
            database: Database instance for storing IP history
            notifier: NtfyNotifier instance for sending change notifications
        """
        self.db = database
        self.notifier = notifier
        
        # Services to try (with fallback)
        # Using multiple services for reliability
        self.services = [
            'https://api.ipify.org',
            'https://ifconfig.me/ip',
            'https://icanhazip.com'
        ]
        
        # Request timeout in seconds
        self.timeout = 10
    
    def get_public_ip(self) -> Optional[str]:
        """
        Fetch current public IP address
        Tries multiple services with fallback
        
        Returns:
            IP address string or None if all services fail
        """
        for service_url in self.services:
            try:
                logger.debug(f"Fetching IP from {service_url}")
                response = requests.get(service_url, timeout=self.timeout)
                response.raise_for_status()
                
                ip_address = response.text.strip()
                
                # Basic validation (simple IPv4/IPv6 check)
                if ip_address and ('.' in ip_address or ':' in ip_address):
                    logger.debug(f"Successfully fetched IP: {ip_address}")
                    return ip_address
                else:
                    logger.warning(f"Invalid IP format from {service_url}: {ip_address}")
                    continue
                    
            except requests.exceptions.Timeout:
                logger.debug(f"Timeout fetching from {service_url}, trying next service")
                continue
            except requests.exceptions.RequestException as e:
                logger.debug(f"Error fetching from {service_url}: {e}, trying next service")
                continue
            except Exception as e:
                logger.debug(f"Unexpected error with {service_url}: {e}, trying next service")
                continue
        
        # All services failed
        logger.debug("All IP services failed, will retry on next check")
        return None
    
    def check_and_notify(self):
        """
        Main monitoring logic:
        1. Fetch current public IP
        2. Compare with last known IP
        3. If changed, save to DB and send notification
        4. If same or fetch failed, do nothing (silent)
        """
        try:
            # Fetch current IP
            current_ip = self.get_public_ip()
            
            if current_ip is None:
                # Failed to fetch IP, skip silently
                return
            
            # Get last known IP from database
            last_ip = self.db.get_current_ip()
            
            # Check if IP changed (or first run)
            if last_ip is None:
                # First run, save IP but don't notify (just initialize)
                now = datetime.now()
                self.db.save_ip_address(current_ip, now)
                logger.info(f"✓ Initial IP recorded: {current_ip}")
                print(f"✓ Initial IP recorded: {current_ip}")
                
                # Send initial notification
                self.notifier.send_ip_change_notification(
                    new_ip=current_ip,
                    old_ip=None
                )
                
            elif last_ip != current_ip:
                # IP changed! Save and notify
                now = datetime.now()
                self.db.save_ip_address(current_ip, now)
                logger.info(f"✓ IP changed: {last_ip} → {current_ip}")
                print(f"✓ IP changed: {last_ip} → {current_ip}")
                
                # Send notification
                self.notifier.send_ip_change_notification(
                    new_ip=current_ip,
                    old_ip=last_ip
                )
            else:
                # IP unchanged, silent (no logging)
                pass
                
        except Exception as e:
            # Log error but don't crash
            logger.error(f"Error in IP monitoring: {e}", exc_info=True)
