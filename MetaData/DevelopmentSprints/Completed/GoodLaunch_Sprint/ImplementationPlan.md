# GoodLaunch Sprint - Implementation Plan

## Overview

This document outlines the detailed implementation plan for the GoodLaunch Development Sprint. It breaks down the high-level goals into specific implementation tasks, defines the phasing, specifies testing requirements, and identifies documentation that must be updated.

Tekton is an intelligent orchestration system that coordinates multiple CI models and resources to efficiently solve complex software engineering problems. This Implementation Plan focuses on component reliability, launch system robustness, and lifecycle management.

## Debug Instrumentation Requirements

All code produced in this sprint **MUST** follow the [Debug Instrumentation Guidelines](/MetaData/TektonDocumentation/DeveloperGuides/Debugging/DebuggingInstrumentation.md). This section specifies the debug instrumentation requirements for this sprint's implementation.

### JavaScript Components

The following JavaScript components must be instrumented:

| Component | Log Level | Notes |
|-----------|-----------|-------|
| Hephaestus UI Status Display | INFO | Component status updates, connection events |
| Real-time Status Updates | DEBUG | WebSocket messages, state changes |
| Error Display Components | ERROR | Component failure notifications, error details |

All instrumentation must use conditional checks:

```javascript
if (window.TektonDebug) TektonDebug.info('componentName', 'Message', optionalData);
```

### Python Components

The following Python components must be instrumented:

| Component | Log Level | Notes |
|-----------|-----------|-------|
| Launch System Core | INFO | Component startup/shutdown events, dependency resolution |
| Health Check Manager | DEBUG | Health check requests/responses, timeout handling |
| Process Manager | INFO | Process lifecycle events, resource management |
| Import Resolution | DEBUG | Import success/failure, dependency loading |

All instrumentation must use the `debug_log` utility:

```python
from shared.debug.debug_utils import debug_log, log_function

debug_log.info("component_name", "Message")
```

Key methods should use the `@log_function` decorator:

```python
@log_function()
def important_method(param1, param2):
    # Method implementation
```

## Implementation Phases

This sprint will be implemented in 5 phases:

### Phase 1: Import Resolution and Health Fixes

**Objectives:**
- Resolve all import errors preventing component startup
- Fix timeout issues for health check responses
- Eliminate critical Pydantic v2 compatibility warnings
- Ensure fail-fast error handling works correctly

**Components Affected:**
- Prometheus (RetrospectiveAnalysis import)
- Sophia (ChatCompletionOptions import)
- Apollo (get_tools, get_apollo_manager imports)
- Metis (MCP decorator capability parameter)
- Budget (Pydantic root validator warnings)
- All components (Pydantic field shadowing warnings)

**Tasks:**

1. **Fix Missing Import Dependencies**
   - **Description:** Add missing classes and functions that components are trying to import
   - **Deliverables:** 
     - `RetrospectiveAnalysis` class in `prometheus.models.retrospective`
     - `ChatCompletionOptions` alias in `tekton_llm_client.models`
     - `get_tools` function in `apollo.core.mcp`
     - `get_apollo_manager` function in `apollo.api.dependencies`
   - **Acceptance Criteria:** All import errors resolved, components start without ImportError exceptions
   - **Dependencies:** None

2. **Fix MCP Decorator Issues**
   - **Description:** Resolve capability parameter issues with mcp_tool decorator
   - **Deliverables:** Updated MCP decorator implementation to handle capability parameters correctly
   - **Acceptance Criteria:** Metis and other components use MCP decorators without parameter errors
   - **Dependencies:** Task 1 completion

3. **Resolve Critical Pydantic v2 Issues**
   - **Description:** Fix root validator and field shadowing issues that prevent startup
   - **Deliverables:** 
     - Updated Pydantic models with proper v2 syntax
     - Renamed conflicting field names where necessary
     - Fixed root validator implementations
   - **Acceptance Criteria:** Components start without Pydantic validation errors
   - **Dependencies:** Task 1 completion

**Documentation Updates:**
- Import dependency tracking document
- MCP integration troubleshooting guide
- Pydantic v2 migration status

**Testing Requirements:**
- Import resolution verification tests
- Component startup health checks
- MCP decorator functionality tests

**Phase Completion Criteria:**
- All components start without import errors
- Health checks respond within timeout periods
- No critical Pydantic errors blocking startup
- Launch system properly reports actual failures

### Phase 2: Component Registration and Communication

**Objectives:**
- Ensure all components register with Hermes service registry
- Implement standardized health check endpoints
- Verify inter-component communication works correctly
- Establish proper component lifecycle management

**Components Affected:**
- All Tekton components (registration)
- Hermes (service registry enhancements)
- Health check endpoint implementations

**Tasks:**

1. **Standardize Health Check Endpoints**
   - **Description:** Implement consistent /health endpoints across all components
   - **Deliverables:** Standardized health check responses with status, timestamp, and component info
   - **Acceptance Criteria:** All components provide /health endpoint that responds within 5 seconds
   - **Dependencies:** Phase 1 completion

2. **Implement Service Registration**
   - **Description:** Ensure all components register with Hermes upon successful startup
   - **Deliverables:** Registration logic in component startup sequences
   - **Acceptance Criteria:** tekton-status shows 100% component registration rate
   - **Dependencies:** Task 1 completion

3. **Verify Component Communication**
   - **Description:** Test inter-component communication through Hermes message bus
   - **Deliverables:** Component communication verification tests
   - **Acceptance Criteria:** Components can successfully communicate through established channels
   - **Dependencies:** Task 2 completion

**Documentation Updates:**
- Component registration process documentation
- Health check endpoint specification
- Inter-component communication patterns

**Testing Requirements:**
- Service registration integration tests
- Health check endpoint tests
- Component communication verification tests

**Phase Completion Criteria:**
- 100% component registration with Hermes
- All health endpoints respond correctly
- Component communication verified through message bus
- Service discovery works for all registered components

### Phase 3: Python Launch System Development

**Objectives:**
- Create robust Python replacements for bash scripts
- Implement cross-platform compatibility
- Add structured error reporting and logging
- Ensure scripts can run from any directory

**Components Affected:**
- New Python launch system
- Process management utilities
- Configuration management
- Error reporting system

**Tasks:**

1. **Create tekton-launch.py**
   - **Description:** Python replacement for tekton-launch bash script with enhanced error handling
   - **Deliverables:** 
     - `tekton-launch.py` with full functionality
     - Cross-platform process management
     - Structured logging and error reporting
     - Configuration file support
   - **Acceptance Criteria:** Launches all components successfully, runs from any directory
   - **Dependencies:** Phase 2 completion

2. **Create tekton-status.py**
   - **Description:** Python replacement for tekton-status with detailed health information
   - **Deliverables:**
     - `tekton-status.py` with enhanced status reporting
     - JSON output option for programmatic use
     - Real-time status monitoring capabilities
   - **Acceptance Criteria:** Provides comprehensive status information, works from any directory
   - **Dependencies:** Task 1 completion

3. **Create tekton-kill.py**
   - **Description:** Python replacement for tekton-kill with proper cleanup verification
   - **Deliverables:**
     - `tekton-kill.py` with graceful shutdown
     - Resource cleanup verification
     - Process tree management
   - **Acceptance Criteria:** Cleanly shuts down all components, verifies resource cleanup
   - **Dependencies:** Task 2 completion

**Documentation Updates:**
- Python launch system user guide
- Installation and configuration instructions
- Cross-platform compatibility notes

**Testing Requirements:**
- Cross-platform launch tests
- Process management tests
- Error handling verification tests

**Phase Completion Criteria:**
- Python scripts fully replace bash scripts
- Scripts work from any directory location
- Cross-platform compatibility verified
- Structured error reporting implemented

### Phase 4: Parallel Launch Implementation

**Objectives:**
- Implement intelligent parallel component launching
- Maintain proper dependency ordering
- Optimize system startup time
- Handle parallel launch failures gracefully

**Components Affected:**
- Launch system core
- Dependency management system
- Process orchestration
- Error aggregation

**Tasks:**

1. **Implement Dependency Management**
   - **Description:** Create dependency graph and launch ordering system
   - **Deliverables:** 
     - Component dependency definitions
     - Dependency resolution algorithm
     - Launch order calculation
   - **Acceptance Criteria:** Core components (Hermes→Engram→Rhetor) launch sequentially, others in parallel
   - **Dependencies:** Phase 3 completion

2. **Create Parallel Process Manager** 
   - **Description:** Implement parallel process launching with proper resource management
   - **Deliverables:**
     - Parallel process manager
     - Resource allocation controls
     - Progress tracking and reporting
   - **Acceptance Criteria:** Multiple components launch simultaneously without conflicts
   - **Dependencies:** Task 1 completion

3. **Implement Failure Handling**
   - **Description:** Handle individual component failures without stopping other launches
   - **Deliverables:**
     - Isolated failure handling
     - Error aggregation and reporting
     - Retry mechanisms for transient failures
   - **Acceptance Criteria:** System continues launching other components when one fails
   - **Dependencies:** Task 2 completion

**Documentation Updates:**
- Component dependency documentation
- Parallel launch architecture guide
- Failure handling procedures

**Testing Requirements:**
- Dependency resolution tests
- Parallel launch performance tests
- Failure scenario tests

**Phase Completion Criteria:**
- System startup time reduced by 50%+
- Dependency ordering properly maintained
- Parallel launches work without conflicts
- Individual failures don't block other components

### Phase 5: UI Status Integration

**Objectives:**
- Add real-time component status indicators to Hephaestus UI
- Implement color-coded navigation dots
- Provide detailed component information on demand
- Enable real-time status updates via WebSocket

**Components Affected:**
- Hephaestus UI navigation system
- WebSocket communication layer
- Status monitoring backend
- Component status tracking

**Tasks:**

1. **Implement Status Dots in Navigation**
   - **Description:** Add color-coded status indicators to LEFT PANEL navigation tabs
   - **Deliverables:**
     - Visual status dots (🟢🟡🔴⚪)
     - CSS styling for different states
     - JavaScript status management
   - **Acceptance Criteria:** Navigation shows real-time component status with color coding
   - **Dependencies:** Phase 4 completion

2. **Create Real-time Status Updates**
   - **Description:** Implement WebSocket-based status updates between launch system and UI
   - **Deliverables:**
     - WebSocket status broadcasting
     - UI status update handlers
     - Connection management
   - **Acceptance Criteria:** UI updates component status within 2 seconds of changes
   - **Dependencies:** Task 1 completion

3. **Add Detailed Status Information**
   - **Description:** Provide detailed component information accessible from navigation
   - **Deliverables:**
     - Status detail modal/panel
     - Component health information
     - Error message display
   - **Acceptance Criteria:** Users can access detailed status information for any component
   - **Dependencies:** Task 2 completion

**Documentation Updates:**
- UI status integration guide
- WebSocket API documentation
- User interface documentation

**Testing Requirements:**
- UI status display tests
- WebSocket communication tests
- Real-time update verification tests

**Phase Completion Criteria:**
- Navigation shows real-time component status
- Status updates occur within 2 seconds
- Detailed status information accessible
- WebSocket communication works reliably

## Import Error Analysis

Based on the latest launch log, the following import errors need resolution:

### Prometheus Import Issues
- **Error**: `cannot import name 'RetrospectiveAnalysis' from 'prometheus.models.retrospective'`
- **File**: `/Users/cskoons/projects/github/Tekton/Prometheus/prometheus/models/retrospective.py`
- **Solution**: Create RetrospectiveAnalysis class with proper interface

### Sophia Import Issues  
- **Error**: `cannot import name 'ChatCompletionOptions' from 'tekton_llm_client.models'`
- **File**: `/Users/cskoons/projects/github/Tekton/tekton-llm-client/tekton_llm_client/models.py`
- **Solution**: Add ChatCompletionOptions alias or class

### Apollo Import Issues
- **Error 1**: `cannot import name 'get_tools' from 'apollo.core.mcp'`
- **Error 2**: `cannot import name 'get_apollo_manager' from 'apollo.api.dependencies'`
- **Files**: Apollo MCP and dependencies modules
- **Solution**: Implement missing functions with proper interfaces

### Metis MCP Issues
- **Error**: `mcp_tool() got an unexpected keyword argument 'capability'`
- **Solution**: Update MCP decorator to handle capability parameter correctly

### Budget Pydantic Issues
- **Error**: Root validator compatibility warnings
- **Solution**: Update to Pydantic v2 syntax patterns

## Technical Design Details

### Architecture Changes

The sprint maintains existing component architecture while enhancing the launch and monitoring infrastructure. No major architectural changes are required, but several infrastructure improvements will be made:

- Enhanced service registry in Hermes for better component tracking
- Standardized health check endpoints across all components  
- Python-based launch system with better process management
- Real-time status communication via WebSocket

### Data Model Changes

Minimal data model changes are required:

- Addition of component status models for tracking
- Health check response standardization
- Service registration metadata enhancement

### API Changes

New APIs will be added:

- Standardized `/health` endpoints for all components
- Service registration API enhancements in Hermes
- WebSocket API for real-time status updates

### User Interface Changes

UI changes will be additive:

- Color-coded status dots in navigation
- Status detail panels/modals
- Real-time update handling
- Error message display improvements

### Cross-Component Integration

Enhanced integration patterns:

- Consistent service registration across components
- Standardized health check interfaces
- Improved error propagation and aggregation
- Better dependency management during startup

## Code Organization

```
scripts/
├── python/                    # New Python launch system
│   ├── tekton-launch.py      # Main launch script
│   ├── tekton-status.py      # Status monitoring
│   ├── tekton-kill.py        # Shutdown management
│   ├── lib/                  # Shared utilities
│   │   ├── process_manager.py
│   │   ├── dependency_manager.py
│   │   ├── health_checker.py
│   │   └── status_reporter.py
│   └── tests/                # Python script tests
│       ├── test_launch.py
│       ├── test_status.py
│       └── test_shutdown.py
Hephaestus/
├── ui/
│   ├── scripts/
│   │   ├── status-monitor.js # Real-time status monitoring
│   │   └── component-status.js # Status display management
│   └── styles/
│       └── status-indicators.css # Status dot styling
```

## Testing Strategy

### Unit Tests

- Import resolution verification
- Health check endpoint functionality
- Process management utilities
- Status communication handlers

### Integration Tests

- Component startup sequences
- Service registration processes
- Inter-component communication
- Real-time status updates

### System Tests

- Full system launch scenarios
- Parallel launch performance
- Failure recovery procedures
- Cross-platform compatibility

### Performance Tests

- Launch time measurements
- Resource utilization during parallel startup
- WebSocket communication latency
- Health check response times

## Documentation Updates

### MUST Update Documentation

The following documentation **must** be updated as part of this sprint:

- Component startup procedures and dependencies
- Health check endpoint specifications
- Service registration process documentation
- Python launch system user guide
- UI status indicator documentation

### CAN Update Documentation

The following documentation **can** be updated if relevant:

- Component architecture overviews
- Troubleshooting guides
- Performance optimization recommendations
- Cross-platform deployment notes

### CANNOT Update without Approval

The following documentation **cannot** be updated without explicit approval:

- Core component API specifications
- Authentication and security procedures
- Database schema documentation

## Deployment Considerations

- Python launch scripts must be executable from any directory
- WebSocket endpoints must be accessible to UI components
- Configuration files must support different deployment environments
- Health check endpoints must not interfere with existing functionality

## Rollback Plan

If issues are encountered:

1. **Phase 1**: Revert import fixes if they break existing functionality
2. **Phase 3**: Fall back to bash scripts if Python scripts fail
3. **Phase 5**: Disable UI status features if WebSocket communication fails
4. **General**: All changes are additive; original functionality remains available

## Success Criteria

The implementation will be considered successful if:

- All components launch without import errors (100% success rate)
- System startup time is reduced by at least 50%
- Python scripts successfully replace bash scripts with equivalent functionality
- UI provides real-time component status with visual indicators
- Component registration with Hermes reaches 100%
- All health checks respond within defined timeouts
- Parallel launching works without resource conflicts

## References

- [SprintPlan.md](./SprintPlan.md) - High-level sprint goals and approach
- [ArchitecturalDecisions.md](./ArchitecturalDecisions.md) - Key architectural decisions
- [Debug Instrumentation Guidelines](/MetaData/TektonDocumentation/DeveloperGuides/Debugging/DebuggingInstrumentation.md)
- [Tekton Component Documentation](/MetaData/ComponentDocumentation/)
- [Single Port Architecture](/docs/SINGLE_PORT_ARCHITECTURE.md)