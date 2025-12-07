"""CLI interface for Todo Console Application using Typer and Rich.

This module provides the user interface following the specification:
- Rich Panel for main menu (Section 5.1)
- Rich Table for task list with ✅/❌ icons (FR-004)
- Typer for command structure
- User-friendly prompts and confirmations
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

from src.exceptions import TaskNotFoundError, ValidationError
from src.storage import InMemoryStorage

# Initialize Rich console
console = Console()

# Create Typer app
app = typer.Typer(
    name="todo",
    help="🗒️ Todo Console Application - Phase I",
    add_completion=False,
)

# Global storage instance
storage = InMemoryStorage()


def display_menu() -> None:
    """Display the main menu using Rich Panel."""
    menu_text = """
[bold cyan][1][/] 📋 View all tasks
[bold cyan][2][/] ➕ Add new task
[bold cyan][3][/] ✏️  Update task
[bold cyan][4][/] 🗑️  Delete task
[bold cyan][5][/] ✔️  Toggle complete/incomplete
[bold cyan][0][/] 🚪 Exit
"""
    panel = Panel(
        menu_text.strip(),
        title="🗒️ [bold blue]TODO CONSOLE - Phase I[/]",
        border_style="blue",
        padding=(1, 2),
    )
    console.print(panel)


def view_tasks() -> None:
    """Display all tasks in a Rich Table (FR-004)."""
    tasks = storage.get_all()

    if not tasks:
        console.print(
            Panel(
                "[yellow]No tasks found. Add one![/]",
                title="📋 Task List",
                border_style="yellow",
            )
        )
        return

    # Create Rich Table
    table = Table(
        title="📋 Task List",
        show_header=True,
        header_style="bold magenta",
        border_style="blue",
    )

    table.add_column("ID", style="cyan", justify="center", width=6)
    table.add_column("Status", justify="center", width=8)
    table.add_column("Title", style="white", min_width=20)
    table.add_column("Description", style="dim", min_width=25)

    for task in tasks:
        # Status icon with color
        if task.completed:
            status = Text("✅", style="green")
        else:
            status = Text("❌", style="red")

        description = task.description if task.description else "(no description)"

        table.add_row(
            str(task.id),
            status,
            task.title,
            description,
        )

    console.print(table)

    # Summary
    total, complete, pending = storage.count()
    console.print(
        f"\n[bold]Total:[/] {total} tasks "
        f"([green]{complete} complete[/], [red]{pending} pending[/])"
    )


def add_task() -> None:
    """Add a new task (FR-001)."""
    console.print("\n[bold blue]➕ Add New Task[/]")
    console.print("-" * 30)

    title = Prompt.ask("[cyan]Title[/]")
    description = Prompt.ask("[cyan]Description[/] (optional)", default="")

    try:
        task = storage.add(title, description)
        console.print(
            f"\n[green]✓ Task #{task.id} created:[/] {task.title}",
            style="bold",
        )
    except ValidationError as e:
        console.print(f"\n[red]✗ Error:[/] {e.message}")


def update_task() -> None:
    """Update an existing task (FR-003)."""
    console.print("\n[bold blue]✏️ Update Task[/]")
    console.print("-" * 30)

    try:
        task_id = int(Prompt.ask("[cyan]Task ID to update[/]"))
    except ValueError:
        console.print("[red]✗ Error:[/] Invalid ID format")
        return

    try:
        task = storage.get(task_id)

        # Show current values
        console.print(f"\n[dim]Current title:[/] {task.title}")
        console.print(f"[dim]Current description:[/] {task.description or '(empty)'}")
        console.print("\n[dim]Press Enter to keep current value[/]")

        new_title = Prompt.ask("[cyan]New title[/]", default="")
        new_description = Prompt.ask("[cyan]New description[/]", default="")

        # Only update if user provided new values
        title_update = new_title if new_title else None
        desc_update = new_description if new_description else None

        if title_update is None and desc_update is None:
            console.print("[yellow]No changes made[/]")
            return

        storage.update(task_id, title=title_update, description=desc_update)
        console.print(f"\n[green]✓ Task #{task_id} updated[/]", style="bold")

    except TaskNotFoundError as e:
        console.print(f"\n[red]✗ Error:[/] {e}")
    except ValidationError as e:
        console.print(f"\n[red]✗ Error:[/] {e.message}")


def delete_task() -> None:
    """Delete a task with confirmation (FR-002)."""
    console.print("\n[bold blue]🗑️ Delete Task[/]")
    console.print("-" * 30)

    try:
        task_id = int(Prompt.ask("[cyan]Task ID to delete[/]"))
    except ValueError:
        console.print("[red]✗ Error:[/] Invalid ID format")
        return

    try:
        task = storage.get(task_id)

        # Confirmation prompt
        if Confirm.ask(f"Delete task #{task_id} '{task.title}'?", default=False):
            storage.delete(task_id)
            console.print(f"\n[green]✓ Task #{task_id} deleted[/]", style="bold")
        else:
            console.print("[yellow]Deletion cancelled[/]")

    except TaskNotFoundError as e:
        console.print(f"\n[red]✗ Error:[/] {e}")


def toggle_complete() -> None:
    """Toggle task completion status (FR-005)."""
    console.print("\n[bold blue]✔️ Toggle Complete/Incomplete[/]")
    console.print("-" * 30)

    try:
        task_id = int(Prompt.ask("[cyan]Task ID to toggle[/]"))
    except ValueError:
        console.print("[red]✗ Error:[/] Invalid ID format")
        return

    try:
        task = storage.toggle_complete(task_id)

        if task.completed:
            console.print(
                f"\n[green]✓ Task #{task_id} marked as complete ✓[/]",
                style="bold",
            )
        else:
            console.print(
                f"\n[yellow]○ Task #{task_id} marked as incomplete[/]",
                style="bold",
            )

    except TaskNotFoundError as e:
        console.print(f"\n[red]✗ Error:[/] {e}")


def run_interactive_menu() -> None:
    """Run the interactive menu loop."""
    console.print(
        "\n[bold magenta]Welcome to Todo Console - Phase I[/]",
        style="bold",
    )
    console.print("[dim]Evolution of Todo - Hackathon II[/]\n")

    while True:
        display_menu()
        choice = Prompt.ask("\n[bold]Enter choice[/]", default="0")

        if choice == "1":
            view_tasks()
        elif choice == "2":
            add_task()
        elif choice == "3":
            update_task()
        elif choice == "4":
            delete_task()
        elif choice == "5":
            toggle_complete()
        elif choice == "0":
            console.print("\n[bold green]Goodbye! 👋[/]")
            raise typer.Exit()
        else:
            console.print("[red]Invalid choice. Please try again.[/]")

        console.print()  # Blank line before next menu


@app.command()
def main() -> None:
    """🗒️ Todo Console Application - Interactive Mode."""
    run_interactive_menu()


if __name__ == "__main__":
    app()
