#!/usr/bin/env python3
"""
Simple integration test to validate the workflow endpoint works.
"""

import sys
import os
import json
from fastapi import FastAPI
import httpx

# Add shared directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from endpoint_template import create_workflow_endpoint

def test_apollo_workflow_endpoint():
    """Test the workflow endpoint for Apollo component."""
    
    # Create test app
    app = FastAPI()
    
    # Add workflow endpoint for Apollo
    workflow_router = create_workflow_endpoint("apollo")
    app.include_router(workflow_router)
    
    # Get the router and extract the endpoint function
    router = create_workflow_endpoint("apollo")
    workflow_endpoint = None
    for route in router.routes:
        if hasattr(route, 'endpoint'):
            workflow_endpoint = route.endpoint
            break
    
    # Test message
    test_message = {
        "purpose": "check_work",
        "dest": "apollo",
        "payload": {
            "component": "apollo",
            "action": "look_for_work"
        }
    }
    
    # Call endpoint directly
    import asyncio
    result = asyncio.run(workflow_endpoint(test_message))
    
    print("Apollo workflow endpoint test:")
    print(f"Status: {result['status']}")
    print(f"Component: {result['component']}")
    print(f"Work available: {result['work_available']}")
    print(f"Work count: {result['work_count']}")
    
    assert result["status"] == "success"
    assert result["component"] == "apollo"
    assert "work_available" in result
    assert "work_count" in result
    assert "work_items" in result
    
    print("✅ Apollo workflow endpoint working correctly!")

if __name__ == "__main__":
    test_apollo_workflow_endpoint()
    print("\n🎉 Integration test passed!")