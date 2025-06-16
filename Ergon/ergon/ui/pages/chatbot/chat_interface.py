"""
Chat interface for the Ergon chatbot.

Provides the main chat display and user interaction handling.
"""

import streamlit as st
import time
from typing import List, Dict, Any, Optional

from .agent_services import find_agent_by_name_or_id, run_agent, create_execution_id, find_matching_agents
from .ui_components import build_agent_recommendation
from .session_management import add_message
from .constants import sample_plan

def display_chat():
    """Display the chat interface and handle user inputs."""
    # Special modes handling
    if st.session_state.feature_rating_mode:
        from .ui_components import rate_feature_importance
        rate_feature_importance()
        
        if st.button("Return to Chat"):
            st.session_state.feature_rating_mode = False
        
        return
    
    if st.session_state.plan_review_mode and "current_plan" in st.session_state:
        from .ui_components import display_plan_review
        feedback = display_plan_review(st.session_state.current_plan)
        
        if st.button("Return to Chat"):
            st.session_state.plan_review_mode = False
        
        return
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # Display pending response if any
    if "pending_response" in st.session_state and st.session_state.pending_response:
        with st.chat_message("assistant"):
            st.markdown(st.session_state.pending_response)
        # Clear pending response after displaying
        st.session_state.pending_response = None
    
    # Input area - always allow input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to chat
        add_message("user", user_input)
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Process special commands
        if user_input.startswith("!plan"):
            handle_plan_command()
        elif user_input.startswith("!rate"):
            handle_rate_command()
        else:
            handle_normal_message(user_input)

def handle_plan_command():
    """Handle the !plan command - generates an implementation plan."""
    # Switch to plan mode
    st.session_state.plan_mode = True
    
    # Store the sample plan in session state
    st.session_state.current_plan = sample_plan
    
    # Store the response
    response = "I've created an implementation plan. You can review it using the 'Review Implementation Plan' button in the sidebar."
    
    # Add assistant message to chat
    add_message("assistant", response)
    
    # Enable plan review mode
    st.session_state.plan_review_mode = True
    st.experimental_rerun()

def handle_rate_command():
    """Handle the !rate command - opens the feature rating interface."""
    # Switch to feature rating mode
    st.session_state.feature_rating_mode = True
    
    # Store the response
    response = "Let's rate the importance of different features. I've opened the rating interface in the main area."
    
    # Add assistant message to chat
    add_message("assistant", response)
    
    st.experimental_rerun()

def handle_normal_message(user_input: str):
    """Handle normal user messages (not commands)."""
    # Check if an agent is selected
    if "selected_agent" not in st.session_state or not st.session_state.selected_agent:
        # Try to find a relevant agent based on the user's message
        matching_agents = find_matching_agents(user_input)
        
        # Build a helpful response with agent recommendations
        response = build_agent_recommendation(matching_agents)
        
        # Add response to chat history
        add_message("assistant", response)
        return
    
    # Find agent
    agent = find_agent_by_name_or_id(str(st.session_state.selected_agent["id"]))
    
    if not agent:
        # Store response if agent not found
        response = "Error: Agent not found. Please select a different agent or create a new one."
        add_message("assistant", response)
        return
    
    # Create or reuse execution_id
    if not st.session_state.execution_id:
        st.session_state.execution_id = create_execution_id(agent.id)
    
    # Show thinking indicator
    with st.chat_message("assistant"):
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown("Thinking...")
        
        try:
            # Get memory setting
            disable_memory = st.session_state.get("disable_memory", False)
            
            # Run the agent
            response = run_agent(
                agent, 
                user_input, 
                st.session_state.execution_id,
                disable_memory
            )
            
            # Add to chat history
            add_message("assistant", response)
            
            # Remove the thinking placeholder
            thinking_placeholder.empty()
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            
            # Add error to chat history
            add_message("assistant", error_msg)
            
            # Remove the thinking placeholder
            thinking_placeholder.empty()
            
            # Reset execution_id on error
            st.session_state.execution_id = None