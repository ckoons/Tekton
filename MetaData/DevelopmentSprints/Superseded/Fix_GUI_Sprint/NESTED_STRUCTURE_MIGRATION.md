# Nested Structure Migration Plan

## Overview

This document outlines the plan to standardize all components to use a nested directory structure, removing support for flat structures. This standardization will improve code organization, make the codebase more maintainable, and reduce the complexity of the component loader.

## Standardized Structure

All components will follow this standardized nested structure:

- **HTML**: `/components/component-name/component-name-component.html`
- **CSS**: `/styles/component-name/component-name-component.css`
- **JavaScript**: `/scripts/component-name/component-name-component.js`

## Migration Steps

### 1. Component File Migration

| Component | HTML Status | CSS Status | JS Status | UI Verified |
|-----------|:-----------:|:----------:|:---------:|:-----------:|
| **Athena** | ✅ Present | ✅ Present | ✅ Present | 🔄 Partially Working |
| **Ergon** | ✅ Present | ✅ Present | ✅ Present | ❌ Loading Error |
| **Hermes** | ⬜ Pending | ⬜ Pending | ⬜ Pending | ⬜ Unverified |
| **Rhetor** | ⬜ Pending | ⬜ Pending | ⬜ Pending | ⬜ Unverified |
| **Terma** | ⬜ Pending | ⬜ Pending | ⬜ Pending | ⬜ Unverified |
| **Engram** | ⬜ Pending | ⬜ Pending | ⬜ Pending | ⬜ Unverified |
| **Prometheus** | ⬜ Pending | ⬜ Pending | ⬜ Pending | ⬜ Unverified |
| **Telos** | ⬜ Pending | ⬜ Pending | ⬜ Pending | ⬜ Unverified |
| **Harmonia** | ⬜ Pending | ⬜ Pending | ⬜ Pending | ⬜ Unverified |
| **Synthesis** | ⬜ Pending | ⬜ Pending | ⬜ Pending | ⬜ Unverified |
| **Sophia** | ⬜ Pending | ⬜ Pending | ⬜ Pending | ⬜ Unverified |
| **Codex** | ⬜ Pending | ⬜ Pending | ⬜ Pending | ⬜ Unverified |

### 2. Code Modifications

| File | Status | Notes |
|------|:------:|-------|
| **component-loader.js** | ✅ Complete | Modified to only use standardized nested structure |
| **ui-manager.js** | ⬜ Pending | Mark for replacement with better-named file |
| **main.js** | ⬜ Pending | Verify it only uses nested structure |
| **Other JS files** | ⬜ Pending | Identify and update any hardcoded paths |

### 3. Legacy File Identification

We'll use the following mechanism to identify deprecated files before removal:

1. Create an inventory of all current component files in both structures
2. After migration, mark files in flat structure for removal
3. Verify no code references these files before deletion
4. Document all removed files for reference

## Deprecated Files Inventory

| File Path | Referenced By | Status |
|-----------|--------------|:------:|
| `/scripts/athena-component.js` | main.js, ui-manager-core.js | ⬜ Pending Removal |
| `/components/athena-component.html` | ui-manager-core.js | ⬜ Pending Removal |
| `/scripts/ergon-component.js` | main.js, ui-manager-core.js | ⬜ Pending Removal |
| `/components/ergon-component.html` | ui-manager-core.js | ⬜ Pending Removal |

## Large Files for Refactoring

| File | Lines | Size | Replacement Strategy | Status |
|------|-------|------|----------------------|:------:|
| **ui-manager.js** | TBD | TBD | Create modular components with better naming | ⬜ Pending |

## Migration Progress

1. 🔄 In Progress - Create inventory of all component files
2. ✅ Complete - Update component-loader.js to only use nested structure
3. 🔄 In Progress - Migrate and verify Athena component (highest priority)
4. 🔄 In Progress - Migrate and verify Ergon component (high priority)
5. ⬜ Pending - Migrate and verify Hermes component
6. ⬜ Pending - Migrate remaining components
7. ⬜ Pending - Update all code references to use nested structure
8. ⬜ Pending - Identify deprecated files for removal
9. ⬜ Pending - Verify UI functionality for all components
10. ⬜ Pending - Remove deprecated files

## Testing Protocol

For each component:
1. Migrate files to nested structure
2. Remove any fallback paths
3. Launch the UI
4. Verify component loads correctly
5. Test all tabs and functionality
6. Mark as "Verified" once confirmed working

## Notes on ui-manager.js Replacement

The current ui-manager.js file is too large and needs to be replaced with a more modular approach. Requirements for the replacement:

1. Create smaller, focused files with clear responsibility
2. Use more descriptive naming that reflects purpose
3. Implement proper error handling
4. Ensure complete test coverage
5. Document all new modules thoroughly

## Large File Threshold and Guidelines

- Files should not exceed 600 lines of code
- Functions should not exceed 50 lines
- All new files should follow the ES6 class pattern
- Use proper error handling with try/catch blocks
- Include JSDoc comments for all public methods