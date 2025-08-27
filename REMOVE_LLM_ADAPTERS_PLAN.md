# LLM Adapter Removal Plan

## Overview
Remove all legacy LLM adapter code since components now use Rhetor for LLM interactions.

## Phase 1: Core Component Files to Remove
These files can be deleted entirely as they're pure LLM adapter implementations:

### Component-specific adapters (DELETE):
```bash
rm Engram/engram/core/llm_adapter.py
rm Telos/telos/core/llm_adapter.py
rm Budget/budget/adapters/llm_adapter.py
rm Terma/terma/core/llm_adapter.py
rm Sophia/sophia/core/llm_adapter.py
rm Metis/metis/core/llm_adapter.py
rm Synthesis/synthesis/core/llm_adapter.py
rm Prometheus/prometheus/utils/llm_adapter.py
rm Ergon/ergon/core/llm/adapter.py
rm Harmonia/harmonia/core/llm/adapter.py
```

### Shared adapter files (DELETE):
```bash
rm shared/llm_adapter_migration.py
```

### Example files (DELETE):
```bash
rm Ergon/examples/llm_adapter_example.py
rm Ergon/examples/run_llm_adapter_example.sh
rm Harmonia/examples/llm_adapter_example.py
rm Harmonia/examples/run_llm_adapter_example.sh
rm Telos/examples/run_llm_example.sh
```

### UI adapter client (DELETE):
```bash
rm Hephaestus/ui/scripts/shared/llm_adapter_client.js
```

## Phase 2: Files Requiring Code Removal
These files have imports or references that need to be cleaned:

### Python files with imports to fix:
1. **Budget/budget/service/assistant.py** (line 552)
   - Remove: `from budget.adapters.llm_adapter import get_llm_client`
   - Replace with Rhetor client if needed

2. **Synthesis/synthesis/core/step_handlers.py** (line 24)
   - Remove: `from synthesis.core.llm_adapter import get_llm_adapter`
   - Replace with Rhetor client

3. **Prometheus/prometheus/api/endpoints/llm_integration.py** (line 20)
   - Remove: `from ...utils.llm_adapter import PrometheusLLMAdapter`
   - Update to use Rhetor

4. **Metis/metis/core/task_decomposer.py** (line 14)
   - Remove: `from metis.core.llm_adapter import MetisLLMAdapter`
   - Update to use Rhetor

5. **Metis/metis/core/mcp/tools.py** (line 14)
   - Remove: `from metis.core.llm_adapter import MetisLLMAdapter`

6. **Metis/test_llm_connection.py** (line 9)
   - Remove: `from metis.core.llm_adapter import MetisLLMAdapter`
   - Update test to use Rhetor

7. **Terma/terma/api/app.py** (lines 453, 489, 508)
   - Remove all: `from ..core.llm_adapter import LLMAdapter`
   - Update endpoints to use Rhetor

8. **Sophia/sophia/api/endpoints/*.py** (experiments.py, recommendations.py, metrics.py)
   - Remove: `from sophia.core.llm_adapter import get_llm_adapter`
   - Update to use Rhetor

9. **Sophia/sophia/core/recommendation_system.py** (lines 593, 784)
   - Remove: `from .llm_adapter import get_llm_adapter`
   - Update to use Rhetor

10. **Engram/engram/api/llm_endpoints.py** (line 33)
    - Remove: `from engram.core.llm_adapter import LLMAdapter`
    - Update endpoints to use Rhetor

### JavaScript files to update:
1. **Hephaestus/ui/scripts/ergon/ergon-component.js**
   - Remove any llm_adapter references
   - Use Rhetor service instead

2. **Hephaestus/ui/scripts/hermes-connector.js**
   - Remove adapter references
   - Connect to Rhetor instead

3. **Hephaestus/ui/scripts/shared/chat-interface.js**
   - Remove adapter client usage
   - Use Rhetor endpoints

## Phase 3: Documentation Cleanup
Remove or update documentation files:

### Delete outdated docs:
```bash
rm -rf MetaData/Documentation/Architecture/LLMAdapter/
rm -rf MetaData/TektonDocumentation/Architecture/LLMAdapter/
rm MetaData/Documentation/Architecture/LLMIntegrationPlan.md
rm MetaData/TektonDocumentation/Architecture/LLMIntegrationPlan.md
rm MetaData/TektonDocumentation/Developer_Reference/LLMClient_Migration_Guide.md
```

### Update component documentation:
- Update all `llm_integration.md` files in ComponentDocumentation/
- Remove references from README files

## Phase 4: Configuration Cleanup

1. **config/tekton_components.yaml**
   - Remove any llm_adapter configuration

2. **shared/requirements/ai.txt**
   - Remove llm_adapter dependencies if listed

3. **Hephaestus/ui/server/component_registry.json**
   - Remove adapter registrations

## Phase 5: Testing

After removal, test each component:
```bash
# Test that components still work via Rhetor
python -m pytest Metis/tests/
python -m pytest Sophia/tests/
python -m pytest Terma/tests/
# ... etc for each component
```

## Execution Script

Create a script to automate the removal:

```bash
#!/bin/bash
# remove_llm_adapters.sh

echo "Phase 1: Removing adapter files..."
# Add all rm commands from Phase 1

echo "Phase 2: Cleaning imports..."
# Use sed to remove imports:
sed -i '' '/from.*llm_adapter/d' Budget/budget/service/assistant.py
sed -i '' '/from.*llm_adapter/d' Synthesis/synthesis/core/step_handlers.py
# ... etc

echo "Phase 3: Documentation cleanup..."
# Remove doc directories

echo "Complete! Now manually review and test each component."
```

## Manual Review Required

After automated removal:
1. Check each modified file for broken functionality
2. Ensure Rhetor client is properly initialized where needed
3. Update any configuration that referenced adapters
4. Run component tests to verify functionality

## Rollback Plan

Before starting:
```bash
git checkout -b remove-llm-adapters
git add -A
git commit -m "Checkpoint before removing LLM adapters"
```

If issues arise:
```bash
git checkout main
git branch -D remove-llm-adapters
```