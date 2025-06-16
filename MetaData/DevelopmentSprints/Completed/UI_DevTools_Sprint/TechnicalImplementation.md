# Technical Implementation Guide - UI DevTools

## Overview

Detailed implementation guide for the four MCP tools in Hephaestus that will enable Claude to work effectively with UI.

## Prerequisites

```bash
# In Hephaestus requirements.txt
playwright>=1.40.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
cssselect>=1.2.0
```

## Tool 1: ui_capture

### Purpose
Get UI state without screenshots eating context.

### Implementation

```python
# hephaestus/mcp/ui_tools.py

from playwright.async_api import async_playwright, Page
from bs4 import BeautifulSoup
import base64
import json

class UIDevTools:
    def __init__(self):
        self.browser = None
        self.contexts = {}  # component -> browser context
        self.pages = {}     # component -> page
        
    async def _ensure_browser(self):
        """Ensure browser is running."""
        if not self.browser:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=True)
    
    async def _get_page(self, component: str) -> Page:
        """Get or create page for component."""
        await self._ensure_browser()
        
        if component not in self.pages:
            context = await self.browser.new_context()
            page = await context.new_page()
            
            # Navigate to component
            port = GLOBAL_CONFIG.ports.get(component)
            if not port:
                raise ValueError(f"Unknown component: {component}")
                
            await page.goto(f"http://localhost:{port}")
            
            self.contexts[component] = context
            self.pages[component] = page
            
        return self.pages[component]
    
    @tool()
    async def ui_capture(self, component: str, selector: str = "body", 
                        format: str = "structured") -> dict:
        """Capture UI state efficiently."""
        page = await self._get_page(component)
        
        # Get element
        element = await page.query_selector(selector)
        if not element:
            return {"error": f"Selector '{selector}' not found"}
        
        # Get HTML
        html = await element.inner_html()
        
        # Parse with BeautifulSoup for structure
        soup = BeautifulSoup(html, 'lxml')
        
        # Extract structure
        structure = {
            "html": html if len(html) < 5000 else html[:5000] + "...",
            "text": soup.get_text(strip=True)[:1000],
            "elements": []
        }
        
        # Find interactive elements
        for tag in ['button', 'input', 'select', 'a', 'textarea']:
            elements = soup.find_all(tag)
            for elem in elements:
                structure["elements"].append({
                    "tag": tag,
                    "id": elem.get('id'),
                    "class": elem.get('class'),
                    "text": elem.get_text(strip=True)[:50],
                    "attrs": {k: v for k, v in elem.attrs.items() 
                             if k in ['href', 'type', 'name', 'value']}
                })
        
        # Get computed styles if requested
        if format in ["structured", "both"]:
            styles = await page.evaluate('''(selector) => {
                const elem = document.querySelector(selector);
                const computed = window.getComputedStyle(elem);
                return {
                    display: computed.display,
                    position: computed.position,
                    width: computed.width,
                    height: computed.height,
                    color: computed.color,
                    backgroundColor: computed.backgroundColor,
                    font: computed.font
                };
            }''', selector)
            structure["styles"] = styles
        
        # Screenshot only if requested
        if format in ["visual", "both"]:
            screenshot = await element.screenshot()
            structure["screenshot"] = base64.b64encode(screenshot).decode()
            
        return structure
```

## Tool 2: ui_interact

### Purpose
Interact with UI and see what happens.

### Implementation

```python
    @tool()
    async def ui_interact(self, component: str, action: str, 
                         target: str, value: str = None) -> dict:
        """Interact with UI elements and capture results."""
        page = await self._get_page(component)
        
        # Capture before state
        before = await self.ui_capture(component, "body", "structured")
        
        # Store current console messages
        console_messages = []
        page.on("console", lambda msg: console_messages.append({
            "type": msg.type,
            "text": msg.text
        }))
        
        # Store network requests
        network_requests = []
        page.on("request", lambda req: network_requests.append({
            "url": req.url,
            "method": req.method
        }))
        
        try:
            element = await page.query_selector(target)
            if not element:
                return {"error": f"Element '{target}' not found"}
            
            # Perform action
            if action == "click":
                await element.click()
            elif action == "type":
                await element.fill(value or "")
            elif action == "select":
                await element.select_option(value)
            elif action == "hover":
                await element.hover()
            else:
                return {"error": f"Unknown action: {action}"}
                
            # Wait for any updates
            await page.wait_for_timeout(500)
            
            # Capture after state
            after = await self.ui_capture(component, "body", "structured")
            
            # Compute changes
            changes = self._compute_changes(before, after)
            
            return {
                "success": True,
                "action": {"type": action, "target": target, "value": value},
                "changes": changes,
                "console": console_messages,
                "network": network_requests,
                "elements_changed": len(changes)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": {"type": action, "target": target, "value": value}
            }
    
    def _compute_changes(self, before: dict, after: dict) -> list:
        """Compute what changed between states."""
        changes = []
        
        # Compare HTML structure
        before_soup = BeautifulSoup(before["html"], 'lxml')
        after_soup = BeautifulSoup(after["html"], 'lxml')
        
        # Find added/removed elements
        before_ids = {elem.get('id') for elem in before_soup.find_all(id=True)}
        after_ids = {elem.get('id') for elem in after_soup.find_all(id=True)}
        
        added = after_ids - before_ids
        removed = before_ids - after_ids
        
        for id in added:
            changes.append({"type": "added", "id": id})
        for id in removed:
            changes.append({"type": "removed", "id": id})
            
        # Check text changes
        if before["text"] != after["text"]:
            changes.append({
                "type": "text_changed",
                "before": before["text"][:100],
                "after": after["text"][:100]
            })
            
        return changes
```

## Tool 3: ui_sandbox

### Purpose
Test changes without committing them.

### Implementation

```python
    @tool()
    async def ui_sandbox(self, component: str, html_changes: str = None,
                        css_changes: str = None, js_changes: str = None) -> dict:
        """Test changes in isolated environment."""
        # Create a new context for sandboxing
        await self._ensure_browser()
        sandbox_context = await self.browser.new_context()
        sandbox_page = await sandbox_context.new_page()
        
        try:
            # Navigate to component
            port = GLOBAL_CONFIG.ports.get(component)
            await sandbox_page.goto(f"http://localhost:{port}")
            
            # Apply changes
            if html_changes:
                # Detect if it's a full page or fragment
                if html_changes.strip().startswith('<!DOCTYPE') or html_changes.strip().startswith('<html'):
                    # Full page replacement - DANGER!
                    return {
                        "error": "Full page replacement detected",
                        "safe_to_apply": False,
                        "warning": "Attempting to replace entire page. Use targeted selectors instead."
                    }
                    
                # Check for framework signatures
                if any(framework in html_changes for framework in 
                       ['<script src="react"', '<script src="vue"', 'ng-app=', 'webpack']):
                    return {
                        "error": "Framework detected",
                        "safe_to_apply": False,
                        "warning": "New framework detected. Simple HTML only!",
                        "frameworks_found": self._detect_frameworks(html_changes)
                    }
            
            if css_changes:
                await sandbox_page.add_style_tag(content=css_changes)
                
            if js_changes:
                # Check for dangerous patterns
                if any(pattern in js_changes for pattern in 
                       ['npm', 'require(', 'import ', 'webpack']):
                    return {
                        "error": "Complex JavaScript detected",
                        "safe_to_apply": False,
                        "warning": "Build system or modules detected. Keep it simple!"
                    }
                await sandbox_page.add_script_tag(content=js_changes)
            
            # Take screenshot of result
            screenshot = await sandbox_page.screenshot(full_page=False)
            
            # Analyze complexity
            analysis = await self._analyze_complexity(sandbox_page)
            
            return {
                "safe_to_apply": analysis["complexity"] == "simple",
                "preview": base64.b64encode(screenshot).decode()[:1000] + "...",
                "analysis": analysis,
                "changes_summary": {
                    "html": bool(html_changes),
                    "css": bool(css_changes),
                    "js": bool(js_changes)
                }
            }
            
        finally:
            await sandbox_context.close()
    
    def _detect_frameworks(self, html: str) -> list:
        """Detect frontend frameworks."""
        frameworks = []
        patterns = {
            "React": ["react", "jsx", "React."],
            "Vue": ["vue", "v-model", "v-if"],
            "Angular": ["ng-", "angular"],
            "Svelte": ["svelte"],
            "jQuery": ["jquery", "$("]
        }
        
        for framework, indicators in patterns.items():
            if any(ind in html.lower() for ind in indicators):
                frameworks.append(framework)
                
        return frameworks
```

## Tool 4: ui_analyze

### Purpose
Understand UI structure without guessing.

### Implementation

```python
    @tool()
    async def ui_analyze(self, component: str) -> dict:
        """Analyze UI structure and patterns."""
        page = await self._get_page(component)
        
        # Get full page HTML
        html = await page.content()
        soup = BeautifulSoup(html, 'lxml')
        
        analysis = {
            "structure": {},
            "patterns": [],
            "api_calls": [],
            "complexity": "simple",
            "recommendations": []
        }
        
        # Analyze structure
        analysis["structure"] = {
            "forms": len(soup.find_all('form')),
            "inputs": len(soup.find_all('input')),
            "buttons": len(soup.find_all('button')),
            "tables": len(soup.find_all('table')),
            "divs": len(soup.find_all('div')),
            "scripts": len(soup.find_all('script')),
            "styles": len(soup.find_all('style'))
        }
        
        # Detect patterns
        scripts = soup.find_all('script')
        for script in scripts:
            content = script.string or ""
            
            # Find API calls
            if 'fetch(' in content:
                # Extract fetch URLs
                import re
                urls = re.findall(r'fetch\([\'"]([^\'"]+)[\'"]', content)
                analysis["api_calls"].extend(urls)
                
            # Check for frameworks
            if any(fw in content for fw in ['React', 'Vue', 'Angular']):
                analysis["complexity"] = "complex"
                analysis["patterns"].append("framework_detected")
                
        # Detect Tekton patterns
        if all(script.get('src', '').startswith('/') or not script.get('src') 
               for script in scripts):
            analysis["patterns"].append("no_external_dependencies")
            
        if analysis["structure"]["scripts"] < 3:
            analysis["patterns"].append("minimal_javascript")
            
        # Recommendations
        if analysis["complexity"] == "simple":
            analysis["recommendations"].append("Safe to modify with simple HTML/CSS")
        else:
            analysis["recommendations"].append("Complex structure detected - be careful!")
            
        if not analysis["api_calls"]:
            analysis["recommendations"].append("No API calls found - may need to add fetch()")
            
        return analysis
    
    async def _analyze_complexity(self, page: Page) -> dict:
        """Analyze page complexity."""
        metrics = await page.evaluate('''() => {
            return {
                scripts: document.querySelectorAll('script').length,
                external_scripts: document.querySelectorAll('script[src^="http"]').length,
                stylesheets: document.querySelectorAll('link[rel="stylesheet"]').length,
                dom_depth: (() => {
                    let depth = 0, current = document.body;
                    while (current.children.length > 0) {
                        depth++;
                        current = current.children[0];
                    }
                    return depth;
                })(),
                total_elements: document.querySelectorAll('*').length
            };
        }''')
        
        # Determine complexity
        if (metrics["external_scripts"] > 0 or 
            metrics["scripts"] > 5 or 
            metrics["total_elements"] > 1000):
            complexity = "complex"
        elif metrics["total_elements"] > 500:
            complexity = "moderate"
        else:
            complexity = "simple"
            
        return {
            "complexity": complexity,
            "metrics": metrics
        }
```

## Integration with Hephaestus MCP

```python
# hephaestus/mcp/__init__.py
from .ui_tools import UIDevTools

# Register tools
ui_tools = UIDevTools()

# In MCP server setup
server.register_tool(ui_tools.ui_capture)
server.register_tool(ui_tools.ui_interact)
server.register_tool(ui_tools.ui_sandbox)
server.register_tool(ui_tools.ui_analyze)
```

## Usage Examples

```python
# Claude can now do:

# 1. See without screenshots
result = await ui_capture("rhetor", "footer")
print(f"Footer has {len(result['elements'])} interactive elements")

# 2. Click and verify
result = await ui_interact("rhetor", "click", "#submit-btn")
print(f"Click resulted in {len(result['changes'])} changes")

# 3. Preview safely
result = await ui_sandbox("rhetor", html_changes="<div>New widget</div>")
if result["safe_to_apply"]:
    print("Changes are safe!")
else:
    print(f"Warning: {result['warning']}")

# 4. Understand structure
result = await ui_analyze("rhetor")
print(f"Complexity: {result['complexity']}")
print(f"API endpoints: {result['api_calls']}")
```

This implementation gives Claude exactly what's needed to work with UI effectively!