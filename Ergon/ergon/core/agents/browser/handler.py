import json
import asyncio
import logging
from typing import Dict, Any, Optional

from ergon.core.agents.browser.service import BrowserService
from ergon.core.agents.browser.registry import BrowserToolRegistry
from ergon.utils.config.settings import settings

logger = logging.getLogger(__name__)

class BrowserToolHandler:
    """Handler for executing browser tools"""
    
    def __init__(self):
        """Initialize the browser tool handler"""
        # Get headless mode from settings (default to True)
        headless = getattr(settings, "browser_headless", True)
        if isinstance(headless, str):
            headless = headless.lower() == "true"
            
        self.browser_service = BrowserService(
            config_path=getattr(settings, "config_path", None),
            headless=headless
        )
        self.tool_registry = BrowserToolRegistry(self.browser_service)
        
    async def execute_tool(self, tool_name: str, tool_params: Dict[str, Any]) -> str:
        """
        Execute a browser tool
        
        Args:
            tool_name: Name of the tool to execute
            tool_params: Parameters for the tool
            
        Returns:
            Tool execution result
        """
        try:
            if not tool_name.startswith("browse_"):
                logger.warning(f"Not a browser tool: {tool_name}")
                return f"Error: Not a browser tool: {tool_name}"
                
            # Execute the tool
            result = await self.tool_registry.execute_tool(tool_name, tool_params)
            return result
        except Exception as e:
            logger.error(f"Error executing browser tool {tool_name}: {str(e)}")
            return f"Error executing browser tool {tool_name}: {str(e)}"
            
    async def cleanup(self):
        """Clean up resources (close browser)"""
        try:
            await self.browser_service.close()
        except Exception as e:
            logger.error(f"Error cleaning up browser resources: {str(e)}")
            
    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.cleanup())
            else:
                loop.run_until_complete(self.cleanup())
        except Exception:
            pass