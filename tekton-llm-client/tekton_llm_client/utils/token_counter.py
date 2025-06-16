"""
Utility functions for token counting.
"""

import re
import logging
import tiktoken
from typing import List, Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

def get_encoder(model: str) -> Any:
    """
    Get the appropriate tokenizer for a model.
    
    Args:
        model: Model name or ID
        
    Returns:
        Tokenizer instance
    """
    try:
        if "gpt-4" in model:
            return tiktoken.encoding_for_model("gpt-4")
        elif "gpt-3.5-turbo" in model:
            return tiktoken.encoding_for_model("gpt-3.5-turbo")
        elif "claude" in model:
            # Use cl100k_base for Claude models (approximate)
            return tiktoken.get_encoding("cl100k_base")
        else:
            # Default to cl100k_base for unknown models
            return tiktoken.get_encoding("cl100k_base")
    except Exception as e:
        logger.warning(f"Failed to get encoder for model {model}: {str(e)}")
        # Fallback to simple estimation
        return None

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Count the number of tokens in a text string.
    
    Args:
        text: The text to count tokens in
        model: Model name for tokenization
        
    Returns:
        Number of tokens
    """
    encoder = get_encoder(model)
    
    if encoder:
        try:
            # Use the encoder
            return len(encoder.encode(text))
        except Exception as e:
            logger.warning(f"Error encoding text: {str(e)}")
            # Fall back to simple estimation
            pass
    
    # Simple approximation (about 4 chars per token)
    return len(text) // 4 + 1

def count_message_tokens(messages: List[Dict[str, str]], model: str = "gpt-4") -> Dict[str, int]:
    """
    Count tokens in a list of chat messages.
    
    Args:
        messages: List of message dictionaries with "role" and "content"
        model: Model name for tokenization
        
    Returns:
        Dictionary with token counts for prompt and total
    """
    total_tokens = 0
    
    for message in messages:
        # Count tokens in message content
        content_tokens = count_tokens(message.get("content", ""), model)
        
        # Add overhead for message format (role, metadata)
        # This is an approximation that varies by model
        overhead = 4  # Approximation for message overhead
        
        total_tokens += content_tokens + overhead
    
    # Add conversation overhead
    # (varies by model but typically 2-3 tokens)
    total_tokens += 3
    
    return {
        "prompt_tokens": total_tokens,
        "total_tokens": total_tokens
    }

def truncate_text_to_token_limit(text: str, max_tokens: int, model: str = "gpt-4") -> str:
    """
    Truncate text to fit within a token limit.
    
    Args:
        text: Text to truncate
        max_tokens: Maximum number of tokens
        model: Model name for tokenization
        
    Returns:
        Truncated text
    """
    encoder = get_encoder(model)
    
    if encoder:
        try:
            tokens = encoder.encode(text)
            if len(tokens) <= max_tokens:
                return text
                
            truncated_tokens = tokens[:max_tokens]
            return encoder.decode(truncated_tokens)
        except Exception as e:
            logger.warning(f"Error truncating with encoder: {str(e)}")
            # Fall back to character-based estimation
            pass
    
    # Simple approximation (about 4 chars per token)
    chars_per_token = 4
    max_chars = max_tokens * chars_per_token
    
    if len(text) <= max_chars:
        return text
        
    return text[:max_chars]

def optimize_messages_for_token_limit(
    messages: List[Dict[str, str]], 
    max_tokens: int,
    model: str = "gpt-4",
    keep_system_prompt: bool = True
) -> List[Dict[str, str]]:
    """
    Optimize a list of messages to fit within a token limit.
    
    Args:
        messages: List of message dictionaries with "role" and "content"
        max_tokens: Maximum number of tokens
        model: Model name for tokenization
        keep_system_prompt: Whether to always keep the system prompt
        
    Returns:
        Optimized list of messages
    """
    # Count tokens in all messages
    messages_with_tokens = []
    total_tokens = 0
    system_prompt = None
    
    for msg in messages:
        # Extract system prompt if needed
        if keep_system_prompt and msg.get("role") == "system":
            system_prompt = msg
            continue
            
        tokens = count_tokens(msg.get("content", ""), model)
        messages_with_tokens.append({
            "message": msg,
            "tokens": tokens
        })
        total_tokens += tokens
    
    # Add system prompt tokens if present
    system_tokens = 0
    if system_prompt:
        system_tokens = count_tokens(system_prompt.get("content", ""), model)
        total_tokens += system_tokens
    
    # If messages fit within limit, return as is
    if total_tokens <= max_tokens:
        if system_prompt:
            return [system_prompt] + [m["message"] for m in messages_with_tokens]
        return [m["message"] for m in messages_with_tokens]
    
    # Otherwise, we need to optimize
    optimized_messages = []
    
    # Always include system prompt if specified
    if system_prompt:
        optimized_messages.append(system_prompt)
        max_tokens -= system_tokens
    
    # Prioritize recent messages
    messages_with_tokens.reverse()  # Most recent first
    
    tokens_used = 0
    for msg_data in messages_with_tokens:
        if tokens_used + msg_data["tokens"] <= max_tokens:
            optimized_messages.append(msg_data["message"])
            tokens_used += msg_data["tokens"]
        else:
            # Not enough room for this message
            break
    
    # Restore original order (oldest first)
    optimized_messages.sort(key=lambda m: (
        0 if m.get("role") == "system" else
        messages.index(m) if m in messages else 999
    ))
    
    return optimized_messages