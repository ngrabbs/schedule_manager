# Quick Start Guide

Get your AI Schedule Manager up and running in 5 minutes!

## Prerequisites

- Python 3.8+
- ntfy.sh app (iOS/Android)
- Basic terminal knowledge

## 1. Install ntfy.sh App

**On your phone/watch:**
- iOS: https://apps.apple.com/us/app/ntfy/id1625396347  
- Android: https://play.google.com/store/apps/details?id=io.heckel.ntfy

## 2. Configure Your Topic

Edit `config.yaml`:

```yaml
ntfy:
  topic: "my_secret_schedule_abc123xyz"  # CHANGE THIS!
  command_topic: "my_commands_xyz789"    # CHANGE THIS TOO!
```

**Important:** Pick something unique and random. These are like passwords!

Quick random topic generator:
```bash
echo "my_schedule_$(openssl rand -hex 8)"
echo "my_commands_$(openssl rand -hex 8)"
```

## 3. Install Dependencies

```bash
cd schedule-manager
pip3 install -r requirements.txt
```

## 4. Initialize Database

```bash
python3 -m schedule_manager.database
```

## 5. Test Setup

```bash
python3 example_usage.py
```

Check your phone - you should get a test notification!

## 6. Start the Daemon

```bash
python3 -m schedule_manager.daemon
```

The daemon will:
- ✓ Send you reminders before tasks
- ✓ Send morning daily summary at 7am
- ✓ Send "upcoming" summaries during work hours
- ✓ Generate recurring tasks automatically
- ✓ Listen for voice commands on your command topic

## Usage Examples

### Via Voice Commands (iOS Shortcuts):

```
You: "Hey Siri, add schedule"
Siri: "What should I schedule?"
You: "Call mom tomorrow at 3pm"
[Notification]: "✅ Added: Call mom 📅 Mon Jan 12 at 03:00 PM"
```

See [Voice Commands Guide](../user-guides/voice-commands.md) for full setup.

### Via Python:

```python
from schedule_manager.core import ScheduleManager

manager = ScheduleManager()

# Add task
manager.add_task_natural("Team meeting tomorrow at 10am")

# View tasks
tasks = manager.get_tasks()

# Get summary
print(manager.get_daily_summary())
```

### Via OpenCode Integration:

```
You: "Add a task to call mom tomorrow at 3pm"
OpenCode: ✓ Added: "Call mom" scheduled for Jan 12, 2026 at 3:00 PM

You: "What do I have today?"
OpenCode: [Shows your daily schedule]

You: "I have class mon, wed, fri at 12:00-12:45"
OpenCode: ✓ Added recurring task with time-blocking
```

See [Installation Guide](installation.md) for OpenCode MCP setup.

## Notifications You'll Get

**Morning Summary (7am):**
```
📅 Monday, January 12

🔴 09:00 AM - Team standup (30min)
🟡 02:00 PM - Client call (45min)
🟢 05:00 PM - Gym (60min)

💡 Free time: 4h 45m
```

**Task Reminder (15 min before):**
```
⏰ Reminder: Team Meeting
Starting in 15 minutes at 10:00 AM

Discuss Q1 roadmap
```

**Upcoming Summary (every 2 hours during work):**
```
📋 Upcoming (4h)

🟡 02:00 PM (in 1h 30m) - Client call
🟢 05:00 PM (in 4h 30m) - Gym
```

## Running as a Service

To keep the daemon running 24/7, see [Systemd Setup Guide](../user-guides/systemd.md).

## Troubleshooting

**Not getting notifications?**
1. Check ntfy.sh app is subscribed to your topic
2. Verify config.yaml topic matches
3. Run test: `python3 -c "from schedule_manager.core import ScheduleManager; ScheduleManager().send_test_notification()"`

**Daemon crashed?**
```bash
# Check logs
tail -f daemon.log
```

For more help, see [Troubleshooting Guide](../troubleshooting/common-issues.md).

## Next Steps

- [Set up Voice Commands](../user-guides/voice-commands.md) - Control with Siri
- [iOS Shortcuts Guide](../user-guides/ios-shortcuts.md) - Detailed setup
- [Command Reference](../user-guides/commands.md) - All available commands
- [Full Installation Guide](installation.md) - Advanced setup options

---

Enjoy your AI-powered schedule! 🎉
