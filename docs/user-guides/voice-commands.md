# Voice Commands Guide 🎤

Control your schedule with Siri on iPhone and Apple Watch.

## Quick Start

**Your commands topic:** Check `config.yaml` for your `command_topic`

🔒 **Keep this secret!** It's like a password - anyone with this topic can control your schedule.

## How It Works

```
You → Siri → iOS Shortcut → ntfy.sh → Server Daemon → Schedule Manager → ntfy.sh → You
```

Responses arrive as push notifications within 1-2 seconds!

## Available Commands

| Command | Example | Purpose |
|---------|---------|---------|
| `add:` | add: call mom tomorrow at 3pm | Add new task |
| `list` | list or today | View today's schedule |
| `upcoming` | upcoming or upcoming 4 | See upcoming tasks |
| `complete:` | complete: 15 | Mark task done |
| `delete:` | delete: 15 | Remove task |
| `reschedule:` | reschedule: 15 to 5pm | Change task time |
| `help` | help | Show available commands |

See [Command Reference](commands.md) for detailed command documentation.

## iOS Shortcuts Setup

### Prerequisites

1. ✅ Schedule manager daemon running
2. ✅ ntfy.sh app installed on iPhone/Watch
3. ✅ Your commands topic from `config.yaml`

### Shortcut 1: "Add Schedule"

**Purpose:** Add tasks by voice

**Steps:**

1. Open **Shortcuts** app on iPhone
2. Tap **+** to create new shortcut
3. **Add Action** → Search "Ask for Input"
4. Configure:
   - Prompt: `What should I schedule?`
   - Input Type: Text
5. **Add Action** → Search "Get Contents of URL"
6. Configure:
   - URL: `https://ntfy.sh/YOUR_COMMAND_TOPIC`
   - Method: `POST`
   - Request Body: **Form** (or File)
   - Body: `add: [Provided Input]`
     - Tip: Switch to text mode, type `add: ` then insert the "Provided Input" variable
   - Headers (optional):
     - `Title`: Schedule Command
     - `Priority`: default
7. Name shortcut: "Add Schedule"
8. Tap (i) info button → "Add to Siri"
9. Record phrase: **"Add schedule"**

**Test it:**
- Tap the shortcut
- Type: "Call mom tomorrow at 3pm"
- Check notifications for response!

### Shortcut 2: "My Schedule"

**Purpose:** View today's tasks

**Steps:**

1. Create new shortcut
2. **Add Action** → "Get Contents of URL"
3. Configure:
   - URL: `https://ntfy.sh/YOUR_COMMAND_TOPIC`
   - Method: `POST`
   - Body: `list`
   - Headers: (optional, same as above)
4. Name: "My Schedule"
5. Siri phrase: **"My schedule"**

### Shortcut 3: "What's Coming Up"

**Purpose:** See upcoming tasks (next 4 hours)

**Steps:**

1. Create new shortcut
2. **Add Action** → "Get Contents of URL"
3. Configure:
   - URL: `https://ntfy.sh/YOUR_COMMAND_TOPIC`
   - Method: `POST`
   - Body: `upcoming`
4. Name: "What's Coming Up"
5. Siri phrase: **"What's coming up"**

### Shortcut 4: "Complete Task"

**Purpose:** Mark a task as done

**Steps:**

1. Create new shortcut
2. **Add Action** → "Ask for Input"
   - Prompt: `Task ID to complete?`
   - Input Type: Number
3. **Add Action** → "Get Contents of URL"
   - URL: `https://ntfy.sh/YOUR_COMMAND_TOPIC`
   - Method: `POST`
   - Body: `complete: [Provided Input]`
4. Name: "Complete Task"
5. Siri phrase: **"Complete task"**

### Shortcut 5: "Help"

**Purpose:** Show available commands

**Steps:**

1. Create new shortcut
2. **Add Action** → "Get Contents of URL"
   - URL: `https://ntfy.sh/YOUR_COMMAND_TOPIC`
   - Method: `POST`
   - Body: `help`
3. Name: "Schedule Help"
4. Siri phrase: **"Schedule help"**

## Apple Watch Usage

Once shortcuts are created on iPhone, they automatically sync to Apple Watch!

### Method 1: Siri (Easiest)
```
Raise wrist → "Hey Siri, add schedule"
→ Speak your task
→ Done!
```

### Method 2: Shortcuts App
```
Open Shortcuts on watch
→ Tap your shortcut
→ Follow prompts
```

### Method 3: Watch Face Complication (Fastest)
```
Edit watch face
→ Add Shortcuts complication
→ Configure to show your schedule shortcuts
→ Tap from watch face to run instantly
```

## Example Voice Interactions

### Adding a Task
```
You: "Hey Siri, add schedule"
Siri: "What should I schedule?"
You: "Call mom tomorrow at 3pm"
[Notification]: "✅ Added: Call mom 📅 Mon Jan 12 at 03:00 PM"
```

### Viewing Schedule
```
You: "Hey Siri, my schedule"
[Notification]: 
📅 Monday, January 12

🟡 10:00 AM - Team standup (30min)
🔴 02:00 PM - Client call (45min)
🟢 05:00 PM - Gym (60min)

💡 Scheduled: 135min | Free: 6h 45m
```

### Checking Upcoming
```
You: "Hey Siri, what's coming up"
[Notification]:
📋 Upcoming (4h)

🟡 02:00 PM (in 1h 30m)
   Client call
🟢 05:00 PM (in 4h 30m)
   Gym
```

### Completing a Task
```
You: "Hey Siri, complete task"
Siri: "Task ID to complete?"
You: "Fifteen"
[Notification]: "✅ Completed: Call mom"
```

## Tips for Best Voice Recognition

1. **Speak Clearly:** Especially for times
   - Good: "three P M"
   - Avoid: "three pee em"

2. **Use Numbers:** For task IDs
   - Good: "fifteen"
   - Avoid: "one five"

3. **Natural Language:** For tasks
   - Good: "call mom tomorrow afternoon"
   - Also Good: "call mom tomorrow at three"

4. **Confirmation:** Always check the notification
   - The response shows exactly what was created

## Troubleshooting

### Shortcut Not Working?

**Check daemon is running:**
```bash
ps aux | grep daemon
```

**Test manually:**
```bash
curl -d "help" https://ntfy.sh/YOUR_COMMAND_TOPIC
```

**Check daemon logs:**
```bash
python3 -m schedule_manager.daemon --verbose
```

### No Response Received?

1. **Check ntfy.sh subscription:** Ensure you're subscribed to your notification topic (NOT command topic)
2. **Wait a moment:** Processing takes 1-2 seconds
3. **Verify internet:** Both phone and server need connectivity
4. **Check config:** Ensure notification topic is correct in `config.yaml`

### Siri Not Recognizing Phrase?

1. **Re-record phrase:** Edit shortcut → Siri & Search → Re-add to Siri
2. **Use different phrase:** "Schedule add" instead of "Add schedule"
3. **Check language:** Siri language must match iOS system language

### Parse Errors?

Commands failing to understand times? Try:
- Instead of: "meeting 3 days from now"
- Try: "meeting in 3 days" or "meeting friday at 2pm"

See [Troubleshooting Guide](../troubleshooting/ios-shortcuts.md) for more help.

## Security Best Practices

🔒 **Protect Your Command Topic:**
- Don't share shortcuts publicly (they contain your topic)
- Don't post your topic in screenshots
- Change topic if compromised (edit `config.yaml` and recreate shortcuts)
- Use random, unguessable topics

## Testing Without Voice

### Using Test Script:
```bash
python3 test_command_listener.py "add: test task tomorrow at 10am"
python3 test_command_listener.py "list"
python3 test_command_listener.py "help"
```

### Using curl:
```bash
curl -d "list" https://ntfy.sh/YOUR_COMMAND_TOPIC
curl -d "add: test tomorrow at 3pm" https://ntfy.sh/YOUR_COMMAND_TOPIC
```

### Using ntfy.sh App:
1. Open ntfy.sh app
2. Go to your commands topic
3. Tap message input
4. Type command
5. Send

## Next Steps

- [Command Reference](commands.md) - Complete command documentation
- [iOS Shortcuts Guide](ios-shortcuts.md) - Advanced shortcut configurations
- [Common Issues](../troubleshooting/common-issues.md) - Troubleshooting help

---

**Happy voice scheduling! 🎉**
