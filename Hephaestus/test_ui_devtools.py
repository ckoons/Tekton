"""
Test script for Hephaestus UI DevTools MCP
"""

import asyncio
import json
import httpx
from datetime import datetime

MCP_URL = "http://localhost:8088"


async def test_capabilities():
    """Test getting MCP capabilities"""
    print("\n=== Testing MCP Capabilities ===")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{MCP_URL}/api/mcp/v2/capabilities")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Component: {data['name']}")
            print(f"✓ Version: {data['version']}")
            print(f"✓ Tools: {', '.join(data['tools'])}")
            return True
        else:
            print(f"✗ Failed to get capabilities: {response.status_code}")
            return False


async def test_tools():
    """Test getting tool metadata"""
    print("\n=== Testing Tool Metadata ===")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{MCP_URL}/api/mcp/v2/tools")
        if response.status_code == 200:
            data = response.json()
            for tool_name, tool_info in data['tools'].items():
                print(f"✓ {tool_name}: {tool_info['description']}")
            return True
        else:
            print(f"✗ Failed to get tools: {response.status_code}")
            return False


async def test_ui_capture():
    """Test ui_capture tool"""
    print("\n=== Testing ui_capture ===")
    async with httpx.AsyncClient() as client:
        # Test capturing Rhetor's UI
        request_data = {
            "tool_name": "ui_capture",
            "arguments": {
                "component": "rhetor",
                "selector": "#rhetor-component"
            }
        }
        
        response = await client.post(
            f"{MCP_URL}/api/mcp/v2/execute",
            json=request_data,
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                result = data['result']
                print(f"✓ Captured {result['component']} UI")
                print(f"  - URL: {result['url']}")
                print(f"  - Structure: {result['structure']['element_count']} elements")
                if 'forms' in result:
                    print(f"  - Forms: {len(result['forms'])}")
                if 'buttons' in result:
                    print(f"  - Buttons: {len(result['buttons'])}")
                return True
            else:
                print(f"✗ Tool execution failed: {data['error']}")
                return False
        else:
            print(f"✗ Request failed: {response.status_code}")
            return False


async def test_ui_analyze():
    """Test ui_analyze tool"""
    print("\n=== Testing ui_analyze ===")
    async with httpx.AsyncClient() as client:
        request_data = {
            "tool_name": "ui_analyze",
            "arguments": {
                "component": "rhetor",
                "deep_scan": True
            }
        }
        
        response = await client.post(
            f"{MCP_URL}/api/mcp/v2/execute",
            json=request_data,
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                result = data['result']
                analysis = result['analysis']
                
                print(f"✓ Analyzed {result['component']} UI")
                print(f"  - Total elements: {analysis['structure']['total_elements']}")
                print(f"  - Complexity: {analysis['complexity']['level']} (score: {analysis['complexity']['score']})")
                
                # Check for frameworks
                frameworks = analysis['frameworks']
                detected = [k for k, v in frameworks.items() if v]
                if detected:
                    print(f"  ⚠ Frameworks detected: {', '.join(detected)}")
                else:
                    print(f"  ✓ No frameworks detected")
                
                # Show recommendations
                if result.get('recommendations'):
                    print("  - Recommendations:")
                    for rec in result['recommendations']:
                        print(f"    • [{rec['type']}] {rec['message']}")
                
                return True
            else:
                print(f"✗ Tool execution failed: {data['error']}")
                return False
        else:
            print(f"✗ Request failed: {response.status_code}")
            return False


async def test_ui_sandbox():
    """Test ui_sandbox tool"""
    print("\n=== Testing ui_sandbox ===")
    async with httpx.AsyncClient() as client:
        # Test adding a simple timestamp to footer
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        request_data = {
            "tool_name": "ui_sandbox",
            "arguments": {
                "component": "rhetor",
                "changes": [
                    {
                        "type": "html",
                        "selector": "#rhetor-footer",
                        "content": f'<span id="timestamp" style="color: #666; font-size: 12px;">{timestamp}</span>',
                        "action": "append"
                    }
                ],
                "preview": True  # Just preview, don't apply
            }
        }
        
        response = await client.post(
            f"{MCP_URL}/api/mcp/v2/execute",
            json=request_data,
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                result = data['result']
                print(f"✓ Sandboxed changes for {result['component']}")
                
                # Check validations
                if result['validations']:
                    print("  - Validations:")
                    for val in result['validations']:
                        print(f"    • Change {val['change_index']}: {val['status']} - {val['reason']}")
                
                # Check results
                summary = result['summary']
                print(f"  - Summary: {summary['successful']}/{summary['total_changes']} successful")
                
                if result.get('error'):
                    print(f"  ⚠ Error: {result['error']}")
                    return False
                
                return summary['successful'] > 0
            else:
                print(f"✗ Tool execution failed: {data['error']}")
                return False
        else:
            print(f"✗ Request failed: {response.status_code}")
            return False


async def test_dangerous_pattern_detection():
    """Test that dangerous patterns are detected and rejected"""
    print("\n=== Testing Dangerous Pattern Detection ===")
    async with httpx.AsyncClient() as client:
        # Try to add React
        request_data = {
            "tool_name": "ui_sandbox",
            "arguments": {
                "component": "rhetor",
                "changes": [
                    {
                        "type": "html",
                        "selector": "body",
                        "content": '<script>import React from "react"; ReactDOM.render(<App />, document.getElementById("root"));</script>',
                        "action": "append"
                    }
                ],
                "preview": True
            }
        }
        
        response = await client.post(
            f"{MCP_URL}/api/mcp/v2/execute",
            json=request_data,
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                result = data['result']
                
                # Should be rejected
                if result.get('error') and 'rejected' in result['error']:
                    print("✓ Dangerous patterns correctly rejected")
                    if result.get('validations'):
                        for val in result['validations']:
                            if val['status'] == 'rejected':
                                print(f"  - Detected: {', '.join(val['patterns'][:3])}")
                    return True
                else:
                    print("✗ Dangerous patterns were not rejected!")
                    return False
            else:
                print(f"✗ Tool execution failed: {data['error']}")
                return False
        else:
            print(f"✗ Request failed: {response.status_code}")
            return False


async def main():
    """Run all tests"""
    print("Hephaestus UI DevTools MCP Test Suite")
    print("=====================================")
    print(f"Testing MCP at: {MCP_URL}")
    
    # Wait a bit for server to be ready
    print("\nWaiting for MCP server to be ready...")
    await asyncio.sleep(2)
    
    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MCP_URL}/health", timeout=5.0)
            if response.status_code != 200:
                print("✗ MCP server is not responding at expected URL")
                print("  Please start the MCP server with: ./run_mcp.sh")
                return
    except Exception as e:
        print(f"✗ Cannot connect to MCP server: {e}")
        print("  Please start the MCP server with: ./run_mcp.sh")
        return
    
    # Run tests
    tests = [
        test_capabilities,
        test_tools,
        test_ui_capture,
        test_ui_analyze,
        test_ui_sandbox,
        test_dangerous_pattern_detection
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n=== Test Summary ===")
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed! The UI DevTools MCP is working correctly.")
    else:
        print(f"\n✗ {total - passed} tests failed. Please check the output above.")


if __name__ == "__main__":
    asyncio.run(main())