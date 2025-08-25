# CI Platform Cleanup Tasks

## Overview
After pushing to GitHub, we have a green field to remove deprecated code from the CI Platform Integration Sprint.

## Deprecated Files to Remove

### 1. Core Deprecated Stubs
```bash
# These are stub files that can be safely deleted
Rhetor/rhetor/core/ai_specialist_manager.py  # DEPRECATED stub
Rhetor/rhetor/core/specialist_router.py      # DEPRECATED stub
Rhetor/rhetor/core/socket_specialist_integration.py  # Old integration
Rhetor/rhetor/core/component_specialists.py  # Old specialist system
```

### 2. Old MCP Integration
```bash
Rhetor/rhetor/core/mcp/tools_integration.py  # Replaced by tools_integration_unified.py
Rhetor/rhetor/core/mcp/init_integration.py   # Old initialization
```

### 3. Backup/Original Files
```bash
Rhetor/rhetor/api/app_original.py  # Old API backup
```

### 4. Old CI Messaging
```bash
Rhetor/rhetor/core/ai_messaging_integration.py  # Replaced by CI Registry
```

## Import References to Clean

### 1. In rhetor_component.py
- Remove: `from .specialist_router import SpecialistRouter`
- Already done: Removed CI specialist manager references

### 2. Check and Update
Files that might have old imports:
- `Rhetor/rhetor/core/mcp/dynamic_specialist_tools.py`
- Any files in `MetaData/DevelopmentSprints/Completed/` (these are archived, leave as-is)

## Code Sections to Clean

### 1. Rhetor Component (rhetor_component.py)
- Line 79-80: Warning about deprecated SpecialistRouter
- Remove specialist_router initialization

### 2. LLM Client References
Check if `llm_client.py` still has old provider-specific code that should be removed.

## Safe Cleanup Commands

```bash
# 1. Remove deprecated stub files
rm Rhetor/rhetor/core/ai_specialist_manager.py
rm Rhetor/rhetor/core/specialist_router.py
rm Rhetor/rhetor/core/socket_specialist_integration.py
rm Rhetor/rhetor/core/component_specialists.py

# 2. Remove old MCP files
rm Rhetor/rhetor/core/mcp/tools_integration.py
rm Rhetor/rhetor/core/mcp/init_integration.py

# 3. Remove backup files
rm Rhetor/rhetor/api/app_original.py

# 4. Remove old integration
rm Rhetor/rhetor/core/ai_messaging_integration.py
```

## Testing After Cleanup

```bash
# 1. Start Rhetor and verify no import errors
tekton-launch rhetor

# 2. Test MCP tools still register
tekton-status -c rhetor -l 50 | grep "Tool registered"

# 3. Test CI endpoints work
curl http://localhost:8003/api/ai/specialists

# 4. Verify Greek Chorus still registers
tekton-status -c apollo,athena,prometheus
```

## Additional Cleanup Opportunities

### 1. Unified CI Client
Check if `unified_ai_client.py` has any old provider logic that can be simplified.

### 2. Model Router
Review if `model_router.py` still needs provider-specific routing or can be simplified.

### 3. Old Config Files
Look for any old specialist configuration files in:
- `Rhetor/rhetor/config/`
- `.tekton/config/`

## Notes
- The dual architecture (socket vs API) is intentional - don't remove socket code
- Keep the unified endpoints and CI Registry integration
- The MCP tools_integration_unified.py needs completion, not removal
- Don't touch files in `MetaData/DevelopmentSprints/Completed/` - these are historical

## Verification Checklist
- [ ] All deprecated files removed
- [ ] No import errors on startup
- [ ] MCP tools still register
- [ ] CI discovery works
- [ ] Greek Chorus CIs register
- [ ] Rhetor API endpoints respond
- [ ] No orphaned imports