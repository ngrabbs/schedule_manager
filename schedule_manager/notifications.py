"""
ntfy.sh notification integration
"""

import requests
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta


class NtfyNotifier:
    def __init__(self, server: str, topic: str, priority_map: Optional[Dict[str, str]] = None):
        """
        Initialize ntfy.sh notifier
        
        Args:
            server: ntfy.sh server URL (e.g., "https://ntfy.sh")
            topic: Topic name to publish to
            priority_map: Map of priority levels (high/medium/low) to ntfy priorities
        """
        self.server = server.rstrip('/')
        self.topic = topic
        self.priority_map = priority_map or {
            'high': 'urgent',
            'medium': 'high',
            'low': 'default'
        }
    
    def send_notification(
        self,
        title: str,
        message: str,
        priority: str = 'medium',
        tags: Optional[List[str]] = None,
        actions: Optional[List[Dict[str, str]]] = None,
        attach: Optional[str] = None,
        click_url: Optional[str] = None
    ) -> Optional[str]:
        """
        Send a notification via ntfy.sh
        
        Args:
            title: Notification title
            message: Notification message body
            priority: Priority level (high/medium/low)
            tags: List of emoji tags
            actions: List of action buttons
            attach: URL to attach (for images, etc.)
            click_url: URL to open when notification is clicked
        
        Returns:
            Message ID from ntfy.sh, or None if failed
        """
        # POST to topic endpoint with UTF-8 message body and headers
        url = f"{self.server}/{self.topic}"
        
        # Build headers
        headers = {
            "Priority": self.priority_map.get(priority, 'default'),
        }
        
        # Handle title with emojis
        # HTTP headers only support latin-1, so we need to handle UTF-8 specially
        if title:
            # Check if title contains non-latin-1 characters (like emojis)
            try:
                title.encode('latin-1')
                # If this succeeds, title is latin-1 safe
                headers["Title"] = title
            except UnicodeEncodeError:
                # Title contains emojis or other UTF-8 chars
                # Move emojis to message and keep ASCII in title
                title_clean = ''.join(c for c in title if ord(c) < 128).strip()
                if title_clean:
                    headers["Title"] = title_clean
                    # Prepend the full title (with emojis) to the message
                    message = f"{title}\n\n{message}" if message else title
                else:
                    # Title is only emojis, put it all in the message
                    headers["Title"] = "Notification"
                    message = f"{title}\n\n{message}" if message else title
        
        if tags:
            headers["Tags"] = ",".join(tags)
        
        if click_url:
            headers["Click"] = click_url
        
        if attach:
            headers["Attach"] = attach
        
        if actions:
            # Format: action=view, label=Open, url=https://...; action=http, label=Done, url=https://...
            action_strs = []
            for action in actions:
                parts = [f"{k}={v}" for k, v in action.items()]
                action_strs.append(", ".join(parts))
            headers["Actions"] = "; ".join(action_strs)
        
        try:
            # Send UTF-8 encoded message body
            response = requests.post(url, data=message.encode('utf-8'), headers=headers)
            response.raise_for_status()
            
            # ntfy returns the message ID in the response
            result = response.json()
            return result.get('id')
        except Exception as e:
            print(f"Error sending notification: {e}")
            return None
    
    def send_task_reminder(
        self,
        task_title: str,
        task_description: Optional[str],
        scheduled_time: datetime,
        priority: str = 'medium',
        task_id: Optional[int] = None,
        minutes_before: int = 15
    ) -> Optional[str]:
        """Send a task reminder notification"""
        
        time_str = scheduled_time.strftime("%I:%M %p")
        
        if minutes_before > 0:
            title = f"⏰ Reminder: {task_title}"
            message = f"Starting in {minutes_before} minutes at {time_str}"
        else:
            title = f"📌 Now: {task_title}"
            message = f"Scheduled for {time_str}"
        
        if task_description:
            message += f"\n\n{task_description}"
        
        tags = ["calendar", "alarm_clock"]
        if priority == 'high':
            tags.append("warning")
        
        actions = []
        if task_id:
            # Note: These would need to be actual endpoints on your server
            actions = [
                {
                    "action": "http",
                    "label": "✓ Done",
                    "url": f"http://localhost:8080/api/tasks/{task_id}/complete",
                    "method": "POST"
                },
                {
                    "action": "http",
                    "label": "Snooze 15m",
                    "url": f"http://localhost:8080/api/tasks/{task_id}/snooze",
                    "method": "POST"
                }
            ]
        
        return self.send_notification(
            title=title,
            message=message,
            priority=priority,
            tags=tags,
            actions=actions if task_id else None
        )
    
    def send_daily_summary(
        self,
        date: datetime,
        tasks: List[Dict[str, Any]],
        total_duration: int = 0
    ) -> Optional[str]:
        """Send a daily summary notification"""
        
        date_str = date.strftime("%A, %B %d")
        title = f"📅 {date_str}"
        
        if not tasks:
            message = "No tasks scheduled for today. Enjoy your free time! 🎉"
        else:
            message = f"Here's your day:\n\n"
            
            for task in tasks:
                scheduled_time = datetime.fromisoformat(task['scheduled_time'])
                time_str = scheduled_time.strftime("%I:%M %p")
                duration = task.get('duration', 30)
                
                emoji = "🔴" if task.get('priority') == 'high' else "🟡" if task.get('priority') == 'medium' else "🟢"
                message += f"{emoji} {time_str} - {task['title']} ({duration}min)\n"
            
            # Calculate free time
            work_hours = 8 * 60  # Assume 8 hour workday
            free_time = work_hours - total_duration
            if free_time > 0:
                hours = free_time // 60
                minutes = free_time % 60
                message += f"\n💡 Free time: {hours}h {minutes}m"
        
        return self.send_notification(
            title=title,
            message=message,
            priority='medium',
            tags=["calendar", "sunrise"]
        )
    
    def send_upcoming_summary(
        self,
        tasks: List[Dict[str, Any]],
        hours_ahead: int = 4
    ) -> Optional[str]:
        """Send an upcoming tasks summary"""
        
        title = f"📋 Upcoming ({hours_ahead}h)"
        
        if not tasks:
            message = "No tasks scheduled in the next few hours. You're all clear! ✨"
        else:
            message = "Coming up:\n\n"
            
            for task in tasks:
                scheduled_time = datetime.fromisoformat(task['scheduled_time'])
                time_str = scheduled_time.strftime("%I:%M %p")
                
                # Calculate time until task
                now = datetime.now(scheduled_time.tzinfo)
                time_until = scheduled_time - now
                hours = int(time_until.total_seconds() // 3600)
                minutes = int((time_until.total_seconds() % 3600) // 60)
                
                time_desc = ""
                if hours > 0:
                    time_desc = f"in {hours}h {minutes}m"
                elif minutes > 0:
                    time_desc = f"in {minutes}m"
                else:
                    time_desc = "now"
                
                emoji = "🔴" if task.get('priority') == 'high' else "🟡" if task.get('priority') == 'medium' else "🟢"
                message += f"{emoji} {time_str} ({time_desc}) - {task['title']}\n"
        
        return self.send_notification(
            title=title,
            message=message,
            priority='low',
            tags=["calendar", "information_source"]
        )
    
    def send_test_notification(self) -> Optional[str]:
        """Send a test notification to verify setup"""
        return self.send_notification(
            title="✅ Schedule Manager Connected",
            message="Your AI schedule manager is up and running! You'll receive notifications here.",
            priority='low',
            tags=["white_check_mark", "rocket"]
        )
