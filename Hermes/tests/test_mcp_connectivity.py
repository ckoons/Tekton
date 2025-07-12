#!/usr/bin/env python3
"""
Test script for Hermes MCP connectivity.

This script tests the MCP endpoints and verifies that the service is working correctly
after the Phase 1 fixes from YetAnotherMCP Sprint.
"""

import asyncio
import sys
import logging
import json
import aiohttp
from datetime import datetime
from shared.env import TektonEnviron
from shared.urls import tekton_url

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp_test")

# Add proper imports for Tekton environment
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from shared.utils.env_config import get_component_config
    config = get_component_config()
    HERMES_PORT = config.hermes.port
except (ImportError, AttributeError) as e:
    # Must get from environment - no hardcoded fallback
    hermes_port_str = TektonEnviron.get("HERMES_PORT")
    if not hermes_port_str:
        logger.error("HERMES_PORT not found in environment")
        sys.exit(1)
    HERMES_PORT = int(hermes_port_str)

# Hermes URL
HERMES_URL = tekton_url("hermes")
MCP_V2_BASE = tekton_url("hermes", "/api/mcp/v2")

# Test results
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}


async def test_mcp_health_endpoint():
    """Test the MCP health endpoint."""
    test_name = "MCP Health Endpoint"
    logger.info(f"Testing {test_name}...")
    
    async with aiohttp.ClientSession() as session:
        url = f"{MCP_V2_BASE}/health"
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    logger.info(f"✅ {test_name} passed: {json.dumps(data, indent=2)}")
                    test_results["passed"] += 1
                    test_results["tests"].append({
                        "name": test_name,
                        "status": "passed",
                        "response": data
                    })
                    return True
                else:
                    logger.error(f"❌ {test_name} failed: HTTP {resp.status}")
                    test_results["failed"] += 1
                    test_results["tests"].append({
                        "name": test_name,
                        "status": "failed",
                        "error": f"HTTP {resp.status}"
                    })
                    return False
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {e}")
            test_results["failed"] += 1
            test_results["tests"].append({
                "name": test_name,
                "status": "failed",
                "error": str(e)
            })
            return False


async def test_mcp_capabilities_endpoint():
    """Test the MCP capabilities endpoint."""
    test_name = "MCP Capabilities Endpoint"
    logger.info(f"Testing {test_name}...")
    
    async with aiohttp.ClientSession() as session:
        url = f"{MCP_V2_BASE}/capabilities"
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    logger.info(f"✅ {test_name} passed")
                    logger.info(f"Capabilities: {json.dumps(data, indent=2)}")
                    test_results["passed"] += 1
                    test_results["tests"].append({
                        "name": test_name,
                        "status": "passed",
                        "response": data
                    })
                    return True
                else:
                    error_text = await resp.text()
                    logger.error(f"❌ {test_name} failed: HTTP {resp.status} - {error_text}")
                    test_results["failed"] += 1
                    test_results["tests"].append({
                        "name": test_name,
                        "status": "failed",
                        "error": f"HTTP {resp.status}: {error_text}"
                    })
                    return False
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {e}")
            test_results["failed"] += 1
            test_results["tests"].append({
                "name": test_name,
                "status": "failed",
                "error": str(e)
            })
            return False


async def test_mcp_tools_endpoint():
    """Test the MCP tools endpoint."""
    test_name = "MCP Tools Endpoint"
    logger.info(f"Testing {test_name}...")
    
    async with aiohttp.ClientSession() as session:
        url = f"{MCP_V2_BASE}/tools"
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    logger.info(f"✅ {test_name} passed")
                    logger.info(f"Found {len(data) if isinstance(data, list) else 0} tools")
                    if isinstance(data, list) and len(data) > 0:
                        logger.info("Sample tools:")
                        for tool in data[:3]:  # Show first 3 tools
                            logger.info(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                    test_results["passed"] += 1
                    test_results["tests"].append({
                        "name": test_name,
                        "status": "passed",
                        "tool_count": len(data) if isinstance(data, list) else 0
                    })
                    return True
                else:
                    error_text = await resp.text()
                    logger.error(f"❌ {test_name} failed: HTTP {resp.status} - {error_text}")
                    test_results["failed"] += 1
                    test_results["tests"].append({
                        "name": test_name,
                        "status": "failed",
                        "error": f"HTTP {resp.status}: {error_text}"
                    })
                    return False
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {e}")
            test_results["failed"] += 1
            test_results["tests"].append({
                "name": test_name,
                "status": "failed",
                "error": str(e)
            })
            return False


async def test_hermes_registration_endpoint():
    """Test that Hermes itself is properly registered."""
    test_name = "Hermes Registration Status"
    logger.info(f"Testing {test_name}...")
    
    async with aiohttp.ClientSession() as session:
        url = f"{HERMES_URL}/api/v1/registry"
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Look for MCP service registration
                    mcp_service = None
                    for component_id, component_data in data.items():
                        if "mcp-service" in component_id or component_data.get("name") == "Hermes MCP Service":
                            mcp_service = component_data
                            break
                    
                    if mcp_service:
                        logger.info(f"✅ {test_name} passed: MCP service is registered")
                        logger.info(f"MCP Service endpoint: {mcp_service.get('endpoint', 'Unknown')}")
                        test_results["passed"] += 1
                        test_results["tests"].append({
                            "name": test_name,
                            "status": "passed",
                            "mcp_service": mcp_service
                        })
                        return True
                    else:
                        logger.warning(f"⚠️  {test_name}: MCP service not found in registry")
                        test_results["failed"] += 1
                        test_results["tests"].append({
                            "name": test_name,
                            "status": "failed",
                            "error": "MCP service not found in registry"
                        })
                        return False
                else:
                    logger.error(f"❌ {test_name} failed: HTTP {resp.status}")
                    test_results["failed"] += 1
                    test_results["tests"].append({
                        "name": test_name,
                        "status": "failed",
                        "error": f"HTTP {resp.status}"
                    })
                    return False
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {e}")
            test_results["failed"] += 1
            test_results["tests"].append({
                "name": test_name,
                "status": "failed",
                "error": str(e)
            })
            return False


async def test_old_mcp_endpoint():
    """Test that the old MCP endpoint is no longer accessible."""
    test_name = "Old MCP Endpoint (Should Fail)"
    logger.info(f"Testing {test_name}...")
    
    async with aiohttp.ClientSession() as session:
        url = f"{HERMES_URL}/mcp/health"  # Old endpoint
        try:
            async with session.get(url) as resp:
                if resp.status == 404:
                    logger.info(f"✅ {test_name} passed: Old endpoint correctly returns 404")
                    test_results["passed"] += 1
                    test_results["tests"].append({
                        "name": test_name,
                        "status": "passed",
                        "note": "Old endpoint correctly not found"
                    })
                    return True
                else:
                    logger.warning(f"⚠️  {test_name}: Old endpoint still accessible (HTTP {resp.status})")
                    test_results["failed"] += 1
                    test_results["tests"].append({
                        "name": test_name,
                        "status": "failed",
                        "error": f"Old endpoint returned HTTP {resp.status}"
                    })
                    return False
        except Exception as e:
            # Connection error is expected for non-existent endpoint
            logger.info(f"✅ {test_name} passed: Old endpoint not accessible")
            test_results["passed"] += 1
            test_results["tests"].append({
                "name": test_name,
                "status": "passed",
                "note": "Old endpoint not accessible"
            })
            return True


async def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("Testing Hermes MCP Connectivity - Phase 1 Verification")
    logger.info(f"Target: {MCP_V2_BASE}")
    logger.info(f"Time: {datetime.now().isoformat()}")
    logger.info("=" * 60)
    logger.info("")
    
    # Check if Hermes is running
    logger.info("Checking if Hermes is running...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{HERMES_URL}/health") as resp:
                if resp.status != 200:
                    logger.error("❌ Hermes is not running or not healthy")
                    logger.error("Please start Hermes before running this test:")
                    logger.error("  ./scripts/enhanced_tekton_launcher.py")
                    return 1
                else:
                    logger.info("✅ Hermes is running and healthy")
    except Exception as e:
        logger.error(f"❌ Cannot connect to Hermes: {e}")
        logger.error("Please start Hermes before running this test:")
        logger.error("  ./scripts/enhanced_tekton_launcher.py")
        return 1
    
    logger.info("")
    
    # Run all tests
    tests = [
        test_mcp_health_endpoint,
        test_mcp_capabilities_endpoint,
        test_mcp_tools_endpoint,
        test_hermes_registration_endpoint,
        test_old_mcp_endpoint
    ]
    
    for test in tests:
        await test()
        logger.info("")
    
    # Summary
    logger.info("=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    logger.info(f"Total tests: {test_results['passed'] + test_results['failed']}")
    logger.info(f"Passed: {test_results['passed']} ✅")
    logger.info(f"Failed: {test_results['failed']} ❌")
    logger.info("")
    
    if test_results["failed"] == 0:
        logger.info("🎉 All tests passed! Phase 1 fixes are working correctly.")
        return 0
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)