# Tekton Shared Component Utilities

**Last Updated:** April 27, 2025

## Overview

This document provides a comprehensive guide to the shared utilities available for Tekton components. These utilities implement standardized patterns for common operations, reducing code duplication and ensuring consistent behavior across the system.

## Table of Contents

1. [Benefits of Shared Utilities](#benefits-of-shared-utilities)
2. [Available Utilities](#available-utilities)
   - [HTTP Client (`tekton_http.py`)](#http-client-tekton_httppy)
   - [Configuration Management (`tekton_config.py`)](#configuration-management-tekton_configpy)
   - [Logging Setup (`tekton_logging.py`)](#logging-setup-tekton_loggingpy)
   - [WebSocket Management (`tekton_websocket.py`)](#websocket-management-tekton_websocketpy)
   - [Hermes Registration (`tekton_registration.py`)](#hermes-registration-tekton_registrationpy)
   - [Error Handling (`tekton_errors.py`)](#error-handling-tekton_errorspy)
   - [Component Lifecycle (`tekton_lifecycle.py`)](#component-lifecycle-tekton_lifecyclepy)
   - [Authentication (`tekton_auth.py`)](#authentication-tekton_authpy)
   - [Context Management (`tekton_context.py`)](#context-management-tekton_contextpy)
   - [CLI Argument Parsing (`tekton_cli.py`)](#cli-argument-parsing-tekton_clipy)
3. [Integration Guide](#integration-guide)
4. [Migration Best Practices](#migration-best-practices)
5. [Example Usage](#example-usage)

## Benefits of Shared Utilities

The shared utilities provide several key benefits:

1. **Reduced Duplication**: Eliminates duplicate code across components
2. **Consistent Behavior**: Ensures components behave consistently for common operations
3. **Improved Maintainability**: Centralizes implementation of common patterns
4. **Standardized Error Handling**: Provides a uniform approach to error management
5. **Enhanced Logging**: Implements consistent logging patterns
6. **Simplified Component Development**: Reduces the boilerplate needed for new components

## Available Utilities

### HTTP Client (`tekton_http.py`)

A standardized HTTP client for making requests to other Tekton components and external services, with consistent error handling, retries, and timeouts.

**Key Features**:
- Consistent error handling with standardized exceptions
- Automatic retries with configurable backoff
- Support for both synchronous and asynchronous usage
- Simplified creation of clients for Tekton components
- Standardized authentication header handling

**Example**:
```python
from tekton.utils.tekton_http import http_request, create_hermes_client

# Function-based interface
response = await http_request(
    method="GET",
    url="http://localhost:8001/api/components",
    headers={"Authorization": "Bearer token"}
)

# Client-based interface
hermes_client = create_hermes_client()
components = await hermes_client.get("/api/components")
```

### Configuration Management (`tekton_config.py`)

A unified configuration management system that loads from environment variables, files, and default values with type validation.

**Key Features**:
- Priority-based configuration loading (defaults → file → environment)
- Type validation and conversion
- Schema-based configuration validation
- Support for multiple file formats (JSON, YAML)
- Consistent environment variable handling

**Example**:
```python
from tekton.utils.tekton_config import TektonConfig, config_from_env

# Class-based interface
config = TektonConfig("mycomponent")
config.load_defaults({
    "port": 8000,
    "log_level": "INFO",
})
config.load_from_env()
port = config.get_int("port")

# Function-based interface
port = config_from_env("MYCOMPONENT_PORT", default=8000, value_type=int)
```

### Logging Setup (`tekton_logging.py`)

Standardized logging configuration with consistent formatting, levels, and handling across components.

**Key Features**:
- Consistent log format and levels
- Context and correlation ID tracking
- Log rotation support
- JSON formatting for machine-readable logs
- Thread-local context storage

**Example**:
```python
from tekton.utils.tekton_logging import setup_logging, get_logger

# Set up component logging
logger = setup_logging(
    "mycomponent", 
    log_level="DEBUG",
    log_file="/var/log/tekton/mycomponent.log",
    include_json=True
)

# Get a child logger for a specific module
module_logger = get_logger("mycomponent.module")

# Log with context
logger.info("Processing request", extra={"request_id": "123"})
```

### WebSocket Management (`tekton_websocket.py`)

Standardized WebSocket client and server implementations with connection management, reconnection logic, and error handling.

**Key Features**:
- Consistent connection management
- Automatic reconnection with backoff
- Standardized message format
- Integration with FastAPI for server-side WebSockets
- Connection tracking and broadcasting

**Example**:
```python
from tekton.utils.tekton_websocket import WebSocketClient

# Client usage
client = WebSocketClient(
    ws_url="ws://localhost:8001/ws", 
    on_message=lambda msg: print(f"Received: {msg}")
)

await client.connect()
await client.send_message({"type": "request", "id": "123", "action": "get_status"})
await client.close()
```

### Hermes Registration (`tekton_registration.py`)

Standardized component registration with Hermes, including capability declarations, heartbeat management, and dependency tracking.

**Key Features**:
- Consistent component registration
- Standardized capability declarations
- Automatic heartbeat management
- Health status reporting
- Graceful deregistration

**Example**:
```python
from tekton.utils.tekton_registration import TektonComponent, StandardCapabilities

# Register component
component = TektonComponent(
    component_id="mycomponent",
    component_name="My Component",
    component_type="service",
    version="1.0.0",
    capabilities=[
        StandardCapabilities.memory_storage(),
        StandardCapabilities.memory_query()
    ]
)

await component.register()

# Update status
await component.update_status(ComponentStatus.READY)

# Graceful shutdown
await component.unregister()
```

### Error Handling (`tekton_errors.py`)

Standardized error hierarchy and handling mechanisms for consistent error reporting and management.

**Key Features**:
- Comprehensive error hierarchy
- Standardized error creation and handling
- Context-aware error reporting
- Utility functions for common error patterns
- Integration with HTTP status codes

**Example**:
```python
from tekton.utils.tekton_errors import (
    TektonError,
    ConfigurationError,
    handle_exception
)

try:
    # Component logic
    if "required_param" not in config:
        raise ConfigurationError("Missing required parameter")
except Exception as e:
    # Generic error handler
    tekton_error = handle_exception(
        e, 
        component_id="mycomponent",
        re_raise=False
    )
    logger.error(f"Component error: {tekton_error}")
```

### Component Lifecycle (`tekton_lifecycle.py`)

Standardized component lifecycle management, including initialization, startup, shutdown, and health checking.

**Key Features**:
- Consistent component lifecycle
- Resource tracking and cleanup
- Standardized health checking
- Signal handling
- Integration with Hermes registration

**Example**:
```python
from tekton.utils.tekton_lifecycle import TektonLifecycle

class MyComponent(TektonLifecycle):
    async def initialize(self):
        # Initialize resources
        self.database = await self.track_resource(Database())
        return True
        
    async def start(self):
        # Start the component
        self.server = await self.track_resource(Server())
        return True
        
    async def stop(self):
        # Explicit shutdown logic (resource cleanup happens automatically)
        await self.database.flush()
        return True

# Run the component
component = MyComponent("mycomponent")
exit_code = await component.run()
```

### Authentication (`tekton_auth.py`)

Standardized authentication mechanisms, including token generation, validation, and permission checking.

**Key Features**:
- JWT token generation and validation
- API key management
- Permission system
- Integration with FastAPI
- Secure token handling

**Example**:
```python
from tekton.utils.tekton_auth import create_token, validate_token, Permission

# Create a token with permissions
token = create_token(
    subject="user123",
    permissions=[Permission.COMPONENT_READ, Permission.MEMORY_READ]
)

# Validate a token
try:
    payload = validate_token(
        token,
        required_permissions=[Permission.COMPONENT_READ]
    )
    user_id = payload["sub"]
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
```

### Context Management (`tekton_context.py`)

Standardized conversation context management for tracking conversation history, metadata, and state.

**Key Features**:
- Conversation context tracking
- Message history management
- Context serialization and persistence
- Thread-local context storage
- Integration with FastAPI

**Example**:
```python
from tekton.utils.tekton_context import ConversationContext, get_current_context

# Create a new context
context = ConversationContext(context_id="abc123")
context.add_message("user", "Hello, how are you?")
context.add_message("assistant", "I'm doing well, thank you!")

# Access in request handlers
def handle_request():
    context = get_current_context() or ConversationContext()
    context.add_message("user", "New message")
    return context.get_messages(limit=5)
```

### CLI Argument Parsing (`tekton_cli.py`)

Standardized command-line interface parsing with consistent help text, subcommand handling, and validation.

**Key Features**:
- Consistent help text formatting
- Subcommand support
- Standard argument patterns
- Integration with component lifecycle
- Common utility functions

**Example**:
```python
from tekton.utils.tekton_cli import TektonCLI

# Create CLI
cli = TektonCLI(
    component_id="mycomponent",
    description="My Component CLI",
    version="1.0.0"
)

# Add command handlers
@cli.command("start")
def start_command(args):
    print(f"Starting with config: {args.config_file}")
    # Component startup logic
    
@cli.command("stop")
def stop_command(args):
    print("Stopping component")
    # Component shutdown logic

# Run CLI
cli.run()
```

## Integration Guide

To integrate these shared utilities into your component:

1. **Import Required Utilities**: Import the utilities you need in your component code
2. **Replace Custom Implementations**: Identify any custom code that duplicates shared utility functionality and replace it
3. **Update Initialization**: Modify component initialization to use the standardized lifecycle
4. **Update Error Handling**: Adopt the standardized error hierarchy and handling patterns
5. **Update Configuration**: Use the standardized configuration system

For detailed integration instructions, see the [Component Integration Patterns](../Architecture/ComponentIntegrationPatterns.md) document.

## Migration Best Practices

When migrating an existing component to use shared utilities:

1. **Start with Core Utilities**: Begin with the basic utilities like logging and error handling
2. **Incremental Integration**: Migrate one utility at a time, testing thoroughly between changes
3. **Component-Specific Subclasses**: Create component-specific subclasses of shared utilities when needed
4. **Update Tests**: Update tests to account for the new utility implementations
5. **Document Changes**: Document any behavior changes that result from the migration

See the [Component Integration Patterns](../Architecture/ComponentIntegrationPatterns.md) for detailed migration guidance.

## Example Usage

### Basic Component Template

Here's a template for a basic component that uses the shared utilities:

```python
"""Example Tekton component using shared utilities."""

import asyncio
import logging

from tekton.utils.tekton_lifecycle import TektonLifecycle
from tekton.utils.tekton_config import TektonConfig
from tekton.utils.tekton_logging import setup_logging
from tekton.utils.tekton_http import HTTPClient
from tekton.utils.tekton_registration import StandardCapabilities
from tekton.utils.tekton_cli import TektonCLI


class MyComponent(TektonLifecycle):
    """Example Tekton component."""
    
    async def initialize(self):
        """Initialize the component."""
        # Set up configuration
        self.config = TektonConfig("mycomponent")
        self.config.load_defaults({
            "port": 8099,
            "log_level": "INFO",
        })
        
        # Load configuration from file and environment
        if hasattr(self, "config_file") and self.config_file:
            self.config.load_from_file(self.config_file)
        self.config.load_from_env()
        
        # Set up clients
        self.hermes_client = self.track_resource(HTTPClient(
            base_url=f"http://localhost:{self.config.get_int('hermes_port', 8001)}",
            component_id=self.component_id
        ))
        
        # Check for required configuration
        if not self.config.get("required_param"):
            self.logger.error("Missing required configuration: required_param")
            return False
        
        self.logger.info("Component initialized")
        return True
    
    async def start(self):
        """Start the component."""
        # Start server
        self.server = self.create_task(self._run_server)
        
        self.logger.info("Component started")
        return True
    
    async def stop(self):
        """Stop the component."""
        self.logger.info("Component stopping")
        return True
    
    async def health_check(self):
        """Check component health."""
        # Basic health check
        health_info = await super().health_check()
        
        # Add component-specific health info
        health_info["custom_metric"] = "value"
        
        return health_info
    
    async def _run_server(self):
        """Run the component server."""
        # Server implementation
        pass


# CLI implementation
def main():
    """Run the component CLI."""
    cli = TektonCLI(
        component_id="mycomponent",
        description="My Example Component",
        version="1.0.0"
    )
    
    @cli.command("start")
    def start_command(args):
        """Start the component."""
        # Initialize logging
        logger = setup_logging(
            "mycomponent",
            log_level=args.log_level,
            log_file=args.log_file
        )
        
        # Create and run component
        component = MyComponent(
            component_id="mycomponent",
            component_name="My Component",
            component_type="example",
            version="1.0.0",
            description="Example component using shared utilities",
            hermes_registration=True
        )
        
        # Add config file if specified
        if args.config_file:
            component.config_file = args.config_file
        
        # Run the component
        return asyncio.run(component.run())
    
    # Add command-line arguments
    start_command.parser.add_argument(
        "--log-file",
        help="Path to log file"
    )
    
    # Run CLI
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
```

For more detailed examples, see the examples directory in `tekton-core/tekton/utils/examples/`.