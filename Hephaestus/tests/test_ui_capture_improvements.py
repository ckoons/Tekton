"""
Tests for UI DevTools improvements
Tests the fixes for element count, HTML inclusion, and ui_sandbox
"""
import asyncio
import pytest
import httpx
from typing import Dict, Any

# MCP server URL
MCP_URL = "http://localhost:8088"
EXECUTE_URL = f"{MCP_URL}/api/mcp/v2/execute"


class TestUIDevToolsImprovements:
    """Test suite for UI DevTools improvements"""
    
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
    
    @pytest.mark.asyncio
    async def test_ui_capture_element_count_fixed(self):
        """Test that ui_capture returns correct total element count, not just 1"""
        result = await self.execute_tool("ui_capture", {"area": "hephaestus"})
        
        assert result["status"] == "success"
        structure = result["result"]["structure"]
        
        # Should have more than 1 element (was broken before)
        assert structure["element_count"] > 1, f"Expected >1 elements, got {structure['element_count']}"
        
        # Should have the new total_element_count field when no selector
        assert "total_element_count" in structure or structure["element_count"] > 1
        
        # Should have root_element_count = 1 for backward compatibility
        if "root_element_count" in structure:
            assert structure["root_element_count"] == 1
    
    @pytest.mark.asyncio
    async def test_ui_capture_includes_html(self):
        """Test that ui_capture includes raw HTML for searching"""
        result = await self.execute_tool("ui_capture", {"area": "hephaestus"})
        
        assert result["status"] == "success"
        assert "html" in result["result"], "HTML should be included in result"
        assert "html_length" in result["result"], "HTML length should be included"
        assert result["result"]["html_length"] > 1000, "HTML should have substantial content"
        
        # HTML should contain expected elements
        html = result["result"]["html"]
        assert "data-component" in html
        assert "nav-label" in html
    
    @pytest.mark.asyncio
    async def test_ui_capture_selectors_available(self):
        """Test that ui_capture shows available selectors with counts"""
        result = await self.execute_tool("ui_capture", {"area": "hephaestus"})
        
        assert result["status"] == "success"
        assert "selectors_available" in result["result"]
        
        selectors = result["result"]["selectors_available"]
        assert isinstance(selectors, dict)
        
        # Should have common selectors
        expected_selectors = [".nav-label", "[data-component]", "button", "input"]
        for sel in expected_selectors:
            assert sel in selectors, f"Expected selector {sel} in selectors_available"
        
        # Counts should be integers >= 0
        for sel, count in selectors.items():
            assert isinstance(count, int) and count >= 0
    
    @pytest.mark.asyncio
    async def test_ui_sandbox_can_modify_elements(self):
        """Test that ui_sandbox can successfully modify elements (was broken)"""
        result = await self.execute_tool("ui_sandbox", {
            "area": "hephaestus",
            "changes": [{
                "type": "text",
                "selector": "[data-component='prometheus'] .nav-label",
                "content": "Prometheus - Test Modified",
                "action": "replace"
            }],
            "preview": False
        })
        
        assert result["status"] == "success"
        summary = result["result"]["summary"]
        
        # Should have successful changes (was 0 before fix)
        assert summary["successful"] > 0, "Should have at least one successful change"
        assert summary["failed"] == 0, "Should have no failed changes"
        
        # Check sandbox results
        sandbox_results = result["result"]["sandbox_results"]
        assert len(sandbox_results) > 0
        assert sandbox_results[0]["success"] is True
        assert sandbox_results[0].get("elements_modified", 0) > 0
    
    @pytest.mark.asyncio
    async def test_ui_sandbox_handles_quotes_in_selectors(self):
        """Test that ui_sandbox properly escapes quotes in selectors"""
        # This selector has single quotes that need escaping
        result = await self.execute_tool("ui_sandbox", {
            "area": "hephaestus",
            "changes": [{
                "type": "text",
                "selector": "[data-component='rhetor'] .nav-label",
                "content": "Rhetor - Quote Test",
                "action": "replace"
            }],
            "preview": False
        })
        
        assert result["status"] == "success"
        
        # Should not have JavaScript syntax errors
        sandbox_results = result["result"]["sandbox_results"]
        if sandbox_results and not sandbox_results[0]["success"]:
            error = sandbox_results[0].get("error", "")
            assert "SyntaxError" not in error, f"Should not have syntax errors: {error}"
    
    @pytest.mark.asyncio
    async def test_ui_sandbox_clear_error_for_missing_selector(self):
        """Test that ui_sandbox provides clear error for missing selectors"""
        result = await self.execute_tool("ui_sandbox", {
            "area": "hephaestus",
            "changes": [{
                "type": "text",
                "selector": ".definitely-does-not-exist-12345",
                "content": "Won't work",
                "action": "replace"
            }],
            "preview": False
        })
        
        assert result["status"] == "success"
        
        # Should have clear error message
        sandbox_results = result["result"]["sandbox_results"]
        assert len(sandbox_results) > 0
        assert sandbox_results[0]["success"] is False
        
        error = sandbox_results[0].get("error", "")
        assert "No elements found" in error
        assert ".definitely-does-not-exist-12345" in error
    
    @pytest.mark.asyncio
    async def test_multiple_changes_in_sandbox(self):
        """Test that ui_sandbox can handle multiple changes"""
        result = await self.execute_tool("ui_sandbox", {
            "area": "hephaestus",
            "changes": [
                {
                    "type": "text",
                    "selector": "[data-component='prometheus'] .nav-label",
                    "content": "Prometheus - Multi 1",
                    "action": "replace"
                },
                {
                    "type": "attribute",
                    "selector": "[data-component='prometheus']",
                    "attribute": "data-test",
                    "value": "multi-change"
                }
            ],
            "preview": False
        })
        
        assert result["status"] == "success"
        summary = result["result"]["summary"]
        
        # Should handle multiple changes
        assert summary["total_changes"] == 2
        assert summary["successful"] >= 1  # At least one should work


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v"])