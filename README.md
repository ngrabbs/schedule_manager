# AI Schedule Manager 🤖📅

An AI-powered schedule manager with ntfy.sh notifications, designed to work seamlessly with OpenCode and AI agents. No more manually managing schedules - just talk to your AI and get notified at the right times!

## Features

- **Voice Commands via Apple Watch**: Control your schedule with Siri! "Hey Siri, add schedule"
- **Bidirectional ntfy.sh Integration**: Send commands TO your schedule manager, not just receive notifications
- **Natural Language Interface**: Add tasks by saying "Team meeting tomorrow at 10am for 1 hour"
- **Smart Notifications**: Get reminders via ntfy.sh on your phone, watch, and desktop
- **Daily Summaries**: Morning briefing of your day ahead
- **Periodic Updates**: Optional "upcoming tasks" summaries during work hours
- **Recurring Tasks**: Time-blocking support (e.g., "I have class mon,wed,fri 12:00-12:45")
- **OpenCode Integration**: MCP server for seamless AI agent control
- **Priority-Based**: High/medium/low priority tasks with different notification urgency
- **Zero Sync Lag**: Everything runs on your local server

## Quick Start

### 1. Install Dependencies

```bash
cd schedule-manager
pip install -r requirements.txt
```

### 2. Configure ntfy.sh

First, install the ntfy.sh app on your phone/watch:
- iOS: https://apps.apple.com/us/app/ntfy/id1625396347
- Android: https://play.google.com/store/apps/details?id=io.heckel.ntfy

Then edit `config.yaml`:

```yaml
ntfy:
  server: "https://ntfy.sh"
  topic: "my_secret_schedule_abc123"  # Change this to something unique!
  
schedule:
  timezone: "America/Los_Angeles"  # Change to your timezone
```

**Important**: Pick a unique, random topic name that can't be guessed! This is essentially your password.

### 3. Test Your Setup

```bash
cd schedule-manager
python3 -c "from schedule_manager.core import ScheduleManager; ScheduleManager().send_test_notification()"
```

You should receive a test notification on your phone!

### 4. Start the Notification Daemon

```bash
python3 -m schedule_manager.daemon
```

The daemon will:
- Send reminders 15 and 5 minutes before tasks
- Send a daily summary at 7:00 AM
- Send periodic "upcoming" summaries during work hours
- Generate recurring task instances automatically

### 5. Set Up OpenCode Integration

Add to your OpenCode MCP configuration (`~/.config/opencode/mcp.json` or similar):

```json
{
  "mcpServers": {
    "schedule-manager": {
      "command": "python3",
      "args": ["-m", "schedule_manager.mcp_server"],
      "cwd": "/path/to/schedule-manager"
    }
  }
}
```

Now you can manage your schedule through OpenCode!

## Voice Commands via Apple Watch / Siri

**NEW!** Control your schedule with your voice from anywhere!

### Quick Start

1. **The daemon listens to commands** via ntfy.sh topic: `nick_cmd_a1ask10h`
2. **Set up iOS Shortcuts** to send commands via Siri
3. **Use your Apple Watch** to add tasks, check schedule, complete tasks, and more!

### Example Voice Interactions

```
You: "Hey Siri, add schedule"
Siri: "What should I schedule?"
You: "Call mom tomorrow at 3pm"
[Notification]: "✅ Added: Call mom 📅 Mon Jan 12 at 03:00 PM"

You: "Hey Siri, my schedule"
[Notification]: Shows today's full schedule

You: "Hey Siri, what's coming up"
[Notification]: Shows tasks in next 4 hours
```

### Available Voice Commands

- **Add tasks**: `add: call mom tomorrow at 3pm`
- **View schedule**: `list` or `today`
- **Upcoming tasks**: `upcoming` or `upcoming 4`
- **Complete task**: `complete: 15`
- **Delete task**: `delete: 15`
- **Reschedule**: `reschedule: 15 to 5pm`
- **Help**: `help`

### Setup Guide

See **[IOS_SHORTCUTS_GUIDE.md](IOS_SHORTCUTS_GUIDE.md)** for complete step-by-step instructions on setting up Siri shortcuts on your iPhone and Apple Watch.

See **[COMMANDS.md](COMMANDS.md)** for complete command reference and examples.

### Test Voice Commands

```bash
# Test command processing
python3 test_command_listener.py "help"
python3 test_command_listener.py "add: test task tomorrow at 3pm"
python3 test_command_listener.py "list"
```

---

## Usage Examples

### Via OpenCode (Natural Language)

Once the MCP server is configured, you can talk to OpenCode like this:

```
You: "Add a task to call mom tomorrow at 3pm"
OpenCode: [Uses schedule_add tool]
✓ Added: "Call mom" scheduled for Jan 12, 2026 at 3:00 PM

You: "What do I have today?"
OpenCode: [Uses schedule_view tool]
📅 Sunday, January 11

🟡 10:00 AM - Team standup (30min)
🔴 02:00 PM - Client presentation (60min)
🟢 05:00 PM - Gym workout (45min)

💡 Scheduled time: 135min | Free time: 6h 45m

You: "I have class mon, wed, fri at 12:00-12:45"
OpenCode: [Uses schedule_add_recurring tool]
✓ Added recurring task with time-blocking

You: "Reschedule the gym to 6pm"
OpenCode: [Finds task ID, uses schedule_reschedule]
✓ Rescheduled to 6:00 PM
```

### Via Python API

```python
from schedule_manager.core import ScheduleManager
from datetime import datetime, timedelta

manager = ScheduleManager()

# Add a task naturally
result = manager.add_task_natural("Team meeting tomorrow at 10am for 1 hour")
print(result)

# Add a task explicitly
tomorrow = datetime.now() + timedelta(days=1)
tomorrow = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)

manager.add_task(
    title="Doctor appointment",
    description="Annual checkup",
    scheduled_time=tomorrow,
    duration=60,
    priority="high",
    tags=["health"]
)

# View today's tasks
tasks = manager.get_tasks()
for task in tasks:
    print(f"{task['title']} at {task['scheduled_time']}")

# Get upcoming tasks
upcoming = manager.get_upcoming_tasks(hours_ahead=4)

# Get daily summary
summary = manager.get_daily_summary()
print(summary)
```

## MCP Tools Available

When using OpenCode, these tools are available:

- `schedule_add` - Add a task using natural language
- `schedule_add_recurring` - Add recurring tasks (time-blocking)
- `schedule_view` - View tasks for a date range
- `schedule_upcoming` - See what's coming up in the next N hours
- `schedule_summary` - Get a formatted daily summary
- `schedule_update` - Update task details
- `schedule_reschedule` - Move a task to a different time
- `schedule_complete` - Mark a task as done
- `schedule_delete` - Remove a task
- `schedule_test_notification` - Test your ntfy.sh setup

## Configuration Reference

### `config.yaml`

```yaml
ntfy:
  server: "https://ntfy.sh"
  topic: "your_unique_topic"  # Outbound notifications
  commands_topic: "your_commands_topic"  # Inbound voice commands (KEEP SECRET!)
  commands_enabled: true  # Enable/disable voice command processing
  priority:
    high: "urgent"    # ntfy.sh priority for high-priority tasks
    medium: "high"    # ntfy.sh priority for medium-priority tasks
    low: "default"    # ntfy.sh priority for low-priority tasks

notifications:
  daily_summary_time: "07:00"  # When to send morning summary
  reminder_minutes_before: [15, 5]  # Send reminders N minutes before
  upcoming_summary_interval_minutes: 120  # Send "upcoming" every 2 hours
  upcoming_summary_work_hours: ["09:00", "17:00"]  # Only during work hours
  
schedule:
  timezone: "America/Los_Angeles"
  work_hours_start: "09:00"
  work_hours_end: "17:00"
  
database:
  path: "data/schedule.db"  # SQLite database location
```

## Running as a Service

To run the daemon automatically on your server:

### Option 1: systemd (Linux)

```bash
# Copy service file
sudo cp schedule-manager.service /etc/systemd/system/schedule-manager@.service

# Enable and start for your user
sudo systemctl enable schedule-manager@yourusername
sudo systemctl start schedule-manager@yourusername

# Check status
sudo systemctl status schedule-manager@yourusername

# View logs
sudo journalctl -u schedule-manager@yourusername -f
```

### Option 2: Screen/Tmux

```bash
# In a screen session
screen -S schedule-manager
cd schedule-manager
python3 -m schedule_manager.daemon

# Detach: Ctrl+A, D
# Reattach: screen -r schedule-manager
```

### Option 3: nohup

```bash
cd schedule-manager
nohup python3 -m schedule_manager.daemon > daemon.log 2>&1 &
```

## Natural Language Examples

The system understands a wide variety of natural language:

**Absolute times:**
- "tomorrow at 3pm"
- "next monday at 10:00"
- "friday afternoon"
- "jan 15 at 2:30pm"

**Relative times:**
- "in 2 hours"
- "in 30 minutes"
- "in 3 days"

**Recurring patterns:**
- "every monday"
- "mon, wed, fri at 12:00"
- "daily at 9am"
- "weekdays at 8am"

**Durations:**
- "for 30 minutes"
- "for 1 hour"
- "for 1.5 hours"
- "for 2h 30m"

## Notification Examples

### Task Reminder
```
⏰ Reminder: Team Meeting
Starting in 15 minutes at 10:00 AM

Discuss Q1 roadmap and priorities

[✓ Done] [Snooze 15m]
```

### Daily Summary
```
📅 Monday, January 12

🔴 09:00 AM - Team standup (30min)
🟡 11:00 AM - Code review (60min)
🟡 02:00 PM - Client call (45min)
🟢 05:00 PM - Gym (60min)

💡 Free time: 4h 45m
```

### Upcoming Tasks
```
📋 Upcoming (4h)

Coming up:

🟡 02:00 PM (in 1h 30m) - Client call
🟢 05:00 PM (in 4h 30m) - Gym
```

## Database Schema

The system uses SQLite with two main tables:

**tasks:**
- id, title, description
- scheduled_time, duration, priority, status
- tags (JSON), is_recurring, recurrence_rule (JSON)
- created_at, updated_at, completed_at

**notifications:**
- id, task_id, notification_time, notification_type
- sent, ntfy_message_id, created_at

You can inspect the database directly:
```bash
sqlite3 data/schedule.db
.tables
SELECT * FROM tasks;
```

## Troubleshooting

### Not receiving notifications?

1. Check ntfy.sh app is subscribed to your topic
2. Verify config.yaml has the correct topic name
3. Test notifications: `python3 -c "from schedule_manager.core import ScheduleManager; ScheduleManager().send_test_notification()"`
4. Check daemon is running: `ps aux | grep daemon`

### Daemon crashes or errors?

```bash
# Check logs if using systemd
sudo journalctl -u schedule-manager@yourusername -n 50

# Or check daemon.log if using nohup
tail -f daemon.log
```

### Time zone issues?

Make sure `config.yaml` has your correct timezone:
```yaml
schedule:
  timezone: "America/New_York"  # Or your timezone
```

Find your timezone: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

### Tasks not showing up?

```python
# Debug in Python
from schedule_manager.core import ScheduleManager
manager = ScheduleManager()

# Check all tasks
all_tasks = manager.db.get_tasks(status=None)
print(f"Total tasks: {len(all_tasks)}")
for task in all_tasks:
    print(task)
```

## Architecture

```
┌─────────────────────────────────────────┐
│         Your Home Server                │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  Notification Daemon             │  │
│  │  (runs in background)            │  │
│  │  • Checks for pending reminders  │  │
│  │  • Sends daily summaries         │  │
│  │  • Generates recurring tasks     │  │
│  └──────────────────────────────────┘  │
│             │                           │
│             ▼                           │
│  ┌──────────────────────────────────┐  │
│  │  SQLite Database                 │  │
│  │  (schedule.db)                   │  │
│  └──────────────────────────────────┘  │
│             │                           │
│             ▼                           │
│  ┌──────────────────────────────────┐  │
│  │  ntfy.sh HTTP API                │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
              │
              │ Push notifications
              ▼
   ┌─────────────────────┐
   │   Your Devices      │
   │  • Phone            │
   │  • Watch            │
   │  • Desktop          │
   └─────────────────────┘
```

## Contributing

This is your personal schedule manager! Feel free to modify it:

- Add custom notification types
- Integrate with other services (calendar sync, email parsing, etc.)
- Build a web dashboard
- Add location-based reminders
- Create custom priority rules
- Whatever you want!

## Why This Instead of Sorted³?

1. **Voice control from Apple Watch** - "Hey Siri, add schedule" from your wrist!
2. **True AI integration** - Your AI can directly manage your schedule
3. **Better notifications** - ntfy.sh works everywhere, customizable
4. **Bidirectional** - Send commands AND receive notifications
5. **No sync lag** - Everything's local
6. **Programmable** - Build any workflow you want
7. **Conversational** - Natural language, no UI clicking
8. **Your data** - SQLite file you own and control
9. **Extensible** - Add any feature easily

## License

MIT - Do whatever you want with it!

---

Made with ❤️ for AI-powered productivity
