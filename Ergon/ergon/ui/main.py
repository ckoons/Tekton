"""
Main entry point for the Ergon UI
"""

import streamlit as st
import os
import sys
import traceback

# Import utility modules and styling
from .utils.session import debug, check_authentication
from .utils.styling import load_css

# Import UI components
from .components.navigation import create_sidebar_navigation

# Import pages (only when needed to avoid exposing module names in UI)
# These will be imported within the respective functions

def main():
    """Main application entry point"""
    # Apply custom styling
    load_css()
    
    # Add additional global styling
    st.markdown("""
    <style>
    /* Make the title bar more compact */
    h1 {
        margin-top: 0 !important;
        padding-top: 1rem !important;
    }
    
    /* Hide development-mode elements */
    .stException, .element-container:has(.stException) {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if "page" not in st.session_state:
        st.session_state.page = "Nexus"
        
    # Handle navigation redirects
    if "redirect_after_load" in st.session_state and st.session_state.redirect_after_load:
        st.session_state.redirect_after_load = False
        st.rerun()
    
    # Check authentication if enabled
    if os.environ.get("ERGON_AUTHENTICATION", "true").lower() == "true":
        if not check_authentication():
            from .pages.auth import login_page
            login_page()
            return
    
    # Create sidebar navigation
    create_sidebar_navigation()
    
    # Get current page from session state
    page = st.session_state.page
    
    # Render the selected page
    # Removed Home page - Nexus is now our primary page
                
    if page == "Create Agent":
        from .pages.agent_creation import agent_creation_page
        agent_creation_page()
        
    elif page == "Nexus":
        from .pages.chatbot import chatbot_interface
        chatbot_interface()
        
    elif page == "My Agents":
        st.title("My Agents")
        
        # Import agent helpers
        from .utils.agent_helpers import get_all_agents
        
        # Get all agents
        agents = get_all_agents()
        
        if not agents:
            st.info("You don't have any agents yet. Create your first agent using the 'Create Agent' page.")
        else:
            st.write(f"You have {len(agents)} agent(s) available:")
            
            # Display agents by type
            agent_types = {}
            for agent in agents:
                agent_type = agent.get("type") or "standard"
                if agent_type not in agent_types:
                    agent_types[agent_type] = []
                agent_types[agent_type].append(agent)
            
            # Create tabs for each agent type
            if agent_types:
                tabs = st.tabs(list(agent_types.keys()))
                
                for i, (agent_type, agents_of_type) in enumerate(agent_types.items()):
                    with tabs[i]:
                        for agent in agents_of_type:
                            with st.expander(f"{agent['name']} (ID: {agent['id']})"):
                                st.write(f"**Description:** {agent['description'] or 'No description'}")
                                st.write(f"**Type:** {agent_type}")
                                
                                # Add actions
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button(f"Use in Nexus", key=f"use_{agent['id']}"):
                                        # Store agent selection in session state
                                        st.session_state.selected_agent = agent
                                        st.session_state.page = "Nexus"
                                        st.session_state.redirect_after_load = True
                                
                                with col2:
                                    if st.button(f"Delete", key=f"delete_{agent['id']}"):
                                        st.session_state.delete_agent_id = agent["id"]
                                        st.session_state.delete_agent_name = agent["name"]
                                        st.session_state.confirm_delete = True
            
            # Handle agent deletion
            if "confirm_delete" in st.session_state and st.session_state.confirm_delete:
                st.warning(f"Are you sure you want to delete agent '{st.session_state.delete_agent_name}'? This action cannot be undone.")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes, delete"):
                        from .utils.agent_helpers import delete_agent
                        result = delete_agent(st.session_state.delete_agent_id)
                        
                        if result.get("success", False):
                            st.success(f"Agent '{result.get('name')}' deleted successfully.")
                        else:
                            st.error(f"Error deleting agent: {result.get('error', 'Unknown error')}")
                        
                        # Clear delete confirmation state
                        st.session_state.confirm_delete = False
                        st.session_state.pop("delete_agent_id", None)
                        st.session_state.pop("delete_agent_name", None)
                        st.session_state.redirect_after_load = True
                
                with col2:
                    if st.button("No, cancel"):
                        # Clear delete confirmation state
                        st.session_state.confirm_delete = False
                        st.session_state.pop("delete_agent_id", None)
                        st.session_state.pop("delete_agent_name", None)
        
    elif page == "Documentation":
        from .pages.documentation import documentation_page
        documentation_page()
        
    else:
        st.error(f"Unknown page: {page}")