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
            "description": "Create a new task in the todo list",
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
    ) -> dict[str, Any]:
        """Add a new task."""
        task = Task(
            title=title,
            description=description,
            user_id=self.user_id,
        )
        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)

        return {
            "task_id": task.id,
            "status": "created",
            "title": task.title,
        }

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

        return [
            {
                "id": t.id,
                "title": t.title,
                "completed": t.completed,
                "description": t.description,
            }
            for t in tasks
        ]

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
