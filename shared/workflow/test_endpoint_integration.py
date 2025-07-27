#!/usr/bin/env python3
"""
Test script to verify the standardized /workflow endpoints work correctly
across all Tekton components.
"""

import requests
import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_workflow_endpoint(component_name: str, port: int):
    """Test the /workflow endpoint for a component."""
    
    # Create the test message
    test_message = {
        "purpose": "check_work",
        "dest": component_name,
        "payload": {
            "component": component_name,
            "action": "look_for_work"
        }
    }
    
    url = f"http://localhost:{port}/workflow"
    
    try:
        print(f"Testing {component_name} on port {port}...")
        
        response = requests.post(
            url,
            json=test_message,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {component_name}: {result.get('status', 'unknown')}")
            print(f"   Work available: {result.get('work_available', False)}")
            print(f"   Work count: {result.get('work_count', 0)}")
            return True
        else:
            print(f"❌ {component_name}: HTTP {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Error: {error_detail}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"🔌 {component_name}: Not running (connection refused)")
        return False
    except requests.exceptions.Timeout:
        print(f"⏱️ {component_name}: Timeout")
        return False
    except Exception as e:
        print(f"❌ {component_name}: Error - {e}")
        return False

def main():
    """Test workflow endpoints for all Planning Team components."""
    
    # Component name to port mapping (from env.js)
    components = {
        "telos": 8020,
        "prometheus": 8021, 
        "metis": 8022,
        "harmonia": 8023,
        "synthesis": 8024
    }
    
    print("Testing standardized /workflow endpoints...")
    print("=" * 50)
    
    success_count = 0
    total_count = len(components)
    
    for component_name, port in components.items():
        if test_workflow_endpoint(component_name, port):
            success_count += 1
        print()
    
    print("=" * 50)
    print(f"Results: {success_count}/{total_count} components responding")
    
    if success_count == total_count:
        print("🎉 All components have working /workflow endpoints!")
        return 0
    else:
        print("⚠️ Some components are not responding or have issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())