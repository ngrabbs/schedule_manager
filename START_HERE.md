# 🎯 START HERE: Quick Setup for Voice Commands

## Your Setup

**Commands Topic:** `nick_cmd_a1ask10h` (keep secret!)  
**Notification Topic:** `nick_testing_12345`

---

## Step 1: Test the System (2 minutes)

First, make sure everything works:

```bash
# Start the daemon if not running
python3 -m schedule_manager.daemon --verbose

# In another terminal, send a test command
python3 test_command_listener.py "help"
```

✅ **You should receive a notification** with available commands!

If this works, move to Step 2. If not, check the daemon logs.

---

## Step 2: iOS Shortcuts Setup (5 minutes)

### ✅ GOOD NEWS: Both Methods Now Work!

The system now automatically decodes iOS Shortcuts messages, so **both methods work**:

**You have TWO options:**

### Option A: Use Headers (Easier!) ⭐ Recommended

This avoids the Form complexity entirely:

1. Create shortcut → Add "Get Contents of URL"
2. URL: `https://ntfy.sh/nick_cmd_a1ask10h`
3. Method: `POST`
4. **Headers** (tap + to add):
   - Key: `Message`, Value: `help` (for testing)
   - Key: `Title`, Value: `Test`
5. **Request Body**: Form with 0 items (leave empty!)

Test this first! You should get a notification.

### Option B: Use Form with File Type

If you prefer using Request Body:

1. Request Body: Select `Form`
2. Tap `+` to add a row
3. Fill in:
   - **Key**: (leave empty or anything)
   - **Type**: Select **"File"**
   - **Value**: Type your command (e.g., `add: [Ask for Input]`)

**Note:** The system now automatically handles URL encoding from Form mode!

### Option C: Even Easier - Just Use JSON!

Actually, the simplest method:

1. Request Body: Select `JSON`
2. Type your command directly: `add: [Ask for Input]`
3. That's it!

The system will extract your command from the JSON wrapper automatically.

---

## Step 3: Build Your Shortcuts

Once testing works, create these shortcuts using **Option A** (Headers method):

### Shortcut 1: "Add Schedule"

```
Action 1: Ask for Input
  Prompt: "What should I schedule?"

Action 2: Get Contents of URL
  URL: https://ntfy.sh/nick_cmd_a1ask10h
  Method: POST
  Headers:
    Message: add: [Provided Input]
    Title: Schedule Command
  Request Body: Form (0 items)

Siri Phrase: "Add schedule"
```

### Shortcut 2: "My Schedule"

```
Action: Get Contents of URL
  URL: https://ntfy.sh/nick_cmd_a1ask10h
  Method: POST
  Headers:
    Message: list
    Title: Schedule Query
  Request Body: Form (0 items)

Siri Phrase: "My schedule"
```

### Shortcut 3: "What's Coming Up"

```
Action: Get Contents of URL
  URL: https://ntfy.sh/nick_cmd_a1ask10h
  Method: POST
  Headers:
    Message: upcoming
    Title: Schedule Query
  Request Body: Form (0 items)

Siri Phrase: "What's coming up"
```

---

## Step 4: Test from Apple Watch

1. Raise your wrist
2. "Hey Siri, add schedule"
3. Say: "test tomorrow at 3pm"
4. Check your notifications!

---

## Troubleshooting

### Not working?

1. **Check daemon is running:**
   ```bash
   ps aux | grep daemon
   ```

2. **Test manually:**
   ```bash
   curl -d "help" https://ntfy.sh/nick_cmd_a1ask10h
   ```

3. **Check logs:**
   ```bash
   python3 -m schedule_manager.daemon --verbose
   ```

### Still stuck?

- **For iOS Shortcuts issues:** See [SHORTCUTS_FIX_FORM.md](SHORTCUTS_FIX_FORM.md)
- **For detailed setup:** See [IOS_SHORTCUTS_GUIDE.md](IOS_SHORTCUTS_GUIDE.md)
- **For all commands:** See [COMMANDS.md](COMMANDS.md)

---

## Quick Reference

**Available Commands:**
```
add: call mom tomorrow at 3pm
list
upcoming
complete: 15
delete: 15
reschedule: 15 to 5pm
help
```

**Test Commands:**
```bash
python3 test_command_listener.py "help"
python3 test_command_listener.py "add: test tomorrow at 3pm"
python3 test_command_listener.py "list"
```

---

## Success! What's Next?

Once your shortcuts work:

1. ✅ Create more shortcuts (complete task, reschedule, etc.)
2. ✅ Add them to your Apple Watch complications
3. ✅ Set up automation triggers (location-based, time-based)
4. ✅ Share shortcuts with family (give them their own commands topic!)

---

**You're all set! Enjoy voice-controlling your schedule! 🎉**
