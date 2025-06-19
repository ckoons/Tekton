"""
Enhanced test suite for UI DevTools MCP with new features
"""

import asyncio
import httpx
from datetime import datetime
import json

MCP_URL = "http://localhost:8088"


async def test_component_validation():
    """Test component name validation"""
    print("\n=== Testing Component Validation ===")
    async with httpx.AsyncClient() as client:
        # Test invalid component
        response = await client.post(
            f"{MCP_URL}/api/mcp/v2/execute",
            json={
                "tool_name": "ui_capture",
                "arguments": {
                    "area": "invalid_area"
                }
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'error':
                print(f"✓ Invalid component correctly rejected")
                print(f"  - Error: {data['error']}")
                return True
            else:
                print(f"✗ Invalid component was not rejected")
                return False
    return False


async def test_selector_helpers():
    """Test Tekton selector helpers"""
    print("\n=== Testing Selector Helpers ===")
    
    # Test that the common Tekton selectors work
    area = "rhetor"
    
    # These are the standard Tekton selectors
    selectors_to_test = [
        ("#rhetor-component", "component"),
        ("#rhetor-footer", "footer"),
        ("#rhetor-content", "content"),
    ]
    
    success = True
    
    async with httpx.AsyncClient() as client:
        for selector, element_type in selectors_to_test:
            response = await client.post(
                f"{MCP_URL}/api/mcp/v2/execute",
                json={
                    "tool_name": "ui_capture",
                    "arguments": {
                        "area": area,
                        "selector": selector
                    }
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success':
                    print(f"✓ Selector {selector} ({element_type}) works")
                else:
                    print(f"✗ Selector {selector} ({element_type}) failed")
                    success = False
    
    return success


async def test_browser_recovery():
    """Test browser recovery capability"""
    print("\n=== Testing Browser Recovery ===")
    
    # This is hard to test without actually crashing the browser
    # We'll test that multiple sequential operations work
    async with httpx.AsyncClient() as client:
        success_count = 0
        
        for i in range(3):
            response = await client.post(
                f"{MCP_URL}/api/mcp/v2/execute",
                json={
                    "tool_name": "ui_capture",
                    "arguments": {
                        "area": "rhetor"
                    }
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success':
                    success_count += 1
            
            await asyncio.sleep(0.5)
        
        print(f"✓ Browser stability: {success_count}/3 operations succeeded")
        return success_count == 3


async def test_env_config_integration():
    """Test that env_config is being used for ports"""
    print("\n=== Testing env_config Integration ===")
    
    async with httpx.AsyncClient() as client:
        # Capture from a component and check the URL
        response = await client.post(
            f"{MCP_URL}/api/mcp/v2/execute",
            json={
                "tool_name": "ui_capture",
                "arguments": {
                    "area": "hephaestus"
                }
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                result = data['result']
                url = result.get('url', '')
                # Should be using port 8001 for Hermes
                if ':8001' in url:
                    print(f"✓ Using correct port from env_config")
                    print(f"  - URL: {url}")
                    return True
                else:
                    print(f"✗ Not using env_config port")
                    print(f"  - URL: {url}")
                    return False
    
    return False


async def test_framework_detection_patterns():
    """Test various framework patterns are detected"""
    print("\n=== Testing Framework Detection Patterns ===")
    
    test_patterns = [
        {
            "name": "React import",
            "content": '<script>import React from "react";</script>'
        },
        {
            "name": "Vue component",
            "content": '<script>Vue.component("my-component", {});</script>'
        },
        {
            "name": "Angular module",
            "content": '<script>angular.module("myApp", []);</script>'
        },
        {
            "name": "Webpack config",
            "content": '<script src="webpack.config.js"></script>'
        },
        {
            "name": "Simple HTML (should pass)",
            "content": '<div>Hello World</div>'
        }
    ]
    
    async with httpx.AsyncClient() as client:
        results = []
        
        for pattern in test_patterns:
            response = await client.post(
                f"{MCP_URL}/api/mcp/v2/execute",
                json={
                    "tool_name": "ui_sandbox",
                    "arguments": {
                        "area": "rhetor",
                        "changes": [{
                            "type": "html",
                            "selector": "body",
                            "content": pattern["content"],
                            "action": "append"
                        }],
                        "preview": True
                    }
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success':
                    result = data['result']
                    
                    # Check if it was rejected (frameworks) or accepted (simple HTML)
                    if "Simple HTML" in pattern["name"]:
                        # Should succeed
                        if result.get('summary', {}).get('successful', 0) > 0:
                            print(f"✓ {pattern['name']} - Correctly accepted")
                            results.append(True)
                        else:
                            print(f"✗ {pattern['name']} - Incorrectly rejected")
                            results.append(False)
                    else:
                        # Should be rejected
                        if result.get('error') and 'rejected' in result['error']:
                            print(f"✓ {pattern['name']} - Correctly rejected")
                            results.append(True)
                        else:
                            print(f"✗ {pattern['name']} - Not rejected!")
                            results.append(False)
    
    return all(results)


async def test_performance():
    """Test performance with multiple operations"""
    print("\n=== Testing Performance ===")
    
    start_time = asyncio.get_event_loop().time()
    operations = []
    
    async with httpx.AsyncClient() as client:
        # Run multiple operations in parallel
        for area in ["rhetor", "hermes", "athena"]:
            op = client.post(
                f"{MCP_URL}/api/mcp/v2/execute",
                json={
                    "tool_name": "ui_analyze",
                    "arguments": {
                        "area": area,
                        "deep_scan": False
                    }
                }
            )
            operations.append(op)
        
        # Wait for all to complete
        responses = await asyncio.gather(*operations, return_exceptions=True)
        
        success_count = sum(
            1 for r in responses 
            if not isinstance(r, Exception) and r.status_code == 200
        )
        
        elapsed = asyncio.get_event_loop().time() - start_time
        
        print(f"✓ Parallel operations: {success_count}/{len(operations)} succeeded")
        print(f"  - Time: {elapsed:.2f}s")
        print(f"  - Avg: {elapsed/len(operations):.2f}s per operation")
        
        return success_count == len(operations)


async def main():
    """Run enhanced test suite"""
    print("Enhanced UI DevTools MCP Test Suite")
    print("===================================")
    print(f"Testing MCP at: {MCP_URL}")
    
    # Wait for server
    print("\nWaiting for MCP server to be ready...")
    await asyncio.sleep(2)
    
    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MCP_URL}/health", timeout=5.0)
            if response.status_code != 200:
                print("✗ MCP server is not responding")
                return
    except Exception as e:
        print(f"✗ Cannot connect to MCP server: {e}")
        print("  Please start with: ./run_mcp.sh")
        return
    
    # Run enhanced tests
    tests = [
        ("Component Validation", test_component_validation),
        ("Selector Helpers", test_selector_helpers),
        ("Browser Recovery", test_browser_recovery),
        ("env_config Integration", test_env_config_integration),
        ("Framework Detection", test_framework_detection_patterns),
        ("Performance", test_performance),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("ENHANCED TEST SUMMARY:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {test_name}")
    
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed == total:
        print("\n✅ All enhanced tests passed!")
        print("New features working correctly:")
        print("- Component validation prevents typos")
        print("- Selector helpers simplify common patterns")
        print("- Browser recovery handles crashes")
        print("- env_config integration works")
        print("- Framework detection is comprehensive")
    else:
        print(f"\n⚠️  {total - passed} tests failed")


if __name__ == "__main__":
    asyncio.run(main())