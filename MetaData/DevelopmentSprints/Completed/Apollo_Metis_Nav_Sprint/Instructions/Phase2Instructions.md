# Apollo & Metis Navigation Sprint - Phase 2 Instructions

This document provides detailed instructions for implementing Phase 2 of the Apollo & Metis Navigation Sprint. It is intended for the Working Claude Code session that will implement these changes.

## Implementation Tasks

### Task 1: Add Apollo and Metis Navigation Tabs

1. **Add Apollo Tab**:
   - Open `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/index.html`
   - Find the Engram tab (around line 151)
   - Add the following HTML immediately after the Engram tab and before the Rhetor tab:
   ```html
   <li class="nav-item" data-component="apollo">
       <span class="nav-label" data-greek-name="Apollo - Attention/Prediction" data-functional-name="Attention/Prediction">Apollo - Attention/Prediction</span>
       <span class="status-indicator"></span>
   </li>
   ```

2. **Add Metis Tab**:
   - Find the Ergon tab (around line 131)
   - Add the following HTML immediately after the Ergon tab and before the Harmonia tab:
   ```html
   <li class="nav-item" data-component="metis">
       <span class="nav-label" data-greek-name="Metis - Workflows" data-functional-name="Workflows">Metis - Workflows</span>
       <span class="status-indicator"></span>
   </li>
   ```

3. **Add Color Indicators**:
   - Find the component color indicators section (around line 21)
   - Add the following CSS:
   ```css
   .nav-item[data-component="apollo"] .status-indicator { 
       background-color: #FFD600; /* Amber/Golden Yellow */
   }
   .nav-item[data-component="metis"] .status-indicator { 
       background-color: #00BFA5; /* Mint/Turquoise */
   }
   ```

### Task 2: Optimize Navigation Space

1. **Adjust Navigation Item Sizing**:
   - Find the CSS that affects `.nav-item` sizing
   - If using inline styles, add the following to the `<style>` section:
   ```css
   /* Optimized navigation item height */
   .nav-item {
       padding: 11px 16px !important; /* Reduced from 12px vertical padding */
       height: 18px !important; /* Reduced from 20px height */
   }
   
   /* Adjust footer navigation buttons to match main navigation */
   .footer-buttons .control-button {
       padding: 11px 16px !important; /* Match main navigation padding */
       height: 18px !important; /* Match main navigation height */
   }
   
   /* Optimized navigation container padding */
   .component-nav {
       padding: 8px 0 !important; /* Reduced from 10px vertical padding */
   }
   ```

2. **Additional Space Optimization** (if needed):
   - If additional optimization is required after testing, add:
   ```css
   /* Further space optimization */
   .left-panel-nav {
       padding-top: 5px !important;
       padding-bottom: 5px !important;
   }
   ```

### Task 3: Create Component Placeholders

1. **Create Apollo Component Placeholder**:
   - Create directory `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/apollo/`
   - Create file `apollo-component.html` in that directory
   - Use the template provided in the NavigationImplementation.md document

2. **Create Metis Component Placeholder**:
   - Create directory `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/metis/`
   - Create file `metis-component.html` in that directory
   - Use the template provided in the NavigationImplementation.md document

### Task 4: Test and Verify Changes

1. **Visual Testing**:
   - Open the Tekton UI in a browser
   - Verify all tabs are visible without scrolling
   - Check that the new tabs are in the correct positions
   - Verify color indicators display correctly

2. **Functional Testing**:
   - Click each tab to verify navigation works
   - Ensure placeholder components load correctly
   - Test on different browser window sizes

3. **Iterative Adjustments**:
   - If any issues are found, make incremental adjustments
   - Focus on ensuring all tabs fit without scrolling
   - Maintain visual quality and usability

## Implementation Notes

- Follow the Clean Slate architecture principles
- Make minimal changes to ensure stability
- Use the existing patterns and conventions
- Maintain BEM naming conventions for any new CSS
- Include debug instrumentation in component placeholders

## Verification Checklist

Use this checklist to verify your implementation:

- [ ] Apollo tab appears between Engram and Rhetor
- [ ] Metis tab appears between Ergon and Harmonia
- [ ] Both tabs have the correct color indicators
- [ ] All tabs fit in the LEFT PANEL without scrolling
- [ ] Tab text is fully visible and readable
- [ ] Clicking tabs works correctly
- [ ] Placeholder components load when tabs are clicked
- [ ] No visual glitches or UI issues are present

## Completion Criteria

Phase 2 is considered complete when:

1. Both navigation tabs have been added to the LEFT PANEL
2. Space optimization changes have been implemented
3. Component placeholder files have been created
4. All verification checks pass
5. Changes have been tested in multiple browsers

## Next Steps After Completion

After successful implementation:

1. Document any challenges encountered
2. Create a Phase 2 status report
3. Prepare for Phase 3 (Testing and Verification)
4. Outline any recommendations for future improvements