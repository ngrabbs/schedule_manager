"""
Command processor for handling inbound commands from ntfy.sh
"""

import logging
import re
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class CommandProcessor:
    def __init__(self, schedule_manager):
        """
        Initialize command processor
        
        Args:
            schedule_manager: ScheduleManager instance to execute commands
        """
        self.manager = schedule_manager
        self.last_command_time = {}  # For rate limiting
        self.rate_limit_seconds = 1  # Minimum time between commands
    
    def process_command(self, message: str, source: str = "unknown") -> Dict[str, Any]:
        """
        Process an inbound command
        
        Args:
            message: Command text from ntfy.sh
            source: Source identifier for logging
        
        Returns:
            Dict with 'success', 'message', and optional 'data'
        """
        message = message.strip()
        
        if not message:
            return {
                'success': False,
                'message': "Empty command received"
            }
        
        logger.info(f"Processing command from {source}: {message[:50]}...")
        
        # Rate limiting check
        now = datetime.now()
        if source in self.last_command_time:
            time_diff = (now - self.last_command_time[source]).total_seconds()
            if time_diff < self.rate_limit_seconds:
                logger.warning(f"Rate limit exceeded for {source}")
                return {
                    'success': False,
                    'message': "⏱️ Please wait a moment between commands"
                }
        
        self.last_command_time[source] = now
        
        # Parse and route command
        try:
            # Add task command
            if message.lower().startswith('add:') or message.lower().startswith('add '):
                return self._handle_add(message)
            
            # List/today commands
            elif message.lower() in ['list', 'today', 'schedule']:
                return self._handle_list()
            
            # Upcoming commands
            elif message.lower().startswith('upcoming'):
                return self._handle_upcoming(message)
            
            # Complete task commands
            elif message.lower().startswith(('complete:', 'done:', 'complete ', 'done ')):
                return self._handle_complete(message)
            
            # Delete task commands
            elif message.lower().startswith(('delete:', 'remove:', 'delete ', 'remove ')):
                return self._handle_delete(message)
            
            # Reschedule task commands
            elif message.lower().startswith('reschedule:') or message.lower().startswith('reschedule '):
                return self._handle_reschedule(message)
            
            # Help command
            elif message.lower() in ['help', 'commands', '?']:
                return self._handle_help()
            
            # Unknown command
            else:
                logger.warning(f"Unknown command format: {message}")
                return {
                    'success': False,
                    'message': f"❌ Unknown command. Send 'help' for available commands."
                }
        
        except Exception as e:
            logger.error(f"Error processing command: {e}", exc_info=True)
            return {
                'success': False,
                'message': f"❌ Error: {str(e)}"
            }
    
    def _handle_add(self, message: str) -> Dict[str, Any]:
        """Handle add task command"""
        # Extract description after 'add:' or 'add '
        if ':' in message:
            description = message.split(':', 1)[1].strip()
        else:
            description = message.split(' ', 1)[1].strip() if ' ' in message else ''
        
        if not description:
            return {
                'success': False,
                'message': "❌ Please provide a task description\nExample: add: call mom tomorrow at 3pm"
            }
        
        try:
            result = self.manager.add_task_natural(description)
            
            if result['success']:
                task = result['task']
                scheduled_time = task.get('scheduled_time')
                
                if scheduled_time:
                    dt = datetime.fromisoformat(scheduled_time)
                    time_str = dt.strftime('%a %b %d at %I:%M %p')
                    response = f"✅ Added: {task['title']}\n📅 {time_str}"
                else:
                    response = f"✅ Added: {task['title']}"
                
                logger.info(f"Task added successfully: {task['title']}")
                return {
                    'success': True,
                    'message': response,
                    'data': {'task_id': task['id']}
                }
            else:
                return {
                    'success': False,
                    'message': f"❌ {result.get('message', 'Failed to add task')}"
                }
        
        except Exception as e:
            logger.error(f"Error adding task: {e}", exc_info=True)
            return {
                'success': False,
                'message': f"❌ Could not parse task description. Try: 'add: task description tomorrow at 3pm'"
            }
    
    def _handle_list(self) -> Dict[str, Any]:
        """Handle list/today command"""
        try:
            summary = self.manager.get_daily_summary()
            logger.info("Daily summary generated")
            
            return {
                'success': True,
                'message': summary,
                'data': {}
            }
        
        except Exception as e:
            logger.error(f"Error getting daily summary: {e}", exc_info=True)
            return {
                'success': False,
                'message': f"❌ Error getting schedule: {str(e)}"
            }
    
    def _handle_upcoming(self, message: str) -> Dict[str, Any]:
        """Handle upcoming command"""
        # Parse hours from message (e.g., "upcoming 4" or just "upcoming")
        hours_match = re.search(r'upcoming\s+(\d+)', message.lower())
        hours_ahead = int(hours_match.group(1)) if hours_match else 4
        
        # Limit to reasonable range
        hours_ahead = max(1, min(hours_ahead, 24))
        
        try:
            tasks = self.manager.get_upcoming_tasks(hours_ahead=hours_ahead)
            
            if not tasks:
                return {
                    'success': True,
                    'message': f"📋 No tasks in the next {hours_ahead} hour{'s' if hours_ahead > 1 else ''}\n\nYou're all clear! ✨",
                    'data': {}
                }
            
            # Format task list
            message_parts = [f"📋 Upcoming ({hours_ahead}h)\n"]
            
            for task in tasks:
                scheduled_time = datetime.fromisoformat(task['scheduled_time'])
                time_str = scheduled_time.strftime("%I:%M %p")
                
                # Calculate time until task
                now = datetime.now(scheduled_time.tzinfo)
                time_until = scheduled_time - now
                hours = int(time_until.total_seconds() // 3600)
                minutes = int((time_until.total_seconds() % 3600) // 60)
                
                if hours > 0:
                    time_desc = f"in {hours}h {minutes}m"
                elif minutes > 0:
                    time_desc = f"in {minutes}m"
                else:
                    time_desc = "now"
                
                emoji = "🔴" if task['priority'] == 'high' else "🟡" if task['priority'] == 'medium' else "🟢"
                message_parts.append(f"{emoji} {time_str} ({time_desc})\n   {task['title']}")
            
            logger.info(f"Upcoming tasks retrieved: {len(tasks)} tasks")
            
            return {
                'success': True,
                'message': "\n".join(message_parts),
                'data': {'task_count': len(tasks)}
            }
        
        except Exception as e:
            logger.error(f"Error getting upcoming tasks: {e}", exc_info=True)
            return {
                'success': False,
                'message': f"❌ Error getting upcoming tasks: {str(e)}"
            }
    
    def _handle_complete(self, message: str) -> Dict[str, Any]:
        """Handle complete/done command"""
        # Extract task ID
        task_id_match = re.search(r'(?:complete|done)[:\s]+(\d+)', message.lower())
        
        if not task_id_match:
            return {
                'success': False,
                'message': "❌ Please specify task ID\nExample: complete: 15"
            }
        
        task_id = int(task_id_match.group(1))
        
        try:
            # Get task info before completing
            task = self.manager.db.get_task(task_id)
            
            if not task:
                return {
                    'success': False,
                    'message': f"❌ Task {task_id} not found"
                }
            
            task_title = task['title']
            
            result = self.manager.complete_task(task_id)
            
            if result['success']:
                logger.info(f"Task {task_id} completed: {task_title}")
                return {
                    'success': True,
                    'message': f"✅ Completed: {task_title}",
                    'data': {'task_id': task_id}
                }
            else:
                return {
                    'success': False,
                    'message': f"❌ {result.get('message', 'Could not complete task')}"
                }
        
        except Exception as e:
            logger.error(f"Error completing task: {e}", exc_info=True)
            return {
                'success': False,
                'message': f"❌ Error completing task: {str(e)}"
            }
    
    def _handle_delete(self, message: str) -> Dict[str, Any]:
        """Handle delete/remove command"""
        # Extract task ID
        task_id_match = re.search(r'(?:delete|remove)[:\s]+(\d+)', message.lower())
        
        if not task_id_match:
            return {
                'success': False,
                'message': "❌ Please specify task ID\nExample: delete: 15"
            }
        
        task_id = int(task_id_match.group(1))
        
        try:
            # Get task info before deleting
            task = self.manager.db.get_task(task_id)
            
            if not task:
                return {
                    'success': False,
                    'message': f"❌ Task {task_id} not found"
                }
            
            task_title = task['title']
            
            result = self.manager.delete_task(task_id)
            
            if result['success']:
                logger.info(f"Task {task_id} deleted: {task_title}")
                return {
                    'success': True,
                    'message': f"🗑️ Deleted: {task_title}",
                    'data': {'task_id': task_id}
                }
            else:
                return {
                    'success': False,
                    'message': f"❌ {result.get('message', 'Could not delete task')}"
                }
        
        except Exception as e:
            logger.error(f"Error deleting task: {e}", exc_info=True)
            return {
                'success': False,
                'message': f"❌ Error deleting task: {str(e)}"
            }
    
    def _handle_reschedule(self, message: str) -> Dict[str, Any]:
        """Handle reschedule command"""
        # Parse "reschedule: 15 to tomorrow at 3pm"
        match = re.search(r'reschedule[:\s]+(\d+)\s+to\s+(.+)', message.lower())
        
        if not match:
            return {
                'success': False,
                'message': "❌ Invalid format\nExample: reschedule: 15 to tomorrow at 3pm"
            }
        
        task_id = int(match.group(1))
        new_time_desc = match.group(2).strip()
        
        try:
            # Get task info before rescheduling
            task = self.manager.db.get_task(task_id)
            
            if not task:
                return {
                    'success': False,
                    'message': f"❌ Task {task_id} not found"
                }
            
            task_title = task['title']
            
            result = self.manager.reschedule_task(task_id, new_time_desc)
            
            if result['success']:
                task = result['task']
                scheduled_time = datetime.fromisoformat(task['scheduled_time'])
                time_str = scheduled_time.strftime('%a %b %d at %I:%M %p')
                
                logger.info(f"Task {task_id} rescheduled: {task_title}")
                return {
                    'success': True,
                    'message': f"📅 Rescheduled: {task_title}\n🕐 New time: {time_str}",
                    'data': {'task_id': task_id}
                }
            else:
                return {
                    'success': False,
                    'message': f"❌ {result.get('message', 'Could not reschedule task')}"
                }
        
        except Exception as e:
            logger.error(f"Error rescheduling task: {e}", exc_info=True)
            return {
                'success': False,
                'message': f"❌ Error rescheduling task: {str(e)}"
            }
    
    def _handle_help(self) -> Dict[str, Any]:
        """Handle help command"""
        help_text = """📚 Available Commands

📝 Add Task:
   add: call mom tomorrow at 3pm

📅 View Schedule:
   list  (or 'today')

⏰ Upcoming Tasks:
   upcoming  (or 'upcoming 4')

✅ Complete Task:
   complete: 15  (or 'done: 15')

🗑️ Delete Task:
   delete: 15

📅 Reschedule Task:
   reschedule: 15 to 5pm

❓ Help:
   help  (or 'commands')
"""
        
        logger.info("Help command requested")
        return {
            'success': True,
            'message': help_text,
            'data': {}
        }
