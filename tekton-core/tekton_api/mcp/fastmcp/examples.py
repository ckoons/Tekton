"""
FastMCP Examples - Examples of using the FastMCP integration.

This module provides examples of how to use the FastMCP integration
to define and use MCP tools, processors, and capabilities.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional

from tekton.mcp.fastmcp import (
    mcp_tool,
    mcp_capability,
    mcp_processor,
    mcp_context,
    MCPClient,
    register_component,
    execute_tool
)

# Example 1: Creating a simple tool

@mcp_tool(
    name="HelloWorld",
    description="A simple hello world tool",
    tags=["example", "greeting"],
    category="demo"
)
async def hello_world(name: str = "World") -> Dict[str, str]:
    """
    Say hello to the specified name.
    
    Args:
        name: Name to greet
        
    Returns:
        Greeting message
    """
    return {
        "message": f"Hello, {name}!"
    }

# Example 2: Creating a tool with multiple parameters

@mcp_tool(
    name="Calculator",
    description="A simple calculator tool",
    tags=["math", "calculator"],
    category="utility"
)
async def calculator(
    operation: str,
    a: float,
    b: float,
    precision: int = 2
) -> Dict[str, Any]:
    """
    Perform a calculation.
    
    Args:
        operation: Operation to perform (add, subtract, multiply, divide)
        a: First number
        b: Second number
        precision: Decimal precision for the result
        
    Returns:
        Calculation result
    """
    result = None
    
    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b == 0:
            return {
                "error": "Division by zero"
            }
        result = a / b
    else:
        return {
            "error": f"Unknown operation: {operation}"
        }
        
    return {
        "operation": operation,
        "a": a,
        "b": b,
        "result": round(result, precision)
    }

# Example 3: Defining capabilities

@mcp_capability(
    name="text_analysis",
    description="Capability for analyzing text content",
    modality="text"
)
@mcp_tool(
    name="WordCount",
    description="Count words in text",
    tags=["text", "analysis"],
    category="text_processing"
)
async def word_count(text: str) -> Dict[str, Any]:
    """
    Count words in text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Word count and statistics
    """
    words = text.split()
    word_count = len(words)
    char_count = len(text)
    
    return {
        "word_count": word_count,
        "character_count": char_count,
        "average_word_length": char_count / word_count if word_count > 0 else 0
    }

# Example 4: Creating a processor

@mcp_processor(
    name="TextProcessor",
    description="Processor for text content",
    capabilities=["text_analysis", "text_processing"],
    endpoint="http://localhost:8000/mcp/process"
)
class TextProcessor:
    """
    Processor for text content.
    
    This class processes text content, implementing various
    text analysis and processing capabilities.
    """
    
    def __init__(self):
        """Initialize the text processor."""
        self.statistics = {
            "messages_processed": 0,
            "characters_processed": 0
        }
        
    @mcp_capability(
        name="text_processing",
        description="Capability for processing text content",
        modality="text"
    )
    async def process_text(self, text: str) -> Dict[str, Any]:
        """
        Process text content.
        
        Args:
            text: Text to process
            
        Returns:
            Processing result
        """
        # Update statistics
        self.statistics["messages_processed"] += 1
        self.statistics["characters_processed"] += len(text)
        
        # Process text
        words = text.split()
        word_count = len(words)
        char_count = len(text)
        
        return {
            "word_count": word_count,
            "character_count": char_count,
            "language": "en",  # Simple assumption
            "processed_by": "TextProcessor"
        }
        
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get processor statistics.
        
        Returns:
            Processor statistics
        """
        return self.statistics

# Example 5: Using the MCP client

async def client_example():
    """Example of using the MCP client."""
    # Create client
    client = MCPClient(
        base_url="http://localhost:8000",
        component_id="example-client",
        component_name="Example Client"
    )
    
    try:
        # Register component
        registered = await client.register_component(
            capabilities=["text_processing", "calculator"],
            endpoint="http://localhost:8001",
            metadata={
                "description": "Example client for MCP integration"
            }
        )
        
        if registered:
            # Execute calculator tool
            result = await client.execute_tool(
                tool_id="calculator",
                parameters={
                    "operation": "add",
                    "a": 2,
                    "b": 3
                }
            )
            
            print(f"Calculator result: {result}")
            
            # Get capabilities
            capabilities = await client.get_capabilities()
            print(f"MCP capabilities: {capabilities}")
    finally:
        # Close client
        await client.close()
        
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Print tool metadata
    print(f"HelloWorld tool metadata: {hello_world._mcp_tool_meta.to_dict()}")
    print(f"Calculator tool metadata: {calculator._mcp_tool_meta.to_dict()}")
    print(f"WordCount tool metadata: {word_count._mcp_tool_meta.to_dict()}")
    
    # Create and print processor metadata
    processor = TextProcessor()
    print(f"TextProcessor metadata: {processor._mcp_processor_meta}")
    
    # Run async example
    asyncio.run(client_example())