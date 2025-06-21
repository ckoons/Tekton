"""
Screenshot Tools for UI DevTools - Phase 4
Allows CIs to take their own screenshots without bothering humans!
"""

from typing import Dict, Any, Optional
import base64
from datetime import datetime
from pathlib import Path


async def ui_screenshot(
    component: Optional[str] = None,
    full_page: bool = True,
    highlight: Optional[str] = None,
    save_to_file: bool = False
) -> Dict[str, Any]:
    """
    Take a screenshot of the Tekton UI
    
    Args:
        component: Specific component to capture (None = entire Hephaestus)
        full_page: Capture full scrollable area or just viewport
        highlight: CSS selector to highlight with a border before capture
        save_to_file: Save to file in addition to returning base64
        
    Returns:
        Dict containing:
        - image: Base64 encoded PNG
        - timestamp: When the screenshot was taken
        - component: What was captured
        - dimensions: Width and height
        - file_path: Path if saved to file
    """
    try:
        from .browser_manager import browser_manager
        
        # Get the browser page
        page = await browser_manager.get_page()
        if not page:
            return {
                "error": "No browser page available",
                "help": "Make sure to use ui_navigate or ui_capture first"
            }
        
        # Navigate to component if specified
        if component:
            # Try to click on the component's nav item
            try:
                await page.click(f'[data-component="{component}"]', timeout=5000)
                await page.wait_for_timeout(500)  # Let transitions complete
            except:
                # Component might already be visible or nav click failed
                pass
        
        # Highlight element if requested
        if highlight:
            try:
                await page.evaluate(f'''
                    const element = document.querySelector('{highlight}');
                    if (element) {{
                        element.style.border = '3px solid #ff0000';
                        element.style.boxShadow = '0 0 10px rgba(255,0,0,0.5)';
                    }}
                ''')
            except:
                pass  # Don't fail if highlight doesn't work
        
        # Take the screenshot
        screenshot_options = {
            "full_page": full_page,
            "type": "png"
        }
        
        # If component specified, try to capture just that area
        if component and not full_page:
            try:
                # Find the component's container
                element = await page.query_selector(f'[data-tekton-component="{component}"]')
                if not element:
                    element = await page.query_selector(f'.{component}')
                
                if element:
                    screenshot_data = await element.screenshot()
                else:
                    screenshot_data = await page.screenshot(**screenshot_options)
            except:
                screenshot_data = await page.screenshot(**screenshot_options)
        else:
            screenshot_data = await page.screenshot(**screenshot_options)
        
        # Remove highlight if we added one
        if highlight:
            try:
                await page.evaluate(f'''
                    const element = document.querySelector('{highlight}');
                    if (element) {{
                        element.style.border = '';
                        element.style.boxShadow = '';
                    }}
                ''')
            except:
                pass
        
        # Get page dimensions
        dimensions = await page.evaluate('''() => {
            return {
                width: document.documentElement.scrollWidth,
                height: document.documentElement.scrollHeight,
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight
                }
            }
        }''')
        
        # Convert to base64
        image_base64 = base64.b64encode(screenshot_data).decode('utf-8')
        
        result = {
            "success": True,
            "image": image_base64,
            "timestamp": datetime.now().isoformat(),
            "component": component or "full_hephaestus",
            "dimensions": dimensions,
            "full_page": full_page
        }
        
        # Save to file if requested
        if save_to_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{component or 'hephaestus'}_{timestamp}.png"
            file_path = Path(f"/tmp/{filename}")
            file_path.write_bytes(screenshot_data)
            result["file_path"] = str(file_path)
            result["file_size"] = len(screenshot_data)
        
        return result
        
    except Exception as e:
        return {
            "error": f"Failed to take screenshot: {str(e)}",
            "success": False
        }


async def ui_visual_diff(
    before_action: Dict[str, Any],
    after_action: Dict[str, Any],
    highlight_changes: bool = True
) -> Dict[str, Any]:
    """
    Compare UI state before and after an action
    
    Args:
        before_action: Action to perform before first screenshot
                      e.g., {"type": "navigate", "component": "rhetor"}
        after_action: Action to perform before second screenshot
                     e.g., {"type": "modify", "selector": ".title", "text": "New Title"}
        highlight_changes: Whether to highlight what changed
        
    Returns:
        Comparison results with before/after screenshots and analysis
    """
    try:
        from .browser_manager import browser_manager
        from .sandbox_tools import ui_sandbox
        from .navigation_tools import ui_navigate
        
        # Take "before" screenshot
        if before_action.get("type") == "navigate":
            await ui_navigate(before_action.get("component", "hephaestus"))
        
        before_screenshot = await ui_screenshot(
            component=before_action.get("component"),
            full_page=False  # Viewport only for faster comparison
        )
        
        if not before_screenshot.get("success"):
            return {
                "error": "Failed to capture 'before' state",
                "details": before_screenshot
            }
        
        # Perform the action
        if after_action.get("type") == "modify":
            # Use sandbox to make temporary changes
            changes = [{
                "type": "text",
                "selector": after_action.get("selector"),
                "content": after_action.get("text", ""),
                "action": "replace"
            }]
            
            result = await ui_sandbox(
                area=after_action.get("component", "hephaestus"),
                changes=changes,
                preview=False  # Actually apply for screenshot
            )
            
            if result.get("error"):
                return {
                    "error": "Failed to apply changes",
                    "details": result
                }
        
        # Take "after" screenshot
        after_screenshot = await ui_screenshot(
            component=after_action.get("component", before_action.get("component")),
            full_page=False,
            highlight=after_action.get("selector") if highlight_changes else None
        )
        
        if not after_screenshot.get("success"):
            return {
                "error": "Failed to capture 'after' state",
                "details": after_screenshot
            }
        
        # Analyze what changed (basic for now)
        analysis = {
            "before_size": len(before_screenshot["image"]),
            "after_size": len(after_screenshot["image"]),
            "size_change": len(after_screenshot["image"]) - len(before_screenshot["image"]),
            "dimensions_changed": before_screenshot["dimensions"] != after_screenshot["dimensions"]
        }
        
        return {
            "success": True,
            "before": {
                "screenshot": before_screenshot["image"],
                "timestamp": before_screenshot["timestamp"],
                "dimensions": before_screenshot["dimensions"]
            },
            "after": {
                "screenshot": after_screenshot["image"],
                "timestamp": after_screenshot["timestamp"],
                "dimensions": after_screenshot["dimensions"]
            },
            "analysis": analysis,
            "actions_performed": {
                "before": before_action,
                "after": after_action
            }
        }
        
    except Exception as e:
        return {
            "error": f"Failed to perform visual diff: {str(e)}",
            "success": False
        }


async def ui_capture_all_components() -> Dict[str, Any]:
    """
    Take screenshots of all Tekton components in sequence
    Perfect for documentation or full system visual testing
    
    Returns:
        Dict with screenshots of all components
    """
    try:
        from .browser_manager import browser_manager
        from .navigation_tools import ui_navigate
        from .constants import UI_COMPONENTS
        
        results = {}
        failed = []
        
        # Get list of components
        components = list(UI_COMPONENTS.keys())
        
        for component in components:
            try:
                # Navigate to component
                nav_result = await ui_navigate(component)
                if nav_result.get("error"):
                    failed.append({
                        "component": component,
                        "error": "Navigation failed",
                        "details": nav_result
                    })
                    continue
                
                # Wait a bit for component to load
                page = await browser_manager.get_page()
                await page.wait_for_timeout(1000)
                
                # Take screenshot
                screenshot = await ui_screenshot(
                    component=component,
                    full_page=True,
                    save_to_file=True  # Save for documentation
                )
                
                if screenshot.get("success"):
                    results[component] = {
                        "image": screenshot["image"],
                        "file_path": screenshot.get("file_path"),
                        "dimensions": screenshot["dimensions"],
                        "timestamp": screenshot["timestamp"]
                    }
                else:
                    failed.append({
                        "component": component,
                        "error": "Screenshot failed",
                        "details": screenshot
                    })
                    
            except Exception as e:
                failed.append({
                    "component": component,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "captured": len(results),
            "failed": len(failed),
            "components": results,
            "failures": failed,
            "summary": f"Captured {len(results)}/{len(components)} components"
        }
        
    except Exception as e:
        return {
            "error": f"Failed to capture all components: {str(e)}",
            "success": False
        }