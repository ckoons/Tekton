# Component Consistency Guide

*Created: 2025-07-04 by Kari (Claude)*  
*Purpose: Define consistency rules for all Tekton UI components*

## Overview

This guide defines the standards that ALL Tekton components must follow to ensure a consistent, maintainable, and reliable user interface. These rules support the "Browser adds 71 tags" philosophy and CSS-first architecture.

## Core Consistency Rules

### 1. CSS-First Navigation (MANDATORY)

**Rule**: All component navigation MUST use the radio button pattern, not JavaScript onclick handlers.

**✅ Correct Pattern**:
```html
<!-- Hidden radio buttons -->
<input type="radio" name="component-tab" id="tab-dashboard" checked style="display: none;">
<input type="radio" name="component-tab" id="tab-settings" style="display: none;">

<!-- Labels for navigation -->
<label for="tab-dashboard" class="component__tab" data-tab="dashboard">
  <span class="component__tab-label">Dashboard</span>
</label>
```

**❌ Forbidden Pattern**:
```html
<!-- NO JavaScript onclick handlers allowed -->
<div class="component__tab" onclick="component_switchTab('dashboard')">
  <span class="component__tab-label">Dashboard</span>
</div>
```

**CSS for state management**:
```css
/* Hide all panels by default */
.component__panel { display: none; }

/* Show panel when radio is checked */
#tab-dashboard:checked ~ .component__content #dashboard-panel {
  display: block;
}

/* Style active tab */
#tab-dashboard:checked ~ .component__menu-bar label[for="tab-dashboard"] {
  background-color: var(--bg-hover);
}
```

### 2. Required Semantic Tags (MANDATORY)

**Every component MUST include these core tags**:

```html
<div class="component-name" 
     data-tekton-component="componentName"
     data-tekton-area="componentName"
     data-tekton-type="component-workspace"
     data-tekton-ai="component-ai"
     data-tekton-ai-ready="false">
```

**Navigation areas MUST be tagged**:
```html
<div data-tekton-zone="menu" data-tekton-nav="component-menu">
  <label data-tekton-menu-item="Dashboard"
         data-tekton-menu-component="componentName"
         data-tekton-menu-panel="dashboard-panel">
```

**Content panels MUST be tagged**:
```html
<div data-tekton-panel="dashboard"
     data-tekton-panel-for="Dashboard"
     data-tekton-panel-component="componentName">
```

### 3. Chat Interface Consistency (MANDATORY)

**Every component MUST include both chat types**:

1. **Specialist Chat** - Connected to component's AI
2. **Team Chat** - Shared across all components

**Specialist Chat structure**:
```html
<!-- Radio button -->
<input type="radio" name="component-tab" id="tab-specialist" style="display: none;">

<!-- Navigation label -->
<label for="tab-specialist" class="component__tab" data-tab="specialist">
  <span class="component__tab-label">[Component] Chat</span>
</label>

<!-- Chat panel -->
<div id="specialist-panel" class="component__panel"
     data-tekton-panel="specialist"
     data-tekton-panel-for="[Component] Chat">
  <div class="component__chat-container">
    <div class="component__chat-messages" id="specialist-chat-messages"></div>
    <input class="component__chat-input" 
           data-tekton-chat-input="specialist"
           data-tekton-ai="component-ai"
           placeholder="Ask [Component] AI...">
  </div>
</div>
```

**Team Chat structure**:
```html
<!-- Radio button -->
<input type="radio" name="component-tab" id="tab-teamchat" style="display: none;">

<!-- Navigation label -->
<label for="tab-teamchat" class="component__tab" data-tab="teamchat">
  <span class="component__tab-label">Team Chat</span>
</label>

<!-- Team chat panel (shared implementation) -->
<div id="teamchat-panel" class="component__panel"
     data-tekton-panel="teamchat"
     data-tekton-panel-for="Team Chat">
  <!-- Shared team chat content included here -->
</div>
```

### 4. Component Structure Standards (MANDATORY)

**Every component MUST follow this structure**:

```html
<div class="component-name" data-tekton-component="componentName">
  <!-- Header -->
  <div class="component__header" data-tekton-zone="header">
    <div class="component__title-container">
      <img src="/images/hexagon.jpg" alt="Tekton" class="component__icon">
      <h2 class="component__title">
        <span class="component__title-main">Component Name</span>
        <span class="component__title-sub">Purpose/Description</span>
      </h2>
    </div>
  </div>
  
  <!-- Menu Bar -->
  <div class="component__menu-bar" data-tekton-zone="menu" data-tekton-nav="component-menu">
    <div class="component__tabs">
      <!-- Tabs here -->
    </div>
    <div class="component__actions">
      <!-- Action buttons here -->
    </div>
  </div>
  
  <!-- Content Area -->
  <div class="component__content" data-tekton-zone="content" data-tekton-scrollable="true">
    <!-- Panels here -->
  </div>
</div>
```

### 5. CSS Class Naming Standards (MANDATORY)

**Use BEM (Block Element Modifier) pattern consistently**:

- **Block**: `.component` (e.g., `.rhetor`, `.apollo`)
- **Element**: `.component__element` (e.g., `.rhetor__header`, `.apollo__tab`)  
- **Modifier**: `.component__element--modifier` (e.g., `.rhetor__tab--active`)

**Examples**:
```css
/* Block */
.rhetor { }

/* Elements */
.rhetor__header { }
.rhetor__menu-bar { }
.rhetor__tab { }
.rhetor__panel { }

/* Modifiers (avoid for CSS-first, use :checked instead) */
.rhetor__tab--disabled { }  /* Only for non-navigation states */
```

### 6. Color and Theme Consistency (MANDATORY)

**Use CSS custom properties (variables) exclusively**:

```css
/* Use these variables, never hardcoded colors */
:root {
  --bg-primary: #1a1a1a;
  --bg-secondary: #2d2d2d;
  --bg-hover: #3d3d3d;
  --text-primary: #ffffff;
  --text-secondary: #cccccc;
  --text-muted: #888888;
  --accent-primary: #007acc;
  --accent-secondary: #005a9e;
  --border-color: #444444;
  --success-color: #28a745;
  --warning-color: #ffc107;
  --error-color: #dc3545;
}
```

### 7. Accessibility Standards (MANDATORY)

**All components MUST be accessible**:

1. **Semantic HTML**: Use proper heading hierarchy (h1 → h2 → h3)
2. **Keyboard Navigation**: Tab key must work through all interactive elements
3. **Focus Management**: Visible focus indicators required
4. **Screen Reader Support**: Proper ARIA labels where needed

```html
<!-- Proper heading hierarchy -->
<h2 class="component__title-main">Component Name</h2>
<h3 class="component__section-title">Section Title</h3>

<!-- Keyboard accessible tabs -->
<label for="tab-dashboard" class="component__tab" tabindex="0">
  Dashboard
</label>

<!-- ARIA labels for complex elements -->
<div role="tabpanel" aria-labelledby="tab-dashboard" id="dashboard-panel">
```

## Browser Enrichment Compatibility

### Design for Browser Additions

**Remember**: Browser adds 71+ dynamic tags to components. Design semantic tags to work WITH this enrichment.

**✅ Good - Complementary semantic tags**:
```html
<div data-tekton-component="rhetor" 
     data-tekton-ai-ready="false"
     data-tekton-state="active">
<!-- Browser will add additional tags like:
     data-loading-state="initialized"
     data-nav-context="component-menu"
     aria-label="Rhetor Component" -->
```

**❌ Bad - Fighting browser behavior**:
```html
<div data-no-framework="true" 
     data-static-only="true"
     data-prevent-enrichment="true">
<!-- This fights against browser behavior -->
```

### UIDevTools V2 Integration

**Use UIDevTools V2 to validate browser enrichment**:

```bash
# Verify component follows standards
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -d '{"tool_name": "browser_verifier", "arguments": {"component": "componentName"}}'
```

## Validation Checklist

Before marking a component as "consistent", verify:

### Navigation ✅
- [ ] Uses radio button pattern (no onclick handlers)
- [ ] CSS handles all state changes
- [ ] Default tab is checked
- [ ] All tabs switch correctly
- [ ] Keyboard navigation works

### Semantic Tags ✅
- [ ] `data-tekton-component` present on root
- [ ] `data-tekton-zone` tags all major areas
- [ ] `data-tekton-nav` tags navigation
- [ ] `data-tekton-panel` tags all panels
- [ ] Chat inputs have `data-tekton-chat-input`

### Chat Interfaces ✅
- [ ] Specialist Chat implemented with component AI
- [ ] Team Chat included (shared implementation)
- [ ] Both chats accessible via navigation
- [ ] Chat inputs properly tagged
- [ ] WebSocket connections configured

### CSS Standards ✅
- [ ] BEM naming convention followed
- [ ] CSS variables used (no hardcoded colors)
- [ ] No JavaScript-dependent classes
- [ ] Responsive design works
- [ ] Theme switching supported

### Accessibility ✅
- [ ] Proper heading hierarchy
- [ ] Keyboard navigation complete
- [ ] Focus indicators visible
- [ ] ARIA labels where needed
- [ ] Screen reader friendly

## Migration Process

### Step-by-Step Component Migration

1. **Analyze Current State**
   - Document current tab structure
   - Identify JavaScript dependencies
   - Note any custom features

2. **Apply Radio Button Pattern**
   - Add hidden radio buttons
   - Convert divs to labels
   - Update CSS selectors

3. **Add Semantic Tags**
   - Follow SemanticTagRegistry.md
   - Tag all major areas
   - Validate with UIDevTools V2

4. **Implement Chat Interfaces**
   - Add Specialist Chat panel
   - Include Team Chat
   - Configure WebSocket connections

5. **Update CSS**
   - Apply BEM naming
   - Use CSS variables
   - Remove JavaScript dependencies

6. **Test and Validate**
   - Run validation checklist
   - Test in multiple browsers
   - Verify UIDevTools V2 results

### Common Migration Issues

**Issue**: Radio buttons don't show panels
**Solution**: Check CSS selector specificity and DOM structure

**Issue**: Styling doesn't match original
**Solution**: Verify CSS variable usage and BEM class names

**Issue**: Chat doesn't connect
**Solution**: Check WebSocket configuration and CI endpoint

## Anti-Patterns to Avoid

### ❌ Navigation Anti-Patterns

```html
<!-- Don't use JavaScript onclick -->
<div onclick="switchTab()">Tab</div>

<!-- Don't use href="#" links -->
<a href="#" onclick="switchTab()">Tab</a>

<!-- Don't mix patterns -->
<div class="tab" onclick="showPanel()" data-tekton-tab="mixed">Tab</div>
```

### ❌ CSS Anti-Patterns

```css
/* Don't hardcode colors */
.component { background: #1a1a1a; }

/* Don't use JavaScript-dependent classes */
.component__tab.active { }
.component__panel.show { }

/* Don't fight browser behavior */
.component[data-no-framework] { }
```

### ❌ Semantic Tag Anti-Patterns

```html
<!-- Don't use inconsistent naming -->
<div data-tekton-comp="name" data-component-area="main">

<!-- Don't duplicate information -->
<div class="rhetor__panel" data-tekton-rhetor-panel="dashboard">

<!-- Don't fight browser enrichment -->
<div data-static-only="true" data-no-dynamic-tags="true">
```

## Testing Standards

### Automated Testing

Components should pass these automated tests:

1. **Semantic Tag Validation**: All required tags present
2. **Navigation Testing**: All tabs switch correctly
3. **CSS Validation**: No JavaScript dependencies
4. **Chat Integration**: Both chat types functional
5. **Accessibility Testing**: WCAG 2.1 compliance

### Manual Testing

1. **Visual Regression**: Component looks identical to original
2. **Cross-Browser**: Works in Chrome, Firefox, Safari, Edge
3. **Keyboard Navigation**: Complete keyboard accessibility
4. **Responsive Design**: Works on different screen sizes
5. **Theme Switching**: Supports light/dark themes

## Future Enhancements

### Planned Improvements

1. **Animation Support**: CSS transitions for smooth state changes
2. **Advanced Accessibility**: Enhanced screen reader support
3. **Performance Optimization**: Further CSS optimization
4. **Tool Integration**: Better UIDevTools V2 integration

### Extension Points

Components can extend beyond these standards by:
- Adding component-specific semantic tags
- Including additional accessibility features  
- Implementing component-specific animations
- Adding advanced keyboard shortcuts

All extensions must maintain compatibility with these core standards.

## References

- [Semantic Tag Registry](/MetaData/TektonDocumentation/Guides/SemanticTagRegistry.md)
- [CSS-First Architecture](/MetaData/TektonDocumentation/Architecture/CSSFirstArchitecture.md)
- [UIDevTools V2 Core Philosophy](/MetaData/TektonDocumentation/Developer_Reference/UIDevToolsV2/CorePhilosophy.md)
- [Rhetor Reference Implementation](/Hephaestus/ui/components/rhetor/rhetor-component.html)