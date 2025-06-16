"""
Tests for Tekton Shared Models

Validates that all Pydantic v2 models work correctly with:
- Serialization and deserialization
- Field validation
- JSON schema generation
- Proper camelCase aliasing
"""

import json
from datetime import datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

import sys
sys.path.insert(0, '/Users/cskoons/projects/github/Tekton')

from tekton.models import (
    # Base models
    TektonBaseModel,
    ErrorResponse,
    SuccessResponse,
    ValidationErrorDetail,
    APIResponse,
    # Health models
    HealthStatus,
    HealthCheckResponse,
    StatusResponse,
    DependencyStatus,
    ComponentInfo,
    create_health_response,
    # MCP models
    MCPTool,
    MCPToolList,
    MCPToolCall,
    MCPToolResponse,
    MCPError,
    MCPErrorCode,
    # Registration models
    ComponentRegistration,
    RegistrationRequest,
    RegistrationResponse,
    HeartbeatRequest,
    HeartbeatResponse,
)


class TestBaseModels:
    """Test base model functionality"""
    
    def test_tekton_base_model_camel_case(self):
        """Test that TektonBaseModel converts to camelCase in JSON"""
        
        class TestModel(TektonBaseModel):
            snake_case_field: str
            another_field: int
        
        model = TestModel(snake_case_field="test", another_field=42)
        json_dict = model.model_dump(by_alias=True)
        
        assert "snakeCaseField" in json_dict
        assert "anotherField" in json_dict
        assert json_dict["snakeCaseField"] == "test"
        assert json_dict["anotherField"] == 42
    
    def test_error_response(self):
        """Test ErrorResponse model"""
        error = ErrorResponse(
            error="ValidationError",
            message="Invalid input data",
            component="test-component"
        )
        
        assert error.error == "ValidationError"
        assert error.message == "Invalid input data"
        assert error.component == "test-component"
        assert isinstance(error.request_id, UUID)
        assert isinstance(error.timestamp, datetime)
        
        # Test JSON serialization
        json_str = error.model_dump_json(by_alias=True)
        data = json.loads(json_str)
        assert "requestId" in data
        assert "timestamp" in data
    
    def test_success_response(self):
        """Test SuccessResponse model"""
        success = SuccessResponse(message="Operation completed")
        
        assert success.success is True
        assert success.message == "Operation completed"
        assert isinstance(success.request_id, UUID)
        
    def test_api_response_generic(self):
        """Test generic APIResponse wrapper"""
        
        class UserModel(TektonBaseModel):
            name: str
            email: str
        
        user = UserModel(name="John Doe", email="john@example.com")
        response = APIResponse[UserModel](
            data=user,
            message="User retrieved"
        )
        
        assert response.success is True
        assert response.data.name == "John Doe"
        assert response.message == "User retrieved"


class TestHealthModels:
    """Test health and status models"""
    
    def test_health_status_enum(self):
        """Test HealthStatus enum values"""
        assert HealthStatus.HEALTHY == "healthy"
        assert HealthStatus.DEGRADED == "degraded"
        assert HealthStatus.UNHEALTHY == "unhealthy"
        assert HealthStatus.UNKNOWN == "unknown"
    
    def test_component_info_validation(self):
        """Test ComponentInfo validation"""
        # Valid component
        info = ComponentInfo(
            name="testcomponent",
            version="1.0.0",
            description="Test component"
        )
        assert info.name == "testcomponent"
        
        # Invalid name (not lowercase)
        with pytest.raises(ValidationError) as exc_info:
            ComponentInfo(name="TestComponent", version="1.0.0")
        assert "Component name must be lowercase" in str(exc_info.value)
        
        # Invalid version format
        with pytest.raises(ValidationError) as exc_info:
            ComponentInfo(name="test", version="1.0")
        assert "semantic versioning" in str(exc_info.value)
    
    def test_health_check_response(self):
        """Test HealthCheckResponse model"""
        health = HealthCheckResponse(
            status=HealthStatus.HEALTHY,
            component="rhetor",
            version="0.1.0",
            port=8003,
            registered_with_hermes=True,
            uptime=3600.5,
            dependencies=[
                DependencyStatus(
                    name="hermes",
                    status=HealthStatus.HEALTHY,
                    message="Connected"
                )
            ],
            metrics={"requests": 100},
            details={"providers": ["openai", "anthropic"]}
        )
        
        assert health.status == HealthStatus.HEALTHY
        assert health.component == "rhetor"
        assert health.port == 8003
        assert health.registered_with_hermes is True
        assert len(health.dependencies) == 1
        assert health.dependencies[0].name == "hermes"
        
        # Test JSON serialization with camelCase
        json_dict = health.model_dump(by_alias=True)
        assert "registeredWithHermes" in json_dict
        assert json_dict["registeredWithHermes"] is True
    
    def test_create_health_response_helper(self):
        """Test the create_health_response helper function"""
        health = create_health_response(
            component_name="test",
            port=8000,
            version="1.0.0",
            status=HealthStatus.HEALTHY,
            registered=True,
            uptime=100.0,
            details={"test": "data"}
        )
        
        assert isinstance(health, HealthCheckResponse)
        assert health.component == "test"
        assert health.port == 8000
        assert health.registered_with_hermes is True


class TestMCPModels:
    """Test MCP models"""
    
    def test_mcp_tool(self):
        """Test MCPTool model"""
        tool = MCPTool(
            name="get_weather",
            description="Get weather information",
            input_schema={
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        )
        
        assert tool.name == "get_weather"
        assert tool.input_schema["type"] == "object"
        
        # Test invalid tool name
        with pytest.raises(ValidationError):
            MCPTool(
                name="123-invalid",  # Must start with letter
                description="Test",
                input_schema={}
            )
    
    def test_mcp_tool_call(self):
        """Test MCPToolCall model"""
        call = MCPToolCall(
            tool_name="test_tool",
            arguments={"arg1": "value1"},
            metadata={"request_id": "123"}
        )
        
        assert call.tool_name == "test_tool"
        assert call.arguments["arg1"] == "value1"
        
        # Test alias
        json_dict = call.model_dump(by_alias=True)
        assert "name" in json_dict
        assert json_dict["name"] == "test_tool"
    
    def test_mcp_error(self):
        """Test MCPError model"""
        error = MCPError(
            code=MCPErrorCode.TOOL_NOT_FOUND,
            message="Tool not found",
            details={"available": ["tool1", "tool2"]}
        )
        
        assert error.code == MCPErrorCode.TOOL_NOT_FOUND
        assert error.message == "Tool not found"


class TestRegistrationModels:
    """Test registration models"""
    
    def test_component_registration(self):
        """Test ComponentRegistration model"""
        reg = ComponentRegistration(
            name="testcomponent",
            type="test-type",
            version="1.0.0",
            host="localhost",
            port=8000,
            protocol="http"
        )
        
        assert reg.name == "testcomponent"
        assert reg.type == "test-type"  # Should be lowercased
        assert reg.base_url == "http://localhost:8000"
        assert reg.is_healthy is False  # Default status is UNKNOWN
        assert reg.is_stale is True  # No heartbeat yet
        
        # Update with heartbeat
        reg.status = HealthStatus.HEALTHY
        reg.last_heartbeat = datetime.utcnow()
        assert reg.is_healthy is True
        assert reg.is_stale is False
    
    def test_registration_request(self):
        """Test RegistrationRequest model"""
        req = RegistrationRequest(
            name="apollo",
            type="action-planner",
            version="0.1.0",
            port=8009
        )
        
        assert req.name == "apollo"
        assert req.host == "localhost"  # Default
        assert req.protocol == "http"  # Default
        assert req.heartbeat_interval == 30  # Default
        
        # Test invalid port
        with pytest.raises(ValidationError):
            RegistrationRequest(
                name="test",
                type="test",
                version="1.0.0",
                port=70000  # Too high
            )
    
    def test_heartbeat_models(self):
        """Test heartbeat request and response"""
        req = HeartbeatRequest(
            component_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            status=HealthStatus.HEALTHY,
            metrics={"uptime": 1000}
        )
        
        assert req.status == HealthStatus.HEALTHY
        assert req.metrics["uptime"] == 1000
        
        resp = HeartbeatResponse(
            component_id=req.component_id,
            next_heartbeat=datetime.utcnow()
        )
        
        assert resp.success is True
        assert resp.component_id == req.component_id


def test_all_models_have_json_schema():
    """Ensure all models can generate JSON schema"""
    models_to_test = [
        ErrorResponse,
        SuccessResponse,
        HealthCheckResponse,
        StatusResponse,
        MCPTool,
        MCPToolCall,
        ComponentRegistration,
        RegistrationRequest,
    ]
    
    for model_class in models_to_test:
        schema = model_class.model_json_schema()
        assert "properties" in schema
        assert "type" in schema
        
        # Check if examples are included
        if "example" in model_class.model_config.get("json_schema_extra", {}):
            assert "$defs" in schema or "definitions" in schema or "examples" in schema