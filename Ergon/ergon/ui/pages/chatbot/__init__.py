"""
Chatbot interface for Ergon with memory and agent awareness.

Provides a Streamlit-based user interface for interacting with Ergon agents.
"""

from .session_management import initialize_session, initialize_page
from .sidebar import setup_sidebar
from .chat_interface import display_chat

def chatbot_interface():
    """Main function for the Nexus chatbot interface."""
    # Initialize the page title and styles
    initialize_page()
    
    # Initialize session state
    initialize_session()
    
    # Setup sidebar
    setup_sidebar()
    
    # Display chat interface
    display_chat()
    
# Export the main interface function
__all__ = ['chatbot_interface']