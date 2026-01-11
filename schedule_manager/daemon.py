"""
Notification daemon that runs in the background and sends scheduled notifications
"""

import time
import signal
import sys
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import pytz

from .core import ScheduleManager


class NotificationDaemon:
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the notification daemon"""
        self.manager = ScheduleManager(config_path)
        self.scheduler = BackgroundScheduler()
        self.config = self.manager.config
        self.timezone = pytz.timezone(self.config['schedule']['timezone'])
        self.running = False
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        self.stop()
        sys.exit(0)
    
    def start(self):
        """Start the notification daemon"""
        print("🚀 Starting Schedule Manager Notification Daemon")
        print(f"   Topic: {self.config['ntfy']['topic']}")
        print(f"   Timezone: {self.config['schedule']['timezone']}")
        
        # Schedule check for pending notifications (every minute)
        self.scheduler.add_job(
            self._check_pending_notifications,
            trigger=IntervalTrigger(minutes=1),
            id='check_notifications',
            name='Check pending notifications'
        )
        
        # Schedule daily summary
        summary_time = self.config['notifications']['daily_summary_time']
        hour, minute = summary_time.split(':')
        self.scheduler.add_job(
            self._send_daily_summary,
            trigger=CronTrigger(hour=int(hour), minute=int(minute), timezone=self.timezone),
            id='daily_summary',
            name='Send daily summary'
        )
        
        # Schedule periodic upcoming summaries during work hours
        interval_minutes = self.config['notifications'].get('upcoming_summary_interval_minutes')
        if interval_minutes:
            self.scheduler.add_job(
                self._send_upcoming_summary,
                trigger=IntervalTrigger(minutes=interval_minutes),
                id='upcoming_summary',
                name='Send upcoming summary'
            )
        
        # Schedule recurring task generation (daily at midnight)
        self.scheduler.add_job(
            self._generate_recurring_tasks,
            trigger=CronTrigger(hour=0, minute=0, timezone=self.timezone),
            id='recurring_tasks',
            name='Generate recurring tasks'
        )
        
        self.scheduler.start()
        self.running = True
        
        print("✅ Daemon started successfully")
        print("\nScheduled jobs:")
        for job in self.scheduler.get_jobs():
            print(f"   - {job.name} (next run: {job.next_run_time})")
        
        print("\n💡 Press Ctrl+C to stop\n")
        
        # Keep the daemon running
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the notification daemon"""
        print("Stopping daemon...")
        self.running = False
        if self.scheduler.running:
            self.scheduler.shutdown()
        print("✅ Daemon stopped")
    
    def _check_pending_notifications(self):
        """Check for pending notifications and send them"""
        now = datetime.now(self.timezone)
        
        # Get notifications that should be sent now
        pending = self.manager.db.get_pending_notifications(before_time=now)
        
        for notification in pending:
            try:
                task_id = notification.get('task_id')
                notification_type = notification['notification_type']
                
                if notification_type == 'reminder' and task_id:
                    # Send task reminder
                    task = self.manager.db.get_task(task_id)
                    if task and task['status'] == 'pending':
                        scheduled_time = datetime.fromisoformat(task['scheduled_time'])
                        notification_time = datetime.fromisoformat(notification['notification_time'])
                        
                        # Calculate minutes before
                        time_diff = scheduled_time - notification_time
                        minutes_before = int(time_diff.total_seconds() / 60)
                        
                        message_id = self.manager.notifier.send_task_reminder(
                            task_title=task['title'],
                            task_description=task['description'],
                            scheduled_time=scheduled_time,
                            priority=task['priority'],
                            task_id=task_id,
                            minutes_before=minutes_before
                        )
                        
                        if message_id:
                            self.manager.db.mark_notification_sent(
                                notification['id'],
                                ntfy_message_id=message_id
                            )
                            print(f"✓ Sent reminder for: {task['title']}")
                
            except Exception as e:
                print(f"Error processing notification {notification['id']}: {e}")
    
    def _send_daily_summary(self):
        """Send daily summary notification"""
        try:
            today = datetime.now(self.timezone)
            tasks = self.manager.get_tasks(date=today, status="pending")
            
            total_duration = sum(task.get('duration', 30) for task in tasks)
            
            message_id = self.manager.notifier.send_daily_summary(
                date=today,
                tasks=tasks,
                total_duration=total_duration
            )
            
            if message_id:
                print(f"✓ Sent daily summary ({len(tasks)} tasks)")
        except Exception as e:
            print(f"Error sending daily summary: {e}")
    
    def _send_upcoming_summary(self):
        """Send upcoming tasks summary (only during work hours)"""
        try:
            now = datetime.now(self.timezone)
            current_time = now.time()
            
            # Check if we're in work hours
            work_hours = self.config['notifications'].get('upcoming_summary_work_hours', ["09:00", "17:00"])
            start_hour, start_min = map(int, work_hours[0].split(':'))
            end_hour, end_min = map(int, work_hours[1].split(':'))
            
            work_start = now.replace(hour=start_hour, minute=start_min, second=0, microsecond=0).time()
            work_end = now.replace(hour=end_hour, minute=end_min, second=0, microsecond=0).time()
            
            if not (work_start <= current_time <= work_end):
                return  # Outside work hours, skip
            
            # Check if it's a weekday (0-4 = Mon-Fri)
            if now.weekday() >= 5:
                return  # Weekend, skip
            
            # Get upcoming tasks
            hours_ahead = 4
            tasks = self.manager.get_upcoming_tasks(hours_ahead=hours_ahead)
            
            if tasks:  # Only send if there are upcoming tasks
                message_id = self.manager.notifier.send_upcoming_summary(
                    tasks=tasks,
                    hours_ahead=hours_ahead
                )
                
                if message_id:
                    print(f"✓ Sent upcoming summary ({len(tasks)} tasks)")
        except Exception as e:
            print(f"Error sending upcoming summary: {e}")
    
    def _generate_recurring_tasks(self):
        """Generate instances of recurring tasks for the next day"""
        try:
            # Get all recurring tasks
            conn = self.manager.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE is_recurring = 1")
            recurring_tasks = [self.manager.db._row_to_dict(row) for row in cursor.fetchall()]
            conn.close()
            
            tomorrow = datetime.now(self.timezone) + timedelta(days=1)
            tomorrow_weekday = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'][tomorrow.weekday()]
            
            for task in recurring_tasks:
                recurrence_rule = task.get('recurrence_rule')
                if not recurrence_rule:
                    continue
                
                days = recurrence_rule.get('days', [])
                time_str = recurrence_rule.get('time')
                
                # Check if task should occur tomorrow
                should_create = False
                if 'all' in days:
                    should_create = True
                elif tomorrow_weekday in days:
                    should_create = True
                
                if should_create and time_str:
                    # Parse time
                    hour, minute = map(int, time_str.split(':'))
                    scheduled_time = tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    # Create the task instance
                    self.manager.add_task(
                        title=task['title'],
                        description=task['description'],
                        scheduled_time=scheduled_time,
                        duration=task['duration'],
                        priority=task['priority'],
                        tags=task.get('tags'),
                        is_recurring=False  # This is an instance, not the template
                    )
                    
                    print(f"✓ Created recurring task: {task['title']} for {tomorrow.strftime('%Y-%m-%d %H:%M')}")
        
        except Exception as e:
            print(f"Error generating recurring tasks: {e}")


def main():
    """Main entry point for the daemon"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Schedule Manager Notification Daemon')
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    args = parser.parse_args()
    
    daemon = NotificationDaemon(config_path=args.config)
    daemon.start()


if __name__ == '__main__':
    main()
