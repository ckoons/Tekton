"""
Browser Manager for UI DevTools

Manages the Playwright browser instance for interacting with the Hephaestus UI.
"""

import asyncio
from typing import Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from .constants import HEPHAESTUS_URL, UIToolsError


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