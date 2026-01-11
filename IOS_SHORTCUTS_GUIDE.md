# iOS Shortcuts Guide for Voice Commands

This guide will help you set up Siri voice commands on your iPhone and Apple Watch to control your schedule manager.

## Prerequisites

1. ✅ Schedule manager daemon running on your server
2. ✅ ntfy.sh app installed on iPhone/Apple Watch
3. ✅ Commands topic from `config.yaml`: `nick_cmd_a1ask10h`

## Setup Overview

The flow works like this:
```
You → Siri → iOS Shortcut → ntfy.sh → Your Server Daemon → Schedule Manager → ntfy.sh → Notification Back to You
```

---

## Part 1: Basic Setup

### Step 1: Open Shortcuts App

1. Open the **Shortcuts** app on your iPhone
2. Tap the **+** button (top right) to create a new shortcut

---

## Part 2: Create "Add Schedule" Shortcut

This shortcut lets you add tasks with your voice.

### Configuration

1. **Add Action**: Tap "Add Action"
2. **Search**: Type "Ask for Input" and select it
3. **Configure Ask for Input**:
   - Prompt: `What should I schedule?`
   - Input Type: Text
   - Leave other options default

4. **Add Another Action**: Tap the + button
5. **Search**: Type "Get Contents of URL" and select it
6. **Configure Get Contents of URL**:
   - **URL**: `https://ntfy.sh/nick_cmd_a1ask10h`
   - **Method**: `POST`
   - **Request Body**: Select "Text" from the dropdown
   - **Body Content**: Tap and select "Ask for Input" from the variables menu, then type `add: ` before it
     - Final text should be: `add: [Provided Input]`
   - **Headers**: Tap "Add new field" → "Add Header"
     - Key: `Title`, Value: `Schedule Command`
     - Key: `Priority`, Value: `default`

7. **Name the Shortcut**: Tap the shortcut name at the top and rename to "Add Schedule"

8. **Set Siri Phrase**:
   - Tap the (i) info button at the bottom
   - Tap "Add to Siri"
   - Record phrase: **"Add schedule"** or **"Schedule something"**

### Test It

1. Tap the shortcut to test
2. Say or type: "Call mom tomorrow at 3pm"
3. Check your notifications for the response!

---

## Part 3: Create "My Schedule" Shortcut

This shortcut shows your tasks for today.

### Configuration

1. **Create New Shortcut**: Tap + button
2. **Add Action**: "Get Contents of URL"
3. **Configure**:
   - **URL**: `https://ntfy.sh/nick_cmd_a1ask10h`
   - **Method**: `POST`
   - **Request Body**: Text
   - **Body**: `list`
   - **Headers**:
     - `Title`: `Schedule Command`
     - `Priority`: `default`

4. **Name**: "My Schedule"
5. **Siri Phrase**: "My schedule" or "What's on my schedule"

---

## Part 4: Create "What's Coming Up" Shortcut

Shows upcoming tasks in the next 4 hours.

### Configuration

1. **Create New Shortcut**
2. **Add Action**: "Get Contents of URL"
3. **Configure**:
   - **URL**: `https://ntfy.sh/nick_cmd_a1ask10h`
   - **Method**: `POST`
   - **Request Body**: Text
   - **Body**: `upcoming`
   - **Headers**: Same as above

4. **Name**: "What's Coming Up"
5. **Siri Phrase**: "What's coming up" or "Upcoming tasks"

---

## Part 5: Create "Complete Task" Shortcut

Mark a task as done by its ID number.

### Configuration

1. **Create New Shortcut**
2. **Add Action**: "Ask for Input"
   - Prompt: `Which task number?`
   - Input Type: Number
3. **Add Action**: "Get Contents of URL"
4. **Configure**:
   - **URL**: `https://ntfy.sh/nick_cmd_a1ask10h`
   - **Method**: `POST`
   - **Request Body**: Text
   - **Body**: `complete: [Provided Input]`
   - **Headers**: Same as above

5. **Name**: "Complete Task"
6. **Siri Phrase**: "Complete task" or "Mark task done"

---

## Part 6: Apple Watch Setup

Once your shortcuts are created on iPhone, they automatically sync to Apple Watch!

### Using on Apple Watch

**Method 1: Siri**
1. Raise wrist and say "Hey Siri"
2. Say your trigger phrase: "Add schedule"
3. Follow the prompts

**Method 2: Shortcuts App**
1. Open Shortcuts app on watch
2. Tap the shortcut you want to run
3. Follow prompts using dictation or scribble

**Method 3: Complications**
1. Long-press your watch face
2. Tap "Edit"
3. Select a complication slot
4. Choose Shortcuts
5. Select your schedule shortcut
6. Now you can tap it directly from your watch face!

---

## Advanced Shortcuts

### Quick Add with Predefined Time

Create shortcuts for common tasks:

**"Remind Me in 1 Hour"**
- Body: `add: reminder in 1 hour`

**"Team Standup Tomorrow"**
- Body: `add: team standup tomorrow at 9am`

### Reschedule Task

**Configuration:**
1. Ask for Input: "Which task number?"
2. Ask for Input: "New time?"
3. Get Contents of URL:
   - Body: `reschedule: [Task Number] to [New Time]`

---

## Troubleshooting

### Issue: "Could not connect to server"
**Solution**: Check your internet connection. ntfy.sh requires internet access.

### Issue: "No response received"
**Solutions**:
- Verify daemon is running: `ps aux | grep daemon`
- Check daemon logs for errors
- Test with: `python3 test_command_listener.py "help"`

### Issue: "Command not recognized"
**Solution**: Check your command syntax. Send "help" to see available commands.

### Issue: Siri doesn't understand the command
**Solutions**:
- Re-record your Siri phrase with clear pronunciation
- Try a different phrase
- Use the Shortcuts app directly instead

### Issue: Shortcut works on iPhone but not Watch
**Solutions**:
- Wait a few minutes for sync
- Check Watch storage isn't full
- Toggle iPhone → Watch → Shortcuts sync in Watch app

---

## Example Siri Conversations

### Adding a Task
```
You: "Hey Siri, add schedule"
Siri: "What should I schedule?"
You: "Call mom tomorrow at 3pm for 30 minutes"
[Notification appears]: "✅ Added: Call mom
📅 Mon Jan 12 at 03:00 PM"
```

### Checking Schedule
```
You: "Hey Siri, my schedule"
[Notification appears with today's tasks]
```

### Completing a Task
```
You: "Hey Siri, complete task"
Siri: "Which task number?"
You: "Fifteen"
[Notification]: "✅ Completed: Call mom"
```

---

## Tips & Tricks

### 1. Voice Recognition Tips
- Speak clearly and at normal pace
- For task IDs, say "fifteen" not "one five"
- Use common phrases like "tomorrow" instead of dates

### 2. Batch Task Adding
Create a shortcut that adds multiple common tasks at once:
```
add: morning routine today at 7am
add: workout today at 8am
add: breakfast today at 9am
```

### 3. Location-Based Shortcuts
iOS Shortcuts can trigger based on location:
- Set up "When I arrive at work" → Send "list"
- "When I leave work" → Send "upcoming"

### 4. Time-Based Shortcuts
Use Automations:
- Every morning at 7am → Run "My Schedule"
- Every Friday at 5pm → Run "What's Coming Up"

### 5. Share Shortcuts
You can share shortcuts with family:
- Open shortcut → (i) button → Share
- They'll need their own commands topic though!

---

## Security Notes

🔒 **Keep Your Commands Topic Secret**
- The topic `nick_cmd_a1ask10h` acts like a password
- Don't share it publicly or post it online
- Anyone with this topic can control your schedule

🔒 **Recommendations**:
- Don't share your shortcuts publicly (they contain the topic)
- If compromised, change the topic in `config.yaml` and update shortcuts
- Consider running daemon behind a VPN for extra security

---

## All Available Commands

See [COMMANDS.md](COMMANDS.md) for a complete reference of all commands you can use.

---

## Need Help?

1. Test commands manually: `python3 test_command_listener.py "help"`
2. Check daemon logs: `journalctl -u schedule-manager -f`
3. Verify config: `cat config.yaml`
4. Send test notification: `python3 -c "from schedule_manager.core import ScheduleManager; ScheduleManager().send_test_notification()"`

---

**Enjoy your voice-controlled schedule! 🎉🎤**
