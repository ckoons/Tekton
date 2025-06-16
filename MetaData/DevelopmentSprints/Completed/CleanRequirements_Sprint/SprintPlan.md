# CleanRequirements Sprint Plan

## Overview

This Development Sprint focuses on comprehensive dependency optimization across all Tekton components, addressing critical version conflicts, eliminating massive dependency duplication, and establishing sustainable dependency management practices. The sprint will reduce the overall dependency footprint by 60-70% while resolving system-breaking compatibility issues.

## Sprint Goals

### Primary Objectives
1. **Resolve Critical Version Conflicts**: Fix Pydantic, Anthropic, and WebSocket version incompatibilities
2. **Eliminate Dependency Duplication**: Consolidate vector processing and web framework stacks
3. **Standardize Dependency Management**: Create centralized, maintainable dependency specifications
4. **Improve System Performance**: Reduce install times, disk usage, and memory footprint

### Secondary Objectives
1. **Separate Production/Development Dependencies**: Clean architectural boundaries
2. **Implement Optional Dependency Patterns**: Graceful degradation for heavy libraries
3. **Create Sustainable Maintenance Processes**: Long-term dependency management strategies

## Current State Analysis

### Critical Issues Identified

#### 1. System-Breaking Version Conflicts
- **Pydantic**: Range from 1.9.0 to 2.10.6 (major API changes causing component communication failures)
- **Anthropic**: 0.5.0 to 0.10.0 (significant API differences)
- **WebSockets**: 10.3 to 11.0.3 (major version incompatibilities)

#### 2. Massive Dependency Duplication
- **Vector Processing Stack**: `faiss-cpu`, `sentence-transformers`, `torch` appear in 3+ components (~6GB redundant)
- **Data Science Stack**: `numpy`, `pandas`, `scipy` duplicated across 4+ components (~2GB redundant)
- **Web Framework Stack**: FastAPI ecosystem duplicated across 15+ components

#### 3. Dependency Management Issues
- Missing version pinning causing unpredictable behavior
- Development dependencies mixed with production requirements
- Redundant installations (e.g., Engram's double Flask-Bootstrap dependencies)
- 23+ requirements.txt files with inconsistent patterns

### Impact Assessment
- **System Reliability**: Version conflicts causing component launch failures
- **Resource Usage**: ~8GB+ unnecessary dependency duplication
- **Development Velocity**: Inconsistent dependencies slowing development
- **Maintenance Burden**: Manual dependency conflict resolution

## Implementation Strategy

### Phase 1: Critical Conflict Resolution (Session 1)
**Objective**: Resolve immediate system-breaking version conflicts

**Scope**:
- Standardize Pydantic to 2.x across all components
- Fix Anthropic API version conflicts
- Resolve WebSocket version incompatibilities
- Remove obvious redundant dependencies (Engram Flask-Bootstrap)

**Success Criteria**:
- All components use compatible Pydantic versions
- No version conflict errors during component launches
- Successful `tekton-launch --launch-all` execution

**Key Files**:
- All component `requirements.txt` files
- `tekton-llm-client/requirements.txt` (Pydantic 1.x source)
- `Engram/requirements.txt` (redundant Flask dependencies)

### Phase 2: Dependency Consolidation (Sessions 2-3)
**Objective**: Create shared dependency packages and eliminate duplication

**Scope**:
- Create `/shared/requirements/` with consolidated dependency specifications
- Consolidate vector processing stack into `tekton-core` or dedicated package
- Standardize web framework dependencies across components
- Create shared LLM integration dependencies

**Success Criteria**:
- 60-70% reduction in total dependency footprint
- Shared requirements files covering common dependency patterns
- No functionality regression in any component

**Key Deliverables**:
- `/shared/requirements/web-common.txt`
- `/shared/requirements/llm-common.txt`
- `/shared/requirements/vector-common.txt`
- Updated component requirements referencing shared dependencies

### Phase 3: Architecture Optimization (Sessions 4-5)
**Objective**: Implement sustainable dependency management patterns

**Scope**:
- Separate production and development dependencies
- Implement optional dependency patterns for heavy libraries
- Create dependency injection mechanisms for better modularity
- Establish version constraint standards

**Success Criteria**:
- Clear separation between production and development dependencies
- Optional heavy dependencies with graceful fallback
- Documented dependency management standards

**Key Deliverables**:
- `requirements-dev.txt` files for development dependencies
- Optional dependency loading patterns
- Dependency management documentation

### Phase 4: Testing and Validation (Session 6)
**Objective**: Comprehensive testing and performance validation

**Scope**:
- Full system testing with optimized dependencies
- Performance benchmarking (install times, memory usage)
- Regression testing for all component functionality
- Documentation updates

**Success Criteria**:
- All components launch successfully with new dependency structure
- Measurable performance improvements
- No functionality regressions
- Complete documentation

## Resource Requirements

### Technical Resources
- Access to all component repositories
- Ability to modify requirements.txt files across components
- Testing environment for full system validation

### Time Allocation
- **Phase 1**: 1 Claude Code session (4-6 hours)
- **Phase 2**: 2 Claude Code sessions (8-12 hours)
- **Phase 3**: 1-2 Claude Code sessions (6-10 hours)
- **Phase 4**: 1 Claude Code session (4-6 hours)

**Total Estimated Effort**: 22-34 hours across 5-6 sessions

## Risk Assessment

### High Risks
- **Breaking Component Functionality**: Dependency changes could break existing features
  - *Mitigation*: Incremental changes with comprehensive testing
- **Version Incompatibilities**: New standardized versions might have undiscovered conflicts
  - *Mitigation*: Careful version selection and thorough compatibility testing

### Medium Risks
- **Performance Regression**: Shared dependencies might impact specific component performance
  - *Mitigation*: Performance benchmarking and rollback plans
- **Development Workflow Disruption**: Changes might affect developer environments
  - *Mitigation*: Clear migration instructions and support

### Low Risks
- **Documentation Lag**: Updated dependency patterns need documentation
  - *Mitigation*: Documentation updates as part of each phase

## Success Metrics

### Quantitative Metrics
- **Dependency Footprint Reduction**: Target 60-70% reduction in total dependencies
- **Install Time Improvement**: Target 40-50% faster installation
- **Disk Usage Reduction**: Target 4-6GB savings through deduplication
- **Version Conflict Elimination**: Zero version conflicts across components

### Qualitative Metrics
- **System Reliability**: Consistent component launches without dependency errors
- **Developer Experience**: Easier dependency management and conflict resolution
- **Maintenance Burden**: Reduced effort for dependency updates and troubleshooting

## Communication Plan

### Stakeholder Updates
- Progress reports after each phase completion
- Issue escalation for any blocking dependencies discoveries
- Final summary with performance improvements and architectural changes

### Documentation Updates
- Real-time updates to dependency management documentation
- Component-specific migration guides
- Best practices documentation for future dependency additions

## Next Steps

1. **Immediate**: Begin Phase 1 with critical conflict resolution
2. **Short-term**: Create shared requirements structure in Phase 2
3. **Medium-term**: Implement architectural optimizations in Phase 3
4. **Long-term**: Establish ongoing dependency management processes

This sprint will establish Tekton as having best-in-class dependency management with significant performance benefits and long-term maintainability.