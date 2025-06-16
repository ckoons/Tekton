# BEM Implementation Guide for Tekton UI Components

This guide provides detailed instructions for implementing BEM (Block, Element, Modifier) naming conventions in Tekton UI components. Following these guidelines ensures consistent, maintainable CSS that prevents class name collisions without requiring Shadow DOM.

## Table of Contents

1. [BEM Naming Overview](#bem-naming-overview)
2. [Block Naming Rules](#block-naming-rules)
3. [Element Naming Rules](#element-naming-rules)
4. [Modifier Naming Rules](#modifier-naming-rules)
5. [File Organization](#file-organization)
6. [HTML Structure](#html-structure)
7. [CSS Organization](#css-organization)
8. [JavaScript Usage](#javascript-usage)
9. [Best Practices](#best-practices)
10. [Migration Guide](#migration-guide)
11. [Examples](#examples)

## BEM Naming Overview

BEM (Block, Element, Modifier) is a naming methodology that provides a clear, strict naming convention for CSS classes. In Tekton, we use BEM to create a virtual scope for styles without relying on Shadow DOM encapsulation.

### Basic Structure

```
.block__element--modifier
```

- **Block**: The standalone component name (`athena`, `ergon`, `terminal`)
- **Element**: Parts of the block, separated by double underscore (`__header`, `__button`, `__menu`)
- **Modifier**: Variants or states, separated by double hyphen (`--active`, `--disabled`, `--dark`)

## Block Naming Rules

1. **Component as Block**: Each UI component gets its own block name
   ```css
   .athena { }
   .ergon { }
   .terminal { }
   ```

2. **Block Naming**: Use kebab-case for multi-word blocks
   ```css
   .knowledge-graph { }
   .data-panel { }
   ```

3. **Block as Namespace**: Always scope elements within a block to prevent collisions
   
4. **Block Composition**: Large components may use multiple blocks for logical grouping
   ```html
   <div class="athena">
     <div class="athena__header">
       <!-- Header content -->
     </div>
     <div class="athena__content">
       <div class="knowledge-graph">
         <!-- Nested component with its own BEM structure -->
       </div>
     </div>
   </div>
   ```

## Element Naming Rules

1. **Element as Component Part**: Elements are parts of a block that have no standalone meaning
   ```css
   .athena__header { }
   .athena__menu { }
   .athena__button { }
   ```

2. **Element Naming**: Use kebab-case for multi-word elements
   ```css
   .athena__menu-item { }
   .ergon__status-indicator { }
   ```

3. **Element Nesting**: Don't reflect DOM hierarchy in class names; keep it flat
   ```css
   /* GOOD */
   .athena__menu-item { }

   /* BAD - Don't do this */
   .athena__menu__item { }
   ```

4. **Element Relationships**: Every element must be part of a block
   ```html
   <div class="athena">
     <button class="athena__button">
       <span class="athena__button-icon"></span>
       <span class="athena__button-text">Click Me</span>
     </button>
   </div>
   ```

## Modifier Naming Rules

1. **Modifier Purpose**: Represent states, variations, or behaviors
   ```css
   .athena__button--primary { }
   .athena__button--disabled { }
   .athena__panel--active { }
   ```

2. **Modifier Naming**: Use kebab-case for multi-word modifiers
   ```css
   .athena__button--extra-large { }
   .ergon__panel--read-only { }
   ```

3. **Boolean Modifiers**: When the modifier doesn't need a value
   ```css
   .athena__menu-item--active { }
   .ergon__input--disabled { }
   ```

4. **Key-Value Modifiers**: When a specific value is needed
   ```css
   .athena__theme--dark { }
   .athena__theme--light { }
   .athena__layout--compact { }
   ```

5. **Multiple Modifiers**: One element can have multiple modifiers
   ```html
   <button class="athena__button athena__button--large athena__button--primary athena__button--disabled">
     Button Text
   </button>
   ```

## File Organization

### Component File Structure

```
Hephaestus/ui/
├── components/
│   └── athena/
│       └── athena-component.html
├── styles/
│   └── athena/
│       └── athena-component.css
└── scripts/
    └── athena/
        └── athena-component.js
```

### CSS File Structure

```css
/* athena-component.css */

/* 1. Block */
.athena {
  /* Block styles */
}

/* 2. Elements */
.athena__header {
  /* Header styles */
}

.athena__content {
  /* Content styles */
}

.athena__footer {
  /* Footer styles */
}

/* 3. Element variations */
.athena__button {
  /* Button base styles */
}

.athena__menu-item {
  /* Menu item base styles */
}

/* 4. Modifiers */
.athena__button--primary {
  /* Primary button styles */
}

.athena__button--secondary {
  /* Secondary button styles */
}

.athena__menu-item--active {
  /* Active menu item styles */
}

/* 5. States */
.athena__button--disabled {
  /* Disabled button styles */
}

.athena__menu-item--hidden {
  /* Hidden menu item styles */
}

/* 6. Responsive variations */
@media (max-width: 768px) {
  .athena__header {
    /* Mobile header styles */
  }
}
```

## HTML Structure

### Basic Component Structure

```html
<div class="athena">
  <header class="athena__header">
    <h2 class="athena__title">Athena</h2>
    <nav class="athena__menu">
      <button class="athena__menu-item athena__menu-item--active">Graph</button>
      <button class="athena__menu-item">Entities</button>
      <button class="athena__menu-item">History</button>
    </nav>
  </header>
  
  <main class="athena__content">
    <div class="athena__panel athena__panel--active">
      <!-- Graph panel content -->
    </div>
    <div class="athena__panel">
      <!-- Entities panel content -->
    </div>
    <div class="athena__panel">
      <!-- History panel content -->
    </div>
  </main>
  
  <footer class="athena__footer">
    <div class="athena__input-container">
      <textarea class="athena__input"></textarea>
      <button class="athena__button athena__button--primary">Send</button>
    </div>
  </footer>
</div>
```

### Common RIGHT PANEL Structure

All components should follow the standard RIGHT PANEL structure with BEM naming:

```html
<div class="component-name">
  <!-- HEADER -->
  <header class="component-name__header">
    <h2 class="component-name__title">Component Title</h2>
    
    <!-- MENU BAR -->
    <nav class="component-name__menu">
      <button class="component-name__menu-item component-name__menu-item--active">Tab 1</button>
      <button class="component-name__menu-item">Tab 2</button>
    </nav>
  </header>
  
  <!-- WORKSPACE -->
  <main class="component-name__workspace">
    <div class="component-name__panel component-name__panel--active">
      <!-- Panel 1 content -->
    </div>
    <div class="component-name__panel">
      <!-- Panel 2 content -->
    </div>
  </main>
  
  <!-- CHAT-INPUT-AREA (Optional) -->
  <footer class="component-name__footer">
    <div class="component-name__input-container">
      <textarea class="component-name__input"></textarea>
      <button class="component-name__button component-name__button--primary">Send</button>
    </div>
  </footer>
</div>
```

## CSS Organization

### Component-Specific Variables

Define component-specific CSS variables at the block level:

```css
.athena {
  --athena-header-height: 60px;
  --athena-footer-height: 80px;
  --athena-spacing: 16px;
  --athena-border-radius: 4px;
}
```

### Element Styling

Style elements within the context of their block:

```css
.athena__header {
  height: var(--athena-header-height);
  padding: var(--athena-spacing);
  border-bottom: 1px solid var(--border-color);
}

.athena__menu {
  display: flex;
  gap: calc(var(--athena-spacing) / 2);
}

.athena__menu-item {
  padding: calc(var(--athena-spacing) / 2) var(--athena-spacing);
  border-radius: var(--athena-border-radius);
  background: transparent;
  border: none;
  cursor: pointer;
}
```

### Modifier Styling

Apply modifiers to change element appearance:

```css
.athena__menu-item--active {
  background-color: var(--bg-accent);
  color: var(--text-accent);
}

.athena__button--primary {
  background-color: var(--primary-color);
  color: white;
}

.athena__button--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

## JavaScript Usage

### Accessing Elements

Use the `$` and `$$` utility methods to access elements within a component:

```javascript
class AthenaComponent extends BaseComponent {
  constructor(id, container) {
    super(id, container);
  }
  
  initEventHandlers() {
    // Find elements using BEM selectors
    const menuItems = this.$$('.athena__menu-item');
    const panels = this.$$('.athena__panel');
    
    // Add event listeners
    menuItems.forEach((item, index) => {
      this.addEventHandler(item, 'click', () => {
        this.activateTab(index);
      });
    });
  }
  
  activateTab(index) {
    // Reset active states
    this.$$('.athena__menu-item').forEach(item => {
      item.classList.remove('athena__menu-item--active');
    });
    
    this.$$('.athena__panel').forEach(panel => {
      panel.classList.remove('athena__panel--active');
    });
    
    // Set new active states
    this.$$('.athena__menu-item')[index].classList.add('athena__menu-item--active');
    this.$$('.athena__panel')[index].classList.add('athena__panel--active');
  }
}
```

### BEM Utilities

Use the `BEMUtilities` class for programmatically working with BEM classes:

```javascript
// Import BEM utilities
import { BEMUtilities } from '../bem-utilities.js';

class AthenaComponent extends BaseComponent {
  constructor(id, container) {
    super(id, container);
    this.block = 'athena'; // Component block name
  }
  
  createButton(text, isPrimary = false, isDisabled = false) {
    // Create button element
    const button = document.createElement('button');
    
    // Apply base class
    button.classList.add(BEMUtilities.element(this.block, 'button'));
    
    // Apply modifiers conditionally
    if (isPrimary) {
      button.classList.add(BEMUtilities.modifier(
        BEMUtilities.element(this.block, 'button'), 
        'primary'
      ));
    }
    
    if (isDisabled) {
      button.classList.add(BEMUtilities.modifier(
        BEMUtilities.element(this.block, 'button'), 
        'disabled'
      ));
      button.disabled = true;
    }
    
    button.textContent = text;
    return button;
  }
}
```

## Best Practices

1. **Single Responsibility**
   - Each block should represent a single component
   - Each element should serve a single purpose
   - Each modifier should alter a single aspect

2. **Consistency**
   - Use consistent naming across all components
   - Follow the RIGHT PANEL structure for component layout
   - Use the same modifiers for similar states (e.g., `--active`, `--disabled`)

3. **Specificity**
   - Avoid using IDs for styling
   - Minimize use of !important
   - Keep selectors as flat as possible
   - Avoid targeting elements directly (e.g., use `.athena__title` instead of `.athena h2`)

4. **Documentation**
   - Comment complex selectors
   - Document component-specific variables
   - Explain non-obvious modifiers

5. **State Management**
   - Use modifiers for state representation (`--active`, `--loading`, `--error`)
   - Toggle modifiers with JavaScript, not inline styles
   - Keep state logic separated from rendering logic

6. **File Size**
   - Keep CSS files under 500 lines
   - Split components at 600+ lines
   - Hard limit of 1000 lines per file

## Migration Guide

### From Shadow DOM to BEM

1. **Identify Components**
   - Map out all existing components
   - Document their current DOM structure

2. **Create BEM Structure**
   - Define the block name (usually the component name)
   - Map elements to their BEM equivalents
   - Identify states and variations as modifiers

3. **Convert HTML**
   - Replace Shadow DOM template with direct HTML
   - Apply BEM classes to all elements

4. **Convert CSS**
   - Move styles from Shadow DOM to component CSS file
   - Convert selectors to BEM naming pattern
   - Remove :host selectors and Shadow DOM specific features

5. **Update JavaScript**
   - Replace shadowRoot references with container
   - Update query selectors to use BEM classes
   - Replace custom event dispatch with standard events

### Example Migration

#### Before (Shadow DOM)

```html
<!-- Component in HTML -->
<tekton-athena id="athena-component"></tekton-athena>

<!-- Shadow DOM template -->
<template id="athena-template">
  <style>
    :host {
      display: block;
      height: 100%;
    }
    
    .header {
      height: 60px;
      border-bottom: 1px solid var(--border-color);
    }
    
    .menu-item.active {
      background-color: var(--bg-accent);
    }
  </style>
  
  <div class="container">
    <div class="header">
      <h2>Athena</h2>
      <div class="menu">
        <button class="menu-item active">Graph</button>
        <button class="menu-item">Entities</button>
      </div>
    </div>
    <div class="content">
      <!-- Content here -->
    </div>
  </div>
</template>

<script>
  class AthenaComponent extends HTMLElement {
    constructor() {
      super();
      const shadowRoot = this.attachShadow({mode: 'open'});
      const template = document.getElementById('athena-template');
      shadowRoot.appendChild(template.content.cloneNode(true));
      
      // Initialize the component
      this.init();
    }
    
    init() {
      // Find elements in shadow DOM
      const menuItems = this.shadowRoot.querySelectorAll('.menu-item');
      
      // Add event listeners
      menuItems.forEach(item => {
        item.addEventListener('click', () => {
          // Remove active class from all menu items
          menuItems.forEach(item => item.classList.remove('active'));
          
          // Add active class to clicked item
          item.classList.add('active');
        });
      });
    }
  }
  
  customElements.define('tekton-athena', AthenaComponent);
</script>
```

#### After (BEM)

```html
<!-- Component in HTML -->
<div id="athena-container"></div>

<!-- Component HTML Template (in separate file) -->
<div class="athena">
  <header class="athena__header">
    <h2 class="athena__title">Athena</h2>
    <nav class="athena__menu">
      <button class="athena__menu-item athena__menu-item--active">Graph</button>
      <button class="athena__menu-item">Entities</button>
    </nav>
  </header>
  <main class="athena__content">
    <!-- Content here -->
  </main>
</div>

<!-- Component CSS (in separate file) -->
<style>
  .athena {
    display: block;
    height: 100%;
  }
  
  .athena__header {
    height: 60px;
    border-bottom: 1px solid var(--border-color);
  }
  
  .athena__menu-item--active {
    background-color: var(--bg-accent);
  }
</style>

<!-- Component JavaScript (in separate file) -->
<script>
  class AthenaComponent extends BaseComponent {
    constructor(id, container) {
      super(id, container);
    }
    
    initEventHandlers() {
      // Find elements using BEM selectors
      const menuItems = this.$$('.athena__menu-item');
      
      // Add event listeners
      menuItems.forEach(item => {
        this.addEventHandler(item, 'click', () => {
          // Remove active modifier from all menu items
          menuItems.forEach(item => item.classList.remove('athena__menu-item--active'));
          
          // Add active modifier to clicked item
          item.classList.add('athena__menu-item--active');
        });
      });
    }
  }
  
  // Initialize component
  const athenaContainer = document.getElementById('athena-container');
  const athenaComponent = new AthenaComponent('athena', athenaContainer);
  athenaComponent.init();
</script>
```

## Examples

### Athena Component

```html
<div class="athena">
  <header class="athena__header">
    <h2 class="athena__title">Knowledge Graph</h2>
    <nav class="athena__menu">
      <button class="athena__menu-item athena__menu-item--active">Graph</button>
      <button class="athena__menu-item">Entities</button>
      <button class="athena__menu-item">History</button>
    </nav>
  </header>
  
  <main class="athena__content">
    <div class="athena__panel athena__panel--active">
      <div class="athena__graph-container">
        <!-- Graph visualization -->
      </div>
    </div>
    <div class="athena__panel">
      <div class="athena__entity-list">
        <!-- Entity list -->
      </div>
    </div>
    <div class="athena__panel">
      <div class="athena__history-list">
        <!-- History list -->
      </div>
    </div>
  </main>
  
  <footer class="athena__footer">
    <div class="athena__input-container">
      <textarea class="athena__input" placeholder="Ask about the knowledge graph..."></textarea>
      <button class="athena__button athena__button--primary">Send</button>
    </div>
  </footer>
</div>
```

### Ergon Component

```html
<div class="ergon">
  <header class="ergon__header">
    <h2 class="ergon__title">Agent Management</h2>
    <nav class="ergon__menu">
      <button class="ergon__menu-item ergon__menu-item--active">Agents</button>
      <button class="ergon__menu-item">Executions</button>
      <button class="ergon__menu-item">Workflows</button>
    </nav>
  </header>
  
  <main class="ergon__content">
    <div class="ergon__panel ergon__panel--active">
      <div class="ergon__toolbar">
        <button class="ergon__button ergon__button--primary">New Agent</button>
        <div class="ergon__search">
          <input type="text" class="ergon__search-input" placeholder="Search agents...">
        </div>
      </div>
      
      <div class="ergon__agent-list">
        <div class="ergon__agent-item">
          <div class="ergon__agent-name">File Browser</div>
          <div class="ergon__agent-status ergon__agent-status--active">Active</div>
          <div class="ergon__agent-actions">
            <button class="ergon__action-button">Edit</button>
            <button class="ergon__action-button">Stop</button>
          </div>
        </div>
        
        <div class="ergon__agent-item">
          <div class="ergon__agent-name">Web Search</div>
          <div class="ergon__agent-status ergon__agent-status--inactive">Inactive</div>
          <div class="ergon__agent-actions">
            <button class="ergon__action-button">Edit</button>
            <button class="ergon__action-button">Start</button>
          </div>
        </div>
      </div>
    </div>
    
    <div class="ergon__panel">
      <!-- Executions panel content -->
    </div>
    
    <div class="ergon__panel">
      <!-- Workflows panel content -->
    </div>
  </main>
</div>
```

These examples demonstrate how BEM naming conventions, combined with the standard RIGHT PANEL structure, create consistent, maintainable component templates that don't require Shadow DOM for CSS isolation.