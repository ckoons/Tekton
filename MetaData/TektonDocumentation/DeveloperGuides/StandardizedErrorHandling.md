# Tekton Standardized Error Handling

**Last Updated:** April 27, 2025

## Overview

This document describes the standardized error handling approach implemented across Tekton components. A consistent error handling strategy is essential for reliable system behavior, effective debugging, and seamless component integration.

## Table of Contents

1. [Error Hierarchy](#error-hierarchy)
2. [Error Categories](#error-categories)
3. [Error Handling Patterns](#error-handling-patterns)
4. [HTTP Error Integration](#http-error-integration)
5. [Component-Specific Errors](#component-specific-errors)
6. [Logging and Reporting](#logging-and-reporting)
7. [Recovery and Fallback Strategies](#recovery-and-fallback-strategies)
8. [Best Practices](#best-practices)
9. [Migration Guide](#migration-guide)

## Error Hierarchy

The Tekton error system is built around a hierarchical structure of error classes:

```
TektonError (base class)
├── ConfigurationError
│   ├── ConfigKeyError
│   ├── ConfigValueError
│   └── ConfigurationFileError
├── ConnectionError
│   ├── ServiceUnavailableError
│   └── ServiceTimeoutError
├── AuthenticationError
│   ├── TokenExpiredError
│   └── InvalidCredentialsError
├── AuthorizationError
├── TektonHTTPError
│   ├── TektonConnectionError
│   ├── TektonTimeoutError
│   ├── TektonAuthenticationError
│   ├── TektonAuthorizationError
│   ├── TektonNotFoundError
│   ├── TektonServerError
│   ├── TektonClientError
│   └── TektonRequestError
├── ComponentError
│   ├── ComponentNotFoundError
│   ├── ComponentNotReadyError
│   ├── ComponentUnavailableError
│   ├── CapabilityNotFoundError
│   └── CapabilityInvocationError
├── DataError
│   ├── DataValidationError
│   ├── DataNotFoundError
│   └── DataConflictError
├── LifecycleError
│   ├── InitializationError
│   └── ShutdownError
├── ResourceError
│   ├── ResourceUnavailableError
│   ├── ResourceLimitExceededError
│   └── ResourceConflictError
├── ContextError
│   ├── ContextNotFoundError
│   └── ContextValidationError
└── WebSocketError
    ├── WebSocketConnectionError
    ├── WebSocketProtocolError
    └── WebSocketClosedError
```

This hierarchy allows for specific error handling at different levels of abstraction.

## Error Categories

Tekton errors are grouped into several main categories:

1. **Configuration Errors**: Issues with component configuration
2. **Connection Errors**: Problems connecting to other components or services
3. **Authentication/Authorization Errors**: Security-related errors
4. **HTTP Errors**: Issues with HTTP requests and responses
5. **Component Errors**: Problems with specific Tekton components
6. **Data Errors**: Issues with data validation, storage, or retrieval
7. **Lifecycle Errors**: Problems with component lifecycle management
8. **Resource Errors**: Issues with system resources
9. **Context Errors**: Problems with conversation or request contexts
10. **WebSocket Errors**: Issues with WebSocket connections

## Error Handling Patterns

### Basic Error Handling

```python
from tekton.utils.tekton_errors import TektonError, ConfigurationError

try:
    # Component logic
    if "required_param" not in config:
        raise ConfigurationError("Missing required parameter")
except TektonError as e:
    # Handle Tekton-specific errors
    logger.error(f"Configuration error: {e}")
    # Take appropriate action
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Unexpected error: {e}")
    # Take fallback action
```

### Utility-Based Error Handling

```python
from tekton.utils.tekton_errors import (
    handle_exception,
    TektonError,
    ConfigurationError
)

try:
    # Component logic
except Exception as e:
    # Convert to appropriate Tekton error
    tekton_error = handle_exception(
        e,
        component_id="mycomponent",
        default_error_cls=ConfigurationError,
        default_message="Component configuration error",
        re_raise=False
    )
    logger.error(f"Component error: {tekton_error}")
```

### Safe Execution Pattern

```python
from tekton.utils.tekton_errors import safe_execute, ConnectionError

# Execute with automatic error handling
result = safe_execute(
    fetch_data,
    url, 
    auth_token,
    default=default_data,
    error_cls=ConnectionError,
    error_message="Failed to fetch data",
    component_id="mycomponent",
    log_error=True,
    re_raise=False
)
```

## HTTP Error Integration

The error hierarchy integrates with HTTP status codes for consistent error responses:

| HTTP Status | Tekton Error Class | Description |
|-------------|-------------------|-------------|
| 400 | TektonRequestError | Bad request |
| 401 | TektonAuthenticationError | Authentication failed |
| 403 | TektonAuthorizationError | Permission denied |
| 404 | TektonNotFoundError | Resource not found |
| 408 | TektonTimeoutError | Request timeout |
| 409 | DataConflictError | Resource conflict |
| 500 | TektonServerError | Server error |
| 503 | ServiceUnavailableError | Service unavailable |

### HTTP Response Example

```python
from fastapi import HTTPException
from tekton.utils.tekton_errors import (
    TektonError,
    TektonNotFoundError,
    create_error_response
)

@app.get("/api/resource/{resource_id}")
async def get_resource(resource_id: str):
    try:
        # Component logic
        resource = await fetch_resource(resource_id)
        if not resource:
            raise TektonNotFoundError(f"Resource not found: {resource_id}")
        return resource
    except TektonNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TektonError as e:
        # Create standardized error response
        error_response = create_error_response(
            e,
            component_id="mycomponent",
            include_traceback=is_debug_mode()
        )
        raise HTTPException(status_code=500, detail=error_response)
```

## Component-Specific Errors

Components can extend the error hierarchy with component-specific errors:

```python
from tekton.utils.tekton_errors import TektonError, DataError

# Component-specific error
class EngineError(TektonError):
    """Base class for engine-related errors."""
    pass

class EngineExecutionError(EngineError):
    """Raised when engine execution fails."""
    pass

class InvalidInputError(DataError):
    """Raised when input data is invalid."""
    pass
```

## Logging and Reporting

The error handling system integrates with Tekton's logging system:

```python
from tekton.utils.tekton_errors import TektonError

# Errors have built-in logging capability
try:
    # Component logic
except TektonError as e:
    # Log with proper context and level
    e.log(logger, level=logging.ERROR)
    
    # Create dictionary representation for reporting
    error_dict = e.to_dict()
    await report_error(error_dict)
```

## Recovery and Fallback Strategies

Tekton implements several error recovery and fallback strategies:

### Circuit Breaking

```python
from tekton.utils.tekton_errors import ConnectionError, ServiceUnavailableError

# Track consecutive failures
failure_count = 0
failure_threshold = 3

try:
    # Service call
    response = await service.call()
    # Reset failure count on success
    failure_count = 0
    return response
except (ConnectionError, ServiceUnavailableError) as e:
    failure_count += 1
    if failure_count >= failure_threshold:
        # Circuit is open, use fallback
        return fallback_response()
    # Re-raise if below threshold
    raise
```

### Graceful Degradation

```python
try:
    # Primary functionality
    result = await primary_function()
    return result
except TektonError as e:
    logger.warning(f"Primary function failed: {e}, falling back to alternate")
    try:
        # Fallback functionality
        result = await alternate_function()
        return result
    except TektonError as fallback_error:
        logger.error(f"Fallback also failed: {fallback_error}")
        # Return minimal functionality
        return minimal_response()
```

### Automatic Retry

```python
from tekton.utils.tekton_errors import ConnectionError, ServiceTimeoutError

max_retries = 3
retry_delay = 1.0  # seconds

for attempt in range(max_retries):
    try:
        # Service call
        return await service.call()
    except (ConnectionError, ServiceTimeoutError) as e:
        if attempt < max_retries - 1:
            logger.warning(f"Attempt {attempt+1} failed: {e}, retrying...")
            await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
        else:
            logger.error(f"All retry attempts failed: {e}")
            raise
```

## Best Practices

1. **Always Use Tekton Error Classes**: Extend the base `TektonError` for all component-specific errors
2. **Include Component Context**: Always include the component ID when creating errors
3. **Provide Meaningful Messages**: Error messages should be clear, concise, and actionable
4. **Handle Errors at the Right Level**: Don't catch errors too early or too late
5. **Log with Appropriate Levels**: Use the right log level for different error severity
6. **Implement Recovery Mechanisms**: Use circuit breaking, retries, and fallbacks where appropriate
7. **Don't Silently Fail**: Always log, report, or re-raise errors
8. **Use the Standard Hierarchy**: Place new errors in the appropriate category
9. **Include Relevant Details**: Add useful context to error details for debugging
10. **Don't Expose Sensitive Information**: Redact passwords, tokens, and other sensitive data

## Migration Guide

To migrate existing error handling to the standardized approach:

1. **Identify Existing Errors**: Map custom exception classes to the Tekton error hierarchy
2. **Replace Custom Classes**: Update code to use the appropriate Tekton error classes
3. **Update Handler Code**: Modify catch blocks to handle the Tekton error hierarchy
4. **Add Context Information**: Include component ID and relevant details in error creation
5. **Update Error Responses**: Standardize API error responses using `create_error_response`
6. **Implement Recovery Patterns**: Add appropriate recovery mechanisms
7. **Update Documentation**: Document any error handling changes
8. **Update Tests**: Modify tests to expect the new error classes

### Example Migration

Before:
```python
class MyComponentError(Exception):
    pass

class ConfigError(MyComponentError):
    pass

try:
    if not config_file.exists():
        raise ConfigError("Configuration file not found")
except ConfigError as e:
    logger.error(f"Configuration error: {e}")
    return None
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return None
```

After:
```python
from tekton.utils.tekton_errors import (
    ConfigurationFileError,
    handle_exception
)

try:
    if not config_file.exists():
        raise ConfigurationFileError(
            f"Configuration file not found: {config_file}",
            component_id="mycomponent"
        )
except Exception as e:
    error = handle_exception(
        e,
        component_id="mycomponent",
        re_raise=False
    )
    error.log(logger)
    return None
```