"""
Examples of MCP tool registration and usage.

This module provides examples of registering and using tools with Ergon's
MCP integration system.
"""

import logging
from typing import Dict, List, Any, Optional

from ergon.core.repository.mcp import (
    register_tool,
    unregister_tool,
    mcp_tool,
    adapt_tool_for_mcp,
    MCPToolAdapter
)

logger = logging.getLogger(__name__)

# Example 1: Simple function with manual schema
def text_summarizer(text: str, max_length: int = 100) -> str:
    """
    Summarize text to the specified maximum length.
    
    Args:
        text: Text to summarize
        max_length: Maximum length of summary
        
    Returns:
        Summarized text
    """
    if len(text) <= max_length:
        return text
    
    # Simple summarization by truncation with ellipsis
    return text[:max_length-3] + "..."

# Register the function manually
register_tool(
    name="text_summarizer",
    description="Summarizes text to the specified maximum length",
    function=text_summarizer,
    schema={
        "name": "text_summarizer",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to summarize"
                },
                "max_length": {
                    "type": "integer",
                    "description": "Maximum length of summary",
                    "default": 100
                }
            },
            "required": ["text"]
        }
    },
    tags=["text", "summarization", "utility"],
    version="1.0.0"
)

# Example 2: Using the decorator
@mcp_tool(
    name="reverse_text",
    description="Reverses input text",
    schema={
        "name": "reverse_text",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to reverse"
                },
                "preserve_words": {
                    "type": "boolean",
                    "description": "Whether to preserve word order",
                    "default": False
                }
            },
            "required": ["text"]
        }
    },
    tags=["text", "utility"],
    version="1.0.0"
)
def reverse_text(text: str, preserve_words: bool = False) -> str:
    """
    Reverse input text.
    
    Args:
        text: Text to reverse
        preserve_words: If True, reverse each word but preserve word order
        
    Returns:
        Reversed text
    """
    if preserve_words:
        words = text.split()
        reversed_words = [word[::-1] for word in words]
        return " ".join(reversed_words)
    else:
        return text[::-1]

# Example 3: Using auto-generated schema
def calculate_statistics(
    numbers: List[float], 
    include_median: bool = False,
    include_mode: bool = False
) -> Dict[str, float]:
    """
    Calculate statistical measures for a list of numbers.
    
    Args:
        numbers: List of numbers to analyze
        include_median: Whether to include median in results
        include_mode: Whether to include mode in results
        
    Returns:
        Dictionary of statistical measures
    """
    if not numbers:
        return {"error": "Empty list provided"}
    
    result = {
        "count": len(numbers),
        "sum": sum(numbers),
        "mean": sum(numbers) / len(numbers),
        "min": min(numbers),
        "max": max(numbers)
    }
    
    if include_median:
        sorted_nums = sorted(numbers)
        mid = len(sorted_nums) // 2
        if len(sorted_nums) % 2 == 0:
            result["median"] = (sorted_nums[mid-1] + sorted_nums[mid]) / 2
        else:
            result["median"] = sorted_nums[mid]
    
    if include_mode:
        from collections import Counter
        counts = Counter(numbers)
        mode_count = max(counts.values())
        if mode_count > 1:  # Mode only exists if a value appears more than once
            result["mode"] = [num for num, count in counts.items() if count == mode_count]
        else:
            result["mode"] = "No mode (all values appear once)"
    
    return result

# Auto-generate and register
stats_tool = adapt_tool_for_mcp(
    func=calculate_statistics,
    name="stat_calculator",
    description="Calculate statistical measures for a list of numbers",
    tags=["math", "statistics", "analysis"],
    version="1.0.0"
)

register_tool(**stats_tool)

def example_usage():
    """
    Example of using the registered tools.
    """
    from ergon.core.repository.mcp import get_tool, get_registered_tools
    
    # Get all registered tools
    all_tools = get_registered_tools()
    logger.info(f"Registered tools: {', '.join(all_tools.keys())}")
    
    # Use the summarizer
    summarizer = get_tool("text_summarizer")
    if summarizer:
        success, result = MCPToolAdapter.execute_tool(
            summarizer["function"],
            {"text": "This is a very long text that should be summarized to fit within a smaller length.", "max_length": 20}
        )
        logger.info(f"Summarization result: {result}")
    
    # Use the statistics calculator
    stats_tool = get_tool("stat_calculator")
    if stats_tool:
        success, result = MCPToolAdapter.execute_tool(
            stats_tool["function"],
            {"numbers": [1, 2, 3, 4, 5, 5, 6], "include_median": True, "include_mode": True}
        )
        logger.info(f"Statistics result: {result}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    example_usage()