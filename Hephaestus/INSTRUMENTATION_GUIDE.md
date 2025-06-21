# Tekton UI Instrumentation Guide

## Overview

This guide provides a comprehensive reference for Tekton's semantic instrumentation system - a structured approach to making UI components and codebase elements discoverable and modifiable by AI/CI tools. The instrumentation uses semantic HTML attributes (`data-tekton-*`) to create a machine-readable interface for the entire platform.

## Philosophy and Goals

### Core Principles
1. **Simple is better** - No frameworks, vanilla HTML/CSS/JS only
2. **AI-friendly** - Every element should be discoverable and understandable
3. **CI empowerment** - Computational Intelligences can modify anything independently
4. **Semantic clarity** - Tags should clearly describe purpose and relationships

### Benefits
- **Discoverability** - AI/CI tools can find any UI element or code component
- **Context** - Clear understanding of element purpose and relationships
- **State Management** - Component states are explicit and observable
- **Navigation** - Panel/tab relationships are machine-readable
- **Actions** - Interactive elements are clearly identified

## Complete Tag Categories

### 1. Component Root Tags
Every component must have these attributes on its root element:

```html
<div class="component-name"
     data-tekton-area="component-name"
     data-tekton-component="component-name"
     data-tekton-type="component-workspace"
     data-tekton-description="Brief description of component purpose">
```

### 2. Layout Zone Tags
Major layout areas within a component:

```html
data-tekton-zone="header"    <!-- Component header/title area -->
data-tekton-zone="menu"      <!-- Navigation/tab menu area -->
data-tekton-zone="content"   <!-- Main content area -->
data-tekton-zone="footer"    <!-- Footer area (if present) -->
```

Additional zone attributes:
- `data-tekton-section="header"` - Explicit section marker
- `data-tekton-scrollable="true"` - Indicates scrollable content areas

### 3. Navigation Tags
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

### 4. Content Panel Tags
For tab content panels:

```html
<div id="panel-id" 
     data-tekton-panel="panel-name"
     data-tekton-panel-for="Tab Name"
     data-tekton-panel-component="component-name"
     data-tekton-panel-active="true|false">
```

### 5. Interactive Element Tags
For buttons and actions:

```html
<button data-tekton-action="action-name"
        data-tekton-action-type="primary|secondary">
```

### 6. Loading State Tags
For component loading states (automatically managed by MinimalLoader):

```html
<div id="html-panel" 
     data-tekton-loading-state="pending|loading|loaded|error"
     data-tekton-loading-component="component-name"
     data-tekton-loading-started="timestamp"
     data-tekton-loading-error="error message">
```

### 7. Component State Tags
For exposing runtime component states:

```html
<div class="rhetor" 
     data-tekton-area="rhetor"
     data-tekton-state-loaded="true"
     data-tekton-state-active="true"
     data-tekton-state-mode="chat"
     data-tekton-state-model="claude-3">
```

### 8. AI Integration Tags (Advanced)
For AI-aware components:

```html
data-tekton-ai="ai-specialist-name"
data-tekton-ai-ready="true|false"
```

## Implementation Examples

### Complete Component Example (Profile)

```html
<div class="profile"
     data-tekton-area="profile"
     data-tekton-component="profile"
     data-tekton-type="component-workspace"
     data-tekton-description="User profile and preferences management">
    
    <!-- Header Zone -->
    <div class="profile__header" data-tekton-zone="header">
        <h2 data-tekton-element="title">Profile</h2>
    </div>
    
    <!-- Navigation Menu -->
    <div class="profile__menu-bar" data-tekton-zone="menu" data-tekton-nav="component-menu">
        <div class="profile__tab profile__tab--active"
             data-tekton-menu-item="Personal Information"
             data-tekton-menu-component="profile"
             data-tekton-menu-active="true"
             data-tekton-menu-panel="personal-panel">
            Personal Information
        </div>
        <div class="profile__tab"
             data-tekton-menu-item="AI Preferences"
             data-tekton-menu-component="profile"
             data-tekton-menu-active="false"
             data-tekton-menu-panel="ai-panel">
            AI Preferences
        </div>
    </div>
    
    <!-- Content Area -->
    <div class="profile__content" data-tekton-zone="content">
        <!-- Active Panel -->
        <div id="personal-panel"
             class="profile__panel profile__panel--active"
             data-tekton-panel="personal"
             data-tekton-panel-for="Personal Information"
             data-tekton-panel-component="profile"
             data-tekton-panel-active="true">
            
            <!-- Form fields -->
            <input type="text" data-tekton-field="username">
            
            <!-- Actions -->
            <button data-tekton-action="save-profile"
                    data-tekton-action-type="primary">
                Save Changes
            </button>
        </div>
        
        <!-- Inactive Panel -->
        <div id="ai-panel"
             class="profile__panel"
             data-tekton-panel="ai"
             data-tekton-panel-for="AI Preferences"
             data-tekton-panel-component="profile"
             data-tekton-panel-active="false">
            <!-- AI settings content -->
        </div>
    </div>
</div>
```

### Loading State Example

```html
<!-- During component load -->
<div id="html-panel" 
     data-tekton-loading-state="loading"
     data-tekton-loading-component="athena"
     data-tekton-loading-started="1750456131623">
  <div>Loading athena...</div>
</div>

<!-- After successful load -->
<div id="html-panel" 
     data-tekton-loading-state="loaded"
     data-tekton-loading-component="athena">
  <!-- Athena component content -->
</div>
```

## Current Implementation Status

### Summary (as of 2025-06-21)
- **Total Components**: 23
- **Fully Instrumented**: 2 (8.7%) - rhetor, profile
- **Partially Instrumented**: 11 (47.8%) - have root tags, need zones
- **Not Instrumented**: 10 (43.5%) - need complete instrumentation

### ✅ Fully Instrumented Components
| Component | Tags | Notes |
|-----------|------|-------|
| rhetor | 31 | Gold standard example, includes AI integration |
| profile | 43 | Comprehensive instrumentation with all patterns |

### ⚠️ Partially Instrumented Components
Need zone tags added:
- apollo, athena, budget, engram, ergon, harmonia
- metis, prometheus, sophia, synthesis, telos

All have root-level `data-tekton-area` and `data-tekton-component` tags.

### ❌ Not Instrumented Components
Need full instrumentation:
- codex, hermes, settings, terma, test, tekton
- tekton-dashboard, github-panel, telos-chat-tab, component-template

## Testing and Verification

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

### 2. DevTools Verification

```python
# Check semantic coverage
result = await devtools_request("ui_semantic_scan", {})

# Analyze specific component
result = await devtools_request("ui_semantic_analysis", {"component": "profile"})

# Capture with loading state detection
result = await devtools_request("ui_capture", {"area": "hephaestus"})
# Check result["loading_states"] for component status
```

### 3. Validation Requirements

Each component should have:
- [ ] Root element with area, component, type, and description
- [ ] At least 2 zones (header and content minimum)
- [ ] Menu items with proper navigation tags
- [ ] Panels with active/inactive states
- [ ] Actions with proper identification
- [ ] Loading states managed by MinimalLoader

## Implementation Guide

### Step 1: Assess Current State

```bash
# Run semantic scan
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -d '{"tool_name":"ui_semantic_scan","arguments":{}}'
```

### Step 2: Add Root Tags

```html
<!-- Start with the component container -->
<div class="component-name"
     data-tekton-area="component-name"
     data-tekton-component="component-name"
     data-tekton-type="component-workspace"
     data-tekton-description="What this component does">
```

### Step 3: Add Zone Tags

Map BEM-style classes to zones:
- `.component__header` → `data-tekton-zone="header"`
- `.component__menu` → `data-tekton-zone="menu"`
- `.component__content` → `data-tekton-zone="content"`
- `.component__footer` → `data-tekton-zone="footer"`

### Step 4: Add Navigation Tags

For components with tabs:
1. Mark the menu container with `data-tekton-nav="component-menu"`
2. Tag each tab with menu item attributes
3. Link tabs to panels with `data-tekton-menu-panel`

### Step 5: Add Panel Tags

For each content panel:
1. Add panel identification tags
2. Mark active/inactive states
3. Link back to menu items with `data-tekton-panel-for`

### Step 6: Tag Interactive Elements

```html
<button data-tekton-action="action-name"
        data-tekton-action-type="primary">
```

### Step 7: Verify Implementation

```bash
# Test the instrumentation
python3 tools/test_instrumentation.py component-name
```

## Future Work and Roadmap

### Phase 1: Complete UI Instrumentation (Current)
- [ ] Finish instrumenting all 23 UI components
- [ ] Implement automated validation tests
- [ ] Create component registry from semantic tags

### Phase 2: Navigation Reliability
- [ ] Ensure 100% reliable component loading
- [ ] Fix terminal panel vs HTML panel switching
- [ ] Add component load verification events

### Phase 3: Codebase Instrumentation
- [ ] Add AI-readable headers to all Python/JS files
- [ ] Instrument functions with action metadata
- [ ] Add configuration instrumentation
- [ ] Implement test instrumentation

### Phase 4: Advanced Features
- [ ] Performance metric tags
- [ ] Error tracking instrumentation
- [ ] Dynamic state exposure
- [ ] AI behavior hints

## Best Practices

### DO:
- Use descriptive, meaningful tag values
- Keep tag names consistent across components
- Update state tags dynamically as component state changes
- Document any new tag patterns you create
- Test instrumentation with DevTools

### DON'T:
- Create overly complex tag hierarchies
- Duplicate information unnecessarily
- Forget to update inactive states
- Mix presentation classes with semantic tags
- Add tags without documenting them

## Quick Reference

### Minimum Required Tags
```html
data-tekton-area="component-name"
data-tekton-component="component-name"
data-tekton-zone="header|menu|content|footer"
```

### Navigation Pattern
```html
<!-- Menu -->
<div data-tekton-nav="component-menu">
  <div data-tekton-menu-item="Tab Name"
       data-tekton-menu-active="true"
       data-tekton-menu-panel="panel-id">
</div>

<!-- Panel -->
<div id="panel-id"
     data-tekton-panel="panel-name"
     data-tekton-panel-for="Tab Name"
     data-tekton-panel-active="true">
```

### Loading States (Automatic)
```html
data-tekton-loading-state="pending|loading|loaded|error"
data-tekton-loading-component="component-name"
```

## Conclusion

The semantic instrumentation system is the foundation for making Tekton fully AI/CI-friendly. By following these patterns and completing the instrumentation of all components, we enable any AI or CI to understand, navigate, and modify the entire platform effectively. The loading state system ensures reliable component detection, while the semantic tags provide the context needed for intelligent interaction.

Remember Casey's vision: Simple is better, no frameworks, and every element should be discoverable by AI. This instrumentation system achieves those goals while maintaining clean, maintainable code.