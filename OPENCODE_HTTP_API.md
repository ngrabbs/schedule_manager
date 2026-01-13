# OpenCode HTTP API Integration

## Overview

The Schedule Manager AI Agent now uses OpenCode's HTTP API to interact with AI models through a persistent session. This document explains the integration architecture and how it works.

## Architecture

```
Schedule Manager Daemon
        ↓
ScheduleAgent Manager
        ↓
OpenCode Server (HTTP)
        ↓
Session (persistent context)
        ↓
AI Model (Ollama/etc.)
```

## Key Components

### 1. Server Startup

The agent spawns an OpenCode server process:

```bash
opencode serve --port 5555 --hostname 127.0.0.1
```

**Note:** Model and agent are **NOT** specified at server startup (unlike previous versions). They are specified per-request.

### 2. Session Creation

After the server is ready, the agent creates a persistent HTTP session:

```http
POST http://localhost:5555/session
Content-Type: application/json

{
  "title": "Schedule Manager Agent"
}
```

**Response:**
```json
{
  "id": "ses_abc123...",
  "title": "Schedule Manager Agent",
  "time": { "created": 1234567890, "updated": 1234567890 }
}
```

The session ID is stored for all subsequent requests.

### 3. Sending Messages

To process a user command, the agent sends a message to the session:

```http
POST http://localhost:5555/session/{session_id}/message
Content-Type: application/json

{
  "parts": [
    {
      "type": "text",
      "text": "add: call mom tomorrow at 3pm"
    }
  ],
  "model": {
    "providerID": "ollama",
    "modelID": "llama3.2:3b"
  },
  "agent": "general",
  "system": "You are a scheduling assistant..."
}
```

**Response:**
```json
{
  "info": { 
    "id": "msg_xyz...",
    "role": "assistant",
    ...
  },
  "parts": [
    {
      "type": "text",
      "text": "I've added 'call mom' to your schedule for tomorrow at 3pm."
    }
  ]
}
```

### 4. Response Processing

The agent extracts text from the response parts:

```python
def _extract_text_from_parts(self, parts: list) -> str:
    text_parts = []
    for part in parts:
        if isinstance(part, dict) and part.get('type') == 'text':
            text_parts.append(part.get('text', ''))
    return '\n'.join(text_parts).strip()
```

### 5. Session Cleanup

When the agent stops, it deletes the session:

```http
DELETE http://localhost:5555/session/{session_id}
```

Then terminates the OpenCode server process.

## System Prompt

The agent includes a custom system prompt with each request to guide the AI's behavior:

```
You are a scheduling assistant integrated with a task management system.

Your role is to parse natural language commands and respond with clear, concise confirmations.

Available operations:
- ADD: Create new tasks
- VIEW: Show tasks  
- UPDATE: Modify task details
- RESCHEDULE: Change task time
- COMPLETE: Mark tasks done
- DELETE: Remove tasks
- RECURRING: Add repeating tasks

Guidelines:
- Be concise and direct in responses
- Confirm what action was taken
- If the command is unclear, ask for clarification
- Focus on scheduling operations only
- Parse dates/times naturally
```

## Configuration

The agent is configured via `config.yaml`:

```yaml
agent:
  enabled: true
  port: 5555
  model: "ollama/llama3.2:3b"  # Sent per-request
  agent_name: "general"         # Sent per-request
  startup_timeout_seconds: 30
  health_check_timeout_seconds: 5
```

## Benefits of Session-Based Architecture

1. **Conversation Context**: The AI remembers previous commands in the session
2. **Persistent Connection**: No need to restart OpenCode for each command
3. **Flexible Configuration**: Model and agent can be changed per-request
4. **Clean Separation**: Server lifecycle independent of AI configuration

## Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check if server is ready |
| `/session` | POST | Create new session |
| `/session/:id/message` | POST | Send message to session |
| `/session/:id` | DELETE | Delete session |

## Error Handling

The agent implements graceful error handling:

- **Server not ready**: Waits up to 30s for server startup
- **Session creation fails**: Raises `AgentStartupError`
- **Message timeout**: Raises `AgentCommunicationError` after 30s
- **Health check fails**: Sets `is_running = False` and raises `AgentUnavailableError`
- **Daemon fallback**: If agent unavailable, daemon falls back to simple processor

## Testing

A test script is available at `test_agent_http.py`:

```bash
python3 test_agent_http.py
```

This tests:
1. ✅ Server startup
2. ✅ Session creation
3. ✅ Message sending (requires Ollama)
4. ✅ Health checks
5. ✅ Session deletion
6. ✅ Graceful shutdown

## Next Steps

To enable full AI functionality:

1. **Install Ollama**: `curl -fsSL https://ollama.ai/install.sh | sh`
2. **Pull model**: `ollama pull llama3.2:3b`
3. **Enable agent**: Set `agent.enabled: true` in `config.yaml`
4. **Start daemon**: The agent will automatically start with the daemon

## Troubleshooting

### "OpenCode executable not found"
- Install OpenCode: `npm install -g @opencode-ai/opencode`
- Or ensure it's in PATH

### "Session creation failed: 400"
- Check OpenCode server logs
- Verify JSON payload matches schema
- Ensure `permission` field is omitted or array type

### "Message timeout after 30s"
- Check if Ollama is running: `ollama list`
- Verify model is available: `ollama pull llama3.2:3b`
- Check OpenCode server logs for errors

### "Agent not responding"
- Check health endpoint: `curl http://localhost:5555/health`
- Verify port not in use: `lsof -i :5555`
- Check firewall settings

## References

- OpenCode HTTP API: See `../opencode/packages/opencode/src/server/server.ts`
- Session schema: See `../opencode/packages/opencode/src/session/index.ts`
- Prompt schema: See `../opencode/packages/opencode/src/session/prompt.ts`
