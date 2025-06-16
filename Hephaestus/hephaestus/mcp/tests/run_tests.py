#!/usr/bin/env python3
"""
Simple test runner for UI DevTools tests
Can be used without pytest for basic testing
"""
import asyncio
import httpx
import sys
import time
from typing import Dict, Any


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


class SimpleTestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.mcp_url = "http://localhost:8088"
        self.execute_url = f"{self.mcp_url}/api/mcp/v2/execute"
    
    async def check_server(self):
        """Check if MCP server is running"""
        print(f"{Colors.BLUE}Checking MCP server...{Colors.END}")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.mcp_url}/health")
                if response.status_code == 200:
                    print(f"{Colors.GREEN}✓ MCP server is healthy{Colors.END}")
                    return True
            except:
                pass
        
        print(f"{Colors.RED}✗ MCP server not available at {self.mcp_url}{Colors.END}")
        print(f"{Colors.YELLOW}Please start the server with: ./run_mcp.sh{Colors.END}")
        return False
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP tool"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.execute_url,
                json={"tool_name": tool_name, "arguments": arguments}
            )
            return response.json()
    
    async def run_test(self, test_name: str, test_func):
        """Run a single test"""
        print(f"\n{Colors.BLUE}Running: {test_name}{Colors.END}")
        try:
            await test_func()
            self.passed += 1
            print(f"{Colors.GREEN}✓ PASSED{Colors.END}")
        except AssertionError as e:
            self.failed += 1
            self.errors.append((test_name, str(e)))
            print(f"{Colors.RED}✗ FAILED: {e}{Colors.END}")
        except Exception as e:
            self.failed += 1
            self.errors.append((test_name, f"ERROR: {e}"))
            print(f"{Colors.RED}✗ ERROR: {e}{Colors.END}")
    
    # Test functions
    async def test_ui_capture_basic(self):
        """Test basic UI capture"""
        result = await self.execute_tool("ui_capture", {"area": "hephaestus"})
        assert result["status"] == "success", "Capture should succeed"
        assert "loaded_component" in result["result"], "Should detect loaded component"
        assert "structure" in result["result"], "Should have structure data"
    
    async def test_ui_navigate(self):
        """Test navigation"""
        result = await self.execute_tool("ui_navigate", {"component": "rhetor"})
        assert result["status"] == "success", "Navigation should succeed"
        assert result["result"]["navigation_started"], "Navigation should start"
    
    async def test_ui_sandbox_preview(self):
        """Test sandbox in preview mode"""
        result = await self.execute_tool("ui_sandbox", {
            "area": "hephaestus",
            "changes": [{
                "type": "text",
                "selector": ".nav-label",
                "content": "Test",
                "action": "replace"
            }],
            "preview": True
        })
        assert result["status"] == "success", "Sandbox should succeed"
        assert result["result"]["preview"] == True, "Should be in preview mode"
    
    async def test_ui_validate_navigation(self):
        """Test navigation validation"""
        result = await self.execute_tool("ui_validate", {"scope": "navigation"})
        assert result["status"] == "success", "Validation should succeed"
        assert "score" in result["result"]["summary"], "Should have score"
    
    async def test_ui_analyze(self):
        """Test UI analysis"""
        result = await self.execute_tool("ui_analyze", {"area": "hephaestus"})
        assert result["status"] == "success", "Analysis should succeed"
        assert "analysis" in result["result"], "Should have analysis data"
    
    async def test_no_nav_state_dependency(self):
        """Test that we don't rely on nav active state"""
        result = await self.execute_tool("ui_capture", {"area": "hephaestus"})
        assert "active_nav_item" not in result["result"], "Should not include nav active state"
        assert "loaded_component" in result["result"], "Should only track loaded component"
    
    async def test_error_handling(self):
        """Test error handling"""
        result = await self.execute_tool("ui_navigate", {})  # Missing required param
        assert result["status"] == "error" or "error" in result, "Should handle missing params"
    
    async def run_all_tests(self):
        """Run all tests"""
        if not await self.check_server():
            return False
        
        print(f"\n{Colors.BLUE}Running UI DevTools Tests{Colors.END}")
        print("=" * 50)
        
        tests = [
            ("Basic UI Capture", self.test_ui_capture_basic),
            ("Navigation", self.test_ui_navigate),
            ("Sandbox Preview", self.test_ui_sandbox_preview),
            ("Validate Navigation", self.test_ui_validate_navigation),
            ("UI Analysis", self.test_ui_analyze),
            ("No Nav State Dependency", self.test_no_nav_state_dependency),
            ("Error Handling", self.test_error_handling),
        ]
        
        start_time = time.time()
        
        for test_name, test_func in tests:
            await self.run_test(test_name, test_func)
        
        duration = time.time() - start_time
        
        # Summary
        print("\n" + "=" * 50)
        print(f"{Colors.BLUE}Test Summary{Colors.END}")
        print(f"Total: {self.passed + self.failed}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.END}")
        print(f"Time: {duration:.2f}s")
        
        if self.errors:
            print(f"\n{Colors.RED}Failures:{Colors.END}")
            for test_name, error in self.errors:
                print(f"  {test_name}: {error}")
        
        return self.failed == 0


async def main():
    """Main entry point"""
    runner = SimpleTestRunner()
    success = await runner.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())