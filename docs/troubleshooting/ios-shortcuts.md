# iOS Shortcuts Troubleshooting

Common issues and solutions for setting up iOS Shortcuts with the Schedule Manager.

## Request Body Options Missing

### Problem

In "Get Contents of URL", you don't see a "Text" option for Request Body.

### Solution

#### Method 1: Use "Form" (Recommended)

1. Select **"Form"** from Request Body dropdown
2. Look for a **text/toggle switch** (usually top right of form area)
3. Switch to **text mode**
4. Now you can type plain text: `add: [Provided Input]`

**Visual cue:** After switching, you'll see a plain text field instead of key-value pairs.

#### Method 2: Use "File"

1. Select **"File"** from Request Body dropdown
2. Tap in the file field
3. Select "Text" from content types
4. Type your command: `add: [Provided Input]`

#### Method 3: Use JSON (Workaround)

Less ideal but works:

1. Select **"JSON"**
2. Type: `{"message": "add: [Provided Input]"}`
3. May require adding header: `Content-Type: text/plain`

### Finding Request Body Option

The option might be hidden:

1. Tap **"Show More"** to expand all options
2. Check **"Advanced"** section
3. Look for **three dots (...)** menu

## Siri Not Recognizing Phrase

### Problem

Siri doesn't activate your shortcut when you say the phrase.

### Solutions

1. **Re-record the phrase:**
   - Edit shortcut
   - Tap (i) info button
   - Tap "Siri & Search"
   - Delete old phrase
   - Add new phrase

2. **Try different wording:**
   - Instead of: "Add schedule"
   - Try: "Schedule add" or "New schedule"

3. **Check language:**
   - Siri language must match iOS system language
   - Settings → Siri & Search → Language

4. **Use type instead of speak:**
   - Enable "Type to Siri" in Settings
   - Invoke Siri and type your command

## Variables Not Showing Up

### Problem

Can't find "Provided Input" variable when building shortcut.

### Solutions

1. **Add "Ask for Input" first:**
   - The variable only appears AFTER you add the "Ask for Input" action
   
2. **Insert variable properly:**
   - Long-press in text field
   - Tap "Select Variable"
   - Choose "Provided Input"

3. **Use magic variable button:**
   - Some iOS versions have a dedicated variable button (looks like a pill icon)
   - Tap it to see available variables

## Shortcut Runs But No Response

### Problem

Shortcut executes but you don't get a notification back.

### Troubleshooting Steps

1. **Check ntfy.sh subscription:**
   ```
   Open ntfy.sh app
   → Verify you're subscribed to notification topic (not command topic!)
   → Config uses two topics: command_topic and topic
   ```

2. **Wait a moment:**
   - Processing takes 1-2 seconds
   - Don't immediately assume it failed

3. **Test command manually:**
   ```bash
   curl -d "help" https://ntfy.sh/YOUR_COMMAND_TOPIC
   ```

4. **Check daemon logs:**
   ```bash
   python3 -m schedule_manager.daemon --verbose
   ```

5. **Verify topics in config.yaml:**
   ```yaml
   ntfy:
     topic: "your_notifications_here"  # Where responses are sent
     command_topic: "your_commands_here"  # Where shortcuts send commands
   ```

## Parse Errors / Unrecognized Commands

### Problem

You get "Unknown command" or parse errors.

### Solutions

1. **Check command format:**
   - ✅ Correct: `add: call mom tomorrow at 3pm`
   - ❌ Wrong: `add call mom tomorrow at 3pm` (missing colon)
   - ❌ Wrong: `Add: call mom` (capital A)

2. **Use simpler phrasing:**
   - Instead of: "meeting 3 days from now at sometime"
   - Try: "meeting friday at 2pm"

3. **Test with curl:**
   ```bash
   curl -d "add: test tomorrow at 3pm" https://ntfy.sh/YOUR_COMMAND_TOPIC
   ```

4. **Check rate limiting:**
   - Only 1 command per second allowed
   - Wait between rapid commands

## Apple Watch Shortcuts Not Syncing

### Problem

Shortcuts work on iPhone but not showing on Apple Watch.

### Solutions

1. **Wait for sync:**
   - Can take 5-15 minutes after creating shortcut
   - Restart both devices if needed

2. **Check watch Shortcuts settings:**
   - Open Watch app on iPhone
   - Go to Shortcuts
   - Ensure "Show on Apple Watch" is enabled

3. **Recreate shortcut:**
   - Delete shortcut on iPhone
   - Create again
   - Wait for sync

4. **Use Siri instead:**
   - Even if shortcut doesn't appear in Shortcuts app
   - Siri voice command should still work

## Network / Connection Issues

### Problem

"Could not connect to server" or timeout errors.

### Solutions

1. **Check internet on both devices:**
   - iPhone needs internet to reach ntfy.sh
   - Server needs internet to receive commands

2. **Test ntfy.sh directly:**
   ```bash
   curl https://ntfy.sh
   # Should return ntfy.sh website
   ```

3. **Try different network:**
   - Switch between WiFi and cellular
   - Some corporate networks block ntfy.sh

4. **Check server connectivity:**
   ```bash
   curl https://ntfy.sh/YOUR_TOPIC/json?poll=1
   # Should return recent messages
   ```

## Shortcut Permission Errors

### Problem

"This shortcut cannot be run" or permission denied errors.

### Solutions

1. **Allow untrusted shortcuts:**
   - Settings → Shortcuts
   - Enable "Allow Running Scripts"
   - Enable "Allow Untrusted Shortcuts" (if needed)

2. **Grant network permissions:**
   - First time shortcut runs, iOS asks for permission
   - Tap "Allow" when prompted

3. **Check privacy settings:**
   - Settings → Privacy & Security → Shortcuts
   - Ensure Shortcuts app has necessary permissions

## Task IDs Not Working

### Problem

Commands like `complete: 15` fail with "Task not found".

### Solutions

1. **Get correct task ID:**
   ```bash
   # Start daemon in verbose mode
   python3 -m schedule_manager.daemon --verbose
   
   # Send list command
   curl -d "list" https://ntfy.sh/YOUR_COMMAND_TOPIC
   
   # Task IDs will be in daemon output
   ```

2. **Use OpenCode integration:**
   ```
   Ask OpenCode: "Show me task IDs for today"
   ```

3. **Tasks might have been deleted:**
   - Completed tasks are removed from active list
   - Check if task still exists

## Still Having Issues?

### Debug Mode

Run daemon in verbose mode to see what's happening:

```bash
python3 -m schedule_manager.daemon --verbose
```

Then send a test command and watch the output.

### Test Step-by-Step

1. **Test daemon is listening:**
   ```bash
   ps aux | grep daemon
   ```

2. **Test notification sending:**
   ```python
   python3 -c "from schedule_manager.core import ScheduleManager; ScheduleManager().send_test_notification()"
   ```

3. **Test command processing:**
   ```bash
   python3 test_command_listener.py "help"
   ```

4. **Test iOS shortcut:**
   - Run shortcut manually (not via Siri)
   - Check for errors

### Get Help

If none of these solutions work:

1. **Check daemon logs:**
   ```bash
   tail -f daemon.log
   # or
   journalctl -u schedule-manager -f
   ```

2. **Review configuration:**
   ```bash
   cat config.yaml | grep -A 5 ntfy
   ```

3. **Open an issue:**
   - Include daemon logs
   - Include iOS version
   - Include steps you've tried
   - Include error messages

## Common Misconceptions

❌ **Wrong:** "Shortcut sends command to my notification topic"  
✅ **Right:** "Shortcut sends to `command_topic`, daemon replies to `topic`"

❌ **Wrong:** "I need to subscribe to command topic in ntfy app"  
✅ **Right:** "Subscribe to notification topic only, command topic is for sending"

❌ **Wrong:** "Task IDs are shown in notifications"  
✅ **Right:** "Task IDs are in daemon logs, or use OpenCode integration"

## Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| No response | Check you're subscribed to notification topic |
| Parse error | Check command format (lowercase, colon after command) |
| Siri not working | Re-record Siri phrase |
| Variable missing | Ensure "Ask for Input" is BEFORE URL action |
| Network error | Test: `curl https://ntfy.sh` |
| Permission error | Settings → Shortcuts → Allow Running Scripts |
| Watch not syncing | Wait 15 min, restart both devices |

## Next Steps

- [Voice Commands Guide](../user-guides/voice-commands.md) - Full setup instructions
- [Command Reference](../user-guides/commands.md) - All available commands
- [Common Issues](common-issues.md) - General troubleshooting

---

Still stuck? Check the daemon logs - they usually reveal the issue!
