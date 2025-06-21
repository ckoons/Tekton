"""
Semantic Query Tools for Hephaestus UI DevTools - Phase 2

Tools for querying UI elements by their semantic tags.
"""

from typing import Dict, Any, List, Optional, Union
from playwright.async_api import Page

from .constants import ComponentNotFoundError
from .browser_manager import browser_manager
from shared.utils.logging_setup import setup_component_logging

logger = setup_component_logging("ui_semantic_query")


async def ui_semantic_query(
    query: Union[str, Dict[str, str]],
    area: str = "hephaestus",
    wait_for: Optional[str] = None,
    timeout: int = 5000,
    return_content: bool = True
) -> Dict[str, Any]:
    """
    Query UI elements by semantic tags
    
    Args:
        query: Either a CSS selector string for semantic tags, or a dict of tag:value pairs
               Examples: 
               - "[data-tekton-component='rhetor']"
               - {"component": "rhetor", "state": "active"}
               - "[data-tekton-loading-state='loaded']"
        area: UI area to search within (default: entire UI)
        wait_for: Optional selector to wait for before querying
        timeout: Maximum time to wait (ms)
        return_content: Whether to return element content (text/HTML)
        
    Returns:
        Matching elements with their attributes and content
    """
    await browser_manager.initialize()
    page = await browser_manager.get_page()
    
    result = {
        "query": query,
        "area": area,
        "matches": [],
        "count": 0
    }
    
    try:
        # Build the query selector
        if isinstance(query, dict):
            # Convert dict to CSS selector
            selector_parts = []
            for tag, value in query.items():
                if value:
                    selector_parts.append(f'[data-tekton-{tag}="{value}"]')
                else:
                    selector_parts.append(f'[data-tekton-{tag}]')
            selector = "".join(selector_parts)
            result["selector"] = selector
        else:
            selector = query
            result["selector"] = selector
        
        # Wait for optional element first
        if wait_for:
            try:
                await page.wait_for_selector(wait_for, timeout=timeout)
                result["wait_for_completed"] = True
            except Exception as e:
                result["wait_for_error"] = str(e)
                logger.warning(f"Wait for selector failed: {e}")
        
        # Find all matching elements
        elements = await page.query_selector_all(selector)
        
        if not elements:
            result["message"] = f"No elements found matching: {selector}"
            return result
        
        # Extract information from each element
        for i, element in enumerate(elements[:50]):  # Limit to 50 elements
            element_info = {
                "index": i,
                "tag": await element.evaluate("el => el.tagName.toLowerCase()"),
                "attributes": {}
            }
            
            # Get all data-tekton attributes
            attributes = await element.evaluate("""
                el => {
                    const attrs = {};
                    for (const attr of el.attributes) {
                        if (attr.name.startsWith('data-tekton-')) {
                            attrs[attr.name.replace('data-tekton-', '')] = attr.value;
                        }
                    }
                    return attrs;
                }
            """)
            element_info["attributes"] = attributes
            
            # Get common attributes
            for attr in ["id", "class", "href", "src", "type", "name"]:
                value = await element.get_attribute(attr)
                if value:
                    element_info[attr] = value
            
            # Get content if requested
            if return_content:
                # Text content
                text = await element.text_content()
                if text and text.strip():
                    element_info["text"] = text.strip()[:200]  # Limit length
                
                # Inner HTML for containers
                if element_info["tag"] in ["div", "section", "main", "article"]:
                    inner_html = await element.inner_html()
                    if inner_html:
                        element_info["html_preview"] = inner_html[:300] + "..." if len(inner_html) > 300 else inner_html
            
            # Check visibility
            element_info["visible"] = await element.is_visible()
            
            # Get bounding box for visible elements
            if element_info["visible"]:
                try:
                    box = await element.bounding_box()
                    if box:
                        element_info["position"] = {
                            "x": int(box["x"]),
                            "y": int(box["y"]),
                            "width": int(box["width"]),
                            "height": int(box["height"])
                        }
                except:
                    pass
            
            result["matches"].append(element_info)
        
        result["count"] = len(elements)
        if len(elements) > 50:
            result["message"] = f"Found {len(elements)} elements, showing first 50"
        
        # Add summary of found semantic tags
        all_tags = set()
        for match in result["matches"]:
            all_tags.update(match["attributes"].keys())
        result["semantic_tags_found"] = sorted(list(all_tags))
        
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Semantic query error: {e}")
    
    return result


async def ui_query_loading_states() -> Dict[str, Any]:
    """
    Query all loading states in the UI
    
    Returns:
        All elements with loading state information
    """
    result = await ui_semantic_query(
        query="[data-tekton-loading-state]",
        return_content=False
    )
    
    # Enhance with loading-specific information
    if result.get("matches"):
        loading_summary = {
            "pending": 0,
            "loading": 0,
            "loaded": 0,
            "error": 0
        }
        
        for match in result["matches"]:
            state = match["attributes"].get("loading-state", "unknown")
            if state in loading_summary:
                loading_summary[state] += 1
            
            # Add timing info if available
            if "loading-started" in match["attributes"]:
                try:
                    started = int(match["attributes"]["loading-started"])
                    # Calculate duration if loaded/error
                    if state in ["loaded", "error"]:
                        match["load_duration_ms"] = "calculated from timestamp"
                except:
                    pass
        
        result["loading_summary"] = loading_summary
        result["has_active_loading"] = loading_summary["pending"] > 0 or loading_summary["loading"] > 0
    
    return result


async def ui_find_interactive(
    area: str = "hephaestus",
    type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Find all interactive elements in an area
    
    Args:
        area: UI area to search
        type: Optional type filter (button, input, link, form)
        
    Returns:
        Interactive elements with their semantic tags
    """
    await browser_manager.initialize()
    page = await browser_manager.get_page()
    
    result = {
        "area": area,
        "interactive_elements": [],
        "summary": {}
    }
    
    # Define interactive selectors
    interactive_selectors = {
        "button": "button, [data-tekton-action], [data-tekton-trigger]",
        "input": "input, textarea, select, [data-tekton-input]",
        "link": "a[href], [data-tekton-link]",
        "form": "form, [data-tekton-form]"
    }
    
    if type and type in interactive_selectors:
        selectors_to_check = {type: interactive_selectors[type]}
    else:
        selectors_to_check = interactive_selectors
    
    try:
        for element_type, selector in selectors_to_check.items():
            elements = await page.query_selector_all(selector)
            
            for element in elements[:20]:  # Limit per type
                element_info = {
                    "type": element_type,
                    "tag": await element.evaluate("el => el.tagName.toLowerCase()"),
                    "semantic_tags": {}
                }
                
                # Get semantic attributes
                semantic_attrs = await element.evaluate("""
                    el => {
                        const attrs = {};
                        for (const attr of el.attributes) {
                            if (attr.name.startsWith('data-tekton-')) {
                                attrs[attr.name.replace('data-tekton-', '')] = attr.value;
                            }
                        }
                        return attrs;
                    }
                """)
                element_info["semantic_tags"] = semantic_attrs
                
                # Get identifying info
                element_info["id"] = await element.get_attribute("id")
                element_info["name"] = await element.get_attribute("name")
                
                # Get text/label
                if element_type == "button":
                    element_info["text"] = await element.text_content()
                elif element_type == "input":
                    element_info["placeholder"] = await element.get_attribute("placeholder")
                    element_info["value"] = await element.get_attribute("value")
                elif element_type == "link":
                    element_info["href"] = await element.get_attribute("href")
                    element_info["text"] = await element.text_content()
                
                # Check if enabled/visible
                element_info["enabled"] = await element.is_enabled()
                element_info["visible"] = await element.is_visible()
                
                result["interactive_elements"].append(element_info)
        
        # Create summary
        result["summary"] = {
            "total_found": len(result["interactive_elements"]),
            "by_type": {}
        }
        
        for element in result["interactive_elements"]:
            elem_type = element["type"]
            if elem_type not in result["summary"]["by_type"]:
                result["summary"]["by_type"][elem_type] = 0
            result["summary"]["by_type"][elem_type] += 1
        
        # Find semantic patterns
        semantic_actions = set()
        semantic_triggers = set()
        for element in result["interactive_elements"]:
            if "action" in element["semantic_tags"]:
                semantic_actions.add(element["semantic_tags"]["action"])
            if "trigger" in element["semantic_tags"]:
                semantic_triggers.add(element["semantic_tags"]["trigger"])
        
        if semantic_actions:
            result["semantic_actions_found"] = sorted(list(semantic_actions))
        if semantic_triggers:
            result["semantic_triggers_found"] = sorted(list(semantic_triggers))
            
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Find interactive error: {e}")
    
    return result


async def ui_query_by_state(
    state_type: str,
    state_value: Optional[str] = None
) -> Dict[str, Any]:
    """
    Query elements by their state attributes
    
    Args:
        state_type: Type of state to query (state, status, loading-state, etc.)
        state_value: Optional specific value to match
        
    Returns:
        Elements matching the state criteria
    """
    if state_value:
        query = f"[data-tekton-{state_type}='{state_value}']"
    else:
        query = f"[data-tekton-{state_type}]"
    
    result = await ui_semantic_query(query, return_content=True)
    
    # Add state-specific analysis
    if result.get("matches"):
        state_values = {}
        for match in result["matches"]:
            value = match["attributes"].get(state_type, "undefined")
            if value not in state_values:
                state_values[value] = 0
            state_values[value] += 1
        
        result["state_distribution"] = state_values
        result["unique_states"] = sorted(list(state_values.keys()))
    
    return result