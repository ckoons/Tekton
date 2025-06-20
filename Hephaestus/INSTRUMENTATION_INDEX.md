# Tekton UI Instrumentation Index

## Quick Start for Future Claudes
1. **Read First**: `INSTRUMENTATION_PATTERNS.md` - Explains all semantic tag patterns
2. **Check Status**: `INSTRUMENTATION_STATUS.md` - Current progress on all components
3. **See Example**: `ui/components/rhetor/rhetor-component.html` - Gold standard
4. **Test Tool**: Run `python3 tests/test_instrumentation.py` - Validates all components

## Component Instrumentation Status

### ✅ Fully Instrumented (2/23)
| Component | File Path | Tags | Test Status |
|-----------|-----------|------|-------------|
| rhetor | `ui/components/rhetor/rhetor-component.html` | 31 | ✓ Passes |
| profile | `ui/components/profile/profile-component.html` | 43 | ✓ Passes |

### ⚠️ Partially Instrumented (11/23)
Need zones added (header, menu, content, footer):
- apollo, athena, budget, engram, ergon, harmonia
- metis, prometheus, sophia, synthesis, telos

### ❌ Not Instrumented (10/23)
- codex, hermes, settings, terma, test, tekton
- tekton-dashboard, github-panel, telos-chat-tab, component-template

## Testing Instrumentation

### 1. Manual Testing Commands
```bash
# Count semantic tags in a component
grep -c "data-tekton-" ui/components/rhetor/rhetor-component.html

# List all semantic tag types
grep -o "data-tekton-[^=]*" ui/components/rhetor/rhetor-component.html | sort | uniq

# Find components missing instrumentation
grep -L "data-tekton-area" ui/components/*/*.html

# Check all components status
python3 tools/test_instrumentation.py
```

### 2. Automated Test Suite
See `tools/test_instrumentation.py` for automated validation that checks:
- [ ] Component has data-tekton-area
- [ ] Component has data-tekton-component
- [ ] Has at least 2 zones (header, content minimum)
- [ ] Menu items have proper navigation tags
- [ ] Panels have active/inactive states
- [ ] Actions have proper tags

### 3. Visual Testing (When UI Works)
```bash
# Use DevTools to validate semantic tags are discoverable
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -d '{"tool_name":"ui_semantic_analysis","arguments":{"component":"profile"}}'
```

## Key Files & Locations

### Documentation
- `INSTRUMENTATION_PATTERNS.md` - Complete guide to semantic patterns
- `INSTRUMENTATION_STATUS.md` - Current progress report
- `INSTRUMENTATION_INDEX.md` - This file
- `INSTRUMENTATION_HANDOFF.md` - Original requirements and progress

### Tools & Tests
- `tests/test_instrumentation.py` - Validation script
- `tests/add_zone_tags.py` - Helper to add zones to partial components (to be created)
- `tmp/check_uninstrumented.py` - Quick status checker

### Component Locations
All components: `ui/components/*/`
- Each has a `*-component.html` file
- Some have additional sub-components

## Semantic Tag Reference

### Required Tags (Minimum)
```html
data-tekton-area="component-name"
data-tekton-component="component-name"
data-tekton-zone="header|menu|content|footer"
```

### Navigation Tags
```html
data-tekton-nav="component-menu"
data-tekton-menu-item="Tab Name"
data-tekton-menu-active="true|false"
data-tekton-menu-panel="panel-id"
```

### Panel Tags
```html
data-tekton-panel="panel-name"
data-tekton-panel-for="Tab Name"
data-tekton-panel-active="true|false"
```

### Action Tags
```html
data-tekton-action="action-name"
data-tekton-action-type="primary|secondary"
```

## Next Steps Checklist
- [ ] Run `python3 tools/add_zone_tags.py` to complete partial components
- [ ] Manually instrument the 10 remaining components
- [ ] Run `python3 tools/test_instrumentation.py` to validate
- [ ] Update this index with test results
- [ ] Create component registry from semantic tags