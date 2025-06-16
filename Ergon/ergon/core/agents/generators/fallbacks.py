"""
Fallback code generators for when LLM generation fails.
"""

import os
from typing import Dict, Any, List, Optional


def generate_fallback_main_file(
    name: str,
    description: str,
    model_name: str
) -> str:
    """
    Generate a fallback agent main file when LLM fails.
    
    Args:
        name: Name of the agent
        description: Description of the agent
        model_name: Name of the model to use
        
    Returns:
        Fallback code as string
    """
    snake_case_name = name.lower().replace(" ", "_")
    
    return f"""from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIModel
from dotenv import load_dotenv
import os
import asyncio
from typing import Optional

# Import prompts and tools
from agent_prompts import SYSTEM_PROMPT

# Load environment variables
load_dotenv()

def create_agent() -> Agent:
    \"\"\"
    Create and initialize the {name} agent.
    
    Returns:
        Agent: Initialized Pydantic AI agent
    \"\"\"
    # Initialize model based on environment variable
    model_name = os.getenv("AGENT_MODEL", "{model_name}")
    
    if "claude" in model_name.lower():
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        model = AnthropicModel(model_name, api_key=api_key)
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        model = OpenAIModel(model_name, api_key=api_key)
    
    # Create agent
    agent = Agent(
        model,
        system_prompt=SYSTEM_PROMPT
    )
    
    return agent

{snake_case_name}_agent = create_agent()

async def run_agent(user_input: str) -> str:
    \"\"\"
    Run the {name} agent with user input.
    
    Args:
        user_input: User's message to the agent
        
    Returns:
        str: Agent's response
    \"\"\"
    try:
        result = await {snake_case_name}_agent.run(user_input)
        return result.data
    except Exception as error:
        return f"Error running {name}: {str(error)}"

def main():
    \"\"\"CLI entry point for the agent.\"\"\"
    print(f"Welcome to {name}! Type 'exit' to quit.")
    
    async def interact():
        while True:
            user_input = input("> ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            response = await run_agent(user_input)
            print(f"{name}: {response}")
    
    asyncio.run(interact())

if __name__ == "__main__":
    main()
"""


def generate_fallback_tools_file(
    name: str,
    tools: List[Dict[str, Any]]
) -> str:
    """
    Generate a fallback agent tools file when LLM fails.
    
    Args:
        name: Name of the agent
        tools: List of tools for the agent
        
    Returns:
        Fallback code as string
    """
    tool_implementations = []
    
    for tool in tools:
        tool_name = tool["name"]
        tool_desc = tool.get("description", f"Tool for {tool_name}")
        
        tool_implementation = f"""
async def {tool_name}(query: str) -> str:
    \"\"\"
    {tool_desc}
    
    Args:
        query: Input for the tool
        
    Returns:
        str: Tool output
    \"\"\"
    # TODO: Implement {tool_name} functionality
    return f"The {tool_name} tool received: {{query}}"
"""
        tool_implementations.append(tool_implementation)
    
    return f"""from typing import Dict, Any, List, Optional
import os
import asyncio

{os.linesep.join(tool_implementations)}
"""


def generate_fallback_prompts_file(
    name: str,
    description: str,
    tools: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Generate a fallback agent prompts file when LLM fails.
    
    Args:
        name: Name of the agent
        description: Description of the agent
        tools: Optional list of tools for the agent
        
    Returns:
        Fallback code as string
    """
    system_prompt = f"""You are {name}, an AI assistant. {description}

Your goal is to provide helpful, accurate, and friendly responses to user queries.

Always be respectful and avoid any harmful, illegal, unethical or deceptive content.
If you're unsure about something, acknowledge that limitation rather than making up information.
"""
    
    if tools:
        tool_descriptions = "\n".join(f"- {tool['name']}: {tool.get('description', 'No description')}" for tool in tools)
        system_prompt += f"\n\nYou have access to the following tools:\n{tool_descriptions}\n"
        system_prompt += "\nWhen a tool would be helpful for answering a question, use it rather than making up information."
    
    return f"""# System prompt for {name} agent

SYSTEM_PROMPT = \"\"\"
{system_prompt}
\"\"\"
"""


def generate_fallback_requirements_file() -> str:
    """
    Generate a fallback requirements.txt file when LLM fails.
    
    Returns:
        Fallback content as string
    """
    return """pydantic-ai>=0.7.0
python-dotenv>=1.0.0
anthropic>=0.6.0
openai>=1.1.0
"""


def generate_fallback_env_file(
    name: str,
    model_name: str
) -> str:
    """
    Generate a fallback .env.example file.
    
    Args:
        name: Name of the agent
        model_name: Name of the model to use
        
    Returns:
        Fallback content as string
    """
    return f"""# {name} Environment Variables

# API Keys (one is required)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Model selection
AGENT_MODEL={model_name}

# Tool-specific settings
"""


def generate_fallback_readme_file(
    name: str,
    description: str,
    tools: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Generate a fallback README.md file when LLM fails.
    
    Args:
        name: Name of the agent
        description: Description of the agent
        tools: Optional list of tools for the agent
        
    Returns:
        Fallback content as string
    """
    readme = f"""# {name}

{description}

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file based on `.env.example` with your API keys

## Usage

Run the agent:
```
python agent.py
```

## Features

This agent can help with:

- Responding to questions related to {description.lower()}
"""
    
    if tools:
        readme += "\n\n## Tools\n\n"
        for tool in tools:
            readme += f"- **{tool['name']}**: {tool.get('description', 'No description')}\n"
    
    return readme