# AI Agent Mode Guide

## Overview

AI Agent Mode enhances the schedule manager with intelligent natural language understanding and conversation context. Instead of simple keyword matching, commands are processed by an AI agent that can:

- ✅ Understand natural variations ("call mom" vs "reminder to call mom")
- ✅ Maintain conversation context ("actually make it 5pm" - remembers previous task)
- ✅ Resolve ambiguity ("3" → infers 3pm based on context)
- ✅ Handle complex requests naturally
- ✅ Learn from conversation flow

## Architecture

```
Voice Command → ntfy.sh → Daemon → HealthCheck → OpenCode Agent (AI)
                                        ↓ (if fails)
                                  Simple Processor (Fallback)
                                        ↓
                              Response via ntfy.sh
```

### How It Works

1. **Daemon** spawns an OpenCode server process on startup
2. **OpenCode** runs a persistent AI agent (Claude, Ollama, etc.)
3. **Commands** are routed to the agent for intelligent processing
4. **Agent** uses MCP tools to manage schedule
5. **Responses** are sent back via ntfy.sh automatically
6. **Fallback**: If agent fails, simple processor handles commands

## Configuration

### Enable Agent Mode

Edit `config.yaml`:

```yaml
agent:
  enabled: true  # Enable AI agent mode
  port: 5555  # Port for OpenCode server
  model: "ollama/llama3.2"  # or "claude", "openai/gpt-4"
  agent_name: "schedule"  # OpenCode agent to use
  startup_timeout_seconds: 30
  health_check_timeout_seconds: 5
```

### Model Options

**Cloud Models** (requires API keys):
- `"claude"` - Anthropic Claude (recommended for quality)
- `"openai/gpt-4"` - OpenAI GPT-4
- `"openai/gpt-3.5-turbo"` - OpenAI GPT-3.5

**Local Models** (free, private):
- `"ollama/llama3.2"` - Llama 3.2 via Ollama
- `"ollama/mistral"` - Mistral via Ollama
- `"ollama/phi3"` - Phi-3 (smaller, faster)

### Prerequisites

1. **OpenCode** installed and in PATH
   ```bash
   which opencode  # Should show path
   ```

2. **For Ollama models**: Ollama installed and running
   ```bash
   ollama serve  # Start Ollama server
   ollama pull llama3.2  # Download model
   ```

3. **For cloud models**: API keys configured in OpenCode

## Usage

### Starting the Daemon

```bash
# With agent mode enabled in config
python3 -m schedule_manager.daemon --verbose
```

**Expected output**:
```
✅ AI Schedule Agent running
   Model: ollama/llama3.2
   Port: 5555
✅ Voice commands enabled (AI mode)
```

### If Agent Fails to Start

The daemon will:
1. Log the error
2. Send you a notification
3. Fall back to simple command processing
4. Continue operating (degraded mode)

**Notification**:
```
⚠️ Agent Startup Failed
AI agent failed to start. Using simple command processing.
Check logs for details.
```

### Sending Commands

Commands work the same way (ntfy.sh or iOS Shortcuts), but with AI intelligence:

**Simple mode**:
```
"remind me to call mom at 3"
→ Keyword match: "remind" + time parsing
→ Creates task literally as stated
```

**AI mode**:
```
"remind me to call mom at 3"
→ AI infers: 3pm (not 3am) based on time of day
→ AI understands: "remind me" = create task
→ AI formats: "Call mom" (natural title)
→ Creates optimized task
```

### Context Awareness

**Example conversation**:
```
You: "add meeting with bob tomorrow at 2pm"
AI: ✅ Added: Meeting with bob
📅 Mon Jan 13 at 02:00 PM

You: "actually make it 3pm"
AI: (remembers "it" = bob meeting)
✅ Rescheduled: Meeting with bob
🕐 New time: Mon Jan 13 at 03:00 PM

You: "add another one at 4pm"
AI: (knows you're talking about meetings with bob)
✅ Added: Meeting with bob
📅 Mon Jan 13 at 04:00 PM
```

In simple mode, "make it 3pm" would fail (no context).

## Error Handling

### Agent Goes Offline During Operation

```
You send: "add: reminder..."
↓
Health check fails (agent crashed/unresponsive)
↓
Notification: "⚠️ AI Agent Offline. Using simple processing."
↓
Command processed via simple processor
↓
Response sent normally
```

**No commands are lost!** The system automatically falls back.

### Agent Startup Timeout

If OpenCode doesn't start within timeout (default: 30s):
```
Error: OpenCode did not become ready within 30 seconds

Daemon continues with simple processor
Notification sent to alert you
```

### OpenCode Not Found

```
Error: OpenCode executable not found in PATH

Agent mode disabled
Simple processor used
Notification sent
```

## Monitoring

### Check Agent Status

View daemon logs for agent health:
```bash
# If using systemd
journalctl -u schedule-manager -f | grep -i agent

# If running manually
python3 -m schedule_manager.daemon --verbose
```

**Healthy agent**:
```
INFO: ✓ OpenCode agent started
INFO: Agent manager initialized: port=5555, model=ollama/llama3.2
INFO: Agent processed command: add: reminder...
```

**Agent issues**:
```
WARNING: Agent unavailable: OpenCode is not responding
INFO: Falling back to simple command processor
```

### Agent Process

Check if OpenCode is running:
```bash
ps aux | grep opencode

# Should show:
# opencode --port 5555 --model ollama/llama3.2 --agent schedule serve
```

### Health Check

The daemon performs health checks:
- Every time a command is sent
- Before routing to agent
- Falls back if unhealthy

## Troubleshooting

### Problem: Agent Won't Start

**Symptoms**:
- Daemon logs: "Failed to start OpenCode agent"
- Notification: "Agent Startup Failed"

**Solutions**:
1. Check OpenCode is installed:
   ```bash
   which opencode
   opencode --version
   ```

2. For Ollama models, ensure Ollama is running:
   ```bash
   ollama list  # Check models
   ollama serve  # Start server
   ```

3. Check ports aren't in use:
   ```bash
   lsof -i :5555  # Check if port is free
   ```

4. Try with increased timeout:
   ```yaml
   agent:
     startup_timeout_seconds: 60  # Give it more time
   ```

### Problem: Agent Slow to Respond

**Symptoms**:
- Commands take 10+ seconds
- Timeout errors

**Solutions**:
1. **For Ollama**: Ensure model is loaded
   ```bash
   ollama run llama3.2  # Pre-load model
   ```

2. **Switch to faster model**:
   ```yaml
   model: "ollama/phi3"  # Smaller, faster
   ```

3. **Use cloud model** for speed:
   ```yaml
   model: "claude"  # Faster than local
   ```

### Problem: Poor Understanding

**Symptoms**:
- Agent misinterprets commands
- Wrong times, dates, or actions

**Solutions**:
1. **Try different model**:
   ```yaml
   model: "claude"  # Better understanding
   ```

2. **Be more specific**:
   - Instead of: "remind me tomorrow"
   - Try: "remind me tomorrow at 3pm to call mom"

3. **Check model is appropriate**:
   - Llama3.2: Good balance
   - Phi3: Fast but less capable
   - Claude: Best understanding

### Problem: Agent Crashes Frequently

**Symptoms**:
- Frequent "Agent Offline" notifications
- Daemon logs show reconnection attempts

**Solutions**:
1. **Check system resources**:
   ```bash
   top  # CPU/Memory usage
   ```
   
2. **Ollama models need RAM**:
   - Llama3.2: ~8GB
   - Mistral: ~4GB
   - Phi3: ~2GB

3. **Switch to cloud model**:
   ```yaml
   model: "claude"  # No local resources needed
   ```

### Problem: Context Not Working

**Symptoms**:
- "make it 5pm" doesn't work
- Agent forgets previous commands

**Solutions**:
1. **Ensure agent mode is truly enabled**:
   - Check logs for "AI mode" vs "simple mode"
   - Verify `agent.enabled: true` in config

2. **Context has limits**:
   - Very old messages may be forgotten
   - After ~50 commands, oldest are dropped
   - Restart daemon for fresh context

3. **Be explicit when needed**:
   - Instead of: "cancel it"
   - Try: "cancel the meeting with bob"

## Performance Comparison

### Response Time

| Mode | Avg Response Time | Notes |
|------|------------------|-------|
| Simple | 200ms | Fast, no AI latency |
| Agent (Ollama local) | 2-5s | Depends on model/hardware |
| Agent (Claude) | 1-3s | Network + API latency |
| Agent (GPT-4) | 2-4s | Network + API latency |

### Quality

| Feature | Simple | AI Agent |
|---------|--------|----------|
| Exact matches | ✅ | ✅ |
| Natural language | ❌ | ✅ |
| Context awareness | ❌ | ✅ |
| Ambiguity resolution | ❌ | ✅ |
| Conversation flow | ❌ | ✅ |

### Cost

| Model | Cost | Notes |
|-------|------|-------|
| Simple processor | $0 | Free |
| Ollama (local) | $0 | Free, uses your hardware |
| Claude | ~$0.01-0.05/command | API costs |
| OpenAI | ~$0.01-0.10/command | API costs |

## Best Practices

### 1. Start with Local Model

Test with Ollama first (free):
```yaml
agent:
  enabled: true
  model: "ollama/llama3.2"
```

If it works well, stick with it. If not, try cloud.

### 2. Use Cloud for Production

For best reliability and understanding:
```yaml
agent:
  enabled: true
  model: "claude"
```

### 3. Monitor Logs

Always run with `--verbose` initially:
```bash
python3 -m schedule_manager.daemon --verbose
```

Check for:
- Agent startup success
- Command routing (AI vs simple)
- Error patterns

### 4. Have Fallback Ready

The system automatically falls back, but ensure:
- Simple processor still works
- Notifications still send
- Database still accessible

### 5. Context Management

For long-term use:
- Restart daemon weekly (fresh context)
- Or implement context pruning (future feature)

## Advanced Configuration

### Custom Startup Command

If you need custom OpenCode args, modify `agent.py`:

```python
def _spawn_process(self):
    cmd = [
        'opencode',
        '--port', str(self.port),
        '--model', self.model,
        '--agent', self.agent_name,
        '--custom-arg', 'value',  # Add your args
        'serve'
    ]
```

### Multiple Agents

Run multiple daemon instances with different agents:

```bash
# Instance 1: Claude for primary
python3 -m schedule_manager.daemon --config config_claude.yaml

# Instance 2: Ollama for testing
python3 -m schedule_manager.daemon --config config_ollama.yaml
```

Use different ports and topics for each.

### Agent Restart Script

Auto-restart agent on failure:

```bash
#!/bin/bash
while true; do
    python3 -m schedule_manager.daemon --verbose
    echo "Daemon stopped, restarting in 5s..."
    sleep 5
done
```

## Future Enhancements

Planned features:
- **Multi-turn clarification**: Agent asks questions via ntfy.sh
- **Conflict detection**: "You already have a meeting at that time"
- **Smart suggestions**: "Your usual lunch time is 12pm, schedule then?"
- **Learning preferences**: Remembers your patterns
- **Voice response**: Send audio responses back

## Summary

**Use AI Agent Mode when**:
- ✅ You want natural language understanding
- ✅ You need conversation context
- ✅ You're okay with 2-5 second response time
- ✅ You have OpenCode available

**Use Simple Mode when**:
- ✅ You want instant responses (<1s)
- ✅ You use exact command syntax
- ✅ You don't need context
- ✅ OpenCode isn't available

Both modes work via the same interface - switch anytime by toggling `agent.enabled` in config!

---

**Questions or issues?** Check the logs first, then see TROUBLESHOOTING.md
