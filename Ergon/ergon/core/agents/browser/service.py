import os
import asyncio
import logging
from typing import Optional, Dict, Any, List
import time
import json
from datetime import datetime
from pathlib import Path

# Import browser-use correctly based on OpenManus implementation
try:
    from browser_use import Browser as BrowserUseBrowser
    from browser_use import BrowserConfig
    from browser_use.browser.context import BrowserContext
    from browser_use.dom.service import DomService
    BROWSER_USE_AVAILABLE = True
except ImportError:
    BROWSER_USE_AVAILABLE = False
    
logger = logging.getLogger(__name__)

class BrowserService:
    """
    Service for managing browser interactions
    """
    def __init__(self, config_path: Optional[str] = None, headless: bool = True):
        """
        Initialize the browser service
        
        Args:
            config_path: Path to config directory
            headless: Whether to run browser in headless mode
        """
        self.config_path = config_path
        self.headless = headless
        self.browser = None
        self.context = None
        self.dom_service = None
        self._check_dependencies()
        
        # Screenshot directory
        if config_path:
            screenshot_dir = os.path.join(config_path, "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            self.screenshot_dir = screenshot_dir
        else:
            self.screenshot_dir = os.path.expanduser("~/ergon_screenshots")
            os.makedirs(self.screenshot_dir, exist_ok=True)
    
    def _check_dependencies(self):
        """Check if required dependencies are available"""
        if not BROWSER_USE_AVAILABLE:
            logger.warning("browser-use package not found. Install with: pip install browser-use")
            
    async def initialize(self) -> Any:
        """Initialize the browser and context"""
        if not BROWSER_USE_AVAILABLE:
            raise ImportError("browser-use package is required but not installed")
            
        if self.browser is None:
            try:
                browser_config = BrowserConfig(headless=self.headless)
                self.browser = BrowserUseBrowser(browser_config)
                logger.info("Browser initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize browser: {str(e)}")
                raise
                
        if self.context is None:
            try:
                self.context = await self.browser.new_context()
                self.dom_service = DomService(await self.context.get_current_page())
                logger.info("Browser context initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize browser context: {str(e)}")
                raise
                
        return self.context
    
    async def close(self):
        """Close the browser"""
        if self.context:
            try:
                await self.context.close()
                self.context = None
                self.dom_service = None
                logger.info("Browser context closed successfully")
            except Exception as e:
                logger.error(f"Failed to close browser context: {str(e)}")
        
        if self.browser:
            try:
                await self.browser.close()
                self.browser = None
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.error(f"Failed to close browser: {str(e)}")
    
    async def navigate(self, url: str) -> str:
        """Navigate to a URL"""
        context = await self.initialize()
        try:
            await context.navigate_to(url)
            return f"Successfully navigated to {url}"
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {str(e)}")
            return f"Error navigating to {url}: {str(e)}"
    
    async def get_text(self) -> str:
        """Get text content from the current page"""
        context = await self.initialize()
        try:
            text = await context.execute_javascript("document.body.innerText")
            return text
        except Exception as e:
            logger.error(f"Failed to get text: {str(e)}")
            return f"Error getting text: {str(e)}"
    
    async def get_html(self) -> str:
        """Get HTML content from the current page"""
        context = await self.initialize()
        try:
            html = await context.get_page_html()
            return html
        except Exception as e:
            logger.error(f"Failed to get HTML: {str(e)}")
            return f"Error getting HTML: {str(e)}"
    
    async def click(self, selector: str) -> str:
        """Click an element using CSS selector"""
        context = await self.initialize()
        try:
            # Get the current page
            page = await context.get_current_page()
            
            # Use Playwright to click the element
            await page.click(selector)
            return f"Successfully clicked element with selector: {selector}"
        except Exception as e:
            logger.error(f"Failed to click element {selector}: {str(e)}")
            return f"Error clicking element {selector}: {str(e)}"
    
    async def type(self, selector: str, text: str) -> str:
        """Type text into an element using CSS selector"""
        context = await self.initialize()
        try:
            # Get the current page
            page = await context.get_current_page()
            
            # Use Playwright to fill the text
            await page.fill(selector, text)
            return f"Successfully typed text into element with selector: {selector}"
        except Exception as e:
            logger.error(f"Failed to type text into element {selector}: {str(e)}")
            return f"Error typing text into element {selector}: {str(e)}"
    
    async def screenshot(self, path: Optional[str] = None) -> str:
        """Take a screenshot of the current page"""
        context = await self.initialize()
        try:
            if not path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                path = os.path.join(self.screenshot_dir, f"screenshot_{timestamp}.png")
                
            # Ensure directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Get the page from the context
            page = await context.get_current_page()
                
            # Take screenshot using Playwright directly
            await page.screenshot(path=path, full_page=True)
            return f"Screenshot saved to {path}"
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
            return f"Error taking screenshot: {str(e)}"
    
    async def scroll(self, direction: str, selector: Optional[str] = None, amount: int = 300) -> str:
        """Scroll the page"""
        context = await self.initialize()
        try:
            if direction == "to_element" and selector:
                # Find the element first
                elements = await self.dom_service.get_elements_by_css_selector(selector)
                if not elements or len(elements) == 0:
                    return f"No elements found with selector: {selector}"
                
                # Scroll to the element
                await context.execute_javascript(f"""
                    const element = document.querySelector("{selector}");
                    if (element) {{
                        element.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                    }}
                """)
                return f"Successfully scrolled to element with selector: {selector}"
            elif direction == "up":
                # Scroll up
                await context.execute_javascript(f"window.scrollBy(0, -{amount});")
                return f"Successfully scrolled up by {amount} pixels"
            elif direction == "down":
                # Scroll down
                await context.execute_javascript(f"window.scrollBy(0, {amount});")
                return f"Successfully scrolled down by {amount} pixels"
            else:
                return f"Invalid scroll direction: {direction}"
        except Exception as e:
            logger.error(f"Failed to scroll: {str(e)}")
            return f"Error scrolling: {str(e)}"
    
    async def wait(self, milliseconds: int) -> str:
        """Wait for specified time"""
        try:
            await asyncio.sleep(milliseconds / 1000)
            return f"Successfully waited for {milliseconds} milliseconds"
        except Exception as e:
            logger.error(f"Failed to wait: {str(e)}")
            return f"Error waiting: {str(e)}"
    
    async def get_element(self, selector: str) -> str:
        """Get information about an element"""
        context = await self.initialize()
        try:
            # Try to find the element
            elements = await self.dom_service.get_elements_by_css_selector(selector)
            if not elements or len(elements) == 0:
                return f"No elements found with selector: {selector}"
            
            # Get element info using JavaScript
            info = await context.execute_javascript(f"""
                const element = document.querySelector("{selector}");
                if (element) {{
                    return {{
                        tag: element.tagName,
                        text: element.innerText || element.textContent,
                        attributes: Object.entries(element.attributes)
                            .map(([_, attr]) => `${{attr.name}}="${{attr.value}}"`)
                            .join(', ')
                    }};
                }}
                return null;
            """)
            
            if info:
                return f"Element found with selector {selector}: {json.dumps(info)}"
            else:
                return f"Element found but could not get details for selector: {selector}"
        except Exception as e:
            logger.error(f"Failed to get element {selector}: {str(e)}")
            return f"Error getting element {selector}: {str(e)}"