# Testing Guide

This guide covers the test-driven development approach for Tekton components. Tests define success criteria and drive implementation.

## Testing Philosophy

In Tekton development:
1. **Test Writer** creates tests that define expected behavior
2. **Developer** implements functionality to make tests pass
3. **Tests are fluid** - they change as requirements evolve
4. **Coverage is managed** - sprint lead decides what needs testing

## Test Structure

### Directory Layout

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests for individual functions
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_core.py
│   └── test_utils.py
├── integration/             # Integration tests
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_mcp.py
│   └── test_hermes.py
└── e2e/                     # End-to-end tests (optional)
    ├── __init__.py
    └── test_workflows.py
```

## Setting Up Tests

### conftest.py

```python
"""
Test configuration and shared fixtures
"""
import pytest
import asyncio
import os
from typing import AsyncGenerator
from httpx import AsyncClient

# Set test environment
os.environ["MYCOMPONENT_PORT"] = "8999"  # Use different port for tests
os.environ["TESTING"] = "true"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def app():
    """Create FastAPI app for testing."""
    from mycomponent.api.app import app as _app
    
    # Override startup/shutdown to avoid external connections
    _app.state.testing = True
    
    yield _app

@pytest.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def mock_hermes():
    """Mock Hermes registration."""
    class MockHermesRegistration:
        async def register_component(self, **kwargs):
            return True
        
        async def deregister(self, component_name):
            pass
        
        async def heartbeat(self, component_name):
            return True
    
    return MockHermesRegistration()
```

## Unit Tests

### Testing Models

```python
# tests/unit/test_models.py
import pytest
from datetime import datetime
from pydantic import ValidationError

from mycomponent.models.data import DataModel, StatusEnum

class TestDataModel:
    """Test data model validation and behavior."""
    
    def test_valid_model_creation(self):
        """Test creating a valid model instance."""
        data = DataModel(
            id="test-123",
            name="Test Data",
            status=StatusEnum.ACTIVE,
            created_at=datetime.utcnow()
        )
        
        assert data.id == "test-123"
        assert data.name == "Test Data"
        assert data.status == StatusEnum.ACTIVE
    
    def test_model_validation_errors(self):
        """Test model validation catches invalid data."""
        with pytest.raises(ValidationError) as exc_info:
            DataModel(
                id="",  # Empty ID should fail
                name="Test",
                status="invalid_status"  # Invalid enum value
            )
        
        errors = exc_info.value.errors()
        assert len(errors) >= 2
        assert any(e["loc"] == ("id",) for e in errors)
        assert any(e["loc"] == ("status",) for e in errors)
    
    def test_model_serialization(self):
        """Test model serialization to dict/json."""
        data = DataModel(
            id="test-123",
            name="Test Data",
            status=StatusEnum.ACTIVE
        )
        
        # Test dict conversion
        data_dict = data.model_dump()
        assert data_dict["id"] == "test-123"
        assert "created_at" in data_dict
        
        # Test JSON serialization
        json_str = data.model_dump_json()
        assert "test-123" in json_str
```

### Testing Core Logic

```python
# tests/unit/test_core.py
import pytest
from unittest.mock import AsyncMock, MagicMock

from mycomponent.core.service import MyService
from mycomponent.core.exceptions import ProcessingError

@pytest.fixture
async def service():
    """Create service instance for testing."""
    service = MyService()
    await service.initialize()
    yield service
    await service.cleanup()

class TestMyService:
    """Test core service functionality."""
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """Test service initializes correctly."""
        assert service.initialized
        assert service.config is not None
    
    @pytest.mark.asyncio
    async def test_process_valid_input(self, service):
        """Test processing valid input."""
        input_data = {"key": "value", "number": 42}
        
        result = await service.process(input_data)
        
        assert result["status"] == "success"
        assert result["processed_at"] is not None
        assert "output" in result
    
    @pytest.mark.asyncio
    async def test_process_invalid_input(self, service):
        """Test handling of invalid input."""
        with pytest.raises(ProcessingError) as exc_info:
            await service.process(None)
        
        assert "Invalid input" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_service_cleanup(self, service):
        """Test service cleanup releases resources."""
        assert service.initialized
        
        await service.cleanup()
        
        assert not service.initialized
```

## Integration Tests

### Testing API Endpoints

```python
# tests/integration/test_api.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
class TestAPI:
    """Test API endpoints."""
    
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint returns component info."""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "MyComponent"
        assert "version" in data
        assert "documentation" in data
    
    async def test_health_endpoint(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert data["component"] == "mycomponent"
        assert "timestamp" in data
        assert "port" in data
        assert "checks" in data
    
    async def test_api_error_handling(self, client: AsyncClient):
        """Test API error handling."""
        response = await client.get("/api/nonexistent")
        
        assert response.status_code == 404
    
    async def test_api_validation(self, client: AsyncClient):
        """Test API input validation."""
        # Send invalid data
        response = await client.post(
            "/api/process",
            json={"invalid": "data"}
        )
        
        assert response.status_code == 422  # Validation error
        error_detail = response.json()["detail"]
        assert len(error_detail) > 0
```

### Testing MCP Integration

```python
# tests/integration/test_mcp.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
class TestMCPIntegration:
    """Test MCP v2 endpoints."""
    
    async def test_list_tools(self, client: AsyncClient):
        """Test MCP tool listing."""
        response = await client.post("/mcp/v2/tools/list")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "tools" in data
        assert isinstance(data["tools"], list)
        
        # Verify tool structure
        for tool in data["tools"]:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
    
    async def test_call_tool_success(self, client: AsyncClient):
        """Test successful tool execution."""
        response = await client.post(
            "/mcp/v2/tools/call",
            json={
                "name": "example_tool",
                "arguments": {"input": "test data"}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "content" in data
        assert isinstance(data["content"], list)
        assert not data.get("isError", False)
    
    async def test_call_unknown_tool(self, client: AsyncClient):
        """Test calling unknown tool returns error."""
        response = await client.post(
            "/mcp/v2/tools/call",
            json={
                "name": "nonexistent_tool",
                "arguments": {}
            }
        )
        
        assert response.status_code == 200  # MCP returns 200 with error flag
        data = response.json()
        
        assert data.get("isError") is True
        assert any("not found" in c.get("text", "") for c in data["content"])
```

## Testing Patterns

### Mock External Dependencies

```python
@pytest.fixture
def mock_external_service(monkeypatch):
    """Mock external service calls."""
    async def mock_call(*args, **kwargs):
        return {"status": "success", "data": "mocked"}
    
    monkeypatch.setattr(
        "mycomponent.core.external.ExternalService.call",
        mock_call
    )

# Usage
@pytest.mark.asyncio
async def test_with_mock(mock_external_service, service):
    result = await service.process_with_external()
    assert result["external_data"] == "mocked"
```

### Testing Async Operations

```python
@pytest.mark.asyncio
async def test_concurrent_operations(service):
    """Test handling concurrent operations."""
    import asyncio
    
    # Create multiple concurrent tasks
    tasks = [
        service.process({"id": i}) 
        for i in range(10)
    ]
    
    results = await asyncio.gather(*tasks)
    
    assert len(results) == 10
    assert all(r["status"] == "success" for r in results)
```

### Testing WebSocket Connections

```python
@pytest.mark.asyncio
async def test_websocket_connection(client: AsyncClient):
    """Test WebSocket connection and messaging."""
    from fastapi.testclient import TestClient
    
    # FastAPI TestClient supports WebSocket testing
    with TestClient(app) as test_client:
        with test_client.websocket_connect("/ws") as websocket:
            # Send message
            websocket.send_json({
                "type": "test",
                "payload": {"data": "test"}
            })
            
            # Receive response
            data = websocket.receive_json()
            assert data["type"] == "response"
```

## Test Execution

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mycomponent --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py

# Run specific test
pytest tests/unit/test_models.py::TestDataModel::test_valid_model_creation

# Run with verbose output
pytest -v

# Run only marked tests
pytest -m "integration"
```

### Test Markers

```python
# Mark slow tests
@pytest.mark.slow
async def test_long_running_operation():
    pass

# Mark integration tests
@pytest.mark.integration
async def test_external_integration():
    pass

# Skip test conditionally
@pytest.mark.skipif(
    os.environ.get("SKIP_EXTERNAL") == "true",
    reason="Skipping external tests"
)
async def test_external_api():
    pass
```

## Test-Driven Development Flow

### 1. Test Writer Creates Tests

```python
# Initial test defining expected behavior
@pytest.mark.asyncio
async def test_new_feature(client):
    """Test new feature processes data correctly."""
    response = await client.post(
        "/api/new-feature",
        json={
            "input": "test data",
            "options": {"mode": "fast"}
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    
    # Define expected behavior
    assert result["status"] == "processed"
    assert "output" in result
    assert result["mode"] == "fast"
    assert len(result["output"]) > 0
```

### 2. Developer Implements Feature

The developer implements code to make the test pass:

```python
@router.post("/api/new-feature")
async def new_feature(request: NewFeatureRequest):
    """Implement new feature to satisfy test."""
    # Implementation that makes test pass
    return {
        "status": "processed",
        "output": process_data(request.input),
        "mode": request.options.mode
    }
```

### 3. Iterate and Refine

As requirements change, tests are updated:

```python
# Updated test with new requirements
@pytest.mark.asyncio
async def test_new_feature_with_validation(client):
    """Test new feature with input validation."""
    # Test invalid input
    response = await client.post(
        "/api/new-feature",
        json={"input": ""}  # Empty input should fail
    )
    
    assert response.status_code == 422
    assert "Input cannot be empty" in response.text
```

## Best Practices

1. **Test Behavior, Not Implementation** - Focus on what, not how
2. **Keep Tests Simple** - Each test should verify one thing
3. **Use Descriptive Names** - Test names should explain what they test
4. **Isolate Tests** - Tests shouldn't depend on each other
5. **Mock External Dependencies** - Tests should be fast and reliable
6. **Test Edge Cases** - Empty inputs, large inputs, invalid data
7. **Clean Up After Tests** - Don't leave test data behind

## Common Testing Scenarios

### Testing with Different Configurations

```python
@pytest.mark.parametrize("config,expected", [
    ({"mode": "fast"}, "quick_result"),
    ({"mode": "accurate"}, "precise_result"),
    ({"mode": "balanced"}, "balanced_result"),
])
async def test_different_modes(service, config, expected):
    """Test service with different configurations."""
    service.update_config(config)
    result = await service.process({"data": "test"})
    assert expected in result["output"]
```

### Testing Error Scenarios

```python
async def test_error_recovery(service):
    """Test service recovers from errors."""
    # Cause an error
    with pytest.raises(ProcessingError):
        await service.process({"invalid": "data"})
    
    # Verify service still works
    result = await service.process({"valid": "data"})
    assert result["status"] == "success"
```

### Testing Performance

```python
@pytest.mark.slow
async def test_performance(service):
    """Test service meets performance requirements."""
    import time
    
    start = time.time()
    
    # Process 100 items
    for i in range(100):
        await service.process({"id": i})
    
    duration = time.time() - start
    
    # Should complete in under 10 seconds
    assert duration < 10.0
```

---

*Next: [Documentation Requirements](./Documentation_Requirements.md)*