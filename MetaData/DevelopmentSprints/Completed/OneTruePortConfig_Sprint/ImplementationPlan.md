# Implementation Plan - OneTruePortConfig Sprint

## Overview
This implementation plan outlines the phases and approach for centralizing port configuration. The implementing Claude should review and refine this plan based on their analysis of the codebase.

## Debug Instrumentation Requirements
All new code MUST include debug instrumentation following Tekton standards:
- Python: Use `@debug_log` decorators and `logger.debug()` with TEKTON_DEBUG awareness
- Configuration modules should have verbose debug output for troubleshooting
- Service discovery should log all resolution attempts when debugging enabled

## Implementation Phases

### Phase 1: Core Infrastructure (Day 1)
**Goal**: Create the central port configuration system

**Suggested Tasks**:
1. Design central port configuration module structure
2. Create port validation utilities
3. Implement configuration loading with error handling
4. Design service discovery interface
5. Create migration compatibility layer

**Key Considerations**:
- How to handle missing port definitions
- Validation of port ranges (1024-65535)
- Conflict detection between components
- Clear error messages

### Phase 2: Component Migration (Day 2)
**Goal**: Systematically migrate all components to central configuration

**Suggested Approach**:
1. Create migration script/tool to identify hardcoded ports
2. Start with core infrastructure components (Hermes, Engram)
3. Update each component to use central configuration
4. Maintain backwards compatibility during transition
5. Update component tests

**Components to Migrate** (in suggested order):
- Hermes (central registry)
- Engram (memory system)
- Rhetor (LLM management)
- All other components alphabetically

### Phase 3: Service Discovery Integration (Day 2-3)
**Goal**: Enable dynamic component discovery

**Suggested Tasks**:
1. Implement service discovery utilities
2. Update cross-component communication patterns
3. Add caching for performance
4. Create fallback mechanisms
5. Document patterns for component communication

**Key Areas**:
- Components calling Hermes for registration
- Rhetor client initialization
- Budget tracking integration
- UI components finding backend services

### Phase 4: Testing and Validation (Day 3)
**Goal**: Ensure system stability with new configuration

**Testing Strategy**:
1. Unit tests for configuration module
2. Integration tests for service discovery
3. Component startup tests
4. Cross-component communication tests
5. Migration validation tests

**Validation Checklist**:
- [ ] All components start successfully
- [ ] No hardcoded ports remain
- [ ] Service discovery works
- [ ] Backwards compatibility verified
- [ ] Performance impact measured

### Phase 5: Documentation and Cleanup (Day 3)
**Goal**: Complete documentation and remove legacy code

**Documentation Updates**:
1. Update component documentation
2. Create port configuration guide
3. Document service discovery patterns
4. Update .env.tekton template with examples
5. Create troubleshooting guide

**Cleanup Tasks**:
1. Remove compatibility layer (after verification)
2. Remove hardcoded port comments
3. Update all README files
4. Create migration guide for future components

## Technical Design Considerations

### Central Configuration Module Structure
```
shared/utils/
├── port_config.py          # Central port definitions and access
├── service_discovery.py    # Component discovery utilities
└── port_validation.py      # Validation and conflict detection
```

### Configuration Access Pattern
The implementing Claude should propose the specific API, but consider:
- Simple, intuitive interface
- Type safety where possible
- Clear error messages
- Minimal boilerplate

### Service Discovery Pattern
Consider leveraging existing Hermes registry with enhancements:
- Cached lookups
- Health check integration
- Fallback mechanisms
- Clear timeout handling

## Risk Mitigation

### Rollback Strategy
- Keep compatibility layer until fully validated
- Document rollback procedures
- Test rollback scenarios

### Monitoring
- Log all port resolution attempts
- Monitor component startup times
- Track service discovery failures

## Success Criteria
1. Zero hardcoded ports in component code
2. All components use same configuration pattern
3. Service discovery works reliably
4. Clear documentation exists
5. All tests pass
6. Performance impact < 100ms on startup

## Notes for Implementation
This plan provides structure and guidance. The implementing Claude should:
1. Analyze the current state thoroughly
2. Propose specific implementation details
3. Identify any additional considerations
4. Refine the phase breakdown as needed
5. Ensure debug instrumentation throughout

The goal is clean, maintainable port configuration that serves Tekton's growth.