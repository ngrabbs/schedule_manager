# Quick Start: Voice Commands 🎤

## Your Commands Topic
```
nick_cmd_a1ask10h
```
🔒 **Keep this secret!** It's like a password.

---

## Test It Now

### 1. Start Daemon (if not running)
```bash
python3 -m schedule_manager.daemon --verbose
```

### 2. Send Test Command
```bash
python3 test_command_listener.py "help"
```

You should receive a notification with available commands!

---

## Quick Command Reference

```bash
# Add a task
python3 test_command_listener.py "add: call mom tomorrow at 3pm"

# View today's schedule
python3 test_command_listener.py "list"

# See what's coming up
python3 test_command_listener.py "upcoming"

# Complete a task (need task ID)
python3 test_command_listener.py "complete: 15"

# Get help
python3 test_command_listener.py "help"
```

---

## iOS Shortcuts Setup (5 minutes)

### Shortcut 1: "Add Schedule"

1. Open **Shortcuts** app on iPhone
2. Create new shortcut
3. Add action: **Ask for Input**
   - Prompt: "What should I schedule?"
4. Add action: **Get Contents of URL**
   - URL: `https://ntfy.sh/nick_cmd_a1ask10h`
   - Method: `POST`
   - Request Body: **Form** (if available) or **File**
   - Body: Switch to text mode, type `add: ` then add the variable [Provided Input]
5. Name it "Add Schedule"
6. Add to Siri: "Hey Siri, add schedule"

**Tip:** In "Get Contents of URL", tap "Show More" to see Request Body options.

### Shortcut 2: "My Schedule"

1. Create new shortcut
2. Add action: **Get Contents of URL**
   - URL: `https://ntfy.sh/nick_cmd_a1ask10h`
   - Method: `POST`
   - Request Body: **Form** (switch to text mode)
   - Body: Type `list`
3. Name it "My Schedule"
4. Add to Siri: "Hey Siri, my schedule"

### Shortcut 3: "What's Coming Up"

Same as above, but use body: `upcoming`

---

## Apple Watch Usage

Once shortcuts are created on iPhone:

1. **Siri Method:**
   - Raise wrist
   - "Hey Siri, add schedule"
   - Speak your task
   - Done!

2. **Shortcuts App Method:**
   - Open Shortcuts on watch
   - Tap your shortcut
   - Follow prompts

3. **Complication Method:**
   - Add Shortcuts complication to watch face
   - Tap to run instantly

---

## Example Voice Interactions

```
You: "Hey Siri, add schedule"
Siri: "What should I schedule?"
You: "Call mom tomorrow at 3pm"
[Notification]: "✅ Added: Call mom 📅 Mon Jan 12 at 03:00 PM"
```

```
You: "Hey Siri, my schedule"
[Notification]: Shows full day's schedule
```

```
You: "Hey Siri, what's coming up"
[Notification]: Shows next 4 hours of tasks
```

---

## Troubleshooting

**Not working?**

1. Check daemon is running:
   ```bash
   ps aux | grep daemon
   ```

2. Check logs:
   ```bash
   python3 -m schedule_manager.daemon --verbose
   ```

3. Test manually:
   ```bash
   curl -d "help" https://ntfy.sh/nick_cmd_a1ask10h
   ```

4. Verify you're subscribed to notification topic in ntfy.sh app

---

## Full Documentation

- **Complete Setup Guide:** [IOS_SHORTCUTS_GUIDE.md](IOS_SHORTCUTS_GUIDE.md)
- **All Commands:** [COMMANDS.md](COMMANDS.md)
- **Implementation Details:** [VOICE_COMMANDS_SUMMARY.md](VOICE_COMMANDS_SUMMARY.md)

---

**That's it! You're ready to control your schedule with your voice! 🎉**
