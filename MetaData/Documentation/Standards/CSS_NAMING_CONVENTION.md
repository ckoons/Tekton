# Hephaestus CSS Naming Convention

## Overview

This document defines the CSS naming convention to be used across all Hephaestus UI components to ensure consistency, maintainability, and proper isolation.

## BEM Methodology

We will use a modified BEM (Block-Element-Modifier) methodology with component prefixes to ensure style isolation.

### Structure

```
{componentId}-{block}__{element}--{modifier}
```

- **componentId**: The component identifier (e.g., rhetor, budget)
- **block**: The main component or standalone entity
- **element**: A part of the block (prefixed with `__`)
- **modifier**: A variation or state of the block or element (prefixed with `--`)

### Examples

```css
/* Block: the main component container */
.rhetor-container { }

/* Element: a part of the component */
.rhetor-container__header { }
.rhetor-container__body { }

/* Element within another element */
.rhetor-container__tab-panel__header { }

/* Modifier: a variation or state */
.rhetor-container--expanded { }
.rhetor-container__header--sticky { }
```

## Component Namespacing

### Common Components

For common UI patterns that appear in multiple components, namespace with the component ID:

```css
/* Instead of generic class names */
.tab-button { } /* BAD: Generic name that can conflict */

/* Use component-specific names */
.rhetor-tab-button { } /* GOOD: Specific to Rhetor */
.budget-tab-button { } /* GOOD: Specific to Budget */
```

### Shared Components

For truly shared components that are used across the application, use a `tekton-` prefix:

```css
/* Shared UI components */
.tekton-button { }
.tekton-form-field { }
.tekton-dropdown { }
```

## CSS Variables

### Global Variables

Global CSS variables should be defined at the `:root` level with a `--tekton-` prefix:

```css
:root {
  --tekton-color-primary: #007bff;
  --tekton-color-secondary: #6c757d;
  --tekton-font-size-base: 1rem;
}
```

### Component-Specific Variables

Component-specific variables should use the component ID as a prefix:

```css
/* In rhetor-component.css */
:root {
  --rhetor-container-padding: 1rem;
  --rhetor-tab-height: 48px;
}
```

## Class Naming Conventions

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

## Component-Specific Prefixes

Each component should use its assigned ID from the component registry as a prefix for all its CSS classes:

- `tekton-`: Core UI elements
- `prometheus-`: Planning components
- `telos-`: Requirements components
- `ergon-`: Agent/tools components
- `harmonia-`: Orchestration components
- `synthesis-`: Integration components
- `athena-`: Knowledge components
- `sophia-`: Learning components
- `engram-`: Memory components
- `rhetor-`: Context components
- `hermes-`: Message components
- `codex-`: Coding components
- `terma-`: Terminal components
- `budget-`: Budget components
- `profile-`: Profile components
- `settings-`: Settings components

## Examples by Component

### Rhetor Component

```css
/* Container */
.rhetor-container { }

/* Tabs */
.rhetor-tabs { }
.rhetor-tabs__item { }
.rhetor-tabs__item--active { }
.rhetor-tabs__content { }

/* Provider Form */
.rhetor-provider-form { }
.rhetor-provider-form__select { }
.rhetor-provider-form__label { }
.rhetor-provider-form__input { }

/* Templates */
.rhetor-template-list { }
.rhetor-template-list__item { }
.rhetor-template-editor { }
.rhetor-template-editor__textarea { }
```

### Budget Component

```css
/* Container */
.budget-container { }

/* Cards */
.budget-card { }
.budget-card__header { }
.budget-card__value { }
.budget-card__progress { }
.budget-card__footer { }

/* Charts */
.budget-chart { }
.budget-chart__legend { }
.budget-chart__bar { }
.budget-chart__pie { }

/* Tables */
.budget-table { }
.budget-table__header { }
.budget-table__row { }
.budget-table__cell { }
```

## CSS File Organization

### File Structure

```
/styles
  /main.css                    # Global styles
  /themes                      # Theme variations
    /dark.css
    /light.css
  /{componentId}               # Component-specific styles
    /{componentId}-component.css
```

### Import Order

Within each component CSS file:

1. CSS Variables (component-specific)
2. Core component styles
3. Layout elements
4. UI components (forms, buttons, etc.)
5. State variations
6. Media queries for responsiveness

## Implementation Checklist

When implementing or updating component CSS:

1. [ ] Use component-specific prefixes for all classes
2. [ ] Follow BEM naming convention
3. [ ] Use CSS variables for themeable properties
4. [ ] Avoid styling by HTML tag alone
5. [ ] Include comments for complex selectors
6. [ ] Group related styles together
7. [ ] Maintain specificity as low as possible
8. [ ] Test isolation in Shadow DOM context

## Example Migration

### Old CSS:
```css
.tab-button {
  padding: 16px;
  cursor: pointer;
  border-bottom: 3px solid transparent;
}

.tab-button.active {
  border-bottom-color: blue;
}

.tab-content {
  display: none;
  padding: 20px;
}

.tab-content.active {
  display: block;
}
```

### New CSS:
```css
.rhetor-tabs__button {
  padding: var(--tekton-spacing-md, 16px);
  cursor: pointer;
  border-bottom: 3px solid transparent;
}

.rhetor-tabs__button--active {
  border-bottom-color: var(--tekton-color-primary, blue);
}

.rhetor-tabs__content {
  display: none;
  padding: var(--tekton-spacing-lg, 20px);
}

.rhetor-tabs__content--active {
  display: block;
}
```

## Additional Considerations

### Utility Classes

For common utility needs, use the tekton prefix with a utility namespace:

```css
.tekton-util-text-center { text-align: center; }
.tekton-util-mt-1 { margin-top: var(--tekton-spacing-xs); }
.tekton-util-hidden { display: none; }
```

### Transition Classes

For animation controls, use a standardized naming convention:

```css
.tekton-fade-in { animation: tekton-fade-in 0.3s ease; }
.tekton-slide-up { animation: tekton-slide-up 0.3s ease; }
```

### Theme-Specific Overrides

When implementing theme-specific overrides:

```css
/* In dark.css */
[data-theme="dark"] .rhetor-container {
  --rhetor-bg-color: var(--tekton-dark-bg);
  --rhetor-text-color: var(--tekton-dark-text);
}
```

This naming convention ensures that components remain isolated, styles are maintainable, and the codebase stays consistent as it scales.