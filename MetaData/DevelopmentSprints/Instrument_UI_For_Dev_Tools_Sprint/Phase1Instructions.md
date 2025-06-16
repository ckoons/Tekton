# Phase 1 Instructions: Foundation & Core Components

## Overview

This phase establishes the foundation for UI instrumentation by creating standards, templates, and implementing core examples.

## Objectives

1. Implement ui_navigate helper tool
2. Create semantic tagging standards document  
3. Create component instrumentation template
4. Instrument 4 example components (Rhetor, Prometheus, Athena, Hermes)
5. Test DevTools with instrumented components

## Detailed Tasks

### Task 1: Implement ui_navigate Tool

Add to `/Hephaestus/hephaestus/mcp/ui_tools_v2.py`:

```python
async def ui_navigate(component: str) -> Dict[str, Any]:
    """
    Navigate to a specific component by clicking its nav item
    
    Args:
        component: Component name to navigate to (e.g., 'rhetor', 'prometheus')
        
    Returns:
        Navigation result with loaded component confirmation
    """
```

This tool should:
- Find the nav item with `data-tekton-nav-item="[component]"`  
- Click it to load the component
- Wait for component to load
- Confirm the component is active

### Task 2: Create Semantic Tagging Standards

Create `/MetaData/TektonDocumentation/Standards/SemanticTaggingStandards.md`:

Document the hierarchical tagging system:
- `data-tekton-area`: Component root containers
- `data-tekton-zone`: Major sections (header, menu, content, footer)
- `data-tekton-element`: Specific UI elements
- `data-tekton-action`: Interactive elements
- `data-tekton-state`: Dynamic states

Include:
- Naming conventions
- Required vs optional tags
- Examples for each tag type
- Special cases and exceptions

### Task 3: Create Component Template

Create `/Hephaestus/ui/components/shared/instrumented-component-template.html`:

```html
<!-- [Component] Component - [Description] -->
<div class="[component]" 
     data-tekton-area="[component]"
     data-tekton-component="[component]">
    
    <!-- Component Header -->
    <div class="[component]__header" 
         data-tekton-zone="header"
         data-tekton-element="component-header">
        <!-- Header content -->
    </div>
    
    <!-- Component Menu Bar -->
    <div class="[component]__menu-bar" 
         data-tekton-zone="menu"
         data-tekton-element="tab-navigation">
        <!-- Tab items with data-tekton-action -->
    </div>
    
    <!-- Component Content -->
    <div class="[component]__content" 
         data-tekton-zone="content"
         data-tekton-element="scrolling-area">
        <!-- Dynamic content -->
    </div>
    
    <!-- Component Footer -->
    <div class="[component]__footer" 
         data-tekton-zone="footer"
         data-tekton-element="action-bar">
        <!-- Footer actions -->
    </div>
</div>
```

### Task 4: Instrument Example Components

Apply the template to these components:

1. **Rhetor** (`/components/rhetor/rhetor-component.html`):
   - Add zone tags to header, chat area, input area
   - Add action tags to send button, clear button
   - Add state tags for connected/disconnected

2. **Prometheus** (`/components/prometheus/prometheus-component.html`):
   - Add zone tags to header, menu, content areas
   - Add action tags to each tab
   - Add element tags to planning widgets

3. **Athena** (`/components/athena/athena-component.html`):
   - Add zone tags to main sections
   - Add action tags to knowledge operations
   - Add element tags to search and display areas

4. **Hermes** (`/components/hermes/hermes-component.html`):
   - Add zone tags to message areas
   - Add action tags to message controls
   - Add state tags for message status

### Task 5: Test and Document

For each instrumented component:

1. Navigate using ui_navigate
2. Capture with ui_capture to verify tags
3. Test ui_sandbox modifications
4. Document any component-specific patterns

Create test results document showing:
- Successful navigation
- Tag visibility in captures
- Successful modifications
- Any issues or limitations

## Deliverables Checklist

- [ ] ui_navigate tool implemented and tested
- [ ] Semantic Tagging Standards document created
- [ ] Component instrumentation template created
- [ ] Rhetor fully instrumented with all tag types
- [ ] Prometheus fully instrumented with all tag types  
- [ ] Athena fully instrumented with all tag types
- [ ] Hermes fully instrumented with all tag types
- [ ] Test results documented for all components
- [ ] Any discovered patterns or issues documented

## Notes for Next Phase

Document any patterns, challenges, or insights discovered during this phase that will inform the bulk instrumentation work in Phase 2.