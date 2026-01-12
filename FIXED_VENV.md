# ✅ Virtual Environment Fixed!

## What Was Wrong

Your `.venv` was created but the requirements weren't installed. The venv only had pip, wheel, and packaging - none of the actual dependencies.

## What I Did

1. **Recreated the venv:**
   ```bash
   cd /workspace/notes/schedule-manager
   rm -rf .venv
   python3 -m venv .venv
   ```

2. **Installed all requirements:**
   ```bash
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Verified MCP works:**
   ```bash
   python3 -c "import mcp; print('✅ MCP imported!')"
   ```

All packages installed successfully, including:
- ✅ requests
- ✅ python-dateutil  
- ✅ pytz
- ✅ pyyaml
- ✅ apscheduler
- ✅ **mcp** (with all dependencies)

## Now Try OpenCode

Restart OpenCode:

```bash
# Exit if running (Ctrl+C)
opencode
```

The MCP section should now show: **schedule-manager ✓**

## Test the MCP Server Works

You can test manually:

```bash
cd /workspace/notes/schedule-manager
source .venv/bin/activate
python3 -m schedule_manager.mcp_server
```

If it just waits for input (no errors), it's working! Press Ctrl+C to stop.

## Use It in OpenCode

Once OpenCode connects, try:

```
You: "use schedule_add to add a task"

Or just talk naturally:

You: "Add a task for dentist tomorrow at 2pm"
OpenCode: [Automatically uses schedule_add tool]
```

## Your OpenCode Config

The config is already set correctly at `/root/.config/opencode/opencode.json`:

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

## Two Separate Processes

Remember you have:

1. **Notification Daemon** (on your home server 192.168.1.250)
   ```bash
   python3 -m schedule_manager.daemon
   ```
   - Runs 24/7
   - Sends notifications via ntfy.sh

2. **MCP Server** (in this Docker container)
   ```bash
   python3 -m schedule_manager.mcp_server
   ```
   - Started automatically by OpenCode
   - Provides tools for schedule management
   - Only runs when OpenCode is running

Both access the same SQLite database at `/workspace/notes/schedule-manager/data/schedule.db`.

---

**Everything should work now!** Restart OpenCode and the MCP error should be gone. 🎉
