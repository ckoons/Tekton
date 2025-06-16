# MCP Integration Test Plan

This document outlines the test plan for the MCP Integration Sprint, which will focus on implementing and testing the Multimodal Cognitive Protocol (MCP) functionality across all Tekton components.

## Context

During the Launch Testing Sprint, we verified that all components successfully launch and respond to basic health checks. We also identified that while the Single Port Architecture has been implemented, there are issues with MCP service initialization and component registration that need to be addressed in this phase.

## Current Status

- **Basic Ports & Health Endpoints**: ✅ Working
- **MCP Capability Reporting**: ✅ Working via Hermes
- **MCP Service Initialization**: ❌ Not fully implemented ("MCP service not initialized" errors)
- **Component Registration**: ❌ Issues with 422 validation errors
- **Service Registry**: ❌ Empty responses from registry endpoints

## Test Plan

### Phase 1: MCP Service Initialization

1. **MCP Service Initialization**
   - Diagnose why Hermes MCP service is not fully initialized
   - Fix initialization sequence in Hermes MCP implementation
   - Test all MCP endpoints (/api/mcp/processors, /api/mcp/contexts, /api/mcp/tools)
   - Verify proper error handling during initialization

2. **Hermes MCP Endpoint Testing**
   - Test `/api/mcp/capabilities` - ✅ Already working
   - Test `/api/mcp/processors` - Fix "MCP service not initialized" errors
   - Test `/api/mcp/contexts` - Fix "MCP service not initialized" errors
   - Test `/api/mcp/tools` - Fix "MCP service not initialized" errors
   - Test `/api/mcp/process` - Implement and test basic processing

### Phase 2: Component Registration Protocol

1. **Registration Protocol Enhancement**
   - Analyze 422 errors during component registration
   - Update registration request formats to meet validation requirements
   - Standardize registration process across all components
   - Implement proper error handling with clear error messages

2. **Component Registration Testing**
   - Test Rhetor registration with Hermes
   - Test Engram registration with Hermes
   - Test other component registrations (Prometheus, Harmonia, etc.)
   - Verify components appear in the Hermes registry

### Phase 3: MCP End-to-End Testing

1. **MCP Request Routing**
   - Implement request routing from Hermes to appropriate components
   - Test routing based on modality and capability requirements
   - Verify cross-component requests work correctly
   - Measure performance and optimize routing

2. **MCP Processing End-to-End Tests**
   - Test text processing via MCP
   - Test code processing via MCP
   - Test image processing via MCP
   - Test structured data processing via MCP
   - Test multi-modal requests that require multiple components

### Phase 4: Service Discovery & Registry

1. **Registry Enhancement**
   - Fix empty responses from registry endpoints
   - Implement proper component capability discovery
   - Add health monitoring for registered services
   - Implement service filtering and querying

2. **Registry Testing**
   - Test service discovery by capability
   - Test service discovery by component type
   - Test health status monitoring
   - Test dynamic registration and unregistration

## Success Criteria

The MCP Integration will be considered successful when:

1. All components can register with Hermes without errors
2. The Hermes service registry properly shows all registered components
3. MCP services are properly initialized in Hermes
4. MCP requests can be routed to the appropriate components
5. End-to-end MCP processing works for all supported modalities
6. Components can be discovered through the service registry
7. Health status is properly tracked for all components

## Testing Tools

1. **Command Line Testing**
   ```bash
   # Test MCP capabilities
   curl -X POST http://localhost:8001/api/mcp/capabilities -H "Content-Type: application/json" -d '{}'
   
   # Test MCP processors
   curl -X POST http://localhost:8001/api/mcp/processors -H "Content-Type: application/json" -d '{}'
   
   # Test component registration
   curl -X POST http://localhost:8001/api/registry/services
   ```

2. **Integration Test Scripts**
   - Create automated test scripts for MCP functionality
   - Add integration tests for cross-component communication
   - Implement performance testing for MCP request routing

3. **Monitoring Tools**
   - Enhance tekton-status to show MCP service status
   - Add monitoring for component registration
   - Implement health dashboard for all services

## Timeline

- **Week 1**: MCP Service Initialization & Component Registration
- **Week 2**: MCP Request Routing & End-to-End Testing
- **Week 3**: Service Discovery & Registry Enhancement
- **Week 4**: Documentation, Performance Optimization, and Final Testing

## Documentation Deliverables

1. **MCP Integration Guide**: Comprehensive documentation on MCP implementation
2. **Component Registration Protocol**: Detailed specification for component registration
3. **Service Discovery API**: Documentation for the service discovery mechanism
4. **MCP Client Libraries**: Example client code for accessing MCP services