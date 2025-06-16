# UI Styling Standards

This document defines the styling standards and conventions for Tekton UI components. It consolidates best practices for consistency, maintainability, and accessibility across all components.

## Core Principles

1. **Keep It Simple** - Implement the simplest solution that meets requirements
2. **Maintain Clarity** - Prefer clear, readable code over clever optimizations
3. **File Size Limits** - Though often exceeded in practice:
   - Hard limit: 1000 lines per file
   - Target: <500 lines per file
   - Split files that exceed 600 lines when feasible
4. **Self-Contained Components** - Each component owns its styles
5. **Minimal Dependencies** - Avoid unnecessary libraries and frameworks

## Component Color Scheme

Each Tekton component has a designated color for visual identification:

| Component    | Color Code | Color Name    | Usage                        |
|-------------|------------|---------------|------------------------------|
| Hermes      | #4285F4    | Blue          | Service registry & messaging |
| Engram      | #34A853    | Green         | Memory system               |
| Tekton Core | #FBBC05    | Yellow/Gold   | Orchestration core          |
| Athena      | #7B1FA2    | Purple        | Knowledge graph             |
| Ergon       | #0097A7    | Teal          | Agent coordination          |
| Rhetor      | #D32F2F    | Red           | LLM management              |
| Harmonia    | #F57C00    | Orange        | Workflow engine             |
| Telos       | #00796B    | Dark Teal     | Requirements management     |
| Prometheus  | #C2185B    | Pink          | Planning & tracking         |
| Terma       | #5D4037    | Brown         | Terminal interface          |
| Sophia      | #7CB342    | Light Green   | Reasoning engine            |
| Synthesis   | #3949AB    | Indigo        | Execution engine            |
| Codex       | #00ACC1    | Light Blue    | Software engineering        |
| Budget      | #8E24AA    | Deep Purple   | Token management            |
| Apollo      | #FFB300    | Amber         | Executive coordinator       |
| Metis       | #1976D2    | Dark Blue     | Task decomposition          |
| Nexus       | #388E3C    | Dark Green    | Connection management       |
| Hephaestus  | #616161    | Gray          | UI system                   |

### Color Application

Include these color variables in your CSS:

```css
:root {
  /* Component Colors */
  --color-hermes: #4285F4;
  --color-engram: #34A853;
  --color-tekton-core: #FBBC05;
  --color-athena: #7B1FA2;
  --color-ergon: #0097A7;
  --color-rhetor: #D32F2F;
  --color-harmonia: #F57C00;
  --color-telos: #00796B;
  --color-prometheus: #C2185B;
  --color-terma: #5D4037;
  --color-sophia: #7CB342;
  --color-synthesis: #3949AB;
  --color-codex: #00ACC1;
  --color-budget: #8E24AA;
  --color-apollo: #FFB300;
  --color-metis: #1976D2;
  --color-nexus: #388E3C;
  --color-hephaestus: #616161;
}
```

Use component colors for:
- Header accents and borders
- Active tab indicators
- Status indicators
- Focus states
- Selection highlights

## BEM Naming Convention

Use Block Element Modifier methodology for all CSS classes:

```css
/* Block: represents a component */
.mycomponent { }

/* Element: a part of the block */
.mycomponent__header { }
.mycomponent__content { }

/* Modifier: a variation or state */
.mycomponent--expanded { }
.mycomponent__button--primary { }
```

## CSS Variables

Define standard variables for consistency:

```css
:root {
  /* Typography */
  --font-family-mono: 'Consolas', 'Courier New', monospace;
  --font-family-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.25rem;
  --font-size-xl: 1.5rem;
  
  /* Base Colors */
  --color-primary: #4a9eff;
  --color-secondary: #6c757d;
  --color-success: #4ade80;
  --color-danger: #f87171;
  --color-warning: #fbbf24;
  --color-info: #60a5fa;
  
  /* Dark Theme Colors */
  --component-bg: #1a1a1a;
  --component-text: #e0e0e0;
  --header-bg: #2a2a2a;
  --border-color: #3a3a3a;
  --card-bg: #2a2a2a;
  
  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  
  /* Borders */
  --border-radius-sm: 4px;
  --border-radius-md: 8px;
  --border-radius-lg: 12px;
  
  /* Transitions */
  --transition-fast: 0.15s ease;
  --transition-base: 0.2s ease;
  --transition-slow: 0.3s ease;
}
```

## Component Structure

Every component follows this standard panel structure:

### 1. Header Section
- Component name and logo
- Status indicators
- Control buttons
- Consistent 64px height

### 2. Menu Bar
- Chat options (Main Chat, Help Chat)
- Consistent styling across components

### 3. Tab Navigation
- Component-specific tabs
- Active state indicators using component color
- Consistent tab behavior

### 4. Content Area
- Tab-specific content panels
- Appropriate padding and spacing
- Scrollable when needed

### 5. Chat Container
- Right-side chat panel (hidden by default)
- Managed by tekton-llm-client.js
- Consistent width (350px)

## Styling Guidelines

### Headers and Navigation
- Fixed height headers (64px)
- Consistent vertical alignment
- 16px spacing between navigation items
- Subtle hover effects
- Truncate long names with ellipsis

### Content Areas
- Minimum 16px padding
- Maximum width 1200px for readability
- Use flexbox or grid layouts
- Include loading states

### Forms and Controls
- 32px height for input elements
- Clear focus states
- Consistent spacing
- Visible validation states
- Appropriate cursor styles

### Colors and States
- Follow dark theme by default
- Use CSS variables for all colors
- Clear hover/active/focus states
- Status-specific colors (success, warning, error)

### Responsive Design
- Mobile-first approach
- Breakpoints:
  - Mobile: < 768px
  - Tablet: 768px - 1024px
  - Desktop: > 1024px
- Flexible layouts that adapt

## Environment Variables

### SHOW_GREEK_NAMES
Controls display of Greek component names:
- `true`: Shows "Athena - Knowledge"
- `false`: Shows only "Knowledge"

Implementation example:
```javascript
function createComponentHeader(greekName, functionalName) {
  const titleText = window.SHOW_GREEK_NAMES === 'true' 
    ? `${greekName} - ${functionalName}` 
    : functionalName;
  
  return `<h1>${titleText}</h1>`;
}
```

## Accessibility Requirements

1. **Color Contrast** - Minimum 4.5:1 for normal text, 3:1 for large text
2. **Keyboard Navigation** - All interactive elements keyboard accessible
3. **ARIA Labels** - Proper ARIA attributes for screen readers
4. **Focus Indicators** - Visible focus states for all interactive elements
5. **Semantic HTML** - Use proper HTML elements for their intended purpose

## Performance Guidelines

1. **Minimize Specificity** - Keep CSS selectors simple
2. **Avoid Deep Nesting** - Maximum 3 levels of nesting
3. **Use CSS Transitions** - Prefer CSS over JavaScript animations
4. **Optimize Selectors** - Avoid universal selectors and excessive descendant selectors
5. **Critical CSS** - Include essential styles inline for faster initial render

## Common Patterns

### Status Badges
```css
.mycomponent__status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.mycomponent__status-badge--healthy {
  background-color: rgba(74, 222, 128, 0.1);
  color: #4ade80;
}

.mycomponent__status-badge--error {
  background-color: rgba(248, 113, 113, 0.1);
  color: #f87171;
}
```

### Loading States
```css
.mycomponent__loading {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.mycomponent__loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-color);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

### Truncation
```css
.mycomponent__text--truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mycomponent__text--truncate-multiline {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

## Testing Your Styles

1. **Theme Testing** - Verify in both light and dark themes
2. **Browser Testing** - Chrome, Firefox, Safari, Edge
3. **Device Testing** - Mobile, tablet, desktop viewports
4. **Accessibility Testing** - Use Axe or Lighthouse
5. **Performance Testing** - Check render performance

## Best Practices Summary

1. **Use BEM consistently** - Makes styles predictable and maintainable
2. **Leverage CSS variables** - Easy theme switching and consistency
3. **Keep specificity low** - Easier to override when needed
4. **Mobile-first approach** - Build up from mobile to desktop
5. **Component isolation** - Styles shouldn't leak between components
6. **Semantic class names** - Classes describe purpose, not appearance
7. **Document edge cases** - Comment tricky CSS solutions

---

*Remember: Good styling enhances usability without drawing attention to itself. Keep it simple, consistent, and accessible.*