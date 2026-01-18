# AI Agent

The schedule manager uses an AI agent to understand natural language commands.

## How It Works

When a voice command arrives, the daemon runs OpenCode CLI:

```bash
opencode --agent=schedule --model=ollama/gpt-oss:120b-128k run "your command"
```

The AI agent:
1. Parses natural language
2. Decides which MCP tool to call
3. Executes the tool (creates/modifies tasks)
4. Returns a confirmation

## Configuration

```yaml
# config.yaml
agent:
  enabled: true
  model: "ollama/gpt-oss:120b-128k"  # Must support tool calling
  agent_name: "schedule"              # Custom agent with MCP tools
  command_timeout_seconds: 90         # CLI timeout
```

### Model Requirements

The model must support **tool/function calling**. Not all models do.

**Working models:**
- `ollama/gpt-oss:120b-128k` (tested, works well)
- Models with `"tools": true` in OpenCode config

**Non-working models:**
- `ollama/llama3.2:3b` (doesn't support tools)
- Most small models

Check your OpenCode config (`~/.config/opencode/opencode.json`) for models with tool support.

## The Schedule Agent

Located at `~/.config/opencode/agent/schedule.md`:

```markdown
# Schedule Manager Agent

You are a direct, efficient schedule management assistant.

## Your Job
Manage the user's schedule using the schedule-manager MCP tools.
Execute commands immediately without commentary.

## Response Style
- DO: Show results directly
- DON'T: Explain what you're doing

## Available Tools
- schedule_add - Add tasks
- schedule_view - View tasks
- schedule_complete - Mark done
- schedule_delete - Remove tasks
- schedule_reschedule - Change time
...
```

This agent is configured to:
- Be concise (phone notifications are small)
- Use MCP tools directly
- Not explain itself unless asked

## MCP Tools

The agent has access to these tools via the schedule-manager MCP server:

| Tool | Purpose |
|------|---------|
| `schedule_add` | Add new task |
| `schedule_add_recurring` | Add recurring task |
| `schedule_view` | View tasks by date |
| `schedule_upcoming` | See next N hours |
| `schedule_summary` | Daily summary |
| `schedule_update` | Modify task |
| `schedule_reschedule` | Change time |
| `schedule_complete` | Mark done |
| `schedule_delete` | Remove task |

## CLI Mode vs Server Mode

We use **CLI mode** (per-command) instead of server mode:

| Aspect | CLI Mode | Server Mode |
|--------|----------|-------------|
| Startup | Fresh per command | Persistent server |
| Complexity | Simple subprocess | HTTP API, sessions |
| Memory | Clean between commands | Can accumulate |
| Debugging | Easy to reproduce | Harder |
| Code | ~130 lines | ~450 lines |

CLI mode is simpler and more reliable for voice commands which are independent and sporadic.

## Fallback Behavior

If the AI agent fails (timeout, error, unavailable), the daemon falls back to a simple keyword-based processor:

```python
# Simple processor handles basic patterns:
"add: call mom at 3pm"  → Creates task
"list"                   → Shows today
"complete: 5"            → Marks task done
```

This ensures commands still work even if the AI is unavailable.

## Troubleshooting

### Agent timing out

Increase timeout:
```yaml
agent:
  command_timeout_seconds: 120
```

### Agent not calling tools

Check the model supports tool calling. Try `gpt-oss:120b-128k`.

### Agent giving wrong responses

Check the agent prompt at `~/.config/opencode/agent/schedule.md`. It should instruct the agent to use tools directly.

### Testing manually

Run the same command the daemon would:

```bash
opencode --agent=schedule --model=ollama/gpt-oss:120b-128k run "add meeting tomorrow at 2pm"
```

Check:
- Tool calls shown in output
- Task created in database
- Reasonable response

## Code Reference

Main agent code: `schedule_manager/agent.py`

```python
class ScheduleAgent:
    def process_command(self, message, context):
        cmd = [
            'opencode',
            f'--agent={self.agent_name}',
            f'--model={self.model}',
            'run',
            message
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=self.command_timeout)
        return self._parse_output(result.stdout)
```

The implementation is intentionally simple - just subprocess + output parsing.
