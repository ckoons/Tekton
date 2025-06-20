# DevToolsComponentImprovement_Sprint - Implementation Plan

## Overview

This document outlines the detailed implementation plan for the DevToolsComponentImprovement Development Sprint. It breaks down the high-level goals into specific implementation tasks, defines the phasing, specifies testing requirements, and identifies documentation that must be updated.

Tekton is an intelligent orchestration system that coordinates multiple AI models and resources to efficiently solve complex software engineering problems. This Implementation Plan focuses on enhancing the UI DevTools to properly handle dynamically loaded components and leverage semantic instrumentation.

## Debug Instrumentation Requirements

All code produced in this sprint **MUST** follow the [Debug Instrumentation Guidelines](/MetaData/TektonDocumentation/DeveloperGuides/Debugging/DebuggingInstrumentation.md). This section specifies the debug instrumentation requirements for this sprint's implementation.

### JavaScript Components

The following JavaScript components must be instrumented:

| Component | Log Level | Notes |
|-----------|-----------|-------|
| Component Loader | DEBUG | Log component load events and timing |
| Semantic Tag Parser | TRACE | Log all tags found and parsed |
| State Inspector | DEBUG | Log state snapshots and changes |

All instrumentation must use conditional checks:

```javascript
if (window.TektonDebug) TektonDebug.info('componentName', 'Message', optionalData);
```

### Python Components

The following Python components must be instrumented:

| Component | Log Level | Notes |
|-----------|-----------|-------|
| Navigation Tools | INFO | Log navigation attempts and results |
| UI Capture Tools | DEBUG | Log capture operations and semantic tags found |
| Wait Strategies | DEBUG | Log wait conditions and timeouts |

All instrumentation must use the `debug_log` utility:

```python
from shared.debug.debug_utils import debug_log, log_function

debug_log.info("component_name", "Message")
```

## Implementation Phases

This sprint will be implemented in 3 phases:

### Phase 1: Dynamic Component Detection Fix

**Objectives:**
- Fix component detection in dynamically loaded content
- Implement proper wait strategies
- Ensure semantic tags are discoverable

**Components Affected:**
- `/hephaestus/mcp/navigation_tools.py`
- `/hephaestus/mcp/ui_tools.py`
- `/ui/scripts/minimal-loader.js`

**Tasks:**

1. **Implement Component Load Detection**
   - **Description:** Create reliable detection for when components are fully loaded
   - **Deliverables:** 
     - Enhanced `wait_for_component_load()` function
     - Component ready indicators
   - **Acceptance Criteria:** 100% reliable component detection
   - **Dependencies:** None

2. **Fix Navigation Tool Wait Strategy**
   - **Description:** Update navigation to wait for component and semantic tags
   - **Deliverables:**
     - Updated `ui_navigate` tool
     - Semantic tag wait conditions
   - **Acceptance Criteria:** Navigation works for all 19 components
   - **Dependencies:** Task 1.1

3. **Enhance UI Capture for Dynamic Content**
   - **Description:** Improve capture to handle dynamically loaded HTML
   - **Deliverables:**
     - Updated `ui_capture` tool
     - Dynamic content detection
   - **Acceptance Criteria:** Captures all semantic tags
   - **Dependencies:** Task 1.1

4. **Create Semantic Tag Query Tool**
   - **Description:** New tool specifically for querying semantic tags
   - **Deliverables:**
     - `ui_semantic_query` tool
     - Tag relationship mapper
   - **Acceptance Criteria:** Can query any semantic tag pattern
   - **Dependencies:** Tasks 1.2, 1.3

**Code Examples:**

```python
# navigation_tools.py enhancement
async def wait_for_component_load(page, component_name: str, timeout: int = 10000):
    """Wait for component to be fully loaded with semantic tags"""
    debug_log.debug("navigation_tools", f"Waiting for {component_name} to load")
    
    # Wait for component container
    await page.wait_for_selector(
        f'[data-tekton-component="{component_name}"]',
        timeout=timeout,
        state="visible"
    )
    
    # Wait for zones to be present
    await page.wait_for_function(
        f"""
        () => {{
            const component = document.querySelector('[data-tekton-component="{component_name}"]');
            if (!component) return false;
            
            // Check for required zones
            const hasHeader = component.querySelector('[data-tekton-zone="header"]');
            const hasContent = component.querySelector('[data-tekton-zone="content"]');
            
            return hasHeader && hasContent;
        }}
        """,
        timeout=timeout
    )
    
    debug_log.info("navigation_tools", f"Component {component_name} fully loaded")
```

**Documentation Updates:**
- DevTools usage guide with new wait strategies
- Component loading lifecycle documentation
- Semantic tag query examples

**Testing Requirements:**
- Test all 19 components load successfully
- Verify semantic tags are captured
- Performance benchmarks for load times

### Phase 2: Semantic Tag Utilization

**Objectives:**
- Create tools that leverage semantic instrumentation
- Enable component state inspection
- Build relationship mapping capabilities

**Components Affected:**
- New `/hephaestus/mcp/semantic_tools.py`
- Enhanced `/hephaestus/mcp/ui_tools.py`
- Component state extractors

**Tasks:**

1. **Create Semantic Query Tool**
   - **Description:** Tool to query components by semantic tags
   - **Deliverables:**
     - `ui_semantic_query` function
     - Query builder interface
   - **Acceptance Criteria:** Can find any element by semantic tags
   - **Dependencies:** Phase 1 completion

2. **Build Component State Inspector**
   - **Description:** Extract and inspect component state
   - **Deliverables:**
     - `ui_inspect_state` tool
     - State snapshot functionality
   - **Acceptance Criteria:** Can inspect all component states
   - **Dependencies:** Task 2.1

3. **Implement Action Discovery Tool**
   - **Description:** Find all available actions in a component
   - **Deliverables:**
     - `ui_discover_actions` tool
     - Action categorization
   - **Acceptance Criteria:** Lists all data-tekton-action elements
   - **Dependencies:** Task 2.1

4. **Create Component Relationship Mapper**
   - **Description:** Map relationships between components
   - **Deliverables:**
     - `ui_map_relationships` tool
     - Visual relationship data
   - **Acceptance Criteria:** Shows component dependencies
   - **Dependencies:** Tasks 2.1, 2.2, 2.3

**Code Examples:**

```python
# semantic_tools.py
@tool_function
async def ui_semantic_query(area: str, query: dict) -> dict:
    """
    Query components using semantic tags
    
    @tekton-function ui_semantic_query
    @tekton-inputs [{"name": "area", "type": "str", "purpose": "component area"},
                    {"name": "query", "type": "dict", "purpose": "semantic query"}]
    @tekton-outputs {"type": "dict", "purpose": "matching elements and data"}
    """
    page = await get_page()
    
    # Build query selector from semantic tags
    selector_parts = []
    for tag, value in query.items():
        if tag.startswith('data-tekton-'):
            selector_parts.append(f'[{tag}="{value}"]')
    
    selector = ''.join(selector_parts)
    debug_log.debug("semantic_tools", f"Querying with selector: {selector}")
    
    # Find matching elements
    elements = await page.query_selector_all(selector)
    
    results = []
    for element in elements:
        result = {
            'tag': await element.evaluate('el => el.tagName'),
            'attributes': await element.evaluate('''el => {
                const attrs = {};
                for (const attr of el.attributes) {
                    if (attr.name.startsWith('data-tekton-')) {
                        attrs[attr.name] = attr.value;
                    }
                }
                return attrs;
            }'''),
            'text': await element.inner_text()
        }
        results.append(result)
    
    return {
        'query': query,
        'matches': len(results),
        'elements': results
    }
```

**Documentation Updates:**
- Semantic query language guide
- State inspection documentation
- Action discovery patterns

**Testing Requirements:**
- Query tests for all semantic tag types
- State inspection validation
- Action discovery coverage

### Phase 3: Testing Framework

**Objectives:**
- Build comprehensive testing for DevTools
- Create performance benchmarks
- Ensure reliability across all components

**Components Affected:**
- New `/tests/devtools/` test suite
- Performance monitoring
- Documentation

**Tasks:**

1. **Create DevTools Test Framework**
   - **Description:** Comprehensive test suite for all DevTools
   - **Deliverables:**
     - Test framework structure
     - Base test classes
   - **Acceptance Criteria:** Covers all DevTools functions
   - **Dependencies:** Phases 1 & 2

2. **Implement Component Navigation Tests**
   - **Description:** Test navigation for all 19 components
   - **Deliverables:**
     - Navigation test suite
     - Load time benchmarks
   - **Acceptance Criteria:** 100% pass rate
   - **Dependencies:** Task 3.1

3. **Build Semantic Query Tests**
   - **Description:** Test semantic tag queries
   - **Deliverables:**
     - Query test suite
     - Edge case coverage
   - **Acceptance Criteria:** All query patterns tested
   - **Dependencies:** Task 3.1

4. **Create Integration Tests**
   - **Description:** End-to-end workflow tests
   - **Deliverables:**
     - Integration test suite
     - Workflow documentation
   - **Acceptance Criteria:** Common workflows covered
   - **Dependencies:** All previous tasks

**Test Structure:**

```python
# tests/devtools/test_navigation.py
import pytest
from tests.devtools.base import DevToolsTestBase

class TestNavigation(DevToolsTestBase):
    """
    @tekton-class TestNavigation
    @tekton-purpose "Test DevTools navigation functionality"
    """
    
    @pytest.mark.parametrize("component", [
        "rhetor", "profile", "settings", "athena", "budget",
        "hermes", "apollo", "codex", "engram", "ergon",
        "harmonia", "metis", "prometheus", "sophia", 
        "synthesis", "tekton", "telos", "terma"
    ])
    async def test_component_navigation(self, component):
        """Test navigation to each component"""
        result = await self.execute_tool("ui_navigate", {
            "component": component
        })
        
        assert result["status"] == "success"
        
        # Verify component loaded
        semantic_result = await self.execute_tool("ui_semantic_query", {
            "area": component,
            "query": {
                "data-tekton-component": component
            }
        })
        
        assert semantic_result["matches"] > 0
```

**Documentation Updates:**
- DevTools testing guide
- Performance benchmarks
- Troubleshooting guide

**Testing Requirements:**
- 95%+ test coverage
- Performance regression tests
- Error scenario coverage

## Success Metrics

- **Component Load Success**: 100% of components load with semantic tags visible
- **Query Performance**: Semantic queries complete in <100ms
- **Test Coverage**: 95%+ code coverage in DevTools
- **Documentation**: Complete usage examples for all new tools
- **Reliability**: Zero failures in 100 consecutive component loads

## Migration Guide

For existing DevTools users:

1. **Navigation Changes**:
   - Old: `ui_navigate` might fail silently
   - New: `ui_navigate` waits for full component load
   - Migration: No code changes needed, just more reliable

2. **New Semantic Tools**:
   - `ui_semantic_query`: Query by any semantic tag
   - `ui_inspect_state`: Get component state
   - `ui_discover_actions`: Find available actions

3. **Enhanced Capture**:
   - Now captures all semantic tags in dynamic content
   - Includes component relationships

## Example Workflows

### Finding and Clicking a Button
```python
# Find button by semantic action
result = await execute_tool("ui_semantic_query", {
    "area": "profile",
    "query": {
        "data-tekton-action": "save-profile"
    }
})

# Click the button
await execute_tool("ui_interact", {
    "area": "profile",
    "selector": '[data-tekton-action="save-profile"]',
    "action": "click"
})
```

### Inspecting Component State
```python
# Get current state of a component
state = await execute_tool("ui_inspect_state", {
    "component": "rhetor"
})

print(f"Active tab: {state['active_tab']}")
print(f"Menu items: {state['menu_items']}")
print(f"Available actions: {state['actions']}")
```