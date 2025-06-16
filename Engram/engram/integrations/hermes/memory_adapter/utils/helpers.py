"""
Helper utilities for the Hermes Memory Adapter.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Union, Optional

from ..core.imports import logger


def format_conversation(content: Union[str, List[Dict[str, str]]]) -> str:
    """
    Format content as a conversation string.
    
    Args:
        content: Content string or list of message objects
        
    Returns:
        Formatted conversation string
    """
    if isinstance(content, list):
        try:
            # Format as conversation
            content_str = "\n".join([
                f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" 
                for msg in content
            ])
        except Exception as e:
            logger.error(f"Error formatting conversation: {e}")
            content_str = str(content)
    else:
        content_str = content
    
    return content_str


def generate_memory_id(namespace: str, content: str) -> str:
    """
    Generate a unique memory ID.
    
    Args:
        namespace: Namespace for the memory
        content: Content of the memory
        
    Returns:
        Unique memory ID
    """
    return f"{namespace}-{int(time.time())}-{hash(content) % 10000}"


def validate_namespace(namespace: str, valid_namespaces: List[str], 
                      compartments: Dict[str, Dict[str, Any]]) -> str:
    """
    Validate and normalize a namespace name.
    
    Args:
        namespace: Namespace to validate
        valid_namespaces: List of valid base namespaces
        compartments: Dictionary of compartment data
        
    Returns:
        Normalized namespace name (or "conversations" if invalid)
    """
    # Support compartment namespaces 
    if namespace.startswith("compartment-"):
        compartment_id = namespace[len("compartment-"):]
        if compartment_id not in compartments:
            logger.warning(f"Invalid compartment: {compartment_id}, using 'conversations'")
            return "conversations"
        return namespace
    elif namespace not in valid_namespaces:
        logger.warning(f"Invalid namespace: {namespace}, using 'conversations'")
        return "conversations"
    
    return namespace


def filter_forgotten_content(results: List[Dict[str, Any]], 
                            forgotten_items: List[str]) -> List[Dict[str, Any]]:
    """
    Filter out results containing forgotten content.
    
    Args:
        results: List of search results
        forgotten_items: List of forgotten content strings
        
    Returns:
        Filtered list of results
    """
    if not forgotten_items:
        return results
    
    filtered_results = []
    for result in results:
        should_include = True
        content = result.get("content", "")
        
        # Check if any forgotten item appears in this content
        for forgotten in forgotten_items:
            if forgotten.lower() in content.lower():
                # This memory contains forgotten information
                should_include = False
                logger.debug(f"Filtered out memory containing: {forgotten}")
                break
        
        if should_include:
            filtered_results.append(result)
    
    return filtered_results


def format_context(all_results: List[Dict[str, Any]], namespaces: List[str], 
                  compartments: Dict[str, Dict[str, Any]]) -> str:
    """
    Format search results into a context string.
    
    Args:
        all_results: List of results with namespace information
        namespaces: List of namespaces that were searched
        compartments: Dictionary of compartment data
        
    Returns:
        Formatted context string
    """
    if not all_results:
        return ""
    
    context_parts = ["### Memory Context\n"]
    
    for namespace in namespaces:
        namespace_results = [r for r in all_results if r["namespace"] == namespace]
        
        if namespace_results:
            if namespace == "conversations":
                context_parts.append(f"\n#### Previous Conversations\n")
            elif namespace == "thinking":
                context_parts.append(f"\n#### Thoughts\n")
            elif namespace == "longterm":
                context_parts.append(f"\n#### Important Information\n")
            elif namespace == "projects":
                context_parts.append(f"\n#### Project Context\n")
            elif namespace == "session":
                context_parts.append(f"\n#### Session Memory\n")
            elif namespace == "compartments":
                context_parts.append(f"\n#### Compartment Information\n")
            elif namespace.startswith("compartment-"):
                compartment_id = namespace[len("compartment-"):]
                compartment_name = compartments.get(compartment_id, {}).get("name", compartment_id)
                context_parts.append(f"\n#### Compartment: {compartment_name}\n")
            
            for i, result in enumerate(namespace_results):
                timestamp = result.get("metadata", {}).get("timestamp", "Unknown time")
                content = result.get("content", "")
                
                # Truncate long content
                if len(content) > 500:
                    content = content[:497] + "..."
                
                context_parts.append(f"{i+1}. {content}\n")
    
    return "\n".join(context_parts)