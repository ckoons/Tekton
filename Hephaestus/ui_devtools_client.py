"""
Simple client wrapper for Hephaestus UI DevTools MCP v2

This is the ONLY way to interact with Tekton UI!
DO NOT use playwright, puppeteer, or any other browser tools!

IMPORTANT: All UI is at http://localhost:8080 (Hephaestus)
Components like Rhetor, Hermes, etc. are AREAS within Hephaestus UI!

Usage:
    from ui_devtools_client import UIDevTools, check_and_start_mcp
    
    # Check MCP is running
    if not await check_and_start_mcp():
        return
    
    ui = UIDevTools()
    
    # Get help!
    help = await ui.help()  # General help
    help = await ui.help("areas")  # Specific topic
    
    # List all UI areas
    areas = await ui.list_areas()
    
    # See UI structure (no screenshots!)
    result = await ui.capture("rhetor")
    
    # Test changes safely
    result = await ui.sandbox("rhetor", [
        {"type": "html", "selector": "#footer", "content": "<div>Test</div>", "action": "append"}
    ])
    
    # Click something
    result = await ui.interact("rhetor", "click", "button#submit")
    
    # Check for frameworks
    result = await ui.analyze("rhetor")
"""

import httpx
import asyncio
from typing import Dict, List, Any, Optional


class UIDevTools:
    """Client for Hephaestus UI DevTools MCP v2 - The ONLY way to work with Tekton UI"""
    
    def __init__(self, mcp_url: str = "http://localhost:8088"):
        self.mcp_url = mcp_url
        self.api_endpoint = f"{mcp_url}/api/mcp/v2/execute"
        self._last_error = None
        
    async def health_check(self) -> bool:
        """Check if UI DevTools MCP is running"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.mcp_url}/health", timeout=5.0)
                return response.status_code == 200
        except:
            return False
    
    async def help(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Get help about UI DevTools usage
        
        Args:
            topic: Optional specific topic. Valid topics:
                   'areas', 'selectors', 'frameworks', 'errors', 'tasks', 'architecture'
                   
        Returns:
            Help information with examples and guidance
        """
        args = {}
        if topic:
            args["topic"] = topic
            
        return await self._execute("ui_help", args)
    
    async def list_areas(self) -> Dict[str, Any]:
        """
        List all available UI areas in Hephaestus
        
        Returns:
            Information about available UI areas and how to use them
        """
        return await self._execute("ui_list_areas", {})
    
    async def capture(self, area: str = "hephaestus", selector: Optional[str] = None) -> Dict[str, Any]:
        """
        Capture UI structure without screenshots
        
        Args:
            area: UI area name (e.g., 'rhetor', 'navigation', 'content')
                  Use 'hephaestus' for the entire UI
            selector: Optional CSS selector to focus on
            
        Returns:
            Structured data about UI elements
        """
        args = {"area": area}
        if selector:
            args["selector"] = selector
            
        return await self._execute("ui_capture", args)
    
    async def sandbox(self, area: str, changes: List[Dict[str, Any]], preview: bool = True) -> Dict[str, Any]:
        """
        Test UI changes safely (detects and rejects frameworks!)
        
        Args:
            area: UI area name (use 'hephaestus' for general changes)
            changes: List of changes, each with:
                - type: 'html', 'css', or 'js'
                - selector: CSS selector
                - content: HTML/CSS/JS content
                - action: 'append', 'prepend', 'replace', 'before', 'after'
            preview: If True, test only. If False, apply changes.
            
        Returns:
            Result with validation and summary
        """
        return await self._execute("ui_sandbox", {
            "area": area,
            "changes": changes,
            "preview": preview
        })
    
    async def interact(self, area: str, action: str, selector: str, value: Optional[str] = None) -> Dict[str, Any]:
        """
        Interact with UI elements
        
        Args:
            area: UI area name
            action: 'click', 'type', 'select', or 'hover'
            selector: CSS selector for element
            value: Value for type/select actions
            
        Returns:
            Interaction result with changes captured
        """
        args = {
            "area": area,
            "action": action,
            "selector": selector
        }
        if value:
            args["value"] = value
            
        return await self._execute("ui_interact", args)
    
    async def analyze(self, area: str = "hephaestus", deep_scan: bool = False) -> Dict[str, Any]:
        """
        Analyze UI for frameworks and complexity
        
        Args:
            area: UI area name
            deep_scan: If True, performs deeper analysis
            
        Returns:
            Analysis including framework detection and recommendations
        """
        return await self._execute("ui_analyze", {
            "area": area,
            "deep_scan": deep_scan
        })
    
    async def _execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a UI DevTools command via HTTP API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_endpoint,
                    json={
                        "tool_name": tool_name,
                        "arguments": arguments
                    },
                    timeout=30.0
                )
                
                data = response.json()
                
                if data.get("status") == "success":
                    return data.get("result", {})
                else:
                    error = data.get('error', 'Unknown error')
                    self._last_error = error
                    
                    # Try to provide helpful guidance
                    if "Unknown UI area" in error:
                        raise Exception(f"{error}\n💡 Tip: Use ui.list_areas() to see valid area names!")
                    elif "rejected" in error.lower() and "framework" in error.lower():
                        raise Exception(f"{error}\n💡 Tip: Keep it simple! No React/Vue/Angular allowed!")
                    else:
                        raise Exception(f"UI DevTools error: {error}")
        except httpx.ConnectError:
            raise Exception(
                "Cannot connect to UI DevTools MCP!\n"
                "💡 Start it with: cd $TEKTON_ROOT/Hephaestus && ./run_mcp.sh"
            )
    
    async def add_footer_widget(self, area: str, content: str) -> bool:
        """
        Helper: Add a footer widget the RIGHT way
        
        Args:
            area: UI area name
            content: HTML content for the widget
            
        Returns:
            True if successful
        """
        # First test in preview mode
        preview_result = await self.sandbox(
            area,
            [{
                "type": "html",
                "selector": "body",  # Add to body if no footer exists
                "content": f'<div class="footer-widget">{content}</div>',
                "action": "append"
            }],
            preview=True
        )
        
        # Check if it would succeed
        if preview_result.get("summary", {}).get("successful", 0) > 0:
            # Apply for real
            result = await self.sandbox(
                area,
                [{
                    "type": "html",
                    "selector": "body",
                    "content": f'<div class="footer-widget">{content}</div>',
                    "action": "append"
                }],
                preview=False
            )
            return result.get("summary", {}).get("successful", 0) > 0
        
        return False


# Valid UI areas (v2 naming)
VALID_AREAS = [
    "hephaestus",  # The main UI container
    "rhetor", "hermes", "athena", "engram", "apollo",
    "prometheus", "ergon", "metis", "navigation",
    "content", "panel", "footer"
]


async def check_and_start_mcp():
    """Helper to check if MCP is running and provide instructions"""
    ui = UIDevTools()
    
    if await ui.health_check():
        print("✅ UI DevTools MCP is running")
        return True
    else:
        print("❌ UI DevTools MCP is NOT running")
        print("\nTo start it:")
        print("  cd $TEKTON_ROOT/Hephaestus")
        print("  ./run_mcp.sh")
        print("\nThen try again.")
        return False


# Example usage
if __name__ == "__main__":
    async def example():
        # Check MCP is running
        if not await check_and_start_mcp():
            return
        
        ui = UIDevTools()
        
        # Get help first!
        print("\n0. Getting help...")
        help_info = await ui.help()
        print(f"   Golden Rules: {len(help_info['golden_rules'])}")
        print(f"   First rule: {help_info['golden_rules'][0]}")
        
        # List available areas
        print("\n1. Listing UI areas...")
        areas = await ui.list_areas()
        print(f"   UI URL: {areas['ui_url']}")
        print(f"   Available areas: {len(areas['areas'])}")
        
        # Capture UI structure
        print("\n2. Capturing Rhetor area...")
        result = await ui.capture("rhetor")
        print(f"   Found {len(result.get('buttons', []))} buttons")
        print(f"   Found {len(result.get('forms', []))} forms")
        
        # Check for frameworks
        print("\n3. Analyzing for frameworks...")
        analysis = await ui.analyze("rhetor")
        frameworks = analysis['analysis']['frameworks']
        if any(frameworks.values()):
            print("   ⚠️  Frameworks detected!")
        else:
            print("   ✅ No frameworks detected")
        
        # Get specific help
        print("\n4. Getting help about common tasks...")
        task_help = await ui.help("tasks")
        print(f"   Available task examples: {len(task_help['tasks'])}")
        
        # Add a simple widget
        print("\n5. Adding footer widget...")
        success = await ui.add_footer_widget("rhetor", "Test Widget - Added via UI DevTools v2")
        if success:
            print("   ✅ Widget added successfully")
        else:
            print("   ❌ Failed to add widget")
    
    asyncio.run(example())