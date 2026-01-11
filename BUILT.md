# AI Schedule Manager - Build Complete! 🎉

I've built you a complete AI-powered schedule manager with ntfy.sh notifications that replaces Sorted³!

## What Was Built

**Location:** `/workspace/notes/sorted/schedule-manager/`

### Core Components (1,764 lines of Python)

1. **Database Layer** (`database.py`)
   - SQLite with full CRUD operations
   - Tasks with scheduling, priorities, tags
   - Notification tracking
   - Recurring task support

2. **Natural Language Parser** (`nlp.py`)
   - Understands "tomorrow at 3pm", "next monday", "in 2 hours"
   - Parses durations ("30 minutes", "1.5 hours")
   - Handles recurring patterns ("mon,wed,fri at 12:00")

3. **ntfy.sh Integration** (`notifications.py`)
   - Task reminders with action buttons
   - Daily morning summaries
   - Periodic "upcoming" summaries
   - Priority-based notification levels

4. **Core Manager** (`core.py`)
   - Schedule management API
   - Natural language task creation
   - Task CRUD operations
   - Summary generation

5. **Notification Daemon** (`daemon.py`)
   - Background process with APScheduler
   - Sends reminders 15 & 5 minutes before tasks
   - Morning daily summary at 7am
   - Periodic upcoming summaries during work hours
   - Auto-generates recurring task instances

6. **MCP Server** (`mcp_server.py`)
   - 10 tools for OpenCode integration
   - Full natural language interface
   - Async stdio-based server

### Supporting Files

- `config.yaml` - Configuration template
- `requirements.txt` - Python dependencies
- `setup.py` - Package setup
- `install.sh` - Installation script
- `example_usage.py` - Demo script
- `schedule-manager.service` - systemd service
- `mcp-config-example.json` - MCP setup example
- `README.md` - Comprehensive documentation
- `QUICKSTART.md` - 5-minute setup guide
- `.gitignore` - Git ignore rules

## Features You Get

### ✅ Natural Language Interface
```
"Team meeting tomorrow at 10am for 1 hour"
"Call mom next friday at 3pm"
"Buy groceries this afternoon"
"I have class mon,wed,fri 12:00-12:45"
```

### ✅ Smart Notifications (via ntfy.sh)
- **Time-based reminders** - 15 & 5 minutes before tasks
- **Morning summary** - Daily briefing at 7am
- **Upcoming updates** - Every 2 hours during work
- **Priority levels** - Different urgency based on task priority
- **Action buttons** - Complete/snooze from notification

### ✅ OpenCode Integration
10 MCP tools available:
- `schedule_add` - Add tasks naturally
- `schedule_add_recurring` - Time-blocking
- `schedule_view` - See your schedule
- `schedule_upcoming` - What's coming up
- `schedule_summary` - Daily summary
- `schedule_update` - Modify tasks
- `schedule_reschedule` - Move tasks
- `schedule_complete` - Mark done
- `schedule_delete` - Remove tasks
- `schedule_test_notification` - Test setup

### ✅ Recurring Tasks (Time-Blocking)
Perfect for classes, meetings, workouts:
```
"I have class mon,wed,fri 12:00-12:45"
"Gym every weekday at 6am"
"Team sync every monday at 9am"
```

### ✅ Flexible Deployment
- Run as systemd service
- Run in screen/tmux
- Run with nohup
- Or just run manually when needed

## How It Works

```
┌─────────────────────────────────────┐
│      Your Home Server               │
│                                     │
│  [Notification Daemon]              │
│         ↓                           │
│  [SQLite Database]                  │
│         ↓                           │
│  [ntfy.sh HTTP API]                 │
└─────────────────────────────────────┘
              ↓
      (Push notifications)
              ↓
   ┌──────────────────────┐
   │   Your Devices       │
   │  • Phone             │
   │  • Watch             │
   │  • Desktop           │
   └──────────────────────┘
```

## Next Steps on Your Home Server

### 1. Copy to Your Home Server
```bash
# From your laptop
scp -r schedule-manager/ yourusername@your-home-server:~/

# Or use git if you set up a repo
cd schedule-manager
git init
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Install on Server
```bash
ssh yourusername@your-home-server
cd ~/schedule-manager
./install.sh
```

### 3. Configure Your ntfy.sh Topic
```bash
# Edit config.yaml
nano config.yaml

# Change this line:
topic: "your_schedule_topic_changeme"

# To something unique like:
topic: "my_secret_schedule_a7f3c9e2b1d4f8a6"
```

### 4. Subscribe on Your Phone
1. Open ntfy.sh app
2. Subscribe to your topic name
3. Done!

### 5. Test It
```bash
python3 example_usage.py
```

Check your phone for notifications!

### 6. Start the Daemon
```bash
# Option A: Run manually (for testing)
python3 -m schedule_manager.daemon

# Option B: Run as service (recommended)
sudo cp schedule-manager.service /etc/systemd/system/schedule-manager@.service
sudo systemctl enable schedule-manager@yourusername
sudo systemctl start schedule-manager@yourusername
```

### 7. Set Up OpenCode Integration
Add to your OpenCode MCP config:
```json
{
  "mcpServers": {
    "schedule-manager": {
      "command": "python3",
      "args": ["-m", "schedule_manager.mcp_server"],
      "cwd": "/home/yourusername/schedule-manager"
    }
  }
}
```

## Usage Examples

### Talk to OpenCode via SSH
```bash
ssh yourusername@your-home-server
opencode
```

Then:
```
You: "Add a task to review code tomorrow at 2pm"
OpenCode: ✓ Added: "Review code" scheduled for Jan 12, 2026 at 2:00 PM

You: "What do I have today?"
OpenCode: [Shows your schedule with times and priorities]

You: "Move the gym workout to 6pm"
OpenCode: ✓ Rescheduled to 6:00 PM
```

### Direct Python API
```python
from schedule_manager.core import ScheduleManager

manager = ScheduleManager()

# Add task
manager.add_task_natural("Dentist appointment next monday at 10am")

# View schedule
tasks = manager.get_tasks()
print(manager.get_daily_summary())
```

## Why This Is Better Than Sorted³

| Feature | Sorted³ | AI Schedule Manager |
|---------|---------|-------------------|
| AI Integration | ❌ No API | ✅ Full MCP integration |
| Notifications | ✅ iOS only, basic | ✅ Cross-platform, rich |
| Sync | ⚠️ iCloud (laggy) | ✅ Instant (local) |
| Natural Language | ✅ Built-in | ✅ Advanced NLP |
| Recurring Tasks | ✅ Yes | ✅ Yes |
| Programmable | ❌ Closed | ✅ Fully open |
| Cost | 💰 $15-25 | ✅ Free |
| Data Ownership | ⚠️ iCloud | ✅ Your SQLite file |
| Extensible | ❌ No | ✅ Add any feature |

## Notifications You'll Receive

**Morning Summary (7:00 AM):**
```
📅 Monday, January 12

🔴 09:00 AM - Team standup (30min)
🟡 11:00 AM - Code review (60min)
🟡 02:00 PM - Client call (45min)
🟢 05:00 PM - Gym (60min)

💡 Free time: 4h 45m
```

**Task Reminder (15 min before):**
```
⏰ Reminder: Team Meeting
Starting in 15 minutes at 10:00 AM

Discuss Q1 roadmap and priorities

[✓ Done] [Snooze 15m]
```

**Upcoming Summary (every 2h during work):**
```
📋 Upcoming (4h)

Coming up:

🟡 02:00 PM (in 1h 30m) - Client call
🟢 05:00 PM (in 4h 30m) - Gym
```

## Configuration Options

Edit `config.yaml`:

```yaml
notifications:
  daily_summary_time: "07:00"  # Change morning summary time
  reminder_minutes_before: [15, 5]  # Add more reminders
  upcoming_summary_interval_minutes: 120  # Change frequency
  upcoming_summary_work_hours: ["09:00", "17:00"]  # Work hours
  
schedule:
  timezone: "America/Los_Angeles"  # Your timezone
  work_hours_start: "09:00"
  work_hours_end: "17:00"
```

## Future Enhancement Ideas

Since it's fully open and programmable, you could add:

1. **Calendar Sync** - Import from Google Calendar / Apple Calendar
2. **Email Parsing** - Extract tasks from emails automatically  
3. **Location-Based** - Remind when near relevant location
4. **Weather Integration** - Adjust outdoor tasks based on weather
5. **Pomodoro Timer** - Built-in focus sessions
6. **Analytics Dashboard** - Track time usage, completion rates
7. **Voice Interface** - Call a number, speak your tasks
8. **Web Dashboard** - Visual interface for viewing schedule
9. **Multi-User** - Share schedules with family/team
10. **AI Auto-Scheduling** - Let AI optimize your schedule

## Troubleshooting

**Not getting notifications?**
```bash
# Test notification
python3 -c "from schedule_manager.core import ScheduleManager; ScheduleManager().send_test_notification()"

# Check daemon logs (if using systemd)
sudo journalctl -u schedule-manager@yourusername -f
```

**Daemon crashed?**
```bash
# Check status
sudo systemctl status schedule-manager@yourusername

# Restart
sudo systemctl restart schedule-manager@yourusername
```

**Database issues?**
```bash
# Inspect database
sqlite3 data/schedule.db
.tables
SELECT * FROM tasks;
.quit
```

## Documentation

- **QUICKSTART.md** - 5-minute setup guide
- **README.md** - Full documentation (comprehensive)
- **config.yaml** - Configuration with comments
- **example_usage.py** - Working examples

## Technical Specs

- **Language:** Python 3.8+
- **Database:** SQLite3
- **Scheduler:** APScheduler
- **NLP:** dateutil + custom parser
- **Notifications:** ntfy.sh HTTP API
- **Integration:** MCP protocol
- **Total Code:** 1,764 lines

## What You Can Do Now

1. ✅ Manage your schedule with natural language
2. ✅ Get smart notifications on all devices
3. ✅ Talk to OpenCode to manage tasks
4. ✅ Time-block recurring events
5. ✅ Get morning summaries
6. ✅ See upcoming tasks during the day
7. ✅ No more sync lag between devices
8. ✅ Own your data completely
9. ✅ Extend with any feature you want
10. ✅ Use your Apple Watch for notifications!

---

**You're all set!** 🚀

SSH into your home server, copy over the `schedule-manager/` directory, run `./install.sh`, and you're ready to go. Your AI agents can now manage your schedule, and you'll get timely notifications via ntfy.sh.

Enjoy your new AI-powered schedule manager! 📅🤖
