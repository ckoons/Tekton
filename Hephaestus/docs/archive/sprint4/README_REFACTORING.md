# Hephaestus UI Refactoring README

## Overview

This refactoring addresses the critical issue with `ui-manager.js` becoming too large (>50,000 tokens, ~200KB) to manage effectively. The monolithic file has been refactored into a modular architecture with smaller, focused modules organized by responsibility.

## Installation

To install the refactored architecture, run the installation script:

```bash
cd /Users/cskoons/projects/github/Tekton/Hephaestus/ui
./install_refactored_ui.sh
```

This script will:
1. Create backups of existing files (.bak extensions)
2. Create the necessary directory structure
3. Copy the new modular files into place
4. Install the updated index.html and main.js

## New Directory Structure

```
ui/
  scripts/
    core/
      ui-manager-core.js     # Core UI management functionality
      component-loader.js    # Generic component loading utilities
      panel-manager.js       # Panel switching and management
    components/
      athena/
        athena-component.js  # Athena implementation
      ergon/
        ergon-component.js   # Ergon implementation
      shared/
        chat-panel.js        # Shared chat functionality
        tab-navigation.js    # Shared tab functionality
```

## Testing After Installation

After installing, please verify that:

1. The UI loads correctly
2. Navigation between components works
3. The Athena component functions properly
4. The Ergon component functions properly
5. Terminal input and WebSocket communication work

## Rollback Procedure

If issues are encountered, you can roll back to the previous version:

```bash
cd /Users/cskoons/projects/github/Tekton/Hephaestus/ui
cp scripts/main.js.bak scripts/main.js
cp index.html.bak index.html
```

## Next Steps

The next session should:

1. Test the refactored architecture to ensure it works correctly
2. Complete any remaining Ergon component implementation
3. Begin implementing the Hermes component using the new architecture

## Documentation

For more detailed information about the refactoring, please refer to:

- `REFACTORING.md` - Complete documentation of the refactoring approach
- `UI_REFACTORING_SUMMARY.md` - Implementation summary in the MetaData directory
- `SprintPlan.md` - Updated sprint plan with next steps

## Legacy Code Cleanup

Legacy code cleanup will be performed after all components are implemented and tested using the new architecture. The cleanup process will:

1. Verify all functionality works correctly
2. Temporarily rename legacy files (*.deprecated)
3. Test thoroughly
4. Permanently remove legacy files
5. Conduct final verification testing

## Implementation Standards

All components MUST follow the Component Implementation Standard found in `/MetaData/UI/ComponentImplementationStandard.md`. This standard ensures components work reliably when loaded together and prevents tab switching issues between components.

Refer to these reference implementations:
- `/components/athena/athena-component.html` - Fully implemented using the standard pattern
- `/components/ergon/ergon-component.html` - Fully implemented using the standard pattern

## Components Implemented

- ✅ Athena - Fully implemented following the standard
- ✅ Ergon - Fully implemented following the standard

## Components To Be Implemented

1. Hermes (next)
2. Engram
3. Rhetor
4. Prometheus
5. Telos
6. Harmonia
7. Synthesis
8. Sophia
9. Terma
10. Codex (later)