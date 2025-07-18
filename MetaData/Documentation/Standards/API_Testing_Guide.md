# API Testing Guide

## Overview

This guide provides testing standards and patterns for Tekton component APIs following the new consistency standards.

## Required Test Coverage

### 1. Infrastructure Endpoints
Every component must test:
- Root endpoint (`/`)
- Health check (`/health`)
- Ready check (`/ready`)
- Status endpoint (`/status`)
- Discovery endpoint (`/api/v1/discovery`)

### 2. Business Logic Endpoints
- All CRUD operations
- Error cases (404, 400, 500)
- Input validation
- Response format validation

### 3. Integration Tests
- Hermes registration
- Component startup/shutdown
- MCP tool functionality
- WebSocket connections (if applicable)

## Test Structure

### Basic Test Setup
```python
import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient

from mycomponent.api.app import app

# Async client for async tests
@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

# Sync client for simple tests  
@pytest.fixture
def client():
    return TestClient(app)
```

### Testing Infrastructure Endpoints

#### Root Endpoint Test
```python
def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "MyComponent"
    assert data["version"] == "0.1.0"
    assert data["docs"] == "/api/v1/docs"
```

#### Health Check Test
```python
@pytest.mark.asyncio
async def test_health_endpoint(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] in ["healthy", "degraded", "unhealthy"]
    assert data["component"] == "mycomponent"
    assert data["version"] == "0.1.0"
    assert "timestamp" in data
    assert isinstance(data["registered"], bool)
```

#### Ready Check Test
```python
@pytest.mark.asyncio
async def test_ready_endpoint(async_client):
    response = await async_client.get("/ready")
    assert response.status_code == 200
    
    data = response.json()
    assert "ready" in data
    assert data["component"] == "MyComponent"
    assert data["version"] == "0.1.0"
    assert "uptime" in data
```

#### Discovery Endpoint Test
```python
@pytest.mark.asyncio
async def test_discovery_endpoint(async_client):
    response = await async_client.get("/api/v1/discovery")
    assert response.status_code == 200
    
    data = response.json()
    assert data["component"] == "MyComponent"
    assert data["version"] == "0.1.0"
    assert len(data["endpoints"]) > 0
    assert len(data["capabilities"]) > 0
    
    # Verify endpoint structure
    for endpoint in data["endpoints"]:
        assert "path" in endpoint
        assert "method" in endpoint
        assert "description" in endpoint
```

### Testing Business Logic Endpoints

#### GET Collection Test
```python
@pytest.mark.asyncio
async def test_list_resources(async_client):
    response = await async_client.get("/api/v1/resources")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
```

#### POST Create Test
```python
@pytest.mark.asyncio
async def test_create_resource(async_client):
    payload = {
        "name": "Test Resource",
        "type": "test"
    }
    
    response = await async_client.post(
        "/api/v1/resources",
        json=payload
    )
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == payload["name"]
    assert "id" in data
```

#### Error Case Tests
```python
@pytest.mark.asyncio
async def test_resource_not_found(async_client):
    response = await async_client.get("/api/v1/resources/nonexistent")
    assert response.status_code == 404
    
    data = response.json()
    assert "error" in data
    assert data["component"] == "mycomponent"

@pytest.mark.asyncio
async def test_invalid_input(async_client):
    response = await async_client.post(
        "/api/v1/resources",
        json={"invalid": "data"}
    )
    assert response.status_code == 422
```

### Testing MCP Endpoints

```python
@pytest.mark.asyncio
async def test_mcp_tools_list(async_client):
    response = await async_client.post("/api/mcp/v2/tools/list")
    assert response.status_code == 200
    
    data = response.json()
    assert "tools" in data
    assert len(data["tools"]) > 0

@pytest.mark.asyncio
async def test_mcp_tool_call(async_client):
    payload = {
        "name": "test_tool",
        "arguments": {"input": "test"}
    }
    
    response = await async_client.post(
        "/api/mcp/v2/tools/call",
        json=payload
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "content" in data
    assert isinstance(data["content"], list)
```

### Testing Component Lifecycle

```python
@pytest.mark.asyncio
async def test_component_startup_shutdown():
    """Test full component lifecycle"""
    from mycomponent.api.app import lifespan, app
    
    # Test startup
    async with lifespan(app):
        # Component should be initialized
        assert hasattr(app.state, "connection_manager")
        
        # Test operations while running
        client = AsyncClient(app=app, base_url="http://test")
        response = await client.get("/health")
        assert response.status_code == 200
    
    # After exiting context, component should be shut down
    # Verify cleanup occurred
```

## Mock Patterns

### Mocking Hermes Registration
```python
@pytest.fixture
def mock_hermes_registration(monkeypatch):
    async def mock_register(*args, **kwargs):
        return True
    
    async def mock_deregister(*args, **kwargs):
        return True
    
    class MockHermesRegistration:
        is_registered = True
        register_component = mock_register
        deregister = mock_deregister
    
    monkeypatch.setattr(
        "mycomponent.api.app.HermesRegistration",
        MockHermesRegistration
    )
```

### Mocking External Services
```python
@pytest.fixture
def mock_external_service(monkeypatch):
    async def mock_call(*args, **kwargs):
        return {"status": "success"}
    
    monkeypatch.setattr(
        "mycomponent.core.service.external_call",
        mock_call
    )
```

## Performance Testing

### Load Testing Endpoints
```python
import asyncio
import time

@pytest.mark.asyncio
async def test_endpoint_performance(async_client):
    """Test endpoint can handle concurrent requests"""
    start_time = time.time()
    
    # Create 100 concurrent requests
    tasks = [
        async_client.get("/api/v1/resources")
        for _ in range(100)
    ]
    
    responses = await asyncio.gather(*tasks)
    
    # All should succeed
    assert all(r.status_code == 200 for r in responses)
    
    # Should complete within reasonable time
    duration = time.time() - start_time
    assert duration < 5.0  # 5 seconds for 100 requests
```

### Health Check Performance
```python
@pytest.mark.asyncio
async def test_health_check_performance(async_client):
    """Health check should respond quickly"""
    start_time = time.time()
    
    response = await async_client.get("/health")
    
    duration = time.time() - start_time
    assert response.status_code == 200
    assert duration < 0.1  # 100ms max
```

## WebSocket Testing

```python
from fastapi.testclient import TestClient

def test_websocket_connection():
    client = TestClient(app)
    
    with client.websocket_connect("/ws") as websocket:
        # Send message
        websocket.send_json({"type": "ping"})
        
        # Receive response
        data = websocket.receive_json()
        assert data["type"] == "pong"
```

## Test Organization

### Directory Structure
```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_core_logic.py
│   └── test_utils.py
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_mcp_tools.py
│   └── test_hermes_integration.py
├── performance/
│   └── test_load.py
└── conftest.py
```

### Pytest Configuration
```ini
# pytest.ini
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
    - name: Run tests
      run: |
        pytest tests/ -v --cov=mycomponent --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Use Fixtures**: Share common setup with pytest fixtures
3. **Mock External Dependencies**: Don't rely on external services
4. **Test Edge Cases**: Empty lists, None values, malformed input
5. **Verify Response Format**: Check structure, not just status code
6. **Test Async Properly**: Use pytest-asyncio for async tests
7. **Performance Benchmarks**: Set reasonable performance expectations
8. **Document Test Purpose**: Clear test names and docstrings

## Common Testing Pitfalls

1. **Not Testing Error Cases**: Always test 404, 400, 500 scenarios
2. **Ignoring Async Context**: Use proper async test patterns
3. **Hardcoding Ports**: Use dynamic ports in tests
4. **Not Mocking External Services**: Tests fail when services are down
5. **Testing Implementation**: Test behavior, not implementation details
6. **Skipping Integration Tests**: Unit tests alone aren't enough
7. **No Performance Tests**: Discover issues before production