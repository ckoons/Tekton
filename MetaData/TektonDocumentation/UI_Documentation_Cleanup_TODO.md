# UI Documentation Cleanup TODO

Generated: 2025-01-03

## Overview
This document tracks the UI documentation cleanup needed after the CSS-first architecture evolution and the discovery that the pure CSS approach had limitations.

## Current State
- The UI uses `minimal-loader.js` for dynamic component loading (not deprecated)
- The pure CSS `:target` approach was attempted but had fundamental limitations
- `build-simplified.py` was deleted as it created broken navigation
- `index-simplified.html` was renamed to `index-simplified.html.deprecated`

## Files to Update

### 1. High Priority - Contains Inaccurate Information

#### `/Hephaestus/ui/README.md`
- [ ] Remove all references to `build-simplified.py` (lines 80, 92)
- [ ] Update or remove the old component implementation pattern section (lines 110-142)
- [ ] Clarify that minimal-loader.js is the current approach

#### `/MetaData/TektonDocumentation/Building_New_Tekton_Components/Hephaestus_UI_Implementation.md`
- [ ] Add deprecation notice at the top
- [ ] Update to reflect current minimal-loader.js approach
- [ ] Remove or clearly mark old dynamic loading examples as outdated

### 2. Files to Review and Potentially Archive

- `/MetaData/TektonDocumentation/Architecture/ComponentManagement.md`
- `/MetaData/TektonDocumentation/Architecture/ComponentLifecycle.md`
- `/MetaData/TektonDocumentation/Building_New_Tekton_Components/LoadingStateSystem.md`

### 3. Files to Delete

- [ ] `index-simplified.html.deprecated` (already renamed, can be deleted)
- [ ] Any archived documentation about the old UI system that might confuse new developers

## Good Examples to Follow

`/MetaData/TektonDocumentation/Building_New_Tekton_Components/HowTektonUIWorks.md` is a good example because it:
- Has a clear CSS-first update notice at the top
- Marks deprecated sections with "⚠️ DEPRECATED"
- Explains what changed and why

## Key Messages to Reinforce

1. **Current Architecture**: Uses minimal-loader.js for dynamic component loading
2. **No Build Step**: Edit component files directly, refresh browser to see changes
3. **CSS-First Philosophy**: CSS handles styling and layout, minimal JavaScript for functionality
4. **Deprecated Approach**: The pure CSS `:target` approach had limitations and was abandoned

## Cleanup Principles

1. Don't delete historical information - mark it as deprecated
2. Add clear notices about what's current vs. outdated
3. Explain WHY approaches were changed (e.g., CSS limitations)
4. Keep documentation that helps understand the evolution of the system