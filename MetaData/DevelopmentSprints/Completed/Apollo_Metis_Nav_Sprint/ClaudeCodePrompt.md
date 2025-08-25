# Claude Code Prompt for Apollo & Metis Navigation Sprint

## Project Context

You are assisting with the Apollo & Metis Navigation Sprint for the Tekton project. Tekton is an intelligent orchestration system that coordinates multiple CI models and resources to efficiently solve complex software engineering problems.

This sprint focuses on extending the Tekton UI by adding two new navigation tabs to the LEFT PANEL:
1. Apollo - Attention/Prediction (positioned between Engram and Rhetor)
2. Metis - Workflow (positioned between Ergon and Harmonia)

We will also need to optimize the spacing of all tabs to ensure they fit within the LEFT PANEL without requiring scrolling.

## Your Task

Your task is to implement the UI changes needed to add these two new navigation components to the Tekton LEFT PANEL. You will NOT be implementing any actual functionality for these components, only adding the navigation tabs and preparing for future implementation.

Specifically, you need to:

1. Add a new Apollo tab in the LEFT PANEL navigation between Engram and Rhetor
   - Use "Apollo - Attention/Prediction" as the label
   - Assign #FFD600 (Amber/Golden Yellow) as the color indicator

2. Add a new Metis tab in the LEFT PANEL navigation between Ergon and Harmonia
   - Use "Metis - Workflow" as the label
   - Assign #00BFA5 (Mint/Turquoise) as the color indicator

3. Adjust the spacing in the LEFT PANEL to accommodate all tabs
   - Reduce the height of all navigation tabs by approximately 6%
   - Adjust footer navigation buttons (Budget, Profile, Settings) to match the main navigation height
   - Reduce vertical padding as needed
   - Ensure all tabs remain visible and clickable

4. Create basic placeholder files for the components to ensure navigation works

## Implementation Guidelines

Follow these implementation guidelines:

1. Make your changes on the `sprint/Clean_Slate_051125` branch.

2. Focus on the main `index.html` file for the navigation changes.

3. Follow the existing patterns for tab structure:
   ```html
   <li class="nav-item" data-component="componentname">
       <span class="nav-label">ComponentName - Description</span>
       <span class="status-indicator"></span>
   </li>
   ```

4. Follow the existing pattern for color indicators:
   ```css
   .nav-item[data-component="componentname"] .status-indicator { 
       background-color: #HEXCOLOR;
   }
   ```

5. Adjust CSS for navigation tabs to reduce height by about 6%:
   - Modify the `.nav-item` and `.component-nav` CSS classes
   - Adjust `.footer-buttons .control-button` to match the main navigation
   - Be careful not to break existing functionality

6. Create minimal component placeholder files at:
   - `/components/apollo/apollo-component.html`
   - `/components/metis/metis-component.html`

7. Test thoroughly to ensure:
   - All tabs are visible without scrolling
   - New tabs are correctly positioned
   - Navigation functionality works
   - No visual glitches occur

## Resources to Reference

- The main `index.html` file contains the LEFT PANEL navigation structure
- The Clean Slate Sprint documentation provides guidance on component structure
- The existing component HTML files serve as templates for placeholder files

## Deliverables

1. Modified `index.html` file with new navigation tabs
2. CSS adjustments for tab sizing
3. Basic component placeholder files
4. Verification that all tabs fit and function correctly

## Notes

- Remember, we are only adding navigation elements, not implementing actual functionality
- Keep changes targeted and minimal to reduce risk
- Follow established Tekton UI patterns and conventions
- Verify all changes visually in the browser
- Document any challenges or decisions made during implementation

Please proceed step by step, testing your changes at each stage. Document your approach and any issues encountered.