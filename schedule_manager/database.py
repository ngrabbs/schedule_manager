"""
Database management for schedule storage using SQLite
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def init_db(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                scheduled_time TEXT,  -- ISO format datetime
                duration INTEGER DEFAULT 30,  -- Duration in minutes
                priority TEXT DEFAULT 'medium',  -- high, medium, low
                status TEXT DEFAULT 'pending',  -- pending, in_progress, completed, cancelled
                tags TEXT,  -- JSON array of tags
                is_recurring BOOLEAN DEFAULT 0,
                recurrence_rule TEXT,  -- JSON with recurrence rules (e.g., {"days": ["mon", "wed", "fri"], "time": "12:00"})
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT
            )
        """)
        
        # Notifications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                notification_time TEXT,
                notification_type TEXT,  -- reminder, summary, upcoming
                sent BOOLEAN DEFAULT 0,
                ntfy_message_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
        """)
        
        # IP history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ip_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT NOT NULL,
                detected_at TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indices for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_scheduled ON tasks(scheduled_time)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_time ON notifications(notification_time, sent)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ip_history_detected ON ip_history(detected_at)")
        
        conn.commit()
        conn.close()
    
    def add_task(
        self,
        title: str,
        description: Optional[str] = None,
        scheduled_time: Optional[datetime] = None,
        duration: int = 30,
        priority: str = "medium",
        tags: Optional[List[str]] = None,
        is_recurring: bool = False,
        recurrence_rule: Optional[Dict[str, Any]] = None
    ) -> int:
        """Add a new task"""
        logger.debug(f"DB: Adding task '{title}' (scheduled: {scheduled_time}, recurring: {is_recurring})")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO tasks (
                title, description, scheduled_time, duration, priority, 
                tags, is_recurring, recurrence_rule, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title,
            description,
            scheduled_time.isoformat() if scheduled_time else None,
            duration,
            priority,
            json.dumps(tags) if tags else None,
            is_recurring,
            json.dumps(recurrence_rule) if recurrence_rule else None,
            datetime.now().isoformat()
        ))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"DB: Added task ID {task_id}: '{title}'")
        return task_id
    
    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Get a single task by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_dict(row)
        return None
    
    def get_tasks(
        self,
        status: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        priority: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get tasks with optional filters"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if start_time:
            query += " AND scheduled_time >= ?"
            params.append(start_time.isoformat())
        
        if end_time:
            query += " AND scheduled_time <= ?"
            params.append(end_time.isoformat())
        
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        
        query += " ORDER BY scheduled_time ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in rows]
    
    def update_task(self, task_id: int, **kwargs) -> bool:
        """Update task fields"""
        if not kwargs:
            return False
        
        logger.debug(f"DB: Updating task {task_id}: {kwargs}")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Add updated_at timestamp
        kwargs['updated_at'] = datetime.now().isoformat()
        
        # Handle datetime objects
        if 'scheduled_time' in kwargs and isinstance(kwargs['scheduled_time'], datetime):
            kwargs['scheduled_time'] = kwargs['scheduled_time'].isoformat()
        
        # Handle JSON fields
        if 'tags' in kwargs and isinstance(kwargs['tags'], list):
            kwargs['tags'] = json.dumps(kwargs['tags'])
        
        if 'recurrence_rule' in kwargs and isinstance(kwargs['recurrence_rule'], dict):
            kwargs['recurrence_rule'] = json.dumps(kwargs['recurrence_rule'])
        
        # Build update query
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        query = f"UPDATE tasks SET {set_clause} WHERE id = ?"
        params = list(kwargs.values()) + [task_id]
        
        cursor.execute(query, params)
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        if rows_affected > 0:
            logger.info(f"DB: Updated task {task_id}")
        else:
            logger.warning(f"DB: Task {task_id} not found for update")
        
        return rows_affected > 0
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        logger.debug(f"DB: Deleting task {task_id}")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        if rows_affected > 0:
            logger.info(f"DB: Deleted task {task_id}")
        else:
            logger.warning(f"DB: Task {task_id} not found for deletion")
        
        return rows_affected > 0
    
    def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed"""
        return self.update_task(
            task_id,
            status='completed',
            completed_at=datetime.now().isoformat()
        )
    
    def add_notification(
        self,
        task_id: Optional[int],
        notification_time: datetime,
        notification_type: str = "reminder"
    ) -> int:
        """Schedule a notification"""
        logger.debug(f"DB: Adding notification for task {task_id} at {notification_time}")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO notifications (task_id, notification_time, notification_type)
            VALUES (?, ?, ?)
        """, (task_id, notification_time.isoformat(), notification_type))
        
        notification_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"DB: Added notification ID {notification_id} for task {task_id}")
        return notification_id
    
    def get_pending_notifications(self, before_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get notifications that need to be sent"""
        logger.debug(f"DB: Getting pending notifications (before_time={before_time.isoformat() if before_time else 'None'})")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT n.*, t.title, t.description, t.scheduled_time, t.priority, t.duration
            FROM notifications n
            LEFT JOIN tasks t ON n.task_id = t.id
            WHERE n.sent = 0
        """
        params = []
        
        if before_time:
            query += " AND n.notification_time <= ?"
            params.append(before_time.isoformat())
        
        query += " ORDER BY n.notification_time ASC"
        
        logger.debug(f"DB: Query: {query}")
        logger.debug(f"DB: Params: {params}")
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        result = [self._row_to_dict(row) for row in rows]
        logger.debug(f"DB: Found {len(result)} pending notification(s)")
        
        return result
    
    def mark_notification_sent(self, notification_id: int, ntfy_message_id: Optional[str] = None) -> bool:
        """Mark a notification as sent"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE notifications 
            SET sent = 1, ntfy_message_id = ?
            WHERE id = ?
        """, (ntfy_message_id, notification_id))
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_affected > 0
    
    def delete_notifications_for_task(self, task_id: int) -> int:
        """Delete all unsent notifications for a task"""
        logger.debug(f"DB: Deleting unsent notifications for task {task_id}")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM notifications WHERE task_id = ? AND sent = 0", (task_id,))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"DB: Deleted {rows_affected} unsent notification(s) for task {task_id}")
        return rows_affected
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert a database row to a dictionary"""
        result = dict(row)
        
        # Parse JSON fields
        if result.get('tags'):
            try:
                result['tags'] = json.loads(result['tags'])
            except:
                result['tags'] = []
        
        if result.get('recurrence_rule'):
            try:
                result['recurrence_rule'] = json.loads(result['recurrence_rule'])
            except:
                result['recurrence_rule'] = None
        
        return result
    
    def get_current_ip(self) -> Optional[str]:
        """Get the most recent IP address from history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ip_address FROM ip_history 
            ORDER BY detected_at DESC 
            LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return row['ip_address']
        return None
    
    def save_ip_address(self, ip_address: str, detected_at: datetime) -> int:
        """Save a new IP address to history"""
        logger.debug(f"DB: Saving IP address {ip_address}")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ip_history (ip_address, detected_at)
            VALUES (?, ?)
        """, (ip_address, detected_at.isoformat()))
        
        ip_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"DB: Saved IP address ID {ip_id}: {ip_address}")
        return ip_id
    
    def get_ip_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get IP address change history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM ip_history 
            ORDER BY detected_at DESC 
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
