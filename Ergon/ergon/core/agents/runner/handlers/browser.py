"""
Browser agent handler.
"""

import re
import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable, Union

# Configure logger
logger = logging.getLogger(__name__)

async def handle_browser_direct_workflow(
    input_text: str,
    tool_funcs: Dict[str, Callable]
) -> Optional[str]:
    """
    Handle direct browser workflow for browser agents.
    
    Args:
        input_text: User input text
        tool_funcs: Dictionary of tool functions
        
    Returns:
        Response if handled directly, None otherwise
    """
    if "go to" not in input_text.lower() or not any(x in input_text.lower() for x in ["title", "text", "content"]):
        return None
    
    try:
        # Extract URL from input
        url_pattern = r"go to\s+([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\/[^\s]*)?)"
        url_match = re.search(url_pattern, input_text, re.IGNORECASE)
        
        if url_match and "browse_navigate" in tool_funcs and "browse_get_text" in tool_funcs:
            url = url_match.group(1)
            if not url.startswith("http"):
                url = "https://" + url
            
            # First, navigate to the URL
            logger.info(f"Direct browser workflow: navigating to {url}")
            navigate_result = await tool_funcs["browse_navigate"](url=url)
            logger.info(f"Navigation result: {navigate_result}")
            
            # Then get the page text
            logger.info("Direct browser workflow: getting page text")
            text_result = await tool_funcs["browse_get_text"]()
            logger.info(f"Got page text (first 100 chars): {text_result[:100] if isinstance(text_result, str) else 'Not a string'}")
            
            # Check if we need the title specifically
            if "title" in input_text.lower() and "browse_get_html" in tool_funcs:
                # Get HTML to extract title
                html_result = await tool_funcs["browse_get_html"]()
                title_pattern = r"<title>(.*?)</title>"
                title_match = re.search(title_pattern, html_result if isinstance(html_result, str) else "")
                if title_match:
                    title = title_match.group(1)
                    return f"The title of the page at {url} is: {title}"
                else:
                    return f"I visited {url} but couldn't find a title tag. Here's some text content: {text_result[:200] if isinstance(text_result, str) else 'Not available'}"
            else:
                return f"I visited {url}. Here's the text content: {text_result[:500] if isinstance(text_result, str) else 'Not available'}"
    except Exception as e:
        logger.error(f"Error in direct browser workflow: {str(e)}")
    
    # Return None if direct workflow failed or not applicable
    return None