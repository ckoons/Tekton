#!/usr/bin/env python3
"""
Latent Reasoning Agent Runner for Ergon.

This module provides a specialized runner for executing AI agents with
latent space reasoning capabilities integrated with the Tekton framework.
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, Union
from datetime import datetime

from ergon.core.agents.runner import AgentRunner
from ergon.core.agents.latent_reasoning import LatentReasoningAgentRunner
from ergon.core.database.models import Agent, AgentExecution
from ergon.utils.config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ergon.core.agents.latent_runner")


def create_latent_agent_runner(
    agent: Agent,
    execution_id: Optional[int] = None,
    model_name: Optional[str] = None,
    temperature: float = 0.7,
    timeout: Optional[int] = None,
    timeout_action: str = "log"
) -> LatentReasoningAgentRunner:
    """
    Create an agent runner with latent reasoning capabilities.
    
    Args:
        agent: Agent to run
        execution_id: Optional execution ID for tracking
        model_name: Optional model name override
        temperature: Temperature for LLM
        timeout: Optional timeout in seconds for agent execution
        timeout_action: Action to take on timeout ('log', 'alarm', or 'kill')
        
    Returns:
        LatentReasoningAgentRunner instance
    """
    # Create the standard agent runner
    standard_runner = AgentRunner(
        agent=agent,
        execution_id=execution_id,
        model_name=model_name,
        temperature=temperature,
        timeout=timeout,
        timeout_action=timeout_action
    )
    
    # Wrap it with latent reasoning capabilities
    latent_runner = LatentReasoningAgentRunner(standard_runner)
    
    logger.info(f"Created latent reasoning runner for agent '{agent.name}' (ID: {agent.id})")
    return latent_runner


async def run_agent_with_latent_reasoning(
    agent_id_or_name: Union[int, str],
    input_text: str,
    model_name: Optional[str] = None,
    temperature: float = 0.7,
    interactive: bool = False,
    timeout: Optional[int] = None,
    timeout_action: str = "log"
) -> Dict[str, Any]:
    """
    Run an agent with latent reasoning capabilities.
    
    Args:
        agent_id_or_name: ID or name of the agent to run
        input_text: Input to send to the agent
        model_name: Optional model name override
        temperature: Temperature for LLM
        interactive: Whether to run in interactive mode
        timeout: Optional timeout in seconds for agent execution
        timeout_action: Action to take on timeout
        
    Returns:
        Dictionary with result and execution details
    """
    # Use the same database lookup logic from the main CLI
    from ergon.core.database.engine import get_db_session
    
    with get_db_session() as db:
        # Look up the agent by ID or name
        if isinstance(agent_id_or_name, int) or agent_id_or_name.isdigit():
            # Look up by ID
            agent = db.query(Agent).filter(Agent.id == int(agent_id_or_name)).first()
        else:
            # Look up by name
            agent = db.query(Agent).filter(Agent.name == agent_id_or_name).first()
        
        if not agent:
            return {"error": f"Agent {agent_id_or_name} not found"}
        
        # Create execution record
        execution = AgentExecution(
            agent_id=agent.id,
            input=input_text,
            started_at=datetime.now()
        )
        db.add(execution)
        db.commit()
        
        execution_id = execution.id
    
    start_time = datetime.now()
    
    try:
        # Create the latent reasoning runner
        runner = create_latent_agent_runner(
            agent=agent,
            execution_id=execution_id,
            model_name=model_name,
            temperature=temperature,
            timeout=timeout,
            timeout_action=timeout_action
        )
        
        # Run the agent
        response = await runner.run(input_text)
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Update execution record
        with get_db_session() as db:
            execution = db.query(AgentExecution).filter(AgentExecution.id == execution_id).first()
            if execution:
                execution.output = response
                execution.completed_at = datetime.now()
                execution.execution_time = execution_time
                execution.success = True
                db.commit()
        
        # Clean up resources
        await runner.cleanup()
        
        return {
            "result": response,
            "agent_id": agent.id,
            "agent_name": agent.name,
            "execution_id": execution_id,
            "execution_time": execution_time
        }
    except Exception as e:
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Update execution record with error
        with get_db_session() as db:
            execution = db.query(AgentExecution).filter(AgentExecution.id == execution_id).first()
            if execution:
                execution.error = str(e)
                execution.completed_at = datetime.now()
                execution.execution_time = execution_time
                execution.success = False
                db.commit()
        
        return {
            "error": str(e),
            "agent_id": agent.id,
            "agent_name": agent.name,
            "execution_id": execution_id,
            "execution_time": execution_time
        }