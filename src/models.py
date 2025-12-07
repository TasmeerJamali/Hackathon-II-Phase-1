"""Task data model for Todo Console Application.

This module defines the Task dataclass following the specification:
- FR-001 through FR-005 data requirements
- Constitution naming conventions (PascalCase for classes)
- Type hints required for all attributes
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    """Represents a single todo task.

    Attributes:
        id: Unique identifier (auto-increment, assigned by storage).
        title: Task title (required, 1-100 characters).
        description: Task description (optional, 0-500 characters).
        completed: Completion status (default: False).
        created_at: Timestamp of creation (auto-generated).
    """

    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        """Return string representation for display."""
        status = "✅" if self.completed else "❌"
        desc = self.description if self.description else "(no description)"
        return f"[{self.id}] {status} {self.title} - {desc}"
