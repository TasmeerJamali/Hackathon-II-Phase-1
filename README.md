# Todo Evolution - Phase I

> 🗒️ **In-Memory Todo Console Application**  
> Built using Spec-Driven Development with Spec-Kit Plus

---

## 📋 Overview

Phase I of the "Evolution of Todo" hackathon project. A command-line todo application with 5 core features:

| Feature | Description |
|---------|-------------|
| ➕ Add Task | Create new tasks with title and description |
| 📋 View Tasks | Display all tasks in a Rich Table |
| ✏️ Update Task | Modify title or description |
| 🗑️ Delete Task | Remove tasks with confirmation |
| ✔️ Toggle Status | Mark complete/incomplete |

---

## 🛠️ Prerequisites

- **Python 3.13+**
- **UV** (Python package manager)

### Install UV

```bash
# On Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 🚀 Setup

```bash
# Clone or navigate to project directory
cd "Hackathon 2 PH 1"

# Sync dependencies
uv sync

# Run the application
uv run python -m src.main
```

---

## 📖 Usage

The application runs in interactive mode with a menu:

```
╭──────────────────────────────────────╮
│     🗒️  TODO CONSOLE - Phase I       │
├──────────────────────────────────────┤
│  [1] 📋 View all tasks               │
│  [2] ➕ Add new task                 │
│  [3] ✏️  Update task                  │
│  [4] 🗑️  Delete task                  │
│  [5] ✔️  Toggle complete/incomplete   │
│  [0] 🚪 Exit                         │
╰──────────────────────────────────────╯
```

### Task List Display

Tasks are shown in a styled table:

```
┏━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ ID ┃ Status ┃ Title           ┃ Description         ┃
┡━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ 1  │ ❌     │ Buy groceries   │ Milk, eggs          │
│ 2  │ ✅     │ Call mom        │ Birthday wishes     │
└────┴────────┴─────────────────┴─────────────────────┘
```

---

## 🧪 Development

```bash
# Run tests
uv run pytest

# Lint code
uv run ruff check .

# Format code
uv run ruff format .

# Type check
uv run mypy .
```

---

## 📁 Project Structure

```
Hackathon 2 PH 1/
├── .specify/                 # Spec-Kit Plus configuration
│   └── memory/
│       └── constitution.md   # Project principles
├── specs/
│   └── 001-phase1.md         # Feature specifications
├── src/
│   ├── __init__.py
│   ├── main.py               # Entry point
│   ├── cli.py                # Typer + Rich UI
│   ├── models.py             # Task dataclass
│   ├── storage.py            # In-memory storage
│   └── exceptions.py         # Custom exceptions
├── tests/
│   └── test_storage.py       # Unit tests
├── pyproject.toml            # UV configuration
├── README.md                 # This file
└── CLAUDE.md                 # AI agent instructions
```

---

## 📜 Spec-Driven Development

This project was built using **Spec-Driven Development (SDD)** methodology:

1. **Constitution** - `.specify/memory/constitution.md`
2. **Specification** - `specs/001-phase1.md`
3. **Implementation** - Generated from specs

---

## 🏆 Hackathon II - Evolution of Todo

**Phase I** establishes the foundation with in-memory storage.  
Future phases will add persistence, AI chatbot integration, and Kubernetes deployment.

---

*Built with 💜 using Spec-Kit Plus and Claude Code*
