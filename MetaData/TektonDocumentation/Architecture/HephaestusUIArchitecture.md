# Hephaestus UI Architecture and DevTools Integration

## Overview

This document captures the discovered architecture of the Hephaestus UI system and how the UI DevTools interact with it. Created after hands-on exploration and fixes to the DevTools implementation.

## UI Architecture Discovery

### Single-Page Application Model

The Hephaestus UI follows a classic single-page application pattern:

1. **Main Container** (`index.html`):
   - Provides the persistent navigation structure
   - Defines the layout with left panel and content area
   - Contains all navigation items for Tekton components

2. **Component Loading**:
   - Each component has its own HTML file in `/Hephaestus/ui/components/[name]/`
   - Clicking a nav item dynamically loads that component's HTML into the content area
   - Components are not pre-loaded - they're injected on demand

3. **File Structure**:
   ```
   /Hephaestus/ui/
   ├── index.html                    # Main container with navigation
   ├── styles/                       # CSS files
   ├── scripts/                      # JavaScript files
   └── components/                   # Component-specific UI
       ├── apollo/apollo-component.html
       ├── athena/athena-component.html
       ├── prometheus/prometheus-component.html
       └── ... (all other components)
   ```

### UI Layout Pattern

The UI has a consistent three-panel layout:

1. **LEFT PANEL** (Navigation):
   - Persistent across all views
   - Contains nav items for all Tekton components
   - Semantic tag: `data-tekton-nav="main"`

2. **CONTENT AREA** (Dynamic):
   - Where component HTML gets injected
   - Changes based on selected nav item
   - Semantic tag: `data-tekton-area="content"`

3. **Component Structure** (Within Content Area):
   - Header: Component title and branding
   - Menu Bar: Tab navigation for component features
   - Scrolling Content: Dynamic based on selected tab
   - Footer: Component-specific actions

### Semantic Tagging System

The UI uses a comprehensive semantic tagging system with `data-tekton-*` attributes:

- `data-tekton-nav="main"` - Main navigation container
- `data-tekton-area="[area-name]"` - Major UI areas
- `data-tekton-nav-item="[component]"` - Navigation items
- `data-tekton-nav-target="[component]"` - Navigation targets
- `data-tekton-state="active|inactive"` - State indicators
- `data-tekton-section="[section-name]"` - UI sections
- `data-tekton-zone="[zone-name]"` - Component zones (header, menu, content, footer)
- `data-tekton-panel="[panel-name]"` - Specific panels

## How DevTools Work with This Architecture

### Key Insights

1. **Dynamic Content Challenge**:
   - DevTools can only capture/modify what's currently loaded
   - Must navigate to a component before working with it
   - Can't see all component UIs at once

2. **Area-Based Targeting**:
   - All DevTools use the 'area' parameter
   - 'hephaestus' captures the entire UI
   - Component names (e.g., 'rhetor') target loaded components
   - Can use CSS selectors within an area for precision

3. **Workflow Pattern**:
   ```
   1. Click nav item → Component loads
   2. ui_capture('area') → See component structure  
   3. ui_sandbox with changes → Modify component
   4. ui_interact → Test interactions
   ```

### DevTools Capabilities (After Fixes)

1. **ui_capture**:
   - Now returns proper DOM tree with children (recursive traversal)
   - Supports CSS selectors via BeautifulSoup
   - Shows element attributes, classes, and data tags

2. **ui_sandbox**:
   - Supports multiple change types:
     - `text`: Safe text content changes
     - `html`: HTML structure changes
     - `css`: Two formats for styling
   - CSS Format 1: `{"type":"css","selector":"...","property":"...","value":"..."}`
   - CSS Format 2: `{"type":"css","content":".class { rules }"}`

3. **ui_interact**:
   - Click, type, select, hover actions
   - Works within loaded components

4. **ui_analyze**:
   - Checks for frameworks (enforcement of no-framework rule)
   - Provides complexity assessment

## Component Instrumentation Patterns

### Standard Component Structure

Each component follows this pattern:

```html
<div class="[component-name]" 
     data-tekton-area="[component-name]"
     data-tekton-component="[component-name]">
    
    <!-- Header -->
    <div class="[component]__header" data-tekton-zone="header">
        <h2 class="[component]__title">Component Name</h2>
    </div>
    
    <!-- Menu Bar -->
    <div class="[component]__menu-bar" data-tekton-zone="menu">
        <div class="[component]__tabs">
            <div class="[component]__tab" data-tab="[tab-name]" 
                 onclick="[component]_switchTab('[tab-name]')">
                Tab Label
            </div>
        </div>
    </div>
    
    <!-- Content Area -->
    <div class="[component]__content" data-tekton-zone="content">
        <!-- Dynamic content based on selected tab -->
    </div>
    
    <!-- Footer -->
    <div class="[component]__footer" data-tekton-zone="footer">
        <!-- Component actions -->
    </div>
</div>
```

### Naming Conventions

- **CSS Classes**: BEM notation `[component]__[element]--[modifier]`
- **Functions**: `[component]_[action]()` (e.g., `prometheus_switchTab()`)
- **Data Attributes**: `data-tekton-[type]="[value]"`

## Practical DevTools Usage

### Finding Elements

1. **By Area**: `{"area": "prometheus"}`
2. **By Selector in Area**: `{"area": "prometheus", "selector": ".prometheus__menu-bar"}`
3. **By Data Attribute**: `{"area": "hephaestus", "selector": "[data-tekton-nav-item='rhetor']"}`

### Common Tasks

1. **Change Navigation Label**:
   ```json
   {
     "type": "text",
     "selector": "[data-component='budget'] .nav-label",
     "content": "Penia - LLM Cost",
     "action": "replace"
   }
   ```

2. **Add Status Indicator**:
   ```json
   {
     "type": "html",
     "selector": ".prometheus__header",
     "content": "<div class='status'>Connected</div>",
     "action": "append"
   }
   ```

3. **Style Component**:
   ```json
   {
     "type": "css",
     "selector": ".nav-item",
     "property": "background-color",
     "value": "rgba(255,255,255,0.1)"
   }
   ```

## Limitations and Workarounds

1. **Can't Move Elements Between Containers**:
   - DevTools excel at in-place modifications
   - Structural reorganization requires manual editing

2. **Component Must Be Loaded**:
   - Can't modify components that aren't currently displayed
   - Must navigate to component first

3. **Dynamic Content Challenges**:
   - Some content may be generated by JavaScript after load
   - May need to wait or interact to see all elements

## Next Steps for Full Instrumentation

To properly instrument all Tekton components for DevTools:

1. **Standardize Semantic Tags**:
   - Ensure all components have data-tekton-area
   - Add data-tekton-zone for major sections
   - Add data-tekton-action for interactive elements

2. **Document Component Patterns**:
   - Create template for new components
   - Document existing component variations

3. **Create Navigation Helpers**:
   - Scripts to navigate to each component
   - Validation tools to check instrumentation

## References

- [UI DevTools Cookbook](/MetaData/TektonDocumentation/Guides/UIDevToolsCookbook.md)
- [UI DevTools Explicit Guide](/MetaData/TektonDocumentation/Guides/UIDevToolsExplicitGuide.md)
- [Semantic UI Navigation Guide](/MetaData/TektonDocumentation/Guides/SemanticUINavigationGuide.md)