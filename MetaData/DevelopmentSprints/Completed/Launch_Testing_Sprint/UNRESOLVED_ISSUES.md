# Unresolved Issues in Tekton Components

This document outlines the key unresolved issues identified during the Launch Testing Sprint. These issues should be addressed in the next development sprint.

## 1. Component Registration Issues

Components are encountering errors when attempting to register with Hermes:

### 1.1 Component ID Format Validation

```
ERROR - Invalid component configuration:
ERROR -   - Component ID must be alphanumeric (can include underscores)
```

**Root Cause**:
- The component ID format validation in Hermes is stricter than the actual component IDs being used
- Some component IDs include characters like periods (e.g., "engram.memory") or hyphens that don't pass validation
- The validation expects alphanumeric IDs, but the examples and tests use IDs with special characters

**Affected Components**:
- Engram
- Rhetor
- Tekton Core
- Potentially all components

**Recommended Fix**:
1. Standardize component ID format across all components (alphanumeric with optional underscores)
2. Update component configuration files to use the standardized format
3. Update validation logic to match the intended format (if periods or hyphens are meant to be allowed)

### 1.2 Registration Request Validation (422 Errors)

Components encounter 422 validation errors when sending registration requests to Hermes:

```
ERROR - Failed to register component: 422
ERROR - Failed to register component rhetor
```

**Root Cause**:
- Mismatch between the request format sent by components and the expected model format in Hermes
- The `ComponentRegistrationRequest` Pydantic model in Hermes has specific field requirements
- Inconsistencies between YAML configuration files and JSON registration requests

**Affected Components**:
- Rhetor
- Engram
- Potentially all components

**Recommended Fix**:
1. Standardize the registration request format across all components
2. Ensure all required fields (`name`, `version`, `type`, `endpoint`) are included
3. Fix any field name inconsistencies (e.g., `component_type` vs `type`)
4. Add better error reporting to identify specific validation issues

## 2. MCP Service Initialization

The MCP service in Hermes is not fully initialized, causing errors when accessing MCP endpoints:

```
{"detail":"MCP service not initialized"}
```

**Root Cause**:
- MCP service depends on other services (ServiceRegistry, MessageBus) that may not be fully initialized
- The initialization sequence may be failing or skipped under certain conditions
- Database MCP server might not be properly started or connected

**Affected Components**:
- Hermes MCP endpoints (`/api/mcp/processors`, `/api/mcp/contexts`, `/api/mcp/tools`)
- Any component trying to use these endpoints

**Recommended Fix**:
1. Fix the MCP service initialization sequence in Hermes
2. Ensure all required dependencies are properly initialized
3. Add better error handling and reporting during initialization
4. Implement proper status checking for MCP service

## 3. HTTP Response Issues

Some components are running but returning errors or not found responses:

### 3.1 Rhetor Root Endpoint 500 Error

Rhetor returns a 500 Internal Server Error on its root endpoint:

```
AttributeError: 'TemplateManager' object has no attribute 'get_categories'
```

**Root Cause**:
- The root endpoint is trying to call `template_manager.get_categories()` which doesn't exist
- Missing implementation in the TemplateManager class
- Possibly a mismatch between the API implementation and the actual class implementation

**Recommended Fix**:
1. Implement the missing `get_categories()` method in TemplateManager
2. Update the root endpoint to handle cases where methods may not be available
3. Add proper error handling in the endpoint

### 3.2 Harmonia 404 Not Found

Harmonia returns a 404 Not Found for its root endpoint:

```
INFO:     127.0.0.1:51945 - "GET / HTTP/1.1" 404 Not Found
```

**Root Cause**:
- The root endpoint (`/`) is not implemented or registered in the FastAPI app
- The application might be expecting requests to `/api/` or another path
- Possible mismatch with the Single Port Architecture pattern

**Recommended Fix**:
1. Implement a proper root endpoint (`/`) in Harmonia
2. Ensure the endpoint follows the Single Port Architecture pattern
3. Add a redirect to the API documentation if appropriate

## 4. Service Registry Empty Responses

The Hermes service registry is not showing any registered components:

```
INFO: No services currently registered with Hermes
```

**Root Cause**:
- Components are failing to register due to the issues above
- The service registry might not be properly initialized
- Possible mismatch between the API paths used for registration and querying

**Recommended Fix**:
1. Fix the component registration issues
2. Ensure the service registry is properly initialized
3. Verify the API paths for registration and querying
4. Add better debugging for the registration process

## 5. Implementation Inconsistencies

There are inconsistencies in how components implement the Single Port Architecture:

**Root Cause**:
- Different interpretation of the Single Port Architecture pattern
- Incomplete implementation of standardized endpoints
- Lack of comprehensive documentation on the expected implementation

**Recommended Fix**:
1. Create a detailed implementation guide for the Single Port Architecture
2. Standardize endpoint paths across all components (`/`, `/health`, `/api/*`, `/ws/*`)
3. Implement consistent error handling and response formats
4. Add validation tests for architecture compliance

## Next Steps

These issues should be addressed in the MCP Integration Sprint as outlined in the [TEST_PLAN.md](../MCP_Integration_Sprint/TEST_PLAN.md) document. The main focus areas should be:

1. Fix component registration format and validation
2. Complete MCP service initialization in Hermes
3. Implement missing endpoints in components
4. Standardize the Single Port Architecture implementation
5. Add comprehensive testing for cross-component communication