# SQLite Database Guide

This guide shows you how to explore and manage the schedule-manager SQLite database from the command line.

## Database Location

The SQLite database is located at:
```
/path/to/schedule-manager/data/schedule.db
```

For example:
```
/home/ngrabbs/schedule-manager/data/schedule.db
```

## Installing SQLite Tools

If you don't have sqlite3 installed:

```bash
# Ubuntu/Debian
sudo apt-get install sqlite3

# CentOS/RHEL
sudo yum install sqlite

# macOS (usually pre-installed)
brew install sqlite3
```

## Quick Start: Open the Database

```bash
# Navigate to schedule-manager directory
cd /path/to/schedule-manager

# Open database
sqlite3 data/schedule.db
```

You'll see the SQLite prompt:
```
SQLite version 3.x.x
Enter ".help" for usage hints.
sqlite>
```

## Common SQLite Commands

### Show All Tables
```sql
.tables
```

Output:
```
ip_history     notifications  tasks
```

### Show Table Schema
```sql
.schema tasks
.schema notifications
.schema ip_history
```

### Enable Column Headers
```sql
.headers on
.mode column
```

### Exit SQLite
```sql
.quit
```
Or press `Ctrl+D`

## Querying the Database

### View All Tasks

```sql
SELECT * FROM tasks;
```

### View Pending Tasks Only

```sql
SELECT id, title, scheduled_time, priority, status 
FROM tasks 
WHERE status = 'pending'
ORDER BY scheduled_time;
```

### View Tasks for Today

```sql
SELECT id, title, scheduled_time, duration, priority
FROM tasks
WHERE date(scheduled_time) = date('now', 'localtime')
  AND status = 'pending'
ORDER BY scheduled_time;
```

### View Recurring Tasks

```sql
SELECT id, title, recurrence_rule
FROM tasks
WHERE is_recurring = 1;
```

### View Recent Notifications

```sql
SELECT n.id, n.notification_type, n.notification_time, n.sent, t.title
FROM notifications n
LEFT JOIN tasks t ON n.task_id = t.id
ORDER BY n.notification_time DESC
LIMIT 10;
```

### View IP Address History

```sql
-- All IP changes
SELECT * FROM ip_history ORDER BY detected_at DESC;

-- Last 5 IP changes
SELECT ip_address, detected_at, created_at
FROM ip_history
ORDER BY detected_at DESC
LIMIT 5;

-- Current IP
SELECT ip_address, detected_at
FROM ip_history
ORDER BY detected_at DESC
LIMIT 1;

-- Count IP changes
SELECT COUNT(*) as total_changes FROM ip_history;
```

## Useful Queries

### Count Tasks by Status

```sql
SELECT status, COUNT(*) as count
FROM tasks
GROUP BY status;
```

### Tasks Due This Week

```sql
SELECT title, scheduled_time, priority
FROM tasks
WHERE scheduled_time BETWEEN datetime('now') 
      AND datetime('now', '+7 days')
  AND status = 'pending'
ORDER BY scheduled_time;
```

### High Priority Tasks

```sql
SELECT id, title, scheduled_time, status
FROM tasks
WHERE priority = 'high'
  AND status = 'pending'
ORDER BY scheduled_time;
```

### Notifications Not Yet Sent

```sql
SELECT n.notification_type, n.notification_time, t.title
FROM notifications n
JOIN tasks t ON n.task_id = t.id
WHERE n.sent = 0
  AND n.notification_time > datetime('now')
ORDER BY n.notification_time;
```

### Task Statistics

```sql
SELECT 
    COUNT(*) as total_tasks,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled
FROM tasks;
```

## One-Line Commands (Without Opening SQLite)

Execute queries directly from bash:

```bash
# View all tasks
sqlite3 data/schedule.db "SELECT * FROM tasks;"

# View IP history
sqlite3 data/schedule.db "SELECT * FROM ip_history ORDER BY detected_at DESC LIMIT 5;"

# Count pending tasks
sqlite3 data/schedule.db "SELECT COUNT(*) FROM tasks WHERE status='pending';"

# Current IP
sqlite3 data/schedule.db "SELECT ip_address FROM ip_history ORDER BY detected_at DESC LIMIT 1;"

# Pretty formatting
sqlite3 -header -column data/schedule.db "SELECT * FROM tasks WHERE status='pending';"
```

## Modifying Data (Dangerous!)

⚠️ **Warning**: Modifying data directly can break the schedule-manager. Make backups first!

### Backup First!

```bash
# Create backup
cp data/schedule.db data/schedule.db.backup

# Or with timestamp
cp data/schedule.db data/schedule.db.$(date +%Y%m%d_%H%M%S).backup
```

### Delete a Task

```sql
DELETE FROM tasks WHERE id = 123;
```

### Mark Task as Completed

```sql
UPDATE tasks 
SET status = 'completed', 
    completed_at = datetime('now')
WHERE id = 123;
```

### Clear Old IP History

```sql
-- Keep only last 100 entries
DELETE FROM ip_history 
WHERE id NOT IN (
    SELECT id FROM ip_history 
    ORDER BY detected_at DESC 
    LIMIT 100
);
```

### Delete All Completed Tasks

```sql
-- Be careful with this!
DELETE FROM tasks WHERE status = 'completed';
```

## Exporting Data

### Export to CSV

```bash
# Export all tasks
sqlite3 -header -csv data/schedule.db "SELECT * FROM tasks;" > tasks_export.csv

# Export IP history
sqlite3 -header -csv data/schedule.db "SELECT * FROM ip_history;" > ip_history.csv
```

### Export to JSON (requires jq)

```bash
sqlite3 data/schedule.db "SELECT * FROM tasks;" | jq -R 'split("|")' > tasks.json
```

### Full Database Dump

```bash
# SQL dump (can restore later)
sqlite3 data/schedule.db .dump > schedule_backup.sql

# Restore from dump
sqlite3 data/schedule_new.db < schedule_backup.sql
```

## Python Access

You can also access the database using Python:

```python
#!/usr/bin/env python3
from schedule_manager.core import ScheduleManager

# Initialize manager
manager = ScheduleManager()

# Get current IP
current_ip = manager.db.get_current_ip()
print(f"Current IP: {current_ip}")

# Get IP history
history = manager.db.get_ip_history(limit=10)
for entry in history:
    print(f"{entry['ip_address']} at {entry['detected_at']}")

# Get pending tasks
tasks = manager.get_tasks(status='pending')
print(f"\nFound {len(tasks)} pending tasks:")
for task in tasks:
    print(f"  - {task['title']} ({task['scheduled_time']})")

# Get task by ID
task = manager.db.get_task(task_id=1)
if task:
    print(f"\nTask 1: {task}")
```

Save as `db_query.py` and run:
```bash
cd /path/to/schedule-manager
python3 db_query.py
```

## Database Schema Reference

### tasks table

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    scheduled_time TEXT,           -- ISO format: 2026-01-13T15:30:00
    duration INTEGER DEFAULT 30,   -- Minutes
    priority TEXT DEFAULT 'medium', -- 'high', 'medium', 'low'
    status TEXT DEFAULT 'pending',  -- 'pending', 'in_progress', 'completed', 'cancelled'
    tags TEXT,                      -- JSON array: ["work", "urgent"]
    is_recurring BOOLEAN DEFAULT 0,
    recurrence_rule TEXT,           -- JSON: {"days": ["mon", "wed"], "time": "12:00"}
    created_at TEXT,
    updated_at TEXT,
    completed_at TEXT
);
```

### notifications table

```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER,                -- References tasks(id)
    notification_time TEXT,         -- When to send
    notification_type TEXT,         -- 'reminder', 'summary', 'upcoming'
    sent BOOLEAN DEFAULT 0,
    ntfy_message_id TEXT,
    created_at TEXT,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);
```

### ip_history table

```sql
CREATE TABLE ip_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT NOT NULL,
    detected_at TEXT NOT NULL,      -- When IP was detected
    created_at TEXT                 -- Database entry timestamp
);
```

## Troubleshooting

### Database Locked Error

If you get "database is locked":
- The daemon is running and has the database open
- Close other sqlite3 sessions
- Use read-only mode: `sqlite3 -readonly data/schedule.db`

### Corrupted Database

```bash
# Check integrity
sqlite3 data/schedule.db "PRAGMA integrity_check;"

# If corrupted, restore from backup
cp data/schedule.db.backup data/schedule.db
```

### Vacuum (Optimize) Database

```bash
sqlite3 data/schedule.db "VACUUM;"
```

## Quick Reference Card

```bash
# Open database
sqlite3 data/schedule.db

# Inside sqlite3:
.tables                          # List tables
.schema TABLE_NAME               # Show table structure
.headers on                      # Show column names
.mode column                     # Pretty formatting
.quit                            # Exit

# Queries:
SELECT * FROM tasks;             # All tasks
SELECT * FROM ip_history;        # All IP changes
SELECT COUNT(*) FROM tasks;      # Count tasks

# From bash (one-line):
sqlite3 data/schedule.db "SELECT * FROM tasks;"
sqlite3 -header -column data/schedule.db "SELECT * FROM ip_history;"
```

## Additional Resources

- SQLite official docs: https://www.sqlite.org/docs.html
- SQLite CLI reference: https://www.sqlite.org/cli.html
- SQL tutorial: https://www.sqlitetutorial.net/

---

**Pro Tip**: For complex queries or regular database inspection, create a `queries.sql` file with your common queries and run it with:

```bash
sqlite3 data/schedule.db < queries.sql
```
