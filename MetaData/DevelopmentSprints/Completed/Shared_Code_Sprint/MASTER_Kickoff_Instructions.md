# Tekton Shared Code Implementation - Kickoff Instructions

## Overview

This document provides instructions for kicking off the Shared Code Implementation Sprint, which will create standardized, shared code utilities across the Tekton ecosystem, eliminating duplicated code and improving maintainability.

## Getting Started

1. **Create a dedicated branch for shared code implementation**:
   ```bash
   git checkout -b shared-code/implementation
   ```

2. **Set up the Claude Code session**:
   - Start a new Claude Code session
   - Provide the MASTER_Claude_Code_Prompt.md as the initial prompt
   - Share the MASTER_Implementation_Plan.md for reference if needed

## Implementation Workflow

The implementation should follow this workflow:

1. **Create shared utilities**: Implement all shared code utilities
2. **Migrate components**: Update components to use shared utilities
3. **Remove duplicated code**: After each successful migration, remove the old code
4. **Test thoroughly**: Verify all functionality works correctly
5. **Update documentation**: Document the new shared utilities

## Clean Slate Approach

This implementation uses a "clean slate" approach:

1. Start by implementing the new shared code utilities
2. For each component:
   - Migrate to use the shared utilities
   - Test to ensure functionality is preserved
   - Remove the old, duplicated code
3. After all components are migrated, verify all functionality

## Key Requirements

1. **Replace ALL duplicated utility code** across components:
   - Bash utility functions
   - Component registration scripts
   - LLM integration utilities

2. **Remove old code** after successful migration:
   - Delete all individual register_with_hermes.py scripts
   - Remove duplicated bash utilities
   - Clean up redundant configuration loading

3. **Maintain backward compatibility** where needed:
   - Ensure components continue to function during transition
   - Provide graceful degradation when dependencies are unavailable

## Testing Guidelines

For each shared utility:

1. Test with normal usage patterns
2. Test edge cases and error conditions
3. Verify compatibility with all components
4. Ensure proper error handling and logging

For the component registration system:

1. Verify each component registers successfully with Hermes
2. Test registration of all component capabilities
3. Verify heartbeat functionality
4. Test graceful shutdown and unregistration

## Documentation Expectations

The following documentation should be updated:

1. `docs/COMPONENT_LIFECYCLE.md` - Updated with standardized registration process
2. `docs/SHARED_COMPONENT_UTILITIES.md` - Document all shared utilities
3. Component-specific documentation - Update to reference shared utilities

## Success Criteria

The implementation is successful when:

1. All components use shared bash utilities
2. All components register with Hermes using tekton-register
3. Components use enhanced LLM client where appropriate
4. No duplicated utility code remains across components
5. Documentation is updated to reflect the new approach
6. All tests pass successfully

## Post-Implementation Review

After completing the implementation:

1. Conduct a code review to ensure quality and consistency
2. Verify all duplicated code has been removed
3. Test all components to ensure functionality is preserved
4. Review documentation for completeness and clarity

## Timeline

- Phase 1 (Week 1): Core Shell Utilities
- Phase 2 (Week 2): Unified Component Registration
- Phase 3 (Week 3): Enhanced LLM Integration
- Phase 4 (Week 4): Complete Component Migration and Cleanup

## Contact Information

If you encounter any issues or have questions during implementation, please document them clearly for review and resolution.