#!/usr/bin/env python3
"""
Test the import chain for MCP bridges
"""

import sys
import os

# Add Tekton root to Python path (same as run script)
tekton_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, tekton_root)

def test_imports():
    """Test each import step."""
    print("🔍 Testing MCP Bridge Import Chain")
    print("=" * 40)
    
    try:
        print("1. Testing shared.mcp import...")
        from shared.mcp import MCPService, MCPConfig
        print("   ✅ shared.mcp imported successfully")
    except Exception as e:
        print(f"   ❌ shared.mcp failed: {e}")
        return False
    
    try:
        print("2. Testing HermesMCPClient import...")
        from shared.mcp.client import HermesMCPClient
        print("   ✅ HermesMCPClient imported successfully")
    except Exception as e:
        print(f"   ❌ HermesMCPClient failed: {e}")
        return False
    
    try:
        print("3. Testing shared.mcp.tools import...")
        from shared.mcp.tools import HealthCheckTool, ComponentInfoTool
        print("   ✅ MCP tools imported successfully")
    except Exception as e:
        print(f"   ❌ MCP tools failed: {e}")
        return False
    
    try:
        print("4. Testing MetisMCPBridge import...")
        from Metis.metis.core.mcp.hermes_bridge import MetisMCPBridge
        print("   ✅ MetisMCPBridge imported successfully")
    except Exception as e:
        print(f"   ❌ MetisMCPBridge failed: {e}")
        return False
    
    try:
        print("5. Testing MCPConfig.from_env...")
        config = MCPConfig.from_env("metis")
        print(f"   ✅ MCPConfig created: {config}")
    except Exception as e:
        print(f"   ❌ MCPConfig.from_env failed: {e}")
        return False
    
    try:
        print("6. Testing HermesMCPClient creation...")
        client = HermesMCPClient(
            component_name="metis",
            component_port=8011
        )
        print(f"   ✅ HermesMCPClient created: {client.mcp_base_url}")
    except Exception as e:
        print(f"   ❌ HermesMCPClient creation failed: {e}")
        return False
    
    print("\n✅ All imports successful!")
    return True

if __name__ == "__main__":
    test_imports()