"""
UI Workflow Tools V2 - Improved based on real testing feedback
Addresses navigation reliability, error messages, and verification
"""
import asyncio
from typing import Dict, List, Any, Optional, Literal, Tuple
from .browser_manager import browser_manager
from .navigation_tools import ui_navigate
from .capture_tools import ui_capture
from .sandbox_tools import ui_sandbox
from .screenshot_tools import ui_screenshot, ui_visual_diff
from .interaction_tools import ui_interact
from shared.utils.logging_setup import setup_component_logging

logger = setup_component_logging("ui_workflow_v2")

WorkflowType = Literal[
    "modify_component",
    "add_to_component", 
    "verify_component",
    "debug_component"
]


async def verify_component_loaded(
    component: str, 
    max_attempts: int = 3,
    wait_between: float = 2.0
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Robustly verify that a component has actually loaded
    
    Returns:
        Tuple of (success, message, capture_data)
    """
    for attempt in range(max_attempts):
        # Capture current state
        capture = await ui_capture(area="content")
        loaded_component = capture.get("loaded_component", "unknown")
        html = capture.get("html", "")
        
        # Multiple verification methods
        checks = {
            "loaded_component_field": loaded_component == component,
            "component_class_in_html": f"{component}__" in html,
            "component_name_in_html": component.lower() in html.lower(),
            "has_component_structure": any([
                f'class="{component}' in html,
                f'id="{component}' in html,
                f'data-component="{component}"' in html
            ])
        }
        
        # If any strong indicator is present, consider it loaded
        if checks["loaded_component_field"] or (checks["component_class_in_html"] and checks["has_component_structure"]):
            return True, f"Component {component} verified as loaded", capture
        
        # If not the last attempt, try navigation again
        if attempt < max_attempts - 1:
            logger.info(f"Component {component} not loaded (attempt {attempt + 1}/{max_attempts}), retrying...")
            
            # Try different navigation methods
            if attempt == 0:
                # First retry: Just navigate again
                await ui_navigate(component=component)
            else:
                # Second retry: Try clicking directly
                await ui_interact(
                    area="navigation",
                    action="click",
                    selector=f'[data-component="{component}"]'
                )
            
            await asyncio.sleep(wait_between)
    
    # Failed after all attempts
    failure_msg = (
        f"Failed to load {component} after {max_attempts} attempts.\n"
        f"Current component: {loaded_component}\n"
        f"Verification results: {checks}"
    )
    return False, failure_msg, capture


async def get_available_selectors(capture_data: Dict[str, Any], limit: int = 10) -> List[str]:
    """Extract available selectors from capture data for better error messages"""
    elements = capture_data.get("structure", {}).get("elements", [])
    selectors = []
    
    for elem in elements[:limit]:
        # Build selector from element info
        tag = elem.get("tag", "")
        elem_id = elem.get("id")
        classes = elem.get("classes", [])
        
        if elem_id:
            selectors.append(f"#{elem_id}")
        elif classes:
            selectors.append(f".{classes[0]}")
        elif tag and tag != "[document]":
            selectors.append(tag)
    
    return selectors


async def ui_workflow_v2(
    workflow: WorkflowType,
    component: str,
    changes: Optional[List[Dict[str, Any]]] = None,
    selector: Optional[str] = None,
    debug: bool = False,
    max_retries: int = 3
) -> Dict[str, Any]:
    """
    Improved UI workflow with better reliability and error handling
    
    Key improvements:
    - Robust navigation verification
    - Detailed error messages with context
    - Better component state detection
    - Retry logic for navigation
    """
    
    result = {
        "workflow": workflow,
        "component": component,
        "steps": [],
        "success": True,
        "screenshots": {},
        "diagnostics": {}
    }
    
    async def log_step(step: str, status: str = "completed", data: Any = None):
        """Enhanced step logging"""
        step_info = {"step": step, "status": status, "timestamp": asyncio.get_event_loop().time()}
        if data:
            step_info["data"] = data
        result["steps"].append(step_info)
        if debug:
            logger.info(f"[{status}] {step}")
    
    try:
        if workflow in ["modify_component", "add_to_component"]:
            if not changes:
                return {
                    "status": "error",
                    "success": False,
                    "error": "No changes provided",
                    "suggestion": "Provide a 'changes' array with objects containing 'selector', 'content', and 'action' fields",
                    "example": {
                        "changes": [{
                            "selector": ".component__header",
                            "content": "<div>New content</div>",
                            "action": "append"
                        }]
                    }
                }
            
            # Step 1: Initial state capture
            await log_step("Capturing initial state")
            initial_capture = await ui_capture(area="content")
            initial_component = initial_capture.get("loaded_component", "unknown")
            result["diagnostics"]["initial_state"] = {
                "loaded_component": initial_component,
                "url": initial_capture.get("current_url")
            }
            
            # Step 2: Navigate with verification
            await log_step(f"Navigating to {component} (from {initial_component})")
            nav_result = await ui_navigate(component=component)
            
            if not nav_result.get("navigation_completed"):
                await log_step("Navigation failed", status="error")
                return {
                    "status": "error",
                    "success": False,
                    "error": f"Navigation to {component} failed",
                    "current_state": initial_component,
                    "suggestion": f"Try navigating manually or check if {component} is available in the navigation"
                }
            
            # Step 3: Robust component verification
            await log_step("Verifying component loaded")
            loaded, message, capture = await verify_component_loaded(component, max_retries)
            
            if not loaded:
                await log_step("Component verification failed", status="error", data=message)
                return {
                    "status": "error",
                    "success": False,
                    "error": f"Component {component} did not load properly",
                    "details": message,
                    "current_state": capture.get("loaded_component", "unknown"),
                    "suggestion": "The component may be unavailable or require different navigation steps"
                }
            
            await log_step("Component verified as loaded")
            result["diagnostics"]["loaded_state"] = {
                "component": component,
                "element_count": len(capture.get("structure", {}).get("elements", []))
            }
            
            # Step 4: Take before screenshot
            await log_step("Taking before screenshot")
            before = await ui_screenshot(component=component, save_to_file=True)
            if before.get("status") == "success":
                result["screenshots"]["before"] = before.get("file_path", "")
            
            # Step 5: Apply changes with detailed error handling
            await log_step("Applying changes to content area")
            
            # Pre-validate selectors exist
            available_selectors = await get_available_selectors(capture)
            
            for i, change in enumerate(changes):
                target_selector = change.get("selector", "")
                
                # Check if selector might exist
                if not any(target_selector in str(s) for s in available_selectors + [capture.get("html", "")]):
                    logger.warning(f"Selector '{target_selector}' may not exist in component")
            
            sandbox_result = await ui_sandbox(
                area="content",
                changes=changes,
                preview=False
            )
            
            if sandbox_result.get("status") != "success":
                # Enhanced error message
                error_msg = sandbox_result.get("error", "Unknown error")
                await log_step("Failed to apply changes", status="error", data=error_msg)
                
                # Build helpful error response
                failed_selector = None
                for change in changes:
                    if change.get("selector") in str(error_msg):
                        failed_selector = change.get("selector")
                        break
                
                return {
                    "status": "error",
                    "success": False,
                    "error": f"Failed to apply changes to {component}",
                    "details": error_msg,
                    "failed_selector": failed_selector,
                    "available_selectors": available_selectors[:5],
                    "loaded_component": capture.get("loaded_component"),
                    "suggestion": (
                        f"The selector '{failed_selector}' was not found. "
                        f"Try one of these selectors: {', '.join(available_selectors[:3])}"
                    ) if failed_selector else "Check that your selectors match the component structure"
                }
            
            # Step 6: Take after screenshot with highlight
            await log_step("Taking after screenshot")
            highlight_selector = changes[0].get("selector") if changes else None
            after = await ui_screenshot(
                component=component,
                highlight=highlight_selector,
                save_to_file=True
            )
            if after.get("status") == "success":
                result["screenshots"]["after"] = after.get("file_path", "")
            
            # Success summary
            result["summary"] = f"Successfully modified {component}"
            result["visual_feedback"] = f"""
✅ Workflow completed successfully!
   
   Component: {component}
   Changes Applied: {len(changes)}
   
   Screenshots:
   - Before: {result['screenshots'].get('before', 'N/A')}
   - After:  {result['screenshots'].get('after', 'N/A')}
   
   Verification: Component was properly loaded before applying changes
"""
            
        elif workflow == "debug_component":
            # Enhanced debugging workflow
            await log_step(f"Starting debug analysis for {component}")
            
            # Comprehensive state analysis
            diagnostics = {
                "initial_state": {},
                "navigation_attempt": {},
                "final_state": {},
                "ui_analysis": {},
                "recommendations": []
            }
            
            # Check initial state
            initial = await ui_capture(area="content")
            diagnostics["initial_state"] = {
                "loaded_component": initial.get("loaded_component", "unknown"),
                "url": initial.get("current_url"),
                "has_terminal_active": "terminal-panel active" in initial.get("html", "")
            }
            
            # Try navigation
            await log_step(f"Attempting navigation to {component}")
            nav = await ui_navigate(component=component)
            diagnostics["navigation_attempt"] = {
                "reported_success": nav.get("navigation_completed", False),
                "method": "ui_navigate"
            }
            
            # Wait and verify
            await asyncio.sleep(2)
            loaded, message, final = await verify_component_loaded(component, max_attempts=1)
            
            diagnostics["final_state"] = {
                "component_loaded": loaded,
                "loaded_component": final.get("loaded_component", "unknown"),
                "verification_message": message
            }
            
            # Analyze UI structure
            diagnostics["ui_analysis"] = {
                "areas_found": {},
                "selectors_found": {}
            }
            
            for area in ["navigation", "content", component]:
                try:
                    area_capture = await ui_capture(area=area)
                    if area_capture.get("status") == "success":
                        html = area_capture.get("html", "")
                        diagnostics["ui_analysis"]["areas_found"][area] = {
                            "accessible": True,
                            "has_component_reference": component in html.lower(),
                            "element_count": len(area_capture.get("structure", {}).get("elements", []))
                        }
                except Exception as e:
                    diagnostics["ui_analysis"]["areas_found"][area] = {
                        "accessible": False,
                        "error": str(e)
                    }
            
            # Generate actionable recommendations
            if not loaded:
                if diagnostics["initial_state"]["has_terminal_active"]:
                    diagnostics["recommendations"].append(
                        "Terminal panel is active. Component might be hidden behind it. "
                        "Try switching to the HTML view or closing the terminal."
                    )
                
                if diagnostics["initial_state"]["loaded_component"] == diagnostics["final_state"]["loaded_component"]:
                    diagnostics["recommendations"].append(
                        f"Navigation didn't change the loaded component. "
                        f"Still showing '{diagnostics['initial_state']['loaded_component']}'. "
                        f"The navigation click might not be working properly."
                    )
                
                if not diagnostics["ui_analysis"]["areas_found"].get("navigation", {}).get("accessible"):
                    diagnostics["recommendations"].append(
                        "Navigation area is not accessible. The UI structure might have changed."
                    )
            else:
                diagnostics["recommendations"].append(
                    f"Component {component} loaded successfully! Use area='content' for modifications."
                )
            
            result["diagnostics"] = diagnostics
            result["visual_feedback"] = f"""
🔍 Debug Report for {component}:

Initial State: {diagnostics['initial_state']['loaded_component']}
Final State: {diagnostics['final_state']['loaded_component']}
Component Loaded: {'✅ Yes' if loaded else '❌ No'}

Navigation:
- Attempted: {'✓' if diagnostics['navigation_attempt']['reported_success'] else '✗'}
- Result: {message}

UI Analysis:
{chr(10).join(f"- {area}: {'✓ Accessible' if info.get('accessible') else '✗ Not accessible'}" 
              for area, info in diagnostics['ui_analysis']['areas_found'].items())}

Recommendations:
{chr(10).join(f"• {rec}" for rec in diagnostics['recommendations'])}
"""
            
        elif workflow == "verify_component":
            # Quick but thorough verification
            await log_step(f"Quick verification of {component}")
            
            # Navigate
            nav = await ui_navigate(component=component)
            
            # Verify with retries
            loaded, message, capture = await verify_component_loaded(component, max_attempts=2)
            
            # Take screenshot
            screenshot = await ui_screenshot(component=component, save_to_file=True)
            
            result["verification"] = {
                "component_loaded": loaded,
                "loaded_component": capture.get("loaded_component", "unknown"),
                "screenshot": screenshot.get("file_path", "") if screenshot.get("status") == "success" else None,
                "element_count": len(capture.get("structure", {}).get("elements", [])),
                "message": message
            }
            
            result["visual_feedback"] = f"""
{'✅' if loaded else '❌'} {component} Verification:
   Status: {'Loaded' if loaded else 'Not Loaded'}
   Actual Component: {capture.get('loaded_component', 'unknown')}
   Elements Found: {len(capture.get('structure', {}).get('elements', []))}
   Screenshot: {result['verification']['screenshot'] or 'Failed to capture'}
   
   {message}
"""
        
        else:
            result["success"] = False
            result["error"] = f"Unknown workflow type: {workflow}"
            result["suggestion"] = "Valid workflows: modify_component, add_to_component, verify_component, debug_component"
        
        return result
        
    except Exception as e:
        await log_step(f"Unexpected error: {str(e)}", status="error")
        result["success"] = False
        result["error"] = f"Workflow failed with unexpected error: {str(e)}"
        result["visual_feedback"] = f"❌ Workflow failed: {str(e)}"
        logger.error(f"Workflow {workflow} failed with exception", exc_info=True)
        return result


# Make it available as the main function
ui_workflow = ui_workflow_v2