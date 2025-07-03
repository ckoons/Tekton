# Deprecated AI Routing and Personality Mapping Code

## Summary
This document identifies overcomplicated AI routing and personality mapping code that should be removed or marked as deprecated in favor of the simplified generic_specialist.py approach.

## Key Findings

### 1. **Registry Client - _component_to_role mapping** 
- **File**: `/shared/ai/registry_client.py`
- **Lines**: 740-754
- **Status**: Still in use but should be DEPRECATED
- **Reason**: Duplicates role mappings in tekton_ai_config.json and COMPONENT_EXPERTISE
- **Action**: Mark as DEPRECATED and rely on config file

### 2. **Personality Definitions in tekton_ai_config.json**
- **File**: `/config/tekton_ai_config.json`
- **Lines**: 18-26, 43-50, 69-76, etc. (personality sections for each AI)
- **Status**: Duplicates COMPONENT_EXPERTISE in generic_specialist.py
- **Action**: Remove personality sections from config, keep only ports and basic metadata

### 3. **Specialist Router References**
- **File**: `/Rhetor/rhetor/core/rhetor_component.py`
- **Lines**: 32, 61, 107-108, 187
- **Status**: Already commented out as DEPRECATED
- **Action**: Remove commented code entirely

### 4. **Dynamic Specialist Templates**
- **File**: `/Rhetor/rhetor/core/specialist_templates.py`
- **Status**: Entire file represents the old complex approach
- **Action**: Mark entire file as DEPRECATED or remove if not used

### 5. **AI Specialist Endpoints - Complex Routing**
- **File**: `/Rhetor/rhetor/api/ai_specialist_endpoints_unified.py`
- **Status**: Still contains hiring/firing metaphors and complex roster management
- **Action**: Simplify to basic registry lookups

### 6. **AI Discovery Service - Uses Deprecated Mappings**
- **File**: `/shared/ai/ai_discovery_service.py`
- **Lines**: 392, 407
- **Status**: Uses deprecated _component_to_role and _get_component_capabilities
- **Action**: Update to read from tekton_ai_config.json

## Recommended Actions

### 1. Update registry_client.py
```python
# Mark _component_to_role as deprecated
def _component_to_role(self, component: str) -> str:
    """
    DEPRECATED: Use roles from tekton_ai_config.json instead.
    This mapping duplicates configuration and should be removed.
    """
    # ... existing code ...
```

### 2. Simplify tekton_ai_config.json
Remove personality sections and keep only essential fields:
```json
{
  "ai_specialists": {
    "apollo": {
      "component": "apollo",
      "port": 45007,
      "roles": ["code-analysis", "code-generation"],
      "model": "llama3.3:70b",
      "auto_start": true,
      "active": true
    }
    // Remove personality, traits, communication_style sections
  }
}
```

### 3. Remove Specialist Router Code
Delete all commented specialist router references in rhetor_component.py

### 4. Mark specialist_templates.py as Deprecated
Add header to file:
```python
"""
DEPRECATED: This module represents the old dynamic specialist system.
Use generic_specialist.py and COMPONENT_EXPERTISE instead.

This file is kept for reference but should not be used for new code.
"""
```

### 5. Simplify AI Discovery
Replace complex hiring/firing metaphors with simple registry operations.

## Migration Path

1. All components should use `generic_specialist.py` with COMPONENT_EXPERTISE
2. Roles and capabilities should come from a single source (tekton_ai_config.json)
3. Remove all personality transformation logic
4. Use AI Registry for all specialist discovery and routing
5. Eliminate duplicate mappings between component names and roles

## Benefits of Removal

1. **Single Source of Truth**: COMPONENT_EXPERTISE in generic_specialist.py
2. **Reduced Complexity**: No more role mapping transformations
3. **Easier Maintenance**: One place to update AI personalities
4. **Consistent Behavior**: All AIs use the same generic implementation
5. **Cleaner Codebase**: Remove unused and deprecated code