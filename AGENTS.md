# Agent Guidelines for dia-mcp

This project is a Model Context Protocol (MCP) server for finding UI/UX inspiration images from various platforms.

## Project Overview

- **Language**: Python 3.13+
- **Package Manager**: uv
- **Server Framework**: FastMCP
- **Database**: SQLite (via aiosqlite)
- **External APIs**: Firecrawl, Tinyfish

## Build / Lint / Test Commands

```bash
# Install dependencies
uv sync

# Run type checking (pyright)
uv run pyright src/

# Run linter (ruff)
uv run ruff check src/

# Run formatter (ruff)
uv run ruff format src/

# Run all checks (typecheck + lint + format)
uv run ruff check src/ && uv run ruff format --check src/ && uv run pyright src/

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/test_filename.py::test_function_name

# Run tests with verbose output
uv run pytest -v

# Add new dependency
uv add <package>

# Add new dev dependency
uv add --group dev <package>
```

## Code Style Guidelines

### Imports

- Use `from __future__ import annotations` for forward references
- Group imports: stdlib → third-party → local
- Use relative imports for intra-package imports: `from dia.clients import firecrawl as fc`
- Avoid wildcard imports

```python
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastmcp import FastMCP
from pydantic import BaseModel

from dia.clients import firecrawl as fc
from dia.index.db import init as init_db
```

### Formatting

- Use 4 spaces for indentation
- Maximum line length: 88 characters (ruff default)
- Use trailing commas for multi-line collections
- Add blank lines between functions and major sections
- Use section comments with fill characters:

```python
# ── Imports ────────────────────────────────────────────────────

# ── Tools ─────────────────────────────────────────────────────

# ── Helpers ───────────────────────────────────────────────────
```

### Type Hints

- Use Python 3.13+ union syntax: `ctx: Context | None = None`
- Use `list[dict]` instead of `List[Dict]` (no typing module needed)
- Use `dict[str, InspoSource]` for mappings
- Define data classes with `@dataclass(frozen=True)` for immutable configs
- Use Pydantic `BaseModel` for validated data structures

### Naming Conventions

- **Modules**: snake_case (`find_inspo.py`, `firecrawl.py`)
- **Classes**: PascalCase (`InspoSource`, `BaseModel`)
- **Functions/variables**: snake_case (`find_inspo`, `screenshot_urls`)
- **Constants**: SCREAMING_SNAKE_CASE (`TINYFISH_API_KEY`)
- **Private functions**: prefix with underscore (`_fc_search`)

### Error Handling

- Use bare `except Exception:` only when necessary, catch specific exceptions
- Always include error context in messages
- Return graceful error responses rather than raising

```python
try:
    res = fc.search(query, limit=limit)
except Exception as e:
    results.append({"error": str(e)})
```

### Async Patterns

- Use `async`/`await` for I/O operations
- Use `asyncio.gather()` for parallel operations
- Use `aiofiles` for file I/O when needed
- Database operations are async via aiosqlite

### Docstrings

- Use Google-style docstrings with Args/Returns sections
- Include examples for complex functions
- Keep brief and descriptive

```python
async def find_inspo(
    query: str,
    platform: str = "auto",
    limit: int = 12,
) -> str:
    """
    🎨 Find UI/UX inspiration images.

    Args:
        query: Search query (e.g., "onboarding flow")
        platform: Source platform or "auto" for smart selection
        limit: Maximum results to return

    Returns:
        JSON string with results
    """
```

### Tool Definition

Tools use the `@mcp.tool` decorator:

```python
@mcp.tool
async def tool_name(
    param: str,
    optional_param: int = 10,
    ctx: Context | None = None,
) -> str:
    """Tool description shown to LLM."""
    # Implementation
    return json.dumps(result)
```

### Configuration

- Store config in `src/dia/config.py`
- Use environment variables with defaults
- Use Path objects for file paths
- Never commit secrets (use `.env` for local dev)

### Testing

- Tests go in `tests/` directory
- Use pytest with pytest-asyncio for async tests
- Test file naming: `test_*.py`
- Use fixtures for common setup
- Mock external API calls (Firecrawl, Tinyfish)

### File Organization

```
src/dia/
├── __init__.py       # Package exports
├── server.py         # MCP server entry point
├── config.py         # Configuration
├── sources.py        # Source registry
├── clients/          # External API clients
│   ├── firecrawl.py
│   └── tinyfish.py
├── tools/            # MCP tools
│   ├── find_inspo.py
│   ├── screenshot.py
│   └── ...
├── index/            # Database operations
│   └── db.py
└── prompts/          # MCP prompts
    └── inspo_hunt.py
```

### General Rules

- Keep functions focused and single-purpose
- Use constants for magic values
- Prefer explicit over implicit
- Use descriptive variable names
- Add emoji indicators in docstrings for MCP tools
- Return JSON strings from tools (not dicts)
