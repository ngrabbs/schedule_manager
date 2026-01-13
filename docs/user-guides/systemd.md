# Running Schedule Manager as a System Service

This guide shows you how to run the schedule-manager daemon automatically as a systemd service, so it starts on boot and restarts on failure.

## Quick Start

Replace `yourusername` with your actual Linux username (e.g., `ngrabbs`):

```bash
# 1. Copy the service file
sudo cp schedule-manager.service /etc/systemd/system/schedule-manager@.service

# 2. Reload systemd to recognize the new service
sudo systemctl daemon-reload

# 3. Enable the service to start on boot
sudo systemctl enable schedule-manager@yourusername

# 4. Start the service now
sudo systemctl start schedule-manager@yourusername

# 5. Check that it's running
sudo systemctl status schedule-manager@yourusername
```

## Common Commands

### Check Service Status
```bash
sudo systemctl status schedule-manager@yourusername
```

### Start the Service
```bash
sudo systemctl start schedule-manager@yourusername
```

### Stop the Service
```bash
sudo systemctl stop schedule-manager@yourusername
```

### Restart the Service
```bash
sudo systemctl restart schedule-manager@yourusername
```

### View Logs (Live)
```bash
# View logs in real-time
sudo journalctl -u schedule-manager@yourusername -f

# View last 50 lines
sudo journalctl -u schedule-manager@yourusername -n 50

# View logs from today
sudo journalctl -u schedule-manager@yourusername --since today

# View logs with timestamps
sudo journalctl -u schedule-manager@yourusername -f --output=short-iso
```

### Disable Auto-Start on Boot
```bash
sudo systemctl disable schedule-manager@yourusername
```

### Re-enable Auto-Start
```bash
sudo systemctl enable schedule-manager@yourusername
```

## Service File Location

The service file should be installed at:
```
/etc/systemd/system/schedule-manager@.service
```

## Important Notes

### Working Directory

The service expects the schedule-manager to be located at:
```
/home/yourusername/schedule-manager
```

If your schedule-manager is in a different location, you need to edit the service file:

```bash
# Edit the service file
sudo nano /etc/systemd/system/schedule-manager@.service

# Change these lines to your actual path:
WorkingDirectory=/path/to/your/schedule-manager
ExecStart=/usr/bin/python3 -m schedule_manager.daemon --config /path/to/your/schedule-manager/config.yaml

# Then reload systemd
sudo systemctl daemon-reload
sudo systemctl restart schedule-manager@yourusername
```

### After Making Changes

Whenever you:
- Update the schedule-manager code
- Change config.yaml
- Modify the service file

You need to restart the service:

```bash
# If you modified the .service file:
sudo systemctl daemon-reload

# Always restart after changes:
sudo systemctl restart schedule-manager@yourusername
```

## Troubleshooting

### Service Won't Start

1. Check the status for errors:
   ```bash
   sudo systemctl status schedule-manager@yourusername
   ```

2. View full logs:
   ```bash
   sudo journalctl -u schedule-manager@yourusername -n 100
   ```

3. Check file permissions:
   ```bash
   ls -la /home/yourusername/schedule-manager/
   ```

4. Test manually first:
   ```bash
   cd /home/yourusername/schedule-manager
   python3 -m schedule_manager.daemon --verbose
   ```

### Service Keeps Restarting

Check logs to see why it's crashing:
```bash
sudo journalctl -u schedule-manager@yourusername -f
```

Common issues:
- Config file missing or malformed
- Database permissions
- ntfy.sh credentials incorrect
- Python dependencies missing

### Check If Service is Running

```bash
# Quick check
sudo systemctl is-active schedule-manager@yourusername

# Detailed status
sudo systemctl status schedule-manager@yourusername

# Or check process list
ps aux | grep schedule_manager
```

### View Service Configuration

```bash
sudo systemctl cat schedule-manager@yourusername
```

## Service Features

The systemd service provides:

✅ **Auto-start on boot** - Daemon starts automatically when system boots  
✅ **Auto-restart on failure** - If daemon crashes, systemd restarts it after 10 seconds  
✅ **Proper logging** - Logs go to systemd journal (viewable with `journalctl`)  
✅ **User isolation** - Runs as your user, not root  
✅ **Clean shutdown** - Handles system shutdown gracefully  

## Example: Complete Setup for User "ngrabbs"

```bash
# Stop if running manually
# (Press Ctrl+C if you have python3 -m schedule_manager.daemon running)

# Copy service file
sudo cp /home/ngrabbs/schedule-manager/schedule-manager.service \
     /etc/systemd/system/schedule-manager@.service

# Reload systemd
sudo systemctl daemon-reload

# Enable and start
sudo systemctl enable schedule-manager@ngrabbs
sudo systemctl start schedule-manager@ngrabbs

# Verify it's running
sudo systemctl status schedule-manager@ngrabbs

# Watch logs
sudo journalctl -u schedule-manager@ngrabbs -f
```

You should see output like:
```
● schedule-manager@ngrabbs.service - AI Schedule Manager Notification Daemon
     Loaded: loaded (/etc/systemd/system/schedule-manager@.service; enabled)
     Active: active (running) since Mon 2026-01-13 17:00:00 CST
   Main PID: 12345 (python3)
     Status: "Running..."
      Tasks: 3
     Memory: 45.2M
        CPU: 1.234s
     CGroup: /system.slice/schedule-manager@ngrabbs.service
             └─12345 /usr/bin/python3 -m schedule_manager.daemon
```

## Stopping Manual Execution

If you currently have the daemon running manually (`python3 -m schedule_manager.daemon`):

1. Press `Ctrl+C` to stop it
2. Start the systemd service instead
3. The systemd service will take over

**Don't run both at the same time!** Either run manually OR as a systemd service, not both.

## Alternative: Run in Screen/Tmux (if systemd not available)

If you can't use systemd, use screen or tmux:

```bash
# Using screen
screen -S schedule-manager
cd /home/yourusername/schedule-manager
python3 -m schedule_manager.daemon

# Detach: Press Ctrl+A, then D
# Reattach: screen -r schedule-manager
# Stop: Reattach and press Ctrl+C

# Using tmux
tmux new -s schedule-manager
cd /home/yourusername/schedule-manager
python3 -m schedule_manager.daemon

# Detach: Press Ctrl+B, then D
# Reattach: tmux attach -t schedule-manager
# Stop: Reattach and press Ctrl+C
```

---

**Recommendation**: Use systemd if available. It's more reliable and provides better logging and auto-restart capabilities.
