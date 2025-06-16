# Apollo & Metis Navigation Sprint - Implementation Plan

This document provides a detailed, step-by-step implementation plan for the Apollo & Metis Navigation Sprint, focusing on adding two new navigation tabs to the Tekton LEFT PANEL while optimizing space usage.

## Phase 1: Preparation and Setup

### Task 1.1: Verify Branch and Environment
- Confirm working on `sprint/Clean_Slate_051125` branch
- Verify access to all relevant files and ensure clean working directory
- Backup current index.html as a reference

### Task 1.2: Analyze UI Component Structure
- Review existing LEFT PANEL navigation implementation in `index.html`
- Identify the exact locations for inserting new navigation tabs
- Analyze current tab spacing, padding, and height configurations
- Identify CSS classes that need modification for space optimization

### Task 1.3: Prepare Color Definitions
- Define color indicators for Apollo and Metis
  - Apollo: #FFD600 (Amber/Golden Yellow)
  - Metis: #00BFA5 (Mint/Turquoise)
- Verify these colors are visually distinct and integrate well with the UI palette
- Create CSS definitions following the pattern of existing components

## Phase 2: UI Modifications

### Task 2.1: Modify LEFT PANEL Spacing
- Update CSS for navigation tabs height (~6% reduction):
  - Adjust `.nav-item` height and padding
  - Modify `.component-nav` vertical padding
  - Ensure text remains fully visible
- Implement changes and verify spacing looks correct

### Task 2.2: Add Apollo Navigation Tab
- Add new `li.nav-item` for Apollo between Engram and Rhetor:
```html
<li class="nav-item" data-component="apollo">
    <span class="nav-label">Apollo - Attention/Prediction</span>
    <span class="status-indicator"></span>
</li>
```
- Add CSS color indicator definition:
```css
.nav-item[data-component="apollo"] .status-indicator { 
    background-color: #FFD600; /* Amber/Golden Yellow */
}
```
- Verify correct positioning and styling

### Task 2.3: Add Metis Navigation Tab
- Add new `li.nav-item` for Metis between Ergon and Harmonia:
```html
<li class="nav-item" data-component="metis">
    <span class="nav-label">Metis - Workflow</span>
    <span class="status-indicator"></span>
</li>
```
- Add CSS color indicator definition:
```css
.nav-item[data-component="metis"] .status-indicator { 
    background-color: #00BFA5; /* Mint/Turquoise */
}
```
- Verify correct positioning and styling

### Task 2.4: Create Component Placeholders
- Create minimal component placeholder files:
  - `components/apollo/apollo-component.html`
  - `components/metis/metis-component.html`
- Ensure files follow the Clean Slate component architecture pattern
- Include basic structure with component container and debug instrumentation

## Phase 3: Testing and Verification

### Task 3.1: Visual Verification
- Load the Tekton UI and visually inspect the LEFT PANEL navigation
- Verify all tabs are visible without scrolling on standard display sizes
- Confirm Apollo and Metis tabs appear in the correct positions
- Validate color indicators are displaying correctly
- Check that all tab labels are fully visible and readable

### Task 3.2: Functional Testing
- Test clicking on all navigation tabs to ensure proper functionality
- Verify that tab selection highlighting works correctly
- Test navigation to and from the new tabs
- Ensure there are no UI glitches or rendering issues
- Test at different browser window sizes to ensure responsive behavior

### Task 3.3: Cross-browser Testing
- Test in multiple browsers to ensure consistent appearance
- Verify in both light and dark themes if applicable
- Check for any spacing or alignment issues across browsers

## Phase 4: Documentation and Finalization

### Task 4.1: Update Documentation
- Create/update component documentation for Apollo and Metis
- Add entries to the component registry
- Document UI changes in relevant user and developer guides
- Update any navigation-related documentation

### Task 4.2: Code Review and Cleanup
- Review all changes for consistency and quality
- Remove any temporary code or comments
- Ensure code follows established patterns and conventions
- Verify all indentation and formatting is consistent

### Task 4.3: Prepare for Commit
- Create detailed commit message following Tekton standards
- Verify all files are ready for commit
- Double-check no unintended changes are included

## Implementation Details

### CSS Changes

Here's the specific CSS changes needed for tab height reduction:

```css
/* Original (approximate) */
.nav-item {
    padding: 12px 16px;
    height: 20px;
    /* other properties */
}

/* Modified (approximate) */
.nav-item {
    padding: 11px 16px;
    height: 18px;
    /* other properties */
}

/* Component nav padding adjustment */
.component-nav {
    padding: 8px 0;  /* Reduced from 10px 0 */
    /* other properties */
}
```

### HTML Changes

The key HTML changes involve adding two new navigation items to the existing list:

1. Apollo tab (add between Engram and Rhetor):
```html
<li class="nav-item" data-component="apollo">
    <span class="nav-label">Apollo - Attention/Prediction</span>
    <span class="status-indicator"></span>
</li>
```

2. Metis tab (add between Ergon and Harmonia):
```html
<li class="nav-item" data-component="metis">
    <span class="nav-label">Metis - Workflow</span>
    <span class="status-indicator"></span>
</li>
```

### Color Definition Changes

Add to the component color indicators section:

```css
.nav-item[data-component="apollo"] .status-indicator { 
    background-color: #FFD600; /* Amber/Golden Yellow */
}
.nav-item[data-component="metis"] .status-indicator { 
    background-color: #00BFA5; /* Mint/Turquoise */
}
```

## Testing Checklist

- [ ] All tabs visible without scrolling
- [ ] Apollo tab correctly positioned between Engram and Rhetor
- [ ] Metis tab correctly positioned between Ergon and Harmonia
- [ ] Color indicators display correctly
- [ ] Tab labels fully visible and readable
- [ ] Navigation functionality works for all tabs
- [ ] No visual glitches or rendering issues
- [ ] UI appears correct in different browsers
- [ ] UI appears correct at different window sizes
- [ ] Works correctly with both light and dark themes (if applicable)

## Rollback Plan

If issues are encountered:
1. Revert changes to index.html
2. Restore original CSS values
3. Document specific issues encountered
4. Develop alternative approach based on findings