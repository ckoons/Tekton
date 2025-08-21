"""Rhetor component implementation using StandardComponentBase."""
import logging
import os
from shared.env import TektonEnviron
from typing import List, Dict, Any

from shared.utils.standard_component import StandardComponentBase
from landmarks import architecture_decision, state_checkpoint, integration_point, danger_zone

logger = logging.getLogger(__name__)


@architecture_decision(
    title="LLM orchestration service",
    rationale="Centralize LLM interactions across Tekton with provider abstraction, budget management, and AI specialist routing",
    alternatives=["Direct LLM API calls per component", "External LLM gateway", "Single provider lock-in"],
    decision_date="2024-01-05"
)
@state_checkpoint(
    title="LLM service state",
    state_type="service",
    persistence=False,
    consistency_requirements="Stateless design with external state in Budget and Engram",
    recovery_strategy="Reconnect to providers, reload templates and specialists"
)
class RhetorComponent(StandardComponentBase):
    """Rhetor LLM orchestration and management component."""
    
    def __init__(self):
        super().__init__(component_name="rhetor", version="0.1.0")
        self.llm_client = None
        self.model_router = None
        self.ai_messaging_integration = None
        self.context_manager = None
        self.prompt_engine = None
        self.template_manager = None
        self.prompt_registry = None
        self.budget_manager = None
        self.anthropic_max_config = None
        self.mcp_bridge = None
        self.mcp_integration = None
        self.initialized = False
        
    @danger_zone(
        title="Complex initialization sequence",
        risk_level="high",
        risks=["Circular dependencies", "Service startup order", "Partial initialization state"],
        mitigations=["Delayed imports", "Try-catch blocks", "Graceful degradation"],
        review_required=True
    )
    async def _component_specific_init(self):
        """Initialize Rhetor-specific services."""
        # Import here to avoid circular imports
        from rhetor.core.llm_client import LLMClient
        from rhetor.core.model_router import ModelRouter
        from rhetor.core.context_manager import ContextManager
        from rhetor.core.prompt_engine import PromptEngine
        from rhetor.core.template_manager import TemplateManager
        from rhetor.core.prompt_registry import PromptRegistry
        from rhetor.core.budget_manager import BudgetManager
        from rhetor.core.anthropic_max_config import AnthropicMaxConfig
        
        try:
            # Initialize core components
            self.llm_client = LLMClient()
            await self.llm_client.initialize()
            logger.info("LLM client initialized successfully")
            
            # Initialize template manager first
            template_data_dir = self.global_config.get_data_dir('rhetor/templates')
            self.template_manager = TemplateManager(template_data_dir)
            logger.info("Template manager initialized")
            
            # Initialize prompt registry
            prompt_data_dir = self.global_config.get_data_dir('rhetor/prompts')
            self.prompt_registry = PromptRegistry(prompt_data_dir)
            logger.info("Prompt registry initialized")
            
            # Initialize enhanced context manager with token counting
            self.context_manager = ContextManager(llm_client=self.llm_client)
            logger.info("Initializing context manager...")
            await self.context_manager.initialize()
            logger.info("Context manager initialized successfully")
            
            # Initialize Anthropic Max configuration
            self.anthropic_max_config = AnthropicMaxConfig()
            logger.info(f"Anthropic Max configuration initialized - enabled: {self.anthropic_max_config.enabled}")
            
            # Initialize budget manager for cost tracking and budget enforcement
            self.budget_manager = BudgetManager()
            
            # Apply Anthropic Max budget override if enabled
            if self.anthropic_max_config.enabled:
                max_budget = self.anthropic_max_config.get_budget_override()
                if max_budget:
                    logger.info("Applying Anthropic Max budget override - unlimited tokens")
                    # Budget manager will still track usage but not enforce limits
            
            logger.info("Budget manager initialized")
            
            # Initialize model router with budget manager
            self.model_router = ModelRouter(self.llm_client, budget_manager=self.budget_manager)
            logger.info("Model router initialized")
            
            # AI specialist management is now handled by the AI Registry
            logger.info("Using AI Registry for specialist management")
            
            # AI messaging integration is deprecated - messaging now handled through AI Registry
            self.ai_messaging_integration = None
            logger.info("AI messaging handled through AI Registry")
            
            # Initialize prompt engine with template manager integration
            self.prompt_engine = PromptEngine(self.template_manager)
            logger.info("Prompt engine initialized")
            
            # Mark as initialized
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing Rhetor services: {e}")
            raise
    
    async def _component_specific_cleanup(self):
        """Cleanup Rhetor-specific resources."""
        # Cleanup AI messaging integration
        if self.ai_messaging_integration:
            try:
                await self.ai_messaging_integration.cleanup()
                logger.info("AI messaging integration cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up AI messaging integration: {e}")
        
        # Cleanup context manager
        if self.context_manager:
            try:
                await self.context_manager.cleanup()
                logger.info("Context manager cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up context manager: {e}")
        
        # Cleanup LLM client
        if self.llm_client:
            try:
                await self.llm_client.cleanup()
                logger.info("LLM client cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up LLM client: {e}")
        
        # Cleanup MCP bridge
        if self.mcp_bridge:
            try:
                await self.mcp_bridge.shutdown()
                logger.info("MCP bridge cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up MCP bridge: {e}")
    
    def get_capabilities(self) -> List[str]:
        """Get component capabilities."""
        return [
            "llm_orchestration",
            "template_management",
            "prompt_engineering",
            "context_management",
            "budget_tracking",
            "specialist_routing",
            "ai_messaging"
        ]
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get component metadata."""
        return {
            "description": "LLM orchestration and management service",
            "category": "ai_services"
        }
    
    def get_component_status(self) -> Dict[str, Any]:
        """Get detailed component status."""
        return {
            "llm_client": self.llm_client is not None,
            "model_router": self.model_router is not None,
            "ai_messaging_integration": self.ai_messaging_integration is not None,
            "context_manager": self.context_manager is not None,
            "prompt_engine": self.prompt_engine is not None,
            "template_manager": self.template_manager is not None,
            "prompt_registry": self.prompt_registry is not None,
            "budget_manager": self.budget_manager is not None,
            "anthropic_max_config": self.anthropic_max_config is not None,
            "anthropic_max_enabled": self.anthropic_max_config.enabled if self.anthropic_max_config else False,
            "mcp_bridge": self.mcp_bridge is not None,
            "mcp_integration": self.mcp_integration is not None
        }
    
    async def initialize_mcp_components(self):
        """Initialize MCP-related components after component startup."""
        # Initialize Hermes MCP Bridge
        try:
            from rhetor.core.mcp.hermes_bridge import RhetorMCPBridge
            self.mcp_bridge = RhetorMCPBridge(self.llm_client)
            await self.mcp_bridge.initialize()
            logger.info("Initialized Hermes MCP Bridge for FastMCP tools")
        except Exception as e:
            logger.warning(f"Failed to initialize MCP Bridge: {e}")
        
        # Initialize MCP Tools Integration with AI Registry
        try:
            from rhetor.core.mcp.tools_integration_simple import (
                MCPToolsIntegrationSimple,
                set_mcp_tools_integration
            )
            
            hermes_url = TektonEnviron.get("HERMES_URL", "http://localhost:8001")
            
            # Create simple MCP integration
            self.mcp_integration = MCPToolsIntegrationSimple(hermes_url=hermes_url)
            set_mcp_tools_integration(self.mcp_integration)
            
            logger.info("MCP Tools Integration initialized with AI Registry")
            
        except Exception as e:
            logger.warning(f"Failed to initialize MCP Tools Integration: {e}")
            self.mcp_integration = None