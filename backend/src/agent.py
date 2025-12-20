"""Groq Agent for Todo Chatbot.

Reference: @specs/features/chatbot.md
Uses Groq API with Llama model - generous free tier (14,000 tokens/min).
"""

import json
import os
from typing import Any

import httpx
from sqlmodel.ext.asyncio.session import AsyncSession

from src.mcp_tools import MCPToolExecutor

# System prompt for the AI agent - Phase V enabled
SYSTEM_PROMPT = """You are a helpful Todo assistant. You help users manage their tasks through natural language.

You have access to these tools:
- add_task: Create a new task
  - Required: title
  - Optional: description, priority (high/medium/low), due_date (ISO format), reminder_at (ISO format)
- list_tasks: List tasks (optional status filter: all, pending, completed)
- complete_task: Mark a task as complete (requires task_id)
- delete_task: Delete a task (requires task_id)  
- update_task: Update a task (requires task_id, optional title/description)

When the user asks "What's pending?" call list_tasks with status="pending".
When the user says "show my tasks" call list_tasks with status="all".
When the user specifies priority (high/medium/low), due date, or reminder, include them in add_task.

IMPORTANT: When calling a tool, respond ONLY with a JSON object in this exact format:
{"tool": "tool_name", "args": {"arg1": "value1"}}

Examples:
- "Add high priority task to finish report due tomorrow" → {"tool": "add_task", "args": {"title": "finish report", "priority": "high", "due_date": "2025-12-21T23:59:59"}}
- "Add task buy milk" → {"tool": "add_task", "args": {"title": "buy milk"}}

If no tool is needed, respond normally with text.
Format task lists nicely showing: ✅/❌ status, 📌 priority, 📅 due date if set.
"""


class TodoAgent:
    """Groq-powered Todo Agent using Llama model."""

    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id
        self.tool_executor = MCPToolExecutor(session, user_id)
        self.api_key = os.getenv("GROQ_API_KEY")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    async def chat(
        self,
        user_message: str,
        history: list[dict[str, str]],
    ) -> tuple[str, list[str]]:
        """Process a chat message and return response with tool calls."""
        tool_calls_made: list[str] = []
        
        # Build messages array
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Make request to Groq
            response = await client.post(
                self.api_url,
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1024,
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code != 200:
                error_text = response.text
                print(f"Groq API error: {response.status_code} - {error_text}")
                return f"Sorry, I encountered an error: {error_text[:200]}", []
            
            result = response.json()
            assistant_message = result["choices"][0]["message"]["content"]
            
            # Check if the response is a tool call (JSON format)
            try:
                # Try to parse as JSON tool call
                if assistant_message.strip().startswith("{"):
                    tool_data = json.loads(assistant_message)
                    if "tool" in tool_data:
                        tool_name = tool_data["tool"]
                        arguments = tool_data.get("args", {})
                        tool_calls_made.append(tool_name)
                        
                        # Execute the tool
                        tool_result = await self.tool_executor.execute_tool(tool_name, arguments)
                        
                        # Add tool result to messages and get final response
                        messages.append({"role": "assistant", "content": assistant_message})
                        messages.append({
                            "role": "user", 
                            "content": f"Tool result: {json.dumps(tool_result)}\n\nPlease provide a friendly response to the user based on this result."
                        })
                        
                        # Get final response
                        response = await client.post(
                            self.api_url,
                            json={
                                "model": "llama-3.3-70b-versatile",
                                "messages": messages,
                                "temperature": 0.7,
                                "max_tokens": 1024,
                            },
                            headers={
                                "Authorization": f"Bearer {self.api_key}",
                                "Content-Type": "application/json"
                            }
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            return result["choices"][0]["message"]["content"], tool_calls_made
            except json.JSONDecodeError:
                pass
            
            return assistant_message, tool_calls_made
