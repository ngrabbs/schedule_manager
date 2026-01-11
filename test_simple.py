#!/usr/bin/env python3
"""
Minimal test to debug ntfy.sh
"""
import requests

# Test 1: Simple notification without emojis
print("Test 1: Simple notification (no emojis)")
response = requests.post(
    'https://ntfy.sh/nick_testing_12345',
    data='This is a test message'.encode('utf-8'),
    headers={
        'Title': 'Simple Test',
        'Priority': 'default'
    }
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"✅ Success: {response.json()['id']}")
else:
    print(f"❌ Failed: {response.text}")

print()

# Test 2: With emojis in message body only
print("Test 2: Emoji in message body")
response = requests.post(
    'https://ntfy.sh/nick_testing_12345',
    data='This message has emojis ✅ 🎉'.encode('utf-8'),
    headers={
        'Title': 'Test with Emoji Body',
        'Priority': 'default'
    }
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"✅ Success: {response.json()['id']}")
else:
    print(f"❌ Failed: {response.text}")

print()

# Test 3: With emojis in title using our notification wrapper
print("Test 3: Emoji in title (using our smart handler)")
try:
    import sys
    sys.path.insert(0, '.')
    from schedule_manager.notifications import NtfyNotifier
    
    notifier = NtfyNotifier(
        server='https://ntfy.sh',
        topic='nick_testing_12345',
        priority_map={'low': 'default'}
    )
    
    message_id = notifier.send_notification(
        title='✅ Test with Emoji Title',
        message='Message body here',
        priority='low',
        tags=['white_check_mark']
    )
    
    if message_id:
        print(f"✅ Success: {message_id}")
        print("\nCheck your phone - all three notifications should appear!")
        print("\nNote: The emoji from the title appears at the start of the message body.")
        print("This is because HTTP headers don't support UTF-8 emojis (protocol limitation).")
    else:
        print(f"❌ Failed to send")
except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()
