#!/usr/bin/env python3
"""
Test Dynamic Specialist Creation functionality.

This script tests the Phase 4B implementation of dynamic specialist creation,
including template listing, specialist creation, cloning, and lifecycle management.
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any


class DynamicSpecialistTester:
    def __init__(self, base_url: str = "http://localhost:8003"):
        self.base_url = base_url
        self.created_specialists = []  # Track created specialists for cleanup
        
    async def test_list_templates(self):
        """Test listing available specialist templates."""
        print("\n📋 Testing: List Specialist Templates")
        print("=" * 50)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/mcp/v2/process",
                json={
                    "tool_name": "ListSpecialistTemplates",
                    "arguments": {}
                }
            ) as response:
                result = await response.json()
                
                # Handle MCP response format
                if result.get("status") == "success" and "result" in result:
                    actual_result = result["result"]
                    success = actual_result.get("success", False)
                else:
                    success = False
                    actual_result = result
                    
                if success:
                    templates = actual_result.get("templates", [])
                    print(f"✅ Found {len(templates)} specialist templates:")
                    
                    # Group by type
                    grouped = actual_result.get("grouped_by_type", {})
                    for base_type, type_templates in grouped.items():
                        print(f"\n  {base_type.upper()} Specialists:")
                        for template in type_templates:
                            print(f"    - {template['template_id']}: {template['name']}")
                            print(f"      {template['description']}")
                else:
                    print(f"❌ Failed to list templates: {actual_result.get('error') or result.get('error')}")
                    
    async def test_create_specialist(self):
        """Test creating a dynamic specialist from template."""
        print("\n🚀 Testing: Create Dynamic Specialist")
        print("=" * 50)
        
        # Test creating a code reviewer
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/mcp/v2/process",
                json={
                    "tool_name": "CreateDynamicSpecialist",
                    "arguments": {
                        "template_id": "code-reviewer",
                        "specialist_name": "Python Expert Reviewer",
                        "customization": {
                            "temperature": 0.2,
                            "additional_traits": ["python-focused", "security-conscious"],
                            "additional_context": "Focus on Python best practices and security vulnerabilities"
                        },
                        "auto_activate": True
                    }
                }
            ) as response:
                result = await response.json()
                
                # Handle MCP response format
                if result.get("status") == "success" and "result" in result:
                    actual_result = result["result"]
                    success = actual_result.get("success", False)
                else:
                    success = False
                    actual_result = result
                    
                if success:
                    specialist_id = actual_result.get("specialist_id")
                    self.created_specialists.append(specialist_id)
                    
                    print(f"✅ Created specialist: {specialist_id}")
                    print(f"   Template: {actual_result.get('template_used')}")
                    print(f"   Status: {actual_result.get('status')}")
                    
                    if actual_result.get("activation_details"):
                        activation = actual_result["activation_details"]
                        print(f"   Activation time: {activation.get('activation_time', 0)}s")
                        print(f"   Ready for tasks: {activation.get('ready_for_tasks')}")
                        
                    return specialist_id
                else:
                    print(f"❌ Failed to create specialist: {actual_result.get('error') or result.get('error')}")
                    
        return None
        
    async def test_use_dynamic_specialist(self, specialist_id: str):
        """Test using a dynamically created specialist."""
        print(f"\n💬 Testing: Use Dynamic Specialist ({specialist_id})")
        print("=" * 50)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/mcp/v2/process",
                json={
                    "tool_name": "SendMessageToSpecialist",
                    "arguments": {
                        "specialist_id": specialist_id,
                        "message": "Please review this Python function for security issues:\n\ndef process_user_input(data):\n    exec(data['command'])\n    return 'Success'",
                        "message_type": "task_assignment"
                    }
                }
            ) as response:
                result = await response.json()
                
                # Handle MCP response format
                if result.get("status") == "success" and "result" in result:
                    actual_result = result["result"]
                    success = actual_result.get("success", False)
                else:
                    success = False
                    actual_result = result
                    
                if success:
                    print(f"✅ Message sent to specialist")
                    print(f"   Message ID: {actual_result.get('message_id')}")
                    
                    if actual_result.get("response"):
                        print(f"   Response: {actual_result['response'].get('content', 'No response')[:200]}...")
                else:
                    print(f"❌ Failed to send message: {actual_result.get('error') or result.get('error')}")
                    
    async def test_clone_specialist(self, source_id: str):
        """Test cloning an existing specialist."""
        print(f"\n🔄 Testing: Clone Specialist ({source_id})")
        print("=" * 50)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/mcp/v2/process",
                json={
                    "tool_name": "CloneSpecialist",
                    "arguments": {
                        "source_specialist_id": source_id,
                        "new_specialist_name": "Security-Focused Reviewer",
                        "modifications": {
                            "temperature": 0.1,
                            "personality_adjustments": {
                                "focus": "security vulnerabilities and code safety"
                            }
                        }
                    }
                }
            ) as response:
                result = await response.json()
                
                # Handle MCP response format
                if result.get("status") == "success" and "result" in result:
                    actual_result = result["result"]
                    success = actual_result.get("success", False)
                else:
                    success = False
                    actual_result = result
                    
                if success:
                    clone_id = actual_result.get("specialist_id")
                    self.created_specialists.append(clone_id)
                    
                    print(f"✅ Cloned specialist: {clone_id}")
                    print(f"   Cloned from: {actual_result.get('cloned_from')}")
                    print(f"   Status: {actual_result.get('status')}")
                    
                    return clone_id
                else:
                    print(f"❌ Failed to clone specialist: {actual_result.get('error') or result.get('error')}")
                    
        return None
        
    async def test_modify_specialist(self, specialist_id: str):
        """Test modifying a specialist's configuration."""
        print(f"\n⚙️ Testing: Modify Specialist ({specialist_id})")
        print("=" * 50)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/mcp/v2/process",
                json={
                    "tool_name": "ModifySpecialist",
                    "arguments": {
                        "specialist_id": specialist_id,
                        "modifications": {
                            "temperature": 0.8,
                            "max_tokens": 3000,
                            "system_prompt": "You are now a creative code reviewer who suggests innovative improvements."
                        }
                    }
                }
            ) as response:
                result = await response.json()
                
                # Handle MCP response format
                if result.get("status") == "success" and "result" in result:
                    actual_result = result["result"]
                    success = actual_result.get("success", False)
                else:
                    success = False
                    actual_result = result
                    
                if success:
                    print(f"✅ Modified specialist")
                    print(f"   Changes applied: {len(actual_result.get('modifications_applied', []))}")
                    for change in actual_result.get("modifications_applied", []):
                        print(f"   - {change}")
                else:
                    print(f"❌ Failed to modify specialist: {actual_result.get('error') or result.get('error')}")
                    
    async def test_specialist_metrics(self, specialist_id: str):
        """Test getting specialist metrics."""
        print(f"\n📊 Testing: Get Specialist Metrics ({specialist_id})")
        print("=" * 50)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/mcp/v2/process",
                json={
                    "tool_name": "GetSpecialistMetrics",
                    "arguments": {
                        "specialist_id": specialist_id
                    }
                }
            ) as response:
                result = await response.json()
                
                # Handle MCP response format
                if result.get("status") == "success" and "result" in result:
                    actual_result = result["result"]
                    success = actual_result.get("success", False)
                else:
                    success = False
                    actual_result = result
                    
                if success:
                    metrics = actual_result.get("metrics", {})
                    print(f"✅ Retrieved metrics:")
                    print(f"   Status: {metrics.get('status')}")
                    print(f"   Uptime: {metrics.get('uptime_seconds', 0)}s")
                    print(f"   Messages processed: {metrics.get('messages_processed', 0)}")
                    
                    model_usage = metrics.get("model_usage", {})
                    print(f"   Model: {model_usage.get('model')}")
                    print(f"   Tokens used: {model_usage.get('tokens_used', 0)}")
                else:
                    print(f"❌ Failed to get metrics: {actual_result.get('error') or result.get('error')}")
                    
    async def test_deactivate_specialist(self, specialist_id: str):
        """Test deactivating a specialist."""
        print(f"\n🛑 Testing: Deactivate Specialist ({specialist_id})")
        print("=" * 50)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/mcp/v2/process",
                json={
                    "tool_name": "DeactivateSpecialist",
                    "arguments": {
                        "specialist_id": specialist_id,
                        "preserve_history": True
                    }
                }
            ) as response:
                result = await response.json()
                
                # Handle MCP response format
                if result.get("status") == "success" and "result" in result:
                    actual_result = result["result"]
                    success = actual_result.get("success", False)
                else:
                    success = False
                    actual_result = result
                    
                if success:
                    print(f"✅ Deactivated specialist")
                    print(f"   Previous status: {actual_result.get('previous_status')}")
                    print(f"   Current status: {actual_result.get('current_status')}")
                    print(f"   History preserved: {actual_result.get('history_preserved')}")
                else:
                    print(f"❌ Failed to deactivate: {actual_result.get('error') or result.get('error')}")
                    
    async def cleanup(self):
        """Clean up created specialists."""
        if self.created_specialists:
            print(f"\n🧹 Cleaning up {len(self.created_specialists)} created specialists...")
            
            for specialist_id in self.created_specialists:
                await self.test_deactivate_specialist(specialist_id)
                
    async def run_all_tests(self):
        """Run all dynamic specialist tests."""
        print("\n🧪 Dynamic Specialist Creation Test Suite")
        print("=" * 70)
        print(f"Testing against: {self.base_url}")
        print(f"Started at: {datetime.now().isoformat()}")
        
        try:
            # Test 1: List templates
            await self.test_list_templates()
            
            # Test 2: Create specialist
            specialist_id = await self.test_create_specialist()
            
            if specialist_id:
                # Test 3: Use the specialist
                await self.test_use_dynamic_specialist(specialist_id)
                
                # Test 4: Get metrics
                await self.test_specialist_metrics(specialist_id)
                
                # Test 5: Clone the specialist
                clone_id = await self.test_clone_specialist(specialist_id)
                
                if clone_id:
                    # Test 6: Modify the clone
                    await self.test_modify_specialist(clone_id)
                
            # Cleanup
            await self.cleanup()
            
            print("\n✅ All tests completed!")
            
        except Exception as e:
            print(f"\n❌ Test suite failed: {e}")
            # Still try to cleanup
            await self.cleanup()


async def main():
    # Check if Rhetor is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8003/health") as response:
                if response.status != 200:
                    print("❌ Rhetor is not running. Please start it first.")
                    return
    except:
        print("❌ Cannot connect to Rhetor. Please start it with: cd Rhetor && ./run_rhetor.sh")
        return
    
    # Run tests
    tester = DynamicSpecialistTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())