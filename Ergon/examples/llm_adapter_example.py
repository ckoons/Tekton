#!/usr/bin/env python3
"""
Example of using the enhanced LLM adapter in Ergon.

This demonstrates how to use the tekton-llm-client based adapter
for various agent tasks and workflow planning.
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ergon.core.llm.adapter import LLMAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("llm_adapter_example")

async def agent_task_example():
    """Example of using the LLM adapter for agent task execution."""
    # Initialize the LLM adapter
    adapter = LLMAdapter()
    
    # Define a task for the agent
    task_description = """
    Analyze the provided product review dataset and identify the top 3 most common
    customer complaints. Create a summary of each complaint type and suggest
    potential solutions that could be implemented to address them.
    """
    
    # Context for the task
    context = """
    The dataset contains 1000 customer reviews for a smartphone product.
    Reviews are rated from 1-5 stars, with 1 being the lowest satisfaction.
    Approximately 30% of reviews are 3 stars or below.
    Many negative reviews mention battery life, camera quality in low light,
    and occasional software freezes.
    """
    
    # Constraints for the task
    constraints = """
    - Focus only on actionable complaints that the product team can address
    - Do not include complaints about pricing or shipping as these are handled by different teams
    - Prioritize issues that appear in multiple reviews rather than one-off problems
    """
    
    # Execute the task
    print("Executing agent task...")
    result = await adapter.execute_agent_task(
        task_description=task_description,
        context=context,
        constraints=constraints
    )
    
    print("\n=== Agent Task Execution Result ===")
    print(result)

async def workflow_planning_example():
    """Example of using the LLM adapter for workflow planning."""
    # Initialize the LLM adapter
    adapter = LLMAdapter()
    
    # Define a goal for the workflow
    goal = """
    Create a comprehensive product research report for a new smart home device,
    including competitive analysis, user needs assessment, and feature recommendations.
    """
    
    # Available agents for the workflow
    available_agents = """
    1. Data Collector Agent: Specializes in gathering information from various sources
    2. Analysis Agent: Focuses on interpreting data and identifying patterns
    3. User Research Agent: Specializes in understanding user needs and preferences
    4. Recommendation Agent: Generates actionable recommendations based on insights
    5. Report Generation Agent: Creates polished, well-structured documentation
    """
    
    # Constraints for the workflow
    constraints = """
    - The entire workflow must be completed within 48 hours
    - The final report should not exceed 20 pages
    - The analysis must include at least 5 competing products
    - All recommendations must be supported by data from the research
    """
    
    # Plan the workflow
    print("Planning workflow...")
    result = await adapter.plan_workflow(
        goal=goal,
        available_agents=available_agents,
        constraints=constraints
    )
    
    print("\n=== Workflow Planning Result ===")
    print(result)

async def memory_query_example():
    """Example of using the LLM adapter for memory queries."""
    # Initialize the LLM adapter
    adapter = LLMAdapter()
    
    # Define a query
    query = "What do we know about the client's requirements for the mobile app project?"
    
    # Retrieved memories (simulated)
    retrieved_memories = """
    Meeting transcript (March 15, 2025):
    Client emphasized the need for offline functionality in the app.
    They mentioned that many of their users work in areas with poor connectivity.
    
    Email from client (April 2, 2025):
    "We would like the app to support both iOS and Android, with a consistent UI across platforms."
    
    Requirements document excerpt (April 10, 2025):
    - User authentication must use biometric options when available
    - Data must be encrypted both in transit and at rest
    - The app should minimize battery usage when running in background
    
    Client feedback on prototype (April 22, 2025):
    "The navigation is confusing. We'd prefer a simpler tab-based interface with no more than 5 main sections."
    """
    
    # Query the memory
    print("Querying memory...")
    result = await adapter.query_memory(
        query=query,
        retrieved_memories=retrieved_memories
    )
    
    print("\n=== Memory Query Result ===")
    print(result)

async def agent_coordination_example():
    """Example of using the LLM adapter for agent coordination."""
    # Initialize the LLM adapter
    adapter = LLMAdapter()
    
    # Define a task
    task_description = """
    Build a machine learning pipeline to classify customer support tickets
    into appropriate categories and priority levels.
    """
    
    # Available agents
    agents = """
    1. Data Preprocessing Agent: Cleans and transforms text data, handles tokenization,
       and prepares features for model training.
    
    2. Model Training Agent: Specializes in selecting and training appropriate machine
       learning models for text classification tasks.
    
    3. Evaluation Agent: Assesses model performance using various metrics and can perform
       cross-validation and error analysis.
    
    4. Pipeline Integration Agent: Connects different components into a cohesive workflow
       and ensures data flows correctly between stages.
    """
    
    # Previous steps completed
    previous_steps = """
    1. Data Preprocessing Agent has cleaned the text data, removed duplicates,
       and performed basic tokenization.
    
    2. Data Preprocessing Agent has split the dataset into training (70%),
       validation (15%), and test (15%) sets.
    """
    
    # Current state
    current_state = """
    - We have 10,000 processed customer tickets ready for feature extraction
    - Each ticket contains the text content, timestamp, and customer ID
    - We need to classify tickets into 5 categories: Technical Issue, Billing Question,
      Account Management, Feature Request, and General Inquiry
    - We also need to assign priority: Low, Medium, High, or Critical
    """
    
    # Coordinate the agents
    print("Coordinating agents...")
    result = await adapter.coordinate_agents(
        task_description=task_description,
        agents=agents,
        previous_steps=previous_steps,
        current_state=current_state
    )
    
    print("\n=== Agent Coordination Result ===")
    print(result)

async def main():
    """Run all examples."""
    try:
        await agent_task_example()
        print("\n" + "="*60 + "\n")
        
        await workflow_planning_example()
        print("\n" + "="*60 + "\n")
        
        await memory_query_example()
        print("\n" + "="*60 + "\n")
        
        await agent_coordination_example()
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")

if __name__ == "__main__":
    asyncio.run(main())