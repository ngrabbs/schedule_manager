"""
Core schedule management logic
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import yaml
from pathlib import Path

from .database import Database
from .notifications import NtfyNotifier
from .nlp import DateTimeParser


class ScheduleManager:
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize schedule manager with configuration"""
        # If config_path is relative, look for it relative to this package
        config_path_obj = Path(config_path)
        if not config_path_obj.is_absolute():
            # Try current directory first
            if not config_path_obj.exists():
                # Fall back to package directory
                package_dir = Path(__file__).parent.parent
                config_path_obj = package_dir / config_path
        
        self.config = self._load_config(str(config_path_obj))
        
        # Initialize database
        db_path = self.config['database']['path']
        if not Path(db_path).is_absolute():
            config_dir = config_path_obj.parent
            db_path = str(config_dir / db_path)
        self.db = Database(db_path)
        
        # Initialize notifier
        ntfy_config = self.config['ntfy']
        self.notifier = NtfyNotifier(
            server=ntfy_config['server'],
            topic=ntfy_config['topic'],
            priority_map=ntfy_config.get('priority', {})
        )
        
        # Initialize NLP parser
        timezone = self.config['schedule']['timezone']
        self.parser = DateTimeParser(timezone)
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def add_task_natural(
        self,
        description: str,
        priority: str = "medium",
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Add a task using natural language
        
        Examples:
        - "Call mom tomorrow at 3pm for 30 minutes"
        - "Team meeting next monday at 10am, high priority"
        - "Buy groceries this friday afternoon"
        """
        
        # Parse time from description
        scheduled_time = self.parser.parse(description)
        
        # Parse duration
        duration = self.parser.parse_duration(description)
        
        # Extract title (first few words or whole thing if no time)
        title = description.split(' at ')[0].split(' tomorrow')[0].split(' next')[0].split(' this')[0].strip()
        if len(title) > 100:
            title = title[:100]
        
        # Check if this is a recurring task
        recurrence = self.parser.parse_recurrence(description)
        is_recurring = recurrence is not None
        
        task_id = self.db.add_task(
            title=title,
            description=description,
            scheduled_time=scheduled_time,
            duration=duration,
            priority=priority,
            tags=tags,
            is_recurring=is_recurring,
            recurrence_rule=recurrence
        )
        
        # Schedule notifications if task has a time
        if scheduled_time:
            self._schedule_task_notifications(task_id, scheduled_time, priority)
        
        # Get the created task
        task = self.db.get_task(task_id)
        
        return {
            'success': True,
            'task': task,
            'message': f"Added: '{title}'" + (f" scheduled for {scheduled_time.strftime('%Y-%m-%d %I:%M %p')}" if scheduled_time else "")
        }
    
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
    ) -> Dict[str, Any]:
        """Add a task with explicit parameters"""
        
        task_id = self.db.add_task(
            title=title,
            description=description,
            scheduled_time=scheduled_time,
            duration=duration,
            priority=priority,
            tags=tags,
            is_recurring=is_recurring,
            recurrence_rule=recurrence_rule
        )
        
        if scheduled_time:
            self._schedule_task_notifications(task_id, scheduled_time, priority)
        
        task = self.db.get_task(task_id)
        
        return {
            'success': True,
            'task': task,
            'message': f"Added: '{title}'"
        }
    
    def _schedule_task_notifications(self, task_id: int, scheduled_time: datetime, priority: str):
        """Schedule reminder notifications for a task"""
        reminder_minutes = self.config['notifications']['reminder_minutes_before']
        
        for minutes_before in reminder_minutes:
            notification_time = scheduled_time - timedelta(minutes=minutes_before)
            
            # Only schedule if notification time is in the future
            if notification_time > datetime.now(scheduled_time.tzinfo):
                self.db.add_notification(
                    task_id=task_id,
                    notification_time=notification_time,
                    notification_type='reminder'
                )
    
    def get_tasks(
        self,
        date: Optional[datetime] = None,
        status: str = "pending",
        days_ahead: int = 0
    ) -> List[Dict[str, Any]]:
        """Get tasks for a specific date or range"""
        
        if date is None:
            date = datetime.now(self.parser.timezone)
        
        start_time = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=days_ahead + 1)
        
        tasks = self.db.get_tasks(
            status=status,
            start_time=start_time,
            end_time=end_time
        )
        
        return tasks
    
    def get_upcoming_tasks(self, hours_ahead: int = 4) -> List[Dict[str, Any]]:
        """Get tasks coming up in the next N hours"""
        now = datetime.now(self.parser.timezone)
        end_time = now + timedelta(hours=hours_ahead)
        
        tasks = self.db.get_tasks(
            status="pending",
            start_time=now,
            end_time=end_time
        )
        
        return tasks
    
    def update_task(self, task_id: int, **kwargs) -> Dict[str, Any]:
        """Update a task"""
        success = self.db.update_task(task_id, **kwargs)
        
        if success:
            task = self.db.get_task(task_id)
            return {
                'success': True,
                'task': task,
                'message': f"Updated task {task_id}"
            }
        else:
            return {
                'success': False,
                'message': f"Task {task_id} not found"
            }
    
    def reschedule_task(self, task_id: int, new_time_description: str) -> Dict[str, Any]:
        """Reschedule a task using natural language"""
        new_time = self.parser.parse(new_time_description)
        
        if not new_time:
            return {
                'success': False,
                'message': f"Could not parse time from: {new_time_description}"
            }
        
        # Get task to check priority
        task = self.db.get_task(task_id)
        if not task:
            return {
                'success': False,
                'message': f"Task {task_id} not found"
            }
        
        # Update task
        success = self.db.update_task(task_id, scheduled_time=new_time)
        
        if success:
            # Reschedule notifications (delete old, create new)
            self.db.delete_notifications_for_task(task_id)
            self._schedule_task_notifications(task_id, new_time, task['priority'])
            
            task = self.db.get_task(task_id)
            return {
                'success': True,
                'task': task,
                'message': f"Rescheduled to {new_time.strftime('%Y-%m-%d %I:%M %p')}"
            }
        else:
            return {
                'success': False,
                'message': f"Task {task_id} not found"
            }
    
    def complete_task(self, task_id: int) -> Dict[str, Any]:
        """Mark a task as completed"""
        success = self.db.complete_task(task_id)
        
        if success:
            return {
                'success': True,
                'message': f"Completed task {task_id}"
            }
        else:
            return {
                'success': False,
                'message': f"Task {task_id} not found"
            }
    
    def delete_task(self, task_id: int) -> Dict[str, Any]:
        """Delete a task"""
        success = self.db.delete_task(task_id)
        
        if success:
            return {
                'success': True,
                'message': f"Deleted task {task_id}"
            }
        else:
            return {
                'success': False,
                'message': f"Task {task_id} not found"
            }
    
    def get_daily_summary(self, date: Optional[datetime] = None) -> str:
        """Generate a daily summary"""
        if date is None:
            date = datetime.now(self.parser.timezone)
        
        tasks = self.get_tasks(date=date, status="pending")
        
        if not tasks:
            return f"No tasks scheduled for {date.strftime('%A, %B %d')}. Enjoy your free time! 🎉"
        
        summary = f"📅 {date.strftime('%A, %B %d')}\n\n"
        total_duration = 0
        
        for task in tasks:
            if task['scheduled_time']:
                scheduled_time = datetime.fromisoformat(task['scheduled_time'])
                time_str = scheduled_time.strftime("%I:%M %p")
            else:
                time_str = "Unscheduled"
            
            duration = task.get('duration', 30)
            total_duration += duration
            
            priority_emoji = "🔴" if task['priority'] == 'high' else "🟡" if task['priority'] == 'medium' else "🟢"
            summary += f"{priority_emoji} {time_str} - {task['title']} ({duration}min)\n"
        
        # Calculate free time
        work_hours = 8 * 60
        free_time = work_hours - total_duration
        if free_time > 0:
            hours = free_time // 60
            minutes = free_time % 60
            summary += f"\n💡 Scheduled time: {total_duration}min | Free time: {hours}h {minutes}m"
        
        return summary
    
    def send_test_notification(self) -> bool:
        """Send a test notification"""
        message_id = self.notifier.send_test_notification()
        return message_id is not None
