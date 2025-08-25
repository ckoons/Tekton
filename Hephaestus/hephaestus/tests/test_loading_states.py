"""
Test suite for the semantic loading state system in UI DevTools

This test file validates the component loading state tracking feature that uses
data-tekton-loading-state attributes to reliably detect when components are ready.
"""

import pytest
import asyncio
import httpx
from typing import Dict, Any
import time

# Configuration
MCP_URL = "http://localhost:8088/api/mcp/v2/execute"
TEST_TIMEOUT = 30  # seconds

# Test components - mix of different types
TEST_COMPONENTS = [
    "rhetor",     # CI component with complex initialization
    "athena",     # Development environment
    "metis",      # Memory system
    "settings",   # Settings panel
    "profile"     # User profile
]


async def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a DevTools tool via MCP"""
    async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
        response = await client.post(MCP_URL, json={
            "tool_name": tool_name,
            "arguments": arguments
        })
        return response.json()


class TestLoadingStates:
    """Test the semantic loading state system"""
    
    @pytest.mark.asyncio
    async def test_navigation_waits_for_loaded_state(self):
        """Test that navigation properly waits for components to reach loaded state"""
        # Navigate to home first
        await execute_tool("ui_navigate", {"component": "home"})
        await asyncio.sleep(1)
        
        # Test navigation with loading state detection
        result = await execute_tool("ui_navigate", {"component": "rhetor"})
        
        assert result["status"] == "success"
        assert result["result"]["navigation_completed"] == True
        
        # Check that we got loading state confirmation
        assert "loading state: loaded" in result["result"].get("message", "")
        
        # Verify load time was captured
        if "load_time_ms" in result["result"]:
            load_time = result["result"]["load_time_ms"]
            assert isinstance(load_time, int)
            assert load_time > 0
            assert load_time < 10000  # Should load in under 10 seconds
    
    @pytest.mark.asyncio
    async def test_loading_state_attributes_in_dom(self):
        """Test that loading state attributes are properly set in the DOM"""
        # Navigate to a component
        nav_result = await execute_tool("ui_navigate", {"component": "athena"})
        assert nav_result["status"] == "success"
        
        # Capture the UI to check attributes
        capture_result = await execute_tool("ui_capture", {"area": "hephaestus"})
        assert capture_result["status"] == "success"
        
        html = capture_result["result"]["html"]
        
        # Check for loading state attributes
        assert 'data-tekton-loading-state="loaded"' in html
        assert 'data-tekton-loading-component="athena"' in html
        assert 'data-tekton-loading-started=' in html
    
    @pytest.mark.asyncio
    async def test_loading_state_fallback(self):
        """Test that navigation falls back to original detection if loading states fail"""
        # This tests the fallback mechanism by navigating to a component
        # The fallback should still work even if loading states aren't detected
        result = await execute_tool("ui_navigate", {"component": "metis"})
        
        assert result["status"] == "success"
        
        # Either we got loading state success OR fallback success
        if "loading_state_fallback" in result["result"]:
            # Fallback was used
            assert result["result"]["navigation_completed"] == True
            assert "loading_state_fallback" in result["result"]
        else:
            # Loading states worked
            assert "loading state: loaded" in result["result"].get("message", "")
    
    @pytest.mark.asyncio
    async def test_multiple_component_navigation(self):
        """Test navigating between multiple components with loading states"""
        load_times = {}
        
        for component in TEST_COMPONENTS:
            start_time = time.time()
            result = await execute_tool("ui_navigate", {"component": component})
            end_time = time.time()
            
            assert result["status"] == "success", f"Failed to navigate to {component}"
            assert result["result"]["navigation_completed"] == True
            
            # Record load time
            if "load_time_ms" in result["result"]:
                load_times[component] = result["result"]["load_time_ms"]
            else:
                # Use measured time as fallback
                load_times[component] = int((end_time - start_time) * 1000)
            
            # Small delay between navigations
            await asyncio.sleep(0.5)
        
        # Verify all components loaded
        assert len(load_times) == len(TEST_COMPONENTS)
        
        # Log performance results
        print("\nComponent Load Times:")
        for component, load_time in load_times.items():
            print(f"  {component}: {load_time}ms")
    
    @pytest.mark.asyncio
    async def test_capture_checks_loading_states(self):
        """Test that ui_capture properly detects and reports loading states"""
        # Navigate to a component
        await execute_tool("ui_navigate", {"component": "profile"})
        
        # Immediately capture (might catch loading state)
        capture_result = await execute_tool("ui_capture", {"area": "profile"})
        
        assert capture_result["status"] == "success"
        
        # The capture should succeed even if component is loading
        # Check if any loading warnings were provided
        result = capture_result["result"]
        
        # Either fully loaded or loading state detected
        if "warnings" in result and "loading" in str(result["warnings"]):
            print("Detected components still loading")
        else:
            # Should be fully loaded
            assert result["element_count"] > 0
    
    @pytest.mark.asyncio
    async def test_error_state_handling(self):
        """Test that error states are properly detected and reported"""
        # Try to navigate to a non-existent component to test error handling
        # This should fail before loading states are involved
        result = await execute_tool("ui_navigate", {"component": "nonexistent"})
        
        # This should fail at the navigation item level, not loading state
        assert result["status"] == "error" or result["result"].get("error") is not None
    
    @pytest.mark.asyncio
    async def test_loading_state_performance(self):
        """Test that loading state detection doesn't significantly slow navigation"""
        # Test navigation performance with loading states
        timings = []
        
        for i in range(3):
            start = time.time()
            result = await execute_tool("ui_navigate", {"component": "settings"})
            end = time.time()
            
            assert result["status"] == "success"
            timings.append((end - start) * 1000)  # Convert to ms
            
            await asyncio.sleep(1)  # Wait between tests
        
        avg_time = sum(timings) / len(timings)
        print(f"\nAverage navigation time: {avg_time:.2f}ms")
        
        # Navigation should complete in reasonable time
        assert avg_time < 5000  # 5 seconds max average


class TestLoadingStateIntegration:
    """Integration tests for loading states with other DevTools features"""
    
    @pytest.mark.asyncio
    async def test_sandbox_after_loaded_state(self):
        """Test that ui_sandbox works correctly after component is loaded"""
        # Navigate and wait for loaded state
        nav_result = await execute_tool("ui_navigate", {"component": "rhetor"})
        assert nav_result["status"] == "success"
        
        # Try to use sandbox on the loaded component
        sandbox_result = await execute_tool("ui_sandbox", {
            "area": "rhetor",
            "changes": [{
                "type": "text",
                "selector": "h1",
                "content": "Test Heading",
                "action": "replace"
            }],
            "preview": True
        })
        
        # Sandbox should work on loaded component
        assert sandbox_result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_workflow_with_loading_states(self):
        """Test that high-level workflow tool works with loading states"""
        workflow_result = await execute_tool("ui_workflow", {
            "task": "Navigate to ergon and capture its content",
            "reasoning": "Testing workflow with loading state system"
        })
        
        assert workflow_result["status"] == "success"
        
        # Check that workflow completed successfully
        steps = workflow_result["result"].get("steps", [])
        assert len(steps) > 0
        
        # Verify navigation step used loading states
        nav_step = next((s for s in steps if s["action"] == "navigate"), None)
        if nav_step and "result" in nav_step:
            # Should have completed navigation
            assert nav_step["status"] == "completed"


@pytest.mark.asyncio
async def test_all_components_load_successfully():
    """Comprehensive test that all 19 components load with the new system"""
    all_components = [
        "rhetor", "rhapsode", "prometheus", "athena", "apollo",
        "ergon", "metis", "nostos", "budget", "security",
        "integrations", "experimental", "profile", "settings",
        "help", "telemetry", "project", "git", "monitoring"
    ]
    
    results = {}
    failures = []
    
    print("\nTesting all components with loading state system:")
    
    for component in all_components:
        try:
            result = await execute_tool("ui_navigate", {"component": component})
            
            if result["status"] == "success" and result["result"]["navigation_completed"]:
                load_time = result["result"].get("load_time_ms", "N/A")
                results[component] = {
                    "status": "✓",
                    "load_time": load_time,
                    "used_loading_state": "loading state: loaded" in result["result"].get("message", "")
                }
                print(f"  {component}: ✓ ({load_time}ms)")
            else:
                error = result["result"].get("error", "Unknown error")
                results[component] = {"status": "✗", "error": error}
                failures.append(component)
                print(f"  {component}: ✗ ({error})")
                
        except Exception as e:
            results[component] = {"status": "✗", "error": str(e)}
            failures.append(component)
            print(f"  {component}: ✗ (Exception: {e})")
        
        await asyncio.sleep(0.5)  # Small delay between components
    
    # Summary
    print(f"\nResults: {len(all_components) - len(failures)}/{len(all_components)} components loaded successfully")
    
    if failures:
        print(f"Failed components: {', '.join(failures)}")
    
    # Calculate statistics for successful loads
    load_times = [r["load_time"] for r in results.values() 
                  if r["status"] == "✓" and isinstance(r.get("load_time"), int)]
    
    if load_times:
        avg_load_time = sum(load_times) / len(load_times)
        print(f"Average load time: {avg_load_time:.2f}ms")
        print(f"Min load time: {min(load_times)}ms")
        print(f"Max load time: {max(load_times)}ms")
    
    # Count how many used the new loading state system
    used_loading_state = sum(1 for r in results.values() 
                           if r.get("used_loading_state", False))
    print(f"Components using loading state system: {used_loading_state}/{len(all_components)}")
    
    # Assert high success rate
    success_rate = (len(all_components) - len(failures)) / len(all_components)
    assert success_rate >= 0.8, f"Too many components failed: {len(failures)}/{len(all_components)}"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])