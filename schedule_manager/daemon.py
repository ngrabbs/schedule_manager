"""
Notification daemon that runs in the background and sends scheduled notifications
"""

import time
import signal
import sys
import logging
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import pytz

from .core import ScheduleManager
from .command_listener import CommandListener
from .command_processor import CommandProcessor
from .agent import ScheduleAgent
from .exceptions import AgentUnavailableError, AgentStartupError, AgentCommunicationError
from .ip_monitor import IPMonitor

# Global logger
logger = logging.getLogger(__name__)


class NotificationDaemon:
    def __init__(self, config_path: str = "config.yaml", verbose: bool = False):
        """Initialize the notification daemon"""
        self.verbose = verbose
        logger.info("Initializing Schedule Manager Notification Daemon")
        logger.info(f"Loading configuration from: {config_path}")
        
        self.manager = ScheduleManager(config_path)
        self.scheduler = BackgroundScheduler()
        self.config = self.manager.config
        self.timezone = pytz.timezone(self.config['schedule']['timezone'])
        self.running = False
        
        logger.info(f"Database path: {self.manager.db.db_path}")
        logger.info(f"Timezone: {self.config['schedule']['timezone']}")
        logger.info(f"Ntfy topic: {self.config['ntfy']['topic']}")
        
        # Initialize command processing
        self.command_processor = CommandProcessor(self.manager)
        self.command_listener = None
        self.agent = None
        
        # Initialize IP monitor
        self.ip_monitor = IPMonitor(self.manager.db, self.manager.notifier)
        logger.info("IP monitor initialized")
        
        # Check if AI agent mode is enabled
        agent_enabled = self.config.get('agent', {}).get('enabled', False)
        if agent_enabled:
            logger.info("AI Agent mode enabled")
            try:
                self.agent = ScheduleAgent(self.config)
                logger.info(f"Agent initialized: {self.agent.model}")
            except Exception as e:
                logger.error(f"Failed to initialize agent: {e}")
                logger.info("Falling back to simple command processor")
                self.agent = None
        else:
            logger.info("AI Agent mode disabled, using simple command processor")
        
        # Check if commands are enabled
        commands_enabled = self.config['ntfy'].get('commands_enabled', False)
        commands_topic = self.config['ntfy'].get('commands_topic')
        
        if commands_enabled and commands_topic:
            logger.info(f"Voice commands enabled on topic: {commands_topic}")
            self.command_listener = CommandListener(
                server=self.config['ntfy']['server'],
                topic=commands_topic,
                on_command=self._handle_command,
                enabled=True
            )
        else:
            logger.info("Voice commands disabled")
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"\nReceived signal {signum}, shutting down gracefully...")
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        self.stop()
        sys.exit(0)
    
    def start(self):
        """Start the notification daemon"""
        print("🚀 Starting Schedule Manager Notification Daemon")
        print(f"   Topic: {self.config['ntfy']['topic']}")
        print(f"   Timezone: {self.config['schedule']['timezone']}")
        if self.verbose:
            print(f"   Verbose logging: ENABLED")
        
        logger.info("Starting scheduler...")
        
        # Schedule check for pending notifications (every minute)
        logger.info("Registering job: Check pending notifications (every 1 minute)")
        self.scheduler.add_job(
            self._check_pending_notifications,
            trigger=IntervalTrigger(minutes=1),
            id='check_notifications',
            name='Check pending notifications'
        )
        
        # Schedule daily summary
        summary_time = self.config['notifications']['daily_summary_time']
        hour, minute = summary_time.split(':')
        logger.info(f"Registering job: Daily summary at {summary_time}")
        self.scheduler.add_job(
            self._send_daily_summary,
            trigger=CronTrigger(hour=int(hour), minute=int(minute), timezone=self.timezone),
            id='daily_summary',
            name='Send daily summary'
        )
        
        # Schedule periodic upcoming summaries during work hours
        interval_minutes = self.config['notifications'].get('upcoming_summary_interval_minutes')
        if interval_minutes:
            logger.info(f"Registering job: Upcoming summary (every {interval_minutes} minutes)")
            self.scheduler.add_job(
                self._send_upcoming_summary,
                trigger=IntervalTrigger(minutes=interval_minutes),
                id='upcoming_summary',
                name='Send upcoming summary'
            )
        
        # Schedule recurring task generation (daily at midnight)
        logger.info("Registering job: Generate recurring tasks (daily at midnight)")
        self.scheduler.add_job(
            self._generate_recurring_tasks,
            trigger=CronTrigger(hour=0, minute=0, timezone=self.timezone),
            id='recurring_tasks',
            name='Generate recurring tasks'
        )
        
        # Schedule IP address monitoring (every 5 minutes)
        logger.info("Registering job: Check IP address (every 5 minutes)")
        self.scheduler.add_job(
            self._check_ip_address,
            trigger=IntervalTrigger(minutes=5),
            id='ip_monitor',
            name='Check IP address'
        )
        
        self.scheduler.start()
        self.running = True
        
        # Start AI agent if configured
        if self.agent:
            try:
                self.agent.start()
                logger.info("✓ OpenCode agent started")
                print("✅ AI Schedule Agent running")
                print(f"   Model: {self.agent.model}")
                print(f"   Port: {self.agent.port}")
            except AgentStartupError as e:
                logger.error(f"Failed to start AI agent: {e}")
                print(f"⚠️  AI agent failed to start: {e}")
                print("⚠️  Falling back to simple command processing")
                
                # Send notification about agent failure
                self.manager.notifier.send_notification(
                    title="⚠️ Agent Startup Failed",
                    message=f"AI agent failed to start. Using simple command processing. Error: {str(e)[:100]}",
                    priority="high"
                )
                
                # Disable agent
                self.agent = None
        
        # Start command listener if configured
        if self.command_listener:
            self.command_listener.start()
            logger.info("✓ Command listener started")
            if self.agent:
                print("✅ Voice commands enabled (AI mode)")
            else:
                print("✅ Voice commands enabled (simple mode)")
        
        logger.info("Scheduler started successfully")
        print("✅ Daemon started successfully")
        print("\nScheduled jobs:")
        for job in self.scheduler.get_jobs():
            print(f"   - {job.name} (next run: {job.next_run_time})")
            logger.info(f"Job scheduled: {job.name} (next run: {job.next_run_time})")
        
        if self.command_listener:
            print(f"\n🎤 Voice commands topic: {self.config['ntfy']['commands_topic']}")
        
        print("\n💡 Press Ctrl+C to stop\n")
        logger.info("Daemon is running. Press Ctrl+C to stop.")
        
        # Keep the daemon running
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the notification daemon"""
        logger.info("Stopping daemon...")
        print("Stopping daemon...")
        self.running = False
        
        # Stop AI agent first
        if self.agent:
            try:
                self.agent.stop()
                logger.info("AI agent stopped")
            except Exception as e:
                logger.error(f"Error stopping agent: {e}")
        
        # Stop command listener
        if self.command_listener:
            self.command_listener.stop()
            logger.info("Command listener stopped")
        
        # Stop scheduler
        if self.scheduler.running:
            self.scheduler.shutdown()
        
        logger.info("Daemon stopped successfully")
        print("✅ Daemon stopped")
    
    def _check_pending_notifications(self):
        """Check for pending notifications and send them"""
        now = datetime.now(self.timezone)
        logger.debug(f"Checking for pending notifications at {now.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get notifications that should be sent now
        pending = self.manager.db.get_pending_notifications(before_time=now)
        
        if pending:
            logger.info(f"Found {len(pending)} pending notification(s)")
        else:
            logger.debug("No pending notifications")
        
        for notification in pending:
            try:
                task_id = notification.get('task_id')
                notification_type = notification['notification_type']
                
                logger.debug(f"Processing notification ID {notification['id']}: type={notification_type}, task_id={task_id}")
                
                if notification_type == 'reminder' and task_id:
                    # Send task reminder
                    task = self.manager.db.get_task(task_id)
                    if task and task['status'] == 'pending':
                        scheduled_time = datetime.fromisoformat(task['scheduled_time'])
                        notification_time = datetime.fromisoformat(notification['notification_time'])
                        
                        # Calculate minutes before
                        time_diff = scheduled_time - notification_time
                        minutes_before = int(time_diff.total_seconds() / 60)
                        
                        logger.info(f"Sending reminder for task '{task['title']}' (ID: {task_id}, {minutes_before}min before)")
                        
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
                            logger.info(f"✓ Sent reminder for: {task['title']} (ntfy message ID: {message_id})")
                            print(f"✓ Sent reminder for: {task['title']}")
                    else:
                        logger.debug(f"Skipping notification: task status is {task.get('status') if task else 'not found'}")
                
            except Exception as e:
                logger.error(f"Error processing notification {notification['id']}: {e}", exc_info=True)
                print(f"Error processing notification {notification['id']}: {e}")
    
    def _send_daily_summary(self):
        """Send daily summary notification"""
        try:
            logger.info("Sending daily summary...")
            today = datetime.now(self.timezone)
            tasks = self.manager.get_tasks(date=today, status="pending")
            
            logger.debug(f"Found {len(tasks)} pending tasks for today")
            total_duration = sum(task.get('duration', 30) for task in tasks)
            
            message_id = self.manager.notifier.send_daily_summary(
                date=today,
                tasks=tasks,
                total_duration=total_duration
            )
            
            if message_id:
                logger.info(f"✓ Sent daily summary ({len(tasks)} tasks, {total_duration} min total)")
                print(f"✓ Sent daily summary ({len(tasks)} tasks)")
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}", exc_info=True)
            print(f"Error sending daily summary: {e}")
    
    def _send_upcoming_summary(self):
        """Send upcoming tasks summary (only during work hours)"""
        try:
            logger.debug("Checking if upcoming summary should be sent...")
            now = datetime.now(self.timezone)
            current_time = now.time()
            
            # Check if we're in work hours
            work_hours = self.config['notifications'].get('upcoming_summary_work_hours', ["09:00", "17:00"])
            start_hour, start_min = map(int, work_hours[0].split(':'))
            end_hour, end_min = map(int, work_hours[1].split(':'))
            
            work_start = now.replace(hour=start_hour, minute=start_min, second=0, microsecond=0).time()
            work_end = now.replace(hour=end_hour, minute=end_min, second=0, microsecond=0).time()
            
            if not (work_start <= current_time <= work_end):
                logger.debug(f"Outside work hours ({work_hours[0]}-{work_hours[1]}), skipping upcoming summary")
                return  # Outside work hours, skip
            
            # Check if it's a weekday (0-4 = Mon-Fri)
            if now.weekday() >= 5:
                logger.debug("Weekend, skipping upcoming summary")
                return  # Weekend, skip
            
            # Get upcoming tasks
            hours_ahead = 4
            tasks = self.manager.get_upcoming_tasks(hours_ahead=hours_ahead)
            
            if tasks:  # Only send if there are upcoming tasks
                logger.info(f"Sending upcoming summary for {len(tasks)} task(s) in next {hours_ahead}h")
                message_id = self.manager.notifier.send_upcoming_summary(
                    tasks=tasks,
                    hours_ahead=hours_ahead
                )
                
                if message_id:
                    logger.info(f"✓ Sent upcoming summary ({len(tasks)} tasks)")
                    print(f"✓ Sent upcoming summary ({len(tasks)} tasks)")
            else:
                logger.debug(f"No upcoming tasks in next {hours_ahead}h")
        except Exception as e:
            logger.error(f"Error sending upcoming summary: {e}", exc_info=True)
            print(f"Error sending upcoming summary: {e}")
    
    def _generate_recurring_tasks(self):
        """Generate instances of recurring tasks for the next day"""
        try:
            logger.info("Generating recurring task instances for tomorrow...")
            
            # Get all recurring tasks
            conn = self.manager.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE is_recurring = 1")
            recurring_tasks = [self.manager.db._row_to_dict(row) for row in cursor.fetchall()]
            conn.close()
            
            logger.debug(f"Found {len(recurring_tasks)} recurring task template(s)")
            
            tomorrow = datetime.now(self.timezone) + timedelta(days=1)
            tomorrow_weekday = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'][tomorrow.weekday()]
            
            logger.debug(f"Tomorrow is {tomorrow.strftime('%Y-%m-%d')} ({tomorrow_weekday})")
            
            created_count = 0
            for task in recurring_tasks:
                recurrence_rule = task.get('recurrence_rule')
                if not recurrence_rule:
                    logger.debug(f"Task '{task['title']}' has no recurrence rule, skipping")
                    continue
                
                days = recurrence_rule.get('days', [])
                time_str = recurrence_rule.get('time')
                
                logger.debug(f"Evaluating task '{task['title']}': days={days}, time={time_str}")
                
                # Check if task should occur tomorrow
                should_create = False
                if 'all' in days:
                    should_create = True
                    logger.debug(f"  -> Matches 'all' days")
                elif tomorrow_weekday in days:
                    should_create = True
                    logger.debug(f"  -> Matches {tomorrow_weekday}")
                else:
                    logger.debug(f"  -> Does not match (looking for {tomorrow_weekday})")
                
                if should_create and time_str:
                    # Parse time
                    hour, minute = map(int, time_str.split(':'))
                    scheduled_time = tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    logger.info(f"Creating instance: '{task['title']}' for {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
                    
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
                    
                    created_count += 1
                    print(f"✓ Created recurring task: {task['title']} for {tomorrow.strftime('%Y-%m-%d %H:%M')}")
            
            logger.info(f"Recurring task generation complete: created {created_count} instance(s)")
        
        except Exception as e:
            logger.error(f"Error generating recurring tasks: {e}", exc_info=True)
            print(f"Error generating recurring tasks: {e}")
    
    def _check_ip_address(self):
        """Check for IP address changes and notify"""
        try:
            logger.debug("Checking public IP address...")
            self.ip_monitor.check_and_notify()
        except Exception as e:
            logger.error(f"Error checking IP address: {e}", exc_info=True)
    
    def _handle_command(self, message: str, metadata: dict):
        """Handle an inbound command from the command listener"""
        try:
            message_id = metadata.get('id', 'unknown')
            logger.info(f"Processing command (msg_id: {message_id}): {message[:50]}...")
            
            # Route to AI agent if available
            if self.agent:
                try:
                    # Ensure agent is healthy before sending
                    self.agent._ensure_healthy()
                    
                    # Send to AI agent
                    logger.debug("Routing command to AI agent")
                    context = {
                        'source': 'ntfy',
                        'message_id': message_id,
                        'timestamp': metadata.get('time'),
                        'notifier': self.manager.notifier  # Pass notifier for responses
                    }
                    
                    result = self.agent.process_command(message, context)
                    
                    # Agent handles response automatically via MCP
                    logger.info(f"Agent processed command: {message[:30]}...")
                    
                    if self.verbose:
                        print(f"✓ AI Agent: {message[:40]}...")
                    
                    return  # Agent handled everything
                
                except AgentUnavailableError as e:
                    logger.error(f"Agent unavailable: {e}")
                    
                    # Send error notification to user
                    self.manager.notifier.send_notification(
                        title="⚠️ AI Agent Offline",
                        message="AI agent is not responding. Using simple command processing.",
                        priority="high"
                    )
                    
                    # Fall through to simple processor
                    logger.info("Falling back to simple command processor")
                
                except AgentCommunicationError as e:
                    logger.error(f"Agent communication error: {e}")
                    
                    # Send error notification
                    self.manager.notifier.send_error_response(
                        f"⚠️ Error communicating with AI agent. Using fallback."
                    )
                    
                    # Fall through to simple processor
                    logger.info("Falling back to simple command processor")
                
                except Exception as e:
                    logger.error(f"Unexpected error with agent: {e}", exc_info=True)
                    
                    # Fall through to simple processor
                    logger.info("Falling back to simple command processor")
            
            # Simple processor path (fallback or when agent disabled)
            logger.debug("Using simple command processor")
            result = self.command_processor.process_command(message, source=message_id)
            
            # Send response
            response_message = result.get('message', 'Command processed')
            success = result.get('success', False)
            
            if success:
                logger.info(f"Command successful: {message[:30]}...")
                self.manager.notifier.send_command_response(
                    message=response_message,
                    success=True,
                    priority='low'
                )
            else:
                logger.warning(f"Command failed: {message[:30]}...")
                self.manager.notifier.send_command_response(
                    message=response_message,
                    success=False,
                    priority='low'
                )
            
            if self.verbose:
                print(f"{'✓' if success else '✗'} Command: {message[:40]}...")
        
        except Exception as e:
            logger.error(f"Error handling command: {e}", exc_info=True)
            try:
                self.manager.notifier.send_error_response(
                    f"Internal error processing command: {str(e)}"
                )
            except:
                pass  # Don't let notification errors crash the handler


def main():
    """Main entry point for the daemon"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Schedule Manager Notification Daemon')
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging (shows all operations in detail)'
    )
    args = parser.parse_args()
    
    # Configure logging based on verbose flag
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    daemon = NotificationDaemon(config_path=args.config, verbose=args.verbose)
    daemon.start()


if __name__ == '__main__':
    main()
