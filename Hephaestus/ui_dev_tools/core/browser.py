"""Browser management abstraction for UI DevTools"""
import asyncio
import logging
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page, Playwright
from pathlib import Path

logger = logging.getLogger(__name__)


class BrowserManager:
    """Singleton browser manager for all tools"""
    _instance = None
    _browser: Optional[Browser] = None
    _page: Optional[Page] = None
    _playwright: Optional[Playwright] = None
    _base_url: str = "http://localhost:8080"  # Default Hephaestus URL
    
    def __new__(cls):
        """Ensure singleton instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize browser manager"""
        # Only initialize once
        if not hasattr(self, '_initialized'):
            self._initialized = True
            logger.info("BrowserManager initialized")
    
    async def get_page(self) -> Page:
        """Get or create browser page"""
        if self._page is None:
            await self._ensure_browser()
            self._page = await self._browser.new_page()
            logger.info("Created new browser page")
        return self._page
    
    async def _ensure_browser(self) -> None:
        """Ensure browser is started"""
        if self._browser is None:
            if self._playwright is None:
                self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            logger.info("Started browser")
    
    async def navigate_to_component(self, component_name: str) -> bool:
        """Navigate to a specific component"""
        try:
            page = await self.get_page()
            
            # First navigate to base URL if not already there
            current_url = page.url
            if not current_url.startswith(self._base_url):
                logger.info(f"Navigating to base URL: {self._base_url}")
                response = await page.goto(self._base_url, wait_until='domcontentloaded')
                if not response or not response.ok:
                    logger.error(f"Failed to navigate to base URL")
                    return False
                await page.wait_for_timeout(2000)  # Wait for app to initialize
            
            # Now try to load the component using JavaScript
            logger.info(f"Loading component: {component_name}")
            
            # Try multiple methods to load component
            load_script = f"""
            async () => {{
                // Method 1: Try using window.loadComponent if available
                if (window.loadComponent && typeof window.loadComponent === 'function') {{
                    await window.loadComponent('{component_name}');
                    return true;
                }}
                
                // Method 2: Try using window.MinimalLoader if available
                if (window.MinimalLoader && window.MinimalLoader.loadComponent) {{
                    await window.MinimalLoader.loadComponent('{component_name}');
                    return true;
                }}
                
                // Method 3: Try clicking on navigation link
                const navLink = document.querySelector(`[data-component="{component_name}"]`);
                if (navLink) {{
                    navLink.click();
                    return true;
                }}
                
                // Method 4: Try changing hash
                window.location.hash = `/component/{component_name}`;
                return false;
            }}
            """
            
            loaded = await page.evaluate(load_script)
            
            # Wait for component to potentially load
            await page.wait_for_timeout(2000)
            
            # Verify component loaded
            check_script = f"""
            () => {{
                const component = document.querySelector('[data-tekton-component="{component_name}"]');
                return component !== null;
            }}
            """
            
            component_exists = await page.evaluate(check_script)
            
            if component_exists:
                logger.info(f"Successfully loaded component {component_name}")
                return True
            else:
                logger.warning(f"Component {component_name} not found in DOM after loading attempt")
                return False
                
        except Exception as e:
            logger.error(f"Error navigating to component {component_name}: {e}")
            return False
    
    async def get_current_url(self) -> str:
        """Get current page URL"""
        page = await self.get_page()
        return page.url
    
    async def wait_for_selector(self, selector: str, timeout: int = 5000) -> bool:
        """Wait for a selector to appear"""
        try:
            page = await self.get_page()
            await page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception:
            return False
    
    async def evaluate_script(self, script: str) -> Any:
        """Evaluate JavaScript in the page"""
        page = await self.get_page()
        return await page.evaluate(script)
    
    async def get_dom_content(self) -> str:
        """Get the current DOM content"""
        page = await self.get_page()
        return await page.content()
    
    async def find_elements_with_semantic_tags(self) -> Dict[str, Any]:
        """Find all elements with data-tekton-* attributes in the DOM"""
        page = await self.get_page()
        
        # JavaScript to find all semantic tags - NO LAMBDAS!
        script = """
        () => {
            const elements = document.querySelectorAll('*');
            const results = [];
            
            for (let i = 0; i < elements.length; i++) {
                const element = elements[i];
                const semanticAttrs = {};
                let hasSemanticTag = false;
                
                // Check each attribute
                for (let j = 0; j < element.attributes.length; j++) {
                    const attr = element.attributes[j];
                    if (attr.name.startsWith('data-tekton-')) {
                        hasSemanticTag = true;
                        const tagName = attr.name.substring(12); // Remove 'data-tekton-'
                        semanticAttrs[tagName] = attr.value;
                    }
                }
                
                if (hasSemanticTag) {
                    results.push({
                        tagName: element.tagName.toLowerCase(),
                        attributes: semanticAttrs,
                        id: element.id || null,
                        className: element.className || null,
                        textContent: element.textContent ? element.textContent.substring(0, 50) : null
                    });
                }
            }
            
            return results;
        }
        """
        
        try:
            results = await page.evaluate(script)
            logger.info(f"Found {len(results)} elements with semantic tags in DOM")
            return results
        except Exception as e:
            logger.error(f"Error finding semantic tags in DOM: {e}")
            return []
    
    async def take_screenshot(self, path: Optional[str] = None) -> bytes:
        """Take a screenshot of the current page"""
        page = await self.get_page()
        if path:
            await page.screenshot(path=path)
            with open(path, 'rb') as f:
                return f.read()
        else:
            return await page.screenshot()
    
    async def cleanup(self) -> None:
        """Clean up browser resources"""
        try:
            if self._page:
                await self._page.close()
                self._page = None
            if self._browser:
                await self._browser.close()
                self._browser = None
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
            logger.info("Browser cleanup completed")
        except Exception as e:
            logger.error(f"Error during browser cleanup: {e}")
    
    def set_base_url(self, url: str) -> None:
        """Set the base URL for navigation"""
        self._base_url = url.rstrip('/')
        logger.info(f"Base URL set to: {self._base_url}")