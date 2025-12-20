"""MCP Tools for Todo Operations.

Reference: @specs/api/mcp-tools.md
Implements 5 tools: add_task, list_tasks, complete_task, delete_task, update_task

These are FUNCTION DEFINITIONS for OpenAI Agents SDK, not an MCP server.
"""

from datetime import datetime
from typing import Any

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models import Task


# ============================================================================
# TOOL DEFINITIONS FOR OPENAI AGENTS SDK
# Per specs/api/mcp-tools.md
# ============================================================================

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task in the todo list with optional priority, due date, and reminder",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Task title (required)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Task description (optional)"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Task priority level (optional, default: medium)"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Due date in ISO format YYYY-MM-DDTHH:MM:SS (optional)"
                    },
                    "reminder_at": {
                        "type": "string",
                        "description": "Reminder datetime in ISO format (optional)"
                    },
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks or filter by status (all, pending, completed)",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter by status. Use 'pending' for incomplete tasks.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as complete",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to complete"
                    },
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task from the list",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to delete"
                    },
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update a task's title or description",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title (optional)"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description (optional)"
                    },
                },
                "required": ["task_id"],
            },
        },
    },
]


class MCPToolExecutor:
    """Execute MCP tools against the database.
    
    Each tool accepts user_id for security isolation.
    """

    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id

    async def add_task(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        due_date: str | None = None,
        reminder_at: str | None = None,
    ) -> dict[str, Any]:
        """Add a new task with Phase V fields."""
        from src.models import Priority
        
        # Parse due_date and reminder_at if provided
        parsed_due_date = None
        parsed_reminder_at = None
        
        if due_date:
            try:
                parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                pass
        
        if reminder_at:
            try:
                parsed_reminder_at = datetime.fromisoformat(reminder_at.replace('Z', '+00:00'))
            except ValueError:
                pass
        
        # Map priority string to enum
        priority_enum = Priority.MEDIUM
        if priority.lower() == "high":
            priority_enum = Priority.HIGH
        elif priority.lower() == "low":
            priority_enum = Priority.LOW
        
        task = Task(
            title=title,
            description=description,
            user_id=self.user_id,
            priority=priority_enum,
            due_date=parsed_due_date,
            reminder_at=parsed_reminder_at,
        )
        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)

        result = {
            "task_id": task.id,
            "status": "created",
            "title": task.title,
            "priority": task.priority.value,
        }
        if task.due_date:
            result["due_date"] = task.due_date.isoformat()
        if task.reminder_at:
            result["reminder_at"] = task.reminder_at.isoformat()
        
        return result

    async def list_tasks(
        self,
        status: str = "all",
    ) -> list[dict[str, Any]]:
        """
        List tasks with optional status filter.
        
        Per AC-CHAT-001.3: "What's pending?" → calls list_tasks(status="pending")
        """
        query = select(Task).where(Task.user_id == self.user_id)

        if status == "pending":
            query = query.where(Task.completed == False)  # noqa: E712
        elif status == "completed":
            query = query.where(Task.completed == True)  # noqa: E712

        result = await self.session.execute(query.order_by(Task.created_at.desc()))
        tasks = result.scalars().all()

        task_list = []
        for t in tasks:
            task_data = {
                "id": t.id,
                "title": t.title,
                "completed": t.completed,
                "description": t.description,
                "priority": t.priority.value if t.priority else "medium",
            }
            if t.due_date:
                task_data["due_date"] = t.due_date.isoformat()
            if t.reminder_at:
                task_data["reminder_at"] = t.reminder_at.isoformat()
            task_list.append(task_data)
        
        return task_list

    async def complete_task(
        self,
        task_id: int | str,
    ) -> dict[str, Any]:
        """Mark task as complete."""
        task_id = int(task_id)  # Ensure int (LLM may pass string)
        result = await self.session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == self.user_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            return {"error": f"Task {task_id} not found"}

        task.completed = True
        task.updated_at = datetime.utcnow()
        await self.session.flush()

        return {
            "task_id": task.id,
            "status": "completed",
            "title": task.title,
        }

    async def delete_task(
        self,
        task_id: int | str,
    ) -> dict[str, Any]:
        """Delete a task."""
        task_id = int(task_id)  # Ensure int (LLM may pass string)
        result = await self.session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == self.user_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            return {"error": f"Task {task_id} not found"}

        title = task.title
        await self.session.delete(task)
        await self.session.flush()

        return {
            "task_id": task_id,
            "status": "deleted",
            "title": title,
        }

    async def update_task(
        self,
        task_id: int | str,
        title: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Update a task."""
        task_id = int(task_id)  # Ensure int (LLM may pass string)
        result = await self.session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == self.user_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            return {"error": f"Task {task_id} not found"}

        if title:
            task.title = title
        if description is not None:
            task.description = description

        task.updated_at = datetime.utcnow()
        await self.session.flush()

        return {
            "task_id": task.id,
            "status": "updated",
            "title": task.title,
        }

    async def execute_tool(self, name: str, arguments: dict[str, Any]) -> dict | list:
        """Execute a tool by name with given arguments."""
        if name == "add_task":
            return await self.add_task(**arguments)
        elif name == "list_tasks":
            return await self.list_tasks(**arguments)
        elif name == "complete_task":
            return await self.complete_task(**arguments)
        elif name == "delete_task":
            return await self.delete_task(**arguments)
        elif name == "update_task":
            return await self.update_task(**arguments)
        else:
            return {"error": f"Unknown tool: {name}"}
