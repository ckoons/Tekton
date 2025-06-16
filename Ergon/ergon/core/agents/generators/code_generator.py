"""
Code generators for creating agent source files.
"""

import os
import json
from typing import Dict, Any, List, Optional
import logging

from ergon.core.llm.client import LLMClient
from ergon.utils.config.settings import settings

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.log_level.value))


async def generate_main_file(
    llm_client: LLMClient,
    name: str,
    description: str,
    tools: Optional[List[Dict[str, Any]]] = None,
    docs_text: str = ""
) -> str:
    """
    Generate main agent implementation file.
    
    Args:
        llm_client: LLM client for generation
        name: Name of the agent
        description: Description of the agent
        tools: Optional list of tools for the agent
        docs_text: Optional documentation text for context
        
    Returns:
        Generated code as string
    """
    # Prepare prompt for the LLM
    messages = [
        {"role": "system", "content": "You are an expert Python programmer specializing in Pydantic AI agents. Your task is to generate professional-grade Python code for an AI agent based on the requirements."},
        {"role": "user", "content": f"""Create the main Python file for an AI assistant with these specifications:

Name: {name}
Description: {description}
Tools: {json.dumps(tools) if tools else 'None'}

Requirements:
1. Use the Pydantic AI framework for the implementation
2. Support both Claude and OpenAI models via environment variables
3. Include a simple CLI for testing the agent
4. Use proper error handling
5. Add appropriate type hints
6. Include docstrings for functions/classes
7. Make the code modular and maintainable

The file should be named agent.py and should be the entry point for the agent.

{f'Here is relevant documentation to help with implementation:{os.linesep}{os.linesep}' + docs_text if docs_text else ''}

Return only the Python code with no additional explanation.
"""}
    ]
    
    code = await llm_client.acomplete(messages)
    return code


async def generate_tools_file(
    llm_client: LLMClient,
    name: str,
    tools: List[Dict[str, Any]],
    docs_text: str = ""
) -> str:
    """
    Generate agent tools implementation file.
    
    Args:
        llm_client: LLM client for generation
        name: Name of the agent
        tools: List of tools for the agent
        docs_text: Optional documentation text for context
        
    Returns:
        Generated code as string
    """
    # Prepare prompt for the LLM
    messages = [
        {"role": "system", "content": "You are an expert Python programmer specializing in Pydantic AI agent tools. Your task is to generate professional-grade Python code for an AI agent tools based on the requirements."},
        {"role": "user", "content": f"""Create the tools implementation file for an AI assistant with these specifications:

Name: {name}
Tools: {json.dumps(tools)}

Requirements:
1. Use the Pydantic AI framework for the implementation
2. Implement each tool with proper function signatures and type hints
3. Include error handling for each tool
4. Add comprehensive docstrings
5. Make the code modular and maintainable

The file should be named agent_tools.py and should contain all the tool implementations.

{f'Here is relevant documentation to help with implementation:{os.linesep}{os.linesep}' + docs_text if docs_text else ''}

Return only the Python code with no additional explanation.
"""}
    ]
    
    code = await llm_client.acomplete(messages)
    return code


async def generate_prompts_file(
    llm_client: LLMClient,
    name: str,
    description: str,
    tools: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Generate agent prompts file.
    
    Args:
        llm_client: LLM client for generation
        name: Name of the agent
        description: Description of the agent
        tools: Optional list of tools for the agent
        
    Returns:
        Generated code as string
    """
    # Prepare prompt for the LLM
    messages = [
        {"role": "system", "content": "You are an expert at creating system prompts for AI assistants. Your task is to generate a prompts file containing well-crafted prompts for an AI agent."},
        {"role": "user", "content": f"""Create a Python file containing system prompts for an AI assistant with these specifications:

Name: {name}
Description: {description}
Tools: {json.dumps(tools) if tools else 'None'}

The file should:
1. Define a SYSTEM_PROMPT constant with a well-crafted system prompt
2. Include comments explaining the purpose of the prompt
3. Use triple-quoted strings for multi-line text
4. Be named agent_prompts.py

Return only the Python code with no additional explanation.
"""}
    ]
    
    code = await llm_client.acomplete(messages)
    return code


async def generate_requirements_file(
    llm_client: LLMClient,
    name: str,
    description: str,
    tools: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Generate requirements.txt file.
    
    Args:
        llm_client: LLM client for generation
        name: Name of the agent
        description: Description of the agent
        tools: Optional list of tools for the agent
        
    Returns:
        Generated content as string
    """
    # Prepare prompt for the LLM
    messages = [
        {"role": "system", "content": "You are an expert at Python package management. Your task is to generate a requirements.txt file for a Python project."},
        {"role": "user", "content": f"""Create a requirements.txt file for an AI assistant with these specifications:

Name: {name}
Description: {description}
Tools: {json.dumps(tools) if tools else 'None'}

The file should include all necessary dependencies for the agent to function, including:
1. Pydantic AI framework
2. Any libraries needed for the tools
3. Appropriate version constraints

Return only the contents of the requirements.txt file with no additional explanation.
"""}
    ]
    
    requirements = await llm_client.acomplete(messages)
    return requirements


async def generate_env_file(
    llm_client: LLMClient,
    name: str,
    model_name: str
) -> str:
    """
    Generate .env.example file.
    
    Args:
        llm_client: LLM client for generation
        name: Name of the agent
        model_name: Name of the model to use
        
    Returns:
        Generated content as string
    """
    # Create a basic .env.example file
    env_example = f"""# {name} Environment Variables

# API Keys (one is required)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Model selection
AGENT_MODEL={model_name}

# Tool-specific settings
"""
    
    return env_example


async def generate_readme_file(
    llm_client: LLMClient,
    name: str,
    description: str,
    tools: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Generate README.md file.
    
    Args:
        llm_client: LLM client for generation
        name: Name of the agent
        description: Description of the agent
        tools: Optional list of tools for the agent
        
    Returns:
        Generated content as string
    """
    # Prepare prompt for the LLM
    messages = [
        {"role": "system", "content": "You are an expert at writing documentation. Your task is to generate a README.md file for a Python project."},
        {"role": "user", "content": f"""Create a README.md file for an AI assistant with these specifications:

Name: {name}
Description: {description}
Tools: {json.dumps(tools) if tools else 'None'}

The README should include:
1. A clear title and description
2. Installation instructions
3. Usage examples
4. Information about available tools if applicable
5. Any special configuration needed

Use proper Markdown formatting.

Return only the Markdown content with no additional explanation.
"""}
    ]
    
    readme = await llm_client.acomplete(messages)
    return readme