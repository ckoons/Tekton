# Virtual Environment Strategy for Tekton

## Overview
Instead of 14+ separate virtual environments, use a tiered approach with shared environments based on dependency profiles.

## Recommended Structure

### 1. Core Environment (`tekton-core`)
For components using only web framework + tekton-core:
```bash
# Location: ~/venvs/tekton-core/
# Size: ~500MB
# Components: Apollo, Telos, Terma, Harmonia
uv venv ~/venvs/tekton-core
uv pip install -r shared/requirements/web.txt
uv pip install tekton-core tekton-llm-client fastmcp
```

### 2. CI Environment (`tekton-ai`) 
For components using LLM integrations:
```bash
# Location: ~/venvs/tekton-ai/
# Size: ~1GB
# Components: Budget, Rhetor, LLMAdapter
uv venv ~/venvs/tekton-ai
uv pip install -r shared/requirements/web.txt
uv pip install -r shared/requirements/ai.txt
uv pip install tekton-core tekton-llm-client
```

### 3. ML Environment (`tekton-ml`)
For components using vector/ML processing:
```bash
# Location: ~/venvs/tekton-ml/
# Size: ~6GB (due to PyTorch)
# Components: Engram, Hermes, Sophia
uv venv ~/venvs/tekton-ml
uv pip install -r shared/requirements/web.txt
uv pip install -r shared/requirements/vector.txt
uv pip install tekton-core
```

### 4. Data Environment (`tekton-data`)
For components with database + data processing:
```bash
# Location: ~/venvs/tekton-data/
# Size: ~2GB
# Components: Ergon, Metis, Harmonia
uv venv ~/venvs/tekton-data
uv pip install -r shared/requirements/web.txt
uv pip install -r shared/requirements/database.txt
uv pip install -r shared/requirements/data.txt
uv pip install tekton-core
```

### 5. Dev Environment (`tekton-dev`)
For development and testing:
```bash
# Location: ~/venvs/tekton-dev/
# Size: ~3GB
# Usage: Testing, linting, formatting
uv venv ~/venvs/tekton-dev
uv pip install -r shared/requirements/web.txt
uv pip install -r shared/requirements/dev.txt
uv pip install -r shared/requirements/ai.txt  # For testing
```

## Component Mapping

| Component | Environment | Rationale |
|-----------|------------|-----------|
| Apollo | tekton-core | Basic web + LLM via client |
| Athena | tekton-ml | Knowledge graphs need embeddings |
| Budget | tekton-ai | LLM cost tracking |
| Engram | tekton-ml | Vector memory storage |
| Ergon | tekton-data | Workflow + database |
| Harmonia | tekton-data | State management + database |
| Hermes | tekton-ml | Message routing + embeddings |
| Metis | tekton-data | Task planning + database |
| Prometheus | tekton-core | Monitoring (basic) |
| Rhetor | tekton-ai | Prompt optimization |
| Sophia | tekton-ml | Embeddings + data analysis |
| Synthesis | tekton-ai | Component coordination |
| Telos | tekton-core | Goal tracking (basic) |
| Terma | tekton-core | Terminal UI |

## Launch Script Integration

The `tekton-launch` script can be updated to:
```bash
# Detect which venv to use based on component
case $component in
  "engram"|"hermes"|"sophia"|"athena")
    source ~/venvs/tekton-ml/bin/activate
    ;;
  "budget"|"rhetor"|"synthesis")
    source ~/venvs/tekton-ai/bin/activate
    ;;
  "ergon"|"metis"|"harmonia")
    source ~/venvs/tekton-data/bin/activate
    ;;
  *)
    source ~/venvs/tekton-core/bin/activate
    ;;
esac
```

## Benefits
1. **Disk savings**: ~60GB → ~12GB total
2. **Update efficiency**: Update 5 venvs instead of 14
3. **Faster installs**: Shared packages installed once
4. **Cleaner testing**: Consistent environments

## Migration Path
1. Create the 5 shared environments
2. Update launch scripts to use appropriate venv
3. Remove individual component venvs
4. Document venv selection in each component

## Development Workflow
```bash
# For development across components
source ~/venvs/tekton-dev/bin/activate

# For running specific component
./scripts/tekton-launch.py --component hermes
# (script activates tekton-ml automatically)

# For testing imports
source ~/venvs/tekton-ml/bin/activate
python shared/requirements/verify-dependencies.py --dry-run
```

## Special Cases
- **Codex**: Keep separate (being rewritten)
- **Production**: Use single unified environment with all deps
- **Docker**: Each container gets minimal requirements