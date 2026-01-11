#!/usr/bin/env python3
"""
Quick test script to verify ntfy.sh notifications work
"""

import sys
import yaml

# Add the parent directory to path so we can import schedule_manager
sys.path.insert(0, '.')

from schedule_manager.notifications import NtfyNotifier

def main():
    print("=" * 60)
    print("Testing ntfy.sh Notification")
    print("=" * 60)
    
    # Load config
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Error loading config.yaml: {e}")
        return
    
    # Get ntfy config
    ntfy_config = config.get('ntfy', {})
    server = ntfy_config.get('server', 'https://ntfy.sh')
    topic = ntfy_config.get('topic', '')
    
    if not topic or topic == 'your_schedule_topic_changeme':
        print("❌ Please update your ntfy topic in config.yaml!")
        print("   Change 'your_schedule_topic_changeme' to something unique")
        return
    
    print(f"Server: {server}")
    print(f"Topic: {topic}")
    print()
    
    # Create notifier
    notifier = NtfyNotifier(
        server=server,
        topic=topic,
        priority_map=ntfy_config.get('priority', {})
    )
    
    # Send test notification
    print("Sending test notification with emojis...")
    message_id = notifier.send_notification(
        title="✅ Test Notification",
        message="If you see this, your ntfy.sh setup is working! 🎉",
        priority='low',
        tags=["white_check_mark", "rocket"]
    )
    
    if message_id:
        print(f"✅ Success! Message ID: {message_id}")
        print()
        print("Check your phone/watch for the notification!")
        print()
        print("If you don't see it:")
        print("1. Open the ntfy.sh app")
        print(f"2. Subscribe to topic: {topic}")
        print("3. Run this test again")
    else:
        print("❌ Failed to send notification")
        print()
        print("Troubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify the ntfy.sh server is accessible")
        print("3. Check config.yaml settings")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
