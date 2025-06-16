"""
Chatbot interface for Ergon with memory and agent awareness.

This file provides backward compatibility with the refactored structure.
The implementation has been split into smaller modules for better maintainability.
"""

# Import the main interface function from the refactored module
from ergon.ui.pages.chatbot import chatbot_interface

# Re-export the main function for backward compatibility
__all__ = ['chatbot_interface']