# YetAnotherMCP_Sprint - Sprint Plan

## Overview

This document outlines the high-level plan for the YetAnotherMCP_Sprint Development Sprint. It provides an overview of the goals, approach, and expected outcomes.

Tekton is an intelligent orchestration system that coordinates multiple CI models and resources to efficiently solve complex software engineering problems. This Development Sprint focuses on standardizing and fixing the Model Context Protocol (MCP) implementation across all Tekton components, with Hermes serving as the central MCP aggregator.

## Sprint Goals

The primary goals of this sprint are:

1. **Fix Hermes MCP Service**: Resolve the initialization bug in Hermes MCP service that's preventing proper functioning
2. **Standardize MCP Endpoints**: Establish `/api/mcp/v2` as the standard endpoint across all Tekton components
3. **Enhance Component Registration**: Update the registration process to include MCP tool registration
4. **Create Unified MCP Library**: Develop a shared MCP library that all components can use

## Business Value

This sprint delivers value by:

- **Simplified Integration**: Claude and other CI assistants can connect to a single MCP endpoint for all Tekton capabilities
- **Improved Reliability**: Standardized implementation eliminates inconsistencies and bugs
- **Enhanced Discoverability**: Tools from all components are discoverable through a single interface
- **Reduced Maintenance**: Shared code reduces duplication and makes future updates easier

## Current State Assessment

### Existing Implementation

Currently, the MCP implementation across Tekton components is inconsistent and has critical issues:

1. **Hermes MCP Service**: Not initializing properly due to a bug with awaiting a boolean value
2. **Endpoint Inconsistency**: Different components use different endpoint paths (`/mcp` vs. `/api/mcp/v2`)
3. **Registration Process**: Components register with Hermes but don't explicitly register their MCP tools
4. **Heartbeat Issues**: Heartbeats to `/api/heartbeat` are failing with 422 errors
5. **Duplicate Implementations**: Each component has its own MCP implementation without shared code

### Pain Points

- **Claude Integration Failure**: Claude can't connect to Hermes MCP service due to initialization issues
- **Tool Discovery**: There's no central registry of available MCP tools across components
- **Inconsistent Interfaces**: Different components have different MCP interfaces
- **Maintenance Challenges**: Changes to MCP implementation require updates to multiple components
- **Debug Difficulty**: Issues are hard to diagnose due to inconsistent implementation

## Proposed Approach

The approach is to standardize on a single MCP implementation pattern with Hermes as the central aggregator, fixing the current issues while establishing a clear standard for future development.

### Key Components Affected

- **Hermes**: Fix MCP service initialization, update MCP router to use `/api/mcp/v2`, enhance tool discovery
- **Shared Utils**: Update `hermes_registration.py` to handle MCP tool registration
- **All Components**: Update to use the standard MCP endpoint and registration process
- **Tekton Core**: Create a new shared MCP library for all components to use

### Technical Approach

1. **Fix Hermes MCP Service**: Correct the bug in the initialization code
2. **Create Shared MCP Library**: Develop a standard library in `tekton/mcp`
3. **Standardize Endpoints**: Update all components to use `/api/mcp/v2`
4. **Enhance Registration**: Update registration to include MCP tools
5. **Integrate with OneHeartbeat**: Ensure MCP registration works with the standardized heartbeat system

## Code Quality Requirements

### Debug Instrumentation

All code produced in this sprint **MUST** follow the [Debug Instrumentation Guidelines](/MetaData/TektonDocumentation/DeveloperGuides/Debugging/DebuggingInstrumentation.md):

- Frontend JavaScript must use conditional `TektonDebug` calls
- Backend Python must use the `debug_log` utility and `@log_function` decorators
- All debug calls must include appropriate component names and log levels
- Error handling must include contextual debug information

This instrumentation will enable efficient debugging and diagnostics without impacting performance when disabled.

### Documentation

Code must be documented according to the following guidelines:

- Class and method documentation with clear purpose statements
- API contracts and parameter descriptions
- Requirements for component initialization
- Error handling strategy

### Testing

The implementation must include appropriate tests:

- Unit tests for MCP service initialization and operation
- Integration tests for MCP tool registration and discovery
- End-to-end tests for Claude integration

## Out of Scope

The following items are explicitly out of scope for this sprint:

- Adding new MCP tools to components (focus is on infrastructure)
- Changing the core MCP protocol specification
- Major refactoring of components beyond MCP integration
- Implementing new component features unrelated to MCP

## Dependencies

This sprint has the following dependencies:

- OneHeartbeat_Sprint (integration with standardized heartbeat system)
- Existing FastMCP implementation in various components
- Claude MCP client capabilities

## Timeline and Phases

This sprint is planned to be completed in 3 phases:

### Phase 1: Fix Core Issues
- **Duration**: 1 week
- **Focus**: Fix Hermes MCP service initialization and update endpoints
- **Key Deliverables**: 
  - Fixed Hermes MCP service
  - Updated MCP endpoints in Hermes
  - Test script for MCP connectivity

### Phase 2: Standardize Implementation
- **Duration**: 1 week
- **Focus**: Create shared MCP library and update component registration
- **Key Deliverables**:
  - Shared MCP library in `tekton/mcp`
  - Updated `hermes_registration.py`
  - Component registration with MCP tools

### Phase 3: Integration and Testing
- **Duration**: 1 week
- **Focus**: Update all components to use the standard and test integration
- **Key Deliverables**:
  - Updated component MCP implementations
  - Updated `install_tekton_mcps.sh` script
  - Integration tests with Claude
  - Documentation of new MCP architecture

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Hermes bug is more complex than expected | High | Medium | Prepare fallback implementation with proxy if needed |
| Component updates cause regressions | High | Medium | Implement comprehensive test suite and rollback plan |
| Integration with OneHeartbeat conflicts | Medium | Low | Coordinate with OneHeartbeat sprint to ensure compatibility |
| Claude MCP client incompatibility | High | Low | Test Claude integration early and adapt as needed |

## Success Criteria

This sprint will be considered successful if:

- Hermes MCP service initializes and operates correctly
- All components use the standard `/api/mcp/v2` endpoint
- Components can register their MCP tools with Hermes
- Claude can connect to Hermes MCP and access tools from all components
- Shared MCP library is used by at least 3 key components
- All code follows the Debug Instrumentation Guidelines
- Documentation is complete and accurate
- Tests pass with 80% coverage

## Key Stakeholders

- **Casey**: Human-in-the-loop project manager
- **Claude**: CI pair programmer and implementation partner
- **Component Maintainers**: Responsible for component-specific MCP implementation

## References

- [MCP_INTEGRATION.md](/Hermes/MCP_INTEGRATION.md)
- [Hermes Core MCP Service](/Hermes/hermes/core/mcp_service.py)
- [Shared Utils Registration](/shared/utils/hermes_registration.py)
- [Engram FastMCP Server](/Engram/engram/api/fastmcp_server.py)
- [Rhetor MCP Implementation](/Rhetor/README.md)