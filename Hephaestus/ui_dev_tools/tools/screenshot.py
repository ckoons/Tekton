"""Screenshot Tool - Capture browser screenshots"""
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from ..core.browser import BrowserManager
from ..core.models import ToolResult, ToolStatus

logger = logging.getLogger(__name__)


class Screenshot:
    """Capture screenshots using the shared browser instance"""
    
    def __init__(self):
        """Initialize screenshot tool"""
        self.browser = BrowserManager()
        logger.info("Screenshot tool initialized")
    
    async def capture_component(self, component_name: str, save_path: Optional[str] = None) -> ToolResult:
        """Capture screenshot of current page state"""
        try:
            # Get the current page
            page = await self.browser.get_page()
            
            # Generate filename if not provided
            if not save_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = f"/tmp/screenshot_{component_name}_{timestamp}.png"
            
            # Take screenshot of current state
            await page.screenshot(path=save_path, full_page=False)
            logger.info(f"Screenshot saved to {save_path}")
            
            return ToolResult(
                tool_name="Screenshot",
                status=ToolStatus.SUCCESS,
                component=component_name,
                data={
                    "screenshot_path": save_path,
                    "timestamp": datetime.now().isoformat(),
                    "url": page.url
                }
            )
            
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return ToolResult(
                tool_name="Screenshot",
                status=ToolStatus.ERROR,
                component=component_name,
                error=str(e)
            )
    
    async def capture_full_page(self, save_path: Optional[str] = None) -> ToolResult:
        """Capture full page screenshot"""
        try:
            # Get the current page
            page = await self.browser.get_page()
            
            # Generate filename if not provided
            if not save_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = f"/tmp/screenshot_full_{timestamp}.png"
            
            # Take full page screenshot
            await page.screenshot(path=save_path, full_page=True)
            logger.info(f"Full page screenshot saved to {save_path}")
            
            return ToolResult(
                tool_name="Screenshot",
                status=ToolStatus.SUCCESS,
                component="full_page",
                data={
                    "screenshot_path": save_path,
                    "timestamp": datetime.now().isoformat(),
                    "url": page.url
                }
            )
            
        except Exception as e:
            logger.error(f"Error capturing full page screenshot: {e}")
            return ToolResult(
                tool_name="Screenshot",
                status=ToolStatus.ERROR,
                component="full_page",
                error=str(e)
            )
    
    async def cleanup(self):
        """Clean up - nothing to do as we use shared browser"""
        pass