#!/usr/bin/env python3
"""
Test script for sending commands to the schedule manager via ntfy.sh

Usage:
    python3 test_command_listener.py "add: call mom tomorrow at 3pm"
    python3 test_command_listener.py list
    python3 test_command_listener.py help
"""

import sys
import requests
import yaml
from pathlib import Path


def send_command(command: str, config_path: str = "config.yaml"):
    """
    Send a command to the schedule manager via ntfy.sh
    
    Args:
        command: Command text to send
        config_path: Path to config file
    """
    # Load config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    server = config['ntfy']['server']
    topic = config['ntfy']['commands_topic']
    
    if not topic:
        print("❌ Error: commands_topic not configured in config.yaml")
        sys.exit(1)
    
    url = f"{server}/{topic}"
    
    print(f"📤 Sending command to {topic}")
    print(f"   Command: {command}")
    print()
    
    try:
        response = requests.post(
            url,
            data=command.encode('utf-8'),
            headers={
                'Title': 'Test Command',
                'Priority': 'default'
            }
        )
        response.raise_for_status()
        
        result = response.json()
        message_id = result.get('id')
        
        print(f"✅ Command sent successfully!")
        print(f"   Message ID: {message_id}")
        print()
        print("💡 Check your notifications for the response")
        print("   (Make sure the daemon is running: python3 -m schedule_manager.daemon)")
        
    except Exception as e:
        print(f"❌ Error sending command: {e}")
        sys.exit(1)


def show_examples():
    """Show example commands"""
    print("""
📚 Command Examples:

Add Tasks:
    python3 test_command_listener.py "add: call mom tomorrow at 3pm"
    python3 test_command_listener.py "add: team meeting next monday at 10am for 1 hour"
    python3 test_command_listener.py "add: buy groceries this friday afternoon"

View Schedule:
    python3 test_command_listener.py "list"
    python3 test_command_listener.py "today"

Upcoming Tasks:
    python3 test_command_listener.py "upcoming"
    python3 test_command_listener.py "upcoming 4"

Complete Task:
    python3 test_command_listener.py "complete: 15"
    python3 test_command_listener.py "done: 15"

Delete Task:
    python3 test_command_listener.py "delete: 15"

Reschedule Task:
    python3 test_command_listener.py "reschedule: 15 to 5pm"
    python3 test_command_listener.py "reschedule: 15 to tomorrow at 2pm"

Help:
    python3 test_command_listener.py "help"
    python3 test_command_listener.py "commands"

Quick Test:
    python3 test_command_listener.py test
    """)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python3 test_command_listener.py <command>")
        print()
        show_examples()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command in ['examples', 'example', '--help', '-h']:
        show_examples()
        return
    
    if command == 'test':
        # Quick test command
        command = "help"
        print("Running quick test with 'help' command...")
        print()
    
    send_command(command)


if __name__ == '__main__':
    main()
