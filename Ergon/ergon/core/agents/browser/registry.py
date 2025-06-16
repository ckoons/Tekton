import asyncio
import json
import logging
from typing import Dict, Any, Callable, Optional

from ergon.core.agents.browser.service import BrowserService

logger = logging.getLogger(__name__)

class BrowserToolRegistry:
    """Registry for browser tools"""
    
    def __init__(self, service: BrowserService):
        self.service = service
        self.tools: Dict[str, Callable] = {}
        self._register_tools()
        
    def _register_tools(self):
        """Register all browser tools"""
        self.tools["browse_navigate"] = self._navigate
        self.tools["browse_get_text"] = self._get_text
        self.tools["browse_get_html"] = self._get_html
        self.tools["browse_click"] = self._click
        self.tools["browse_type"] = self._type
        self.tools["browse_screenshot"] = self._screenshot
        self.tools["browse_scroll"] = self._scroll
        self.tools["browse_wait"] = self._wait
        self.tools["browse_get_element"] = self._get_element
        
    async def _navigate(self, params: Dict[str, Any]) -> str:
        """Navigate to a URL"""
        url = params.get("url", "")
        if not url:
            return "Error: URL is required"
        return await self.service.navigate(url)
        
    async def _get_text(self, params: Dict[str, Any]) -> str:
        """Get text content from the current page"""
        return await self.service.get_text()
        
    async def _get_html(self, params: Dict[str, Any]) -> str:
        """Get HTML content from the current page"""
        return await self.service.get_html()
        
    async def _click(self, params: Dict[str, Any]) -> str:
        """Click an element using CSS selector"""
        selector = params.get("selector", "")
        if not selector:
            return "Error: Selector is required"
        return await self.service.click(selector)
        
    async def _type(self, params: Dict[str, Any]) -> str:
        """Type text into an element using CSS selector"""
        selector = params.get("selector", "")
        text = params.get("text", "")
        if not selector:
            return "Error: Selector is required"
        if not text:
            return "Error: Text is required"
        return await self.service.type(selector, text)
        
    async def _screenshot(self, params: Dict[str, Any]) -> str:
        """Take a screenshot of the current page"""
        path = params.get("path", None)
        return await self.service.screenshot(path)
        
    async def _scroll(self, params: Dict[str, Any]) -> str:
        """Scroll the page"""
        direction = params.get("direction", "")
        selector = params.get("selector", None)
        amount = params.get("amount", 300)
        if not direction:
            return "Error: Direction is required (up, down, or to_element)"
        return await self.service.scroll(direction, selector, amount)
        
    async def _wait(self, params: Dict[str, Any]) -> str:
        """Wait for specified time"""
        milliseconds = params.get("milliseconds", 500)
        return await self.service.wait(milliseconds)
        
    async def _get_element(self, params: Dict[str, Any]) -> str:
        """Get information about an element"""
        selector = params.get("selector", "")
        if not selector:
            return "Error: Selector is required"
        return await self.service.get_element(selector)
        
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> str:
        """Execute a tool by name with parameters"""
        if tool_name not in self.tools:
            return f"Error: Unknown tool '{tool_name}'"
        
        try:
            result = await self.tools[tool_name](params)
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return f"Error executing tool {tool_name}: {str(e)}"