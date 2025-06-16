"""
Tool registry for special agent types.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable, Union

# Configure logger
logger = logging.getLogger(__name__)

async def register_special_tools(
    agent_type: Optional[str],
    agent_id: str,
    agent_name: str,
    tools_dict: Dict[str, Callable]
) -> Dict[str, Callable]:
    """
    Register special tools based on agent type.
    
    Args:
        agent_type: Type of agent (e.g., "browser", "nexus", "mail")
        agent_id: Agent ID
        agent_name: Agent name
        tools_dict: Existing tools dictionary to add to
        
    Returns:
        Updated tools dictionary
    """
    if not agent_type:
        return tools_dict
    
    # Copy the input dictionary to avoid mutating it
    tools = tools_dict.copy()
    
    # Register mail tools
    if "mail" in agent_name.lower() or "email" in agent_name.lower():
        tools = await register_mail_tools(tools)
    
    # Register browser tools
    if "browser" in agent_name.lower() or agent_type == "browser":
        tools = await register_browser_tools(tools)
    
    # Register Nexus memory tools
    if agent_type == "nexus" or "nexus" in agent_name.lower():
        tools = await register_memory_tools(agent_id, tools)
    
    return tools


async def register_mail_tools(tools_dict: Dict[str, Callable]) -> Dict[str, Callable]:
    """
    Register mail tools.
    
    Args:
        tools_dict: Existing tools dictionary to add to
        
    Returns:
        Updated tools dictionary
    """
    try:
        from ergon.core.agents.mail.tools import register_mail_tools as _register_mail_tools
        mail_tools = _register_mail_tools({})
        tools_dict.update(mail_tools)
        logger.info(f"Registered mail tools: {list(mail_tools.keys())}")
    except ImportError as e:
        logger.error(f"Failed to import mail tools: {str(e)}")
    
    return tools_dict


async def register_browser_tools(tools_dict: Dict[str, Callable]) -> Dict[str, Callable]:
    """
    Register browser tools.
    
    Args:
        tools_dict: Existing tools dictionary to add to
        
    Returns:
        Updated tools dictionary
    """
    try:
        from ergon.core.agents.browser.handler import BrowserToolHandler
        from ergon.core.agents.browser.tools import BROWSER_TOOLS
        
        # Initialize browser tool handler
        browser_handler = BrowserToolHandler()
        
        # Create async wrapper function for each browser tool
        for tool in BROWSER_TOOLS:
            tool_name = tool["name"]
            
            # Create a closure to capture the tool name
            async def browser_tool_wrapper(tool_name=tool_name, **kwargs):
                logger.info(f"Executing browser tool: {tool_name} with args: {kwargs}")
                return await browser_handler.execute_tool(tool_name, kwargs)
            
            # Add wrapper function to tools with the correct name
            tools_dict[tool_name] = browser_tool_wrapper
        
        logger.info(f"Registered browser tools: {list(BROWSER_TOOLS)}")
    except ImportError as e:
        logger.error(f"Failed to import browser tools: {str(e)}")
    
    return tools_dict


async def register_memory_tools(agent_id: str, tools_dict: Dict[str, Callable]) -> Dict[str, Callable]:
    """
    Register memory tools for Nexus agents.
    
    Args:
        agent_id: Agent ID
        tools_dict: Existing tools dictionary to add to
        
    Returns:
        Updated tools dictionary
    """
    try:
        from ergon.core.memory.service import MemoryService
        
        # Create memory service
        memory_service = MemoryService(agent_id)
        
        # Define tool functions
        async def store_memory(key: str, value: str) -> str:
            """Store a memory for future reference."""
            try:
                message = {"role": "system", "content": value}
                success = await memory_service.add([message], user_id=key)
                
                if success:
                    return f"Successfully stored memory with key: {key}"
                else:
                    return f"Failed to store memory with key: {key}"
            except Exception as e:
                logger.error(f"Error in store_memory: {str(e)}")
                return f"Error storing memory: {str(e)}"
        
        async def retrieve_memory(query: str, limit: int = 3) -> str:
            """Search memories for relevant information."""
            try:
                memory_results = await memory_service.search(query, limit=limit)
                
                if not memory_results or not memory_results.get("results"):
                    return "No relevant memories found."
                
                response = "Found the following relevant memories:\n\n"
                for i, memory in enumerate(memory_results["results"]):
                    response += f"{i+1}. {memory['memory']}\n\n"
                
                return response
            except Exception as e:
                logger.error(f"Error in retrieve_memory: {str(e)}")
                return f"Error retrieving memories: {str(e)}"
        
        async def remember_interaction(user_message: str, agent_response: str) -> str:
            """Store an interaction in memory."""
            try:
                messages = [
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": agent_response}
                ]
                from datetime import datetime
                timestamp = datetime.now().isoformat()
                success = await memory_service.add(messages, user_id=f"interaction_{timestamp}")
                
                if success:
                    return "Interaction stored in memory successfully."
                else:
                    return "Failed to store interaction in memory."
            except Exception as e:
                logger.error(f"Error in remember_interaction: {str(e)}")
                return f"Error storing interaction: {str(e)}"
        
        # Add memory tools
        tools_dict["store_memory"] = store_memory
        tools_dict["retrieve_memory"] = retrieve_memory
        tools_dict["remember_interaction"] = remember_interaction
        
        logger.info("Registered memory tools for Nexus agent")
    except ImportError as e:
        logger.error(f"Failed to load memory service: {str(e)}")
    except Exception as e:
        logger.error(f"Error initializing memory tools: {str(e)}")
    
    return tools_dict