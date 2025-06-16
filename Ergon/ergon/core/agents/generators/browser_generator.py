from typing import Dict, List, Optional, Any
import logging
import os

from ergon.core.agents.generator import AgentGenerator
from ergon.core.agents.browser.tools import BROWSER_TOOLS

logger = logging.getLogger(__name__)

class BrowserAgentGenerator:
    """Generator for browser agents"""
    
    def __init__(self):
        self.agent_type = "browser"
        
    def generate(self, name: str, description: Optional[str] = None, headless: bool = True, **kwargs) -> Any:
        """
        Generate a browser agent
        
        Args:
            name: Name of the agent
            description: Description of the agent
            headless: Whether to run browser in headless mode
            
        Returns:
            Dictionary with agent data
        """
        if not description:
            description = f"Browser agent that can navigate websites, interact with web pages, and extract information."
            
        # Create browser agent data
        agent_data = {
            "name": name,
            "description": description,
            "tools": BROWSER_TOOLS,
            "metadata": {"headless": headless},
            "system_prompt": self.get_system_prompt()
        }
        
        logger.info(f"Generated browser agent data for '{name}'")
        return agent_data
        
    def get_system_prompt(self) -> str:
        """Get the system prompt for browser agents"""
        return """You are a browser agent that can navigate websites, interact with web pages, and extract information.
        
You can:
1. Navigate to URLs
2. Extract text and HTML from web pages
3. Click on elements using CSS selectors
4. Type text into input fields
5. Take screenshots
6. Scroll web pages
7. Wait for specified times
8. Get information about elements on the page

Use these capabilities to help the user browse the web, extract information, and automate web tasks.
Always think about the best approach for each step:
- Use get_text to extract readable content
- Use get_html when you need to analyze structure
- Use step-by-step navigation through complex pages
- Take screenshots to verify visual elements
- Use appropriate waiting between actions

IMPORTANT: Always verify you're on the correct page before performing actions.
"""