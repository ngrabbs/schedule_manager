#!/usr/bin/env python3
"""
MCP Server for Schedule Manager - Allows OpenCode to manage your schedule
"""

import json
import sys
from datetime import datetime
from typing import Any, Sequence
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server.stdio import stdio_server
import asyncio

from .core import ScheduleManager


# Initialize the schedule manager
manager = ScheduleManager()

# Create MCP server
app = Server("schedule-manager")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available schedule management tools"""
    return [
        Tool(
            name="schedule_add",
            description=(
                "Add a new task to the schedule using natural language. "
                "Examples: 'Team meeting tomorrow at 10am', 'Call mom next friday at 3pm for 30 minutes', "
                "'Buy groceries this afternoon'. Supports time parsing, duration extraction, and priority levels."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Natural language description of the task (include time, duration, etc.)"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Priority level (default: medium)",
                        "default": "medium"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional tags for categorization"
                    }
                },
                "required": ["description"]
            }
        ),
        Tool(
            name="schedule_add_recurring",
            description=(
                "Add a recurring task (for time-blocking like classes). "
                "Example: 'I have class mon, wed, fri 12:00-12:45' or 'Gym every weekday at 6am for 1 hour'"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Description including days and time (e.g., 'Class mon,wed,fri at 12:00')"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Priority level",
                        "default": "medium"
                    }
                },
                "required": ["description"]
            }
        ),
        Tool(
            name="schedule_view",
            description="View tasks for a specific day or upcoming tasks",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date to view (e.g., 'today', 'tomorrow', '2026-01-15'). Default: today"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "completed", "in_progress", "cancelled", "all"],
                        "description": "Filter by status (default: pending)",
                        "default": "pending"
                    },
                    "days_ahead": {
                        "type": "integer",
                        "description": "Number of days ahead to view (0 = single day, 7 = week view)",
                        "default": 0
                    }
                }
            }
        ),
        Tool(
            name="schedule_upcoming",
            description="Get tasks coming up in the next few hours",
            inputSchema={
                "type": "object",
                "properties": {
                    "hours": {
                        "type": "integer",
                        "description": "Number of hours ahead to look (default: 4)",
                        "default": 4
                    }
                }
            }
        ),
        Tool(
            name="schedule_summary",
            description="Get a formatted daily summary (like what's sent in morning notifications)",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date for summary (e.g., 'today', 'tomorrow'). Default: today"
                    }
                }
            }
        ),
        Tool(
            name="schedule_update",
            description="Update a task's details",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "New priority"
                    },
                    "duration": {
                        "type": "integer",
                        "description": "New duration in minutes"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="schedule_reschedule",
            description="Reschedule a task to a different time",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to reschedule"
                    },
                    "new_time": {
                        "type": "string",
                        "description": "New time in natural language (e.g., 'tomorrow at 3pm', 'next monday 10am')"
                    }
                },
                "required": ["task_id", "new_time"]
            }
        ),
        Tool(
            name="schedule_complete",
            description="Mark a task as completed",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to complete"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="schedule_delete",
            description="Delete a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to delete"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="schedule_test_notification",
            description="Send a test notification to verify ntfy.sh setup",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls"""
    
    try:
        if name == "schedule_add":
            result = manager.add_task_natural(
                description=arguments["description"],
                priority=arguments.get("priority", "medium"),
                tags=arguments.get("tags")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        
        elif name == "schedule_add_recurring":
            # Parse recurring pattern and add task
            result = manager.add_task_natural(
                description=arguments["description"],
                priority=arguments.get("priority", "medium")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        
        elif name == "schedule_view":
            date_str = arguments.get("date", "today")
            date = manager.parser.parse(date_str) if date_str != "today" else None
            status = arguments.get("status", "pending")
            days_ahead = arguments.get("days_ahead", 0)
            
            if status == "all":
                status = None
            
            tasks = manager.get_tasks(date=date, status=status, days_ahead=days_ahead)
            
            # Format tasks for display
            if not tasks:
                result = {"message": "No tasks found"}
            else:
                result = {
                    "count": len(tasks),
                    "tasks": tasks
                }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        
        elif name == "schedule_upcoming":
            hours = arguments.get("hours", 4)
            tasks = manager.get_upcoming_tasks(hours_ahead=hours)
            
            if not tasks:
                result = {"message": f"No tasks in the next {hours} hours"}
            else:
                result = {
                    "count": len(tasks),
                    "tasks": tasks
                }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        
        elif name == "schedule_summary":
            date_str = arguments.get("date", "today")
            date = manager.parser.parse(date_str) if date_str != "today" else None
            
            summary = manager.get_daily_summary(date=date)
            return [TextContent(type="text", text=summary)]
        
        elif name == "schedule_update":
            task_id = arguments["task_id"]
            update_fields = {k: v for k, v in arguments.items() if k != "task_id"}
            
            result = manager.update_task(task_id, **update_fields)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        
        elif name == "schedule_reschedule":
            task_id = arguments["task_id"]
            new_time = arguments["new_time"]
            
            result = manager.reschedule_task(task_id, new_time)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        
        elif name == "schedule_complete":
            task_id = arguments["task_id"]
            result = manager.complete_task(task_id)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "schedule_delete":
            task_id = arguments["task_id"]
            result = manager.delete_task(task_id)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "schedule_test_notification":
            success = manager.send_test_notification()
            result = {
                "success": success,
                "message": "Test notification sent!" if success else "Failed to send test notification"
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
