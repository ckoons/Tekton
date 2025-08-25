# Tekton UI Styling Guide

## Overview
This guide establishes the standardized CSS variables, patterns, and best practices for the Tekton UI system. All components must follow these guidelines to ensure visual consistency and maintainability.

## Core Design Principles

### 1. Dark Theme First
Tekton uses a sophisticated dark theme with golden accents as the primary design language.

### 2. CSS Variables for Everything
Never hardcode colors. Always use CSS variables with appropriate fallbacks.

### 3. Golden Accent Philosophy
The golden accent (#FFD700) represents divine wisdom and enlightenment, used sparingly for primary actions and focus states.

## CSS Variable Standards

### Background Colors
```css
--bg-primary: #1a1a2a;      /* Main application background */
--bg-secondary: #252535;    /* Cards, panels, modals */
--bg-tertiary: #333345;     /* Elevated elements, hover states */
--bg-input: #252535;        /* Form inputs background */
--bg-hover: #333345;        /* Hover state backgrounds */
```

### Text Colors
```css
--text-primary: #f0f0f0;    /* Main text content */
--text-secondary: #a0a0a0;  /* Muted text, descriptions */
--text-tertiary: #707080;   /* Disabled text, hints */
--text-inverse: #1a1a2a;    /* Text on light backgrounds */
```

### Border Colors
```css
--border-primary: #404050;   /* Main borders */
--border-secondary: #303040; /* Subtle borders */
--border-focus: #FFD700;     /* Focus state borders */
--border-hover: #505060;     /* Hover state borders */
```

### Accent Colors
```css
--accent-primary: #FFD700;   /* Golden - primary actions, focus */
--accent-hover: #FFC700;     /* Golden hover state */
--accent-active: #FFB700;    /* Golden active/pressed state */
--accent-info: #3b80f7;      /* Information, links */
--accent-success: #28a745;   /* Success states */
--accent-warning: #fd7e14;   /* Warning states */
--accent-error: #dc3545;     /* Error states */
```

### Shadows
```css
--shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.3);
--shadow-md: 0 4px 8px rgba(0, 0, 0, 0.4);
--shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.5);
--shadow-xl: 0 12px 24px rgba(0, 0, 0, 0.6);
--shadow-glow: 0 0 20px rgba(255, 215, 0, 0.3); /* Golden glow */
```

### Transitions
```css
--transition-fast: 0.15s ease;
--transition-base: 0.3s ease;
--transition-slow: 0.5s ease;
```

## Component Patterns

### Buttons

#### Primary Button
```css
.btn-primary {
    background: var(--accent-primary);
    color: var(--text-inverse);
    border: 1px solid var(--accent-primary);
    padding: 8px 16px;
    border-radius: 4px;
    transition: all var(--transition-base);
}

.btn-primary:hover {
    background: var(--accent-hover);
    border-color: var(--accent-hover);
    box-shadow: var(--shadow-glow);
}
```

#### Secondary Button
```css
.btn-secondary {
    background: var(--bg-secondary);
    color: var(--text-primary);
    border: 1px solid var(--border-primary);
    padding: 8px 16px;
    border-radius: 4px;
    transition: all var(--transition-base);
}

.btn-secondary:hover {
    background: var(--bg-tertiary);
    border-color: var(--accent-primary);
}
```

### Form Elements

#### Text Inputs
```css
input[type="text"],
input[type="email"],
input[type="password"],
textarea,
select {
    background: var(--bg-input);
    color: var(--text-primary);
    border: 1px solid var(--border-primary);
    padding: 8px 12px;
    border-radius: 4px;
    transition: all var(--transition-base);
}

input:focus,
textarea:focus,
select:focus {
    outline: none;
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 2px rgba(255, 215, 0, 0.2);
}
```

#### Toggle Switches
```css
/* Standardized toggle: 48x24px */
.toggle {
    width: 48px;
    height: 24px;
    background: var(--bg-tertiary);
    border-radius: 24px;
    position: relative;
    transition: background var(--transition-base);
}

.toggle.active {
    background: var(--accent-primary);
}

.toggle-slider {
    width: 18px;
    height: 18px;
    background: var(--text-primary);
    border-radius: 50%;
    position: absolute;
    top: 3px;
    left: 3px;
    transition: transform var(--transition-base);
}

.toggle.active .toggle-slider {
    transform: translateX(24px);
}
```

### Cards and Panels

```css
.card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 8px;
    padding: 16px;
    box-shadow: var(--shadow-sm);
    transition: all var(--transition-base);
}

.card:hover {
    border-color: var(--accent-primary);
    box-shadow: var(--shadow-md);
}
```

### Navigation Tabs

```css
.tab {
    background: transparent;
    color: var(--text-secondary);
    padding: 12px 20px;
    border-bottom: 2px solid transparent;
    transition: all var(--transition-base);
}

.tab:hover {
    color: var(--text-primary);
    background: var(--bg-tertiary);
}

.tab.active {
    color: var(--accent-primary);
    border-bottom-color: var(--accent-primary);
}
```

### Scrollbars

```css
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-primary);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: var(--border-primary);
    border-radius: 4px;
    transition: background var(--transition-base);
}

::-webkit-scrollbar-thumb:hover {
    background: var(--accent-primary);
}
```

### Modals

```css
.modal {
    background: var(--bg-secondary);
    border: 2px solid var(--accent-primary);
    border-radius: 8px;
    box-shadow: var(--shadow-xl);
    animation: modalAppear 0.3s ease;
}

.modal-backdrop {
    background: rgba(0, 0, 0, 0.7);
}

@keyframes modalAppear {
    from {
        opacity: 0;
        transform: scale(0.95) translateY(-20px);
    }
    to {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}
```

## Status Colors Usage

### Success States
```css
.status-success {
    color: var(--accent-success);
    background: rgba(40, 167, 69, 0.1);
    border: 1px solid rgba(40, 167, 69, 0.3);
}
```

### Error States
```css
.status-error {
    color: var(--accent-error);
    background: rgba(220, 53, 69, 0.1);
    border: 1px solid rgba(220, 53, 69, 0.3);
}
```

### Warning States
```css
.status-warning {
    color: var(--accent-warning);
    background: rgba(253, 126, 20, 0.1);
    border: 1px solid rgba(253, 126, 20, 0.3);
}
```

### Info States
```css
.status-info {
    color: var(--accent-info);
    background: rgba(59, 128, 247, 0.1);
    border: 1px solid rgba(59, 128, 247, 0.3);
}
```

## Animation Guidelines

### Entrance Animations
```css
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes scaleIn {
    from {
        opacity: 0;
        transform: scale(0.95);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}
```

### Loading States
```css
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.loading-spinner {
    width: 32px;
    height: 32px;
    border: 3px solid var(--bg-tertiary);
    border-top-color: var(--accent-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}
```

## Responsive Design

### Breakpoints
```css
--breakpoint-sm: 640px;
--breakpoint-md: 768px;
--breakpoint-lg: 1024px;
--breakpoint-xl: 1280px;
```

### Media Query Usage
```css
/* Mobile First Approach */
.container {
    padding: 16px;
}

@media (min-width: 768px) {
    .container {
        padding: 24px;
    }
}

@media (min-width: 1024px) {
    .container {
        padding: 32px;
    }
}
```

## Accessibility

### Focus States
All interactive elements must have visible focus states using the golden accent:
```css
:focus-visible {
    outline: 2px solid var(--accent-primary);
    outline-offset: 2px;
}
```

### Contrast Requirements
- Text on backgrounds must maintain WCAG AA compliance (4.5:1 for normal text)
- Golden accent on dark backgrounds provides excellent contrast
- Use `var(--text-inverse)` for text on accent backgrounds

## Component-Specific Guidelines

### Greek-Themed Components
Components with Greek names should subtly incorporate classical design elements:
- Use golden accent for divine/important actions
- Maintain clean, philosophical aesthetic
- Avoid excessive ornamentation

### Chat Interfaces
- User messages: Right-aligned with subtle background
- CI messages: Left-aligned with border accent
- Thinking states: Dashed border with pulsing animation

### Terminal/Code Blocks
```css
.code-block {
    background: var(--bg-primary);
    border: 1px solid var(--border-secondary);
    font-family: 'Courier New', monospace;
    font-size: 14px;
    padding: 12px;
    border-radius: 4px;
    overflow-x: auto;
}
```

## Migration Checklist

When updating components to use these standards:

1. ✅ Replace all hardcoded colors with CSS variables
2. ✅ Add appropriate fallback values to all variables
3. ✅ Ensure focus states use golden accent
4. ✅ Standardize button styles
5. ✅ Standardize form element styles
6. ✅ Add consistent hover states
7. ✅ Implement proper transitions
8. ✅ Add loading states where appropriate
9. ✅ Ensure scrollbar styling is applied
10. ✅ Verify WCAG contrast compliance

## File Structure

```
Hephaestus/ui/
├── styles/
│   ├── core/
│   │   └── variables.css    # All CSS variables defined here
│   ├── components/           # Component-specific styles
│   └── shared/              # Shared utility styles
```

## Implementation Priority

1. **Phase 1**: Core variables and high-traffic components (Tekton, Numa, Athena)
2. **Phase 2**: Modal system and chat interfaces
3. **Phase 3**: Settings and configuration panels
4. **Phase 4**: Remaining utility components
5. **Phase 5**: Cleanup and deprecation of old variables

## Maintenance

- Review quarterly for consistency
- Update when adding new components
- Document any exceptions with justification
- Maintain backwards compatibility during transitions

---

*Last Updated: January 2025*
*Version: 1.0*
*Aligned with Modal Styling Sprint specifications*