# OpenCode MCP Configuration

## Quick Setup

Add this to your OpenCode config file:

**Location:** `~/.config/opencode/opencode.json`

```json
{
  "mcp": {
    "schedule-manager": {
      "type": "local",
      "command": [
        "/workspace/notes/schedule-manager/.venv/bin/python3",
        "-m",
        "schedule_manager.mcp_server"
      ],
      "environment": {
        "PYTHONPATH": "/workspace/notes/schedule-manager"
      }
    }
  }
}
```

**Important:** Replace `/workspace/notes/schedule-manager` with your actual path!

## How to Find Your OpenCode Config

```bash
# Linux/macOS
~/.config/opencode/opencode.json

# Check if it exists
ls -la ~/.config/opencode/opencode.json
```

## Verify Configuration

Test that it works:

```bash
# Should start without errors
opencode serve

# Should see: "opencode server listening on..."
# NOT: "Configuration is invalid"
```

## Works From Any Directory

Thanks to the code fix in `schedule_manager/core.py`, the MCP server will work regardless of where you start OpenCode:

```bash
cd ~
opencode        # ✅ schedule-manager tools work

cd ~/project
opencode .      # ✅ schedule-manager tools work

cd /tmp
opencode        # ✅ schedule-manager tools work
```

## Troubleshooting

### "Configuration is invalid"
- Check JSON syntax (use `python3 -m json.tool ~/.config/opencode/opencode.json`)
- Don't add unsupported fields like `cwd`
- Only use: `type`, `command`, `environment`, `enabled`, `timeout`

### "ModuleNotFoundError: No module named 'schedule_manager'"
- Check `PYTHONPATH` is set correctly in config
- Verify path exists: `ls /workspace/notes/schedule-manager`

### "Connection refused" or MCP tools not showing
- Verify daemon is running: `ps aux | grep schedule_manager.daemon`
- Check database exists: `ls /workspace/notes/schedule-manager/data/schedule.db`
- Restart OpenCode after config changes

## Available MCP Tools

Once configured, you'll have these tools in OpenCode:

- `schedule_add` - Add tasks with natural language
- `schedule_add_recurring` - Add recurring tasks
- `schedule_view` - View tasks for a date
- `schedule_complete` - Mark task as done
- `schedule_delete` - Remove task
- `schedule_update` - Update task details

## Example Usage

```
You: "Add a task to call mom tomorrow at 3pm"
OpenCode: [Uses schedule_add tool]
✓ Added: Call mom on Jan 14, 2026 at 3:00 PM

You: "What do I have today?"
OpenCode: [Uses schedule_view tool]
[Shows your schedule]
```

---

**That's it!** Your MCP server is ready to use from anywhere.
