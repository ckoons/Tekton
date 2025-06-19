"""
Acid Test for UI DevTools MCP
Task: Add a timestamp to Rhetor's footer
Success: Simple HTML addition
Failure: Installing React/frameworks
"""

import asyncio
import httpx
from datetime import datetime
import json

MCP_URL = "http://localhost:8088"


async def run_acid_test():
    print("UI DevTools MCP - Acid Test")
    print("===========================")
    print("Task: Add a timestamp to Rhetor's footer")
    print()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Analyze the UI first
        print("1. Analyzing Rhetor UI...")
        response = await client.post(
            f"{MCP_URL}/api/mcp/v2/execute",
            json={
                "tool_name": "ui_analyze",
                "arguments": {
                    "component": "rhetor",
                    "deep_scan": False
                }
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                analysis = data['result']['analysis']
                print(f"   - Total elements: {analysis['structure']['total_elements']}")
                print(f"   - Complexity: {analysis['complexity']['level']}")
                
                # Check for frameworks
                frameworks = analysis['frameworks']
                detected = [k for k, v in frameworks.items() if v]
                if detected:
                    print(f"   ⚠️  Frameworks detected: {', '.join(detected)}")
                else:
                    print(f"   ✓ No frameworks detected")
        
        # Step 2: Capture current footer state
        print("\n2. Capturing current footer state...")
        response = await client.post(
            f"{MCP_URL}/api/mcp/v2/execute",
            json={
                "tool_name": "ui_capture",
                "arguments": {
                    "component": "rhetor",
                    "selector": "footer, #footer, .footer, #rhetor-footer"
                }
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                result = data['result']
                print(f"   ✓ Found footer elements")
                if 'structure' in result:
                    print(f"   - Elements: {result['structure']['element_count']}")
        
        # Step 3: Test the change in sandbox
        print("\n3. Testing timestamp addition in sandbox...")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        response = await client.post(
            f"{MCP_URL}/api/mcp/v2/execute",
            json={
                "tool_name": "ui_sandbox",
                "arguments": {
                    "component": "rhetor",
                    "changes": [{
                        "type": "html",
                        "selector": "body",  # Using body since we don't know exact footer selector
                        "content": f'<div id="timestamp-footer" style="position: fixed; bottom: 10px; right: 10px; color: #666; font-size: 12px; z-index: 1000;">Last updated: {timestamp}</div>',
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
                
                # Check if changes were validated
                if result.get('validations'):
                    print("   - Validation results:")
                    for val in result['validations']:
                        if val['status'] == 'rejected':
                            print(f"     ✗ REJECTED: {val['reason']}")
                            print(f"       Patterns: {', '.join(val['patterns'][:3])}")
                            return False
                
                # Check sandbox results
                summary = result['summary']
                print(f"   ✓ Sandbox test: {summary['successful']}/{summary['total_changes']} successful")
                
                if summary['successful'] > 0:
                    print("\n4. ACID TEST PASSED! ✓")
                    print("   - Simple HTML timestamp added successfully")
                    print("   - No frameworks were harmed in this process")
                    print(f"   - Timestamp: {timestamp}")
                    
                    # Show how to apply for real
                    print("\n   To apply this change for real, use:")
                    print("   ui_sandbox(..., preview=False)")
                    
                    return True
                else:
                    print("\n4. ACID TEST FAILED ✗")
                    print("   - Could not add simple timestamp")
                    return False
        
        print("\n4. ACID TEST FAILED ✗")
        print("   - Unexpected error occurred")
        return False


async def test_bad_approach():
    """Test that React approach is correctly rejected"""
    print("\n\n5. Testing bad approach (should be rejected)...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{MCP_URL}/api/mcp/v2/execute",
            json={
                "tool_name": "ui_sandbox",
                "arguments": {
                    "component": "rhetor",
                    "changes": [{
                        "type": "html",
                        "selector": "head",
                        "content": '<script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>',
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
                
                # Should be rejected
                if result.get('error') and 'rejected' in result['error']:
                    print("   ✓ React correctly rejected!")
                    print("   - Framework detection working as intended")
                    return True
                else:
                    print("   ✗ React was NOT rejected - this is bad!")
                    return False
    
    return False


async def main():
    print("Starting UI DevTools MCP Acid Test...")
    print("=====================================")
    
    # Check if MCP is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MCP_URL}/health", timeout=5.0)
            if response.status_code != 200:
                print("✗ MCP server is not responding")
                print("  Please start with: ./run_mcp.sh")
                return
    except:
        print("✗ Cannot connect to MCP server")
        print("  Please start with: ./run_mcp.sh")
        return
    
    # Run the acid test
    passed = await run_acid_test()
    
    # Also test bad approach
    rejected = await test_bad_approach()
    
    # Final verdict
    print("\n" + "="*50)
    print("FINAL VERDICT:")
    if passed and rejected:
        print("✓ UI DevTools MCP is working correctly!")
        print("  - Can add simple HTML without frameworks")
        print("  - Correctly rejects framework additions")
        print("  - Casey's blood pressure should normalize")
    else:
        print("✗ UI DevTools MCP needs work")
        if not passed:
            print("  - Failed to add simple timestamp")
        if not rejected:
            print("  - Failed to reject framework additions")


if __name__ == "__main__":
    asyncio.run(main())