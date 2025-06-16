#!/usr/bin/env python3
"""
Test script for Rhetor FastMCP implementation.

This script tests the FastMCP integration with Rhetor LLM management, prompt engineering,
and context management to ensure all tools work correctly.
"""

import asyncio
import aiohttp
import json
import sys
from typing import Dict, Any, List


# Configuration
RHETOR_BASE_URL = "http://localhost:8003"  # Default Rhetor port
MCP_BASE_URL = f"{RHETOR_BASE_URL}/api/mcp/v2"


class RhetorMCPTester:
    """Test class for Rhetor MCP functionality."""
    
    def __init__(self):
        """Initialize the tester."""
        self.session = None
        self.created_template_ids = []
        self.test_context_ids = []
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make an HTTP request and return JSON response."""
        try:
            async with self.session.request(method, url, **kwargs) as response:
                if response.content_type == 'application/json':
                    return await response.json()
                else:
                    text = await response.text()
                    return {
                        "success": False,
                        "error": f"Non-JSON response: {text}",
                        "status_code": response.status
                    }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_health_check(self) -> bool:
        """Test basic health check."""
        print("Testing health check...")
        
        response = await self.make_request("GET", f"{RHETOR_BASE_URL}/health")
        
        if response.get("status") == "healthy":
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response}")
            return False
    
    async def test_mcp_status(self) -> bool:
        """Test MCP status endpoint."""
        print("Testing MCP status...")
        
        response = await self.make_request("GET", f"{MCP_BASE_URL}/health")
        
        if response.get("success"):
            print("✅ MCP health check passed")
            print(f"   Available capabilities: {response.get('capabilities', [])}")
            print(f"   Available tools: {response.get('tools', [])}")
            return True
        else:
            print(f"❌ MCP health check failed: {response}")
            return False
    
    async def test_mcp_capabilities(self) -> bool:
        """Test MCP capabilities endpoint."""
        print("Testing MCP capabilities...")
        
        response = await self.make_request("GET", f"{MCP_BASE_URL}/capabilities")
        
        if response.get("success"):
            capabilities = response.get("capabilities", [])
            expected_capabilities = [
                "llm_management",
                "prompt_engineering",
                "context_management"
            ]
            
            for cap in expected_capabilities:
                if cap in [c["name"] for c in capabilities]:
                    print(f"✅ Capability '{cap}' found")
                else:
                    print(f"❌ Capability '{cap}' missing")
                    return False
            
            return True
        else:
            print(f"❌ MCP capabilities test failed: {response}")
            return False
    
    async def test_get_available_models(self) -> bool:
        """Test getting available models via MCP."""
        print("Testing get available models...")
        
        request_data = {
            "tool_name": "get_available_models",
            "arguments": {}
        }
        
        response = await self.make_request(
            "POST", 
            f"{MCP_BASE_URL}/process",
            json=request_data
        )
        
        if response.get("success") and response.get("result", {}).get("success"):
            result = response["result"]
            providers = result["providers"]
            print(f"✅ Available models retrieved successfully")
            print(f"   Total providers: {result['total_providers']}")
            print(f"   Total models: {result['total_models']}")
            print(f"   Providers: {list(providers.keys())}")
            return True
        else:
            print(f"❌ Get available models failed: {response}")
            return False
    
    async def test_model_capabilities(self) -> bool:
        """Test getting model capabilities via MCP."""
        print("Testing model capabilities...")
        
        request_data = {
            "tool_name": "get_model_capabilities",
            "arguments": {
                "provider_id": "anthropic",
                "model_id": "claude-3-sonnet"
            }
        }
        
        response = await self.make_request(
            "POST",
            f"{MCP_BASE_URL}/process", 
            json=request_data
        )
        
        if response.get("success") and response.get("result", {}).get("success"):
            result = response["result"]
            capabilities = result["capabilities"]
            print(f"✅ Model capabilities retrieved successfully")
            print(f"   Model: {result['provider']}/{result['model']}")
            print(f"   Max tokens: {capabilities['max_tokens']}")
            print(f"   Supports streaming: {capabilities['supports_streaming']}")
            return True
        else:
            print(f"❌ Model capabilities test failed: {response}")
            return False
    
    async def test_model_connection(self) -> bool:
        """Test model connection via MCP."""
        print("Testing model connection...")
        
        request_data = {
            "tool_name": "test_model_connection",
            "arguments": {
                "provider_id": "ollama",
                "model_id": "llama2"
            }
        }
        
        response = await self.make_request(
            "POST",
            f"{MCP_BASE_URL}/process",
            json=request_data
        )
        
        if response.get("success"):  # Connection test can succeed or fail
            result = response["result"]
            if result.get("success"):
                print(f"✅ Model connection test successful")
                print(f"   Model: {result['provider']}/{result['model']}")
                print(f"   Response time: {result['response_time']:.2f}s")
                print(f"   Connection quality: {result['connection_quality']}")
            else:
                print(f"⚠️ Model connection test failed (this is normal if model is not available)")
                print(f"   Error: {result.get('error', 'Unknown error')}")
            return True
        else:
            print(f"❌ Model connection test endpoint failed: {response}")
            return False
    
    async def test_create_prompt_template(self) -> bool:
        """Test prompt template creation via MCP."""
        print("Testing prompt template creation...")
        
        request_data = {
            "tool_name": "create_prompt_template",
            "arguments": {
                "name": "Test Analysis Template",
                "template": "Analyze the following {data_type}: {input_data}\n\nPlease provide:\n1. Key insights\n2. Recommendations\n3. Next steps",
                "variables": ["data_type", "input_data"],
                "description": "Template for analyzing various types of data",
                "tags": ["analysis", "general", "test"]
            }
        }
        
        response = await self.make_request(
            "POST", 
            f"{MCP_BASE_URL}/process",
            json=request_data
        )
        
        if response.get("success") and response.get("result", {}).get("success"):
            result = response["result"]
            template = result["template"]
            self.created_template_ids.append(template["template_id"])
            print(f"✅ Prompt template created successfully")
            print(f"   Template ID: {template['template_id']}")
            print(f"   Name: {template['name']}")
            print(f"   Variables: {template['variables']}")
            return True
        else:
            print(f"❌ Prompt template creation failed: {response}")
            return False
    
    async def test_optimize_prompt(self) -> bool:
        """Test prompt optimization via MCP."""
        print("Testing prompt optimization...")
        
        template_id = self.created_template_ids[0] if self.created_template_ids else "test_template"
        
        request_data = {
            "tool_name": "optimize_prompt",
            "arguments": {
                "template_id": template_id,
                "optimization_goals": ["clarity", "effectiveness", "brevity"],
                "context": {"task_type": "data_analysis", "complexity": "medium"}
            }
        }
        
        response = await self.make_request(
            "POST",
            f"{MCP_BASE_URL}/process",
            json=request_data
        )
        
        if response.get("success") and response.get("result", {}).get("success"):
            result = response["result"]
            print(f"✅ Prompt optimization completed")
            print(f"   Template ID: {result['template_id']}")
            print(f"   Optimization score: {result['optimization_score']}")
            print(f"   Improvements made: {len(result['improvements'])}")
            return True
        else:
            print(f"❌ Prompt optimization failed: {response}")
            return False
    
    async def test_validate_prompt_syntax(self) -> bool:
        """Test prompt syntax validation via MCP."""
        print("Testing prompt syntax validation...")
        
        request_data = {
            "tool_name": "validate_prompt_syntax",
            "arguments": {
                "prompt_text": "Please analyze this {data_type} and provide {missing_variable} insights.",
                "template_variables": ["data_type", "requirement_type"]
            }
        }
        
        response = await self.make_request(
            "POST",
            f"{MCP_BASE_URL}/process",
            json=request_data
        )
        
        if response.get("success") and response.get("result", {}).get("success"):
            result = response["result"]
            validation_results = result["results"]
            print(f"✅ Prompt syntax validation completed")
            print(f"   Validation passed: {result['validation_passed']}")
            print(f"   Variables found: {validation_results['template_variables_found']}")
            print(f"   Missing variables: {validation_results['missing_variables']}")
            print(f"   Undefined variables: {validation_results['undefined_variables']}")
            return True
        else:
            print(f"❌ Prompt syntax validation failed: {response}")
            return False
    
    async def test_context_usage_analysis(self) -> bool:
        """Test context usage analysis via MCP."""
        print("Testing context usage analysis...")
        
        request_data = {
            "tool_name": "analyze_context_usage",
            "arguments": {
                "context_id": "test_context_001",
                "time_period": "last_week",
                "include_metrics": True
            }
        }
        
        response = await self.make_request(
            "POST",
            f"{MCP_BASE_URL}/process",
            json=request_data
        )
        
        if response.get("success") and response.get("result", {}).get("success"):
            result = response["result"]
            analysis = result["analysis"]
            usage_stats = analysis["usage_stats"]
            print(f"✅ Context usage analysis completed")
            print(f"   Context ID: {result['context_id']}")
            print(f"   Total messages: {usage_stats['total_messages']}")
            print(f"   Total tokens: {usage_stats['total_tokens']}")
            print(f"   Efficiency score: {usage_stats['efficiency_score']:.2f}")
            print(f"   Optimization needed: {analysis['optimization_needed']}")
            return True
        else:
            print(f"❌ Context usage analysis failed: {response}")
            return False
    
    async def test_context_optimization(self) -> bool:
        """Test context window optimization via MCP."""
        print("Testing context optimization...")
        
        request_data = {
            "tool_name": "optimize_context_window",
            "arguments": {
                "context_id": "test_context_001",
                "optimization_strategy": "efficiency",
                "preserve_recent_messages": True
            }
        }
        
        response = await self.make_request(
            "POST",
            f"{MCP_BASE_URL}/process",
            json=request_data
        )
        
        if response.get("success") and response.get("result", {}).get("success"):
            result = response["result"]
            improvements = result["improvements"]
            print(f"✅ Context optimization completed")
            print(f"   Context ID: {result['context_id']}")
            print(f"   Strategy: {result['optimization_strategy']}")
            print(f"   Tokens reduced: {improvements['tokens_reduced']}")
            print(f"   Efficiency improvement: {improvements['efficiency_improvement_percent']:.1f}%")
            return True
        else:
            print(f"❌ Context optimization failed: {response}")
            return False
    
    async def test_llm_workflow(self) -> bool:
        """Test LLM management workflow execution."""
        print("Testing LLM workflow execution...")
        
        workflow_data = {
            "workflow_name": "model_optimization",
            "parameters": {
                "task_type": "code_analysis",
                "performance_criteria": ["speed", "quality", "cost"]
            }
        }
        
        response = await self.make_request(
            "POST",
            f"{MCP_BASE_URL}/execute-llm-workflow",
            json=workflow_data
        )
        
        if response.get("success"):
            result = response["result"]
            workflow_summary = result["workflow_summary"]
            print(f"✅ LLM workflow executed successfully")
            print(f"   Workflow: {response['workflow']}")
            print(f"   Models tested: {result['models_tested']}")
            print(f"   Models connected: {result['models_connected']}")
            print(f"   Optimization confidence: {workflow_summary['optimization_confidence']}")
            return True
        else:
            print(f"❌ LLM workflow execution failed: {response}")
            return False
    
    async def test_llm_status(self) -> bool:
        """Test LLM status endpoint."""
        print("Testing LLM status...")
        
        response = await self.make_request("GET", f"{MCP_BASE_URL}/llm-status")
        
        if response.get("success"):
            print(f"✅ LLM status retrieved successfully")
            print(f"   Service status: {response['status']}")
            print(f"   Available providers: {response['available_providers']}")
            print(f"   MCP tools available: {response['mcp_tools']}")
            return True
        else:
            print(f"❌ LLM status failed: {response}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all tests."""
        print("🚀 Starting Rhetor FastMCP Tests\n")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("MCP Status", self.test_mcp_status),
            ("MCP Capabilities", self.test_mcp_capabilities),
            ("Get Available Models", self.test_get_available_models),
            ("Model Capabilities", self.test_model_capabilities),
            ("Model Connection", self.test_model_connection),
            ("Create Prompt Template", self.test_create_prompt_template),
            ("Optimize Prompt", self.test_optimize_prompt),
            ("Validate Prompt Syntax", self.test_validate_prompt_syntax),
            ("Context Usage Analysis", self.test_context_usage_analysis),
            ("Context Optimization", self.test_context_optimization),
            ("LLM Workflow", self.test_llm_workflow),
            ("LLM Status", self.test_llm_status),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            try:
                if await test_func():
                    passed += 1
                else:
                    print(f"Test '{test_name}' failed")
            except Exception as e:
                print(f"❌ Test '{test_name}' error: {e}")
        
        print(f"\n🏁 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed!")
            return True
        else:
            print("❌ Some tests failed")
            return False


async def main():
    """Main test function."""
    async with RhetorMCPTester() as tester:
        success = await tester.run_all_tests()
        return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)