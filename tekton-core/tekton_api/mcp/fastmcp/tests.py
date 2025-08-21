"""
FastMCP Tests - Test suite for FastMCP integration.

This module provides tests for the FastMCP integration,
including tests for decorators, adapters, and schema validation.
"""

import unittest
import asyncio
from typing import Dict, Any

from tekton.mcp.fastmcp import (
    mcp_tool,
    mcp_capability,
    mcp_processor,
    mcp_context,
    adapt_tool,
    adapt_processor,
    adapt_context,
    MCPToolMeta,
    validate_schema,
    ToolSchema,
    ProcessorSchema,
    ContextSchema
)

class TestDecorators(unittest.TestCase):
    """Tests for FastMCP decorators."""
    
    def test_mcp_tool_decorator(self):
        """Test mcp_tool decorator."""
        # Create a tool
        @mcp_tool(
            name="TestTool",
            description="A test tool",
            tags=["test", "example"]
        )
        async def test_tool(name: str, value: int = 42) -> Dict[str, Any]:
            """
            A test tool.
            
            Args:
                name: Test name
                value: Test value
                
            Returns:
                Test result
            """
            return {
                "name": name,
                "value": value
            }
            
        # Check that the tool has the correct metadata
        self.assertTrue(hasattr(test_tool, "_mcp_tool_meta"))
        self.assertEqual(test_tool._mcp_tool_meta.name, "TestTool")
        self.assertEqual(test_tool._mcp_tool_meta.description, "A test tool")
        self.assertEqual(test_tool._mcp_tool_meta.tags, ["test", "example"])
        
        # Check that the parameters were correctly extracted
        params = test_tool._mcp_tool_meta.parameters
        self.assertIn("name", params)
        self.assertIn("value", params)
        self.assertTrue(params["name"]["required"])
        self.assertFalse(params["value"]["required"])
        self.assertEqual(params["value"]["default"], 42)
        
    def test_mcp_capability_decorator(self):
        """Test mcp_capability decorator."""
        # Create a function with a capability
        @mcp_capability(
            name="test_capability",
            description="A test capability",
            modality="text"
        )
        def test_function():
            pass
            
        # Check that the function has the correct capability
        self.assertTrue(hasattr(test_function, "_mcp_capabilities"))
        self.assertEqual(len(test_function._mcp_capabilities), 1)
        self.assertEqual(test_function._mcp_capabilities[0]["name"], "test_capability")
        self.assertEqual(test_function._mcp_capabilities[0]["modality"], "text")
        
    def test_mcp_processor_decorator(self):
        """Test mcp_processor decorator."""
        # Create a processor
        @mcp_processor(
            name="TestProcessor",
            description="A test processor",
            capabilities=["test_capability"]
        )
        class TestProcessor:
            """A test processor."""
            pass
            
        # Check that the processor has the correct metadata
        self.assertTrue(hasattr(TestProcessor, "_mcp_processor_meta"))
        self.assertEqual(TestProcessor._mcp_processor_meta["name"], "TestProcessor")
        self.assertEqual(TestProcessor._mcp_processor_meta["description"], "A test processor")
        self.assertEqual(TestProcessor._mcp_processor_meta["capabilities"], ["test_capability"])
        
class TestAdapters(unittest.TestCase):
    """Tests for FastMCP adapters."""
    
    def test_adapt_tool(self):
        """Test adapt_tool function."""
        # Create a tool specification
        tool_spec = {
            "id": "test-tool",
            "name": "Test Tool",
            "description": "A test tool",
            "schema": {
                "parameters": {
                    "name": {
                        "type": "string",
                        "required": True
                    },
                    "value": {
                        "type": "integer",
                        "required": False,
                        "default": 42
                    }
                },
                "return_type": {
                    "type": "object"
                }
            },
            "tags": ["test", "example"]
        }
        
        # Adapt the tool
        adapted_tool = adapt_tool(tool_spec)
        
        # Check that the adapted tool has the correct metadata
        self.assertTrue(hasattr(adapted_tool, "_mcp_tool_meta"))
        self.assertEqual(adapted_tool._mcp_tool_meta.id, "test-tool")
        self.assertEqual(adapted_tool._mcp_tool_meta.name, "Test Tool")
        self.assertEqual(adapted_tool._mcp_tool_meta.tags, ["test", "example"])
        
    def test_adapt_processor(self):
        """Test adapt_processor function."""
        # Create a processor specification
        processor_spec = {
            "id": "test-processor",
            "name": "Test Processor",
            "description": "A test processor",
            "capabilities": ["test_capability"],
            "endpoint": "http://localhost:8000/process"
        }
        
        # Adapt the processor
        AdaptedProcessor = adapt_processor(processor_spec)
        
        # Check that the adapted processor has the correct metadata
        self.assertTrue(hasattr(AdaptedProcessor, "_mcp_processor_meta"))
        self.assertEqual(AdaptedProcessor._mcp_processor_meta["id"], "test-processor")
        self.assertEqual(AdaptedProcessor._mcp_processor_meta["name"], "Test Processor")
        self.assertEqual(AdaptedProcessor._mcp_processor_meta["capabilities"], ["test_capability"])
        
    def test_adapt_context(self):
        """Test adapt_context function."""
        # Create a context
        context = {
            "id": "test-context",
            "data": {"key": "value"},
            "source": {"component": "test"}
        }
        
        # Adapt the context
        adapted_context = adapt_context(context)
        
        # Check that the adapted context has the correct data
        self.assertEqual(adapted_context["id"], "test-context")
        self.assertEqual(adapted_context["data"], {"key": "value"})
        self.assertEqual(adapted_context["source"], {"component": "test"})
        self.assertTrue(adapted_context["metadata"]["adapted"])
        
class TestSchema(unittest.TestCase):
    """Tests for FastMCP schema validation."""
    
    def test_tool_schema(self):
        """Test tool schema validation."""
        # Create a valid tool specification
        tool_spec = {
            "id": "test-tool",
            "name": "Test Tool",
            "description": "A test tool",
            "schema": {
                "parameters": {
                    "name": {
                        "type": "string",
                        "required": True
                    }
                },
                "return_type": {
                    "type": "object"
                }
            }
        }
        
        # Validate the tool
        result = validate_schema("tool", tool_spec)
        self.assertTrue(result)
        
        # Create an invalid tool specification (missing required field)
        invalid_tool_spec = {
            "id": "test-tool",
            "name": "Test Tool"
            # Missing description
        }
        
        # Validate the invalid tool
        with self.assertRaises(Exception):
            validate_schema("tool", invalid_tool_spec)
            
    def test_processor_schema(self):
        """Test processor schema validation."""
        # Create a valid processor specification
        processor_spec = {
            "id": "test-processor",
            "name": "Test Processor",
            "description": "A test processor",
            "capabilities": ["test_capability"]
        }
        
        # Validate the processor
        result = validate_schema("processor", processor_spec)
        self.assertTrue(result)
        
    def test_context_schema(self):
        """Test context schema validation."""
        # Create a valid context
        context = {
            "id": "test-context",
            "data": {"key": "value"},
            "source": {"component": "test"}
        }
        
        # Validate the context
        result = validate_schema("context", context)
        self.assertTrue(result)
        
def run_tests():
    """Run the test suite."""
    unittest.main()
    
if __name__ == "__main__":
    run_tests()