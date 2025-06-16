"""
Agent services module for the Ergon chatbot.

Provides functions for agent discovery, selection, and execution.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional

# Import Ergon components
from ergon.core.agents.runner import AgentRunner
from ergon.core.database.engine import get_db_session
from ergon.core.database.models import Agent, AgentExecution, AgentMessage
from sqlalchemy import func

async def run_agent_async(
    agent_obj: Agent, 
    user_input: str, 
    execution_id: int,
    disable_memory: bool = False
) -> str:
    """Run the agent with the given input and return the response."""
    # Create runner
    runner = AgentRunner(
        agent=agent_obj,
        execution_id=execution_id
    )
    
    # Run agent
    if disable_memory:
        # Run in simple mode without memory tools
        response = await runner._run_simple(user_input)
    else:
        # Run normal mode with memory
        response = await runner.run(user_input)
    
    return response

def run_agent(
    agent_obj: Agent, 
    user_input: str, 
    execution_id: int,
    disable_memory: bool = False
) -> str:
    """Synchronous wrapper for running an agent."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        response = loop.run_until_complete(
            run_agent_async(agent_obj, user_input, execution_id, disable_memory)
        )
    finally:
        loop.close()
    
    return response

def get_agent_list() -> List[Dict[str, Any]]:
    """Get a list of all agents in the system."""
    with get_db_session() as db:
        agents = db.query(Agent).all()
        return [
            {
                "id": agent.id,
                "name": agent.name,
                "description": agent.description,
                "type": agent.type or "standard"
            }
            for agent in agents
        ]

def find_matching_agents(query: str) -> List[Dict[str, Any]]:
    """Find agents matching a search query in name, description or type."""
    from .constants import agent_metadata
    
    agents = get_agent_list()
    query = query.lower()
    
    # Score all agents based on query relevance
    scored_agents = []
    
    for agent in agents:
        score = 0
        agent_type = agent.get("type") or "standard"
        agent_name = agent.get("name", "").lower()
        agent_desc = agent.get("description", "").lower()
        
        # Get metadata for this agent type
        metadata = agent_metadata.get(agent_type, agent_metadata["standard"])
        
        # 1. Check keyword matches (primary criterion)
        for keyword in metadata["keywords"]:
            if keyword in query:
                score += 10  # Strong relevance for keyword matches
        
        # 2. Check name matches
        if query in agent_name:
            score += 8
        elif any(word in agent_name for word in query.split()):
            score += 5
            
        # 3. Check description matches
        if agent_desc and query in agent_desc:
            score += 6
        elif agent_desc and any(word in agent_desc for word in query.split()):
            score += 3
            
        # 4. Add metadata to agent for better descriptions
        agent_with_metadata = agent.copy()
        agent_with_metadata["capabilities"] = metadata["capabilities"]
        agent_with_metadata["type_description"] = metadata["desc"]
        agent_with_metadata["score"] = score
        
        if score > 0:
            scored_agents.append(agent_with_metadata)
    
    # Sort by score (highest first)
    scored_agents.sort(key=lambda a: a["score"], reverse=True)
    
    # Return top matches or all if few
    return scored_agents[:5] if len(scored_agents) > 5 else scored_agents

def find_agent_by_name_or_id(agent_identifier: str) -> Optional[Agent]:
    """Find an agent by ID or name."""
    try:
        agent_id = int(agent_identifier)
        id_lookup = True
    except ValueError:
        id_lookup = False
    
    with get_db_session() as db:
        if id_lookup:
            # Find by ID
            return db.query(Agent).filter(Agent.id == agent_id).first()
        else:
            # Find by exact name match first
            agent = db.query(Agent).filter(func.lower(Agent.name) == agent_identifier.lower()).first()
            
            # Try partial match if no exact match
            if agent is None:
                agent = db.query(Agent).filter(func.lower(Agent.name).contains(agent_identifier.lower())).first()
            
            return agent

def create_execution_id(agent_id: int) -> int:
    """Create a new execution ID for an agent."""
    with get_db_session() as db:
        execution = AgentExecution(
            agent_id=agent_id,
            started_at=datetime.now()
        )
        db.add(execution)
        db.commit()
        return execution.id