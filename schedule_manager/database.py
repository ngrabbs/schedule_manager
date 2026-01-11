"""
Database management for schedule storage using SQLite
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path


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
        
        # Create indices for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_scheduled ON tasks(scheduled_time)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_time ON notifications(notification_time, sent)")
        
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
        
        return rows_affected > 0
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
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
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO notifications (task_id, notification_time, notification_type)
            VALUES (?, ?, ?)
        """, (task_id, notification_time.isoformat(), notification_type))
        
        notification_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return notification_id
    
    def get_pending_notifications(self, before_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get notifications that need to be sent"""
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
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in rows]
    
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
