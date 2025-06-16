"""
Flow factory for Ergon.
"""

import logging
from typing import Dict, Any

from ergon.core.flow.base import BaseFlow
from ergon.core.flow.planning import PlanningFlow
from ergon.core.flow.types import FlowType

logger = logging.getLogger(__name__)


class FlowFactory:
    """Factory for creating flow instances"""
    
    @staticmethod
    def create_flow(flow_type: FlowType, agents: Dict[str, Any], **kwargs) -> BaseFlow:
        """
        Create a flow of the specified type
        
        Args:
            flow_type: Type of flow to create
            agents: Dictionary of agents to use in the flow
            **kwargs: Additional flow-specific parameters
            
        Returns:
            Flow instance
            
        Raises:
            ValueError: If the flow type is not supported
        """
        if flow_type == FlowType.PLANNING:
            logger.info(f"Creating planning flow with {len(agents)} agents")
            return PlanningFlow(agents, **kwargs)
        elif flow_type == FlowType.SIMPLE:
            # Simple flow is just a wrapper around a single agent
            if not agents:
                raise ValueError("Simple flow requires at least one agent")
            
            # Create a wrapper class that implements BaseFlow but just delegates to the agent
            class SimpleFlow(BaseFlow):
                def __init__(self, agents: Dict[str, Any], **kwargs):
                    super().__init__(agents, **kwargs)
                    self.flow_type = FlowType.SIMPLE
                    self.agent = list(agents.values())[0]  # Just use the first agent
                    
                async def execute(self, input_text: str) -> str:
                    """Execute the simple flow by delegating to the agent"""
                    return await self.agent.run(input_text)
            
            logger.info(f"Creating simple flow with agent: {list(agents.keys())[0]}")
            return SimpleFlow(agents, **kwargs)
        else:
            raise ValueError(f"Unsupported flow type: {flow_type}")