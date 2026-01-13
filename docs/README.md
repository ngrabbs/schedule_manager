# Schedule Manager Documentation

Welcome to the AI Schedule Manager documentation!

## 📚 Documentation Structure

### 🚀 Getting Started
Perfect for new users and quick setup.

- **[Quick Start Guide](getting-started/quickstart.md)** - Get running in 5 minutes
- **[Installation Guide](getting-started/installation.md)** - Complete setup instructions
- **[Configuration Guide](getting-started/configuration.md)** - Configure your settings

### 👤 User Guides
Learn how to use all the features.

- **[Voice Commands](user-guides/voice-commands.md)** - Control with Siri on Apple Watch/iPhone
- **[iOS Shortcuts Setup](user-guides/ios-shortcuts.md)** - Detailed shortcut configurations
- **[Command Reference](user-guides/commands.md)** - Complete command documentation
- **[Running as a Service](user-guides/systemd.md)** - Set up systemd/launchd service

### 💻 Developer Guides
For advanced users and contributors.

- **[AI Agent Mode](developer/ai-agent.md)** - OpenCode integration architecture
- **[OpenCode HTTP API](developer/opencode-api.md)** - HTTP API implementation details
- **[Database Schema](developer/database.md)** - Database structure and queries
- **[Docker Setup](developer/docker.md)** - Containerized deployment

### 🔧 Troubleshooting
Solutions to common problems.

- **[Common Issues](troubleshooting/common-issues.md)** - General troubleshooting
- **[iOS Shortcuts Issues](troubleshooting/ios-shortcuts.md)** - Shortcut-specific problems

## 🎯 Quick Links

### By Task

**I want to...**

- **Set up voice commands on Apple Watch** → [Voice Commands Guide](user-guides/voice-commands.md)
- **Install from scratch** → [Installation Guide](getting-started/installation.md)
- **Learn all available commands** → [Command Reference](user-guides/commands.md)
- **Run as a background service** → [Systemd Guide](user-guides/systemd.md)
- **Use with OpenCode** → [AI Agent Guide](developer/ai-agent.md)
- **Fix notification issues** → [Common Issues](troubleshooting/common-issues.md)
- **Fix Siri shortcuts** → [iOS Shortcuts Troubleshooting](troubleshooting/ios-shortcuts.md)

### By Skill Level

**Beginner (Just want it to work)**
1. [Quick Start Guide](getting-started/quickstart.md)
2. [Voice Commands](user-guides/voice-commands.md)
3. [Common Issues](troubleshooting/common-issues.md)

**Intermediate (Want to customize)**
1. [Installation Guide](getting-started/installation.md)
2. [Configuration Guide](getting-started/configuration.md)
3. [Command Reference](user-guides/commands.md)
4. [Systemd Setup](user-guides/systemd.md)

**Advanced (Want to develop/integrate)**
1. [AI Agent Mode](developer/ai-agent.md)
2. [OpenCode HTTP API](developer/opencode-api.md)
3. [Database Schema](developer/database.md)
4. [Docker Setup](developer/docker.md)

## 🌟 Features Overview

### Core Features
- ✅ Natural language task parsing
- ✅ Smart notifications (reminders, summaries)
- ✅ Recurring tasks with time-blocking
- ✅ Voice command support (Siri/Apple Watch)
- ✅ OpenCode MCP integration
- ✅ AI agent mode (optional)

### Notification Types
- **Morning Summary** - Daily schedule at 7am
- **Task Reminders** - 15 minutes before each task
- **Upcoming Summary** - Every 2 hours during work
- **Command Responses** - Instant feedback via push

### Integration Options
- **iOS Shortcuts** - Voice control via Siri
- **OpenCode** - AI-powered task management
- **Python API** - Programmatic access
- **HTTP** - REST-like interface via ntfy.sh
- **Database** - Direct SQLite access

## 📖 Documentation Conventions

### Code Examples

```bash
# Shell commands look like this
python3 -m schedule_manager.daemon
```

```python
# Python code looks like this
from schedule_manager.core import ScheduleManager
manager = ScheduleManager()
```

```yaml
# Config examples look like this
ntfy:
  topic: "your_topic_here"
```

### Indicators

- ✅ **Recommended** - Best practice or recommended approach
- ⚠️ **Warning** - Be careful, potential issue
- 🔒 **Security** - Security-related information
- 💡 **Tip** - Helpful hint or pro tip
- ❌ **Don't** - What NOT to do
- 🎯 **Goal** - What we're trying to achieve

### File Paths

- Relative paths assume you're in the `schedule-manager` directory
- Absolute paths start with `/` (Linux/macOS) or drive letter (Windows)
- Config file is always `config.yaml` in project root

## 🆘 Need Help?

### Documentation Search Order

1. **Check [Quick Start](getting-started/quickstart.md)** - Covers 80% of basic usage
2. **Check [Common Issues](troubleshooting/common-issues.md)** - Most problems are here
3. **Check specific guide** - Use navigation above
4. **Check code comments** - Source is well-documented
5. **Open an issue** - On GitHub with details

### Before Asking for Help

Please collect this information:

```bash
# System info
python3 --version
cat config.yaml | grep -A 3 ntfy

# Check status
ps aux | grep daemon
tail -50 daemon.log

# Test basic functionality
python3 -c "from schedule_manager.core import ScheduleManager; ScheduleManager().send_test_notification()"
```

## 🤝 Contributing to Documentation

Found an error or want to improve the docs?

1. **For typos/small fixes** - Just submit a PR
2. **For new sections** - Open an issue first to discuss
3. **For screenshots** - Place in `docs/screen_cap/`
4. **For examples** - Add to relevant guide

### Documentation Style

- Use clear, simple language
- Include working code examples
- Add troubleshooting for common pitfalls
- Link to related documentation
- Keep it up-to-date with code changes

## 📜 Version Information

These docs are for **Schedule Manager v1.0**

- Last updated: January 2026
- Compatible with: Python 3.8+
- OpenCode version: Current stable
- ntfy.sh: v2.x

## 📞 Support Channels

- **Documentation**: You're reading it!
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Code**: [GitHub Repository](https://github.com/yourusername/schedule-manager)

---

**Ready to get started?** Head to the [Quick Start Guide](getting-started/quickstart.md)!
