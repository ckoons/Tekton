# Numa and Noesis Component Sprint

## Sprint Overview

This sprint implements two new core components for the Tekton ecosystem:
- **Numa**: Platform CI Mentor (Port 8016) - Provides platform-wide guidance and oversight
- **Noesis**: Discovery System (Port 8015) - Pattern discovery and insight generation

## Sprint Status

**Current Phase**: Implementation (Debugging Required)
**Start Date**: 2025-06-26
**Status**: In Progress - UI loading and registration issues need resolution

## Key Objectives

1. Create bare-bones Numa and Noesis components following Rhetor's pattern
2. Implement proper UI integration with dark theme
3. Enable Hermes registration for component discovery
4. Ensure no hardcoded ports (following Single Port Architecture)
5. Make Numa the default component on UI startup

## Current Issues

1. **UI Component Loading**:
   - Numa set as default but shows terminal instead of component
   - Clicking Numa nav tab loads Profile component instead
   - Panel switching not happening automatically

2. **Styling Issues**:
   - Footer styling doesn't match Rhetor
   - Background colors need CSS variable updates

3. **Hermes Registration**:
   - Both components failing with 422 validation error
   - Need to verify registration payload format

## Related Documentation

- [Single Port Architecture](/MetaData/TektonDocumentation/Architecture/SinglePort/)
- [Component Implementation Standard](/MetaData/UI/ComponentImplementationStandard.md)
- [Rhetor Component](/Rhetor/) - Reference implementation
- [UI DevTools V2 Guide](/MetaData/TektonDocumentation/Guides/UIDevToolsV2/)
- [Hermes Registration Protocol](/Hermes/README.md)

## Implementation Artifacts

- `/Numa/` - Platform CI Mentor component
- `/Noesis/` - Discovery System component
- `/shared/utils/env_config.py` - Updated with Numa/Noesis configs
- `/Hephaestus/ui/components/numa/` - UI component files
- `/Hephaestus/ui/components/noesis/` - UI component files