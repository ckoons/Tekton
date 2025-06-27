# Semantic Tags Reference - CSS-First Architecture

## Overview

The simplified Hephaestus UI uses semantic `data-tekton-*` attributes to enable AI navigation and UI DevTools interaction. These tags are now statically embedded in the pre-loaded HTML.

## Root Structure

```html
<div class="app-container" data-tekton-root="true">
    <!-- Main content area with all components -->
    <div class="main-content" 
         data-tekton-area="content"
         data-tekton-type="workspace">
        <!-- All components pre-loaded here -->
    </div>
    
    <!-- Navigation panel -->
    <div class="left-panel" 
         data-tekton-nav="main"
         data-tekton-area="navigation">
        <!-- Navigation structure -->
    </div>
</div>
```

## Component Container Tags

Each component is wrapped with semantic tags:

```html
<div id="rhetor" class="component" 
     data-tekton-area="rhetor"
     data-tekton-type="component-container"
     data-tekton-visibility="hidden">
    <!-- Component content -->
</div>
```

### Visibility States
- `data-tekton-visibility="visible"` - Currently displayed component
- `data-tekton-visibility="hidden"` - Hidden components
- Updated automatically by `app-minimal.js` based on URL hash

## Navigation Tags

### Navigation Structure
```html
<div class="left-panel-nav" 
     data-tekton-zone="main"
     data-tekton-section="nav-main">
    <ul class="component-nav" 
        data-tekton-list="components"
        data-tekton-nav-type="primary">
        <!-- Nav items -->
    </ul>
</div>
```

### Navigation Items
```html
<li class="nav-item" 
    data-component="rhetor"
    data-tekton-nav-item="rhetor"
    data-tekton-nav-target="rhetor"
    data-tekton-state="inactive">
    <a href="#rhetor" class="nav-link">
        <span class="nav-label">Rhetor - LLM/Prompt/Context</span>
        <span class="status-indicator" 
             data-tekton-status="rhetor-health"
             data-status="inactive"></span>
    </a>
</li>
```

### States
- `data-tekton-state="active"` - Currently selected
- `data-tekton-state="inactive"` - Not selected
- Updated by `handleHashChange()` in `app-minimal.js`

## Component Internal Structure

Components maintain their semantic structure:

```html
<div class="rhetor" data-tekton-component="rhetor">
    <div class="rhetor__header" data-tekton-zone="header">
        <!-- Header content -->
    </div>
    <div class="rhetor__menu-bar" data-tekton-zone="menu">
        <!-- Tabs/menu -->
    </div>
    <div class="rhetor__content" data-tekton-zone="content">
        <!-- Main content -->
    </div>
    <div class="rhetor__footer" data-tekton-zone="footer">
        <!-- Chat input -->
    </div>
</div>
```

## Chat Interface Tags

```html
<div class="chat-interface" data-tekton-chat="companion">
    <div class="chat-messages" 
         id="numa-companion-messages" 
         data-tekton-messages="companion">
        <!-- Messages -->
    </div>
</div>

<input type="text" 
       class="chat-input"
       data-tekton-input="chat-input"
       data-tekton-input-type="chat">

<button data-tekton-action="send-message"
        data-tekton-action-type="primary">
    Send
</button>
```

## Health Status Tags

Status indicators for component health:

```html
<span class="status-indicator" 
      data-tekton-status="rhetor-health"
      data-status="inactive"></span>
```

States:
- `data-status="inactive"` - Component not running
- `data-status="connected"` - Component healthy (adds `.connected` class)

## Zone Hierarchy

The UI follows this zone hierarchy:
1. `data-tekton-area` - Major regions (navigation, content, component names)
2. `data-tekton-zone` - Sub-regions (header, main, footer)
3. `data-tekton-section` - Specific sections within zones

## Dynamic Updates

The minimal JavaScript (`app-minimal.js`) updates these attributes:

1. **On hash change**: Updates visibility and state
2. **On health check**: Updates status indicators
3. **On WebSocket connection**: Updates connection states

## Benefits

1. **AI Navigation**: Clear semantic structure for AI assistants
2. **DevTools Compatible**: Semantic tags enable UI DevTools
3. **State Tracking**: Visibility and active states tracked via attributes
4. **Minimal JavaScript**: Most behavior is CSS, tags just track state

## Adding New Components

When adding a component:
1. Include all semantic tags in the component HTML
2. Add to `COMPONENTS` list in `build-simplified.py`
3. Run `python3 build-simplified.py`
4. Tags are automatically integrated