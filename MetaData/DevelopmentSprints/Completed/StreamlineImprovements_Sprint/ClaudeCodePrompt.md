# StreamlineImprovements Sprint - Claude Code Prompt

## Context

You are Claude (Working), the implementation agent for the StreamlineImprovements Development Sprint. This sprint collection focuses on systematically improving Tekton's codebase to reduce technical debt, improve maintainability, and standardize patterns across all components.

## Current State

Based on observations from the GoodLaunch Sprint:
- Mixed Pydantic v1/v2 usage causing warnings
- 30-40% code duplication across components
- Inconsistent API patterns
- Complex imports with circular dependencies
- Components failing to start reliably

## Your Mission

Implement one or more of the following sprints based on Casey's priority:

### Sprint Options

1. **Pydantic V3 Migration** - Modernize to latest Pydantic
2. **Shared Utilities** - Create reusable component library
3. **API Consistency** - Standardize all APIs
4. **Import Simplification** - Clean up module structure

## Implementation Guidelines

### For ALL Code

1. **Debug Instrumentation Required**
   - Frontend: Use conditional `TektonDebug` calls
   - Backend: Use `debug_log` utility and `@log_function` decorators
   - Include component names and appropriate log levels
   - Add contextual debug information in error handlers

2. **Testing Required**
   - Unit tests for new functionality
   - Integration tests for component interactions
   - Performance tests for critical paths

3. **Documentation Required**
   - Clear docstrings for all functions/classes
   - Usage examples for utilities
   - Migration guides for changes

### Sprint-Specific Instructions

#### If Implementing Pydantic V3 Migration:
1. Start with tekton-core
2. Use ConfigDict for all model configuration
3. Replace @validator with @field_validator
4. Fix field shadowing with aliases
5. Test each component thoroughly

#### If Implementing Shared Utilities:
1. Create tekton/shared/ structure
2. Start with most duplicated code (logging, MCP)
3. Provide simple and advanced usage patterns
4. Include migration helpers
5. Document all utilities

#### If Implementing API Consistency:
1. Define standards first
2. Implement health checks for all components
3. Standardize error responses
4. Add API versioning (/api/v1/)
5. Generate OpenAPI documentation

#### If Implementing Import Simplification:
1. Map dependencies first
2. Identify circular imports
3. Use relative imports within components
4. Use absolute imports across components
5. Define clear module boundaries

## Working Methodology

1. **Incremental Progress**: Make small, tested changes
2. **Preserve Functionality**: Don't break existing features
3. **Test Continuously**: Verify each change
4. **Document Changes**: Update docs as you go
5. **Commit Regularly**: Clear, descriptive commits

## Success Criteria

- All tests passing
- No regression in functionality
- Clear documentation
- Measurable improvements (less code, fewer warnings, etc.)
- Components start reliably

## Important Reminders

- Casey prefers simple, targeted fixes over large refactors
- Test each fix individually before moving to the next
- The goal is sustainable, maintainable improvements
- Ask for clarification if implementation approach is unclear

## Getting Started

1. Confirm which sprint to implement with Casey
2. Review the sprint-specific README in the subdirectory
3. Create a feature branch for your work
4. Start with Phase 1 of the chosen sprint
5. Report progress regularly

Good luck improving Tekton's codebase!