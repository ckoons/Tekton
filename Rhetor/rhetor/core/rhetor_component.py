"""Rhetor component implementation using StandardComponentBase."""
import logging
import os
from typing import List, Dict, Any

from shared.utils.standard_component import StandardComponentBase

logger = logging.getLogger(__name__)


class RhetorComponent(StandardComponentBase):
    """Rhetor LLM orchestration and management component."""
    
    def __init__(self):
        super().__init__(component_name="rhetor", version="0.1.0")
        self.llm_client = None
        self.model_router = None
        self.specialist_router = None
        self.ai_specialist_manager = None
        self.ai_messaging_integration = None
        self.context_manager = None
        self.prompt_engine = None
        self.template_manager = None
        self.prompt_registry = None
        self.budget_manager = None
        self.anthropic_max_config = None
        self.mcp_bridge = None
        self.mcp_integration = None
        self.component_specialist_registry = None
        self.initialized = False
        
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
        from rhetor.core.specialist_router import SpecialistRouter
        from rhetor.core.ai_specialist_manager import AISpecialistManager
        from rhetor.core.ai_messaging_integration import AIMessagingIntegration
        from rhetor.core.anthropic_max_config import AnthropicMaxConfig
        from rhetor.core.component_specialists import ComponentSpecialistRegistry
        
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
            
            # Initialize specialist router for AI specialist management
            self.specialist_router = SpecialistRouter(self.llm_client, budget_manager=self.budget_manager)
            logger.info("Specialist router initialized")
            
            # Initialize AI specialist manager
            self.ai_specialist_manager = AISpecialistManager(self.llm_client, self.specialist_router)
            self.specialist_router.set_specialist_manager(self.ai_specialist_manager)
            logger.info("AI specialist manager initialized")
            
            # Initialize component specialist registry
            self.component_specialist_registry = ComponentSpecialistRegistry(self.ai_specialist_manager)
            logger.info("Component specialist registry initialized")
            
            # Ensure rhetor-orchestrator specialist is available
            try:
                rhetor_specialist = await self.component_specialist_registry.ensure_specialist("rhetor")
                if rhetor_specialist:
                    logger.info(f"Rhetor orchestrator specialist ready: {rhetor_specialist.specialist_id}")
            except Exception as e:
                logger.warning(f"Failed to ensure rhetor specialist: {e}")
            
            # Start core AI specialists
            try:
                core_results = await self.ai_specialist_manager.start_core_specialists()
                logger.info(f"Core AI specialists started: {core_results}")
            except Exception as e:
                logger.warning(f"Failed to start core AI specialists: {e}")
            
            # Initialize AI messaging integration with Hermes
            hermes_url = os.environ.get("HERMES_URL", "http://localhost:8001")
            self.ai_messaging_integration = AIMessagingIntegration(
                self.ai_specialist_manager, 
                hermes_url, 
                self.specialist_router
            )
            try:
                await self.ai_messaging_integration.initialize()
                logger.info("AI messaging integration initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize AI messaging integration: {e}")
            
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
            "specialist_router": self.specialist_router is not None,
            "ai_specialist_manager": self.ai_specialist_manager is not None,
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
        
        # Initialize MCP Tools Integration with live components
        try:
            from rhetor.core.mcp.init_integration import (
                initialize_mcp_integration,
                setup_hermes_subscriptions,
                test_mcp_integration
            )
            
            hermes_url = os.environ.get("HERMES_URL", "http://localhost:8001")
            
            # Create the integration
            self.mcp_integration = initialize_mcp_integration(
                specialist_manager=self.ai_specialist_manager,
                messaging_integration=self.ai_messaging_integration,
                hermes_url=hermes_url
            )
            
            # Set up Hermes subscriptions for cross-component messaging
            await setup_hermes_subscriptions(self.mcp_integration)
            
            # Test the integration if in debug mode
            if logger.isEnabledFor(logging.DEBUG):
                await test_mcp_integration(self.mcp_integration)
            
            logger.info("MCP Tools Integration initialized with live components")
            
        except Exception as e:
            logger.warning(f"Failed to initialize MCP Tools Integration: {e}")