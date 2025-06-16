"""
Mock function calling implementation.
"""

import os
import re
import json
import logging
from typing import Dict, List, Any, Optional

# Configure logger
logger = logging.getLogger(__name__)

async def mock_tool_calling(
    llm_client: Any,
    messages: List[Dict[str, str]],
    tool_definitions: List[Dict[str, Any]],
    user_input: str
) -> Dict[str, Any]:
    """
    Mock function calling until we implement it in the LLM client.
    
    In a real implementation, we would use the LLM's function calling API.
    
    Args:
        llm_client: LLM client
        messages: Messages to send to the LLM
        tool_definitions: List of tool definitions
        user_input: Original user input
        
    Returns:
        Response with optional function call
    """
    # Extract tool names for the prompt
    tool_names = [tool["function"]["name"] for tool in tool_definitions]
    tool_descriptions = [f"{tool['function']['name']}: {tool['function']['description']}" for tool in tool_definitions]
    
    tool_prompt = f"""Available tools: {', '.join(tool_names)}

Tool descriptions:
{os.linesep.join(tool_descriptions)}

To use a tool, respond with a JSON object with this format: 
{{"function_call": {{"name": "tool_name", "arguments": {{"arg1": "value1"}}}}}}

If you don't need to use a tool, respond with your regular text answer."""
    
    # Add tool instructions to the system message
    system_message_with_tools = f"{messages[0]['content']}\n\n{tool_prompt}"
    messages_with_tools = [{"role": "system", "content": system_message_with_tools}] + messages[1:]
    
    # Check if we're dealing with a GitHub agent request
    if any(tool["function"]["name"].startswith("list_repositories") for tool in tool_definitions):
        github_tool = handle_github_tools(tool_definitions, user_input)
        if github_tool:
            return github_tool
    
    # Check if we're dealing with a Browser agent request
    elif any(tool["function"]["name"].startswith("browse_") for tool in tool_definitions):
        browser_tool = handle_browser_tools(tool_definitions, user_input)
        if browser_tool:
            return browser_tool
    
    # Generic approach for other tools
    for tool in tool_definitions:
        tool_name = tool["function"]["name"]
        tool_desc = tool["function"]["description"]
        
        # Simple heuristic to decide if tool might be needed
        if any(kw.lower() in user_input.lower() for kw in tool_name.split("_") + tool_desc.split()):
            # Simulate a function call response
            arguments = {}
            for param_name, param_def in tool["function"]["parameters"].get("properties", {}).items():
                if param_name == "query":
                    arguments[param_name] = user_input
                elif param_name == "input":
                    arguments[param_name] = user_input
                else:
                    # For repo_name, try to extract from the input
                    if param_name == "repo_name" and "repo" in user_input.lower():
                        parts = user_input.lower().split("repo ")
                        if len(parts) > 1:
                            repo_name = parts[1].split()[0].strip()
                            arguments[param_name] = repo_name
                    else:
                        # Use default for required parameters
                        if param_name in tool["function"]["parameters"].get("required", []):
                            arguments[param_name] = f"default_{param_name}"
            
            return {
                "function_call": {
                    "name": tool_name,
                    "arguments": json.dumps(arguments)
                }
            }
    
    # If no tool needed, get regular completion
    try:
        response = await llm_client.acomplete(messages)
        return {"content": response}
    except Exception as e:
        # Fallback response if something goes wrong
        return {"content": f"I'm having trouble processing your request. Please try asking in a different way. Error: {str(e)}"}


def handle_github_tools(tool_definitions: List[Dict[str, Any]], user_input: str) -> Optional[Dict[str, Any]]:
    """
    Handle GitHub tools based on user input.
    
    Args:
        tool_definitions: List of tool definitions
        user_input: User input
        
    Returns:
        Function call response or None
    """
    for tool in tool_definitions:
        tool_name = tool["function"]["name"]
        
        if "list" in user_input.lower() and "repositories" in user_input.lower() and tool_name == "list_repositories":
            return {
                "function_call": {
                    "name": tool_name,
                    "arguments": json.dumps({"visibility": "all", "sort": "updated"})
                }
            }
        elif "create" in user_input.lower() and "repository" in user_input.lower() and tool_name == "create_repository":
            # Try to extract name from input
            name = user_input.split("called ")[-1].split()[0].strip() if "called " in user_input else "new-repo"
            return {
                "function_call": {
                    "name": tool_name,
                    "arguments": json.dumps({"name": name, "private": "private" in user_input.lower()})
                }
            }
    
    return None


def handle_browser_tools(tool_definitions: List[Dict[str, Any]], user_input: str) -> Optional[Dict[str, Any]]:
    """
    Handle browser tools based on user input.
    
    Args:
        tool_definitions: List of tool definitions
        user_input: User input
        
    Returns:
        Function call response or None
    """
    for tool in tool_definitions:
        tool_name = tool["function"]["name"]
        
        # Handle browse_navigate for URL navigation
        if tool_name == "browse_navigate" and "go to" in user_input.lower():
            # Extract URL from input
            url_pattern = r"go to\s+([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\/[^\s]*)?)"
            url_match = re.search(url_pattern, user_input, re.IGNORECASE)
            
            if url_match:
                url = url_match.group(1)
                if not url.startswith("http"):
                    url = "https://" + url
                
                logger.info(f"Extracted URL for navigation: {url}")
                return {
                    "function_call": {
                        "name": tool_name,
                        "arguments": json.dumps({"url": url})
                    }
                }
        
        # Handle get_text after navigation
        if tool_name == "browse_get_text" and any(x in user_input.lower() for x in ["content", "text", "title"]):
            return {
                "function_call": {
                    "name": tool_name,
                    "arguments": json.dumps({})
                }
            }
    
    return None