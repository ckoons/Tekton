# BEM Naming Conventions

**Last Updated:** May 10, 2025

## Overview

This document defines the Block-Element-Modifier (BEM) naming conventions used in the Hephaestus UI framework. These conventions ensure consistency, maintainability, and proper CSS isolation between components.

## Table of Contents

1. [BEM Methodology](#bem-methodology)
2. [Naming Structure](#naming-structure)
3. [Component Prefixing](#component-prefixing)
4. [Common CSS Patterns](#common-css-patterns)
5. [CSS Variables](#css-variables)
6. [Example Implementations](#example-implementations)
7. [Implementation Checklist](#implementation-checklist)
8. [Migration Guide](#migration-guide)

## BEM Methodology

The BEM methodology divides the UI into independent blocks, helping to create reusable components while maintaining a clean, modular codebase. It uses a naming convention that makes CSS selectors more specific without relying on nesting.

### Key Concepts

- **Block**: A standalone entity that is meaningful on its own (e.g., `header`, `container`, `menu`)
- **Element**: A part of a block that has no standalone meaning (e.g., `menu__item`, `header__title`)
- **Modifier**: A flag on a block or element that changes appearance or behavior (e.g., `menu--hidden`, `button--primary`)

## Naming Structure

The Hephaestus framework extends BEM with component prefixes:

```
{componentId}-{block}__{element}--{modifier}
```

Where:
- **componentId**: The component identifier (e.g., `rhetor`, `budget`)
- **block**: The main component or standalone entity
- **element**: A part of the block (prefixed with `__`)
- **modifier**: A variation or state of the block or element (prefixed with `--`)

### Examples

```css
/* Block: A container in the Rhetor component */
.rhetor-container { }

/* Element: Header inside the container */
.rhetor-container__header { }

/* Element: Content area inside the container */
.rhetor-container__content { }

/* Modifier: Expanded state of the container */
.rhetor-container--expanded { }

/* Element with modifier: Active state of a tab */
.rhetor-tabs__tab--active { }
```

## Component Prefixing

Component prefixing is crucial for Shadow DOM isolation to prevent class name collisions.

### Component-Specific Prefixes

Each component must use its assigned ID from the component registry as a prefix for all CSS classes:

- `tekton-`: Core UI elements
- `rhetor-`: Context/prompt components
- `budget-`: Budget management components
- `settings-`: Application settings components
- `profile-`: User profile components
- `terma-`: Terminal components
- `prometheus-`: Planning components
- `telos-`: Requirements components
- `ergon-`: Agent components
- `athena-`: Knowledge components
- `sophia-`: Learning components
- `engram-`: Memory components
- `hermes-`: Messaging components
- `codex-`: Coding components

### Shared UI Elements

For truly shared components that are used across the application, use a `tekton-` prefix:

```css
/* Shared button styles */
.tekton-button { }
.tekton-button--primary { }
.tekton-button--secondary { }

/* Shared form elements */
.tekton-input { }
.tekton-select { }
.tekton-checkbox { }
```

## Common CSS Patterns

### Layout Elements

```css
.{componentId}-layout
.{componentId}-layout__header
.{componentId}-layout__body
.{componentId}-layout__footer
.{componentId}-layout__sidebar
```

### Container Elements

```css
.{componentId}-container
.{componentId}-section
.{componentId}-panel
.{componentId}-card
.{componentId}-box
```

### Navigation Elements

```css
.{componentId}-nav
.{componentId}-nav__item
.{componentId}-nav__link
.{componentId}-tabs
.{componentId}-tabs__item
.{componentId}-tabs__content
```

### Form Elements

```css
.{componentId}-form
.{componentId}-form__group
.{componentId}-form__label
.{componentId}-form__input
.{componentId}-form__select
.{componentId}-form__textarea
.{componentId}-form__button
```

### Button Elements

```css
.{componentId}-button
.{componentId}-button--primary
.{componentId}-button--secondary
.{componentId}-button--small
.{componentId}-button--large
```

### State Modifiers

```css
.{componentId}-{block}--active
.{componentId}-{block}--disabled
.{componentId}-{block}--loading
.{componentId}-{block}--error
.{componentId}-{block}--success
```

## CSS Variables

### Global Variables

Global CSS variables should be defined at the `:root` level with a `--tekton-` prefix:

```css
:root {
  /* Colors */
  --tekton-color-primary: #007bff;
  --tekton-color-secondary: #6c757d;
  --tekton-color-success: #28a745;
  --tekton-color-danger: #dc3545;
  --tekton-color-warning: #ffc107;
  --tekton-color-info: #17a2b8;
  
  /* Typography */
  --tekton-font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --tekton-font-size-base: 1rem;
  --tekton-font-size-sm: 0.875rem;
  --tekton-font-size-lg: 1.125rem;
  --tekton-font-weight-normal: 400;
  --tekton-font-weight-bold: 700;
  
  /* Spacing */
  --tekton-spacing-xs: 0.25rem;
  --tekton-spacing-sm: 0.5rem;
  --tekton-spacing-md: 1rem;
  --tekton-spacing-lg: 1.5rem;
  --tekton-spacing-xl: 2rem;
  
  /* Borders */
  --tekton-border-radius-sm: 0.25rem;
  --tekton-border-radius-md: 0.375rem;
  --tekton-border-radius-lg: 0.5rem;
  --tekton-border-width: 1px;
  --tekton-border-color: #dee2e6;
  
  /* Effects */
  --tekton-shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --tekton-shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --tekton-shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  
  /* Animations */
  --tekton-transition-fast: 0.15s ease-in-out;
  --tekton-transition-normal: 0.3s ease-in-out;
  --tekton-transition-slow: 0.5s ease-in-out;
  
  /* Z-index layers */
  --tekton-z-index-base: 1;
  --tekton-z-index-dropdown: 1000;
  --tekton-z-index-sticky: 1020;
  --tekton-z-index-modal: 1040;
  --tekton-z-index-tooltip: 1070;
}
```

### Theme Variables

Theme-specific variables should use theme prefixes:

```css
/* Light theme variables */
[data-theme="light"] {
  --tekton-bg-primary: #ffffff;
  --tekton-bg-secondary: #f8f9fa;
  --tekton-bg-tertiary: #e9ecef;
  --tekton-text-primary: #212529;
  --tekton-text-secondary: #6c757d;
  --tekton-text-muted: #adb5bd;
}

/* Dark theme variables */
[data-theme="dark"] {
  --tekton-bg-primary: #1e1e1e;
  --tekton-bg-secondary: #252525;
  --tekton-bg-tertiary: #333333;
  --tekton-text-primary: #f8f9fa;
  --tekton-text-secondary: #adb5bd;
  --tekton-text-muted: #6c757d;
}
```

### Component-Specific Variables

Component-specific variables should use the component ID as a prefix:

```css
/* Rhetor component variables */
:host {
  --rhetor-container-padding: var(--tekton-spacing-md, 1rem);
  --rhetor-header-height: 60px;
  --rhetor-tab-height: 48px;
  --rhetor-code-font: 'Fira Code', monospace;
}
```

## Example Implementations

### Rhetor Component

```css
/* Container */
.rhetor-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: var(--tekton-bg-primary);
  color: var(--tekton-text-primary);
  padding: var(--rhetor-container-padding);
}

/* Header */
.rhetor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--rhetor-header-height);
  border-bottom: var(--tekton-border-width) solid var(--tekton-border-color);
  margin-bottom: var(--tekton-spacing-md);
}

.rhetor-header__title {
  font-size: var(--tekton-font-size-lg);
  font-weight: var(--tekton-font-weight-bold);
  margin: 0;
}

.rhetor-header__actions {
  display: flex;
  gap: var(--tekton-spacing-sm);
}

/* Tabs */
.rhetor-tabs {
  display: flex;
  border-bottom: var(--tekton-border-width) solid var(--tekton-border-color);
}

.rhetor-tabs__tab {
  padding: var(--tekton-spacing-sm) var(--tekton-spacing-md);
  cursor: pointer;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  color: var(--tekton-text-secondary);
  transition: color var(--tekton-transition-fast),
              border-color var(--tekton-transition-fast);
}

.rhetor-tabs__tab--active {
  border-bottom-color: var(--tekton-color-primary);
  color: var(--tekton-text-primary);
}

/* Content */
.rhetor-content {
  flex: 1;
  overflow: auto;
}

.rhetor-content__panel {
  display: none;
  padding: var(--tekton-spacing-md);
}

.rhetor-content__panel--active {
  display: block;
}

/* Form Elements */
.rhetor-form {
  display: flex;
  flex-direction: column;
  gap: var(--tekton-spacing-md);
}

.rhetor-form__group {
  display: flex;
  flex-direction: column;
  gap: var(--tekton-spacing-xs);
}

.rhetor-form__label {
  font-weight: var(--tekton-font-weight-bold);
  font-size: var(--tekton-font-size-sm);
  color: var(--tekton-text-secondary);
}

.rhetor-form__input {
  padding: var(--tekton-spacing-sm);
  border: var(--tekton-border-width) solid var(--tekton-border-color);
  border-radius: var(--tekton-border-radius-sm);
  background-color: var(--tekton-bg-secondary);
  color: var(--tekton-text-primary);
}

/* Buttons */
.rhetor-button {
  padding: var(--tekton-spacing-sm) var(--tekton-spacing-md);
  border-radius: var(--tekton-border-radius-sm);
  border: var(--tekton-border-width) solid var(--tekton-border-color);
  background-color: var(--tekton-bg-tertiary);
  color: var(--tekton-text-primary);
  cursor: pointer;
  transition: background-color var(--tekton-transition-fast),
              color var(--tekton-transition-fast);
}

.rhetor-button--primary {
  background-color: var(--tekton-color-primary);
  border-color: var(--tekton-color-primary);
  color: white;
}

.rhetor-button:hover {
  opacity: 0.9;
}

.rhetor-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

### Terma Component

```css
/* Terminal Container */
.terma-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: var(--tekton-bg-primary);
  color: var(--tekton-text-primary);
  font-family: 'Fira Code', monospace;
}

/* Terminal Header */
.terma-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--tekton-spacing-sm) var(--tekton-spacing-md);
  background-color: var(--tekton-bg-secondary);
  border-bottom: var(--tekton-border-width) solid var(--tekton-border-color);
}

.terma-header__title {
  font-size: var(--tekton-font-size-sm);
  font-weight: var(--tekton-font-weight-bold);
  margin: 0;
}

.terma-header__controls {
  display: flex;
  gap: var(--tekton-spacing-sm);
}

/* Terminal Content */
.terma-content {
  flex: 1;
  overflow: auto;
  padding: var(--tekton-spacing-md);
  background-color: var(--terma-bg-color, #1a1a1a);
  color: var(--terma-text-color, #f0f0f0);
}

.terma-content__output {
  white-space: pre-wrap;
  font-size: var(--terma-font-size, 14px);
  line-height: 1.6;
}

/* Terminal Input */
.terma-input {
  display: flex;
  padding: var(--tekton-spacing-sm);
  background-color: var(--terma-input-bg, #2a2a2a);
  border-top: var(--tekton-border-width) solid var(--tekton-border-color);
}

.terma-input__prompt {
  color: var(--terma-prompt-color, #4caf50);
  margin-right: var(--tekton-spacing-sm);
}

.terma-input__field {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--terma-text-color, #f0f0f0);
  font-family: inherit;
  font-size: inherit;
}

.terma-input__field:focus {
  outline: none;
}

/* Status Indicator */
.terma-status {
  display: flex;
  align-items: center;
  font-size: var(--tekton-font-size-sm);
  padding: var(--tekton-spacing-xs) var(--tekton-spacing-md);
  background-color: var(--tekton-bg-secondary);
  border-top: var(--tekton-border-width) solid var(--tekton-border-color);
}

.terma-status__indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: var(--tekton-spacing-sm);
}

.terma-status__indicator--connected {
  background-color: var(--tekton-color-success);
}

.terma-status__indicator--disconnected {
  background-color: var(--tekton-color-danger);
}
```

## Implementation Checklist

When implementing CSS for a new component, follow this checklist:

1. **Component Prefix**:
   - [ ] Use the component ID as prefix for all class names
   - [ ] Avoid generic class names
   - [ ] Ensure all selectors use the component prefix

2. **BEM Structure**:
   - [ ] Identify blocks, elements, and modifiers
   - [ ] Use double underscore (`__`) for elements
   - [ ] Use double dash (`--`) for modifiers
   - [ ] Keep class names descriptive and meaningful

3. **CSS Variables**:
   - [ ] Use global variables with fallbacks
   - [ ] Define component-specific variables when needed
   - [ ] Ensure theme compatibility
   - [ ] Follow naming conventions for variables

4. **Responsive Design**:
   - [ ] Use relative units (rem, em, %) where appropriate
   - [ ] Implement responsive breakpoints
   - [ ] Test on different screen sizes

5. **Accessibility**:
   - [ ] Ensure sufficient color contrast
   - [ ] Implement focus states for interactive elements
   - [ ] Test with screen readers
   - [ ] Support reduced motion preferences

6. **Performance**:
   - [ ] Minimize selector specificity
   - [ ] Avoid expensive properties when possible
   - [ ] Group related styles
   - [ ] Remove unused styles

7. **Documentation**:
   - [ ] Add comments for complex selectors
   - [ ] Document component-specific variables
   - [ ] Explain any non-obvious layout techniques

## Migration Guide

When migrating existing components to use BEM naming conventions:

1. **Audit Existing Classes**:
   - List all class names currently used in the component
   - Identify how classes are used (blocks, elements, modifiers)
   - Note any shared or generic class names

2. **Create BEM Mapping**:
   - Map each existing class to its BEM equivalent
   - Add component prefix to all classes
   - Use consistent naming for similar elements across components

3. **Update HTML**:
   - Replace all class names with their BEM equivalents
   - Ensure all elements have appropriate classes
   - Remove unnecessary or redundant classes

4. **Update CSS**:
   - Rewrite selectors using BEM convention
   - Replace hardcoded values with CSS variables
   - Simplify complex selectors
   - Remove unnecessary nesting

5. **Update JavaScript**:
   - Update all DOM selectors to use new class names
   - Update any class manipulation code
   - Ensure event delegation uses correct selectors

6. **Test Thoroughly**:
   - Verify styles apply correctly
   - Test responsive behavior
   - Ensure theme changes work
   - Verify JavaScript functionality

### Example Migration

#### Before:

```html
<div class="container">
  <div class="header">
    <h2 class="title">Component Title</h2>
    <div class="actions">
      <button class="btn primary">Save</button>
    </div>
  </div>
  <div class="content">
    <div class="tab-container">
      <button class="tab active">Tab 1</button>
      <button class="tab">Tab 2</button>
    </div>
    <div class="tab-content active">Tab 1 content</div>
    <div class="tab-content">Tab 2 content</div>
  </div>
</div>
```

```css
.container {
  padding: 16px;
  background-color: #f8f9fa;
}

.header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.actions {
  display: flex;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn.primary {
  background-color: #007bff;
  color: white;
}

.tab-container {
  display: flex;
  border-bottom: 1px solid #dee2e6;
}

.tab {
  padding: 8px 16px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-bottom: 3px solid transparent;
}

.tab.active {
  border-bottom-color: #007bff;
  font-weight: bold;
}

.tab-content {
  display: none;
  padding: 16px;
}

.tab-content.active {
  display: block;
}
```

#### After:

```html
<div class="component-container">
  <div class="component-header">
    <h2 class="component-header__title">Component Title</h2>
    <div class="component-header__actions">
      <button class="component-button component-button--primary">Save</button>
    </div>
  </div>
  <div class="component-content">
    <div class="component-tabs">
      <button class="component-tabs__tab component-tabs__tab--active">Tab 1</button>
      <button class="component-tabs__tab">Tab 2</button>
    </div>
    <div class="component-tabs__content component-tabs__content--active">Tab 1 content</div>
    <div class="component-tabs__content">Tab 2 content</div>
  </div>
</div>
```

```css
.component-container {
  padding: var(--tekton-spacing-md, 16px);
  background-color: var(--tekton-bg-secondary, #f8f9fa);
}

.component-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--tekton-spacing-md, 16px);
}

.component-header__title {
  font-size: var(--tekton-font-size-lg, 18px);
  font-weight: var(--tekton-font-weight-bold, bold);
  margin: 0;
}

.component-header__actions {
  display: flex;
}

.component-button {
  padding: var(--tekton-spacing-sm, 8px) var(--tekton-spacing-md, 16px);
  border-radius: var(--tekton-border-radius-sm, 4px);
  cursor: pointer;
  border: var(--tekton-border-width, 1px) solid transparent;
}

.component-button--primary {
  background-color: var(--tekton-color-primary, #007bff);
  color: white;
}

.component-tabs {
  display: flex;
  border-bottom: var(--tekton-border-width, 1px) solid var(--tekton-border-color, #dee2e6);
}

.component-tabs__tab {
  padding: var(--tekton-spacing-sm, 8px) var(--tekton-spacing-md, 16px);
  border: none;
  background: transparent;
  cursor: pointer;
  border-bottom: 3px solid transparent;
}

.component-tabs__tab--active {
  border-bottom-color: var(--tekton-color-primary, #007bff);
  font-weight: var(--tekton-font-weight-bold, bold);
}

.component-tabs__content {
  display: none;
  padding: var(--tekton-spacing-md, 16px);
}

.component-tabs__content--active {
  display: block;
}
```

By following these BEM naming conventions, components will have consistent, maintainable CSS that works effectively within Shadow DOM isolation boundaries.

## See Also

- [Component Isolation Architecture](../Architecture/ComponentIsolationArchitecture.md) - Overall isolation architecture 
- [UI Component Communication](../Architecture/UIComponentCommunication.md) - Communication between components
- [Component Integration Patterns](../Architecture/ComponentIntegrationPatterns.md) - Standardized patterns for component integration