"""
Specialist Router for dynamic AI specialist allocation.

This module extends the model router to support dynamic AI specialist allocation
and routing based on specialist capabilities and task requirements.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

# Standard logging - removed debug_log import
from .model_router import ModelRouter
from .ai_specialist_manager import AISpecialistManager, AISpecialistConfig

logger = logging.getLogger(__name__)

@dataclass
class SpecialistTask:
    """Represents a task for specialist allocation."""
    task_id: str
    task_type: str
    requirements: List[str]
    context: Dict[str, Any]
    priority: str = "normal"
    
class SpecialistRouter(ModelRouter):
    """
    Extended model router that supports dynamic AI specialist allocation.
    
    This router can:
    - Allocate specialists based on task requirements
    - Route requests to specific AI specialists
    - Handle fallback routing when specialists are unavailable
    - Support dynamic specialist creation
    """
    
    def __init__(self, llm_client, budget_manager=None):
        """Initialize the specialist router."""
        super().__init__(llm_client, budget_manager)
        self.specialist_manager: Optional[AISpecialistManager] = None
        self.specialist_allocations: Dict[str, str] = {}  # task_id -> specialist_id
        
        logger.info("Initialized SpecialistRouter")
        
    def set_specialist_manager(self, specialist_manager: AISpecialistManager):
        """Set the AI specialist manager for dynamic allocation."""
        self.specialist_manager = specialist_manager
        logger.info("Specialist manager connected")
        
    async def allocate_specialist(self, task: SpecialistTask) -> Optional[str]:
        """
        Allocate an AI specialist for a given task.
        
        Args:
            task: Task requiring specialist allocation
            
        Returns:
            Specialist ID if allocated, None otherwise
        """
        if not self.specialist_manager:
            logger.warning("No specialist manager available")
            return None
            
        logger.info(f"Allocating specialist for task: {task.task_id}")
        
        # Find specialists with matching capabilities
        candidates = []
        for specialist_id, config in self.specialist_manager.specialists.items():
            # Check if specialist has required capabilities
            if any(req in config.capabilities for req in task.requirements):
                candidates.append((specialist_id, config))
                
        if not candidates:
            logger.warning(f"No specialists found for requirements: {task.requirements}")
            return None
            
        # Select best candidate based on:
        # 1. Number of matching capabilities
        # 2. Current status (prefer active specialists)
        # 3. Specialist type alignment
        
        best_specialist = None
        best_score = 0
        
        for specialist_id, config in candidates:
            score = 0
            
            # Score based on capability matches
            score += sum(1 for req in task.requirements if req in config.capabilities) * 10
            
            # Bonus for active specialists
            if config.status == "active":
                score += 5
                
            # Bonus for type alignment
            if task.task_type in config.specialist_type:
                score += 3
                
            if score > best_score:
                best_score = score
                best_specialist = specialist_id
                
        if best_specialist:
            # Ensure specialist is active
            if self.specialist_manager.specialists[best_specialist].status != "active":
                success = await self.specialist_manager.create_specialist(best_specialist)
                if not success:
                    logger.error(f"Failed to activate specialist: {best_specialist}")
                    return None
                    
            # Record allocation
            self.specialist_allocations[task.task_id] = best_specialist
            logger.info(f"Allocated specialist {best_specialist} for task {task.task_id}")
            return best_specialist
            
        return None
        
    async def route_to_specialist(
        self,
        specialist_id: str,
        message: str,
        context_id: str,
        system_prompt: Optional[str] = None,
        streaming: bool = False,
        options: Optional[Dict[str, Any]] = None
    ):
        """
        Route a request to a specific AI specialist.
        
        Args:
            specialist_id: ID of the specialist to route to
            message: User message
            context_id: Context ID for tracking
            system_prompt: Optional system prompt override
            streaming: Whether to stream response
            options: Additional options
            
        Returns:
            Response from the specialist
        """
        if not self.specialist_manager or specialist_id not in self.specialist_manager.specialists:
            logger.error(f"Unknown specialist: {specialist_id}")
            # Fall back to default routing
            return await self.route_request(
                message=message,
                context_id=context_id,
                streaming=streaming,
                override_config=options
            )
            
        config = self.specialist_manager.specialists[specialist_id]
        
        # Use specialist's model configuration
        model_config = config.model_config.copy()
        
        # Use specialist's system prompt if not overridden
        if not system_prompt:
            # Check in personality first (where ComponentSpecialistRegistry stores it)
            if hasattr(config, 'personality') and "system_prompt" in config.personality:
                system_prompt = config.personality["system_prompt"]
            # Fall back to options if available
            elif "system_prompt" in model_config.get("options", {}):
                system_prompt = model_config["options"]["system_prompt"]
            
        # Merge any additional options
        if options:
            model_config["options"] = {**model_config.get("options", {}), **options}
            
        # Add specialist context
        model_config["options"]["specialist_id"] = specialist_id
        model_config["options"]["component"] = config.component_id
        
        logger.info(f"Routing to specialist {specialist_id} with model {model_config.get('model')}")
        
        # Route through parent model router with specialist config
        return await self.route_request(
            message=message,
            context_id=context_id,
            component=config.component_id,
            system_prompt=system_prompt,
            streaming=streaming,
            override_config=model_config
        )
        
    async def create_dynamic_specialist(
        self, 
        specialist_type: str,
        requirements: List[str],
        task_context: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create a dynamic specialist for specific requirements.
        
        Args:
            specialist_type: Type of specialist needed
            requirements: Required capabilities
            task_context: Context for specialist creation
            
        Returns:
            New specialist ID if created, None otherwise
        """
        if not self.specialist_manager:
            return None
            
        # Generate dynamic specialist ID
        import uuid
        specialist_id = f"AI({len(self.specialist_manager.specialists) + 1})-{specialist_type}-{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Creating dynamic specialist: {specialist_id}")
        
        # Determine model based on complexity
        if "complex_analysis" in requirements or "strategic_planning" in requirements:
            model = "claude-3-opus-20240229"
            max_tokens = 4000
        elif "quick_response" in requirements or "simple_task" in requirements:
            model = "claude-3-haiku-20240307"
            max_tokens = 2000
        else:
            model = "claude-3-sonnet-20240229"
            max_tokens = 3000
            
        # Create specialist configuration
        config = AISpecialistConfig(
            specialist_id=specialist_id,
            specialist_type=specialist_type,
            component_id="dynamic",
            model_config={
                "provider": "anthropic",
                "model": model,
                "options": {
                    "temperature": 0.4,
                    "max_tokens": max_tokens,
                    "system_prompt": f"You are a dynamic AI specialist focused on {specialist_type}. Your capabilities include: {', '.join(requirements)}."
                }
            },
            personality={
                "role": f"Dynamic {specialist_type} Specialist",
                "traits": ["adaptive", "focused", "efficient"],
                "communication_style": "clear and task-oriented"
            },
            capabilities=requirements
        )
        
        # Add to specialist manager
        self.specialist_manager.specialists[specialist_id] = config
        
        # Create and activate specialist
        success = await self.specialist_manager.create_specialist(specialist_id)
        
        if success:
            logger.info(f"Dynamic specialist {specialist_id} created successfully")
            return specialist_id
        else:
            # Remove failed specialist
            del self.specialist_manager.specialists[specialist_id]
            return None
            
    def get_specialist_for_component(self, component_id: str) -> Optional[str]:
        """
        Get the primary specialist for a component.
        
        Args:
            component_id: Component ID
            
        Returns:
            Specialist ID if found
        """
        if not self.specialist_manager:
            return None
            
        for specialist_id, config in self.specialist_manager.specialists.items():
            if config.component_id == component_id and config.status == "active":
                return specialist_id
                
        return None
        
    def get_model_for_specialist(self, specialist_type: str) -> str:
        """
        Get the appropriate model for a specialist type.
        
        Args:
            specialist_type: Type of specialist (e.g., "rhetor-orchestrator")
            
        Returns:
            Model name
        """
        # Map specialist types to appropriate models
        model_mapping = {
            "rhetor-orchestrator": "claude-3-opus-20240229",      # Meta-AI needs highest capability
            "engram-memory": "claude-3-haiku-20240307",          # Memory/context can use efficient model
            "apollo-coordinator": "claude-3-sonnet-20240229",    # Executive coordination needs balance
            "telos-analyst": "claude-3-haiku-20240307",          # Analysis can be efficient
            "prometheus-strategist": "claude-3-sonnet-20240229", # Strategy needs good reasoning
            "hermes-messenger": "claude-3-haiku-20240307"        # Messaging can be efficient
        }
        
        # Check if Anthropic Max is enabled
        if os.environ.get("ANTHROPIC_MAX_ACCOUNT", "false").lower() == "true":
            # Use best models when in Max mode
            if specialist_type == "rhetor-orchestrator":
                return "claude-3-opus-20240229"
            else:
                return "claude-3-sonnet-20240229"
        
        # Return mapped model or default to Sonnet
        return model_mapping.get(specialist_type, "claude-3-sonnet-20240229")