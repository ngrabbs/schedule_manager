# Installation Guide

Complete installation instructions for the AI Schedule Manager.

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows (WSL recommended)
- **Memory**: 512MB minimum
- **Storage**: 100MB for application + database

## Installation Methods

### Method 1: Standard Installation (Recommended)

```bash
# Clone or download the repository
cd schedule-manager

# Install Python dependencies
pip3 install -r requirements.txt

# Initialize the database
python3 -m schedule_manager.database

# Configure your settings
cp config.yaml.example config.yaml
nano config.yaml  # Edit with your topics
```

### Method 2: Virtual Environment (Isolated)

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -m schedule_manager.database

# Configure
cp config.yaml.example config.yaml
nano config.yaml
```

### Method 3: Docker (Containerized)

See [Docker Setup Guide](../developer/docker.md) for containerized deployment.

## Configuration

### Required Settings

Edit `config.yaml`:

```yaml
ntfy:
  # Main notification topic (for reminders, summaries)
  topic: "your_unique_topic_here"
  
  # Command topic (for voice commands)
  command_topic: "your_command_topic_here"
  
  # Optional: Custom ntfy server
  server: "https://ntfy.sh"

database:
  path: "schedule.db"

notifications:
  # Morning summary time
  morning_summary_time: "07:00"
  
  # How often to send "upcoming" summaries (hours)
  upcoming_interval_hours: 2
  
  # Task reminder time (minutes before)
  reminder_minutes: 15

# Optional: AI Agent Mode
agent:
  enabled: false  # Set to true to enable OpenCode integration
  port: 5555
  model: "ollama/llama3.2:3b"
  agent_name: "general"
```

### Topic Security

Your topics are like passwords. Generate secure random topics:

```bash
# Generate secure topics
echo "schedule_$(openssl rand -hex 12)"
echo "commands_$(openssl rand -hex 12)"
```

**Never share your topics publicly!**

## OpenCode MCP Integration (Optional)

To use the Schedule Manager with OpenCode:

### 1. Find OpenCode Config

```bash
# Linux/macOS
~/.config/opencode/mcp.json

# Windows
%APPDATA%\opencode\mcp.json
```

### 2. Add MCP Server

Edit `mcp.json` and add:

```json
{
  "schedule-manager": {
    "command": "python3",
    "args": ["-m", "schedule_manager.mcp_server"],
    "cwd": "/full/path/to/schedule-manager"
  }
}
```

### 3. Restart OpenCode

```bash
# Kill all OpenCode processes
pkill opencode

# Restart OpenCode
opencode
```

### 4. Test Integration

In OpenCode chat:

```
You: "Add a task to call Sarah tomorrow at 2pm"
OpenCode: ✓ Added: Call Sarah on Jan 13, 2026 at 2:00 PM

You: "Show me today's schedule"
OpenCode: [Displays your tasks for today]
```

## AI Agent Mode (Advanced)

For natural language processing with local AI models:

### Prerequisites

1. **Install Ollama**:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Pull AI Model**:
   ```bash
   ollama pull llama3.2:3b
   ```

### Enable Agent

Edit `config.yaml`:

```yaml
agent:
  enabled: true
  port: 5555
  model: "ollama/llama3.2:3b"
  agent_name: "general"
  startup_timeout_seconds: 30
```

### Start with Agent

```bash
python3 -m schedule_manager.daemon
```

The daemon will automatically start the OpenCode agent server.

For more details, see [AI Agent Documentation](../developer/ai-agent.md).

## Verification

### Test Notifications

```python
python3 -c "from schedule_manager.core import ScheduleManager; ScheduleManager().send_test_notification()"
```

You should receive a test notification on your phone.

### Test Task Creation

```python
from schedule_manager.core import ScheduleManager

manager = ScheduleManager()
manager.add_task_natural("Test task tomorrow at 3pm")
print(manager.get_daily_summary())
```

### Test Command Listener

```bash
# In terminal 1: Start daemon
python3 -m schedule_manager.daemon --verbose

# In terminal 2: Send test command
curl -d "help" https://ntfy.sh/YOUR_COMMAND_TOPIC
```

Check terminal 1 for command processing logs.

## Running as a Service

### Linux (systemd)

See [Systemd Setup Guide](../user-guides/systemd.md) for detailed instructions.

Quick version:

```bash
sudo cp schedule-manager.service /etc/systemd/system/schedule-manager@.service
sudo systemctl enable schedule-manager@$USER
sudo systemctl start schedule-manager@$USER
```

### macOS (launchd)

Create `~/Library/LaunchAgents/com.schedule-manager.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.schedule-manager</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>-m</string>
        <string>schedule_manager.daemon</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/schedule-manager</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load the service:

```bash
launchctl load ~/Library/LaunchAgents/com.schedule-manager.plist
```

## Troubleshooting

### Import Errors

```bash
# Verify installation
pip3 list | grep -E 'requests|dateutil|pytz|yaml|apscheduler'

# Reinstall if needed
pip3 install -r requirements.txt --force-reinstall
```

### Database Errors

```bash
# Reset database
rm schedule.db
python3 -m schedule_manager.database
```

### Permission Errors

```bash
# Fix file permissions
chmod 755 schedule_manager/*.py
chmod 644 schedule.db config.yaml
```

For more help, see [Common Issues](../troubleshooting/common-issues.md).

## Next Steps

- [Quick Start Guide](quickstart.md) - Start using the system
- [Voice Commands](../user-guides/voice-commands.md) - Set up Siri control
- [Command Reference](../user-guides/commands.md) - Learn all commands
- [Configuration Guide](configuration.md) - Advanced configuration options

## Upgrading

To upgrade to a new version:

```bash
# Pull latest changes
git pull origin main

# Upgrade dependencies
pip3 install -r requirements.txt --upgrade

# Restart daemon
# (if using systemd)
sudo systemctl restart schedule-manager@$USER
```

Your database and configuration will be preserved.
