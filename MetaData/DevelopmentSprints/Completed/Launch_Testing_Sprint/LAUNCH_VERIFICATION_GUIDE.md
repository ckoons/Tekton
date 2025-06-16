# Component Launch Verification Guide

This guide provides a systematic approach to verifying Tekton component launch functionality after the implementation of the Single Port Architecture.

## Verification Process Overview

1. **Launch Component**: Use `tekton-launch` to start the component
2. **Check Base Endpoints**: Test root and health endpoints
3. **Check API Endpoints**: Test critical API functionality 
4. **Verify Hermes Registration**: Confirm component is properly registered
5. **Test Cross-Component Communication**: Ensure components can communicate
6. **Document Status**: Update implementation summary with results

## Detailed Steps for Each Component

### 1. Engram Memory System (Port 8000)

```bash
# Launch Engram
./scripts/tekton-launch --components engram --no-ui

# Check root endpoint
curl http://localhost:8000

# Check health endpoint
curl http://localhost:8000/health

# Try adding a memory
curl -X POST http://localhost:8000/memory \
  -H "Content-Type: application/json" \
  -d '{"content": "Test memory", "namespace": "test"}'

# Check Hermes registration
curl -X POST http://localhost:8001/api/query \
  -H "Content-Type: application/json" \
  -d '{"component_type": "memory"}'
```

Expected results:
- Root endpoint returns service information
- Health endpoint returns {"status": "ok", ...} with storage info
- Memory endpoint successfully stores data
- Component shows up in Hermes registry

### 2. Hermes Messaging System (Port 8001)

```bash
# Launch Hermes
./scripts/tekton-launch --components hermes --no-ui

# Check root endpoint
curl http://localhost:8001

# Check health endpoint
curl http://localhost:8001/health

# Check API docs
curl http://localhost:8001/api/docs

# Test service registry
curl -X POST http://localhost:8001/api/query \
  -H "Content-Type: application/json" \
  -d '{}'
```

Expected results:
- Root endpoint returns welcome message
- Health endpoint shows all components healthy
- API docs returns OpenAPI documentation
- Query endpoint returns list of registered services

### 3. Rhetor LLM Management (Port 8003) 

```bash
# Launch Rhetor
./scripts/tekton-launch --components rhetor --no-ui

# Check root endpoint
curl http://localhost:8003

# Check health endpoint
curl http://localhost:8003/health

# Get available providers
curl http://localhost:8003/api/providers

# Check Hermes registration
curl -X POST http://localhost:8001/api/query \
  -H "Content-Type: application/json" \
  -d '{"component_type": "llm_management"}'
```

Expected results:
- Root endpoint returns service information
- Health endpoint shows status as healthy
- Providers endpoint lists available LLM providers
- Component shows up in Hermes registry

### 4. Prometheus Planning System (Port 8006)

```bash
# Launch Prometheus
./scripts/tekton-launch --components prometheus --no-ui

# Check root endpoint
curl http://localhost:8006

# Check health endpoint
curl http://localhost:8006/health

# Get improvement suggestions
curl -X GET "http://localhost:8006/api/suggestions?source_type=project&source_id=test&limit=2"

# Check Hermes registration
curl -X POST http://localhost:8001/api/query \
  -H "Content-Type: application/json" \
  -d '{"component_type": "planning"}'
```

Expected results:
- Root endpoint returns service information
- Health endpoint shows status as healthy
- API endpoint returns suggestions (may be empty)
- Component shows up in Hermes registry

### 5. Harmonia Workflow System (Port 8007)

```bash
# Launch Harmonia
./scripts/tekton-launch --components harmonia --no-ui

# Check root endpoint
curl http://localhost:8007

# Check health endpoint
curl http://localhost:8007/health

# Get workflows
curl http://localhost:8007/api/workflows

# Check Hermes registration
curl -X POST http://localhost:8001/api/query \
  -H "Content-Type: application/json" \
  -d '{"component_type": "workflow"}'
```

Expected results:
- Root endpoint returns service information
- Health endpoint shows status as healthy
- Workflows endpoint returns list (may be empty)
- Component shows up in Hermes registry

### 6. Telos Requirements System (Port 8008)

```bash
# Launch Telos
./scripts/tekton-launch --components telos --no-ui

# Check root endpoint
curl http://localhost:8008

# Check health endpoint
curl http://localhost:8008/health

# Get requirements
curl http://localhost:8008/api/requirements

# Check Hermes registration
curl -X POST http://localhost:8001/api/query \
  -H "Content-Type: application/json" \
  -d '{"component_type": "requirements"}'
```

Expected results:
- Root endpoint returns service information
- Health endpoint shows status as healthy
- Requirements endpoint returns list (may be empty)
- Component shows up in Hermes registry

### 7. Synthesis Execution Engine (Port 8009)

```bash
# Launch Synthesis
./scripts/tekton-launch --components synthesis --no-ui

# Check root endpoint
curl http://localhost:8009

# Check health endpoint
curl http://localhost:8009/health

# Get executions
curl http://localhost:8009/api/executions

# Check Hermes registration
curl -X POST http://localhost:8001/api/query \
  -H "Content-Type: application/json" \
  -d '{"component_type": "execution"}'
```

Expected results:
- Root endpoint returns service information
- Health endpoint shows status as healthy
- Executions endpoint returns list (may be empty)
- Component shows up in Hermes registry

## Troubleshooting Common Issues

### 1. Component Fails to Launch

- Check log file in `~/.tekton/logs/{component}.log`
- Verify port is available with `lsof -i :{port}`
- Check for any leftover processes with `ps aux | grep {component}`

### 2. Component Launches But Health Endpoint Fails

- Inspect implementation of health endpoint in component's code
- Check for missing methods referenced in health check
- Verify proper async implementation for async health checks

### 3. Hermes Registration Fails

- Verify component ID format (should be alphanumeric with optional underscores)
- Check component YAML configuration files
- Ensure Hermes is running before other components

### 4. API Endpoints Not Working

- Verify correct path structure (e.g., `/api/` prefix)
- Check for JSON format errors in requests
- Look for dependency or import issues in component code

## Updating Documentation

After verifying each component, update the implementation summary with the results:

1. Update component status in the Testing Results table
2. Add notes about any issues or fixes
3. Update Key Achievements section with successful implementations
4. Document any remaining issues for future work

By following this guide, you can systematically verify that all Tekton components are properly implementing the Single Port Architecture and launching correctly.