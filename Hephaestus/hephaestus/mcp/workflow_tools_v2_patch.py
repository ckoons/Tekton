"""
Quick patches for the minor suggestions in V2 feedback
These can be integrated into workflow_tools_v2.py
"""

async def ui_workflow_v2_patched(
    workflow: WorkflowType,
    component: str,
    changes: Optional[List[Dict[str, Any]]] = None,
    selector: Optional[str] = None,
    debug: bool = False,
    max_retries: int = 3,
    timeout: Optional[float] = None  # NEW: Configurable timeout
) -> Dict[str, Any]:
    """
    V2.1 with minor improvements based on 9.5/10 feedback
    
    New in V2.1:
    - Configurable timeouts per workflow
    - Better screenshot failure handling
    - Option to force component switch
    """
    
    # Default timeouts by workflow type
    default_timeouts = {
        "verify_component": 15.0,
        "debug_component": 20.0,
        "modify_component": 30.0,
        "add_to_component": 30.0
    }
    
    workflow_timeout = timeout or default_timeouts.get(workflow, 30.0)
    
    # ... rest of implementation with timeout management ...


async def handle_screenshot_safely(component: str, **kwargs) -> Dict[str, Any]:
    """
    Safely handle screenshot with fallback on failure
    """
    try:
        result = await ui_screenshot(component=component, **kwargs)
        if result.get("status") == "success":
            return {"success": True, "path": result.get("file_path", "")}
        else:
            return {
                "success": False, 
                "path": None,
                "note": "Screenshot failed but workflow continued"
            }
    except Exception as e:
        logger.warning(f"Screenshot failed for {component}: {str(e)}")
        return {
            "success": False,
            "path": None, 
            "note": f"Screenshot skipped due to error: {str(e)}"
        }


async def force_component_switch(component: str) -> bool:
    """
    More direct component switching when navigation fails
    
    This could use direct JavaScript evaluation or other methods
    """
    # Try direct panel switching
    try:
        # First, ensure we're in HTML view (not terminal)
        await ui_interact(
            area="content",
            action="execute_script",
            script="""
            // Force switch from terminal to HTML view if needed
            const terminalPanel = document.querySelector('.terminal-panel.active');
            const htmlPanel = document.querySelector('.html-panel');
            if (terminalPanel && htmlPanel) {
                terminalPanel.classList.remove('active');
                htmlPanel.classList.add('active');
            }
            """
        )
        
        # Then try direct component activation
        await ui_interact(
            area="navigation",
            action="execute_script",
            script=f"""
            // Force activate component
            const componentLink = document.querySelector('[data-component="{component}"]');
            if (componentLink) {{
                // Remove active from all
                document.querySelectorAll('.nav-item').forEach(el => 
                    el.classList.remove('active')
                );
                // Add active to target
                componentLink.closest('.nav-item').classList.add('active');
                // Trigger click
                componentLink.click();
            }}
            """
        )
        
        return True
    except Exception as e:
        logger.warning(f"Force switch failed: {str(e)}")
        return False


# Enhanced debug recommendations
def get_enhanced_recommendations(diagnostics: Dict[str, Any], component: str) -> List[str]:
    """
    Generate even more specific recommendations based on diagnostics
    """
    recommendations = []
    
    # Terminal panel detection
    if diagnostics["initial_state"].get("has_terminal_active"):
        recommendations.append(
            "🖥️ Terminal panel is blocking the view. Solutions:\n"
            "   1. Click the HTML/Preview tab to switch views\n"
            "   2. Use ui_interact to click '.html-panel-tab'\n"
            "   3. Or close the terminal with the X button"
        )
    
    # Navigation failure patterns
    if diagnostics["navigation_attempt"]["reported_success"] but \
       diagnostics["final_state"]["loaded_component"] == diagnostics["initial_state"]["loaded_component"]:
        recommendations.append(
            "🔄 Navigation reported success but nothing changed. Try:\n"
            "   1. Refresh the page (F5) and try again\n"
            "   2. Check if component is disabled/hidden\n"
            "   3. Use force_component_switch option (coming soon)"
        )
    
    # Component availability
    nav_accessible = diagnostics["ui_analysis"]["areas_found"].get("navigation", {}).get("accessible")
    if nav_accessible:
        recommendations.append(
            f"✅ Navigation is accessible. Try clicking {component} manually to verify it works"
        )
    
    return recommendations