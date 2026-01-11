#!/usr/bin/env python3
"""
Example usage of the Schedule Manager
Run this to test the system after setup
"""

from schedule_manager.core import ScheduleManager
from datetime import datetime, timedelta

def main():
    print("=" * 60)
    print("AI Schedule Manager - Example Usage")
    print("=" * 60)
    
    # Initialize manager
    manager = ScheduleManager()
    
    # 1. Send a test notification
    print("\n1. Sending test notification...")
    success = manager.send_test_notification()
    if success:
        print("   ✓ Check your phone for the test notification!")
    else:
        print("   ✗ Failed to send. Check your config.yaml settings.")
        return
    
    # 2. Add tasks using natural language
    print("\n2. Adding tasks using natural language...")
    
    tasks_to_add = [
        "Team standup tomorrow at 10am for 30 minutes",
        "Code review tomorrow at 2pm for 1 hour",
        "Gym workout tomorrow at 5pm",
    ]
    
    for task_desc in tasks_to_add:
        result = manager.add_task_natural(task_desc, priority="medium")
        if result['success']:
            print(f"   ✓ {result['message']}")
    
    # 3. Add a recurring task (time-blocking)
    print("\n3. Adding recurring task (time-blocking)...")
    result = manager.add_task_natural(
        "Team sync every monday at 9am for 30 minutes",
        priority="high"
    )
    if result['success']:
        print(f"   ✓ {result['message']}")
    
    # 4. View today's tasks
    print("\n4. Viewing tasks...")
    tomorrow = datetime.now(manager.parser.timezone) + timedelta(days=1)
    tasks = manager.get_tasks(date=tomorrow)
    
    if tasks:
        print(f"   Found {len(tasks)} tasks for tomorrow:")
        for task in tasks:
            time_str = datetime.fromisoformat(task['scheduled_time']).strftime("%I:%M %p")
            print(f"   • {time_str} - {task['title']} ({task['duration']}min) [{task['priority']}]")
    else:
        print("   No tasks scheduled")
    
    # 5. Get daily summary
    print("\n5. Daily summary for tomorrow:")
    summary = manager.get_daily_summary(date=tomorrow)
    print("\n" + summary)
    
    # 6. Get upcoming tasks
    print("\n6. Upcoming tasks (next 24 hours):")
    upcoming = manager.get_upcoming_tasks(hours_ahead=24)
    if upcoming:
        for task in upcoming:
            time_str = datetime.fromisoformat(task['scheduled_time']).strftime("%Y-%m-%d %I:%M %p")
            print(f"   • {time_str} - {task['title']}")
    else:
        print("   No upcoming tasks")
    
    print("\n" + "=" * 60)
    print("Example complete!")
    print("\nNext steps:")
    print("1. Start the daemon: python3 -m schedule_manager.daemon")
    print("2. Set up the MCP server for OpenCode integration")
    print("3. Start managing your schedule with AI!")
    print("=" * 60)

if __name__ == "__main__":
    main()
