# iOS Shortcuts Troubleshooting Guide

## Common Issue: "Request Body" Options

### Problem
In the "Get Contents of URL" action, you see these options:
- JSON
- Form  
- File

But the guides mention "Text" which isn't visible.

### Solution

#### Option 1: Use "Form" (Recommended)

1. Select **"Form"** from the Request Body dropdown
2. You'll see a form-like interface
3. Look for a **text/toggle switch** (usually in the top right)
4. Switch to **text mode**
5. Now you can type plain text like: `add: [variable]`

**Visual cue:** After switching, you should see a plain text field instead of key-value pairs.

#### Option 2: Use "File"

1. Select **"File"** from the Request Body dropdown
2. Tap in the file field
3. Select "Text" from the content types
4. Type your command: `add: [variable]`

#### Option 3: Use JSON (Alternative)

If Form/File don't work, you can use JSON but ntfy.sh expects plain text, so this is less ideal:

1. Select **"JSON"**
2. Type: `{"message": "add: [variable]"}`
3. Add header: `Content-Type: text/plain`

### How to Find "Request Body"

The "Get Contents of URL" action might be collapsed. Look for:

1. **"Show More"** button - Tap it to expand all options
2. **"Advanced"** section - Request Body might be under advanced settings
3. **Three dots (...)** - Some iOS versions hide it in a menu

---

## Working Example: "Add Schedule" Shortcut

### Step-by-Step with Screenshots References

**Step 1: Create Shortcut**
- Open Shortcuts app
- Tap "+" (top right)
- Tap "Add Action"

**Step 2: Add "Ask for Input"**
- Search: "ask for input"
- Tap to add
- Configure:
  - Prompt: `What should I schedule?`
  - Input Type: Text (default)

**Step 3: Add "Get Contents of URL"**
- Tap "+" to add another action
- Search: "get contents"
- Select "Get contents of URL"

**Step 4: Configure URL Action**
- Tap "Show More" to see all options
- **URL**: `https://ntfy.sh/nick_cmd_a1ask10h`
- **Method**: Change to `POST`
- **Request Body**: Select `Form`
- Switch to text mode (toggle/button in the form area)
- **Body content**: 
  1. Type: `add: `
  2. Long-press or tap variable button
  3. Select "Provided Input" from variables
  4. Result should show: `add: [Provided Input icon]`

**Step 5: Add Headers**
- Still in "Get Contents of URL" action
- Scroll to **Headers** section
- Tap "Add new field"
- Select "Add Header"
- Add these two headers:
  - Key: `Title`, Value: `Schedule Command`
  - Key: `Priority`, Value: `default`

**Step 6: Name and Save**
- Tap the shortcut name at top
- Rename to: `Add Schedule`
- Tap "Done"

**Step 7: Add to Siri**
- Tap the (i) info icon
- Tap "Add to Siri"
- Record phrase: "Add schedule"
- Tap "Done"

**Step 8: Test It!**
- Tap the shortcut to run
- Type: "test task tomorrow at 3pm"
- Check your notifications!

---

## Alternative: Testing Without Request Body Issues

If you're having trouble with Request Body, test with a simple GET first:

### Test Shortcut (Verify ntfy.sh works)

1. Create new shortcut
2. Add "Get Contents of URL"
3. URL: `https://ntfy.sh/nick_cmd_a1ask10h`
4. Method: `POST`
5. Skip Request Body entirely
6. Add Headers:
   - `Title`: `Test`
   - `Message`: `hello`
7. Run it

You should see a notification! This confirms connectivity.

---

## Common Errors and Fixes

### Error: "Could not connect to server"

**Causes:**
- No internet connection
- ntfy.sh is down (rare)
- URL is incorrect

**Fix:**
1. Check internet: Open Safari, go to ntfy.sh
2. Verify URL: `https://ntfy.sh/nick_cmd_a1ask10h` (no trailing slash)
3. Try in browser first: Visit the URL

### Error: "400 Bad Request"

**Causes:**
- Request Body format wrong
- Headers missing

**Fix:**
1. Use **Form** request body, text mode
2. Make sure URL is exact: `https://ntfy.sh/nick_cmd_a1ask10h`
3. Headers are optional, but can help

### Error: No notification received

**Causes:**
- Daemon not running
- Wrong topic
- Not subscribed in ntfy.sh app

**Fix:**
1. Check daemon:
   ```bash
   ps aux | grep daemon
   ```

2. Verify topic in ntfy.sh app:
   - Open ntfy.sh app
   - Subscribe to: `nick_testing_12345` (notifications topic)
   - Subscribe to: `nick_cmd_a1ask10h` (optional, for debugging)

3. Test manually:
   ```bash
   curl -d "help" https://ntfy.sh/nick_cmd_a1ask10h
   ```

### Shortcut runs but nothing happens

**Causes:**
- Daemon not processing commands
- Wrong commands topic in config

**Fix:**
1. Check daemon logs:
   ```bash
   python3 -m schedule_manager.daemon --verbose
   ```
   Look for: "Voice commands enabled on topic: nick_cmd_a1ask10h"

2. Verify config.yaml:
   ```yaml
   commands_topic: "nick_cmd_a1ask10h"
   commands_enabled: true
   ```

3. Send test command from terminal:
   ```bash
   python3 test_command_listener.py "help"
   ```

---

## iOS Version Differences

### iOS 16 and newer
- Request Body options: JSON, Form, File
- Use **Form** with text mode toggle

### iOS 15
- Request Body options: JSON, Form, File
- Form has key-value pairs by default
- Look for text mode switch

### iOS 14
- May have "Text" directly in dropdown
- If not, use Form or File

### iOS 17/18
- Enhanced interface
- Form mode has clear "Text" toggle button
- Best experience

---

## Video Guide Alternative

If you prefer visual learning:

1. Record yourself setting up a working shortcut
2. Or search YouTube for: "iOS Shortcuts POST request with text body"
3. The concepts are the same, just adapt to ntfy.sh URL

---

## Working Alternative: Using Shortcuts URL Scheme

If "Get Contents of URL" is too confusing, you can use the ntfy.sh app directly:

### Method: Open URL to ntfy.sh

1. Add action: "Ask for Input"
2. Add action: "Open URL"
3. URL: `ntfy://ntfy.sh/nick_cmd_a1ask10h?message=add: [Provided Input]`

**Note:** This requires the ntfy.sh app and might not work on all versions.

---

## Still Stuck?

### Quick Debug Checklist

- [ ] Daemon is running: `ps aux | grep daemon`
- [ ] Config has correct topic: `cat config.yaml | grep commands_topic`
- [ ] Can send via curl: `curl -d "help" https://ntfy.sh/nick_cmd_a1ask10h`
- [ ] Receive notification from curl test
- [ ] Shortcuts URL is exact: `https://ntfy.sh/nick_cmd_a1ask10h`
- [ ] Request Body is set to Form (text mode)
- [ ] No typos in command format: `add: task description`

### Test Commands

```bash
# Test 1: Send via curl
curl -d "help" https://ntfy.sh/nick_cmd_a1ask10h

# Test 2: Send via Python script
python3 test_command_listener.py "help"

# Test 3: Check daemon logs
python3 -m schedule_manager.daemon --verbose
```

If tests 1 and 2 work but Shortcuts doesn't, the issue is in the Shortcuts configuration.

---

## Contact for Help

If you're still having issues:

1. Take a screenshot of your shortcut configuration
2. Copy the error message (if any)
3. Try the manual curl command
4. Check daemon logs for clues

The most common issue is the Request Body format - using **Form** with text mode should work on all modern iOS versions!
