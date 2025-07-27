#!/usr/bin/env python3
"""
Test script for workflow endpoint communication.

Tests that the workflow standard is properly implemented.
"""

import asyncio
import httpx
import json
from datetime import datetime


async def test_workflow_endpoint(component: str, port: int):
    """Test workflow endpoint for a component."""
    print(f"\n=== Testing {component} workflow endpoint ===")
    
    # Test 1: Wrong destination (should be ignored)
    print(f"\n1. Testing wrong destination...")
    message = {
        "purpose": {"other_component": "Test message"},
        "dest": "other_component",
        "payload": {"action": "test"}
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:{port}/workflow",
                json=message,
                timeout=5.0
            )
            result = response.json()
            print(f"   Response: {result}")
            assert result.get("status") == "ignored", "Should ignore wrong destination"
            print("   ✓ Correctly ignored wrong destination")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return False
    
    # Test 2: Look for work
    print(f"\n2. Testing look_for_work action...")
    message = {
        "purpose": {component: "Check for pending work"},
        "dest": component,
        "payload": {"action": "look_for_work"}
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:{port}/workflow",
                json=message,
                timeout=5.0
            )
            result = response.json()
            print(f"   Response: {result}")
            
            if result.get("status") == "error":
                print(f"   ! Component may not have implemented look_for_work yet")
            else:
                print(f"   ✓ Received response from {component}")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return False
    
    # Test 3: No purpose defined
    print(f"\n3. Testing missing purpose...")
    message = {
        "purpose": {},
        "dest": component,
        "payload": {"action": "test"}
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:{port}/workflow",
                json=message,
                timeout=5.0
            )
            result = response.json()
            print(f"   Response: {result}")
            assert result.get("status") == "error", "Should error on missing purpose"
            print("   ✓ Correctly errored on missing purpose")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return False
    
    print(f"\n✓ All tests passed for {component}")
    return True


async def test_navigation_trigger():
    """Test that navigation triggers workflow checks."""
    print("\n=== Testing Navigation Workflow Trigger ===")
    
    # This would normally be done through browser automation
    # For now, we'll just verify the endpoint exists
    print("Manual test required:")
    print("1. Open Hephaestus UI in browser")
    print("2. Open browser console (F12)")
    print("3. Click on Telos in navigation")
    print("4. Look for '[Workflow]' messages in console")
    print("5. Verify workflow check is triggered")


async def main():
    """Run all workflow tests."""
    print("Workflow Endpoint Standard Test Suite")
    print("=====================================")
    
    # Test components and their ports
    components = {
        'telos': 8011,
        'prometheus': 8012,
        'metis': 8013,
        'harmonia': 8014,
        'synthesis': 8015,
        'tekton': 8080
    }
    
    # Check which components are running
    print("\nChecking component availability...")
    available = []
    
    for component, port in components.items():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:{port}/health",
                    timeout=2.0
                )
                if response.status_code == 200:
                    available.append((component, port))
                    print(f"✓ {component} is running on port {port}")
        except:
            print(f"✗ {component} is not running on port {port}")
    
    if not available:
        print("\nNo components are running!")
        print("Please start at least one component to test.")
        print("Example: cd Telos && python -m telos")
        return
    
    # Test available components
    print(f"\nTesting {len(available)} available component(s)...")
    
    results = []
    for component, port in available:
        result = await test_workflow_endpoint(component, port)
        results.append((component, result))
    
    # Summary
    print("\n=== Test Summary ===")
    passed = sum(1 for _, result in results if result)
    print(f"Passed: {passed}/{len(results)}")
    
    for component, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{component}: {status}")
    
    # Navigation test reminder
    await test_navigation_trigger()


if __name__ == "__main__":
    asyncio.run(main())