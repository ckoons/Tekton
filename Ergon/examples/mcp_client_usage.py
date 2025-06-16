"""
Example usage of the MCP client in Ergon.

This example demonstrates how to use the MCP client to process
multimodal content and register tools.
"""

import os
import asyncio
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add Ergon to path
import sys
ergon_dir = str(Path(__file__).parent.parent)
if ergon_dir not in sys.path:
    sys.path.append(ergon_dir)

from ergon.core.mcp_client import MCPClient
from ergon.utils.mcp_adapter import (
    prepare_text_content,
    prepare_code_content,
    prepare_structured_content,
    extract_text_from_mcp_result,
    extract_data_from_mcp_result
)

async def process_text_example(client: MCPClient):
    """Example of processing text content."""
    logger.info("Processing text content...")
    
    text_content = "Analyze this text and provide key insights."
    processing_options = {
        "analysis_level": "detailed",
        "extract_entities": True
    }
    
    result = await client.process_content(
        content=text_content,
        content_type="text",
        processing_options=processing_options
    )
    
    text_result = extract_text_from_mcp_result(result)
    logger.info(f"Text processing result: {text_result}")
    
    return result

async def process_code_example(client: MCPClient):
    """Example of processing code content."""
    logger.info("Processing code content...")
    
    code_content = """
    def fibonacci(n):
        if n <= 1:
            return n
        else:
            return fibonacci(n-1) + fibonacci(n-2)
    
    print(fibonacci(10))
    """
    
    processing_options = {
        "language": "python",
        "analysis_type": "optimization",
        "code_quality": True
    }
    
    result = await client.process_content(
        content=code_content,
        content_type="code",
        processing_options=processing_options
    )
    
    text_result = extract_text_from_mcp_result(result)
    logger.info(f"Code processing result: {text_result}")
    
    return result

async def process_structured_example(client: MCPClient):
    """Example of processing structured content."""
    logger.info("Processing structured content...")
    
    structured_content = {
        "project": "Tekton",
        "components": [
            {"name": "Ergon", "status": "active"},
            {"name": "Hermes", "status": "active"},
            {"name": "Athena", "status": "development"}
        ],
        "metrics": {
            "performance": 0.85,
            "stability": 0.92
        }
    }
    
    processing_options = {
        "format": "json",
        "analysis_type": "summary"
    }
    
    result = await client.process_content(
        content=structured_content,
        content_type="structured",
        processing_options=processing_options
    )
    
    data_result = extract_data_from_mcp_result(result)
    logger.info(f"Structured data processing result: {data_result}")
    
    return result

async def register_tool_example(client: MCPClient):
    """Example of registering and using a tool."""
    logger.info("Registering a tool...")
    
    # Define a sample tool handler
    async def calculator_handler(parameters, context):
        operation = parameters.get("operation")
        a = parameters.get("a", 0)
        b = parameters.get("b", 0)
        
        if operation == "add":
            return a + b
        elif operation == "subtract":
            return a - b
        elif operation == "multiply":
            return a * b
        elif operation == "divide":
            if b == 0:
                raise ValueError("Cannot divide by zero")
            return a / b
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    # Register the tool
    tool_registered = await client.register_tool(
        tool_id="calculator",
        name="Simple Calculator",
        description="Performs basic arithmetic operations",
        parameters={
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "The operation to perform"
                },
                "a": {
                    "type": "number",
                    "description": "First operand"
                },
                "b": {
                    "type": "number",
                    "description": "Second operand"
                }
            },
            "required": ["operation", "a", "b"]
        },
        returns={
            "type": "number",
            "description": "Result of the operation"
        },
        handler=calculator_handler
    )
    
    if not tool_registered:
        logger.error("Failed to register calculator tool")
        return
    
    logger.info("Tool registered successfully")
    
    # Execute the tool
    logger.info("Executing calculator tool...")
    
    execution_result = await client.execute_tool(
        tool_id="calculator",
        parameters={
            "operation": "add",
            "a": 5,
            "b": 3
        }
    )
    
    logger.info(f"Tool execution result: {execution_result}")
    
    # Unregister the tool
    logger.info("Unregistering calculator tool...")
    
    unregistered = await client.unregister_tool("calculator")
    logger.info(f"Tool unregistered: {unregistered}")
    
    return execution_result

async def context_example(client: MCPClient):
    """Example of creating and enhancing a context."""
    logger.info("Creating a context...")
    
    # Create a new context
    context_id = await client.create_context(
        context_type="conversation",
        content={
            "messages": [
                {"role": "user", "content": "How can I optimize my Python code?"}
            ],
            "metadata": {
                "topic": "code optimization",
                "language": "python"
            }
        }
    )
    
    if not context_id:
        logger.error("Failed to create context")
        return
    
    logger.info(f"Context created with ID: {context_id}")
    
    # Enhance the context
    logger.info("Enhancing the context...")
    
    enhanced = await client.enhance_context(
        context_id=context_id,
        content={
            "messages": [
                {"role": "assistant", "content": "There are several ways to optimize Python code..."},
                {"role": "user", "content": "Could you provide specific examples?"}
            ]
        }
    )
    
    logger.info(f"Context enhanced: {enhanced}")
    
    # Process content with the context
    logger.info("Processing content with context...")
    
    result = await client.process_content(
        content="Here's my code to optimize: def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
        content_type="code",
        context={"context_id": context_id}
    )
    
    text_result = extract_text_from_mcp_result(result)
    logger.info(f"Processing with context result: {text_result}")
    
    return result

async def main():
    """Run the MCP client examples."""
    # Initialize the client
    client = MCPClient(
        client_name="Ergon MCP Example",
        hermes_url=os.environ.get("HERMES_URL")
    )
    
    try:
        # Initialize the client
        await client.initialize()
        
        # Run examples
        await process_text_example(client)
        await process_code_example(client)
        await process_structured_example(client)
        await register_tool_example(client)
        await context_example(client)
        
    finally:
        # Close the client
        await client.close()
        logger.info("Client closed")

if __name__ == "__main__":
    asyncio.run(main())