#!/usr/bin/env python3
"""
Command Processing for Ollama Bridge CLI
This module provides functions for processing special commands.
"""

from typing import Dict, Any, List, Tuple, Optional

from ..memory.handler import MemoryHandler

def process_special_command(command: str, memory_handler: MemoryHandler) -> Tuple[bool, Optional[str]]:
    """
    Process special commands entered by the user.
    
    Args:
        command: The command string
        memory_handler: Memory handler instance
        
    Returns:
        Tuple of (command_processed, message_to_display)
    """
    # Exit commands
    if command and command.lower() in ['exit', '/quit']:
        return True, "Exiting..."
        
    # Reset chat history
    elif command and command.lower() == '/reset':
        return True, "Chat history reset."
        
    # Turn off dialog mode
    elif command and command.lower() == '/dialog_off':
        memory_handler.dialog_mode = False
        memory_handler.dialog_target = None
        memory_handler.dialog_type = None
        return True, "\n[Dialog mode deactivated]"
        
    # Save to memory
    elif command and command.lower().startswith('/remember '):
        memory_text = command[10:]
        if hasattr(memory_handler, 'store_memory'):
            result = memory_handler.store_memory(memory_text)
            return True, f"Saved to memory: {memory_text}"
        else:
            return True, "Memory functions not available."
        
    # List recent memories
    elif command and command.lower() == '/memories':
        if hasattr(memory_handler, 'get_recent_memories'):
            recent_memories = memory_handler.get_recent_memories(5)
            message = "Recent memories:\n"
            for mem in recent_memories:
                content = mem.get("content", "")
                if content:
                    message += f"- {content}\n"
            return True, message
        else:
            return True, "Memory functions not available."
        
    # Search memories
    elif command and command.lower().startswith('/search '):
        query = command[8:]
        if hasattr(memory_handler, 'search_memories'):
            results = memory_handler.search_memories(query)
            message = f"Memory search results for '{query}':\n"
            for result in results:
                content = result.get("content", "")
                if content:
                    message += f"- {content}\n"
            return True, message
        else:
            return True, "Memory functions not available."
            
    # Not a special command
    return False, None
    
def display_help() -> str:
    """Return help text for user commands."""
    return """
Available Commands:
------------------
/quit or exit         - Exit the chat
/reset                - Reset chat history
/dialog_off           - Turn off dialog mode
/remember <text>      - Save text to memory
/memories             - List recent memories
/search <query>       - Search memories for a query
/help                 - Show this help message
"""