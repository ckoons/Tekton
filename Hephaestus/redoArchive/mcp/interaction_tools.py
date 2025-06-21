"""
Interaction Tools Module for Hephaestus UI DevTools

This module contains functions for interacting with UI elements including
clicking, typing, selecting, and hovering actions.
"""

import asyncio
from typing import Dict, Any, Optional

from .constants import ComponentNotFoundError
from .browser_manager import browser_manager
from .navigation_tools import find_component_element
from .html_processor import html_to_structured_data


async def ui_interact(
    area: str,
    action: str,
    selector: str,
    value: Optional[str] = None,
    capture_changes: bool = True
) -> Dict[str, Any]:
    """
    Interact with UI elements in Hephaestus
    
    Args:
        area: UI area name (use 'hephaestus' for general interactions)
        action: Type of action ('click', 'type', 'select', 'hover')
        selector: CSS selector for the element
        value: Value for type/select actions
        capture_changes: Whether to capture before/after state
    
    Returns:
        Result of the interaction including any changes
    """
    await browser_manager.initialize()
    page = await browser_manager.get_page()
    
    result = {
        "area": area,
        "action": action,
        "selector": selector,
        "value": value
    }
    
    # Navigate to component area first if specified
    if area != "hephaestus":
        try:
            await find_component_element(page, area)
        except ComponentNotFoundError as e:
            result["error"] = str(e)
            return result
    
    # Capture before state
    if capture_changes:
        before_html = await page.content()
        result["before"] = html_to_structured_data(before_html)
    
    # Set up monitoring
    console_messages = []
    network_requests = []
    
    async def handle_console(msg):
        console_messages.append({
            "type": msg.type,
            "text": msg.text
        })
    
    async def handle_request(request):
        if request.resource_type in ["xhr", "fetch"]:
            network_requests.append({
                "url": request.url,
                "method": request.method
            })
    
    page.on("console", handle_console)
    page.on("request", handle_request)
    
    try:
        # Wait for element
        element = await page.wait_for_selector(selector, timeout=5000)
        
        # Perform action
        if action == "click":
            await element.click()
            await page.wait_for_load_state("networkidle", timeout=5000)
        
        elif action == "type":
            if value is None:
                raise ValueError("Value required for type action")
            await element.clear()
            await element.type(value)
        
        elif action == "select":
            if value is None:
                raise ValueError("Value required for select action")
            await element.select_option(value)
        
        elif action == "hover":
            await element.hover()
            await asyncio.sleep(0.5)
        
        else:
            raise ValueError(f"Unknown action: {action}")
        
        result["success"] = True
        
        # Capture after state
        if capture_changes:
            after_html = await page.content()
            result["after"] = html_to_structured_data(after_html)
            
            # Simple change detection
            changes = []
            if len(before_html) != len(after_html):
                changes.append("Page content changed")
            
            if console_messages:
                changes.append(f"{len(console_messages)} console messages")
            
            if network_requests:
                changes.append(f"{len(network_requests)} network requests")
            
            result["changes"] = changes
        
        # Add console and network activity
        if console_messages:
            result["console"] = console_messages
        if network_requests:
            result["network"] = network_requests
    
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
    
    finally:
        page.remove_listener("console", handle_console)
        page.remove_listener("request", handle_request)
    
    return result