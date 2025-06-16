# OneTruePortConfig Sprint Plan

## Sprint Overview
**Sprint Name**: OneTruePortConfig_Sprint  
**Duration**: 2-3 days  
**Priority**: High  
**Branch**: sprint/OneTruePortConfig

## Objective
Consolidate and standardize all port configuration across Tekton components into a single, maintainable system that eliminates hardcoded values and provides clear patterns for component communication.

## Problem Statement
Currently, port configuration in Tekton is scattered across multiple locations:
- Hardcoded fallbacks in component files
- Configuration in env_config.py
- Environment variables in .env.tekton
- Inconsistent patterns for accessing port values
- Cross-component port references without clear patterns

This creates maintenance challenges and makes the system fragile when ports need to change.

## Goals
1. **Single Source of Truth**: All port configurations in one place
2. **Zero Hardcoded Ports**: Remove all hardcoded port values from application code
3. **Consistent Access Pattern**: One way to get any component's port
4. **Service Discovery**: Components can easily find each other
5. **Clear Documentation**: How to add new components and configure ports

## Success Criteria
- [ ] All hardcoded port values removed from component code
- [ ] Central port configuration system implemented
- [ ] All components use the same pattern for port access
- [ ] Cross-component communication uses service discovery
- [ ] Documentation updated with new patterns
- [ ] All components start successfully with new configuration
- [ ] Retrospective updates all relevant documentation

## Key Deliverables
1. Central port configuration module
2. Updated env_manager with port-specific utilities
3. Service discovery utilities for cross-component communication
4. Migration of all components to new pattern
5. Updated documentation and examples
6. Comprehensive test coverage

## Technical Approach
1. Create `shared/utils/port_config.py` as the central port authority
2. Enhance env_manager.py with port-specific methods
3. Create service discovery utilities in `shared/utils/service_discovery.py`
4. Systematically update each component to use new patterns
5. Update .env.tekton template with all port definitions
6. Add validation to ensure all required ports are defined

## Risks and Mitigation
- **Risk**: Breaking existing deployments
  - **Mitigation**: Backwards compatibility during transition
- **Risk**: Missing some hardcoded values
  - **Mitigation**: Automated scanning tools to find all occurrences
- **Risk**: Component startup failures
  - **Mitigation**: Comprehensive testing before merge

## Sprint Phases
1. **Architecture & Design** (Day 1)
   - Design central port configuration system
   - Create migration strategy
   - Document new patterns

2. **Implementation** (Day 2)
   - Implement core utilities
   - Migrate components systematically
   - Update configuration files

3. **Testing & Documentation** (Day 3)
   - Test all components
   - Update documentation
   - Create retrospective

## Definition of Done
- All components use centralized port configuration
- No hardcoded ports remain in codebase
- All tests pass
- Documentation is complete and accurate
- Retrospective documents lessons learned