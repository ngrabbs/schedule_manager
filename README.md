# AI Schedule Manager 🤖📅

An AI-powered schedule manager with ntfy.sh push notifications, voice commands via Siri/Apple Watch, and OpenCode integration. Control your schedule naturally with voice or AI chat - get notified at the right times!

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Key Features

### 🎤 Voice Control
- **Apple Watch/iPhone**: "Hey Siri, add schedule" → Add tasks by voice
- **Instant feedback**: Get notifications within 1-2 seconds
- **Natural language**: "Call mom tomorrow at 3pm for 30 minutes"

### 🧠 AI Agent Mode (Optional)
- **Conversation context**: "Actually make it 5pm" - remembers previous task
- **Natural variations**: Understands "call mom" vs "remind me to call mom"
- **Multiple models**: Claude, Ollama (llama3.2), OpenAI
- **Automatic fallback**: Works even if AI unavailable

### 🔔 Smart Notifications
- **Task reminders**: 15 minutes before each task
- **Morning summary**: Daily schedule delivered at 7am
- **Upcoming tasks**: Periodic updates during work hours
- **Command responses**: Instant feedback via push notifications

### 🔄 Recurring Tasks
- **Time-blocking**: "I have class mon,wed,fri 12:00-12:45"
- **Automatic generation**: Creates instances for recurring schedules
- **Flexible patterns**: Daily, weekly, monthly schedules

### 🤖 OpenCode Integration
- **MCP server**: Seamless integration with OpenCode
- **Natural AI control**: Manage schedule through AI chat
- **Tool ecosystem**: Access all schedule features via AI

## 🚀 Quick Start

**New to the project? Start here:**

1. **[Quick Start Guide](docs/getting-started/quickstart.md)** - Get running in 5 minutes
2. **[Voice Commands Setup](docs/user-guides/voice-commands.md)** - Control with Siri/Apple Watch
3. **[Command Reference](docs/user-guides/commands.md)** - Learn all available commands

**Want more details?**

- 📖 [Full Documentation](docs/README.md)
- ⚙️ [Installation Guide](docs/getting-started/installation.md)
- 🔧 [Troubleshooting](docs/troubleshooting/common-issues.md)

## 📋 Prerequisites

- **Python 3.8+**
- **ntfy.sh app** (iOS/Android) - Free push notifications
- **OpenCode** (optional) - For AI integration
- **Ollama** (optional) - For local AI models

## 🏃 5-Minute Setup

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Configure your topics (use random values!)
cp config.yaml.example config.yaml
nano config.yaml  # Edit topics

# 3. Initialize database
python3 -m schedule_manager.database

# 4. Test notifications
python3 -c "from schedule_manager.core import ScheduleManager; ScheduleManager().send_test_notification()"

# 5. Start daemon
python3 -m schedule_manager.daemon
```

**Check your phone** - you should get a test notification!

See [Quick Start Guide](docs/getting-started/quickstart.md) for detailed instructions.

## 💬 Usage Examples

### Voice Commands (Apple Watch/Siri)
```
You: "Hey Siri, add schedule"
Siri: "What should I schedule?"
You: "Call mom tomorrow at 3pm"
📱 Notification: "✅ Added: Call mom 📅 Mon Jan 12 at 03:00 PM"
```

### OpenCode Chat
```
You: "Add a task to call mom tomorrow at 3pm"
OpenCode: ✓ Added: "Call mom" scheduled for Jan 12, 2026 at 3:00 PM

You: "What do I have today?"
OpenCode: [Shows your daily schedule]
```

### Python API
```python
from schedule_manager.core import ScheduleManager

manager = ScheduleManager()

# Add task
manager.add_task_natural("Team meeting tomorrow at 10am")

# View schedule
tasks = manager.get_tasks()
print(manager.get_daily_summary())
```

### HTTP Commands (via ntfy.sh)
```bash
curl -d "add: call mom tomorrow at 3pm" https://ntfy.sh/YOUR_COMMAND_TOPIC
curl -d "list" https://ntfy.sh/YOUR_COMMAND_TOPIC
curl -d "upcoming" https://ntfy.sh/YOUR_COMMAND_TOPIC
```

## 📚 Documentation

### 🚀 Getting Started
- [Quick Start Guide](docs/getting-started/quickstart.md) - 5-minute setup
- [Installation Guide](docs/getting-started/installation.md) - Complete instructions
- [Configuration Guide](docs/getting-started/configuration.md) - All options

### 👤 User Guides
- [Voice Commands](docs/user-guides/voice-commands.md) - Siri/Apple Watch control
- [iOS Shortcuts Setup](docs/user-guides/ios-shortcuts.md) - Detailed setup
- [Command Reference](docs/user-guides/commands.md) - All commands
- [Running as Service](docs/user-guides/systemd.md) - Systemd/Launchd setup

### 💻 Developer Guides
- [AI Agent Mode](docs/developer/ai-agent.md) - OpenCode integration
- [OpenCode HTTP API](docs/developer/opencode-api.md) - API details
- [Database Schema](docs/developer/database.md) - Database structure
- [Docker Setup](docs/developer/docker.md) - Container deployment

### 🔧 Troubleshooting
- [Common Issues](docs/troubleshooting/common-issues.md) - FAQ & fixes
- [iOS Shortcuts Issues](docs/troubleshooting/ios-shortcuts.md) - Shortcut problems

## 🎯 Available Commands

| Command | Example | Purpose |
|---------|---------|---------|
| `add:` | add: call mom tomorrow at 3pm | Add new task |
| `list` | list or today | View today's schedule |
| `upcoming` | upcoming or upcoming 4 | See upcoming tasks |
| `complete:` | complete: 15 | Mark task done |
| `delete:` | delete: 15 | Remove task |
| `reschedule:` | reschedule: 15 to 5pm | Change task time |
| `help` | help | Show available commands |

See [Command Reference](docs/user-guides/commands.md) for full documentation.

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│          Your Home Server                │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │    Notification Daemon              │ │
│  │  • Task reminders                   │ │
│  │  • Daily summaries                  │ │
│  │  • Recurring task generation        │ │
│  │  • Command listener (voice/HTTP)    │ │
│  │  • AI agent (optional)              │ │
│  └────────────────────────────────────┘ │
│              ▲          │                │
└──────────────┼──────────┼────────────────┘
               │          │
          ┌────┴──────────┴────┐
          │     ntfy.sh         │
          │  (Push Gateway)     │
          └────┬──────────┬─────┘
               │          │
       ┌───────┘          └────────┐
       ▼                           ▼
  Commands                  Notifications
  (from you)                (to you)
       │                           │
  ┌────┴─────┐              ┌─────┴─────┐
  │  Apple   │              │  iPhone   │
  │  Watch   │◄─────────────┤  Android  │
  │  Siri    │              │  Desktop  │
  └──────────┘              └───────────┘
```

## 🔒 Security Notes

**Your ntfy topics are secret!**
- They function like passwords
- Anyone with your topic can control your schedule
- Use random, unguessable topic names
- Don't share shortcuts publicly (they contain topics)
- Change topics if compromised

Generate secure topics:
```bash
echo "schedule_$(openssl rand -hex 12)"
echo "commands_$(openssl rand -hex 12)"
```

## 🛠️ Tech Stack

- **Python 3.8+** - Core application
- **SQLite** - Task database
- **ntfy.sh** - Push notifications
- **APScheduler** - Job scheduling
- **python-dateutil** - Natural language date parsing
- **OpenCode** (optional) - AI agent platform
- **Ollama** (optional) - Local AI models

## 📊 Project Status

- ✅ Core schedule management
- ✅ ntfy.sh notifications
- ✅ Voice commands (iOS Shortcuts)
- ✅ OpenCode MCP integration
- ✅ AI agent mode (OpenCode HTTP API)
- ✅ Recurring tasks
- ✅ Command listener
- 📋 Web dashboard (planned)
- 📋 Calendar sync (planned)

## 🤝 Contributing

Contributions welcome! Please:

1. Read the [Developer Guides](docs/developer/)
2. Check existing issues
3. Open an issue for major changes
4. Submit PRs with tests

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- [ntfy.sh](https://ntfy.sh) - Simple push notifications
- [OpenCode](https://opencode.ai) - AI agent platform
- [Ollama](https://ollama.ai) - Local AI models
- Python community - Awesome libraries

## 📞 Support

- 📖 [Documentation](docs/README.md)
- 🐛 [Report Issues](https://github.com/yourusername/schedule-manager/issues)
- 💬 [Discussions](https://github.com/yourusername/schedule-manager/discussions)
- ❓ [Troubleshooting](docs/troubleshooting/common-issues.md)

---

**Ready to get started?** Head to the [Quick Start Guide](docs/getting-started/quickstart.md)!
