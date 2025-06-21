"""
Capture Tools Module for Hephaestus UI DevTools

This module contains functions for capturing UI state, including HTML content,
forms, buttons, links, and screenshots.
"""

from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup

from .constants import HEPHAESTUS_URL, UI_COMPONENTS, ComponentNotFoundError
from .browser_manager import browser_manager
from .navigation_tools import find_component_element
from .html_processor import html_to_structured_data, analyze_dynamic_content
from shared.utils.logging_setup import setup_component_logging

logger = setup_component_logging("ui_capture")


async def ui_capture(
    area: str = "hephaestus",
    selector: Optional[str] = None,
    include_screenshot: bool = False
) -> Dict[str, Any]:
    """
    Capture UI state from Hephaestus UI with enhanced dynamic content detection
    
    Args:
        area: UI area name (e.g., 'rhetor', 'navigation', 'content')
              Use 'hephaestus' for the entire UI
        selector: Optional CSS selector for specific element within the area
        include_screenshot: Whether to include a visual screenshot
    
    Returns:
        Structured data about the UI state with dynamic content analysis
    """
    await browser_manager.initialize()
    page = await browser_manager.get_page()
    
    result = {
        "area": area,
        "ui_url": HEPHAESTUS_URL,
        "title": await page.title(),
        "current_url": page.url,
        "viewport": page.viewport_size,
    }
    
    # Detect current component state (ignoring unreliable nav state)
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
            
            // Check if we're in a special view (settings, profile)
            const specialViews = ['settings', 'profile'];
            let currentView = null;
            for (const view of specialViews) {
                if (document.querySelector(`.${view}__container, #${view}-container, [data-component="${view}"]`)) {
                    currentView = view;
                    break;
                }
            }
            
            return {
                loaded_component: loadedComponent || currentView,
                detection_method: loadedComponent ? 'data-attribute' : (currentView ? 'special-view' : 'none')
            };
        }
    """)
    
    # Add component state to result
    result["loaded_component"] = component_state["loaded_component"]
    
    # What really matters is what's loaded
    if component_state["loaded_component"]:
        result["working_with"] = component_state["loaded_component"]
    
    # Check for loading states in the DOM
    loading_state_check = await page.evaluate("""
        () => {
            const loadingElements = document.querySelectorAll('[data-tekton-loading-state]');
            const loadingComponents = [];
            
            loadingElements.forEach(el => {
                const state = el.getAttribute('data-tekton-loading-state');
                const component = el.getAttribute('data-tekton-loading-component');
                const started = el.getAttribute('data-tekton-loading-started');
                
                if (state && state !== 'loaded') {
                    loadingComponents.push({
                        component: component || 'unknown',
                        state: state,
                        started: started ? new Date(parseInt(started)).toLocaleString() : null,
                        error: state === 'error' ? el.getAttribute('data-tekton-loading-error') : null
                    });
                }
            });
            
            return {
                hasLoadingComponents: loadingComponents.length > 0,
                loadingComponents: loadingComponents,
                allLoadingStates: Array.from(loadingElements).map(el => ({
                    component: el.getAttribute('data-tekton-loading-component'),
                    state: el.getAttribute('data-tekton-loading-state')
                }))
            };
        }
    """)
    
    # Add loading state info to result
    if loading_state_check["hasLoadingComponents"]:
        result["warnings"] = result.get("warnings", [])
        result["warnings"].append({
            "type": "components_loading",
            "message": "Some components are still loading",
            "loading_components": loading_state_check["loadingComponents"]
        })
    
    result["loading_states"] = loading_state_check["allLoadingStates"]
    
    # Get HTML content for the specified area
    if area == "hephaestus":
        # Capture entire UI
        html = await page.content()
        result["description"] = "Entire Hephaestus UI"
    else:
        # Find the component area
        try:
            element = await find_component_element(page, area)
            html = await element.inner_html()
            result["description"] = UI_COMPONENTS[area]["description"]
            result["found_with_selector"] = await element.evaluate("el => el.tagName + (el.id ? '#' + el.id : '') + (el.className ? '.' + el.className.split(' ').join('.') : '')")
        except ComponentNotFoundError as e:
            result["error"] = str(e)
            result["available_areas"] = list(UI_COMPONENTS.keys())
            return result
    
    # Apply additional selector if provided
    if selector:
        result["selector"] = selector
        # Parse the HTML we already have instead of waiting for selector on page
        # This is more reliable and works with the area concept
    
    # Add raw HTML to result for better debugging and searching
    result["html"] = html
    result["html_length"] = len(html)
    
    # Convert to structured data
    result["structure"] = html_to_structured_data(html, selector)
    
    # Parse HTML once for all operations
    soup = BeautifulSoup(html, 'html.parser')
    
    # Add common selector counts for quick reference
    result["selectors_available"] = {
        ".nav-label": len(soup.select(".nav-label")),
        "[data-component]": len(soup.select("[data-component]")),
        "[data-tekton-nav]": len(soup.select("[data-tekton-nav]")),
        "[data-tekton-area]": len(soup.select("[data-tekton-area]")),
        "button": len(soup.select("button")),
        "input": len(soup.select("input")),
        "form": len(soup.select("form")),
        "a": len(soup.select("a"))
    }
    
    # If selector was not found, add the suggestions to the main result for visibility
    if result["structure"].get("selector_not_found"):
        result["selector_error"] = result["structure"]["suggestion_message"]
        result["suggestions"] = result["structure"]["suggestions"]
        # Return early since there's no point extracting forms/buttons/etc from non-existent elements
        return result
    
    # Extract forms
    forms = soup.find_all("form")
    if forms:
        result["forms"] = []
        for form in forms:
            form_data = {
                "id": form.get("id"),
                "action": form.get("action"),
                "method": form.get("method"),
                "inputs": []
            }
            
            inputs = form.find_all(["input", "select", "textarea"])
            for input_el in inputs:
                input_data = {
                    "type": input_el.get("type", "text"),
                    "name": input_el.get("name"),
                    "id": input_el.get("id"),
                    "value": input_el.get("value"),
                    "placeholder": input_el.get("placeholder")
                }
                form_data["inputs"].append(input_data)
            
            result["forms"].append(form_data)
    
    # Extract buttons
    buttons = soup.find_all(["button", "input[type='button']", "input[type='submit']"])
    if buttons:
        result["buttons"] = []
        for button in buttons[:20]:  # Limit to 20
            text = button.get_text(strip=True) if hasattr(button, 'get_text') else button.get("value", "")
            result["buttons"].append({
                "text": text,
                "id": button.get("id"),
                "classes": " ".join(button.get("class", [])) if button.get("class") else None,
                "onclick": button.get("onclick")
            })
    
    # Extract links
    links = soup.find_all("a", href=True)
    if links:
        result["links"] = []
        for link in links[:20]:  # Limit to 20
            result["links"].append({
                "href": link.get("href"),
                "text": link.get_text(strip=True),
                "id": link.get("id")
            })
    
    # PHASE 1 ENHANCEMENT: Dynamic Content Analysis
    result["dynamic_analysis"] = await analyze_dynamic_content(page, area, html)
    
    # Include screenshot if requested
    if include_screenshot:
        screenshot = await page.screenshot(full_page=False)
        result["screenshot"] = {
            "type": "base64",
            "data": screenshot.hex()
        }
    
    return result