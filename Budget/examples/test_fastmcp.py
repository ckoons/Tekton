"""
Test script for Budget's FastMCP implementation

This script tests the FastMCP functionality in the Budget component,
using the MCP client to interact with the Budget API.
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add Tekton root to path for shared imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.env import TektonEnviron
from shared.urls import budget_url

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
║   Budget FastMCP Test                                 ║
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
    """Test getting capabilities from Budget component."""
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
    """Test getting tools from Budget component."""
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

async def test_allocate_budget(client: MCPClient):
    """Test AllocateBudget tool."""
    print_section("Testing AllocateBudget Tool")
    
    try:
        # Create parameters
        context_id = f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        amount = 1000
        component = "test-client"
        
        # Execute tool
        result = await client.execute_tool(
            "AllocateBudget",
            {
                "context_id": context_id,
                "amount": amount,
                "component": component,
                "tier": "local_lightweight"
            }
        )
        
        # Check result
        success = (
            result is not None and
            "allocation_id" in result and
            "amount" in result and 
            result["amount"] == amount
        )
        
        print_result(success, "AllocateBudget", result)
        return success, result
    except Exception as e:
        print(f"Error: {str(e)}")
        print_result(False, "AllocateBudget", {"error": str(e)})
        return False, None

async def test_check_budget(client: MCPClient):
    """Test CheckBudget tool."""
    print_section("Testing CheckBudget Tool")
    
    try:
        # Execute tool
        result = await client.execute_tool(
            "CheckBudget",
            {
                "provider": "anthropic",
                "model": "claude-3-5-sonnet",
                "input_text": "This is a test message",
                "component": "test-client"
            }
        )
        
        # Check result
        success = (
            result is not None and
            "allowed" in result and
            "info" in result
        )
        
        print_result(success, "CheckBudget", result)
        return success
    except Exception as e:
        print(f"Error: {str(e)}")
        print_result(False, "CheckBudget", {"error": str(e)})
        return False

async def test_record_usage(client: MCPClient, allocation_result: Optional[Dict[str, Any]] = None):
    """Test RecordUsage tool."""
    print_section("Testing RecordUsage Tool")
    
    try:
        # Use allocation ID if available, otherwise create new context
        params = {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet",
            "input_tokens": 100,
            "output_tokens": 200,
            "component": "test-client"
        }
        
        if allocation_result and "allocation_id" in allocation_result:
            params["allocation_id"] = allocation_result["allocation_id"]
        else:
            params["context_id"] = f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Execute tool
        result = await client.execute_tool("RecordUsage", params)
        
        # Check result
        success = (
            result is not None and
            "recorded_tokens" in result and
            result["recorded_tokens"] == 300 and  # 100 input + 200 output
            "success" in result and
            result["success"] is True
        )
        
        print_result(success, "RecordUsage", result)
        return success
    except Exception as e:
        print(f"Error: {str(e)}")
        print_result(False, "RecordUsage", {"error": str(e)})
        return False

async def test_get_budget_status(client: MCPClient):
    """Test GetBudgetStatus tool."""
    print_section("Testing GetBudgetStatus Tool")
    
    try:
        # Execute tool
        result = await client.execute_tool(
            "GetBudgetStatus",
            {
                "period": "daily"
            }
        )
        
        # Check result
        success = (
            result is not None and
            "success" in result and
            result["success"] is True
        )
        
        print_result(success, "GetBudgetStatus", result)
        return success
    except Exception as e:
        print(f"Error: {str(e)}")
        print_result(False, "GetBudgetStatus", {"error": str(e)})
        return False

async def test_get_model_recommendations(client: MCPClient):
    """Test GetModelRecommendations tool."""
    print_section("Testing GetModelRecommendations Tool")
    
    try:
        # Execute tool
        result = await client.execute_tool(
            "GetModelRecommendations",
            {
                "provider": "anthropic",
                "model": "claude-3-5-sonnet",
                "task_type": "chat",
                "context_size": 5000
            }
        )
        
        # Check result
        success = (
            result is not None and
            "recommendations" in result
        )
        
        print_result(success, "GetModelRecommendations", result)
        return success
    except Exception as e:
        print(f"Error: {str(e)}")
        print_result(False, "GetModelRecommendations", {"error": str(e)})
        return False

async def test_route_with_budget_awareness(client: MCPClient):
    """Test RouteWithBudgetAwareness tool."""
    print_section("Testing RouteWithBudgetAwareness Tool")
    
    try:
        # Execute tool
        result = await client.execute_tool(
            "RouteWithBudgetAwareness",
            {
                "input_text": "This is a test message",
                "default_provider": "anthropic",
                "default_model": "claude-3-5-sonnet",
                "component": "test-client"
            }
        )
        
        # Check result
        success = (
            result is not None and
            "provider" in result and
            "model" in result and
            "warnings" in result and
            "is_downgraded" in result
        )
        
        print_result(success, "RouteWithBudgetAwareness", result)
        return success
    except Exception as e:
        print(f"Error: {str(e)}")
        print_result(False, "RouteWithBudgetAwareness", {"error": str(e)})
        return False

async def test_get_usage_analytics(client: MCPClient):
    """Test GetUsageAnalytics tool."""
    print_section("Testing GetUsageAnalytics Tool")
    
    try:
        # Execute tool
        result = await client.execute_tool(
            "GetUsageAnalytics",
            {
                "period": "daily"
            }
        )
        
        # Check result
        success = result is not None
        
        print_result(success, "GetUsageAnalytics", result)
        return success
    except Exception as e:
        print(f"Error: {str(e)}")
        print_result(False, "GetUsageAnalytics", {"error": str(e)})
        return False

async def run_all_tests():
    """Run all FastMCP tests."""
    print(BANNER)
    
    # Get Budget URL from environment or use default
    budget_mcp_url = TektonEnviron.get("BUDGET_URL", budget_url("/mcp"))
    print(f"Connecting to Budget MCP at: {budget_mcp_url}")
    
    # Create MCP client
    client = MCPClient(
        component_id="test-client",
        mcp_url=budget_mcp_url,
        timeout=10.0
    )
    
    # Run tests
    results = []
    
    # Test capabilities and tools
    results.append(await test_get_capabilities(client))
    results.append(await test_get_tools(client))
    
    # Test budget management tools
    allocation_success, allocation_result = await test_allocate_budget(client)
    results.append(allocation_success)
    
    results.append(await test_check_budget(client))
    results.append(await test_record_usage(client, allocation_result))
    results.append(await test_get_budget_status(client))
    
    # Test model recommendation tools
    results.append(await test_get_model_recommendations(client))
    results.append(await test_route_with_budget_awareness(client))
    
    # Test analytics tools
    results.append(await test_get_usage_analytics(client))
    
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