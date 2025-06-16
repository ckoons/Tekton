"""
Agent creation page for Ergon UI
"""

import streamlit as st
import json
import os
from datetime import datetime
from ..utils.session import debug, navigate_to

# Import Ergon modules
from ergon.core.database.engine import get_db_session
from ergon.core.database.models import Agent, AgentTool
from ergon.core.agents.generator import generate_agent

def agent_creation_page():
    """Display the agent creation page"""
    st.title("Create Agent")
    
    with st.form("create_agent_form"):
        # Basic agent information
        st.subheader("Basic Information")
        agent_name = st.text_input("Agent Name", placeholder="My Assistant")
        agent_description = st.text_area("Description", placeholder="A helpful assistant that can perform various tasks")
        
        # Agent type selection
        st.subheader("Agent Type")
        agent_type = st.selectbox(
            "Agent Type", 
            options=["standard", "github", "mail", "browser", "nexus"],
            format_func=lambda x: {
                "standard": "Standard Assistant",
                "github": "GitHub Agent",
                "mail": "Email Agent",
                "browser": "Web Browser Agent",
                "nexus": "Memory-Enabled Agent"
            }.get(x, x)
        )
        
        # Agent model selection
        st.subheader("Model Configuration")
        model_options = ["gpt-4o-mini", "gpt-4o", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
        selected_model = st.selectbox("Model", options=model_options)
        
        # Agent tools
        st.subheader("Tools")
        # Default tools based on agent type
        default_tools = {
            "standard": ["search", "calculator", "websearch"],
            "github": ["repos", "issues", "pull_requests"],
            "mail": ["read_mail", "send_mail", "search_mail"],
            "browser": ["navigate", "click", "type", "extract"],
            "nexus": ["memory", "search", "calculator"]
        }
        
        available_tools = default_tools.get(agent_type, [])
        selected_tools = st.multiselect("Available Tools", available_tools, default=available_tools)
        
        # Advanced options (collapsible)
        with st.expander("Advanced Options"):
            temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
            timeout = st.number_input("Timeout (seconds)", min_value=10, max_value=300, value=60, step=10)
            
            if agent_type == "mail":
                email_provider = st.selectbox("Email Provider", ["Gmail", "Outlook", "Other"])
                if email_provider == "Other":
                    imap_server = st.text_input("IMAP Server")
                    smtp_server = st.text_input("SMTP Server")
            
            if agent_type == "github":
                github_token = st.text_input("GitHub Token (optional)", type="password")
            
            if agent_type == "browser":
                headless = st.checkbox("Run browser in headless mode", value=True)
        
        # Create button
        submit = st.form_submit_button("Create Agent")
        
        if submit:
            try:
                # Create the agent
                create_agent(
                    name=agent_name,
                    description=agent_description,
                    agent_type=agent_type,
                    model=selected_model,
                    tools=selected_tools
                )
                
                st.success(f"Agent '{agent_name}' created successfully!")
                
                # Set session state to navigate to the new agent
                navigate_to("MyAgents", created_agent=True)
                st.experimental_rerun()
                
            except Exception as e:
                st.error(f"Error creating agent: {str(e)}")

def create_agent(name, description, agent_type, model, tools):
    """Create a new agent in the database"""
    debug(f"Creating agent: {name} ({agent_type})")
    
    try:
        # Get database session
        session = get_db_session()
        
        # Create the agent
        agent = Agent(
            name=name,
            description=description,
            agent_type=agent_type,
            model=model,
            created_at=datetime.now()
        )
        
        session.add(agent)
        session.flush()  # Flush to get the agent ID
        
        # Add tools
        for tool_name in tools:
            tool = AgentTool(
                agent_id=agent.id,
                tool_name=tool_name,
                enabled=True
            )
            session.add(tool)
        
        # Generate the agent (includes creating LLM client, etc.)
        generate_agent(agent.id)
        
        session.commit()
        
        # Store the created agent ID in session state
        st.session_state.created_agent_id = agent.id
        
        return agent.id
        
    except Exception as e:
        # Rollback on error
        if 'session' in locals():
            session.rollback()
        debug(f"Error in create_agent: {str(e)}")
        raise