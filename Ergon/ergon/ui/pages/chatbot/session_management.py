"""
Session management for the Ergon chatbot.

Provides functions for initializing and managing session state.
"""

import streamlit as st
from typing import Dict, List, Any, Optional

from .constants import welcome_message

def initialize_session():
    """Initialize session state variables for the chatbot."""
    # Initialize main chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
        # Add default welcome message for faster startup
        st.session_state.messages.append({
            "role": "assistant", 
            "content": welcome_message
        })
        
        # Mark welcome as shown
        st.session_state.welcome_shown = True
    
    # Initialize execution ID for agent runs
    if "execution_id" not in st.session_state:
        st.session_state.execution_id = None
    
    # Initialize UI mode flags
    if "plan_mode" not in st.session_state:
        st.session_state.plan_mode = False
    
    if "feature_rating_mode" not in st.session_state:
        st.session_state.feature_rating_mode = False
    
    if "plan_review_mode" not in st.session_state:
        st.session_state.plan_review_mode = False
        
    # Initialize agent selection
    if "selected_agent" not in st.session_state:
        st.session_state.selected_agent = None
        
    # Initialize nexus agent creation flag
    if "show_create_nexus" not in st.session_state:
        st.session_state.show_create_nexus = False

def initialize_page():
    """Initialize page title and styles."""
    from .constants import custom_styles
    
    st.title("Ergon Nexus")
    st.markdown("*Your AI-powered assistant with memory capabilities*")
    
    # Apply custom styles
    st.markdown(custom_styles, unsafe_allow_html=True)

def add_message(role: str, content: str):
    """Add a message to the chat history."""
    st.session_state.messages.append({"role": role, "content": content})
    
    # For assistant messages, set pending response for display
    if role == "assistant":
        st.session_state.pending_response = content

def get_messages() -> List[Dict[str, str]]:
    """Get the current messages in the chat history."""
    return st.session_state.messages