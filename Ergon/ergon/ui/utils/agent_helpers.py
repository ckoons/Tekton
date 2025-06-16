"""
Agent creation and management helpers for UI
"""

import streamlit as st
import asyncio
from typing import Dict, Any, Optional, List

from ergon.core.agents.generator import create_agent
from ergon.core.database.engine import get_db_session
from ergon.core.database.models import Agent
from ergon.utils.config.settings import settings

def get_all_agents() -> List[Dict[str, Any]]:
    """
    Get all agents in the system.
    
    Returns:
        List of dictionaries containing agent information
    """
    try:
        with get_db_session() as db:
            agents = db.query(Agent).all()
            return [
                {
                    "id": agent.id,
                    "name": agent.name,
                    "description": agent.description,
                    "type": agent.type or "standard",
                    "model_name": agent.model_name
                }
                for agent in agents
            ]
    except Exception as e:
        st.error(f"Error getting agents: {str(e)}")
        return []

def create_nexus_agent(name: str, description: str, model_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a memory-enabled Nexus agent.
    
    Args:
        name: Name of the agent
        description: Description of the agent
        model_name: Optional model name override
        
    Returns:
        Dict containing the created agent information
    """
    try:
        # Create agent with 'nexus' type
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Use default model if none specified
        if not model_name:
            model_name = settings.default_model.value
        
        # Create the agent
        agent_data = {
            "name": name,
            "description": description,
            "type": "nexus",
            "model_name": model_name
        }
        
        agent_id = loop.run_until_complete(create_agent(agent_data))
        loop.close()
        
        # Get the created agent
        with get_db_session() as db:
            agent = db.query(Agent).filter(Agent.id == agent_id).first()
            
        return {
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "type": agent.type,
            "success": True
        }
        
    except Exception as e:
        st.error(f"Error creating agent: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def delete_agent(agent_id: int) -> Dict[str, Any]:
    """
    Delete an agent by ID.
    
    Args:
        agent_id: ID of the agent to delete
        
    Returns:
        Dict containing success status and any error messages
    """
    try:
        with get_db_session() as db:
            agent = db.query(Agent).filter(Agent.id == agent_id).first()
            
            if not agent:
                return {
                    "success": False,
                    "error": f"Agent with ID {agent_id} not found"
                }
                
            db.delete(agent)
            db.commit()
            
            return {
                "success": True,
                "name": agent.name,
                "id": agent_id
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }