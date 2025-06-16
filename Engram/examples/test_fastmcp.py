#!/usr/bin/env python3
"""
Test script for Engram's FastMCP implementation

This script tests the FastMCP functionality in the Engram component,
using the MCP client to interact with the Engram API.
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add parent directory to path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Try to import FastMCP client
try:
    from tekton.mcp.fastmcp import MCPClient
except ImportError:
    print("Error: FastMCP client not found. Please make sure tekton-core is installed.")
    sys.exit(1)

# ASCII art for better visibility
BANNER = """
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║   Engram FastMCP Test                                 ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
"""

def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}\n")

def print_result(success: bool, title: str, result: Any):
    """Print a test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {title}")
    print(f"Result: {json.dumps(result, indent=2)}")
    print()

async def test_get_capabilities(client: MCPClient):
    """Test getting capabilities from Engram component."""
    print_section("Testing Get Capabilities")
    
    try:
        capabilities = await client.get_capabilities()
        success = len(capabilities) > 0
        print_result(success, "Get Capabilities", capabilities)
        return success
    except Exception as e:
        print(f"Error: {str(e)}")
        print_result(False, "Get Capabilities", {"error": str(e)})
        return False

async def test_get_tools(client: MCPClient):
    """Test getting tools from Engram component."""
    print_section("Testing Get Tools")
    
    try:
        tools = await client.get_tools()
        success = len(tools) > 0
        print_result(success, "Get Tools", [tool.name for tool in tools])
        return success
    except Exception as e:
        print(f"Error: {str(e)}")
        print_result(False, "Get Tools", {"error": str(e)})
        return False

async def test_memory_store(client: MCPClient):
    """Test MemoryStore tool."""
    print_section("Testing MemoryStore Tool")
    
    try:
        # Create test memory content
        content = f"This is a test memory created at {datetime.now().isoformat()}"
        namespace = "test"
        
        # Execute tool
        result = await client.execute_tool(
            "MemoryStore",
            {
                "content": content,
                "namespace": namespace
            }
        )
        
        # Check result
        success = (
            result is not None and
            "success" in result and
            result["success"] is True and
            "namespace" in result and
            result["namespace"] == namespace
        )
        
        print_result(success, "MemoryStore", result)
        return success
    except Exception as e:
        print(f"Error: {str(e)}")
        print_result(False, "MemoryStore", {"error": str(e)})
        return False

async def test_memory_query(client: MCPClient):
    """Test MemoryQuery tool."""
    print_section("Testing MemoryQuery Tool")
    
    try:
        # Query for memories
        query = "test memory"
        namespace = "test"
        
        # Execute tool
        result = await client.execute_tool(
            "MemoryQuery",
            {
                "query": query,
                "namespace": namespace,
                "limit": 5
            }
        )
        
        # Check result
        success = (
            result is not None and
            "memories" in result
        )
        
        print_result(success, "MemoryQuery", result)
        return success
    except Exception as e:
        print(f"Error: {str(e)}")
        print_result(False, "MemoryQuery", {"error": str(e)})
        return False

async def test_get_context(client: MCPClient):
    """Test GetContext tool."""
    print_section("Testing GetContext Tool")
    
    try:
        # Query for context
        query = "test"
        
        # Execute tool
        result = await client.execute_tool(
            "GetContext",
            {
                "query": query,
                "namespaces": ["test", "conversations"],
                "limit": 3
            }
        )
        
        # Check result
        success = (
            result is not None and
            "context" in result
        )
        
        print_result(success, "GetContext", result)
        return success
    except Exception as e:
        print(f"Error: {str(e)}")
        print_result(False, "GetContext", {"error": str(e)})
        return False

async def test_structured_memory_add(client: MCPClient):
    """Test StructuredMemoryAdd tool."""
    print_section("Testing StructuredMemoryAdd Tool")
    
    try:
        # Create test structured memory
        content = f"This is a structured test memory created at {datetime.now().isoformat()}"
        category = "test"
        importance = 3
        tags = ["test", "fastmcp", "example"]
        
        # Execute tool
        result = await client.execute_tool(
            "StructuredMemoryAdd",
            {
                "content": content,
                "category": category,
                "importance": importance,
                "tags": tags
            }
        )
        
        # Check result
        success = (
            result is not None and
            "success" in result and
            result["success"] is True and
            "memory_id" in result
        )
        
        memory_id = result.get("memory_id") if success else None
        
        print_result(success, "StructuredMemoryAdd", result)
        return success, memory_id
    except Exception as e:
        print(f"Error: {str(e)}")
        print_result(False, "StructuredMemoryAdd", {"error": str(e)})
        return False, None

async def test_structured_memory_get(client: MCPClient, memory_id: Optional[str] = None):
    """Test StructuredMemoryGet tool."""
    print_section("Testing StructuredMemoryGet Tool")
    
    if not memory_id:
        print("No memory ID provided, skipping test")
        return False
    
    try:
        # Execute tool
        result = await client.execute_tool(
            "StructuredMemoryGet",
            {
                "memory_id": memory_id
            }
        )
        
        # Check result
        success = (
            result is not None and
            "success" in result and
            result["success"] is True and
            "memory" in result
        )
        
        print_result(success, "StructuredMemoryGet", result)
        return success
    except Exception as e:
        print(f"Error: {str(e)}")
        print_result(False, "StructuredMemoryGet", {"error": str(e)})
        return False

async def test_structured_memory_update(client: MCPClient, memory_id: Optional[str] = None):
    """Test StructuredMemoryUpdate tool."""
    print_section("Testing StructuredMemoryUpdate Tool")
    
    if not memory_id:
        print("No memory ID provided, skipping test")
        return False
    
    try:
        # Update structured memory
        importance = 5
        tags = ["test", "fastmcp", "example", "updated"]
        
        # Execute tool
        result = await client.execute_tool(
            "StructuredMemoryUpdate",
            {
                "memory_id": memory_id,
                "importance": importance,
                "tags": tags
            }
        )
        
        # Check result
        success = (
            result is not None and
            "success" in result and
            result["success"] is True and
            "memory_id" in result and
            result["memory_id"] == memory_id
        )
        
        print_result(success, "StructuredMemoryUpdate", result)
        return success
    except Exception as e:
        print(f"Error: {str(e)}")
        print_result(False, "StructuredMemoryUpdate", {"error": str(e)})
        return False

async def test_structured_memory_search(client: MCPClient):
    """Test StructuredMemorySearch tool."""
    print_section("Testing StructuredMemorySearch Tool")
    
    try:
        # Search for structured memories
        query = "test memory"
        category = "test"
        
        # Execute tool
        result = await client.execute_tool(
            "StructuredMemorySearch",
            {
                "query": query,
                "category": category,
                "limit": 10
            }
        )
        
        # Check result
        success = (
            result is not None and
            "success" in result and
            result["success"] is True and
            "results" in result
        )
        
        print_result(success, "StructuredMemorySearch", result)
        return success
    except Exception as e:
        print(f"Error: {str(e)}")
        print_result(False, "StructuredMemorySearch", {"error": str(e)})
        return False

async def test_structured_memory_delete(client: MCPClient, memory_id: Optional[str] = None):
    """Test StructuredMemoryDelete tool."""
    print_section("Testing StructuredMemoryDelete Tool")
    
    if not memory_id:
        print("No memory ID provided, skipping test")
        return False
    
    try:
        # Execute tool
        result = await client.execute_tool(
            "StructuredMemoryDelete",
            {
                "memory_id": memory_id
            }
        )
        
        # Check result
        success = (
            result is not None and
            "success" in result and
            result["success"] is True and
            "memory_id" in result and
            result["memory_id"] == memory_id
        )
        
        print_result(success, "StructuredMemoryDelete", result)
        return success
    except Exception as e:
        print(f"Error: {str(e)}")
        print_result(False, "StructuredMemoryDelete", {"error": str(e)})
        return False

async def test_nexus_process(client: MCPClient):
    """Test NexusProcess tool."""
    print_section("Testing NexusProcess Tool")
    
    try:
        # Process a message
        message = "This is a test message for the Nexus interface"
        
        # Execute tool
        result = await client.execute_tool(
            "NexusProcess",
            {
                "message": message,
                "is_user": True
            }
        )
        
        # Check result
        success = (
            result is not None and
            "success" in result and
            result["success"] is True and
            "result" in result
        )
        
        print_result(success, "NexusProcess", result)
        return success
    except Exception as e:
        print(f"Error: {str(e)}")
        print_result(False, "NexusProcess", {"error": str(e)})
        return False

async def run_all_tests():
    """Run all FastMCP tests."""
    print(BANNER)
    
    # Get Engram URL from environment or use default
    engram_url = os.environ.get("ENGRAM_URL", "http://localhost:8001/mcp")
    print(f"Connecting to Engram MCP at: {engram_url}")
    
    # Create MCP client
    client = MCPClient(
        component_id="test-client",
        mcp_url=engram_url,
        timeout=10.0
    )
    
    # Run tests
    results = []
    
    # Test capabilities and tools
    results.append(await test_get_capabilities(client))
    results.append(await test_get_tools(client))
    
    # Test memory operations
    results.append(await test_memory_store(client))
    results.append(await test_memory_query(client))
    results.append(await test_get_context(client))
    
    # Test structured memory operations
    success, memory_id = await test_structured_memory_add(client)
    results.append(success)
    
    if memory_id:
        results.append(await test_structured_memory_get(client, memory_id))
        results.append(await test_structured_memory_update(client, memory_id))
        results.append(await test_structured_memory_search(client))
        results.append(await test_structured_memory_delete(client, memory_id))
    else:
        # Skip tests that require a memory ID
        for _ in range(4):
            results.append(False)
    
    # Test nexus operations
    results.append(await test_nexus_process(client))
    
    # Print summary
    print_section("Test Summary")
    total = len(results)
    passed = results.count(True)
    failed = results.count(False)
    
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    # Display overall result
    if failed == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {failed} test(s) failed.")

if __name__ == "__main__":
    asyncio.run(run_all_tests())