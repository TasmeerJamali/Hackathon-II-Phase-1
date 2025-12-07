# CLAUDE.md

> This file provides instructions for Claude Code (AI coding assistant) when working on this project.

---

## Project Overview

**Phase I**: Todo In-Memory Python Console Application  
**Methodology**: Spec-Driven Development (SDD) with Spec-Kit Plus  
**Tech Stack**: Python 3.13+, UV

---

## Commands

```bash
# Run the application
run: uv run python -m src.main

# Run tests
test: uv run pytest

# Lint the code
lint: uv run ruff check .

# Format the code
format: uv run ruff format .

# Type check
typecheck: uv run mypy .
```

---

## Project Structure

```
Hackathon 2 PH 1/
├── .specify/
│   └── memory/
│       └── constitution.md    # Project principles (READ FIRST)
├── specs/
│   └── 001-phase1.md          # Feature specifications
├── src/
│   ├── __init__.py
│   ├── main.py                # Entry point
│   ├── models.py              # Task dataclass
│   ├── storage.py             # InMemoryStorage
│   ├── cli.py                 # User interface
│   └── exceptions.py          # Custom exceptions
├── tests/
│   └── ...                    # Test files
├── pyproject.toml             # UV project config
├── README.md                  # User documentation
└── CLAUDE.md                  # This file
```

---

## Development Workflow

1. **Read Constitution First**: `.specify/memory/constitution.md`
2. **Follow Specifications**: `specs/001-phase1.md`
3. **Generate Code**: Based on specs, not from scratch
4. **Run Tests**: `uv run pytest`
5. **Lint & Format**: `uv run ruff check . && uv run ruff format .`

---

## Key Principles

- **No External Runtime Dependencies**: Use Python stdlib only
- **Type Hints Required**: All functions and class attributes
- **In-Memory Storage**: No file I/O or databases
- **Clean Code**: Follow PEP 8, use Ruff for formatting
- **Test Coverage**: Aim for 80%+ on core logic

---

## Constitution Reference

The project constitution at `.specify/memory/constitution.md` defines:
- Naming conventions
- Allowed/forbidden libraries
- Architecture patterns
- Testing standards

**Always reference the constitution before making changes.**

---

## Spec-Kit Plus Commands (Simulated)

Since this project simulates Spec-Kit Plus:
- `/sp.constitution` → `.specify/memory/constitution.md`
- `/sp.specify` → `specs/001-phase1.md`
- `/sp.plan` → Implementation plan (in specs)
- `/sp.tasks` → Task breakdown
- `/sp.implement` → Code generation from specs

---

*Hackathon II - Evolution of Todo*
