"""Custom exceptions for Todo Console Application.

This module defines domain-specific exceptions for error handling.
Following the constitution's error handling principles:
- Use explicit exceptions (never fail silently)
- Custom exception classes for domain errors
- User-friendly error messages
"""


class TodoError(Exception):
    """Base exception for all Todo application errors."""

    pass


class TaskNotFoundError(TodoError):
    """Raised when a task with the given ID does not exist."""

    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f"Task #{task_id} not found")


class ValidationError(TodoError):
    """Raised when input validation fails."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(f"Validation error on '{field}': {message}")


class EmptyTitleError(ValidationError):
    """Raised when task title is empty or whitespace-only."""

    def __init__(self) -> None:
        super().__init__("title", "Title cannot be empty")


class TitleTooLongError(ValidationError):
    """Raised when task title exceeds maximum length."""

    def __init__(self, max_length: int = 100) -> None:
        super().__init__("title", f"Title cannot exceed {max_length} characters")


class DescriptionTooLongError(ValidationError):
    """Raised when task description exceeds maximum length."""

    def __init__(self, max_length: int = 500) -> None:
        super().__init__(
            "description", f"Description cannot exceed {max_length} characters"
        )
