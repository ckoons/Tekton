#!/usr/bin/env python3
"""
Latent Reasoning Agent integration for Ergon.

This module provides integration with the Tekton Latent Space Reflection Framework,
allowing Ergon agents to use continuous latent space reasoning.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional, Union, Callable, Awaitable
from datetime import datetime

from ergon.utils.config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ergon.core.agents.latent_reasoning")

# Import LatentReasoningMixin if available
try:
    from tekton.core.latent_reasoning import LatentReasoningMixin
    HAS_LATENT_REASONING = True
except ImportError:
    logger.warning("Tekton Latent Reasoning Framework not available, latent reasoning capabilities will be limited")
    HAS_LATENT_REASONING = False


class LatentReasoningAdapter:
    """
    Adapter that enables latent reasoning capabilities for Ergon agents.
    
    This adapter integrates with the Tekton Latent Space Reflection Framework to 
    provide continuous latent space reasoning capabilities to Ergon agents.
    """
    
    def __init__(self, agent_id: str, agent_name: str, namespace: str = "agents"):
        """
        Initialize the latent reasoning adapter.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_name: Name of the agent for display purposes
            namespace: Namespace for the agent's latent space
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.namespace = namespace
        self.component_id = f"ergon.agent.{agent_id}"
        self.initialized = False
        self.latent_space = None
        
        # Try to initialize latent reasoning
        if HAS_LATENT_REASONING:
            try:
                self.reasoning_mixin = LatentReasoningMixin()
                self.reasoning_mixin.component_id = self.component_id
                logger.info(f"Initialized latent reasoning mixin for agent {agent_name} (ID: {agent_id})")
            except Exception as e:
                logger.error(f"Error initializing latent reasoning mixin: {e}")
                self.reasoning_mixin = None
        else:
            self.reasoning_mixin = None
    
    async def initialize(self) -> bool:
        """
        Initialize the latent reasoning adapter.
        
        Returns:
            Boolean indicating success
        """
        if not HAS_LATENT_REASONING or self.reasoning_mixin is None:
            logger.warning(f"Latent reasoning not available for agent {self.agent_name}")
            return False
        
        try:
            # Initialize the latent space
            await self.reasoning_mixin.initialize_latent_space(
                namespace=self.namespace,
                shared=True,
                max_history=10  # Limit history to conserve resources
            )
            
            self.initialized = True
            self.latent_space = self.reasoning_mixin.latent_space
            
            logger.info(f"Initialized latent reasoning for agent {self.agent_name} (ID: {self.agent_id})")
            return True
        except Exception as e:
            logger.error(f"Error initializing latent reasoning: {e}")
            return False
    
    async def process_with_latent_reasoning(
        self, 
        input_text: str, 
        process_func: Callable[[str], Awaitable[str]],
        max_iterations: int = 3,
        complexity_threshold: float = 0.7,
        share_insights: bool = True
    ) -> Dict[str, Any]:
        """
        Process input with latent reasoning if the input is sufficiently complex.
        
        Args:
            input_text: The input to process
            process_func: Async function to process the input
            max_iterations: Maximum number of reasoning iterations
            complexity_threshold: Threshold for using latent reasoning
            share_insights: Whether to share insights with other components
            
        Returns:
            Dictionary with processing result and metadata
        """
        if not self.initialized:
            try:
                success = await self.initialize()
                if not success:
                    logger.warning(f"Using direct processing for {self.agent_name} (latent reasoning unavailable)")
                    result = await process_func(input_text)
                    return {"result": result, "latent_reasoning_used": False}
            except Exception as e:
                logger.error(f"Error initializing latent reasoning: {e}")
                result = await process_func(input_text)
                return {"result": result, "latent_reasoning_used": False}
        
        try:
            # Analyze complexity to determine whether to use latent reasoning
            complexity_score = await self._analyze_complexity(input_text)
            
            if complexity_score >= complexity_threshold:
                logger.info(f"Using latent reasoning for complex input (score: {complexity_score:.4f})")
                
                # Process with latent reasoning
                result = await self.reasoning_mixin.complexity_based_reasoning(
                    input_content=input_text,
                    process_func=process_func,
                    complexity_analyzer=self._analyze_complexity,
                    complexity_threshold=complexity_threshold,
                    max_iterations=max_iterations,
                    share_final_insight=share_insights,
                    metadata={
                        "agent_id": self.agent_id,
                        "agent_name": self.agent_name,
                        "content_type": "agent_input",
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                return result
            else:
                logger.info(f"Using direct processing for simple input (score: {complexity_score:.4f})")
                
                # Process directly
                result = await process_func(input_text)
                return {"result": result, "latent_reasoning_used": False}
        except Exception as e:
            logger.error(f"Error in latent reasoning processing: {e}")
            
            # Fall back to direct processing
            try:
                result = await process_func(input_text)
                return {"result": result, "latent_reasoning_used": False, "error": str(e)}
            except Exception as inner_e:
                logger.error(f"Error in fallback direct processing: {inner_e}")
                return {"result": f"Error processing input: {inner_e}", "latent_reasoning_used": False, "error": str(e)}
    
    async def _analyze_complexity(self, input_text: str) -> float:
        """
        Analyze the complexity of input text to determine if latent reasoning is needed.
        
        Args:
            input_text: The input text to analyze
            
        Returns:
            Complexity score between 0 and 1
        """
        # Simple heuristic based on:
        # 1. Length (longer inputs are more complex)
        # 2. Question complexity indicators
        # 3. Domain-specific terms
        
        # Length factor (normalized to range 0-1)
        length = len(input_text)
        length_factor = min(length / 500, 1.0)
        
        # Complexity indicators in questions
        complexity_indicators = [
            "why", "how", "explain", "compare", "contrast", "analyze", "evaluate",
            "what if", "impact", "difference", "relationship", "connection",
            "implications", "consequences", "advantages", "disadvantages",
            "pros and cons", "best way", "most effective", "optimal", "trade-off"
        ]
        
        indicator_count = sum(1 for indicator in complexity_indicators if indicator in input_text.lower())
        indicator_factor = min(indicator_count / 5, 1.0)
        
        # Multi-part queries (questions with multiple components)
        parts = input_text.count("?")
        parts_factor = min(parts / 3, 1.0)
        
        # Overall complexity score (weighted average)
        complexity_score = (length_factor * 0.3) + (indicator_factor * 0.5) + (parts_factor * 0.2)
        
        return complexity_score
    
    async def close(self):
        """Close latent reasoning resources."""
        if self.initialized and self.reasoning_mixin:
            try:
                await self.reasoning_mixin.close_latent_space()
                logger.info(f"Closed latent reasoning for agent {self.agent_name}")
            except Exception as e:
                logger.error(f"Error closing latent reasoning: {e}")


class LatentReasoningAgentRunner:
    """
    Agent runner with integrated latent reasoning capabilities.
    
    This class extends the standard agent runner with latent space reasoning,
    allowing for iterative refinement of responses.
    """
    
    def __init__(self, agent_runner):
        """
        Initialize the latent reasoning agent runner.
        
        Args:
            agent_runner: The standard agent runner to wrap
        """
        self.agent_runner = agent_runner
        
        # Configure latent reasoning adapter
        self.latent_adapter = LatentReasoningAdapter(
            agent_id=str(agent_runner.agent.id),
            agent_name=agent_runner.agent.name,
            namespace="ergon_agents"
        )
    
    async def run(self, input_text: str) -> str:
        """
        Run the agent with latent reasoning for complex inputs.
        
        Args:
            input_text: Input to send to the agent
            
        Returns:
            Agent's response
        """
        # Create the process function that will call the agent runner
        async def process_agent(prompt: str) -> str:
            return await self.agent_runner.arun(prompt)
        
        # Process with latent reasoning
        start_time = datetime.now()
        
        try:
            result = await self.latent_adapter.process_with_latent_reasoning(
                input_text=input_text,
                process_func=process_agent,
                max_iterations=3,
                complexity_threshold=0.7,
                share_insights=True
            )
            
            # Log performance information
            elapsed_time = (datetime.now() - start_time).total_seconds()
            iterations = result.get("iterations", 1)
            used_latent = result.get("latent_reasoning_used", False) or result.get("used_latent_reasoning", False)
            
            logger.info(f"Agent '{self.agent_runner.agent.name}' completed in {elapsed_time:.2f}s "
                       f"with {iterations} iteration(s) "
                       f"(latent reasoning: {'YES' if used_latent else 'NO'})")
            
            # Return the result
            return result.get("result", "I couldn't process your request.")
        except Exception as e:
            elapsed_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Error in latent reasoning agent after {elapsed_time:.2f}s: {str(e)}"
            logger.error(error_msg)
            
            # Fall back to standard processing
            try:
                return await self.agent_runner.run(input_text)
            except Exception as fallback_e:
                logger.error(f"Error in fallback processing: {str(fallback_e)}")
                return f"I encountered an error while processing your request: {str(fallback_e)}"
    
    async def arun(self, input_text: str) -> str:
        """
        Run the agent with latent reasoning asynchronously.
        
        This is an alias for run() to match the agent runner interface.
        
        Args:
            input_text: Input to send to the agent
            
        Returns:
            Agent's response
        """
        return await self.run(input_text)
    
    async def cleanup(self):
        """Clean up resources."""
        # Clean up latent reasoning resources
        await self.latent_adapter.close()
        
        # Clean up agent runner resources
        await self.agent_runner.cleanup()


def create_latent_reasoning_generator(agent_type: str = "standard"):
    """
    Create a generator function for latent-enabled agents.
    
    Args:
        agent_type: Type of agent to create
        
    Returns:
        Generator function for latent-enabled agents
    """
    from ergon.core.agents.generator import generate_agent
    
    def generate_latent_agent(
        name: str, 
        description: str,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate a latent-enabled agent.
        
        Args:
            name: Name of the agent
            description: Description of the agent
            model_name: Name of the model to use
            temperature: Temperature for generation
            tools: Optional list of tools for the agent
            
        Returns:
            Dictionary with agent details and files
        """
        # Create the base agent
        agent_data = generate_agent(
            name=name,
            description=description,
            model_name=model_name,
            temperature=temperature,
            tools=tools,
            agent_type=agent_type
        )
        
        # Enhance system prompt with latent reasoning capabilities
        latent_reasoning_description = """
I can use continuous latent space reasoning to handle complex questions. This means I'll:
1. Consider initial thoughts about your question
2. Refine my thinking through multiple iterations when needed
3. Provide more thorough and nuanced responses for complex questions
4. Share insights with other components in the system when appropriate

For simple questions, I'll respond directly. For complex ones, I'll think more deeply before answering.
"""
        
        # Add latent reasoning capabilities to system prompt
        system_prompt = agent_data["system_prompt"]
        if "Your goal is to provide" in system_prompt:
            # Insert after the first paragraph
            parts = system_prompt.split("\n\n", 1)
            if len(parts) > 1:
                system_prompt = f"{parts[0]}\n\n{latent_reasoning_description}\n\n{parts[1]}"
            else:
                system_prompt = f"{system_prompt}\n\n{latent_reasoning_description}"
        else:
            # Append to the end
            system_prompt = f"{system_prompt}\n\n{latent_reasoning_description}"
        
        agent_data["system_prompt"] = system_prompt
        agent_data["latent_reasoning"] = True
        
        return agent_data
    
    return generate_latent_agent


# Create generators for different agent types
generate_latent_agent = create_latent_reasoning_generator("standard")
generate_latent_nexus_agent = create_latent_reasoning_generator("nexus")
generate_latent_github_agent = create_latent_reasoning_generator("github")
generate_latent_browser_agent = create_latent_reasoning_generator("browser")
generate_latent_mail_agent = create_latent_reasoning_generator("mail")