"""
MCP capabilities for Rhetor.

This module defines the Model Context Protocol capabilities that Rhetor provides
for LLM management, prompt engineering, and context management.
"""

from typing import Dict, Any, List
from tekton.mcp.fastmcp.schema import MCPCapability


class LLMManagementCapability(MCPCapability):
    """Capability for managing LLM models and providers."""
    
    name: str = "llm_management"
    description: str = "Manage large language models, providers, and routing"
    version: str = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "get_available_models",
            "set_default_model",
            "get_model_capabilities", 
            "test_model_connection",
            "get_model_performance",
            "manage_model_rotation"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "llm_management",
            "provider": "rhetor",
            "requires_auth": False,
            "rate_limited": True,
            "supports_streaming": True,
            "model_types": ["text", "chat", "completion"],
            "provider_types": ["local", "api", "cloud"]
        }


class PromptEngineeringCapability(MCPCapability):
    """Capability for prompt engineering and template management."""
    
    name: str = "prompt_engineering"
    description: str = "Engineer and optimize prompts, manage templates"
    version: str = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "create_prompt_template",
            "optimize_prompt",
            "validate_prompt_syntax",
            "get_prompt_history",
            "analyze_prompt_performance",
            "manage_prompt_library"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "prompt_engineering",
            "provider": "rhetor",
            "requires_auth": False,
            "template_formats": ["jinja2", "mustache", "f-string"],
            "optimization_methods": ["iterative", "genetic", "manual"],
            "validation_types": ["syntax", "semantic", "performance"],
            "metrics": ["clarity", "specificity", "effectiveness", "token_efficiency"]
        }


class ContextManagementCapability(MCPCapability):
    """Capability for context and conversation management."""
    
    name: str = "context_management"
    description: str = "Manage conversation context and memory optimization"
    version: str = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "analyze_context_usage",
            "optimize_context_window",
            "track_context_history",
            "compress_context"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "context_management",
            "provider": "rhetor",
            "requires_auth": False,
            "context_types": ["conversation", "system", "user", "assistant"],
            "compression_methods": ["semantic", "statistical", "hybrid"],
            "optimization_strategies": ["window_sliding", "importance_weighting", "topic_clustering"],
            "tracking_metrics": ["token_count", "message_frequency", "topic_shifts"]
        }


class CIOrchestrationCapability(MCPCapability):
    """Capability for CI specialist orchestration and management."""
    
    name: str = "ci_orchestration"
    description: str = "Orchestrate and manage CI specialists for collaborative tasks"
    version: str = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "list_ai_specialists",
            "activate_ai_specialist",
            "send_message_to_specialist",
            "orchestrate_team_chat",
            "get_specialist_conversation_history",
            "configure_ai_orchestration"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "ai_orchestration",
            "provider": "rhetor",
            "requires_auth": False,
            "specialist_types": ["meta-orchestrator", "memory-specialist", "executive-coordinator", "strategic-planner"],
            "orchestration_modes": ["collaborative", "directive", "autonomous"],
            "communication_types": ["chat", "coordination", "task_assignment", "status_update"],
            "allocation_strategies": ["dynamic", "static", "hybrid"],
            "max_concurrent_specialists": 10
        }


# Export all capabilities
__all__ = [
    "LLMManagementCapability",
    "PromptEngineeringCapability",
    "ContextManagementCapability",
    "CIOrchestrationCapability"
]