# Schedule Manager

An AI-powered schedule manager with push notifications via ntfy.sh and voice control through Siri/Apple Watch.

## Features

- **Voice Control** - Talk to Siri, tasks appear on your schedule
- **AI Understanding** - Natural language: "remind me to call mom tomorrow at 3pm"
- **Push Notifications** - Reminders sent to your phone at the right time
- **Priority-based Reminders** - Important tasks get multiple reminders
- **OpenCode Integration** - Manage schedule through AI chat

## Quick Start

### 1. Install

```bash
git clone <repo>
cd schedule-manager
pip3 install -r requirements.txt
```

### 2. Configure

```bash
cp config.yaml.example config.yaml
nano config.yaml
```

Set your ntfy.sh topics (use random strings - they're like passwords):
```yaml
ntfy:
  topic: "your_random_notification_topic"
  commands_topic: "your_random_commands_topic"
  commands_enabled: true
```

### 3. Install ntfy App

Install [ntfy.sh](https://ntfy.sh) on your phone and subscribe to your notification topic.

### 4. Start the Daemon

```bash
python3 -m schedule_manager.daemon
```

### 5. Set Up Siri (One Shortcut)

Create ONE iOS Shortcut called "Schedule":

1. **Shortcuts app** → **+** New Shortcut
2. **Add Action** → "Dictate Text"
3. **Add Action** → "Get Contents of URL"
   - URL: `https://ntfy.sh/YOUR_COMMANDS_TOPIC`
   - Method: POST
   - Request Body: File → Select "Dictated Text"
4. **Name it**: "Schedule"
5. **Add to Siri**: Record "Hey Siri, Schedule"

**That's it!** Now say "Hey Siri, Schedule" and speak naturally:
- "Add meeting tomorrow at 2pm"
- "What do I have today"
- "Remind me to call mom at 5"

## How It Works

```
You speak → Siri → iOS Shortcut → ntfy.sh → Daemon → AI Agent → Database
                                                            ↓
Your phone ← ntfy.sh ← Confirmation ←←←←←←←←←←←←←←←←←←←←←←←
```

The AI agent understands natural language - no special syntax or prefixes needed.

## Voice Command Examples

Just speak naturally:

| You Say | Result |
|---------|--------|
| "Add dentist appointment Friday at 10am" | Creates task |
| "Remind me to take out trash tomorrow" | Creates task |
| "What's on my schedule today" | Shows today's tasks |
| "What do I have this week" | Shows week view |
| "Complete task 5" | Marks task done |
| "Delete the dentist appointment" | Removes task |
| "Reschedule task 3 to 4pm" | Changes time |

### Priority

Say "urgent" or "important" for multiple reminders:
- "Add **urgent** meeting at 3pm" → Reminders at 2:45, 2:55, and 3:00
- "Add call mom at 3pm" → Single reminder at 3:00

## Configuration

### Notification Settings

```yaml
notifications:
  daily_summary_time: "07:00"  # Morning summary
  reminder_minutes_before: [0]  # Default: at task time only
  reminder_minutes_before_high_priority: [15, 5, 0]  # High priority: 3 reminders
```

### AI Agent Settings

```yaml
agent:
  enabled: true
  model: "ollama/gpt-oss:120b-128k"  # Or any Ollama model with tool support
  agent_name: "schedule"
  command_timeout_seconds: 90
```

## OpenCode Integration

The schedule manager includes an MCP server for OpenCode:

```json
// ~/.config/opencode/opencode.json
{
  "mcp": {
    "schedule-manager": {
      "type": "local",
      "command": ["/path/to/venv/bin/python3", "-m", "schedule_manager.mcp_server"],
      "environment": {"PYTHONPATH": "/path/to/schedule-manager"}
    }
  }
}
```

Then in OpenCode, just chat naturally:
- "Add a team meeting tomorrow at 10am"
- "Show me my schedule for this week"
- "Mark task 5 as complete"

## Running as a Service

### systemd (Linux)

```bash
sudo cp schedule-manager.service /etc/systemd/system/
sudo systemctl enable schedule-manager
sudo systemctl start schedule-manager
```

### Screen (Simple)

```bash
screen -S schedule-manager
python3 -m schedule_manager.daemon
# Ctrl+A, D to detach
```

## Project Structure

```
schedule-manager/
├── config.yaml              # Your configuration
├── data/schedule.db         # SQLite database
├── schedule_manager/
│   ├── core.py              # Main schedule logic
│   ├── daemon.py            # Background service
│   ├── agent.py             # AI agent (CLI mode)
│   ├── mcp_server.py        # OpenCode integration
│   ├── database.py          # Database operations
│   ├── notifications.py     # ntfy.sh integration
│   └── parser.py            # Natural language parsing
└── docs/                    # Documentation
```

## Troubleshooting

### Commands not working?

1. Check daemon is running: `ps aux | grep daemon`
2. Check logs: `tail -f daemon_output.log`
3. Test manually: `curl -d "what's on my schedule" https://ntfy.sh/YOUR_COMMANDS_TOPIC`

### Not receiving notifications?

1. Check you're subscribed to the **notification** topic (not commands topic)
2. Check ntfy.sh app permissions on your phone
3. Verify topic name matches config.yaml

### AI agent timing out?

Increase timeout in config.yaml:
```yaml
agent:
  command_timeout_seconds: 120
```

## Security

Your ntfy topics are like passwords:
- Use random, unguessable strings
- Don't share them publicly
- Anyone with your commands topic can control your schedule

Generate secure topics:
```bash
echo "schedule_$(openssl rand -hex 8)"
```

## License

MIT
