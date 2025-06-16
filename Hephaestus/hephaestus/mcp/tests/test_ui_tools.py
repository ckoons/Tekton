"""
Tests for Hephaestus UI DevTools MCP
"""
import asyncio
import json
import pytest
import httpx
from typing import Dict, Any
import time

# MCP server URL
MCP_URL = "http://localhost:8088"
EXECUTE_URL = f"{MCP_URL}/api/mcp/v2/execute"


class TestUIDevTools:
    """Test suite for UI DevTools MCP"""
    
    @pytest.fixture(autouse=True)
    async def setup(self):
        """Ensure MCP server is running before tests"""
        async with httpx.AsyncClient() as client:
            retries = 5
            while retries > 0:
                try:
                    response = await client.get(f"{MCP_URL}/health")
                    if response.status_code == 200:
                        break
                except:
                    pass
                retries -= 1
                await asyncio.sleep(1)
            else:
                pytest.fail("MCP server not available")
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to execute MCP tool"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                EXECUTE_URL,
                json={"tool_name": tool_name, "arguments": arguments}
            )
            return response.json()
    
    # ===== UI_CAPTURE TESTS =====
    
    @pytest.mark.asyncio
    async def test_ui_capture_basic(self):
        """Test basic UI capture without parameters"""
        result = await self.execute_tool("ui_capture", {"area": "hephaestus"})
        
        assert result["status"] == "success"
        assert "result" in result
        assert "loaded_component" in result["result"]
        assert "element_count" in result["result"]
        assert result["result"]["element_count"] > 0
    
    @pytest.mark.asyncio
    async def test_ui_capture_with_selector(self):
        """Test UI capture with CSS selector"""
        result = await self.execute_tool("ui_capture", {
            "area": "hephaestus",
            "selector": ".nav-item"
        })
        
        assert result["status"] == "success"
        assert result["result"]["element_count"] >= 0  # May be 0 if no nav items
    
    @pytest.mark.asyncio
    async def test_ui_capture_invalid_area(self):
        """Test UI capture with invalid area"""
        result = await self.execute_tool("ui_capture", {
            "area": "nonexistent"
        })
        
        assert result["status"] == "success"  # Should handle gracefully
        assert "error" in result["result"] or result["result"]["element_count"] == 0
    
    # ===== UI_NAVIGATE TESTS =====
    
    @pytest.mark.asyncio
    async def test_ui_navigate_valid_component(self):
        """Test navigation to valid component"""
        result = await self.execute_tool("ui_navigate", {
            "component": "rhetor"
        })
        
        assert result["status"] == "success"
        assert result["result"]["navigation_started"] == True
        assert "message" in result["result"]
    
    @pytest.mark.asyncio
    async def test_ui_navigate_invalid_component(self):
        """Test navigation to invalid component"""
        result = await self.execute_tool("ui_navigate", {
            "component": "nonexistent"
        })
        
        assert result["status"] == "success"
        assert "error" in result["result"] or result["result"].get("navigation_completed") == False
    
    @pytest.mark.asyncio
    async def test_ui_navigate_no_wait(self):
        """Test navigation without waiting for load"""
        result = await self.execute_tool("ui_navigate", {
            "component": "prometheus",
            "wait_for_load": False
        })
        
        assert result["status"] == "success"
        assert result["result"]["navigation_started"] == True
    
    # ===== UI_SANDBOX TESTS =====
    
    @pytest.mark.asyncio
    async def test_ui_sandbox_preview_text_change(self):
        """Test sandbox preview mode with text change"""
        result = await self.execute_tool("ui_sandbox", {
            "area": "hephaestus",
            "changes": [{
                "type": "text",
                "selector": ".nav-label",
                "content": "Test Label",
                "action": "replace"
            }],
            "preview": True
        })
        
        assert result["status"] == "success"
        assert "preview_mode" in result["result"]
        assert result["result"]["preview_mode"] == True
    
    @pytest.mark.asyncio
    async def test_ui_sandbox_css_change(self):
        """Test sandbox with CSS changes"""
        result = await self.execute_tool("ui_sandbox", {
            "area": "hephaestus",
            "changes": [{
                "type": "css",
                "selector": ".nav-item",
                "property": "border",
                "value": "1px solid red"
            }],
            "preview": True
        })
        
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_ui_sandbox_multiple_changes(self):
        """Test sandbox with multiple changes"""
        result = await self.execute_tool("ui_sandbox", {
            "area": "hephaestus",
            "changes": [
                {
                    "type": "text",
                    "selector": ".nav-label",
                    "content": "New Text",
                    "action": "replace"
                },
                {
                    "type": "css",
                    "selector": ".nav-item",
                    "property": "padding",
                    "value": "10px"
                }
            ],
            "preview": True
        })
        
        assert result["status"] == "success"
        assert len(result["result"]["changes_applied"]) <= 2
    
    # ===== UI_VALIDATE TESTS =====
    
    @pytest.mark.asyncio
    async def test_ui_validate_current_scope(self):
        """Test validation of current component"""
        result = await self.execute_tool("ui_validate", {
            "scope": "current"
        })
        
        assert result["status"] == "success"
        if "error" not in result["result"]:
            assert "summary" in result["result"]
            assert "findings" in result["result"]
            assert "score" in result["result"]["summary"]
    
    @pytest.mark.asyncio
    async def test_ui_validate_navigation_scope(self):
        """Test validation of navigation structure"""
        result = await self.execute_tool("ui_validate", {
            "scope": "navigation"
        })
        
        assert result["status"] == "success"
        assert "summary" in result["result"]
        assert result["result"]["summary"]["score"] >= 0
    
    @pytest.mark.asyncio
    async def test_ui_validate_with_specific_checks(self):
        """Test validation with specific checks"""
        result = await self.execute_tool("ui_validate", {
            "scope": "current",
            "checks": ["semantic-tags", "data-attributes"]
        })
        
        assert result["status"] == "success"
        assert result["result"]["checks_performed"] == ["semantic-tags", "data-attributes"]
    
    # ===== UI_INTERACT TESTS =====
    
    @pytest.mark.asyncio
    async def test_ui_interact_click(self):
        """Test click interaction"""
        # First navigate to ensure we have something to click
        await self.execute_tool("ui_navigate", {"component": "rhetor"})
        
        result = await self.execute_tool("ui_interact", {
            "area": "rhetor",
            "action": "click",
            "selector": "button"
        })
        
        assert result["status"] == "success"
    
    # ===== UI_ANALYZE TESTS =====
    
    @pytest.mark.asyncio
    async def test_ui_analyze_basic(self):
        """Test basic UI analysis"""
        result = await self.execute_tool("ui_analyze", {
            "area": "hephaestus"
        })
        
        assert result["status"] == "success"
        assert "frameworks_detected" in result["result"]
        assert "patterns" in result["result"]
    
    # ===== INTEGRATION TESTS =====
    
    @pytest.mark.asyncio
    async def test_navigate_and_capture_workflow(self):
        """Test complete workflow: navigate then capture"""
        # Navigate to component
        nav_result = await self.execute_tool("ui_navigate", {
            "component": "prometheus"
        })
        assert nav_result["status"] == "success"
        
        # Capture the component
        capture_result = await self.execute_tool("ui_capture", {
            "area": "prometheus"
        })
        assert capture_result["status"] == "success"
        
        # Loaded component should be prometheus (or profile if navigation didn't work)
        loaded = capture_result["result"]["loaded_component"]
        assert loaded in ["prometheus", "profile", "tekton"]
    
    @pytest.mark.asyncio
    async def test_capture_modify_validate_workflow(self):
        """Test workflow: capture, modify in sandbox, validate"""
        # Capture current state
        capture1 = await self.execute_tool("ui_capture", {"area": "hephaestus"})
        initial_count = capture1["result"]["element_count"]
        
        # Make sandbox changes
        sandbox_result = await self.execute_tool("ui_sandbox", {
            "area": "hephaestus",
            "changes": [{
                "type": "html",
                "selector": "body",
                "content": "<div class='test-element'>Test</div>",
                "action": "append"
            }],
            "preview": True
        })
        assert sandbox_result["status"] == "success"
        
        # Validate
        validate_result = await self.execute_tool("ui_validate", {
            "scope": "current"
        })
        assert validate_result["status"] == "success"
    
    # ===== ERROR HANDLING TESTS =====
    
    @pytest.mark.asyncio
    async def test_missing_required_parameters(self):
        """Test handling of missing required parameters"""
        result = await self.execute_tool("ui_navigate", {})
        
        assert result["status"] == "error" or "error" in result
    
    @pytest.mark.asyncio
    async def test_invalid_tool_name(self):
        """Test handling of invalid tool name"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                EXECUTE_URL,
                json={"tool_name": "nonexistent_tool", "arguments": {}}
            )
            result = response.json()
            
        assert result["status"] == "error" or response.status_code == 404


# Performance tests (optional, can be run separately)
class TestPerformance:
    """Performance tests for UI DevTools"""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_ui_capture_performance(self):
        """Test UI capture performance"""
        times = []
        for _ in range(5):
            start = time.time()
            result = await TestUIDevTools().execute_tool("ui_capture", {"area": "hephaestus"})
            times.append(time.time() - start)
            assert result["status"] == "success"
        
        avg_time = sum(times) / len(times)
        assert avg_time < 5.0, f"UI capture too slow: {avg_time:.2f}s average"
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_ui_validate_all_timeout(self):
        """Test that validate all doesn't timeout"""
        start = time.time()
        result = await TestUIDevTools().execute_tool("ui_validate", {
            "scope": "all"
        })
        duration = time.time() - start
        
        # Should complete within 30 seconds (with our fixes)
        assert duration < 30.0, f"Validate all took {duration:.2f}s"
        assert result["status"] == "success"