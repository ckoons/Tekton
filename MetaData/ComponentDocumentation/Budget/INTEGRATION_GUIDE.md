# Budget Component Integration Guide

This guide describes how to integrate the Budget component with other Tekton components and external systems.

## Overview

The Budget component is Tekton's centralized system for managing LLM token allocations and cost tracking. It provides these key capabilities:

1. **Budget Management**: Creation and management of budgets with limits and policies
2. **Allocation System**: Allocating tokens to contexts, components, and operations
3. **Usage Tracking**: Recording and analyzing token usage and costs
4. **Price Monitoring**: Automatically tracking provider pricing changes
5. **Reporting**: Generating reports on usage and costs
6. **Alerting**: Notifying users of budget events and issues

## Single Port Architecture

Budget follows Tekton's Single Port Architecture pattern, meaning all services are exposed through a single HTTP port.

### Port Configuration

Budget uses port 8013 by default, following the [Tekton port assignment standards](../../config/port_assignments.md). The port can be configured through the `BUDGET_PORT` environment variable.

### URL Paths

Budget organizes its endpoints following the standard Tekton URL path conventions:

- **HTTP API**: `http://hostname:8013/api/...`
- **WebSocket**: `ws://hostname:8013/ws/...` (when implemented)
- **Events**: `http://hostname:8013/events/...` (when implemented)
- **Health Check**: `http://hostname:8013/health`

## Hermes Integration

Budget automatically registers with the Hermes service registry on startup, enabling other components to discover its capabilities.

### Registration Process

1. During startup, Budget registers itself with Hermes by calling the `/registration/register` endpoint
2. The registration includes component details, capabilities, and endpoint information
3. Budget establishes a heartbeat with Hermes to maintain its registration
4. On shutdown, Budget unregisters from Hermes

### Component Capabilities

Budget registers the following capabilities with Hermes:

- `budget_management`: Manage token and cost budgets for LLM usage
- `allocation`: Allocate tokens from a budget
- `usage_tracking`: Track token and cost usage
- `pricing`: Manage and retrieve provider pricing information
- `reporting`: Generate budget usage reports

### Registration Config

If Hermes's HTTP API is unavailable, Budget will attempt to register using a file-based registration mechanism for development environments, creating a JSON file in the `Hermes/registrations` directory.

## API Integration

Other components can integrate with Budget through its REST API.

### Client Libraries

Budget provides client libraries to simplify integration:

- **Apollo Integration**: `/Budget/budget/adapters/apollo.py` provides Apollo-specific integration
- **Standard Client**: `/Budget/client/budget_client.py` (to be implemented)

### API Endpoints

The main API endpoints are:

- `/api/budgets`: Budget management
- `/api/policies`: Budget policy management
- `/api/allocations`: Token allocation
- `/api/usage`: Usage tracking and reporting
- `/api/reports`: Reporting functionality
- `/api/alerts`: Budget alerts
- `/api/prices`: Provider pricing

## Environment Variables

Budget supports the following environment variables for configuration:

- `BUDGET_PORT`: HTTP port (default: 8013)
- `BUDGET_HOST`: Hostname for constructing endpoint URL (default: localhost)
- `BUDGET_VERSION`: Component version (default: 0.1.0)
- `HERMES_URL`: Hermes service registry URL (default: http://localhost:8001/api)

## Testing Integration

To test the integration with Budget:

1. Start Hermes: `./run_hermes.sh`
2. Start Budget: `cd Budget && ./run_budget.sh`
3. Verify registration: `curl http://localhost:8001/api/registration/services`
4. Test Budget API: `curl http://localhost:8013/health`

## Example Integration

```python
import requests

# Allocate tokens
allocation_response = requests.post(
    "http://localhost:8013/api/allocations",
    json={
        "context_id": "my-context-123",
        "component": "my-component",
        "tokens_allocated": 1000,
        "tier": "REMOTE_HEAVYWEIGHT",
        "provider": "anthropic",
        "model": "claude-3-opus-20240229"
    }
)
allocation = allocation_response.json()

# Record usage
requests.post(
    "http://localhost:8013/api/usage/record",
    json={
        "context_id": "my-context-123",
        "allocation_id": allocation["allocation_id"],
        "component": "my-component",
        "provider": "anthropic",
        "model": "claude-3-opus-20240229",
        "input_tokens": 100,
        "output_tokens": 250
    }
)
```