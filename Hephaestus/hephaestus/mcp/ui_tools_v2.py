"""
UI DevTools MCP v2 - Fixed to properly work with Hephaestus UI

IMPORTANT: This version correctly targets the Hephaestus UI at port 8080
and understands that all components are rendered within that single UI.
"""

import asyncio
import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from bs4 import BeautifulSoup, NavigableString, Tag
import lxml.html
from cssselect import GenericTranslator

# Import configuration properly
from shared.utils.global_config import GlobalConfig

# The MAIN UI is always Hephaestus at port 8080
global_config = GlobalConfig.get_instance()
HEPHAESTUS_PORT = global_config.config.hephaestus.port
HEPHAESTUS_URL = f"http://localhost:{HEPHAESTUS_PORT}"

# Component areas within Hephaestus UI
UI_COMPONENTS = {
    "hephaestus": {
        "description": "Main Hephaestus UI container",
        "selectors": ["body", "#app", ".main-container"]
    },
    "rhetor": {
        "description": "Rhetor LLM component area",
        "selectors": ["#rhetor-component", ".rhetor-content", "[data-component='rhetor']"]
    },
    "hermes": {
        "description": "Hermes messaging component area", 
        "selectors": ["#hermes-component", ".hermes-content", "[data-component='hermes']"]
    },
    "athena": {
        "description": "Athena knowledge component area",
        "selectors": ["#athena-component", ".athena-content", "[data-component='athena']"]
    },
    "engram": {
        "description": "Engram memory component area",
        "selectors": ["#engram-component", ".engram-content", "[data-component='engram']"]
    },
    "apollo": {
        "description": "Apollo prediction component area",
        "selectors": ["#apollo-component", ".apollo-content", "[data-component='apollo']"]
    },
    "prometheus": {
        "description": "Prometheus planning component area",
        "selectors": ["#prometheus-component", ".prometheus-content", "[data-component='prometheus']"]
    },
    "ergon": {
        "description": "Ergon agents component area",
        "selectors": ["#ergon-component", ".ergon-content", "[data-component='ergon']"]
    },
    "metis": {
        "description": "Metis workflow component area",
        "selectors": ["#metis-component", ".metis-content", "[data-component='metis']"]
    },
    "navigation": {
        "description": "Main navigation area",
        "selectors": ["#left-nav", ".navigation", "nav", ".sidebar"]
    },
    "content": {
        "description": "Main content area",
        "selectors": ["#center-content", ".content-area", "main", ".main-content"]
    },
    "panel": {
        "description": "Right panel area",
        "selectors": ["#right-panel", ".panel-right", ".sidebar-right"]
    },
    "footer": {
        "description": "Footer area",
        "selectors": ["#footer", ".footer", "footer", ".bottom-bar"]
    }
}

# Dangerous patterns to detect and prevent
DANGEROUS_PATTERNS = {
    "frameworks": [
        r"import\s+React",
        r"import\s+\{.*\}\s+from\s+['\"](react|vue|angular)",
        r"Vue\.(component|createApp)",
        r"angular\.(module|component)",
        r"webpack",
        r"babel",
        r"npm\s+install.*react",
        r"yarn\s+add.*vue",
        r"<script.*src=.*react",
        r"<script.*src=.*vue"
    ],
    "build_tools": [
        r"webpack\.config",
        r"rollup\.config",
        r"vite\.config",
        r"parcel",
        r"esbuild"
    ],
    "complex_patterns": [
        r"class\s+\w+\s+extends\s+(React\.)?Component",
        r"function\s+\w+\s*\(\s*props\s*\)",
        r"const\s+\[\s*\w+\s*,\s*set\w+\s*\]\s*=\s*useState"
    ]
}


class UIToolsError(Exception):
    """Base exception for UI tools"""
    pass


class ComponentNotFoundError(UIToolsError):
    """Raised when a component area cannot be found"""
    pass


class FrameworkDetectedError(UIToolsError):
    """Raised when a framework is detected in changes"""
    pass


class BrowserManager:
    """Manages browser instance for Hephaestus UI"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._initialization_lock = asyncio.Lock()
        self._restart_attempts = 0
        self._max_restart_attempts = 3
    
    async def initialize(self, force_restart: bool = False):
        """Initialize the browser with automatic recovery"""
        async with self._initialization_lock:
            if force_restart:
                await self._cleanup_browser()
            
            if not self.playwright:
                self.playwright = await async_playwright().start()
            
            if not self.browser or not self.browser.is_connected():
                try:
                    self.browser = await self.playwright.chromium.launch(headless=True)
                    self._restart_attempts = 0
                except Exception as e:
                    if self._restart_attempts < self._max_restart_attempts:
                        self._restart_attempts += 1
                        await asyncio.sleep(1)
                        return await self.initialize(force_restart=True)
                    raise UIToolsError(f"Failed to start browser after {self._max_restart_attempts} attempts: {str(e)}")
            
            if not self.context:
                self.context = await self.browser.new_context()
            
            if not self.page or not self.page.is_closed():
                self.page = await self.context.new_page()
                # Always navigate to Hephaestus UI
                await self.page.goto(HEPHAESTUS_URL, wait_until="networkidle", timeout=15000)
    
    async def get_page(self) -> Page:
        """Get the page for Hephaestus UI"""
        await self.initialize()
        
        # Check if page is still valid
        try:
            await self.page.evaluate("() => true")
            # Check we're still on Hephaestus
            if not self.page.url.startswith(HEPHAESTUS_URL):
                await self.page.goto(HEPHAESTUS_URL, wait_until="networkidle", timeout=15000)
        except:
            # Page is dead, reinitialize
            await self.initialize(force_restart=True)
        
        return self.page
    
    async def _cleanup_browser(self):
        """Clean up browser resources"""
        if self.page:
            try:
                await self.page.close()
            except:
                pass
            self.page = None
        
        if self.context:
            try:
                await self.context.close()
            except:
                pass
            self.context = None
        
        if self.browser:
            try:
                await self.browser.close()
            except:
                pass
            self.browser = None
    
    async def cleanup(self):
        """Clean up all browser resources"""
        await self._cleanup_browser()
        
        if self.playwright:
            try:
                await self.playwright.stop()
            except:
                pass
            self.playwright = None


# Global browser manager instance
browser_manager = BrowserManager()


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


def _detect_dangerous_patterns(content: str) -> List[str]:
    """Detect dangerous patterns in content"""
    detected = []
    
    for category, patterns in DANGEROUS_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                detected.append(f"{category}: {pattern}")
    
    return detected


def _extract_element_info(element: Tag) -> Dict[str, Any]:
    """Extract relevant information from a BeautifulSoup element"""
    info = {
        "tag": element.name,
        "id": element.get("id"),
        "classes": element.get("class", []),
        "attributes": {}
    }
    
    # Extract relevant attributes
    for attr in ["href", "src", "alt", "title", "placeholder", "value", "type", "name", "data-component"]:
        if element.get(attr):
            info["attributes"][attr] = element.get(attr)
    
    # Extract text content
    text = element.get_text(strip=True)
    if text and len(text) < 200:
        info["text"] = text
    elif text:
        info["text"] = text[:200] + "..."
    
    return info


def _html_to_structured_data(html: str, selector: Optional[str] = None) -> Dict[str, Any]:
    """Convert HTML to structured data representation"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # If selector provided, find matching elements
    if selector:
        if selector.startswith("#"):
            element = soup.find(id=selector[1:])
            elements = [element] if element else []
        elif selector.startswith("."):
            elements = soup.find_all(class_=selector[1:])
        else:
            try:
                doc = lxml.html.fromstring(html)
                xpath = GenericTranslator().css_to_xpath(selector)
                lxml_elements = doc.xpath(xpath)
                
                elements = []
                for lxml_el in lxml_elements:
                    el_html = lxml.html.tostring(lxml_el, encoding='unicode')
                    el_soup = BeautifulSoup(el_html, 'html.parser')
                    if el_soup.body:
                        elements.extend(el_soup.body.children)
                    else:
                        elements.extend(el_soup.children)
            except:
                elements = soup.find_all(selector)
    else:
        elements = [soup.body if soup.body else soup]
    
    result = {
        "element_count": len(elements),
        "elements": []
    }
    
    for element in elements:
        if isinstance(element, Tag):
            el_info = _extract_element_info(element)
            
            # Add child count
            children = [child for child in element.children if isinstance(child, Tag)]
            if children:
                el_info["child_count"] = len(children)
            
            result["elements"].append(el_info)
    
    return result


async def ui_list_areas() -> Dict[str, Any]:
    """
    List all available UI areas in Hephaestus
    
    Returns:
        Information about available UI areas and how to use them
    """
    return list_ui_areas()


async def ui_capture(
    area: str = "hephaestus",
    selector: Optional[str] = None,
    include_screenshot: bool = False
) -> Dict[str, Any]:
    """
    Capture UI state from Hephaestus UI
    
    Args:
        area: UI area name (e.g., 'rhetor', 'navigation', 'content')
              Use 'hephaestus' for the entire UI
        selector: Optional CSS selector for specific element within the area
        include_screenshot: Whether to include a visual screenshot
    
    Returns:
        Structured data about the UI state
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
        try:
            element = await page.wait_for_selector(selector, timeout=5000)
            html = await element.inner_html()
        except:
            result["error"] = f"Selector '{selector}' not found within {area}"
            return result
    
    # Convert to structured data
    result["structure"] = _html_to_structured_data(html, selector)
    
    # Extract common UI elements
    soup = BeautifulSoup(html, 'html.parser')
    
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
    
    # Include screenshot if requested
    if include_screenshot:
        screenshot = await page.screenshot(full_page=False)
        result["screenshot"] = {
            "type": "base64",
            "data": screenshot.hex()
        }
    
    return result


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
        result["before"] = _html_to_structured_data(before_html)
    
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
            result["after"] = _html_to_structured_data(after_html)
            
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


async def ui_sandbox(
    area: str,
    changes: List[Dict[str, Any]],
    preview: bool = True
) -> Dict[str, Any]:
    """
    Test UI changes in a sandboxed environment
    
    Args:
        area: UI area to modify (use 'hephaestus' for general changes)
        changes: List of changes to apply
        preview: Whether to preview changes without applying
    
    Returns:
        Result of sandbox testing including validation
    """
    await browser_manager.initialize()
    page = await browser_manager.get_page()
    
    result = {
        "area": area,
        "changes": changes,
        "preview": preview,
        "validations": []
    }
    
    # Validate changes for dangerous patterns
    for i, change in enumerate(changes):
        change_content = change.get("content", "")
        detected = _detect_dangerous_patterns(change_content)
        
        if detected:
            result["validations"].append({
                "change_index": i,
                "status": "rejected",
                "reason": "Dangerous patterns detected",
                "patterns": detected
            })
            
            result["applied"] = False
            result["error"] = "Changes rejected due to framework/complexity detection"
            return result
    
    # Create snapshot
    original_html = await page.content()
    result["original_snapshot"] = _html_to_structured_data(original_html)
    
    # Apply changes
    sandbox_results = []
    
    for i, change in enumerate(changes):
        change_type = change.get("type", "html")
        selector = change.get("selector")
        content = change.get("content", "")
        action = change.get("action", "replace")
        
        try:
            if change_type == "html":
                js_code = f"""
                (function() {{
                    const elements = document.querySelectorAll('{selector}');
                    if (elements.length === 0) return {{ success: false, error: 'No elements found' }};
                    
                    elements.forEach(el => {{
                        const content = `{content.replace('`', '\\`')}`;
                        
                        switch('{action}') {{
                            case 'replace':
                                el.innerHTML = content;
                                break;
                            case 'append':
                                el.innerHTML += content;
                                break;
                            case 'prepend':
                                el.innerHTML = content + el.innerHTML;
                                break;
                            case 'after':
                                el.insertAdjacentHTML('afterend', content);
                                break;
                            case 'before':
                                el.insertAdjacentHTML('beforebegin', content);
                                break;
                        }}
                    }});
                    
                    return {{ success: true, count: elements.length }};
                }})();
                """
                
                result_js = await page.evaluate(js_code)
                sandbox_results.append({
                    "change_index": i,
                    "success": result_js.get("success", False),
                    "elements_modified": result_js.get("count", 0),
                    "error": result_js.get("error")
                })
            
            elif change_type == "css":
                css_content = f"<style>{content}</style>"
                await page.add_style_tag(content=content)
                sandbox_results.append({
                    "change_index": i,
                    "success": True,
                    "type": "css_injected"
                })
            
            elif change_type == "js":
                if _detect_dangerous_patterns(content):
                    sandbox_results.append({
                        "change_index": i,
                        "success": False,
                        "error": "JavaScript contains framework/build tool references"
                    })
                else:
                    await page.evaluate(content)
                    sandbox_results.append({
                        "change_index": i,
                        "success": True,
                        "type": "js_executed"
                    })
        
        except Exception as e:
            sandbox_results.append({
                "change_index": i,
                "success": False,
                "error": str(e)
            })
    
    result["sandbox_results"] = sandbox_results
    
    # Capture final state
    final_html = await page.content()
    result["final_snapshot"] = _html_to_structured_data(final_html)
    
    # If preview mode, restore
    if preview:
        await page.set_content(original_html)
        result["restored"] = True
    else:
        result["applied"] = True
    
    # Summary
    successful = sum(1 for r in sandbox_results if r.get("success", False))
    result["summary"] = {
        "total_changes": len(changes),
        "successful": successful,
        "failed": len(changes) - successful
    }
    
    return result


async def ui_analyze(
    area: str = "hephaestus",
    deep_scan: bool = False
) -> Dict[str, Any]:
    """
    Analyze UI structure and patterns
    
    Args:
        area: UI area to analyze
        deep_scan: Whether to perform deep analysis
    
    Returns:
        Analysis of UI structure, patterns, and recommendations
    """
    await browser_manager.initialize()
    page = await browser_manager.get_page()
    
    result = {
        "area": area,
        "ui_url": HEPHAESTUS_URL,
        "analysis": {}
    }
    
    # Get HTML for the area
    if area == "hephaestus":
        html = await page.content()
    else:
        try:
            element = await find_component_element(page, area)
            html = await element.inner_html()
        except ComponentNotFoundError as e:
            result["error"] = str(e)
            return result
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Analyze structure
    structure_analysis = {
        "total_elements": len(soup.find_all()),
        "forms": len(soup.find_all("form")),
        "inputs": len(soup.find_all(["input", "textarea", "select"])),
        "buttons": len(soup.find_all(["button", "input[type='button']", "input[type='submit']"])),
        "links": len(soup.find_all("a")),
        "images": len(soup.find_all("img")),
        "tables": len(soup.find_all("table")),
        "divs": len(soup.find_all("div")),
        "sections": len(soup.find_all(["section", "article", "aside", "nav", "header", "footer"]))
    }
    result["analysis"]["structure"] = structure_analysis
    
    # Detect frameworks and libraries
    framework_detection = {
        "react": False,
        "vue": False,
        "angular": False,
        "jquery": False,
        "bootstrap": False,
        "tailwind": False
    }
    
    # Check for framework indicators
    scripts = soup.find_all("script")
    for script in scripts:
        src = script.get("src", "")
        text = script.string or ""
        
        if "react" in src.lower() or "React" in text:
            framework_detection["react"] = True
        if "vue" in src.lower() or "Vue" in text:
            framework_detection["vue"] = True
        if "angular" in src.lower() or "angular" in text:
            framework_detection["angular"] = True
        if "jquery" in src.lower() or "$(" in text or "jQuery" in text:
            framework_detection["jquery"] = True
    
    result["analysis"]["frameworks"] = framework_detection
    
    # Component-specific insights
    if area != "hephaestus":
        component_info = {
            "area_name": area,
            "description": UI_COMPONENTS[area]["description"],
            "suggested_selectors": UI_COMPONENTS[area]["selectors"],
            "found": True
        }
        result["analysis"]["component_info"] = component_info
    
    # Complexity assessment
    complexity_score = 0
    complexity_factors = []
    
    if any(framework_detection.values()):
        complexity_score += 10
        complexity_factors.append("Frameworks detected")
    
    if structure_analysis["total_elements"] > 1000:
        complexity_score += 2
        complexity_factors.append(f"Large DOM ({structure_analysis['total_elements']} elements)")
    
    result["analysis"]["complexity"] = {
        "score": complexity_score,
        "level": "high" if complexity_score >= 10 else "medium" if complexity_score >= 5 else "low",
        "factors": complexity_factors
    }
    
    # Recommendations
    recommendations = []
    
    if any(framework_detection.values()):
        recommendations.append({
            "type": "warning",
            "message": "Frameworks detected. Avoid adding more complexity.",
            "frameworks": [k for k, v in framework_detection.items() if v]
        })
    
    recommendations.append({
        "type": "info",
        "message": f"Working in '{area}' area. Use selectors like: {', '.join(UI_COMPONENTS.get(area, {}).get('selectors', [])[:2])}"
    })
    
    result["recommendations"] = recommendations
    
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

# 2. Capture an area to explore it
rhetor = await ui_capture('rhetor')

# 3. Make a simple change (preview first!)
await ui_sandbox('rhetor', [{
    'type': 'html',
    'selector': '#rhetor-footer',
    'content': '<div>Hello from DevTools!</div>',
    'action': 'append'
}], preview=True)

# 4. Apply if it looks good
await ui_sandbox('rhetor', [...], preview=False)
""",
        "available_tools": {
            "ui_list_areas()": "Discover all UI areas in Hephaestus",
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
    "ui_capture",
    "ui_interact", 
    "ui_sandbox",
    "ui_analyze",
    "ui_help",
    "browser_manager"
]