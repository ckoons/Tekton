# Tekton Semantic Tag Registry

*Created: 2025-07-04 by Kari (Claude)*  
*Purpose: Document all data-tekton-* patterns and the Browser Enrichment Discovery*

## Core Philosophy: "Code is Truth, Browser is Result"

### The Revolutionary Discovery

**Key Insight**: Browser ADDS 71+ dynamic tags to components, it doesn't remove them!

- **Rhetor Source**: 75 semantic tags in HTML  
- **Rhetor Browser**: 146 tags after loading (71 added by browser)  
- **Implication**: Our semantic tags work WITH browser enrichment, not against it

This discovery fundamentally changes our approach to semantic tagging. We design semantic tags to complement browser behavior, not conflict with it.

## Required Semantic Tags

Every Tekton component MUST include these core semantic tags:

### Component Identity
```html
<div class="component-name" 
     data-tekton-component="componentName"
     data-tekton-area="componentName"
     data-tekton-type="component-workspace">
```

### Navigation Structure
```html
<!-- Main navigation -->
<div data-tekton-nav="component-menu" data-tekton-zone="menu">
  
  <!-- Individual menu items -->
  <label data-tekton-menu-item="Dashboard"
         data-tekton-menu-component="componentName"
         data-tekton-menu-panel="dashboard-panel">
```

### Content Areas
```html
<!-- Content container -->
<div data-tekton-zone="content" data-tekton-scrollable="true">
  
  <!-- Individual panels -->
  <div data-tekton-panel="dashboard"
       data-tekton-panel-for="Dashboard"
       data-tekton-panel-component="componentName">
```

### Interactive Elements
```html
<!-- Buttons and actions -->
<button data-tekton-action="clear-chat"
        data-tekton-action-type="secondary">

<!-- Chat interfaces -->
<input data-tekton-chat-input="specialist"
       data-tekton-ai="component-ai">
```

## Semantic Tag Categories

### 1. Component Structure Tags

| Tag | Purpose | Example |
|-----|---------|---------|
| `data-tekton-component` | Component identifier | `rhetor`, `apollo`, `numa` |
| `data-tekton-area` | Major component area | `rhetor`, `chat-interface` |
| `data-tekton-type` | Element type classification | `component-workspace`, `shared-resource` |
| `data-tekton-zone` | Functional zones within component | `header`, `menu`, `content`, `footer` |

### 2. Navigation Tags

| Tag | Purpose | Example |
|-----|---------|---------|
| `data-tekton-nav` | Navigation type | `component-menu`, `main-nav` |
| `data-tekton-menu-item` | Menu item label | `Dashboard`, `Settings` |
| `data-tekton-menu-component` | Which component owns menu | `rhetor`, `apollo` |
| `data-tekton-menu-panel` | Target panel ID | `dashboard-panel` |
| `data-tekton-nav-target` | Navigation target | `dashboard-panel` |

### 3. Content Organization Tags

| Tag | Purpose | Example |
|-----|---------|---------|
| `data-tekton-panel` | Panel identifier | `dashboard`, `settings` |
| `data-tekton-panel-for` | Panel display name | `Dashboard`, `Settings` |
| `data-tekton-panel-component` | Panel owner | `rhetor`, `apollo` |
| `data-tekton-section` | Content sections | `header`, `metrics`, `controls` |
| `data-tekton-scrollable` | Scrollable areas | `true`, `false` |

### 4. Interactive Element Tags

| Tag | Purpose | Example |
|-----|---------|---------|
| `data-tekton-action` | Button/action type | `clear-chat`, `refresh`, `save` |
| `data-tekton-action-type` | Action category | `primary`, `secondary`, `danger` |
| `data-tekton-chat-input` | Chat input type | `specialist`, `team` |
| `data-tekton-ai` | Connected AI | `rhetor-ai`, `apollo-ai` |

### 5. State and Status Tags

| Tag | Purpose | Example |
|-----|---------|---------|
| `data-tekton-status` | Component status | `active`, `loading`, `error` |
| `data-tekton-state` | Current state | `active`, `inactive`, `disabled` |
| `data-tekton-ai-ready` | AI connection state | `true`, `false` |
| `data-tekton-menu-active` | Active menu item | `true`, `false` |

### 6. Data and Content Tags

| Tag | Purpose | Example |
|-----|---------|---------|
| `data-tekton-element` | Specific element type | `component-card`, `metric`, `status-indicator` |
| `data-tekton-grid` | Grid containers | `components`, `metrics`, `tools` |
| `data-tekton-metric` | Metric elements | `usage`, `status`, `performance` |

## Browser Enrichment Patterns

### What the Browser Adds

The browser automatically adds these types of dynamic tags:

1. **Loading States**: Tags that track component loading and initialization
2. **Navigation Context**: Additional context about navigation state
3. **Event Handlers**: Tags related to event binding and handling
4. **Accessibility**: ARIA and accessibility-related attributes
5. **Framework Integration**: Tags added by minimal-loader.js and ui-manager-core.js

### Working WITH Browser Enrichment

**DO**: Design semantic tags that complement browser additions
```html
<!-- Our semantic tag -->
<div data-tekton-component="rhetor" data-tekton-ai-ready="false">

<!-- Browser might add -->
<div data-tekton-component="rhetor" 
     data-tekton-ai-ready="false"
     data-loading-state="initialized"
     data-nav-context="active"
     aria-label="Rhetor Component">
```

**DON'T**: Fight against browser enrichment
```html
<!-- Bad: trying to prevent browser additions -->
<div data-tekton-only="true" data-no-browser-tags="true">
```

## Component-Specific Tag Patterns

### Chat Interfaces
```html
<!-- Chat container -->
<div data-tekton-area="chat" data-tekton-chat-type="specialist">
  
  <!-- Messages area -->
  <div data-tekton-element="chat-messages" data-tekton-scrollable="true">
  
  <!-- Input area -->
  <input data-tekton-chat-input="specialist" 
         data-tekton-ai="component-ai"
         data-tekton-placeholder="Ask specialist...">
```

### Dashboard Components
```html
<!-- Dashboard container -->
<div data-tekton-panel="dashboard" data-tekton-element="dashboard-container">
  
  <!-- Status grid -->
  <div data-tekton-element="component-grid" data-tekton-grid="components">
    
    <!-- Individual cards -->
    <div data-tekton-element="component-card" 
         data-tekton-component="target-component"
         data-tekton-state="active">
```

### Navigation Menus
```html
<!-- Menu container -->
<div data-tekton-nav="component-menu" data-tekton-zone="menu">
  
  <!-- Tab structure -->
  <label data-tekton-menu-item="Dashboard"
         data-tekton-menu-component="rhetor"
         data-tekton-menu-panel="dashboard-panel"
         data-tekton-nav-target="dashboard-panel">
```

## Migration Guidelines

### Adding Semantic Tags to Legacy Components

1. **Start with Core Tags**: Add component, area, type to root element
2. **Add Navigation Tags**: Tag all menu items and panels
3. **Add Zone Tags**: Mark header, menu, content, footer areas
4. **Add Element Tags**: Tag specific interactive elements
5. **Test with UIDevTools V2**: Verify both static and dynamic state

### Validation Process

Use UIDevTools V2 to validate semantic tags:

```bash
# Check source truth (what SHOULD be there)
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "code_reader", "arguments": {"component": "rhetor"}}'

# Check browser result (what IS there)
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "browser_verifier", "arguments": {"component": "rhetor"}}'

# Compare and understand differences
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "comparator", "arguments": {"component": "rhetor"}}'
```

## Anti-Patterns

### ❌ Avoid These Patterns

1. **Fighting Browser Enrichment**
   ```html
   <!-- Bad: trying to prevent browser additions -->
   <div data-no-framework="true" data-static-only="true">
   ```

2. **Inconsistent Naming**
   ```html
   <!-- Bad: inconsistent tag names -->
   <div data-tekton-comp="rhetor" data-tekton-component-name="rhetor">
   ```

3. **Redundant Information**
   ```html
   <!-- Bad: redundant with class names -->
   <div class="rhetor__panel" data-tekton-rhetor-panel="true">
   ```

### ✅ Follow These Patterns

1. **Embrace Browser Enrichment**
   ```html
   <!-- Good: semantic tags that work with browser additions -->
   <div data-tekton-component="rhetor" data-tekton-ai-ready="false">
   ```

2. **Consistent Naming Convention**
   ```html
   <!-- Good: consistent data-tekton-* pattern -->
   <div data-tekton-component="rhetor" data-tekton-area="rhetor">
   ```

3. **Semantic Meaning**
   ```html
   <!-- Good: tags provide semantic meaning beyond CSS -->
   <div class="rhetor__panel" data-tekton-panel="dashboard" data-tekton-panel-for="Dashboard">
   ```

## Future Considerations

### Planned Enhancements

1. **Auto-Validation**: Script to validate semantic tags across all components
2. **Tag Analytics**: Track which tags are most useful for debugging
3. **AI Integration**: Use semantic tags for better AI understanding of UI
4. **Accessibility**: Leverage semantic tags for improved accessibility

### Extensibility

New semantic tag categories can be added following these patterns:
- Always use `data-tekton-` prefix
- Use kebab-case for multi-word attributes
- Provide clear purpose and example usage
- Document browser enrichment interactions

## References

- [UIDevTools V2 Core Philosophy](/MetaData/TektonDocumentation/Developer_Reference/UIDevToolsV2/CorePhilosophy.md)
- [Static vs Dynamic Tags](/MetaData/TektonDocumentation/Developer_Reference/UIDevToolsV2/StaticVsDynamicTags.md)
- [Rhetor Reference Implementation](/Hephaestus/ui/components/rhetor/rhetor-component.html)
- [Component Consistency Guide](/MetaData/TektonDocumentation/Standards/ComponentConsistencyGuide.md)