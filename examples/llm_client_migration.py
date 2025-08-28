#!/usr/bin/env python3
"""
Example of migrating from custom LLM integration to using Rhetor.

This example shows how to migrate an existing component's LLM integration to use
the unified Rhetor service for all LLM operations.
"""

import os
from shared.env import TektonEnviron
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
            api_key=TektonEnviron.get("LLM_API_KEY"),
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
# AFTER: Using Rhetor unified LLM service
###########################################

async def after_migration():
    """Example of LLM integration after migration to Rhetor."""
    logger.info("AFTER MIGRATION - Rhetor unified LLM service")
    
    from shared.rhetor_client import RhetorClient
    import json
    
    try:
        # 1. Create Rhetor client - automatically uses the right model
        client = RhetorClient(component="code-reviewer")
        
        # 2. Prepare the prompt - combine system and user prompts
        full_prompt = f"""{system_prompt}

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
{{"issues": [{{"description": "...", "severity": "high/medium/low", "line": 123}}], "overall_quality": "good/fair/poor", "suggestions": [{{"description": "..."}}]}}
"""
        
        # 3. Generate response using Rhetor
        response = await client.generate(
            prompt=full_prompt,
            capability="code",  # Rhetor will select the best model for code analysis
            temperature=0.7,
            max_tokens=2000
        )
        
        # 4. Parse the response
        try:
            # Extract JSON from response if needed
            json_str = response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json", 1)[1]
                json_str = json_str.split("```", 1)[0]
                
            data = json.loads(json_str)
            
            # Process the structured data
            issues = data.get("issues", [])
            overall_quality = data.get("overall_quality", "")
            suggestions = data.get("suggestions", [])
            
            logger.info(f"Found {len(issues)} issues, overall quality: {overall_quality}")
            for suggestion in suggestions:
                logger.info(f"Suggestion: {suggestion.get('description', '')}")
                
        except json.JSONDecodeError:
            logger.info("Response was not JSON, treating as plain text:")
            logger.info(response)
        
        # 5. Use different capabilities for different tasks
        
        # For task decomposition
        task_steps = await client.decompose_task(
            "Refactor the calculate_sum function to use built-in Python features"
        )
        logger.info(f"Task decomposition: {task_steps}")
        
        # For general chat/explanation
        explanation = await client.chat(
            "Explain why using enumerate() is better than range(len()) in Python"
        )
        logger.info(f"Explanation: {explanation}")
        
        # For code analysis with specific focus
        analysis = await client.analyze(
            "def calculate_sum(items): return sum(items)",
            focus="performance and memory usage"
        )
        logger.info(f"Analysis: {analysis}")
        
    except Exception as e:
        logger.error(f"Error using Rhetor client: {e}")

###########################################
# Migration benefits demonstration
###########################################

async def benefits_demo():
    """Demonstrate the benefits of using Rhetor."""
    logger.info("BENEFITS OF RHETOR MIGRATION")
    
    from shared.rhetor_client import RhetorClient
    
    # 1. Automatic model selection based on task
    client = RhetorClient(component="example")
    
    # Rhetor automatically picks the best model for each capability
    capabilities = ["code", "planning", "reasoning", "chat"]
    
    for capability in capabilities:
        logger.info(f"\nCapability: {capability}")
        response = await client.generate(
            prompt=f"Test prompt for {capability}",
            capability=capability
        )
        logger.info(f"Rhetor selected appropriate model for {capability}")
    
    # 2. Centralized configuration management
    logger.info("\nCentralized model configuration - no need to manage API keys or model names")
    
    # 3. Built-in fallback and retry logic
    logger.info("Built-in error handling and fallbacks")
    
    # 4. Consistent API across all components
    logger.info("Same API for all Tekton components")

###########################################
# Main execution
###########################################

async def main():
    """Run the migration examples."""
    logger.info("=" * 50)
    logger.info("LLM CLIENT MIGRATION EXAMPLE")
    logger.info("=" * 50)
    
    # Show before migration approach
    await before_migration()
    
    logger.info("\n" + "=" * 50 + "\n")
    
    # Show after migration approach
    await after_migration()
    
    logger.info("\n" + "=" * 50 + "\n")
    
    # Show benefits
    await benefits_demo()
    
    logger.info("\n" + "=" * 50)
    logger.info("MIGRATION SUMMARY")
    logger.info("=" * 50)
    logger.info("""
Key advantages of using Rhetor:
1. Automatic model selection based on task type
2. Centralized configuration and API key management
3. Built-in error handling and retries
4. Consistent API across all Tekton components
5. Easy switching between models without code changes
6. Support for multiple capabilities (code, planning, reasoning, chat)
7. No need to manage prompt templates or parsing logic separately
""")

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())