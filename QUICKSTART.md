# Quick Start Guide

Get your AI Schedule Manager up and running in 5 minutes!

## 1. Install ntfy.sh App

**On your phone/watch:**
- iOS: https://apps.apple.com/us/app/ntfy/id1625396347  
- Android: https://play.google.com/store/apps/details?id=io.heckel.ntfy

## 2. Configure Your Topic

Edit `config.yaml`:

```yaml
ntfy:
  topic: "my_secret_schedule_abc123xyz"  # CHANGE THIS!
```

**Important:** Pick something unique and random. This is your password!

Quick random topic generator:
```bash
echo "my_schedule_$(openssl rand -hex 8)"
```

## 3. Install Dependencies

```bash
cd schedule-manager
pip3 install -r requirements.txt
```

## 4. Test Setup

```bash
python3 example_usage.py
```

Check your phone - you should get a test notification!

## 5. Start the Daemon

```bash
python3 -m schedule_manager.daemon
```

The daemon will:
- ✓ Send you reminders before tasks
- ✓ Send morning daily summary at 7am
- ✓ Send "upcoming" summaries during work hours
- ✓ Generate recurring tasks automatically

## 6. Set Up OpenCode Integration

Copy the MCP server config to your OpenCode settings:

```bash
# Find your OpenCode config location
# Usually: ~/.config/opencode/mcp.json

# Add this to your MCP servers:
{
  "schedule-manager": {
    "command": "python3",
    "args": ["-m", "schedule_manager.mcp_server"],
    "cwd": "/path/to/schedule-manager"
  }
}
```

Restart OpenCode, and you're done!

## Usage Examples

### Via OpenCode:

```
You: "Add a task to call mom tomorrow at 3pm"
OpenCode: ✓ Added: "Call mom" scheduled for Jan 12, 2026 at 3:00 PM

You: "What do I have today?"
OpenCode: [Shows your daily schedule]

You: "I have class mon, wed, fri at 12:00-12:45"
OpenCode: ✓ Added recurring task with time-blocking
```

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

## Running as a Service

To keep the daemon running 24/7:

```bash
# Copy service file
sudo cp schedule-manager.service /etc/systemd/system/schedule-manager@.service

# Start service
sudo systemctl enable schedule-manager@yourusername
sudo systemctl start schedule-manager@yourusername

# Check status
sudo systemctl status schedule-manager@yourusername
```

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

## Troubleshooting

**Not getting notifications?**
1. Check ntfy.sh app is subscribed to your topic
2. Verify config.yaml topic matches
3. Run test: `python3 -c "from schedule_manager.core import ScheduleManager; ScheduleManager().send_test_notification()"`

**Daemon crashed?**
```bash
# If using systemd:
sudo journalctl -u schedule-manager@yourusername -n 50

# If running manually:
tail -f daemon.log
```

## Next Steps

- Read the full README.md for advanced features
- Customize notification times in config.yaml
- Add custom workflows and integrations
- Build a web dashboard (optional)

## Support

- Issues: Open a GitHub issue
- Questions: Check README.md
- Want to contribute? Fork and PR!

---

Enjoy your AI-powered schedule! 🎉
