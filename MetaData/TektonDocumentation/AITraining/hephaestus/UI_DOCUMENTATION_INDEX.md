# Hephaestus UI Documentation Index

This index lists all relevant documentation for understanding how the Hephaestus UI works, organized by topic.

## Core UI Architecture Documents

### Primary References
1. **[How Tekton UI Works](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/Building_New_Tekton_Components/HowTektonUIWorks.md)**
   - Living document with hard-won lessons
   - Documents the CSS-first architecture update
   - Critical implementation details and gotchas

2. **[CSS-First Architecture](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/Architecture/CSSFirstArchitecture.md)**
   - Explains the attempted pure CSS navigation approach
   - Documents current hybrid implementation
   - Core philosophy and benefits

3. **[Hephaestus UI Architecture](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/Architecture/HephaestusUIArchitecture.md)**
   - UI DevTools integration
   - Component instrumentation patterns
   - Semantic tagging system

## Implementation Guides

### Component Development
1. **[Hephaestus UI Implementation Guide](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/Building_New_Tekton_Components/Hephaestus_UI_Implementation.md)**
   - Detailed component structure
   - Implementation process
   - File organization and patterns

2. **[UI Implementation Guide](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/Building_New_Tekton_Components/UI_Implementation_Guide.md)**
   - General UI implementation patterns
   - AI interface implementation details
   - Best practices and common patterns

3. **[Component Architecture Guide](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/Building_New_Tekton_Components/Component_Architecture_Guide.md)**
   - Overall component architecture
   - Integration patterns

## Quick References

1. **[CSS-First Quick Reference](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/Developer_Reference/UIDevTools/CSS-FIRST-QUICK-REFERENCE.md)**
   - Quick summary of CSS-first approach
   - Key files and commands
   - What's deprecated vs. current

2. **[How Tekton UI Works (Developer Reference)](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/Developer_Reference/HowTektonUIWorks.md)**
   - Another copy of the core UI documentation
   - Same content as Building_New_Tekton_Components version

## UI Standards and Patterns

1. **[UI Styling Standards](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/Building_New_Tekton_Components/UI_Styling_Standards.md)**
   - CSS naming conventions
   - Theme system usage
   - Component styling patterns

2. **[Semantic UI Architecture](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/Architecture/SemanticUIArchitecture.md)**
   - Semantic tagging patterns
   - Data attributes usage

3. **[Loading State System](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/Building_New_Tekton_Components/LoadingStateSystem.md)**
   - How loading states work
   - Implementation patterns

## UI DevTools Documentation

1. **[UI DevTools Reference](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/Developer_Reference/UIDevTools/UIDevToolsReference.md)**
2. **[UI DevTools Cookbook](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/Developer_Reference/UIDevTools/UIDevToolsCookbook.md)**
3. **[Semantic Tags Reference](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/Developer_Reference/UIDevTools/SEMANTIC-TAGS-REFERENCE.md)**

## Component-Specific Documentation

1. **[Hephaestus Developer Guide](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/Building_New_Tekton_Components/Hephaestus_Developer_Guide.md)**
2. **[Hephaestus Implementation Guide](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/Building_New_Tekton_Components/Hephaestus_Implementation_Guide.md)**

## Key Concepts Summary

### CSS-First Architecture
- All components pre-loaded in HTML (attempted approach)
- CSS handles navigation via `:target` selectors (had limitations)
- Currently uses minimal-loader.js for reliable navigation
- Only ~300 lines of JavaScript total

### Critical Rules
1. **All CSS must be linked in index.html** - No dynamic CSS loading
2. **Use BEM naming convention** - Prevents style conflicts
3. **Set usesShadowDom: false** - For content visibility
4. **Follow semantic tagging** - Use data-tekton-* attributes

### Component Structure
- Header: Component title and branding
- Menu Bar: Tab navigation
- Content: Dynamic based on selected tab
- Footer: Component-specific actions

### File Locations
- Components: `/ui/components/[name]/[name]-component.html`
- Styles: `/ui/styles/[name]/[name]-component.css`
- Scripts: `/ui/scripts/[name]/[name]-component.js`
- Registry: `/ui/server/component_registry.json`

---

*This index compiled January 2025 to consolidate Hephaestus UI documentation.*