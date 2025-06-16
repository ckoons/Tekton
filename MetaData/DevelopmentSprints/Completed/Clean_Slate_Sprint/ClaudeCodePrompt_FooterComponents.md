# Claude Code Prompt: Complete Footer Components Implementation

## Task Overview
Continue implementation of the Budget, Profile, and Settings footer components for the Tekton Clean Slate Sprint. These components have been partially implemented following the Clean Slate architecture pattern, but need additional work to be fully functional and properly styled.

## Current Status
The current implementation progress is documented in `CleanSlateFooterProgress.md`. In summary:
- Budget component has been implemented with proper BEM naming and added to component_registry.json
- Profile and Settings have been converted from buttons to nav-items in the UI
- UI Manager has been updated to handle the new nav-item structure
- CSS styling has been improved for consistency across footer components
- The Budget CSS file has been moved to the correct directory structure

## Task Requirements

### 1. Complete Profile and Settings Components
- Verify Profile and Settings entries in `component_registry.json` are correct
- Check if Profile and Settings need dedicated CSS files in their respective directories
- Ensure click handlers for Profile and Settings properly show their respective panels
- Test tab switching functionality for all three footer components

### 2. Final Testing and Polishing
- Test the Budget, Profile, and Settings components to ensure they display and function correctly
- Verify consistent spacing and styling across all three components
- Check that the components work properly with the rest of the Tekton UI system
- Test the components with different themes if applicable

### 3. Documentation Updates
- Document any additional changes or decisions made
- Update architecture documentation if necessary

## File Locations
- Main UI HTML: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/index.html`
- Component Registry: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/server/component_registry.json`
- UI Manager: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/ui-manager-core.js`
- Budget Component:
  - HTML: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/budget/budget-component.html`
  - JS: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/budget/budget-component.js`
  - CSS: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/styles/budget/budget-component.css`
- Profile Component:
  - HTML: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/profile/profile-component.html`
  - JS: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/profile/profile-component.js`
  - CSS: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/styles/profile/profile-component.css`
- Settings Component:
  - HTML: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/settings/settings-component.html`
  - JS: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/settings/settings-component.js`
  - CSS: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/styles/settings/settings-component.css`

## Implementation Guidelines
- Continue to use Athena component as the "golden reference" for implementation patterns
- Maintain consistent BEM naming throughout all components
- Ensure proper spacing and styling consistent with the existing UI
- Follow the same tab patterns for Profile and Settings as used in Budget and Athena
- Ensure all components are properly isolated with no CSS leakage

## Definition of Done
- All three footer components (Budget, Profile, Settings) display correctly
- Clicking each component shows its respective panel
- Styling is consistent across all components
- Components work correctly on different themes
- All files are in their correct locations with proper naming
- Registry entries are correct for all components