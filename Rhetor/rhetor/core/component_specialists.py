"""
Component-Specialist Mapping and Registry.

This module manages the mapping between Tekton components and their dedicated AI specialists.
Part of the Hephaestus-Rhetor UI Integration Sprint.
"""

import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from .ai_specialist_manager import AISpecialistConfig
from .llm_client import LLMClient

logger = logging.getLogger(__name__)


@dataclass
class ComponentAIConfig:
    """Configuration for a component's AI assistant."""
    specialist_id: str
    model_preference: str
    ollama_fallback: str
    system_prompt: str
    personality: Dict[str, Any]


class ComponentSpecialistRegistry:
    """Registry for component-specialist mappings."""
    
    def __init__(self, specialist_manager=None):
        self.specialist_manager = specialist_manager
        self.specialists = {}
        self.component_configs = self._load_component_configs()
        
    def _load_component_configs(self) -> Dict[str, ComponentAIConfig]:
        """Load default component AI configurations."""
        return {
            "rhetor": ComponentAIConfig(
                specialist_id="rhetor-orchestrator",
                model_preference="claude-3.5-sonnet-20240620",
                ollama_fallback="deepseek-r1:32b",
                system_prompt="You are Rhetor's orchestrator, managing LLM interactions, prompt templates, and context optimization. You have deep knowledge of all Rhetor capabilities including model management, prompt engineering, and AI orchestration.",
                personality={
                    "role": "Rhetor Orchestrator",
                    "traits": ["knowledgeable", "strategic", "technical", "helpful"],
                    "communication_style": "professional yet approachable"
                }
            ),
            "athena": ComponentAIConfig(
                specialist_id="athena-assistant", 
                model_preference="claude-3-haiku-20240307",
                ollama_fallback="qwen2.5-coder:7b",
                system_prompt="You are Athena's knowledge assistant, specializing in quick information retrieval and knowledge graph queries. You help users navigate and query the knowledge base efficiently.",
                personality={
                    "role": "Knowledge Assistant",
                    "traits": ["efficient", "precise", "knowledgeable"],
                    "communication_style": "concise and informative"
                }
            ),
            "budget": ComponentAIConfig(
                specialist_id="budget-assistant",
                model_preference="gpt-4",
                ollama_fallback="mixtral:latest",
                system_prompt="You are the Budget assistant, helping users optimize LLM costs and manage token usage efficiently. You provide insights on cost-effective model selection and usage patterns.",
                personality={
                    "role": "Budget Optimizer",
                    "traits": ["analytical", "cost-conscious", "practical"],
                    "communication_style": "data-driven and clear"
                }
            ),
            "engram": ComponentAIConfig(
                specialist_id="engram-assistant",
                model_preference="claude-3-sonnet-20240229",
                ollama_fallback="llama3.3:70b",
                system_prompt="You are Engram's memory assistant, helping manage persistent memory, context, and information retrieval. You excel at organizing and recalling information effectively.",
                personality={
                    "role": "Memory Manager",
                    "traits": ["organized", "detail-oriented", "reliable"],
                    "communication_style": "structured and thorough"
                }
            ),
            "apollo": ComponentAIConfig(
                specialist_id="apollo-assistant",
                model_preference="gpt-4",
                ollama_fallback="codestral:22b", 
                system_prompt="You are Apollo's assistant, focused on attention management, prediction, and executive coordination. You help prioritize tasks and predict outcomes.",
                personality={
                    "role": "Executive Coordinator",
                    "traits": ["strategic", "predictive", "decisive"],
                    "communication_style": "executive and action-oriented"
                }
            ),
            "prometheus": ComponentAIConfig(
                specialist_id="prometheus-assistant",
                model_preference="claude-3-opus-20240229",
                ollama_fallback="deepseek-r1:32b",
                system_prompt="You are Prometheus's planning assistant, specializing in strategic analysis, project planning, and long-term vision. You help break down complex goals into actionable plans.",
                personality={
                    "role": "Strategic Planner",
                    "traits": ["visionary", "analytical", "methodical"],
                    "communication_style": "strategic and comprehensive"
                }
            )
        }
    
    async def ensure_specialist(self, component_id: str) -> Optional[AISpecialistConfig]:
        """Create or retrieve specialist for component."""
        if component_id not in self.component_configs:
            logger.warning(f"No AI configuration for component: {component_id}")
            return None
            
        config = self.component_configs[component_id]
        
        # Check if specialist already exists
        if config.specialist_id in self.specialists:
            specialist = self.specialists[config.specialist_id]
            if specialist.status == "active":
                return specialist
                
        # Create new specialist configuration
        specialist_config = AISpecialistConfig(
            specialist_id=config.specialist_id,
            specialist_type=f"{component_id}-specialist",
            component_id=component_id,
            model_config={
                "provider": "auto",
                "model": config.model_preference,
                "fallback_model": config.ollama_fallback,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            },
            personality={
                "role": config.personality["role"],
                "traits": config.personality["traits"],
                "system_prompt": config.system_prompt,
                "communication_style": config.personality["communication_style"]
            },
            capabilities=self._get_component_capabilities(component_id),
            status="active"
        )
        
        # Register with specialist manager if available
        if self.specialist_manager:
            self.specialist_manager.specialists[config.specialist_id] = specialist_config
            logger.info(f"Registered specialist {config.specialist_id} for component {component_id}")
        
        self.specialists[config.specialist_id] = specialist_config
        return specialist_config
    
    def _get_component_capabilities(self, component_id: str) -> list:
        """Get capabilities for a component specialist."""
        capabilities_map = {
            "rhetor": ["llm_management", "prompt_engineering", "context_optimization", "model_selection"],
            "athena": ["knowledge_query", "graph_navigation", "information_retrieval", "entity_search"],
            "budget": ["cost_analysis", "token_optimization", "model_comparison", "usage_tracking"],
            "engram": ["memory_storage", "context_management", "information_recall", "pattern_recognition"],
            "apollo": ["task_prioritization", "outcome_prediction", "attention_management", "coordination"],
            "prometheus": ["strategic_planning", "goal_decomposition", "timeline_creation", "risk_assessment"]
        }
        return capabilities_map.get(component_id, ["general_assistance"])
    
    def get_specialist_for_component(self, component_id: str) -> Optional[str]:
        """Get the specialist ID for a component."""
        config = self.component_configs.get(component_id)
        return config.specialist_id if config else None
    
    def list_component_specialists(self) -> Dict[str, str]:
        """List all component-specialist mappings."""
        return {
            comp_id: config.specialist_id 
            for comp_id, config in self.component_configs.items()
        }


# Global registry instance
component_specialist_registry = ComponentSpecialistRegistry()