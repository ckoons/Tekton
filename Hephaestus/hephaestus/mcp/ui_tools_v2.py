"""
UI DevTools MCP v2 - Fixed to properly work with Hephaestus UI

IMPORTANT: This version correctly targets the Hephaestus UI at port 8080
and understands that all components are rendered within that single UI.
"""

import asyncio
import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from bs4 import BeautifulSoup, NavigableString, Tag
import lxml.html
from cssselect import GenericTranslator

# Import configuration properly
from shared.utils.global_config import GlobalConfig
from shared.utils.logging_setup import setup_component_logging

# Import constants and exceptions
from .constants import (
    HEPHAESTUS_PORT, HEPHAESTUS_URL, UI_COMPONENTS, DANGEROUS_PATTERNS,
    UIToolsError, ComponentNotFoundError, FrameworkDetectedError
)

# Import browser manager
from .browser_manager import browser_manager

# Import HTML processing functions
from .html_processor import (
    detect_dangerous_patterns,
    extract_element_info,
    suggest_similar_selectors,
    count_elements_in_tree,
    html_to_structured_data,
    analyze_dynamic_content
)

# Import navigation functions
from .navigation_tools import (
    find_component_element,
    ui_navigate
)

# Import capture functions
from .capture_tools import ui_capture

# Import sandbox functions
from .sandbox_tools import ui_sandbox

# Import analyze functions
from .analyze_tools import ui_analyze

# Import interaction functions
from .interaction_tools import ui_interact

# Import recommendation functions
from .recommendation_tools import ui_recommend_approach

# Import semantic analysis tools (Phase 2)
from .semantic_tools import ui_semantic_analysis, ui_semantic_scan, ui_semantic_patterns

# Initialize logger
logger = setup_component_logging("ui_devtools")





def list_ui_areas() -> Dict[str, Any]:
    """List all available UI areas and their descriptions"""
    return {
        "ui_url": HEPHAESTUS_URL,
        "areas": {
            name: {
                "description": info["description"],
                "example_selectors": info["selectors"][:2]  # Show first 2 examples
            }
            for name, info in UI_COMPONENTS.items()
        },
        "note": "All areas are within the main Hephaestus UI at port 8080"
    }










async def ui_list_areas() -> Dict[str, Any]:
    """
    List all available UI areas in Hephaestus
    
    Returns:
        Information about available UI areas and how to use them
    """
    return list_ui_areas()


async def ui_validate(
    scope: str = "current",
    checks: Optional[List[str]] = None,
    detailed: bool = False
) -> Dict[str, Any]:
    """
    Validate UI instrumentation and semantic tagging
    
    Args:
        scope: 'current' (loaded component), 'navigation', or 'all' (all components)
        checks: List of specific checks to run (defaults to all)
        detailed: Whether to include detailed findings
        
    Returns:
        Validation report with coverage metrics and recommendations
    """
    await browser_manager.initialize()
    page = await browser_manager.get_page()
    
    # Default checks if none specified
    if checks is None:
        checks = ["semantic-tags", "navigation", "data-attributes", "component-structure"]
    
    result = {
        "scope": scope,
        "timestamp": datetime.now().isoformat(),
        "checks_performed": checks,
        "summary": {},
        "findings": [],
        "recommendations": []
    }
    
    # Get current component state (only trust loaded component)
    component_state = await page.evaluate("""
        () => {
            // Find loaded component in content area - this is what matters
            let loadedComponent = null;
            const contentArea = document.querySelector('[data-tekton-area="content"], .main-content, #center-content');
            if (contentArea) {
                // Look for component indicators in content
                const componentElement = contentArea.querySelector('[data-tekton-area], [data-tekton-component], [data-component]');
                if (componentElement) {
                    loadedComponent = componentElement.getAttribute('data-tekton-area') || 
                                    componentElement.getAttribute('data-tekton-component') ||
                                    componentElement.getAttribute('data-component');
                } else {
                    // Try to detect by class name
                    const divWithClass = contentArea.querySelector('div[class*="__"]');
                    if (divWithClass) {
                        const className = divWithClass.className;
                        const match = className.match(/^(\\w+)__/);
                        if (match) {
                            loadedComponent = match[1];
                        }
                    }
                }
            }
            
            return { 
                loadedComponent: loadedComponent || 'unknown',
                hasContentArea: !!contentArea 
            };
        }
    """)
    
    # Validate based on scope
    if scope == "current":
        # Validate currently loaded component
        if not component_state["loadedComponent"] or component_state["loadedComponent"] == "unknown":
            result["error"] = "No component currently loaded"
            return result
            
        validation = await _validate_component(page, component_state["loadedComponent"], checks)
        result["component"] = component_state["loadedComponent"]
        result["summary"] = validation["summary"]
        result["findings"] = validation["findings"]
        result["recommendations"] = validation["recommendations"]
        
    elif scope == "navigation":
        # Validate navigation structure
        nav_validation = await _validate_navigation(page, checks)
        result["summary"] = nav_validation["summary"]
        result["findings"] = nav_validation["findings"]
        result["recommendations"] = nav_validation["recommendations"]
        
    elif scope == "all":
        # Get all components from navigation
        all_components = await page.evaluate("""
            () => {
                const navItems = document.querySelectorAll('.nav-item[data-component]');
                return Array.from(navItems).map(item => item.getAttribute('data-component'));
            }
        """)
        
        result["components_checked"] = []
        result["progress"] = []
        total_score = 0
        
        # Log start
        logger.info(f"Starting validation of {len(all_components)} components")
        
        # Skip certain utility components if desired
        skip_components = ['settings', 'profile']  # Can be made configurable
        
        for idx, component in enumerate(all_components):
            if component in skip_components:
                logger.info(f"Skipping utility component: {component}")
                continue
                
            progress_msg = f"Validating {component} ({idx+1}/{len(all_components)})"
            logger.info(progress_msg)
            result["progress"].append({
                "component": component,
                "status": "started",
                "timestamp": datetime.now().isoformat()
            })
            
            try:
                # Navigate to component with shorter timeout
                nav_result = await ui_navigate(component, wait_for_load=True, timeout=2000)
                
                if nav_result.get("navigation_completed"):
                    # Navigation worked - trust it and validate the component
                    validation = await _validate_component(page, component, checks)
                    
                    component_result = {
                        "component": component,
                        "score": validation["summary"].get("score", 0),
                        "issues": len(validation["findings"])
                    }
                    
                    if detailed:
                        component_result["findings"] = validation["findings"]
                    
                    result["components_checked"].append(component_result)
                    total_score += component_result["score"]
                    
                    result["progress"][-1]["status"] = "completed"
                else:
                    result["progress"][-1]["status"] = "navigation_failed"
                    logger.warning(f"Failed to navigate to {component}")
                    
            except asyncio.TimeoutError:
                result["progress"][-1]["status"] = "timeout"
                logger.warning(f"Timeout navigating to {component}")
            except Exception as e:
                result["progress"][-1]["status"] = "error"
                result["progress"][-1]["error"] = str(e)
                logger.error(f"Error validating {component}: {e}")
        
        # Calculate overall score
        if result["components_checked"]:
            result["summary"]["overall_score"] = total_score / len(result["components_checked"])
            result["summary"]["components_validated"] = len(result["components_checked"])
            result["summary"]["total_issues"] = sum(c["issues"] for c in result["components_checked"])
            result["summary"]["components_attempted"] = len(all_components)
            result["summary"]["validation_time"] = f"{(datetime.now() - datetime.fromisoformat(result['timestamp'])).total_seconds():.1f}s"
    
    # Add general recommendations based on findings
    if result["findings"] or (scope == "all" and result["summary"].get("total_issues", 0) > 0):
        result["recommendations"].append({
            "priority": "high",
            "message": "Review and add missing semantic tags using the instrumentation template"
        })
    
    return result


async def _validate_component(page: Page, component: str, checks: List[str]) -> Dict[str, Any]:
    """Validate a single component's instrumentation"""
    validation = {
        "summary": {"score": 100},
        "findings": [],
        "recommendations": []
    }
    
    # Check if component is loaded
    component_html = await page.evaluate(f"""
        () => {{
            const component = document.querySelector('[data-tekton-area="{component}"], [data-tekton-component="{component}"], .{component}');
            return component ? component.outerHTML : null;
        }}
    """)
    
    if not component_html:
        validation["findings"].append({
            "type": "error",
            "check": "component-presence",
            "message": f"Component '{component}' not found in DOM"
        })
        validation["summary"]["score"] = 0
        return validation
    
    # Parse component HTML
    soup = BeautifulSoup(component_html, 'html.parser')
    root = soup.find()
    
    # Check semantic tags
    if "semantic-tags" in checks:
        semantic_score = 100
        
        # Check root has data-tekton-area
        if not root.get("data-tekton-area"):
            validation["findings"].append({
                "type": "missing",
                "check": "semantic-tags",
                "element": "root",
                "message": f"Root element missing data-tekton-area=\"{component}\""
            })
            semantic_score -= 20
        
        # Check for zone tags
        zones = ["header", "menu", "content", "footer"]
        for zone in zones:
            zone_element = soup.find(attrs={"data-tekton-zone": zone})
            if not zone_element:
                # Try common class patterns
                zone_class = soup.find(class_=re.compile(f"{component}.*__{zone}"))
                if zone_class:
                    validation["findings"].append({
                        "type": "missing",
                        "check": "semantic-tags",
                        "element": f"{zone}",
                        "message": f"Found .{zone_class.get('class', [''])[0]} but missing data-tekton-zone=\"{zone}\""
                    })
                    semantic_score -= 10
        
        # Check for action tags on interactive elements
        buttons = soup.find_all(['button', 'a'])
        tabs = soup.find_all(class_=re.compile(r'.*__tab'))
        interactive = buttons + tabs
        
        if interactive:
            missing_actions = 0
            for elem in interactive[:10]:  # Check first 10
                if not elem.get("data-tekton-action"):
                    missing_actions += 1
            
            if missing_actions > 0:
                validation["findings"].append({
                    "type": "missing",
                    "check": "semantic-tags",
                    "element": "interactive",
                    "message": f"{missing_actions} interactive elements missing data-tekton-action"
                })
                semantic_score -= min(15, missing_actions * 3)
        
        validation["summary"]["semantic_score"] = max(0, semantic_score)
        validation["summary"]["score"] = min(validation["summary"]["score"], semantic_score)
    
    # Check data attributes
    if "data-attributes" in checks:
        data_attrs = {}
        for element in soup.find_all():
            for attr, value in element.attrs.items():
                if attr.startswith("data-"):
                    data_attrs[attr] = data_attrs.get(attr, 0) + 1
        
        validation["summary"]["data_attributes_count"] = len(data_attrs)
        validation["summary"]["data_tekton_coverage"] = sum(1 for k in data_attrs if k.startswith("data-tekton"))
    
    # Check component structure
    if "component-structure" in checks:
        structure_score = 100
        
        # Check BEM naming
        bem_pattern = re.compile(f"^{component}(__[a-z-]+)?(--[a-z-]+)?$")
        non_bem_classes = []
        
        for element in soup.find_all(class_=True):
            for cls in element.get("class", []):
                if cls.startswith(component) and not bem_pattern.match(cls):
                    non_bem_classes.append(cls)
        
        if non_bem_classes:
            validation["findings"].append({
                "type": "warning",
                "check": "component-structure",
                "message": f"Non-BEM classes found: {', '.join(set(non_bem_classes[:5]))}"
            })
            structure_score -= 10
        
        validation["summary"]["structure_score"] = structure_score
        validation["summary"]["score"] = min(validation["summary"]["score"], structure_score)
    
    # Add recommendations
    if validation["findings"]:
        validation["recommendations"].append({
            "component": component,
            "action": "Add missing semantic tags following the instrumentation template"
        })
    
    return validation


async def _validate_navigation(page: Page, checks: List[str]) -> Dict[str, Any]:
    """Validate navigation structure"""
    validation = {
        "summary": {"score": 100},
        "findings": [],
        "recommendations": []
    }
    
    nav_data = await page.evaluate("""
        () => {
            const navItems = document.querySelectorAll('.nav-item');
            const results = [];
            
            navItems.forEach(item => {
                results.push({
                    hasDataComponent: !!item.getAttribute('data-component'),
                    hasDataTektonNavItem: !!item.getAttribute('data-tekton-nav-item'),
                    hasDataTektonState: !!item.getAttribute('data-tekton-state'),
                    component: item.getAttribute('data-component'),
                    classes: Array.from(item.classList)
                });
            });
            
            return {
                totalItems: navItems.length,
                items: results,
                hasMainNav: !!document.querySelector('[data-tekton-nav="main"]')
            };
        }
    """)
    
    if "navigation" in checks:
        nav_score = 100
        
        if not nav_data["hasMainNav"]:
            validation["findings"].append({
                "type": "missing",
                "check": "navigation",
                "message": "Main navigation missing data-tekton-nav=\"main\""
            })
            nav_score -= 20
        
        # Check each nav item
        missing_attrs = 0
        for item in nav_data["items"]:
            if not item["hasDataTektonNavItem"]:
                missing_attrs += 1
        
        if missing_attrs > 0:
            validation["findings"].append({
                "type": "missing",
                "check": "navigation",
                "message": f"{missing_attrs} nav items missing data-tekton-nav-item"
            })
            nav_score -= min(30, missing_attrs * 5)
        
        validation["summary"]["navigation_score"] = nav_score
        validation["summary"]["score"] = nav_score
        validation["summary"]["nav_items_checked"] = nav_data["totalItems"]
    
    return validation


async def ui_batch(
    area: str,
    operations: List[Dict[str, Any]],
    atomic: bool = True
) -> Dict[str, Any]:
    """
    Execute multiple UI operations in batch
    
    Args:
        area: UI area to operate on (e.g., 'hephaestus')
        operations: List of operations to perform
        atomic: If True, all operations must succeed or all are rolled back
        
    Returns:
        Result with success status and details of each operation
    """
    await browser_manager.initialize()
    page = await browser_manager.get_page()
    
    result = {
        "area": area,
        "atomic": atomic,
        "total_operations": len(operations),
        "completed": 0,
        "failed": 0,
        "operations_results": [],
        "rollback_performed": False
    }
    
    # Capture initial state if atomic mode
    initial_state = None
    if atomic:
        logger.info("Capturing initial state for atomic batch operation")
        initial_capture = await ui_capture(area=area)
        initial_state = await page.content()
    
    # Execute each operation
    for idx, operation in enumerate(operations):
        op_result = {
            "index": idx,
            "action": operation.get("action"),
            "status": "pending",
            "details": {}
        }
        
        try:
            action = operation.get("action")
            logger.info(f"Executing batch operation {idx+1}/{len(operations)}: {action}")
            
            if action == "rename":
                # Text replacement operation
                from_text = operation.get("from")
                to_text = operation.get("to")
                selector = operation.get("selector", f"*:contains('{from_text}')")
                
                change = {
                    "type": "text",
                    "selector": selector,
                    "content": to_text,
                    "action": "replace"
                }
                
                sandbox_result = await ui_sandbox(area=area, changes=[change], preview=False)
                op_result["status"] = "success" if sandbox_result.get("summary", {}).get("successful", 0) > 0 else "failed"
                op_result["details"] = sandbox_result
                
            elif action == "remove":
                # Remove element operation
                selector = operation.get("selector")
                if not selector:
                    # Build selector from component and target
                    component = operation.get("component")
                    target = operation.get("target", "emoji")
                    if target == "emoji":
                        selector = f"[data-component='{component}'] .button-icon"
                    else:
                        selector = f"[data-component='{component}'] .{target}"
                
                change = {
                    "type": "html",
                    "selector": selector,
                    "content": "",
                    "action": "replace"
                }
                
                sandbox_result = await ui_sandbox(area=area, changes=[change], preview=False)
                op_result["status"] = "success" if sandbox_result.get("summary", {}).get("successful", 0) > 0 else "failed"
                op_result["details"] = sandbox_result
                
            elif action == "add_class":
                # Add CSS class operation
                selector = operation.get("selector")
                class_name = operation.get("class")
                
                await page.evaluate(f"""
                    () => {{
                        const elements = document.querySelectorAll('{selector}');
                        elements.forEach(el => el.classList.add('{class_name}'));
                        return elements.length;
                    }}
                """)
                
                op_result["status"] = "success"
                op_result["details"]["message"] = f"Added class '{class_name}' to elements"
                
            elif action == "remove_class":
                # Remove CSS class operation
                selector = operation.get("selector")
                class_name = operation.get("class")
                
                await page.evaluate(f"""
                    () => {{
                        const elements = document.querySelectorAll('{selector}');
                        elements.forEach(el => el.classList.remove('{class_name}'));
                        return elements.length;
                    }}
                """)
                
                op_result["status"] = "success"
                op_result["details"]["message"] = f"Removed class '{class_name}' from elements"
                
            elif action == "style":
                # Apply CSS styles
                selector = operation.get("selector")
                styles = operation.get("styles", {})
                
                changes = []
                for prop, value in styles.items():
                    changes.append({
                        "type": "css",
                        "selector": selector,
                        "property": prop,
                        "value": value
                    })
                
                sandbox_result = await ui_sandbox(area=area, changes=changes, preview=False)
                op_result["status"] = "success" if sandbox_result.get("summary", {}).get("successful", 0) > 0 else "failed"
                op_result["details"] = sandbox_result
                
            elif action == "navigate":
                # Navigate to component
                component = operation.get("component")
                nav_result = await ui_navigate(component=component)
                op_result["status"] = "success" if nav_result.get("navigation_completed") else "failed"
                op_result["details"] = nav_result
                
            elif action == "click":
                # Click element
                selector = operation.get("selector")
                interact_result = await ui_interact(area=area, action="click", selector=selector)
                op_result["status"] = "success" if "error" not in interact_result else "failed"
                op_result["details"] = interact_result
                
            else:
                op_result["status"] = "failed"
                op_result["error"] = f"Unknown action: {action}"
            
            # Update counters
            if op_result["status"] == "success":
                result["completed"] += 1
            else:
                result["failed"] += 1
                
            result["operations_results"].append(op_result)
            
            # Check atomic mode failure
            if atomic and op_result["status"] == "failed":
                logger.warning(f"Atomic batch operation failed at step {idx+1}")
                break
                
        except Exception as e:
            logger.error(f"Error in batch operation {idx+1}: {e}")
            op_result["status"] = "error"
            op_result["error"] = str(e)
            result["failed"] += 1
            result["operations_results"].append(op_result)
            
            if atomic:
                break
    
    # Handle rollback if atomic and any failed
    if atomic and result["failed"] > 0 and initial_state:
        logger.info("Performing rollback due to atomic batch failure")
        try:
            # Restore initial state
            await page.set_content(initial_state)
            result["rollback_performed"] = True
            result["rollback_status"] = "success"
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            result["rollback_status"] = "failed"
            result["rollback_error"] = str(e)
    
    # Summary
    result["success"] = result["failed"] == 0
    result["summary"] = {
        "total": len(operations),
        "completed": result["completed"],
        "failed": result["failed"],
        "success_rate": f"{(result['completed'] / len(operations) * 100):.1f}%" if operations else "0%"
    }
    
    return result


async def ui_help(topic: Optional[str] = None) -> Dict[str, Any]:
    """
    Get help about UI DevTools usage
    
    Args:
        topic: Specific topic or leave empty for general help
            Valid topics: 'areas', 'selectors', 'frameworks', 'errors', 'tasks', 'architecture'
    
    Returns:
        Help information with examples and guidance
    """
    from datetime import datetime
    
    help_topics = {
        "areas": {
            "title": "Understanding UI Areas",
            "explanation": "ALL UI is in Hephaestus at port 8080. Components like Rhetor, Hermes, etc. are AREAS within the Hephaestus UI, not separate applications.",
            "key_point": "🎯 There is only ONE UI at http://localhost:8080",
            "example": """# List all available areas
areas = await ui_list_areas()

# Capture the Rhetor area within Hephaestus
result = await ui_capture('rhetor')

# Work with navigation area
nav = await ui_capture('navigation')""",
            "common_mistakes": [
                "❌ Trying to connect to port 8003 - that's Rhetor's API, not UI!",
                "❌ Looking for separate UIs for each component",
                "❌ Using 'rhetor-ui' instead of just 'rhetor'"
            ],
            "pro_tip": "Use ui_list_areas() whenever you're unsure about area names!"
        },
        
        "selectors": {
            "title": "Using CSS Selectors",
            "explanation": "CSS selectors let you target specific elements within a UI area.",
            "selector_priority": [
                "1. #specific-id - Most reliable",
                "2. .component-class - Good for groups",
                "3. [data-component='x'] - Semantic",
                "4. tag - Use sparingly"
            ],
            "example": """# Capture specific element in Rhetor
footer = await ui_capture('rhetor', '#rhetor-footer')

# Multiple selector attempts
selectors = ['#footer', '.footer', 'footer']
for sel in selectors:
    try:
        result = await ui_capture('rhetor', sel)
        break
    except:
        continue""",
            "debugging": "Use ui_capture without selector first to see what's available",
            "patterns": {
                "Tekton standard": "#component-area (e.g., #rhetor-content)",
                "Navigation": "#left-nav, .navigation",
                "Content": "#center-content, .content-area",
                "Panels": "#right-panel, .panel-right"
            }
        },
        
        "frameworks": {
            "title": "The Framework-Free Philosophy",
            "explanation": "Hephaestus UI is intentionally simple. NO frameworks allowed!",
            "casey_says": "🧓 'I'm 70 years old and I like simple things that work!'",
            "why_no_frameworks": [
                "✅ Performance - No framework overhead",
                "✅ Maintainability - Anyone can understand HTML/CSS",
                "✅ Reliability - Fewer dependencies = fewer problems",
                "✅ Casey's sanity - He really means it!"
            ],
            "alternatives": {
                "Instead of React component": "Use simple HTML: '<div class=\"widget\">Content</div>'",
                "Instead of Vue reactivity": "Use data attributes: 'data-state=\"active\"'",
                "Instead of Angular forms": "Use standard HTML forms with fetch",
                "Instead of CSS frameworks": "Use Tekton's existing styles"
            },
            "example": """# ❌ WRONG - This will be rejected!
changes = [{
    "type": "html",
    "content": '<script>import React from "react"</script>'
}]

# ✅ RIGHT - Simple and effective
changes = [{
    "type": "html",
    "content": '<div class="status">Online</div>',
    "selector": "#rhetor-header",
    "action": "append"
}]"""
        },
        
        "errors": {
            "title": "Common Errors and Solutions",
            "errors": {
                "Unknown UI area": {
                    "cause": "Using invalid area name",
                    "solution": "Run ui_list_areas() to see valid names",
                    "example": "Use 'rhetor' not 'rhetor-ui' or 'rhetor-component'"
                },
                "Selector not found": {
                    "cause": "Element doesn't exist or wrong selector",
                    "solution": "Capture area first without selector to explore",
                    "example": "await ui_capture('rhetor') # See what's there"
                },
                "Change rejected": {
                    "cause": "Framework or dangerous pattern detected",
                    "solution": "Use simple HTML/CSS only",
                    "example": "No React, Vue, Angular, webpack, npm, etc."
                },
                "Browser error": {
                    "cause": "Browser crashed or page not loaded",
                    "solution": "The browser will auto-restart, just retry",
                    "example": "await ui_capture('hephaestus') # Retry"
                }
            },
            "debugging_workflow": """1. Check area name with ui_list_areas()
2. Capture without selector to explore
3. Verify selector in captured content
4. Test with preview=True first
5. Check for framework violations"""
        },
        
        "tasks": {
            "title": "Common UI Tasks",
            "tasks": {
                "Add timestamp": {
                    "description": "Add a timestamp to any area",
                    "code": """await ui_sandbox('rhetor', [{
    'type': 'html',
    'selector': '#rhetor-footer',
    'content': f'<div class="timestamp">Updated: {datetime.now():%H:%M}</div>',
    'action': 'append'
}], preview=False)""",
                    "warning": "Don't use moment.js or date libraries!"
                },
                "Add status indicator": {
                    "description": "Show component status",
                    "code": """# HTML
status_html = '''<div id="status" class="status-indicator">
    <span class="dot"></span>
    <span class="text">Ready</span>
</div>'''

# CSS
status_css = '''.status-indicator { display: flex; align-items: center; gap: 8px; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: #4CAF50; }
.dot.busy { background: #FFA726; animation: pulse 1s infinite; }'''

# Apply both
await ui_sandbox('rhetor', [
    {'type': 'html', 'selector': '#rhetor-header', 'content': status_html, 'action': 'append'},
    {'type': 'css', 'content': status_css}
], preview=False)"""
                },
                "Modify navigation": {
                    "description": "Update navigation elements",
                    "code": """# Highlight active nav item
await ui_sandbox('navigation', [{
    'type': 'css',
    'content': '.nav-item.active { background: rgba(255,255,255,0.1); }'
}], preview=True)"""
                },
                "Add notification": {
                    "description": "Show a notification",
                    "code": """notif = '''<div class="notification" style="position:fixed; top:20px; right:20px; 
    background:#333; color:white; padding:12px 20px; border-radius:8px; z-index:1000;">
    ✓ Task completed successfully
</div>'''
await ui_sandbox('hephaestus', [{
    'type': 'html', 'selector': 'body', 'content': notif, 'action': 'append'
}], preview=False)"""
                }
            }
        },
        
        "architecture": {
            "title": "Hephaestus UI Architecture",
            "mental_model": """
🏛️ HEPHAESTUS UI (Port 8080) - The Temple of UI
│
├── 🧭 Navigation Area (#left-nav)
│   └── Links to different component areas
│
├── 📋 Content Area (#center-content)
│   ├── 🤖 Rhetor Area (LLM chat interface)
│   ├── 📨 Hermes Area (Messaging system)
│   ├── 🧠 Athena Area (Knowledge base)
│   ├── 💾 Engram Area (Memory system)
│   └── ... other component areas
│
└── 📊 Panel Area (#right-panel)
    └── Contextual information and controls""",
            "key_concepts": {
                "Single UI": "Everything is at http://localhost:8080",
                "Areas not Apps": "Components are areas within Hephaestus",
                "Dynamic Loading": "Areas appear based on navigation",
                "Shared Layout": "All components use the same structure"
            },
            "port_clarification": """
Component Ports - What They Really Are:
• Port 8080 (Hephaestus) = THE UI ← You want this!
• Port 8003 (Rhetor) = API only (no UI here!)
• Port 8001 (Hermes) = API only (no UI here!)
• Port 8010 (Athena) = API only (no UI here!)

Think of it like a restaurant:
- Hephaestus (8080) is the dining room where you see everything
- Other ports are the kitchen doors (API access only)""",
            "example": """# ✅ CORRECT - All UI work happens through Hephaestus
ui_capture('rhetor')  # Gets Rhetor area from Hephaestus UI

# ❌ WRONG - These ports have no UI!
# http://localhost:8003  # No UI here!
# http://localhost:8001  # No UI here!"""
        }
    }
    
    # If specific topic requested
    if topic and topic.lower() in help_topics:
        return help_topics[topic.lower()]
    
    # General help overview
    return {
        "welcome": "🛠️ Welcome to Hephaestus UI DevTools Help!",
        "version": "v2.0 (The one that actually works correctly)",
        "golden_rules": [
            "🎯 Rule 1: ALL UI is at http://localhost:8080",
            "🚫 Rule 2: NO frameworks (React, Vue, Angular, etc.)",
            "✅ Rule 3: Simple HTML/CSS is always the answer",
            "🔍 Rule 4: Use ui_list_areas() when confused",
            "🧪 Rule 5: Always preview=True before preview=False"
        ],
        "quick_start": """
# 1. See what areas are available
areas = await ui_list_areas()

# 2. Navigate to a component
await ui_navigate('rhetor')

# 3. Capture the area to explore it
rhetor = await ui_capture('rhetor')

# 4. Make a simple change (preview first!)
await ui_sandbox('rhetor', [{
    'type': 'html',
    'selector': '#rhetor-footer',
    'content': '<div>Hello from DevTools!</div>',
    'action': 'append'
}], preview=True)

# 5. Apply if it looks good
await ui_sandbox('rhetor', [...], preview=False)
""",
        "available_tools": {
            "ui_list_areas()": "Discover all UI areas in Hephaestus",
            "ui_navigate(component)": "Navigate to a component by clicking its nav item",
            "ui_capture(area, selector?)": "Look at UI structure without screenshots",
            "ui_sandbox(area, changes, preview)": "Safely test UI modifications", 
            "ui_interact(area, action, selector, value?)": "Click, type, select elements",
            "ui_analyze(area)": "Check for frameworks and complexity",
            "ui_help(topic?)": "This help system!"
        },
        "help_topics": {
            "areas": "Understanding UI areas vs components",
            "selectors": "How to target specific elements",
            "frameworks": "Why we don't use them (and what to do instead)",
            "errors": "Common errors and how to fix them",
            "tasks": "Code examples for common UI tasks",
            "architecture": "The big picture of Hephaestus UI"
        },
        "pro_tips": [
            "💡 Confused about ports? Remember: 8080 is the ONLY UI port",
            "💡 Can't find an element? Capture without selector first",
            "💡 Change rejected? You probably tried to add a framework",
            "💡 Need to modify Rhetor? It's an area IN Hephaestus, not separate"
        ],
        "casey_quote": "🧓 'Keep it simple. If you're thinking about npm install, you're thinking wrong!'",
        "get_specific_help": "Call ui_help('topic') for detailed help. Topics: " + ", ".join(help_topics.keys())
    }


# Export functions for MCP registration
__all__ = [
    "ui_list_areas",
    "ui_recommend_approach",  # Phase 1: Intelligent routing
    "ui_capture",
    "ui_navigate",
    "ui_interact", 
    "ui_sandbox",
    "ui_analyze",
    "ui_validate",
    "ui_batch",
    "ui_help",
    # Phase 2: Semantic analysis
    "ui_semantic_analysis",
    "ui_semantic_scan",
    "ui_semantic_patterns",
    "browser_manager"
]