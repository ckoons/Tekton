"""
Navigation components for Ergon UI
"""

import streamlit as st
from ..utils.session import debug, navigate_to
from ..utils.styling import display_logo

def create_sidebar_navigation():
    """Create the sidebar navigation"""
    with st.sidebar:
        display_logo()
        
        st.markdown("---")
        
        # Main navigation - Nexus as primary option
        if st.button("🧠 Nexus", use_container_width=True):
            st.session_state.page = "Nexus"
            st.session_state.redirect_after_load = True
        
        # My Agents before Create Agent
        if st.button("📋 My Agents", use_container_width=True):
            st.session_state.page = "My Agents"
            st.session_state.redirect_after_load = True
            
        if st.button("🤖 Create Agent", use_container_width=True):
            st.session_state.page = "Create Agent"
            st.session_state.redirect_after_load = True
            
        if st.button("📚 Documentation", use_container_width=True):
            st.session_state.page = "Documentation"
            st.session_state.redirect_after_load = True
            
        # User info and logout
        st.markdown("---")
        if "authenticated" in st.session_state and st.session_state.authenticated:
            st.markdown(f"**Logged in as:** {st.session_state.username}")
            if st.button("Logout", use_container_width=True):
                # Reset authentication state
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.redirect_after_load = True

def render_footer():
    """Render the footer component"""
    st.markdown("---")
    st.markdown(
        """
        <footer>
            <p>Ergon © 2025 | Version 1.0</p>
        </footer>
        """,
        unsafe_allow_html=True
    )