# Fix Applied for UTF-8/Emoji Encoding Issue

## What Was Fixed

The error you encountered:
```
'latin-1' codec can't encode character '\u2705' in position 0
```

This was caused by the ntfy.sh notification trying to send emojis (like ✅) in HTTP headers, which only support latin-1 encoding.

## The Solution

I've updated `schedule_manager/notifications.py` to use **JSON format** instead of HTTP headers for sending notifications. This properly supports UTF-8 characters including emojis.

### Changes Made:

**Before (using headers):**
```python
headers = {
    "Title": title,  # ❌ Headers don't support UTF-8 emojis
    "Priority": priority,
}
response = requests.post(url, data=message, headers=headers)
```

**After (using JSON):**
```python
payload = {
    "title": title,  # ✅ JSON properly handles UTF-8
    "message": message,
    "priority": priority,
}
response = requests.post(url, json=payload)
```

## How to Test the Fix

On your server at `192.168.1.250`:

### Option 1: Quick Test Script

```bash
cd /home/ngrabbs/notes/schedule-manager
source .venv/bin/activate
python3 test_notification.py
```

This new `test_notification.py` script will:
- Load your config
- Send a test notification with emojis
- Give you clear success/failure feedback

### Option 2: Run the Original Example

```bash
cd /home/ngrabbs/notes/schedule-manager
source .venv/bin/activate
python3 example_usage.py
```

This should now work without the encoding error!

### Option 3: Test Directly in Python

```bash
cd /home/ngrabbs/notes/schedule-manager
source .venv/bin/activate
python3
```

Then in Python:
```python
from schedule_manager.core import ScheduleManager

manager = ScheduleManager()
success = manager.send_test_notification()

if success:
    print("✅ It works! Check your phone!")
else:
    print("❌ Still having issues")
```

## Verify Your Config

Make sure your `config.yaml` has a valid topic (not the default):

```yaml
ntfy:
  server: "https://ntfy.sh"
  topic: "your_actual_unique_topic_here"  # Must be changed!
```

If it still says `your_schedule_topic_changeme`, update it to something unique like:
```bash
# Generate a random topic name
echo "my_schedule_$(openssl rand -hex 8)"
```

## Expected Result

You should see:
```
✅ Success! Message ID: abc123xyz
Check your phone/watch for the notification!
```

And receive a notification on your phone that says:
```
✅ Test Notification
If you see this, your ntfy.sh setup is working! 🎉
```

## If It Still Doesn't Work

1. **Check topic subscription:**
   - Open ntfy.sh app on your phone
   - Make sure you're subscribed to the exact topic in config.yaml

2. **Test ntfy.sh manually:**
   ```bash
   curl -d "Test from curl" ntfy.sh/your_topic_here
   ```
   You should get this notification immediately.

3. **Check network/firewall:**
   ```bash
   curl -I https://ntfy.sh
   ```
   Should return `HTTP/2 200`

4. **Verify Python packages:**
   ```bash
   source .venv/bin/activate
   pip install --upgrade requests pyyaml
   ```

## Next Steps After Fix Works

Once you confirm the test notification works:

1. **Add some tasks:**
   ```bash
   python3 example_usage.py
   ```

2. **Start the daemon:**
   ```bash
   python3 -m schedule_manager.daemon
   ```

3. **Set up MCP for OpenCode** (see README.md)

## Technical Details

The ntfy.sh API supports two methods:

1. **Headers method** (old, doesn't support UTF-8):
   - `Title: My Notification`
   - Limited to ASCII/latin-1

2. **JSON method** (new, full UTF-8 support):
   - `{"title": "✅ My Notification", "message": "🎉"}`
   - Full Unicode support

We're now using the JSON method throughout the codebase.

---

**The fix is applied! Try running `test_notification.py` on your server now.** 🚀
