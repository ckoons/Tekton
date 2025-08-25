#!/usr/bin/env python3
"""
Enhanced usage example for Tekton LLM Client.

This example demonstrates the new features:
1. Prompt templates
2. Response handlers
3. Configuration utilities
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any, List
from pydantic import BaseModel

# Add the package to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tekton_llm_client import (
    TektonLLMClient,
    PromptTemplateRegistry, PromptTemplate,
    JSONParser, parse_json,
    StreamHandler, collect_stream,
    StructuredOutputParser, OutputFormat,
    ClientSettings, LLMSettings, load_settings
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("enhanced-example")

# Example model for structured output
class CodeIssue(BaseModel):
    """Model for a code issue."""
    severity: str
    description: str
    line_number: int = 0
    suggestion: str = ""

class CodeReview(BaseModel):
    """Model for a code review response."""
    issues: List[CodeIssue]
    overall_quality: str
    primary_concerns: List[str]

async def prompt_template_example():
    """Example using prompt templates."""
    logger.info("\n=== Prompt Template Example ===")
    
    # Create a template registry
    registry = PromptTemplateRegistry()
    
    # Register a custom template
    registry.register({
        "name": "code_explanation",
        "template": "Explain the following {{ language }} code:\n\n```{{ language }}\n{{ code }}\n```\n\nFocus on {{ focus }}.",
        "description": "Template for code explanation."
    })
    
    # Create a client with settings
    settings = ClientSettings(
        component_id="example-enhanced",
        llm=LLMSettings(
            provider="anthropic",
            model="claude-3-sonnet-20240229",
            temperature=0.2
        )
    )
    
    client = TektonLLMClient(
        component_id=settings.component_id,
        provider_id=settings.llm.provider,
        model_id=settings.llm.model,
        rhetor_url=settings.llm.rhetor_url,
        timeout=settings.llm.timeout
    )
    
    # Initialize the client
    await client.initialize()
    
    try:
        # Prepare a sample code snippet
        code = """
def fibonacci(n):
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    
    return fib
        """
        
        # Render the template
        prompt = registry.render(
            "code_explanation",
            language="python",
            code=code,
            focus="algorithmic complexity and edge cases"
        )
        
        logger.info(f"Generated prompt:\n{prompt}\n")
        
        # Send to LLM
        response = await client.generate_text(
            prompt=prompt,
            system_prompt="You are a senior Python developer reviewing code."
        )
        
        logger.info(f"Response: {response.content[:200]}...\n")
        
    finally:
        await client.shutdown()

async def response_handler_example():
    """Example using response handlers."""
    logger.info("\n=== Response Handler Example ===")
    
    # Create a client
    client = TektonLLMClient(component_id="example-enhanced")
    await client.initialize()
    
    try:
        # Example of structured output with JSON parsing
        system_prompt = """You are a code review assistant. 
When analyzing code, always respond with a JSON object containing:
- "issues": an array of code issues, each with "severity", "description", "line_number", and "suggestion" fields
- "overall_quality": a brief assessment of code quality
- "primary_concerns": an array of primary concerns"""
        
        code = """
function processData(data) {
    var results = [];
    for (var i = 0; i < data.length; i++) {
        if (data[i].status == 'active') {
            results.push(data[i]);
        }
    }
    return results;
}
        """
        
        prompt = f"Review this JavaScript code for issues and improvements:\n\n```js\n{code}\n```"
        
        # Get a raw response
        response = await client.generate_text(
            prompt=prompt,
            system_prompt=system_prompt
        )
        
        # Parse the JSON
        try:
            parsed_data = parse_json(response.content)
            logger.info("Successfully parsed JSON response:")
            logger.info(json.dumps(parsed_data, indent=2))
            
            # Validate with Pydantic model
            review = CodeReview.model_validate(parsed_data)
            logger.info("\nValidated with Pydantic model:")
            logger.info(f"Found {len(review.issues)} issues")
            logger.info(f"Overall quality: {review.overall_quality}")
            
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            logger.info(f"Raw response: {response.content}")
            
        # Example of using StructuredOutputParser
        logger.info("\nUsing StructuredOutputParser:")
        
        # Define a new prompt for list output
        list_prompt = "List 5 best practices for JavaScript coding. Keep it concise."
        list_system = "You are a JavaScript expert. Provide responses as numbered lists only."
        
        list_response = await client.generate_text(
            prompt=list_prompt,
            system_prompt=list_system
        )
        
        # Parse as a list
        parser = StructuredOutputParser(format=OutputFormat.LIST)
        best_practices = parser.parse(list_response.content)
        
        logger.info("Parsed list response:")
        for i, practice in enumerate(best_practices, 1):
            logger.info(f"{i}. {practice}")
        
    finally:
        await client.shutdown()

async def config_example():
    """Example using configuration utilities."""
    logger.info("\n=== Configuration Example ===")
    
    # Create settings with environment-aware values
    temp_file = "/tmp/llm_settings.json"
    
    # Create sample settings
    settings = ClientSettings(
        component_id="example-config",
        llm=LLMSettings(
            provider="anthropic",
            model="claude-3-haiku-20240307",
            temperature=0.5,
            max_tokens=1000,
            templates_dir="/tmp/templates"
        ),
        context_id="config-demo",
        additional_options={
            "debug": True,
            "metrics_enabled": True
        }
    )
    
    # Save settings to file
    from tekton_llm_client.config import save_settings
    save_settings(settings, temp_file)
    logger.info(f"Saved settings to {temp_file}")
    
    # Load settings from file
    from tekton_llm_client.config import load_settings
    loaded_settings = load_settings("example-load", file_path=temp_file)
    logger.info("Loaded settings:")
    logger.info(f"Component ID: {loaded_settings.component_id}")
    logger.info(f"Provider: {loaded_settings.llm.provider}")
    logger.info(f"Model: {loaded_settings.llm.model}")
    logger.info(f"Temperature: {loaded_settings.llm.temperature}")
    
    # Set an environment variable
    from tekton_llm_client.config import set_env, get_env
    set_env("PROVIDER", "openai")
    
    # Load settings with env vars (should override the provider)
    env_settings = load_settings("example-env", file_path=temp_file, load_from_env=True)
    logger.info("\nSettings with environment variables:")
    logger.info(f"Provider: {env_settings.llm.provider}")  # Should be "openai" from env
    
    # Create a client using the settings
    client = TektonLLMClient(
        component_id=loaded_settings.component_id,
        provider_id=loaded_settings.llm.provider,
        model_id=loaded_settings.llm.model,
        timeout=loaded_settings.llm.timeout
    )
    
    logger.info("\nInitialized client with loaded settings")
    
    # Clean up
    try:
        os.remove(temp_file)
        logger.info(f"Removed temporary file {temp_file}")
    except:
        pass

async def streaming_handler_example():
    """Example using streaming response handlers."""
    logger.info("\n=== Streaming Handler Example ===")
    
    # Create a client
    client = TektonLLMClient(component_id="example-streaming")
    await client.initialize()
    
    try:
        prompt = "Write a short story about artificial intelligence in about 150 words."
        system_prompt = "You are a creative writer specialized in brief technological fiction."
        
        # Create a StreamHandler
        handler = StreamHandler()
        
        # Print header for story
        print("\n--- CI Short Story ---\n")
        
        # Stream and collect chunks with live output
        stream = client.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            streaming=True
        )
        
        # Process the stream with live output
        result = await handler.process_stream(
            stream,
            transform=lambda text: text.replace("AI", "Artificial Intelligence")
        )
        
        print("\n--- Story Complete ---\n")
        
        # Show word count
        word_count = len(result.split())
        logger.info(f"Generated {word_count} words")
        
    finally:
        await client.shutdown()

async def main():
    """Run all examples."""
    await prompt_template_example()
    await response_handler_example()
    await config_example()
    await streaming_handler_example()

if __name__ == "__main__":
    asyncio.run(main())