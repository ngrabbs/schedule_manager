# Running Schedule Manager in Docker

You're running inside a Docker container, so systemd is **not available**. This guide shows you the best ways to run the schedule-manager daemon in a Docker environment.

## Current Situation

You're inside a Docker container where:
- PID 1 is `sshd`, not systemd
- `systemctl` commands won't work
- The container is already running and persistent

## ✅ Recommended Approaches for Docker

### Option 1: Supervisor (Recommended for Docker)

Supervisor is the standard process manager for Docker containers.

#### Install Supervisor

```bash
apt-get update
apt-get install -y supervisor
```

#### Create Supervisor Config

```bash
cat > /etc/supervisor/conf.d/schedule-manager.conf <<'EOF'
[program:schedule-manager]
command=/usr/bin/python3 -m schedule_manager.daemon
directory=/workspace/notes/schedule-manager
autostart=true
autorestart=true
stderr_logfile=/var/log/schedule-manager.err.log
stdout_logfile=/var/log/schedule-manager.out.log
user=root
environment=PYTHONUNBUFFERED=1
EOF
```

#### Start Supervisor

```bash
# Start supervisor
supervisord -c /etc/supervisor/supervisord.conf

# Or if already running, reload config
supervisorctl reread
supervisorctl update
supervisorctl start schedule-manager
```

#### Manage the Daemon

```bash
# Status
supervisorctl status schedule-manager

# Start
supervisorctl start schedule-manager

# Stop
supervisorctl stop schedule-manager

# Restart
supervisorctl restart schedule-manager

# View logs
tail -f /var/log/schedule-manager.out.log
tail -f /var/log/schedule-manager.err.log

# Or use supervisorctl
supervisorctl tail -f schedule-manager
supervisorctl tail -f schedule-manager stderr
```

---

### Option 2: Screen/Tmux (Quick & Easy)

Perfect for development or if you don't want to install supervisor.

#### Using Screen

```bash
# Start in screen
screen -S schedule-manager -dm bash -c 'cd /workspace/notes/schedule-manager && python3 -m schedule_manager.daemon'

# Check if running
screen -ls

# Attach to see output
screen -r schedule-manager

# Detach: Press Ctrl+A, then D

# Stop
screen -S schedule-manager -X quit
```

#### Using Tmux

```bash
# Start in tmux
tmux new-session -d -s schedule-manager 'cd /workspace/notes/schedule-manager && python3 -m schedule_manager.daemon'

# Check if running
tmux ls

# Attach to see output
tmux attach -t schedule-manager

# Detach: Press Ctrl+B, then D

# Stop
tmux kill-session -t schedule-manager
```

---

### Option 3: Background Process with nohup

Simple but less robust (no auto-restart on failure).

```bash
cd /workspace/notes/schedule-manager

# Start
nohup python3 -m schedule_manager.daemon > daemon.log 2>&1 &

# Get the PID
echo $! > daemon.pid

# Check if running
ps aux | grep schedule_manager.daemon | grep -v grep

# View logs
tail -f daemon.log

# Stop
kill $(cat daemon.pid)
# Or
pkill -f "schedule_manager.daemon"
```

---

### Option 4: Simple Startup Script

Create a script that runs on container start.

#### Create Startup Script

```bash
cat > /usr/local/bin/start-schedule-manager.sh <<'EOF'
#!/bin/bash
cd /workspace/notes/schedule-manager
exec python3 -m schedule_manager.daemon
EOF

chmod +x /usr/local/bin/start-schedule-manager.sh
```

#### Add to Container Startup

If you have access to modify the container startup:

```bash
# Add to .bashrc or .profile
echo '/usr/local/bin/start-schedule-manager.sh &' >> ~/.bashrc
```

Or run manually:
```bash
/usr/local/bin/start-schedule-manager.sh &
```

---

## 🔧 Making it Persistent Across Container Restarts

### If You Control the Dockerfile

Add to your `Dockerfile`:

```dockerfile
# Install supervisor
RUN apt-get update && apt-get install -y supervisor

# Copy supervisor config
COPY schedule-manager.supervisor.conf /etc/supervisor/conf.d/schedule-manager.conf

# Start supervisor on container startup
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
```

### If Container Already Exists

You need to ensure the process starts when the container starts:

1. **Option A: Modify container startup command** (if you have access)
2. **Option B: Use screen/tmux** and reconnect after restart
3. **Option C: Run manually** after each container restart
4. **Option D: Create a systemd service on the HOST** that runs `docker exec` (see below)

---

## 🐳 Alternative: Run on Docker Host (Outside Container)

If you have access to the Docker host, you can run the daemon there:

### On Docker Host Machine

```bash
# Create systemd service on HOST
sudo nano /etc/systemd/system/schedule-manager-docker.service
```

```ini
[Unit]
Description=Schedule Manager in Docker
After=docker.service
Requires=docker.service

[Service]
Type=simple
ExecStart=/usr/bin/docker exec -it your-container-name bash -c "cd /workspace/notes/schedule-manager && python3 -m schedule_manager.daemon"
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable schedule-manager-docker
sudo systemctl start schedule-manager-docker
```

This way systemd on the HOST manages the process inside the container.

---

## 📊 Comparison Table

| Method | Auto-Restart | Easy Setup | Persistent | Best For |
|--------|-------------|------------|------------|----------|
| **Supervisor** | ✅ Yes | Medium | ✅ Yes* | Production |
| **Screen** | ❌ No | ✅ Easy | ✅ Yes | Development |
| **Tmux** | ❌ No | ✅ Easy | ✅ Yes | Development |
| **nohup** | ❌ No | ✅ Easy | ❌ No | Testing |
| **Host systemd** | ✅ Yes | Hard | ✅ Yes | If you control host |

\* Requires supervisor to start on container boot

---

## 🎯 My Recommendation for Your Setup

Since you're in a Docker container, I recommend **Screen or Tmux** for now because:

1. ✅ Quick to set up (no installation needed)
2. ✅ Survives SSH disconnections
3. ✅ Easy to attach and see logs
4. ✅ Simple to stop/restart
5. ✅ Good for development/testing

**For production**, upgrade to **Supervisor** for automatic restarts.

---

## 🚀 Quick Start (Recommended)

```bash
# Option 1: Screen (recommended)
screen -S schedule-manager -dm bash -c 'cd /workspace/notes/schedule-manager && python3 -m schedule_manager.daemon'

# Verify it's running
screen -ls
ps aux | grep schedule_manager

# View logs (attach to screen)
screen -r schedule-manager
# Detach: Ctrl+A, then D

# Stop
screen -S schedule-manager -X quit
```

```bash
# Option 2: Tmux (alternative)
tmux new-session -d -s schedule-manager 'cd /workspace/notes/schedule-manager && python3 -m schedule_manager.daemon'

# Verify
tmux ls
ps aux | grep schedule_manager

# View logs
tmux attach -t schedule-manager
# Detach: Ctrl+B, then D

# Stop
tmux kill-session -t schedule-manager
```

---

## 🔍 Checking if Daemon is Running

```bash
# Check process
ps aux | grep schedule_manager.daemon | grep -v grep

# Check screen sessions
screen -ls

# Check tmux sessions
tmux ls

# Check supervisor (if using)
supervisorctl status schedule-manager
```

---

## 📝 Notes

- **systemd won't work** in your Docker container (PID 1 is sshd, not systemd)
- The systemd documentation (SYSTEMD_SETUP.md) is only relevant if you run schedule-manager on a traditional Linux host
- For Docker, stick with Supervisor, Screen, or Tmux
- Make sure your container has persistent storage for the database (`/workspace/notes/schedule-manager/data/`)

---

## 🆘 Troubleshooting

### Daemon stops when I disconnect SSH

Use **screen** or **tmux** instead of running directly in the terminal.

### How do I make it start automatically when container restarts?

- Install and configure **Supervisor** (see Option 1 above)
- Or add to container startup script
- Or use host systemd with `docker exec` (if you control the host)

### Can't install supervisor

```bash
# Try screen or tmux instead (usually pre-installed)
which screen
which tmux

# If not installed:
apt-get update
apt-get install -y screen tmux
```

### Process keeps dying

Check logs:
```bash
# If using screen
screen -r schedule-manager

# If using nohup
tail -f /workspace/notes/schedule-manager/daemon.log

# If using supervisor
tail -f /var/log/schedule-manager.err.log
```

---

**Bottom Line**: For Docker, forget systemd. Use Screen/Tmux for simplicity, or Supervisor for production reliability.
