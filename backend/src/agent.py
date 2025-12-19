"""Gemini Agent for Todo Chatbot.

Reference: @specs/features/chatbot.md
- AC-CHAT-001.1: "Add task to X" → calls add_task tool
- AC-CHAT-001.2: "Show my tasks" → calls list_tasks(status="all")
- AC-CHAT-001.3: "What's pending?" → calls list_tasks(status="pending")
- AC-CHAT-001.4: "Mark task X as done" → calls complete_task
- AC-CHAT-001.5: "Delete task X" → calls delete_task

Uses Google Gemini API instead of OpenAI for more generous free tier.
"""

import json
import os
from typing import Any

import google.generativeai as genai
from sqlmodel.ext.asyncio.session import AsyncSession

from src.mcp_tools import MCPToolExecutor

# System prompt for the AI agent
SYSTEM_PROMPT = """You are a helpful Todo assistant. You help users manage their tasks through natural language.

Available commands you can understand:
- "Add a task to buy groceries" → Create a new task
- "Show my tasks" or "List all tasks" → Show all tasks
- "What's pending?" or "Show incomplete tasks" → Show only pending tasks
- "Mark task 3 as done" or "Complete task 3" → Mark a task as complete
- "Delete task 5" or "Remove task 5" → Delete a task
- "Update task 2 to buy milk" → Update a task title

When the user asks "What's pending?" you MUST call list_tasks with status="pending".
When the user says "show my tasks" you MUST call list_tasks with status="all".

Always be friendly and confirm actions with the user.
Format task lists nicely with checkboxes: ✅ for complete, ❌ for pending.
"""

# Gemini tool definitions (different format from OpenAI)
GEMINI_TOOLS = [
    genai.protos.Tool(
        function_declarations=[
            genai.protos.FunctionDeclaration(
                name="add_task",
                description="Create a new task in the todo list",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "title": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="Task title (required)"
                        ),
                        "description": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="Task description (optional)"
                        ),
                    },
                    required=["title"],
                ),
            ),
            genai.protos.FunctionDeclaration(
                name="list_tasks",
                description="List all tasks or filter by status (all, pending, completed)",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "status": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="Filter by status: all, pending, or completed",
                            enum=["all", "pending", "completed"],
                        ),
                    },
                ),
            ),
            genai.protos.FunctionDeclaration(
                name="complete_task",
                description="Mark a task as complete",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "task_id": genai.protos.Schema(
                            type=genai.protos.Type.INTEGER,
                            description="ID of the task to complete"
                        ),
                    },
                    required=["task_id"],
                ),
            ),
            genai.protos.FunctionDeclaration(
                name="delete_task",
                description="Delete a task from the list",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "task_id": genai.protos.Schema(
                            type=genai.protos.Type.INTEGER,
                            description="ID of the task to delete"
                        ),
                    },
                    required=["task_id"],
                ),
            ),
            genai.protos.FunctionDeclaration(
                name="update_task",
                description="Update a task's title or description",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "task_id": genai.protos.Schema(
                            type=genai.protos.Type.INTEGER,
                            description="ID of the task to update"
                        ),
                        "title": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="New title (optional)"
                        ),
                        "description": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="New description (optional)"
                        ),
                    },
                    required=["task_id"],
                ),
            ),
        ]
    )
]


class TodoAgent:
    """Gemini-powered Todo Agent with function calling.
    
    Uses the tools defined for Gemini function calling format.
    """

    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id
        self.tool_executor = MCPToolExecutor(session, user_id)
        
        # Configure Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT,
            tools=GEMINI_TOOLS,
        )

    async def chat(
        self,
        user_message: str,
        history: list[dict[str, str]],
    ) -> tuple[str, list[str]]:
        """
        Process a chat message and return response with tool calls.
        
        Per AC-CHAT-002.1: Server holds NO state between requests.
        History is passed in from the database.
        
        Returns: (response_text, list_of_tool_names_called)
        """
        tool_calls_made: list[str] = []
        
        # Convert history to Gemini format
        gemini_history = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({
                "role": role,
                "parts": [msg["content"]]
            })
        
        # Create chat session with history
        chat = self.model.start_chat(history=gemini_history)
        
        # Send message and process response
        response = chat.send_message(user_message)
        
        # Check for function calls
        while response.candidates[0].content.parts:
            part = response.candidates[0].content.parts[0]
            
            if hasattr(part, 'function_call') and part.function_call.name:
                # Extract function call
                function_call = part.function_call
                tool_name = function_call.name
                tool_calls_made.append(tool_name)
                
                # Parse arguments
                arguments = {}
                for key, value in function_call.args.items():
                    arguments[key] = value
                
                # Execute the tool
                result = await self.tool_executor.execute_tool(tool_name, arguments)
                
                # Send function result back to Gemini
                response = chat.send_message(
                    genai.protos.Content(
                        parts=[
                            genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=tool_name,
                                    response={"result": result}
                                )
                            )
                        ]
                    )
                )
            else:
                # No more function calls, we have the final text response
                break
        
        # Get final text response
        response_text = ""
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'text'):
                response_text += part.text
        
        return response_text, tool_calls_made
