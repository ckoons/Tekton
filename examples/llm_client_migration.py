#!/usr/bin/env python3
"""
Example of migrating from custom LLM integration to the enhanced tekton-llm-client.

This example shows how to migrate an existing component's LLM integration to use
the enhanced tekton-llm-client, including prompt templates, response handlers,
and configuration utilities.
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional

# Add the package to path for example purposes
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("llm_migration_example")

###########################################
# BEFORE: Custom LLM integration example
###########################################

async def before_migration():
    """Example of custom LLM integration before migration."""
    logger.info("BEFORE MIGRATION - Custom LLM integration")
    
    # Custom prompt management
    system_prompt = "You are a helpful code review assistant. Provide detailed feedback on code quality."
    prompt = f"""
    Review this Python code for issues:
    
    ```python
    def calculate_sum(items):
        result = 0
        for i in range(len(items)):
            result += items[i]
        return result
    ```
    
    Focus on: performance, readability, and best practices.
    Return your feedback as JSON with the following structure:
    {{"issues": [{{issue objects}}], "overall_quality": "rating", "suggestions": [{{suggestion objects}}]}}
    """
    
    # Custom LLM client
    try:
        from component.custom_llm import CustomLLMClient
        
        # Initialize custom client
        client = CustomLLMClient(
            api_key=os.environ.get("LLM_API_KEY"),
            model="claude-3-haiku-20240307",
            temperature=0.7
        )
        
        # Custom response handling
        response = await client.generate(system_prompt, prompt)
        
        # Manual JSON parsing with error handling
        try:
            # Extract JSON from response
            json_str = response.strip()
            if json_str.startswith("```json"):
                json_str = json_str.split("```json", 1)[1]
            if json_str.endswith("```"):
                json_str = json_str.rsplit("```", 1)[0]
                
            data = json.loads(json_str)
            
            # Process the data
            issues = data.get("issues", [])
            overall_quality = data.get("overall_quality", "")
            suggestions = data.get("suggestions", [])
            
            logger.info(f"Found {len(issues)} issues, overall quality: {overall_quality}")
            for suggestion in suggestions:
                logger.info(f"Suggestion: {suggestion.get('description', '')}")
                
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from response")
            
        except Exception as e:
            logger.error(f"Error processing response: {e}")
        
        # Clean up
        await client.close()
        
    except ImportError:
        # Simulation for the example
        logger.info("(Simulating custom LLM client for the example)")

###########################################
# AFTER: Enhanced tekton-llm-client
###########################################

async def after_migration():
    """Example of LLM integration after migration to tekton-llm-client."""
    logger.info("AFTER MIGRATION - Enhanced tekton-llm-client")
    
    from tekton_llm_client import (
        TektonLLMClient,
        PromptTemplateRegistry,
        parse_json,
        StructuredOutputParser,
        OutputFormat,
        load_settings,
        ClientSettings,
        LLMSettings
    )
    
    try:
        # 1. Load configuration from environment and file
        settings = load_settings(
            component_id="code-reviewer",
            file_path="/tmp/llm_settings.json",
            load_from_env=True
        )
        
        # 2. Create LLM client with settings
        client = TektonLLMClient(
            component_id=settings.component_id,
            provider_id=settings.llm.provider,
            model_id=settings.llm.model,
            timeout=settings.llm.timeout
        )
        
        # 3. Initialize the client
        await client.initialize()
        
        # 4. Use prompt templates
        registry = PromptTemplateRegistry()
        
        # Register custom template
        registry.register({
            "name": "code_review",
            "template": """Review this {{ language }} code for issues:

```{{ language }}
{{ code }}
```

Focus on: {{ focus_areas }}.
Return your feedback as JSON with the following structure:
{"issues": [{"description": "...", "severity": "high/medium/low", "line": 123}], "overall_quality": "good/fair/poor", "suggestions": [{"description": "..."}]}
""",
            "description": "Template for code review tasks"
        })
        
        # Render the template with variables
        prompt = registry.render(
            "code_review",
            language="python",
            code="def calculate_sum(items):\n    result = 0\n    for i in range(len(items)):\n        result += items[i]\n    return result",
            focus_areas="performance, readability, and best practices"
        )
        
        # 5. Generate text with the client
        response = await client.generate_text(
            prompt=prompt,
            system_prompt="You are a helpful code review assistant. Provide detailed feedback on code quality."
        )
        
        # 6. Parse the response with error handling
        try:
            data = parse_json(response.content)
            
            # Process the structured data
            issues = data.get("issues", [])
            overall_quality = data.get("overall_quality", "")
            suggestions = data.get("suggestions", [])
            
            logger.info(f"Found {len(issues)} issues, overall quality: {overall_quality}")
            for suggestion in suggestions:
                logger.info(f"Suggestion: {suggestion.get('description', '')}")
                
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
        
        # 7. Use structured output parser for other formats
        list_prompt = "List 3 ways to improve the function."
        list_response = await client.generate_text(
            prompt=list_prompt,
            system_prompt="You are a coding assistant. Respond with numbered lists."
        )
        
        parser = StructuredOutputParser(format=OutputFormat.LIST)
        improvements = parser.parse(list_response.content)
        
        logger.info("Improvement suggestions:")
        for i, improvement in enumerate(improvements, 1):
            logger.info(f"{i}. {improvement}")
        
        # 8. Clean up
        await client.shutdown()
        
    except Exception as e:
        logger.error(f"Error in enhanced LLM client example: {e}")

###########################################
# Migration benefits example
###########################################

async def demo_streaming_handler():
    """Demonstrate streaming handler benefits."""
    logger.info("MIGRATION BENEFIT - Advanced streaming handler")
    
    try:
        from tekton_llm_client import TektonLLMClient, StreamHandler
        
        # Initialize client
        client = TektonLLMClient(component_id="demo")
        await client.initialize()
        
        # Create a stream handler
        handler = StreamHandler()
        
        # Stream processing with transformation
        prompt = "Write a haiku about Python programming."
        stream = client.generate_text(
            prompt=prompt,
            system_prompt="You are a creative writing assistant.",
            streaming=True
        )
        
        # Process the stream with a transformation (capitalizing text)
        print("Streaming response with transformation:")
        await handler.process_stream(
            stream,
            transform=lambda text: text.upper()
        )
        
        # Stream with buffering until condition is met
        prompt = "Write a numbered list of 5 Python best practices."
        stream = client.generate_text(
            prompt=prompt,
            system_prompt="You are a Python expert.",
            streaming=True
        )
        
        # Buffer until we have a complete item
        print("\nBuffered streaming (complete items):")
        async for segment in handler.buffer_until(
            stream,
            condition=lambda text: text.count("\n") > 0
        ):
            print(f"COMPLETE ITEM: {segment.strip()}")
        
        await client.shutdown()
        
    except Exception as e:
        logger.error(f"Error in streaming demo: {e}")
        print(f"(Simulating streaming example)")

async def main():
    """Run the migration examples."""
    # Show before migration
    await before_migration()
    
    print("\n" + "="*50 + "\n")
    
    # Show after migration
    await after_migration()
    
    print("\n" + "="*50 + "\n")
    
    # Show migration benefits
    await demo_streaming_handler()
    
    logger.info("Migration example complete")

if __name__ == "__main__":
    asyncio.run(main())