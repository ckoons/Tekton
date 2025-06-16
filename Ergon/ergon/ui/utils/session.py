"""
Session state management utilities for Ergon UI
"""

import streamlit as st
import sys
import os

# Add debug mode for easier troubleshooting
DEBUG = True

def debug(msg):
    """Print debug messages to stderr"""
    if DEBUG:
        print(f"DEBUG: {msg}", file=sys.stderr)

def navigate_to(page):
    """Navigate to a different page"""
    st.session_state.page = page

def check_authentication():
    """Check if the user is authenticated"""
    # If authentication is disabled, auto-authenticate
    if os.environ.get("ERGON_AUTHENTICATION", "true").lower() == "false":
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = True
            st.session_state.username = "DevUser"
        return True
    
    # Otherwise check authentication status
    if "authenticated" in st.session_state and st.session_state.authenticated:
        return True
    return False

def get_or_create_memory_service(agent_id):
    """Get or create a memory service for an agent"""
    from ergon.core.memory.service import MemoryService
    
    # Use session state to cache the memory service
    memory_key = f"memory_service_{agent_id}"
    
    if memory_key not in st.session_state:
        try:
            st.session_state[memory_key] = MemoryService(agent_id)
        except Exception as e:
            debug(f"Error creating memory service: {str(e)}")
            return None
    
    return st.session_state[memory_key]