# Install MCP Server Support

## The Issue

You're seeing: `schedule-manager MCP error -32000: connection closed`

This is because the `mcp` Python package isn't installed in your venv.

## Fix It

On your server (`192.168.1.250`):

```bash
cd /home/ngrabbs/notes/schedule-manager
source .venv/bin/activate

# Install the MCP package
pip install mcp

# Or reinstall all requirements
pip install -r requirements.txt
```

## Verify It Works

Test the MCP server manually:

```bash
cd /home/ngrabbs/notes/schedule-manager
source .venv/bin/activate

# This should start the MCP server (it will wait for input)
python3 -m schedule_manager.mcp_server
```

If you see no errors and it just waits, that's good! Press Ctrl+C to stop.

## Then Restart OpenCode

After installing `mcp`, restart OpenCode:

```bash
# In your OpenCode terminal, press Ctrl+C to exit
# Then start again:
opencode
```

OpenCode should now show "schedule-manager ✓" in the MCP section instead of an error!

## What's Running What

You have **two separate processes**:

### 1. Notification Daemon (already running ✓)
```bash
python3 -m schedule_manager.daemon
```
- Runs in background
- Sends notifications at scheduled times
- Generates recurring tasks
- You keep this running 24/7

### 2. MCP Server (started by OpenCode)
```bash
python3 -m schedule_manager.mcp_server
```
- Started automatically by OpenCode when you open it
- Provides tools for OpenCode to manage your schedule
- Only runs when OpenCode is running

## After Installing

Once `mcp` is installed, you can use these tools in OpenCode:

```
You: "schedule_add call mom tomorrow at 3pm"
OpenCode: ✓ Added task

You: "schedule_view today" 
OpenCode: [Shows your schedule]

You: "schedule_summary"
OpenCode: [Shows formatted daily summary]
```

Or just talk naturally:

```
You: "Add a task to review code tomorrow at 2pm"
OpenCode: [Uses schedule_add tool automatically]
```

---

**TL;DR: Run `pip install mcp` in your venv, then restart OpenCode!** 🚀
