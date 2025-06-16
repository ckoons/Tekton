# Shared Requirements for Tekton Components

This directory contains shared requirement files to reduce duplication and ensure consistency across all Tekton components.

## Structure

### Core Requirements
- **`base.txt`** - Absolute essentials (pydantic, python-dotenv)
- **`web.txt`** - Web framework stack (FastAPI, uvicorn, websockets)
- **`ai.txt`** - AI/LLM integrations (anthropic, openai, litellm)
- **`vector.txt`** - Vector processing and ML (~6GB, includes PyTorch)
- **`database.txt`** - Database tools (SQLAlchemy, Alembic)

### Additional Requirements
- **`data.txt`** - Data processing (pandas, plotly, beautifulsoup4)
- **`utilities.txt`** - Common utilities (click, rich, structlog)
- **`dev.txt`** - Development only (pytest, flake8, black)

## Usage

In your component's `requirements.txt`:

```txt
# Include shared requirements
-r ../../shared/requirements/web.txt
-r ../../shared/requirements/ai.txt

# Add component-specific requirements
fastmcp>=1.0.0
tekton-core>=0.1.0

# Override shared versions if needed (use sparingly!)
# fastapi==0.95.0  # Component requires older version
```

## Installation with uv

```bash
# From component directory
uv pip install -r requirements.txt

# Or use uv sync if using pyproject.toml
uv sync
```

## Version Philosophy

- Use `>=` for all dependencies to allow updates
- Set minimum versions that are known to work
- Allow uv to resolve the best compatible versions
- Run `find-test-new-versions.py` periodically to check for updates

## Maintenance

1. Update shared requirements when multiple components need the same update
2. Test changes with `tekton-launch --launch-all`
3. Document any breaking changes
4. Keep requirements minimal - only add truly shared dependencies

## Components Using Each File

### web.txt (13 components)
Apollo, Budget, Engram, Ergon, Harmonia, Hermes, Metis, Rhetor, Sophia, Telos, Terma, LLMAdapter, tekton-llm-client

### ai.txt (7 components)
Apollo, Budget, Engram, Ergon, LLMAdapter, Rhetor, tekton-llm-client

### vector.txt (5 components)
Engram, Hermes, Rhetor, Sophia, tekton-core

### database.txt (5 components)
Budget, Ergon, Harmonia, Hermes, Metis

### data.txt (3 components)
Apollo, Sophia, Budget

## Notes

- Codex and Terma are excluded from consolidation (will be revised)
- LLMAdapter is deprecated (use tekton-llm-client instead)
- Vector requirements are the largest (~6GB) due to PyTorch and models