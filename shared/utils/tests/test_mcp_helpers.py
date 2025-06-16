"""
Tests for FastMCP helper utilities.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Callable, Dict, Any

from shared.utils.mcp_helpers import (
    create_mcp_server,
    register_mcp_tools,
    convert_tool_to_schema,
    create_standard_tools,
    wrap_tool_with_error_handling,
    MCPToolRegistry
)


def test_create_mcp_server():
    """Test creating standardized FastMCP server."""
    with patch('shared.utils.mcp_helpers.FastMCPServer') as MockServer:
        mock_instance = Mock()
        MockServer.return_value = mock_instance
        
        server = create_mcp_server("test_component", "1.0.0")
        
        MockServer.assert_called_once_with(
            name="test_component",
            version="1.0.0",
            description="FastMCP server for test_component"
        )
        assert server == mock_instance


def test_create_mcp_server_with_custom_description():
    """Test creating FastMCP server with custom description."""
    with patch('shared.utils.mcp_helpers.FastMCPServer') as MockServer:
        mock_instance = Mock()
        MockServer.return_value = mock_instance
        
        server = create_mcp_server(
            "test_component", 
            "1.0.0",
            description="Custom test server"
        )
        
        MockServer.assert_called_once_with(
            name="test_component",
            version="1.0.0",
            description="Custom test server"
        )


def test_register_mcp_tools_success():
    """Test bulk registering tools successfully."""
    mock_server = Mock()
    
    async def tool1():
        """Tool 1 docstring"""
        pass
    
    async def tool2():
        """Tool 2 docstring"""
        pass
    
    tools = [tool1, tool2]
    
    success_count = register_mcp_tools(mock_server, tools)
    
    assert success_count == 2
    assert mock_server.register_tool.call_count == 2


def test_register_mcp_tools_with_failures():
    """Test registering tools with some failures."""
    mock_server = Mock()
    mock_server.register_tool.side_effect = [None, Exception("Registration failed"), None]
    
    async def tool1():
        pass
    
    async def tool2():
        pass
    
    async def tool3():
        pass
    
    tools = [tool1, tool2, tool3]
    
    success_count = register_mcp_tools(mock_server, tools)
    
    assert success_count == 2  # Only 2 succeeded
    assert mock_server.register_tool.call_count == 3


def test_convert_tool_to_schema():
    """Test converting a tool function to MCP schema."""
    async def sample_tool(query: str, limit: int = 10, active: bool = True) -> Dict[str, Any]:
        """
        Search for items in the database.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            active: Only return active items
            
        Returns:
            Dictionary of search results
        """
        return {"results": []}
    
    schema = convert_tool_to_schema(sample_tool)
    
    assert schema["name"] == "sample_tool"
    assert schema["description"] == "Search for items in the database."
    assert "inputSchema" in schema
    assert schema["inputSchema"]["type"] == "object"
    assert "query" in schema["inputSchema"]["properties"]
    assert "limit" in schema["inputSchema"]["properties"]
    assert "active" in schema["inputSchema"]["properties"]
    assert schema["inputSchema"]["required"] == ["query"]


def test_convert_tool_to_schema_no_args():
    """Test converting a tool with no arguments."""
    async def get_status() -> str:
        """Get current system status."""
        return "healthy"
    
    schema = convert_tool_to_schema(get_status)
    
    assert schema["name"] == "get_status"
    assert schema["description"] == "Get current system status."
    assert schema["inputSchema"]["properties"] == {}
    assert schema["inputSchema"]["required"] == []


def test_wrap_tool_with_error_handling():
    """Test wrapping a tool with error handling."""
    call_count = 0
    
    async def failing_tool():
        nonlocal call_count
        call_count += 1
        raise ValueError("Tool failed")
    
    wrapped = wrap_tool_with_error_handling(failing_tool, "test_component")
    
    # Should not raise, but return error dict
    result = asyncio.run(wrapped())
    
    assert call_count == 1
    assert result["error"] is True
    assert "Tool failed" in result["message"]
    assert result["component"] == "test_component"


def test_wrap_tool_success():
    """Test wrapped tool on success."""
    async def working_tool(value: int) -> int:
        return value * 2
    
    wrapped = wrap_tool_with_error_handling(working_tool, "test_component")
    
    result = asyncio.run(wrapped(5))
    
    assert result == 10  # Normal return value


def test_create_standard_tools():
    """Test creating standard tools for a component."""
    tools = create_standard_tools("test_component", port=8000)
    
    assert len(tools) >= 2  # At least health and status
    
    # Find health check tool
    health_tool = next((t for t in tools if t.__name__ == "health_check"), None)
    assert health_tool is not None
    
    # Test health check
    result = asyncio.run(health_tool())
    assert result["status"] == "healthy"
    assert result["component"] == "test_component"
    assert result["port"] == 8000


def test_mcp_tool_registry():
    """Test MCPToolRegistry for managing tools."""
    registry = MCPToolRegistry()
    
    async def tool1():
        """Tool 1"""
        pass
    
    async def tool2():
        """Tool 2"""
        pass
    
    # Register tools
    registry.register("tool1", tool1)
    registry.register("tool2", tool2)
    
    assert len(registry) == 2
    assert registry.get("tool1") == tool1
    assert registry.get("tool2") == tool2
    assert registry.get("nonexistent") is None


def test_mcp_tool_registry_list_tools():
    """Test listing tools in registry."""
    registry = MCPToolRegistry()
    
    async def search_tool():
        """Search for items"""
        pass
    
    async def create_tool():
        """Create new item"""
        pass
    
    registry.register("search", search_tool)
    registry.register("create", create_tool)
    
    tools = registry.list_tools()
    assert len(tools) == 2
    assert any(t["name"] == "search" for t in tools)
    assert any(t["name"] == "create" for t in tools)
    
    # Check descriptions are included
    search_info = next(t for t in tools if t["name"] == "search")
    assert search_info["description"] == "Search for items"


def test_mcp_tool_registry_clear():
    """Test clearing the tool registry."""
    registry = MCPToolRegistry()
    
    async def tool1():
        pass
    
    registry.register("tool1", tool1)
    assert len(registry) == 1
    
    registry.clear()
    assert len(registry) == 0


def test_metis_style_tool_conversion():
    """Test converting Metis-style tool definitions."""
    # Metis uses a specific pattern with tool schemas
    metis_tool = {
        "name": "analyze_task",
        "description": "Analyze a task and break it into subtasks",
        "parameters": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Task to analyze"},
                "max_depth": {"type": "integer", "default": 3}
            },
            "required": ["task"]
        }
    }
    
    # This tests that our helpers can work with Metis-style definitions
    from shared.utils.mcp_helpers import convert_metis_tool
    
    async def analyze_task_impl(task: str, max_depth: int = 3):
        return {"subtasks": []}
    
    converted = convert_metis_tool(metis_tool, analyze_task_impl)
    
    assert converted.__name__ == "analyze_task"
    assert hasattr(converted, "__doc__")
    
    # Test the converted function works
    result = asyncio.run(converted(task="Test task"))
    assert "subtasks" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])