# Voice Commands Reference

Complete reference for all available voice commands in the AI Schedule Manager.

## Command Format

Commands can be sent via:
- **iOS Shortcuts + Siri** (recommended for Apple Watch)
- **ntfy.sh mobile app** (manual text entry)
- **HTTP POST** to ntfy.sh (programmatic access)
- **Test script**: `python3 test_command_listener.py "<command>"`

---

## 📝 Add Task Commands

Add a new task to your schedule using natural language.

### Syntax
```
add: <task description with time>
```

### Examples

**Basic tasks with time:**
```
add: call mom tomorrow at 3pm
add: team meeting next monday at 10am
add: dentist appointment friday at 2:30pm
add: code review this afternoon
```

**With duration:**
```
add: call mom tomorrow at 3pm for 30 minutes
add: team meeting next monday at 10am for 1 hour
add: workout session friday at 6am for 45 minutes
```

**With priority (via tags in future):**
```
add: urgent client call tomorrow at 9am
add: buy groceries this weekend
```

**Relative times:**
```
add: reminder in 1 hour
add: followup in 2 days
add: review document in 30 minutes
```

### Response
```
✅ Added: Call mom
📅 Mon Jan 12 at 03:00 PM
```

### Error Cases
- Missing description: `❌ Please provide a task description`
- Unparseable time: Task added without specific time
- Invalid syntax: `❌ Could not parse task description`

---

## 📅 View Schedule Commands

Display your tasks for today.

### Syntax
```
list
today
schedule
```

### Examples
```
list
today
schedule
```

### Response
```
📅 Sunday, January 11

🟡 10:00 AM - Team standup (30min)
🔴 02:00 PM - Client presentation (60min)
🟢 05:00 PM - Gym workout (45min)

💡 Scheduled time: 135min | Free time: 6h 45m
```

### Empty Schedule
```
No tasks scheduled for Sunday, January 11. Enjoy your free time! 🎉
```

---

## ⏰ Upcoming Tasks Commands

View tasks coming up in the next few hours.

### Syntax
```
upcoming
upcoming <hours>
```

### Examples
```
upcoming          # Next 4 hours (default)
upcoming 2        # Next 2 hours
upcoming 8        # Next 8 hours
```

### Response
```
📋 Upcoming (4h)

🟡 02:00 PM (in 1h 30m)
   Client call
🟢 05:00 PM (in 4h 30m)
   Gym
```

### No Upcoming Tasks
```
📋 No tasks in the next 4 hours

You're all clear! ✨
```

---

## ✅ Complete Task Commands

Mark a task as completed.

### Syntax
```
complete: <task_id>
done: <task_id>
```

### Examples
```
complete: 15
done: 15
complete: 42
```

### How to Find Task IDs
1. Send `list` command - task IDs are shown in logs
2. Check daemon verbose output
3. Use OpenCode to query: `schedule_view`

### Response
```
✅ Completed: Call mom
```

### Error Cases
```
❌ Please specify task ID
❌ Task 15 not found
```

---

## 🗑️ Delete Task Commands

Remove a task from your schedule.

### Syntax
```
delete: <task_id>
remove: <task_id>
```

### Examples
```
delete: 15
remove: 42
```

### Response
```
🗑️ Deleted: Call mom
```

### Error Cases
```
❌ Please specify task ID
❌ Task 15 not found
```

---

## 📅 Reschedule Task Commands

Move a task to a different time.

### Syntax
```
reschedule: <task_id> to <new_time>
```

### Examples
```
reschedule: 15 to 5pm
reschedule: 15 to tomorrow at 2pm
reschedule: 42 to next monday at 9am
reschedule: 15 to friday afternoon
```

### Response
```
📅 Rescheduled: Call mom
🕐 New time: Mon Jan 12 at 05:00 PM
```

### Error Cases
```
❌ Invalid format
❌ Task 15 not found
❌ Could not parse time from: xyz123
```

---

## ❓ Help Command

Show available commands.

### Syntax
```
help
commands
?
```

### Response
```
📚 Available Commands

📝 Add Task:
   add: call mom tomorrow at 3pm

📅 View Schedule:
   list  (or 'today')

⏰ Upcoming Tasks:
   upcoming  (or 'upcoming 4')

✅ Complete Task:
   complete: 15  (or 'done: 15')

🗑️ Delete Task:
   delete: 15

📅 Reschedule Task:
   reschedule: 15 to 5pm

❓ Help:
   help  (or 'commands')
```

---

## Natural Language Parsing

The system understands various natural language patterns:

### Date/Time Formats

**Absolute dates:**
- `tomorrow`, `today`
- `next monday`, `this friday`
- `january 15`, `jan 15`
- `monday`, `friday` (next occurrence)

**Relative times:**
- `in 1 hour`, `in 30 minutes`
- `in 2 days`, `in 3 weeks`

**Time formats:**
- `3pm`, `3:00pm`, `15:00`
- `2:30pm`, `14:30`
- `afternoon`, `morning`, `evening`

**Durations:**
- `for 30 minutes`
- `for 1 hour`
- `for 1.5 hours`
- `for 2h 30m`

### Task Titles

The system extracts task titles automatically:
- `call mom tomorrow at 3pm` → Title: "call mom"
- `team meeting next monday at 10am` → Title: "team meeting"

---

## Priority Indicators

Tasks use emoji indicators for priority:

- 🔴 **High priority** - Urgent, important tasks
- 🟡 **Medium priority** - Normal tasks (default)
- 🟢 **Low priority** - Nice-to-have tasks

---

## Rate Limiting

Commands are rate-limited to prevent spam:
- **Minimum delay**: 1 second between commands
- **Response**: `⏱️ Please wait a moment between commands`

---

## Testing Commands

### Using Test Script

```bash
# Send any command
python3 test_command_listener.py "add: test task tomorrow at 10am"

# View examples
python3 test_command_listener.py examples

# Quick test
python3 test_command_listener.py test
```

### Using curl

```bash
curl -d "list" https://ntfy.sh/nick_cmd_a1ask10h
curl -d "add: test tomorrow at 3pm" https://ntfy.sh/nick_cmd_a1ask10h
```

### Using ntfy.sh Mobile App

1. Open ntfy.sh app
2. Navigate to your commands topic
3. Tap the message input
4. Type your command
5. Send

---

## Tips & Best Practices

### 1. Be Specific with Times
✅ Good: `add: call mom tomorrow at 3pm`  
❌ Vague: `add: call mom sometime`

### 2. Use Natural Language
✅ Good: `add: meeting next monday morning`  
✅ Also good: `add: meeting jan 15 at 9am`

### 3. Include Durations When Known
✅ Good: `add: gym session tomorrow at 6am for 1 hour`  
⚠️ Works but less precise: `add: gym session tomorrow at 6am`

### 4. Keep Task IDs Handy
- When you add a task, note the ID from the response
- Task IDs are sequential integers (1, 2, 3, ...)
- Use `list` to see current tasks (IDs in logs)

### 5. Use Voice Commands Wisely
- Speak clearly for Siri
- Use "fifteen" not "one five" for task IDs
- Common phrases work best

---

## Common Use Cases

### Morning Routine
```
# Check what's on your plate
"Hey Siri, my schedule"

# See what's coming up first
"Hey Siri, what's coming up"
```

### During the Day
```
# Quick task entry
"Hey Siri, add schedule"
→ "Call client tomorrow at 2pm"

# Mark things done
"Hey Siri, complete task"
→ "15"
```

### Evening Review
```
# See tomorrow's schedule
list

# Reschedule if needed
reschedule: 42 to tomorrow at 10am
```

### On-the-Go
```
# Quick reminder
add: reminder in 15 minutes

# Check upcoming
upcoming 2
```

---

## Troubleshooting Commands

### Command Not Working?

1. **Check daemon is running:**
   ```bash
   ps aux | grep daemon
   ```

2. **Test with script:**
   ```bash
   python3 test_command_listener.py "help"
   ```

3. **Check daemon logs:**
   ```bash
   journalctl -u schedule-manager -f
   # or if running manually:
   python3 -m schedule_manager.daemon --verbose
   ```

4. **Verify config:**
   ```bash
   cat config.yaml | grep commands
   ```

### Response Not Received?

1. **Check notifications topic** in ntfy.sh app
2. **Wait a moment** - processing can take 1-2 seconds
3. **Check daemon logs** for errors
4. **Verify internet connection** - requires ntfy.sh access

### Parse Errors?

1. **Try different phrasing:**
   - Instead of: `add: meeting 3 days from now`
   - Try: `add: meeting in 3 days`

2. **Use explicit times:**
   - Instead of: `add: call later`
   - Try: `add: call in 2 hours`

3. **Send help command** to verify system is working

---

## Advanced Usage

### Automation Integration

**Home Assistant:**
```yaml
automation:
  - trigger:
      platform: time
      at: "07:00:00"
    action:
      service: rest_command.schedule_list
```

**Node-RED:**
```javascript
msg.payload = "upcoming 4";
msg.headers = {"Title": "Auto Check"};
msg.url = "https://ntfy.sh/nick_cmd_a1ask10h";
return msg;
```

**Python Script:**
```python
import requests
requests.post(
    "https://ntfy.sh/nick_cmd_a1ask10h",
    data="add: automated task tomorrow at 10am"
)
```

---

## Security Considerations

🔒 **Your commands topic is secret!**
- Anyone with `nick_cmd_a1ask10h` can control your schedule
- Don't post it publicly
- Don't share shortcuts that contain it
- Change it if compromised (edit config.yaml)

---

## Feature Requests?

Want a new command type? You can easily add it by editing:
- `schedule_manager/command_processor.py` - Add command handler
- This file - Document the new command

Example: Add a "snooze" command, "search" command, etc.

---

**Happy scheduling! 🎉**

For setup instructions, see [IOS_SHORTCUTS_GUIDE.md](IOS_SHORTCUTS_GUIDE.md)
