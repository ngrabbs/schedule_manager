#!/usr/bin/env python3
"""
Script to regenerate all notifications for pending tasks with new priority-based logic
"""

from schedule_manager.core import ScheduleManager
from datetime import datetime
import pytz

def main():
    print("🔄 Regenerating notifications with new priority-based logic\n")
    
    # Initialize manager
    manager = ScheduleManager()
    
    # Get all pending tasks
    all_tasks = manager.db.get_tasks(status='pending')
    
    print(f"Found {len(all_tasks)} pending tasks\n")
    
    # Step 1: Delete all existing notifications
    print("Step 1: Deleting all existing notifications...")
    conn = manager.db.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notifications")
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    print(f"✓ Deleted {deleted_count} old notifications\n")
    
    # Step 2: Regenerate notifications for each pending task
    print("Step 2: Regenerating notifications for pending tasks...")
    regenerated_count = 0
    
    for task in all_tasks:
        task_id = task['id']
        title = task['title']
        scheduled_time_str = task['scheduled_time']
        priority = task.get('priority', 'medium')
        
        if not scheduled_time_str:
            print(f"  ⚠ Skipping task {task_id} '{title}' - no scheduled time")
            continue
        
        # Parse scheduled time
        scheduled_time = datetime.fromisoformat(scheduled_time_str)
        
        # Skip if task is in the past
        now = datetime.now(scheduled_time.tzinfo or pytz.timezone('America/Chicago'))
        if scheduled_time < now:
            print(f"  ⚠ Skipping task {task_id} '{title}' - in the past")
            continue
        
        # Regenerate notifications using new priority-based logic
        manager._schedule_task_notifications(task_id, scheduled_time, priority)
        
        # Count how many notifications were created
        conn = manager.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM notifications WHERE task_id = ?", (task_id,))
        notif_count = cursor.fetchone()[0]
        conn.close()
        
        priority_marker = "🔥" if priority == 'high' else "📌"
        print(f"  {priority_marker} Task {task_id} '{title[:40]}' ({priority}) → {notif_count} notification(s)")
        regenerated_count += 1
    
    print(f"\n✅ Regenerated notifications for {regenerated_count} tasks")
    print("\nSummary:")
    
    # Show notification counts
    conn = manager.db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM notifications")
    total_notifs = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT t.priority, COUNT(n.id) as notif_count, COUNT(DISTINCT n.task_id) as task_count
        FROM notifications n
        JOIN tasks t ON n.task_id = t.id
        GROUP BY t.priority
    """)
    by_priority = cursor.fetchall()
    conn.close()
    
    print(f"  Total notifications: {total_notifs}")
    for row in by_priority:
        priority, notif_count, task_count = row
        avg = notif_count / task_count if task_count > 0 else 0
        print(f"  {priority} priority: {task_count} tasks, {notif_count} notifications (avg {avg:.1f} per task)")

if __name__ == '__main__':
    main()
