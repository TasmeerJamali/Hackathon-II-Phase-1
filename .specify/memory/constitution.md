# Project Constitution: Todo Evolution - Phase I

> This constitution establishes the governing principles for the In-Memory Python Console Todo Application. All specifications, plans, and implementations must adhere to these principles.

---

## 1. Technical Standards

### 1.1 Language & Runtime
- **Python Version**: 3.13+
- **Package Manager**: UV (NOT pip)
- **Type Hints**: Required for all functions and class attributes
- **Encoding**: UTF-8 for all source files

### 1.2 Code Style
- **Formatter**: Ruff (via `uv run ruff format .`)
- **Linter**: Ruff (via `uv run ruff check .`)
- **Type Checker**: MyPy (via `uv run mypy .`)
- **Docstrings**: Google-style docstrings for all public modules, classes, and functions
- **Line Length**: Maximum 88 characters

### 1.3 Naming Conventions
| Element | Convention | Example |
|---------|------------|---------|
| Modules | snake_case | `task_storage.py` |
| Classes | PascalCase | `TaskManager` |
| Functions | snake_case | `add_task()` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_TITLE_LENGTH` |
| Variables | snake_case | `task_list` |

---

## 2. Architecture Principles

### 2.1 Separation of Concerns
```
src/
├── models.py      # Data structures only (no logic)
├── storage.py     # Storage operations (CRUD)
├── cli.py         # User interface (input/output)
└── main.py        # Entry point (orchestration)
```

### 2.2 Design Constraints
- **In-Memory Storage**: No database, no file persistence (Phase I requirement)
- **No External Dependencies**: Core functionality uses only Python stdlib
- **Dev Dependencies Allowed**: pytest, ruff, mypy for tooling
- **Single Responsibility**: Each module has exactly one purpose

### 2.3 Error Handling
- Use explicit exceptions (never fail silently)
- Custom exception classes for domain errors (e.g., `TaskNotFoundError`)
- User-friendly error messages in CLI

---

## 3. Testing Standards

### 3.1 Requirements
- **Framework**: pytest
- **Coverage Target**: 80%+ for core business logic
- **Location**: `tests/` directory, mirroring `src/` structure

### 3.2 Test Naming
```python
def test_<function_name>_<scenario>_<expected_outcome>():
    """Example: test_add_task_with_valid_title_creates_task"""
```

---

## 4. User Experience

### 4.1 CLI Behavior
- Clear menu-driven interface
- Numbered options for actions
- Confirmation for destructive operations (delete)
- Status indicators: `[ ]` incomplete, `[x]` complete

### 4.2 Output Format
```
=== TODO LIST ===
[1] [ ] Buy groceries - Get milk and eggs
[2] [x] Call mom - Done!
```

---

## 5. Governance

> **AMENDMENT (2025-12-07)**: Typer and Rich are now REQUIRED for modern UX.

### 5.1 Allowed Libraries
| Category | Allowed |
|----------|---------|
| Core | Python stdlib |
| CLI/UI | typer, rich (**Required for Modern UX**) |
| Dev | pytest, ruff, mypy |

### 5.2 Forbidden
- Databases (SQLite, etc.) - In-memory persistence only for Phase I
- File I/O for persistence - no saving state

### 5.3 Change Process
1. Update specification in `specs/`
2. Review against constitution
3. Generate implementation via AI
4. Verify with tests

---

## 6. Documentation

### 6.1 Required Files
- `README.md`: User-facing setup and usage
- `CLAUDE.md`: AI agent instructions
- `specs/`: All feature specifications
- `pyproject.toml`: Project configuration

### 6.2 Inline Documentation
- Module-level docstring explaining purpose
- Function docstrings with Args, Returns, Raises
- Comments only for non-obvious logic

---

*This constitution was established for Hackathon II - Evolution of Todo, Phase I.*
*Last updated: 2025-12-07*
