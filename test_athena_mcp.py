#!/usr/bin/env python3
"""
Test Athena MCP Tools via HTTP endpoints
"""

import httpx
import json

# Test the MCP endpoint directly
MCP_URL = "http://localhost:8005/mcp/v1/completion"

def test_mcp_tool(tool_name, parameters):
    """Test an MCP tool via HTTP"""
    request = {
        "tool": tool_name,
        "parameters": parameters
    }
    
    print(f"\n🔧 Testing {tool_name}...")
    print(f"Parameters: {json.dumps(parameters, indent=2)}")
    
    try:
        response = httpx.post(MCP_URL, json=request, timeout=10.0)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"Result: {json.dumps(result, indent=2)[:500]}...")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("Testing Athena MCP Tools")
    print("=" * 50)
    
    # Test 1: Search entities
    test_mcp_tool("SearchEntities", {
        "query": "Hermes",
        "limit": 5
    })
    
    # Test 2: Get entity by ID (using a component ID we know exists)
    test_mcp_tool("GetEntityById", {
        "entity_id": "8aa5804d-de7e-44b9-b4e3-8237fdcce21a"  # Hermes ID from our ingestion
    })
    
    # Test 3: Query knowledge graph
    test_mcp_tool("QueryKnowledgeGraph", {
        "query": "What components exist in Tekton?",
        "mode": "naive"
    })
    
    # Test 4: Get entity relationships
    test_mcp_tool("GetEntityRelationships", {
        "entity_id": "8aa5804d-de7e-44b9-b4e3-8237fdcce21a",
        "relationship_type": "contains_landmark"
    })
    
    print("\n" + "=" * 50)
    print("✅ MCP endpoint testing complete!")
    
    # Also test if tools are registered with Hermes
    print("\n📡 Checking Hermes MCP registry...")
    try:
        response = httpx.get("http://localhost:8001/mcp/tools")
        if response.status_code == 200:
            tools = response.json()
            athena_tools = [t for t in tools if t.startswith('athena_')]
            print(f"Found {len(athena_tools)} Athena tools registered with Hermes:")
            for tool in athena_tools[:5]:
                print(f"  - {tool}")
            if len(athena_tools) > 5:
                print(f"  ... and {len(athena_tools) - 5} more")
    except Exception as e:
        print(f"Could not check Hermes registry: {e}")

if __name__ == "__main__":
    main()