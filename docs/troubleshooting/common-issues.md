# Common Issues & Troubleshooting

Solutions to frequently encountered problems with the Schedule Manager.

## Installation Issues

### ModuleNotFoundError: No module named 'requests'

**Problem:** Python dependencies not installed.

**Solution:**
```bash
pip3 install -r requirements.txt

# Or with virtual environment:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Permission Denied Errors

**Problem:** File permissions are incorrect.

**Solution:**
```bash
# Fix permissions
chmod 755 schedule_manager/*.py
chmod 644 schedule.db config.yaml

# If running as service:
sudo chown $USER:$USER schedule.db daemon.log
```

### Database Errors on Startup

**Problem:** Database file corrupt or missing.

**Solution:**
```bash
# Backup existing database (if any)
cp schedule.db schedule.db.backup

# Recreate database
rm schedule.db
python3 -m schedule_manager.database

# Restore data if needed (manual)
```

## Notification Issues

### Not Receiving Any Notifications

**Problem:** ntfy.sh not configured correctly.

**Troubleshooting:**

1. **Test notification system:**
   ```python
   python3 -c "from schedule_manager.core import ScheduleManager; ScheduleManager().send_test_notification()"
   ```

2. **Check ntfy.sh subscription:**
   - Open ntfy.sh app
   - Verify you're subscribed to the topic from `config.yaml`
   - Check topic name matches exactly (case-sensitive!)

3. **Verify config:**
   ```bash
   cat config.yaml | grep topic
   ```

4. **Test with curl:**
   ```bash
   curl -d "Test message" https://ntfy.sh/YOUR_TOPIC
   ```

### Notifications Work But Commands Don't

**Problem:** Command topic misconfigured or daemon not listening.

**Solution:**

1. **Check daemon is running:**
   ```bash
   ps aux | grep daemon
   ```

2. **Start daemon in verbose mode:**
   ```bash
   python3 -m schedule_manager.daemon --verbose
   ```

3. **Test command manually:**
   ```bash
   curl -d "help" https://ntfy.sh/YOUR_COMMAND_TOPIC
   ```

4. **Verify two topics in config:**
   ```yaml
   ntfy:
     topic: "notifications_here"  # For receiving notifications
     command_topic: "commands_here"  # For sending commands
   ```

### Duplicate Notifications

**Problem:** Multiple daemons running or daemon started multiple times.

**Solution:**
```bash
# Kill all running daemons
pkill -f "schedule_manager.daemon"

# Start single daemon
python3 -m schedule_manager.daemon
```

## Daemon Issues

### Daemon Crashes on Startup

**Problem:** Configuration error or missing dependencies.

**Troubleshooting:**

1. **Check logs:**
   ```bash
   tail -50 daemon.log
   ```

2. **Run in foreground:**
   ```bash
   python3 -m schedule_manager.daemon --verbose
   ```

3. **Validate config:**
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"
   ```

4. **Check Python version:**
   ```bash
   python3 --version  # Should be 3.8+
   ```

### Daemon Stops After Some Time

**Problem:** Unhandled exception or system resource issue.

**Solution:**

1. **Use systemd service:** (auto-restart)
   ```bash
   sudo systemctl enable schedule-manager@$USER
   sudo systemctl start schedule-manager@$USER
   ```

2. **Check system resources:**
   ```bash
   free -h  # Check memory
   df -h    # Check disk space
   ```

3. **Monitor with journalctl:**
   ```bash
   journalctl -u schedule-manager -f
   ```

### Command Listener Not Receiving Messages

**Problem:** Network connectivity or ntfy.sh blocking.

**Solution:**

1. **Test ntfy.sh connectivity:**
   ```bash
   curl https://ntfy.sh/YOUR_COMMAND_TOPIC/json?poll=1
   ```

2. **Check firewall:**
   ```bash
   # Ensure outbound HTTPS allowed
   curl https://ntfy.sh
   ```

3. **Try custom ntfy server:**
   ```yaml
   # config.yaml
   ntfy:
     server: "https://ntfy.sh"  # Or self-hosted server
   ```

## Task Management Issues

### Natural Language Parsing Fails

**Problem:** Dateutil can't parse your date/time format.

**Solution:**

Use more explicit formats:
```
❌ Don't: "add: meeting sometime next week"
✅ Do: "add: meeting monday at 2pm"

❌ Don't: "add: call later"
✅ Do: "add: call in 2 hours"
```

### Tasks Not Showing Up

**Problem:** Tasks in database but not returned by queries.

**Troubleshooting:**

1. **Check database directly:**
   ```bash
   sqlite3 schedule.db "SELECT * FROM tasks WHERE status='pending' LIMIT 10;"
   ```

2. **Verify date range:**
   ```python
   from schedule_manager.core import ScheduleManager
   mgr = ScheduleManager()
   tasks = mgr.get_tasks(start_date="2026-01-01", end_date="2026-12-31")
   print(len(tasks))
   ```

3. **Check task status:**
   ```bash
   sqlite3 schedule.db "SELECT status, COUNT(*) FROM tasks GROUP BY status;"
   ```

### Recurring Tasks Not Generating

**Problem:** APScheduler not running or schedule empty.

**Solution:**

1. **Check scheduled jobs:**
   ```python
   from schedule_manager.daemon import NotificationDaemon
   daemon = NotificationDaemon()
   daemon.start()
   print(daemon.scheduler.get_jobs())
   ```

2. **Manually trigger:**
   ```python
   from schedule_manager.core import ScheduleManager
   ScheduleManager().generate_recurring_tasks()
   ```

3. **Verify recurring task config:**
   ```bash
   sqlite3 schedule.db "SELECT * FROM tasks WHERE is_recurring=1;"
   ```

## OpenCode MCP Integration Issues

### OpenCode Not Finding Schedule Tools

**Problem:** MCP server not registered or path incorrect.

**Solution:**

1. **Check MCP config location:**
   ```bash
   # Linux/macOS
   cat ~/.config/opencode/mcp.json
   
   # Windows
   type %APPDATA%\opencode\mcp.json
   ```

2. **Verify config format:**
   ```json
   {
     "schedule-manager": {
       "command": "python3",
       "args": ["-m", "schedule_manager.mcp_server"],
       "cwd": "/FULL/PATH/to/schedule-manager"
     }
   }
   ```

3. **Test MCP server directly:**
   ```bash
   python3 -m schedule_manager.mcp_server
   # Should start MCP server
   ```

4. **Restart OpenCode:**
   ```bash
   pkill opencode
   opencode
   ```

### MCP Server Crashes

**Problem:** Error in MCP server code or dependency issue.

**Solution:**

1. **Check MCP logs:**
   ```bash
   # OpenCode logs usually in:
   tail -f ~/.opencode/logs/mcp.log
   ```

2. **Test tools individually:**
   ```python
   from schedule_manager.core import ScheduleManager
   mgr = ScheduleManager()
   result = mgr.add_task_natural("test tomorrow at 3pm")
   print(result)
   ```

## AI Agent Issues

### Agent Not Starting

**Problem:** OpenCode or Ollama not installed/configured.

**Solution:**

1. **Check OpenCode installation:**
   ```bash
   which opencode
   opencode --version
   ```

2. **Install if missing:**
   ```bash
   npm install -g @opencode-ai/opencode
   ```

3. **Check Ollama:**
   ```bash
   ollama --version
   ollama list  # Should show llama3.2:3b
   ```

4. **Disable agent if not needed:**
   ```yaml
   # config.yaml
   agent:
     enabled: false
   ```

### Agent Timeout Errors

**Problem:** AI model taking too long to respond.

**Solution:**

1. **Check Ollama is running:**
   ```bash
   ps aux | grep ollama
   ```

2. **Test model directly:**
   ```bash
   ollama run llama3.2:3b "Hello"
   ```

3. **Increase timeout:**
   ```yaml
   # config.yaml
   agent:
     startup_timeout_seconds: 60  # Default: 30
   ```

4. **Try smaller model:**
   ```yaml
   agent:
     model: "ollama/llama3.2:1b"  # Faster, smaller
   ```

### Agent Session Errors

**Problem:** OpenCode session creation failing.

**Solution:**

1. **Check OpenCode server:**
   ```bash
   curl http://localhost:5555/health
   ```

2. **Check logs:**
   ```bash
   tail -f daemon.log | grep -i agent
   ```

3. **Restart with agent disabled:**
   ```bash
   # Temporarily disable to verify rest works
   sed -i 's/enabled: true/enabled: false/' config.yaml
   python3 -m schedule_manager.daemon
   ```

## Performance Issues

### High CPU Usage

**Problem:** AI agent consuming resources.

**Solution:**

1. **Disable AI agent if not needed:**
   ```yaml
   agent:
     enabled: false
   ```

2. **Use lighter model:**
   ```yaml
   agent:
     model: "ollama/llama3.2:1b"
   ```

3. **Reduce notification frequency:**
   ```yaml
   notifications:
     upcoming_interval_hours: 4  # Instead of 2
   ```

### High Memory Usage

**Problem:** Database or AI model loaded in memory.

**Solution:**

1. **Restart daemon periodically:**
   ```bash
   # Add to cron
   0 3 * * * systemctl restart schedule-manager@$USER
   ```

2. **Clean old tasks:**
   ```bash
   sqlite3 schedule.db "DELETE FROM tasks WHERE status='completed' AND scheduled_time < date('now', '-30 days');"
   ```

3. **Use smaller AI model** (see CPU section above)

## Network Issues

### Can't Reach ntfy.sh

**Problem:** Network connectivity or firewall blocking.

**Solution:**

1. **Test connectivity:**
   ```bash
   curl https://ntfy.sh
   ping ntfy.sh
   ```

2. **Check proxy settings:**
   ```bash
   env | grep -i proxy
   ```

3. **Use self-hosted ntfy:**
   ```yaml
   ntfy:
     server: "https://your-ntfy-server.com"
   ```

### SSL Certificate Errors

**Problem:** System certificates out of date.

**Solution:**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ca-certificates

# macOS
brew install ca-certificates

# Then restart daemon
```

## Getting More Help

### Enable Debug Logging

```python
# Edit daemon.py temporarily:
logging.basicConfig(level=logging.DEBUG)
```

### Collect Diagnostic Information

```bash
# System info
python3 --version
pip3 list | grep -E 'requests|dateutil|pytz|yaml|apscheduler'

# Check processes
ps aux | grep -E 'daemon|opencode|ollama'

# Check logs
tail -100 daemon.log

# Check database
sqlite3 schedule.db .schema
sqlite3 schedule.db "SELECT COUNT(*) FROM tasks;"

# Check config
cat config.yaml
```

### Report an Issue

When reporting issues, include:

1. Error message (full traceback)
2. Daemon logs (`tail -100 daemon.log`)
3. Python version (`python3 --version`)
4. OS and version
5. Steps to reproduce
6. What you've already tried

## Quick Diagnostic Commands

```bash
# All-in-one health check
echo "=== Python Version ===" && python3 --version && \
echo "=== Dependencies ===" && pip3 list | grep -E 'requests|dateutil|pytz|yaml|apscheduler' && \
echo "=== Daemon Running? ===" && ps aux | grep daemon && \
echo "=== Database ===" && sqlite3 schedule.db "SELECT COUNT(*) FROM tasks;" && \
echo "=== Config ===" && cat config.yaml | grep -A 3 ntfy && \
echo "=== Recent Logs ===" && tail -20 daemon.log
```

## Prevention Best Practices

1. **Use systemd service** for auto-restart
2. **Monitor logs regularly**
3. **Keep topics secret**
4. **Backup database periodically:**
   ```bash
   cp schedule.db schedule.db.$(date +%Y%m%d)
   ```
5. **Test after updates:**
   ```bash
   python3 test_command_listener.py test
   ```

---

**Still stuck?** Check the specialized troubleshooting guides:
- [iOS Shortcuts Issues](ios-shortcuts.md)
- [Installation Guide](../getting-started/installation.md)
- [AI Agent Guide](../developer/ai-agent.md)
