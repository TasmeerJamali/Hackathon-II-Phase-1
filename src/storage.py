"""In-memory storage for Todo Console Application.

This module implements the TaskStorage interface from the specification:
- add(): Create new task with auto-increment ID
- get(): Retrieve task by ID
- get_all(): List all tasks sorted by ID
- update(): Modify task title/description
- delete(): Remove task by ID
- toggle_complete(): Toggle completion status

Storage is in-memory only (Phase I requirement).
"""

from src.exceptions import (
    DescriptionTooLongError,
    EmptyTitleError,
    TaskNotFoundError,
    TitleTooLongError,
)
from src.models import Task

# Constants from specification
MAX_TITLE_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 500


class InMemoryStorage:
    """In-memory task storage with CRUD operations.

    This class manages tasks in a dictionary, using auto-incrementing
    integer IDs. All data is lost when the application exits.

    Attributes:
        _tasks: Dictionary mapping task IDs to Task objects.
        _next_id: Counter for generating unique task IDs.
    """

    def __init__(self) -> None:
        """Initialize empty storage."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, title: str, description: str = "") -> Task:
        """Create a new task.

        Args:
            title: Task title (required, 1-100 characters).
            description: Task description (optional, 0-500 characters).

        Returns:
            The newly created Task object.

        Raises:
            EmptyTitleError: If title is empty or whitespace-only.
            TitleTooLongError: If title exceeds 100 characters.
            DescriptionTooLongError: If description exceeds 500 characters.
        """
        # Validate title
        title = title.strip()
        if not title:
            raise EmptyTitleError()
        if len(title) > MAX_TITLE_LENGTH:
            raise TitleTooLongError(MAX_TITLE_LENGTH)

        # Validate description
        description = description.strip()
        if len(description) > MAX_DESCRIPTION_LENGTH:
            raise DescriptionTooLongError(MAX_DESCRIPTION_LENGTH)

        # Create task with auto-increment ID
        task = Task(
            id=self._next_id,
            title=title,
            description=description,
        )
        self._tasks[self._next_id] = task
        self._next_id += 1

        return task

    def get(self, task_id: int) -> Task:
        """Retrieve a task by ID.

        Args:
            task_id: The unique task identifier.

        Returns:
            The Task object.

        Raises:
            TaskNotFoundError: If no task exists with the given ID.
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        return self._tasks[task_id]

    def get_all(self) -> list[Task]:
        """Retrieve all tasks sorted by ID.

        Returns:
            List of Task objects sorted by ID ascending.
        """
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def update(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
    ) -> Task:
        """Update a task's title and/or description.

        Args:
            task_id: The unique task identifier.
            title: New title (None = keep current).
            description: New description (None = keep current).

        Returns:
            The updated Task object.

        Raises:
            TaskNotFoundError: If no task exists with the given ID.
            EmptyTitleError: If new title is empty.
            TitleTooLongError: If new title exceeds 100 characters.
            DescriptionTooLongError: If new description exceeds 500 characters.
        """
        task = self.get(task_id)

        # Update title if provided
        if title is not None:
            title = title.strip()
            if not title:
                raise EmptyTitleError()
            if len(title) > MAX_TITLE_LENGTH:
                raise TitleTooLongError(MAX_TITLE_LENGTH)
            task.title = title

        # Update description if provided
        if description is not None:
            description = description.strip()
            if len(description) > MAX_DESCRIPTION_LENGTH:
                raise DescriptionTooLongError(MAX_DESCRIPTION_LENGTH)
            task.description = description

        return task

    def delete(self, task_id: int) -> bool:
        """Delete a task by ID.

        Args:
            task_id: The unique task identifier.

        Returns:
            True if task was deleted.

        Raises:
            TaskNotFoundError: If no task exists with the given ID.
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        del self._tasks[task_id]
        return True

    def toggle_complete(self, task_id: int) -> Task:
        """Toggle a task's completion status.

        Args:
            task_id: The unique task identifier.

        Returns:
            The updated Task object.

        Raises:
            TaskNotFoundError: If no task exists with the given ID.
        """
        task = self.get(task_id)
        task.completed = not task.completed
        return task

    def count(self) -> tuple[int, int, int]:
        """Get task counts.

        Returns:
            Tuple of (total, complete, pending) counts.
        """
        tasks = list(self._tasks.values())
        total = len(tasks)
        complete = sum(1 for t in tasks if t.completed)
        pending = total - complete
        return total, complete, pending
