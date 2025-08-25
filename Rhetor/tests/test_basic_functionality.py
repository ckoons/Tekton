#!/usr/bin/env python3
"""
Basic functionality test for Rhetor MCP integration.
Verifies that core features are working properly.
"""

import asyncio
import httpx
import json
import sys


async def test_basic_functionality():
    """Test basic MCP functionality."""
    base_url = "http://localhost:8003"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("\n" + "="*60)
        print("Rhetor Basic Functionality Test")
        print("="*60)
        
        passed_tests = 0
        total_tests = 0
        
        # 1. Test MCP health
        print("\n1. Testing MCP Service Health")
        total_tests += 1
        try:
            response = await client.get(f"{base_url}/api/mcp/v2/health")
            if response.status_code == 200:
                print("   ✓ MCP service is healthy")
                passed_tests += 1
            else:
                print(f"   ✗ Unexpected status: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # 2. Test capabilities
        print("\n2. Testing Capabilities Registration")
        total_tests += 1
        try:
            response = await client.get(f"{base_url}/api/mcp/v2/capabilities")
            if response.status_code == 200:
                data = response.json()
                cap_count = data.get('count', 0)
                if cap_count == 4:
                    print(f"   ✓ All {cap_count} capabilities registered correctly")
                    passed_tests += 1
                else:
                    print(f"   ✗ Expected 4 capabilities, found {cap_count}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # 3. Test tools listing
        print("\n3. Testing Tools Registration")
        total_tests += 1
        try:
            response = await client.get(f"{base_url}/api/mcp/v2/tools")
            if response.status_code == 200:
                data = response.json()
                tool_count = data.get('count', 0)
                if tool_count == 22:
                    print(f"   ✓ All {tool_count} tools registered correctly")
                    passed_tests += 1
                else:
                    print(f"   ✗ Expected 22 tools, found {tool_count}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # 4. Test one tool from each category
        print("\n4. Testing Tool Execution (One from each category)")
        
        # Test LLM Management tool
        print("\n   a) LLM Management - GetAvailableModels")
        total_tests += 1
        try:
            response = await client.post(
                f"{base_url}/api/mcp/v2/process",
                json={
                    "tool_name": "GetAvailableModels",
                    "arguments": {}
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    providers = data.get('result', {}).get('providers', {})
                    print(f"      ✓ Found {len(providers)} LLM providers")
                    passed_tests += 1
                else:
                    print(f"      ✗ Tool error: {data.get('error')}")
            else:
                print(f"      ✗ HTTP {response.status_code}")
        except Exception as e:
            print(f"      ✗ Error: {e}")
        
        # Test Prompt Engineering tool
        print("\n   b) Prompt Engineering - ValidatePromptSyntax")
        total_tests += 1
        try:
            response = await client.post(
                f"{base_url}/api/mcp/v2/process",
                json={
                    "tool_name": "ValidatePromptSyntax",
                    "arguments": {
                        "prompt_text": "Hello {name}, how are you?",
                        "template_variables": ["name"]
                    }
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    print(f"      ✓ Prompt validation executed successfully")
                    passed_tests += 1
                else:
                    print(f"      ✗ Tool error: {data.get('error')}")
            else:
                print(f"      ✗ HTTP {response.status_code}")
        except Exception as e:
            print(f"      ✗ Error: {e}")
        
        # Test Context Management tool
        print("\n   c) Context Management - AnalyzeContextUsage")
        total_tests += 1
        try:
            response = await client.post(
                f"{base_url}/api/mcp/v2/process",
                json={
                    "tool_name": "AnalyzeContextUsage",
                    "arguments": {
                        "context_id": "test",
                        "time_period": "last_hour"
                    }
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    print(f"      ✓ Context analysis executed successfully")
                    passed_tests += 1
                else:
                    print(f"      ✗ Tool error: {data.get('error')}")
            else:
                print(f"      ✗ HTTP {response.status_code}")
        except Exception as e:
            print(f"      ✗ Error: {e}")
        
        # Test CI Orchestration tool - Check live integration
        print("\n   d) CI Orchestration - ListAISpecialists (Live Integration Test)")
        total_tests += 1
        try:
            response = await client.post(
                f"{base_url}/api/mcp/v2/process",
                json={
                    "tool_name": "ListAISpecialists",
                    "arguments": {}
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    specialists = data.get('result', {}).get('specialists', [])
                    # Check if we got the expected specialists
                    specialist_ids = [s.get('specialist_id') for s in specialists]
                    expected_ids = ['rhetor-orchestrator', 'engram-memory']
                    
                    if all(sid in specialist_ids for sid in expected_ids):
                        print(f"      ✓ Live integration working - found {len(specialists)} specialists")
                        print(f"      ✓ Core specialists active: {', '.join(expected_ids)}")
                        passed_tests += 1
                    else:
                        print(f"      ⚠ Found specialists but missing expected ones")
                        print(f"        Expected: {expected_ids}")
                        print(f"        Found: {specialist_ids}")
                else:
                    print(f"      ✗ Tool error: {data.get('error')}")
            else:
                print(f"      ✗ HTTP {response.status_code}")
        except Exception as e:
            print(f"      ✗ Error: {e}")
        
        # Summary
        print("\n" + "="*60)
        print(f"Test Summary: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("✓ All basic functionality tests passed!")
        else:
            print(f"✗ {total_tests - passed_tests} tests failed")
        
        print("="*60)
        
        return passed_tests == total_tests


if __name__ == "__main__":
    success = asyncio.run(test_basic_functionality())
    sys.exit(0 if success else 1)