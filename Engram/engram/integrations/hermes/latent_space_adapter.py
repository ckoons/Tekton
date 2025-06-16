#!/usr/bin/env python3
"""
Hermes Integration for Latent Space Reasoning

This module provides integration between Engram's latent space memory system and
Hermes's centralized services, enabling shared reasoning across components.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Callable, Awaitable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("engram.integrations.hermes.latent_space")

# Import base LatentMemorySpace
from engram.core.latent_space import LatentMemorySpace, ConvergenceDetector

# Import Hermes integrations
try:
    from engram.integrations.hermes.message_bus_adapter import MessageBusAdapter
    from engram.integrations.hermes.memory_adapter import HermesMemoryService
    HAS_HERMES = True
except ImportError:
    logger.warning("Hermes integrations not found, SharedLatentSpace will use fallback implementation")
    HAS_HERMES = False


class SharedLatentSpace(LatentMemorySpace):
    """
    Extension of LatentMemorySpace that enables cross-component sharing via Hermes.
    
    This class integrates with Hermes's message bus and memory services to share
    insights and coordinate reasoning processes across multiple components.
    """
    
    def __init__(self, 
                component_id: str, 
                namespace: str = "default",
                max_history: int = 20,
                data_dir: Optional[str] = None,
                shared_insights: bool = True):
        """
        Initialize a shared latent space with Hermes integration.
        
        Args:
            component_id: Unique identifier for the component
            namespace: Namespace for organizing thoughts
            max_history: Maximum iterations to store per thought
            data_dir: Directory for persisted thoughts
            shared_insights: Whether to share insights with other components
        """
        # Initialize base class
        super().__init__(
            component_id=component_id, 
            namespace=namespace,
            max_history=max_history,
            data_dir=data_dir
        )
        
        self.shared_insights = shared_insights
        self.shared_topic = f"tekton.latent_space.{namespace}"
        self.insight_handlers = []
        
        # Initialize Hermes integrations if available
        self.hermes_available = HAS_HERMES
        self.message_bus = None
        self.memory_service = None
        
        if self.hermes_available:
            try:
                # Initialize message bus
                self.message_bus = MessageBusAdapter(client_id=f"{component_id}_latent")
                
                # Initialize memory service for persisting shared insights
                self.memory_service = HermesMemoryService(client_id=f"{component_id}_latent")
                
                logger.info(f"Initialized Hermes integrations for SharedLatentSpace ({component_id})")
            except Exception as e:
                logger.error(f"Error initializing Hermes integrations: {e}")
                self.hermes_available = False
        
        # Initialize fallback mechanisms if Hermes is not available
        if not self.hermes_available:
            logger.info(f"Using fallback implementation for SharedLatentSpace ({component_id})")
            self.fallback_insights = []
    
    async def start(self):
        """
        Start the shared latent space services.
        
        This initializes connections to Hermes message bus and sets up
        insight sharing.
        
        Returns:
            Boolean indicating success
        """
        if self.hermes_available:
            try:
                # Start message bus
                await self.message_bus.start()
                
                # Subscribe to shared insights
                if self.shared_insights:
                    await self.message_bus.subscribe(
                        self.shared_topic, 
                        self._handle_shared_insight
                    )
                    
                logger.info(f"Started SharedLatentSpace services for {self.component_id}")
                return True
            except Exception as e:
                logger.error(f"Error starting SharedLatentSpace services: {e}")
                self.hermes_available = False
        
        return False
        
    async def close(self):
        """
        Clean up resources and close connections.
        """
        if self.hermes_available:
            try:
                if self.message_bus:
                    await self.message_bus.close()
                    
                if self.memory_service:
                    await self.memory_service.close()
                    
                logger.info(f"Closed SharedLatentSpace connections for {self.component_id}")
            except Exception as e:
                logger.error(f"Error closing SharedLatentSpace connections: {e}")
    
    async def _handle_shared_insight(self, message: Dict[str, Any]):
        """
        Handle insights shared by other components.
        
        Args:
            message: The received message with insight data
        """
        try:
            # Extract message content
            content = message.get("content", {})
            metadata = message.get("metadata", {})
            source_component = metadata.get("component", "unknown")
            
            # Skip our own insights
            if source_component == self.component_id:
                return
                
            # Log the insight
            thought_id = content.get("thought_id", "unknown")
            summary = content.get("summary", "No summary available")
            
            logger.info(f"Received insight from {source_component}: {summary[:100]}...")
            
            # Store the insight in our local collection
            insight = {
                "source_component": source_component,
                "thought_id": thought_id,
                "summary": summary,
                "content": content,
                "received_at": time.time(),
                "namespace": self.namespace
            }
            
            # Add to fallback insights if not using Hermes
            if not self.hermes_available:
                self.fallback_insights.append(insight)
            
            # Call any registered handlers
            for handler in self.insight_handlers:
                try:
                    await handler(insight)
                except Exception as e:
                    logger.error(f"Error in insight handler: {e}")
        except Exception as e:
            logger.error(f"Error handling shared insight: {e}")
    
    async def share_insight(self, 
                           thought_id: str, 
                           summary: Optional[str] = None,
                           additional_content: Optional[Dict[str, Any]] = None):
        """
        Share an insight from latent space with other components.
        
        Args:
            thought_id: Identifier for the thought to share
            summary: Optional summary of the insight (generated if not provided)
            additional_content: Optional additional content to include
            
        Returns:
            Dictionary with the shared insight data
        """
        if not self.shared_insights:
            logger.info(f"Insight sharing is disabled for {self.component_id}")
            return None
            
        if thought_id not in self.thoughts:
            raise ValueError(f"Thought {thought_id} not found")
            
        # Create an insight from the thought
        thought = self.thoughts[thought_id]
        
        # Generate summary if not provided
        if summary is None:
            # Extract first 200 characters
            content = thought["content"]
            summary = content[:200] + "..." if len(content) > 200 else content
        
        # Create shareable message
        insight = {
            "thought_id": thought_id,
            "summary": summary,
            "iteration": thought["metadata"].get("iteration", 0),
            "finalized": thought["metadata"].get("finalized", False),
            "namespace": self.namespace
        }
        
        # Add any additional content
        if additional_content:
            insight.update(additional_content)
        
        # Share via Hermes if available
        if self.hermes_available:
            try:
                # Share via message bus
                await self.message_bus.publish(
                    topic=self.shared_topic,
                    message=insight,
                    metadata={
                        "component": self.component_id,
                        "insight_type": "latent_space",
                        "timestamp": time.time()
                    }
                )
                
                # Persist in shared memory
                await self.memory_service.add(
                    content=f"LATENT INSIGHT: {summary}",
                    namespace="latent_insights",
                    metadata={
                        "thought_id": thought_id,
                        "component": self.component_id,
                        "namespace": self.namespace,
                        "insight": json.dumps(insight)
                    }
                )
                
                logger.info(f"Shared insight for thought {thought_id} via Hermes")
            except Exception as e:
                logger.error(f"Error sharing insight via Hermes: {e}")
                # Fall back to local storage
        
        logger.info(f"Created insight for thought {thought_id}")
        return insight
    
    async def register_insight_handler(self, 
                                     handler: Callable[[Dict[str, Any]], Awaitable[None]]):
        """
        Register a handler for incoming insights from other components.
        
        Args:
            handler: Async function to call when insights are received
            
        Returns:
            Boolean indicating success
        """
        try:
            self.insight_handlers.append(handler)
            logger.debug(f"Registered insight handler for {self.component_id}")
            return True
        except Exception as e:
            logger.error(f"Error registering insight handler: {e}")
            return False
    
    async def get_recent_insights(self, 
                                limit: int = 10, 
                                include_own: bool = False) -> List[Dict[str, Any]]:
        """
        Get recent insights from other components.
        
        Args:
            limit: Maximum number of insights to return
            include_own: Whether to include insights from this component
            
        Returns:
            List of insight data
        """
        if self.hermes_available:
            try:
                # Query memory service for insights
                results = await self.memory_service.search(
                    query="LATENT INSIGHT:",
                    namespace="latent_insights",
                    limit=limit * 2  # Request more to account for filtering
                )
                
                insights = []
                for result in results.get("results", []):
                    try:
                        metadata = result.get("metadata", {})
                        component = metadata.get("component", "")
                        
                        # Skip own insights if not including them
                        if not include_own and component == self.component_id:
                            continue
                            
                        # Extract insight data
                        insight_json = metadata.get("insight", "{}")
                        insight_data = json.loads(insight_json)
                        
                        insights.append({
                            "source_component": component,
                            "thought_id": metadata.get("thought_id", ""),
                            "namespace": metadata.get("namespace", ""),
                            "content": insight_data,
                            "received_at": metadata.get("timestamp", time.time())
                        })
                    except Exception as e:
                        logger.error(f"Error processing insight result: {e}")
                        continue
                
                # Sort by timestamp (newest first) and limit
                insights.sort(key=lambda x: x.get("received_at", 0), reverse=True)
                return insights[:limit]
            except Exception as e:
                logger.error(f"Error fetching insights from Hermes: {e}")
                # Fall back to local insights
        
        # Return fallback insights
        insights = self.fallback_insights.copy()
        
        # Filter own insights if needed
        if not include_own:
            insights = [i for i in insights if i.get("source_component") != self.component_id]
            
        # Sort by timestamp (newest first) and limit
        insights.sort(key=lambda x: x.get("received_at", 0), reverse=True)
        return insights[:limit]