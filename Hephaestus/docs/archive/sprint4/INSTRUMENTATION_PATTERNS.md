# Tekton UI Instrumentation Patterns

## Overview
This document describes the semantic tagging patterns used to make Tekton UI components discoverable and modifiable by AI/CI tools.

## Core Semantic Tag Categories

### 1. Component Root
Every component must have these attributes on its root element:
```html
<div class="component-name"
     data-tekton-area="component-name"
     data-tekton-component="component-name"
     data-tekton-type="component-workspace"
     data-tekton-description="Brief description of component purpose">
```

### 2. Layout Zones
Major layout areas within a component:
```html
data-tekton-zone="header"    <!-- Component header/title area -->
data-tekton-zone="menu"      <!-- Navigation/tab menu area -->
data-tekton-zone="content"   <!-- Main content area -->
data-tekton-zone="footer"    <!-- Footer area (if present) -->
```

Additional zone attributes:
- `data-tekton-section="header"` - Redundant but explicit section marker
- `data-tekton-scrollable="true"` - Indicates scrollable content areas

### 3. Navigation Elements
For tab-based navigation within components:
```html
<!-- Menu container -->
<div data-tekton-zone="menu" data-tekton-nav="component-menu">

<!-- Individual menu items/tabs -->
<div data-tekton-menu-item="Tab Name"
     data-tekton-menu-component="component-name"
     data-tekton-menu-active="true|false"
     data-tekton-menu-panel="panel-id">
```

### 4. Content Panels
For tab content panels:
```html
<div id="panel-id" 
     data-tekton-panel="panel-name"
     data-tekton-panel-for="Tab Name"
     data-tekton-panel-component="component-name"
     data-tekton-panel-active="true|false">
```

### 5. Interactive Elements
For buttons and actions:
```html
<button data-tekton-action="action-name"
        data-tekton-action-type="primary|secondary">
```

### 6. AI Integration (Advanced)
For AI-aware components:
```html
data-tekton-ai="ai-specialist-name"
data-tekton-ai-ready="true|false"
```

## Implementation Status

### ✅ Fully Instrumented (12 components)
- **rhetor** - Excellent example with all patterns
- **profile** - Just completed with full instrumentation
- apollo, athena, budget, engram, ergon, harmonia, metis, prometheus, sophia, synthesis, telos

### ❌ Not Yet Instrumented (11 components)
- codex, hermes, settings, terma, test, tekton, tekton-dashboard, github-panel, telos-chat-tab, component-template

## Example: Profile Component
```html
<div class="profile"
     data-tekton-area="profile"
     data-tekton-component="profile"
     data-tekton-type="component-workspace"
     data-tekton-description="User profile and preferences management">
    
    <div class="profile__header" data-tekton-zone="header">
        <!-- Header content -->
    </div>
    
    <div class="profile__menu-bar" data-tekton-zone="menu" data-tekton-nav="component-menu">
        <div class="profile__tab"
             data-tekton-menu-item="Personal Information"
             data-tekton-menu-active="true">
            <!-- Tab content -->
        </div>
    </div>
    
    <div class="profile__content" data-tekton-zone="content">
        <div id="personal-panel"
             data-tekton-panel="personal"
             data-tekton-panel-active="true">
            <!-- Panel content -->
        </div>
    </div>
</div>
```

## Benefits
1. **Discoverability** - AI/CI can find any UI element
2. **Context** - Clear understanding of element purpose and relationships
3. **State Management** - Active/inactive states are explicit
4. **Navigation** - Panel/tab relationships are machine-readable
5. **Actions** - Buttons and interactions are clearly marked

## Next Steps
1. Apply these patterns to remaining 11 components
2. Create automated validation to ensure pattern compliance
3. Build component registry that reads these tags
4. Enable AI/CI tools to use these tags for navigation and modification