"""
Sidebar components for the Ergon chatbot.

Provides sidebar UI elements for agent selection and configuration.
"""

import streamlit as st
from typing import Dict, List, Any, Optional

from .agent_services import get_agent_list, find_agent_by_name_or_id

def setup_sidebar():
    """Set up the sidebar with configuration options."""
    with st.sidebar:
        st.header("Configuration")
        
        # Help section for commands
        with st.expander("Command Help"):
            st.markdown("""
            ### Chat Commands
            
            - **!rate** - Open feature importance rating tool
            - **!plan** - Generate and review implementation plan
            
            Type these commands in the chat input for additional functionality.
            """)
        
        # Get available memory-enabled agents
        agents = get_agent_list()
        
        # Filter to nexus agents if possible
        nexus_agents = [a for a in agents if a["type"] == "nexus"]
        
        # If no nexus agents, use all agents
        display_agents = nexus_agents if nexus_agents else agents
        
        # Agent selection
        agent_options = [f"{a['name']} (ID: {a['id']})" for a in display_agents]
        agent_options.insert(0, "Select an agent")
        
        selected_agent_str = st.selectbox(
            "Select Agent", 
            agent_options,
            index=0
        )
        
        # Create new nexus agent button
        if st.button("Create New Nexus Agent"):
            st.session_state.show_create_nexus = True
        
        # Create Nexus agent dialog
        if "show_create_nexus" in st.session_state and st.session_state.show_create_nexus:
            create_nexus_agent_ui()
        
        # Memory toggle
        disable_memory = st.checkbox("Disable Memory", value=False)
        st.session_state.disable_memory = disable_memory
        
        # Display warning if not a nexus agent
        if selected_agent_str != "Select an agent":
            agent_id = int(selected_agent_str.split("(ID: ")[1].split(")")[0])
            selected_agent = next((a for a in agents if a["id"] == agent_id), None)
            
            if selected_agent:
                st.session_state.selected_agent = selected_agent
                
                if selected_agent["type"] != "nexus":
                    st.warning("This is not a memory-enabled agent. Memory features will be limited.")
        
        # Feedback & Planning tools
        st.subheader("Feedback Tools")
        
        if st.button("Rate Feature Importance"):
            st.session_state.feature_rating_mode = True
            st.session_state.plan_review_mode = False
            st.session_state.plan_mode = False
        
        if "current_plan" in st.session_state and st.button("Review Implementation Plan"):
            st.session_state.plan_review_mode = True
            st.session_state.feature_rating_mode = False
            st.session_state.plan_mode = False

def create_nexus_agent_ui():
    """Display UI for creating a new Nexus agent."""
    with st.expander("Create New Nexus Agent", expanded=True):
        from ..utils.agent_helpers import create_nexus_agent
        
        new_agent_name = st.text_input("Agent Name", value="MemoryAgent")
        new_agent_desc = st.text_area(
            "Agent Description", 
            value="A memory-enabled agent for Ergon chatbot"
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("Create Agent"):
                if new_agent_name and new_agent_desc:
                    with st.spinner("Creating agent..."):
                        result = create_nexus_agent(new_agent_name, new_agent_desc)
                        
                        if result.get("success", False):
                            st.success(f"Agent '{new_agent_name}' created successfully!")
                            
                            # Refresh agent list
                            agents = get_agent_list()
                            nexus_agents = [a for a in agents if a["type"] == "nexus"]
                            display_agents = nexus_agents if nexus_agents else agents
                            agent_options = [f"{a['name']} (ID: {a['id']})" for a in display_agents]
                            agent_options.insert(0, "Select an agent")
                            
                            # Select the newly created agent
                            new_agent_id = result.get("id")
                            new_agent_option = next(
                                (opt for opt in agent_options if f"(ID: {new_agent_id})" in opt),
                                None
                            )
                            
                            if new_agent_option:
                                st.session_state.selected_agent = result
                            
                            st.session_state.show_create_nexus = False
                            st.experimental_rerun()
                        else:
                            st.error(f"Error creating agent: {result.get('error', 'Unknown error')}")
                else:
                    st.warning("Please provide both name and description")
        
        with col2:
            if st.button("Cancel"):
                st.session_state.show_create_nexus = False
                st.experimental_rerun()