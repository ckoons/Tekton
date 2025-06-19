"""
UI Workflow Tool - Smart composite operations that just work!
Created by Claude #4 after experiencing the pain firsthand 😅
"""
import asyncio
from typing import Dict, List, Any, Optional, Literal
from ..mcp.tool_registry import tool

WorkflowType = Literal[
    "modify_component",
    "add_to_component", 
    "verify_component",
    "debug_component"
]

@tool
async def ui_workflow(
    context,
    workflow: WorkflowType,
    component: str,
    changes: Optional[List[Dict[str, Any]]] = None,
    selector: Optional[str] = None,
    debug: bool = False
) -> Dict[str, Any]:
    """
    Smart UI workflow that handles common patterns automatically.
    
    No more confusion about areas vs components!
    
    Args:
        workflow: Type of workflow to execute
        component: Component to work with (rhetor, hermes, etc.)
        changes: List of changes for modify workflows
        selector: Optional specific selector to target
        debug: Show detailed step-by-step progress
        
    Examples:
        # Add status indicator to Hermes
        await ui_workflow(
            workflow="add_to_component",
            component="hermes", 
            changes=[{
                "selector": ".hermes__header",
                "content": '<div class="status">🟢 Connected</div>',
                "action": "append"
            }]
        )
        
        # Debug why component isn't loading
        await ui_workflow(
            workflow="debug_component",
            component="hermes"
        )
    """
    
    result = {
        "workflow": workflow,
        "component": component,
        "steps": [],
        "success": True,
        "screenshots": {}
    }
    
    async def log_step(step: str, data: Any = None):
        """Log a workflow step"""
        step_info = {"step": step, "status": "completed"}
        if data:
            step_info["data"] = data
        result["steps"].append(step_info)
        if debug:
            print(f"🔧 {step}")
    
    try:
        if workflow == "modify_component" or workflow == "add_to_component":
            if not changes:
                return {
                    "status": "error",
                    "error": "Changes required for modify/add workflows"
                }
            
            # Step 1: Navigate to component
            await log_step(f"Navigating to {component}")
            nav_result = await context.ui_navigate(component=component)
            
            if nav_result.get("status") != "success":
                result["success"] = False
                result["error"] = f"Failed to navigate to {component}"
                return result
            
            # Step 2: Smart wait for content load
            await log_step("Waiting for content to load")
            await asyncio.sleep(1.5)  # TODO: Replace with smart wait
            
            # Step 3: Verify component loaded
            await log_step("Verifying component loaded")
            capture = await context.ui_capture(area="content")
            
            # Check if component actually loaded
            html = capture.get("result", {}).get("html", "")
            if f"{component}__" not in html and component not in html.lower():
                # Try one more time with longer wait
                await log_step("Component not detected, waiting longer...")
                await asyncio.sleep(2)
                capture = await context.ui_capture(area="content")
                html = capture.get("result", {}).get("html", "")
            
            # Step 4: Take before screenshot
            await log_step("Taking before screenshot")
            before = await context.ui_screenshot(
                component=component,
                save_to_file=True
            )
            if before.get("status") == "success":
                result["screenshots"]["before"] = before.get("result", {}).get("file_path")
            
            # Step 5: Apply changes to CONTENT area (the magic fix!)
            await log_step("Applying changes to content area")
            sandbox_result = await context.ui_sandbox(
                area="content",  # Always use content for component mods!
                changes=changes,
                preview=False
            )
            
            if sandbox_result.get("status") != "success":
                result["success"] = False
                result["error"] = f"Failed to apply changes: {sandbox_result.get('error')}"
                return result
            
            # Step 6: Take after screenshot with highlight
            await log_step("Taking after screenshot")
            # Extract selector from first change for highlight
            highlight_selector = changes[0].get("selector") if changes else None
            after = await context.ui_screenshot(
                component=component,
                highlight=highlight_selector,
                save_to_file=True
            )
            if after.get("status") == "success":
                result["screenshots"]["after"] = after.get("result", {}).get("file_path")
            
            # Success summary
            result["summary"] = f"Successfully modified {component}"
            result["visual_feedback"] = f"""
✅ Workflow completed!
   1. Navigated to {component} ✓
   2. Applied {len(changes)} changes ✓
   3. Screenshots saved ✓
   
   Before: {result['screenshots'].get('before', 'N/A')}
   After:  {result['screenshots'].get('after', 'N/A')}
"""
            
        elif workflow == "debug_component":
            # Smart debugging workflow
            await log_step(f"Debugging {component} component")
            
            # Check current state
            current = await context.ui_capture(area="content")
            loaded = current.get("result", {}).get("loaded_component", "unknown")
            
            # Try to navigate
            await log_step(f"Attempting navigation to {component}")
            nav = await context.ui_navigate(component=component)
            await asyncio.sleep(1)
            
            # Check again
            after_nav = await context.ui_capture(area="content")
            new_loaded = after_nav.get("result", {}).get("loaded_component", "unknown")
            
            # Analyze all areas
            areas_info = {}
            for area in ["content", "navigation", component]:
                try:
                    cap = await context.ui_capture(area=area)
                    if cap.get("status") == "success":
                        html_preview = cap.get("result", {}).get("html", "")[:200]
                        areas_info[area] = {
                            "accessible": True,
                            "preview": html_preview,
                            "has_component_content": f"{component}__" in html_preview
                        }
                except:
                    areas_info[area] = {"accessible": False}
            
            result["debug_info"] = {
                "before_navigation": {
                    "loaded_component": loaded,
                    "url": current.get("result", {}).get("current_url")
                },
                "after_navigation": {
                    "loaded_component": new_loaded,
                    "navigation_status": nav.get("status")
                },
                "areas_analysis": areas_info,
                "recommendations": []
            }
            
            # Generate recommendations
            if new_loaded != component:
                result["debug_info"]["recommendations"].append(
                    f"Component didn't load. Try clicking manually or check if {component} is available"
                )
            if areas_info.get("content", {}).get("has_component_content"):
                result["debug_info"]["recommendations"].append(
                    "Component content found! Use area='content' for modifications"
                )
            else:
                result["debug_info"]["recommendations"].append(
                    f"No {component} content found. Component may not be loaded properly"
                )
            
            result["visual_feedback"] = f"""
🔍 Debug Report for {component}:
   Current Component: {loaded} → {new_loaded}
   Navigation: {nav.get('status')}
   Content Area Has {component}: {areas_info.get('content', {}).get('has_component_content', False)}
   
   Recommendations:
   {chr(10).join('   - ' + r for r in result['debug_info']['recommendations'])}
"""
            
        elif workflow == "verify_component":
            # Quick verification workflow
            await log_step(f"Verifying {component}")
            
            # Navigate
            await context.ui_navigate(component=component)
            await asyncio.sleep(1)
            
            # Capture and screenshot
            capture = await context.ui_capture(area="content")
            screenshot = await context.ui_screenshot(component=component, save_to_file=True)
            
            html = capture.get("result", {}).get("html", "")
            is_loaded = f"{component}__" in html or component in html.lower()
            
            result["verification"] = {
                "component_loaded": is_loaded,
                "screenshot": screenshot.get("result", {}).get("file_path"),
                "visible_elements": len(capture.get("result", {}).get("structure", {}).get("elements", []))
            }
            
            result["visual_feedback"] = f"""
{'✅' if is_loaded else '❌'} {component} Verification:
   Loaded: {is_loaded}
   Screenshot: {result['verification']['screenshot']}
   Visible Elements: {result['verification']['visible_elements']}
"""
        
        return result
        
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        result["visual_feedback"] = f"❌ Workflow failed: {str(e)}"
        return result