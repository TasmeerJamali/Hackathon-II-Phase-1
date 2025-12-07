"""Tests for InMemoryStorage class.

Test scenarios from specification Section 7:
- T1: Add task with valid title
- T2: Add task with empty title
- T3: Delete existing task
- T4: Delete non-existent task
- T5: Update task title only
- T6: View empty list
- T7: Toggle incomplete to complete
- T8: Toggle complete to incomplete
"""

import pytest

from src.exceptions import EmptyTitleError, TaskNotFoundError
from src.storage import InMemoryStorage


class TestAddTask:
    """Tests for adding tasks (FR-001)."""

    def test_add_task_with_valid_title_creates_task(self) -> None:
        """T1: Add task with valid title."""
        storage = InMemoryStorage()
        task = storage.add("Buy groceries", "Milk, eggs")

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs"
        assert task.completed is False

    def test_add_task_with_empty_title_raises_error(self) -> None:
        """T2: Add task with empty title."""
        storage = InMemoryStorage()

        with pytest.raises(EmptyTitleError):
            storage.add("")

    def test_add_task_with_whitespace_title_raises_error(self) -> None:
        """Title with only whitespace should fail."""
        storage = InMemoryStorage()

        with pytest.raises(EmptyTitleError):
            storage.add("   ")

    def test_add_multiple_tasks_increments_id(self) -> None:
        """Each task gets a unique auto-increment ID."""
        storage = InMemoryStorage()

        task1 = storage.add("Task 1")
        task2 = storage.add("Task 2")
        task3 = storage.add("Task 3")

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3


class TestDeleteTask:
    """Tests for deleting tasks (FR-002)."""

    def test_delete_existing_task_removes_it(self) -> None:
        """T3: Delete existing task."""
        storage = InMemoryStorage()
        task = storage.add("To delete")

        result = storage.delete(task.id)

        assert result is True
        assert len(storage.get_all()) == 0

    def test_delete_non_existent_task_raises_error(self) -> None:
        """T4: Delete non-existent task."""
        storage = InMemoryStorage()

        with pytest.raises(TaskNotFoundError):
            storage.delete(999)


class TestUpdateTask:
    """Tests for updating tasks (FR-003)."""

    def test_update_task_title_only(self) -> None:
        """T5: Update task title only."""
        storage = InMemoryStorage()
        task = storage.add("Original", "Original description")

        updated = storage.update(task.id, title="Updated Title")

        assert updated.title == "Updated Title"
        assert updated.description == "Original description"

    def test_update_task_description_only(self) -> None:
        """Update description keeps title unchanged."""
        storage = InMemoryStorage()
        task = storage.add("Original", "Original description")

        updated = storage.update(task.id, description="New description")

        assert updated.title == "Original"
        assert updated.description == "New description"

    def test_update_non_existent_task_raises_error(self) -> None:
        """Updating non-existent task fails."""
        storage = InMemoryStorage()

        with pytest.raises(TaskNotFoundError):
            storage.update(999, title="New")


class TestGetAllTasks:
    """Tests for viewing tasks (FR-004)."""

    def test_get_all_empty_list(self) -> None:
        """T6: View empty list."""
        storage = InMemoryStorage()

        tasks = storage.get_all()

        assert tasks == []

    def test_get_all_returns_sorted_by_id(self) -> None:
        """Tasks are returned sorted by ID."""
        storage = InMemoryStorage()
        storage.add("Third")
        storage.add("First")
        storage.add("Second")

        tasks = storage.get_all()

        assert [t.id for t in tasks] == [1, 2, 3]


class TestToggleComplete:
    """Tests for toggling completion (FR-005)."""

    def test_toggle_incomplete_to_complete(self) -> None:
        """T7: Toggle incomplete to complete."""
        storage = InMemoryStorage()
        task = storage.add("Test task")
        assert task.completed is False

        updated = storage.toggle_complete(task.id)

        assert updated.completed is True

    def test_toggle_complete_to_incomplete(self) -> None:
        """T8: Toggle complete to incomplete."""
        storage = InMemoryStorage()
        task = storage.add("Test task")
        storage.toggle_complete(task.id)  # Now complete

        updated = storage.toggle_complete(task.id)

        assert updated.completed is False

    def test_toggle_non_existent_task_raises_error(self) -> None:
        """Toggling non-existent task fails."""
        storage = InMemoryStorage()

        with pytest.raises(TaskNotFoundError):
            storage.toggle_complete(999)


class TestCount:
    """Tests for task counting."""

    def test_count_empty_storage(self) -> None:
        """Empty storage returns zeros."""
        storage = InMemoryStorage()

        total, complete, pending = storage.count()

        assert total == 0
        assert complete == 0
        assert pending == 0

    def test_count_with_mixed_tasks(self) -> None:
        """Count correctly tracks complete and pending."""
        storage = InMemoryStorage()
        storage.add("Task 1")
        storage.add("Task 2")
        task3 = storage.add("Task 3")
        storage.toggle_complete(task3.id)

        total, complete, pending = storage.count()

        assert total == 3
        assert complete == 1
        assert pending == 2
