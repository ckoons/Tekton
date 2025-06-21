"""
Navigation Tools Module for Hephaestus UI DevTools

This module contains all navigation-related functions for moving between
UI components and finding component elements.
"""

from typing import Dict, Any, Optional
from playwright.async_api import Page

from .constants import UI_COMPONENTS, ComponentNotFoundError
from .browser_manager import browser_manager


async def find_component_element(page: Page, component: str) -> Optional[Any]:
    """Try to find a component area using multiple selectors"""
    if component not in UI_COMPONENTS:
        valid = ", ".join(sorted(UI_COMPONENTS.keys()))
        raise ComponentNotFoundError(
            f"Unknown UI area '{component}'. Valid areas: {valid}\n"
            f"Use 'hephaestus' for the main UI or see list_ui_areas() for all options."
        )
    
    selectors = UI_COMPONENTS[component]["selectors"]
    
    for selector in selectors:
        try:
            element = await page.query_selector(selector)
            if element:
                return element
        except:
            continue
    
    # If no element found, provide helpful error
    tried = ", ".join(selectors)
    raise ComponentNotFoundError(
        f"Could not find '{component}' area in the UI.\n"
        f"Tried selectors: {tried}\n"
        f"The component may not be visible or loaded yet."
    )


async def ui_navigate(
    component: str,
    wait_for_load: bool = True,
    timeout: int = 10000
) -> Dict[str, Any]:
    """
    Navigate to a specific component by clicking its nav item
    
    Args:
        component: Component name to navigate to (e.g., 'rhetor', 'prometheus')
        wait_for_load: Whether to wait for component to fully load
        timeout: Maximum time to wait for component load (ms)
        
    Returns:
        Navigation result with loaded component confirmation
    """
    await browser_manager.initialize()
    page = await browser_manager.get_page()
    
    result = {
        "component": component,
        "navigation_started": False,
        "navigation_completed": False,
        "current_component": None
    }
    
    try:
        # First, check what's currently active
        active_nav = await page.query_selector('[data-tekton-nav-item][data-tekton-state="active"]')
        if active_nav:
            current = await active_nav.get_attribute("data-tekton-nav-item")
            result["current_component"] = current
            
            if current == component:
                result["message"] = f"Already on {component}"
                result["navigation_completed"] = True
                return result
        
        # Find the nav item for the requested component
        nav_selector = f'[data-tekton-nav-item="{component}"]'
        nav_item = await page.wait_for_selector(nav_selector, timeout=5000)
        
        if not nav_item:
            result["error"] = f"Navigation item for '{component}' not found"
            return result
        
        # Click the nav item
        await nav_item.click()
        result["navigation_started"] = True
        
        if wait_for_load:
            # Wait a moment for click to register
            await page.wait_for_timeout(500)
            
            # First, try to wait for the component to reach loaded state
            # This leverages our new semantic loading state system
            try:
                # Step 1: Wait for the loading process to START
                # This ensures MinimalLoader has begun working on this component
                component_loading_selector = f'[data-tekton-loading-component="{component}"]'
                await page.wait_for_selector(
                    component_loading_selector,
                    timeout=2000  # 2 seconds should be plenty for loader to start
                )
                
                # Step 2: Now wait for the component to finish loading
                loaded_selector = f'[data-tekton-loading-component="{component}"][data-tekton-loading-state="loaded"]'
                error_selector = f'[data-tekton-loading-component="{component}"][data-tekton-loading-state="error"]'
                
                # Wait for either loaded or error state
                await page.wait_for_selector(
                    f'{loaded_selector}, {error_selector}',
                    timeout=timeout
                )
                
                # Check if it's an error state
                error_element = await page.query_selector(error_selector)
                if error_element:
                    error_msg = await error_element.get_attribute('data-tekton-loading-error')
                    result["error"] = f"Component failed to load: {error_msg}"
                    result["navigation_completed"] = False
                    return result
                
                # If we're here, it's loaded successfully
                result["navigation_completed"] = True
                result["message"] = f"Successfully navigated to {component} (loading state: loaded)"
                
                # Get loading time if available
                container = await page.query_selector(f'[data-tekton-loading-component="{component}"]')
                if container:
                    start_time = await container.get_attribute('data-tekton-loading-started')
                    if start_time:
                        current_time = await page.evaluate("Date.now()")
                        load_time = int(current_time) - int(start_time)
                        result["load_time_ms"] = load_time
                
                return result
                
            except Exception as loading_state_error:
                # Fallback to original detection method if loading states aren't available
                result["loading_state_fallback"] = True
                result["loading_state_error"] = str(loading_state_error)
            
            # Original component detection as fallback
            component_selectors = [
                f'[data-tekton-area="{component}"]',
                f'[data-tekton-component="{component}"]', 
                f'[data-component="{component}"]',
                f'.{component}',
                f'#{component}-component'
            ]
            
            component_found = False
            component_element = None
            
            for selector in component_selectors:
                try:
                    component_element = await page.wait_for_selector(selector, timeout=2000)
                    if component_element:
                        component_found = True
                        break
                except:
                    continue
            
            if component_found and component_element:
                # Give it a moment for any dynamic content to load
                await page.wait_for_load_state("networkidle", timeout=5000)
                
                # Verify it's the right component by checking for unique content
                component_verification = await component_element.evaluate(f"""
                    el => {{
                        const text = el.textContent || '';
                        const hasComponentName = text.toLowerCase().includes('{component.lower()}');
                        const hasUniqueClass = el.className.includes('{component}');
                        const hasDataAttribute = el.getAttribute('data-tekton-area') === '{component}' ||
                                               el.getAttribute('data-tekton-component') === '{component}' ||
                                               el.getAttribute('data-component') === '{component}';
                        
                        return {{
                            tag: el.tagName,
                            classes: el.className,
                            hasContent: el.innerHTML.length > 0,
                            isVisible: el.offsetWidth > 0 && el.offsetHeight > 0,
                            verified: hasComponentName || hasUniqueClass || hasDataAttribute,
                            verificationDetails: {{
                                hasComponentName,
                                hasUniqueClass,
                                hasDataAttribute
                            }}
                        }};
                    }}
                """)
                
                if component_verification.get("verified"):
                    result["navigation_completed"] = True
                    result["message"] = f"Successfully navigated to {component}"
                    result["component_info"] = component_verification
                else:
                    result["warning"] = f"Component loaded but verification failed"
                    result["component_info"] = component_verification
            else:
                result["warning"] = f"Navigation completed but {component} component not found in content area"
                result["tried_selectors"] = component_selectors
        else:
            result["message"] = f"Navigation initiated to {component} (not waiting for load)"
    
    except Exception as e:
        result["error"] = str(e)
        result["navigation_completed"] = False
    
    return result