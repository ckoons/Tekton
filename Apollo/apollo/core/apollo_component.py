"""Apollo component implementation using StandardComponentBase."""
import logging
import os
from typing import List, Dict, Any
from pathlib import Path

# Try to import landmarks
try:
    from landmarks import architecture_decision, state_checkpoint, integration_point, danger_zone
except ImportError:
    # Define no-op decorators if landmarks not available
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def danger_zone(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

from shared.utils.standard_component import StandardComponentBase
from apollo.core.apollo_manager import ApolloManager
from apollo.core.context_observer import ContextObserver
from apollo.core.token_budget import TokenBudgetManager
from apollo.core.predictive_engine import PredictiveEngine
from apollo.core.action_planner import ActionPlanner
from apollo.core.protocol_enforcer import ProtocolEnforcer
from apollo.core.message_handler import MessageHandler, HermesClient
from apollo.core.interfaces.rhetor import RhetorInterface

logger = logging.getLogger(__name__)


@architecture_decision(
    title="Apollo Component Architecture",
    rationale="Modular conversational CI system with attention management, token budgeting, predictive capabilities, and protocol enforcement",
    alternatives_considered=["Monolithic chat manager", "Simple message router", "Stateless request handler"],
    decided_by="Casey"
)
@state_checkpoint(
    title="Apollo Component State",
    state_type="component",
    persistence=True,
    consistency_requirements="Context, budget, predictions, and message history must be consistent",
    recovery_strategy="Load from data directories on startup"
)
class ApolloComponent(StandardComponentBase):
    """Apollo local attention and prediction component."""
    
    def __init__(self):
        super().__init__(component_name="apollo", version="0.1.0")
        
        # Sub-component instances
        self.apollo_manager = None
        self.rhetor_interface = None
        self.message_handler = None
        self.context_observer = None
        self.token_budget_manager = None
        self.protocol_enforcer = None
        self.predictive_engine = None
        self.action_planner = None
        self.hermes_client = None
        
        # Data directories
        self.data_dir = None
        self.context_data_dir = None
        self.budget_data_dir = None
        self.prediction_data_dir = None
        self.action_data_dir = None
        self.protocol_data_dir = None
        self.message_data_dir = None
        
    @integration_point(
        title="Apollo Sub-component Initialization",
        target_component="Rhetor, Hermes, Internal Modules",
        protocol="Direct instantiation and configuration",
        data_flow="Apollo → Sub-components (context, budget, prediction, action, protocol, message)"
    )
    async def _component_specific_init(self):
        """Initialize Apollo-specific services."""
        # Create data directories
        self.data_dir = Path(self.global_config.get_data_dir("apollo"))
        
        # Sub-directories for component data
        self.context_data_dir = self.data_dir / "context_data"
        self.budget_data_dir = self.data_dir / "budget_data" 
        self.prediction_data_dir = self.data_dir / "prediction_data"
        self.action_data_dir = self.data_dir / "action_data"
        self.protocol_data_dir = self.data_dir / "protocol_data"
        self.message_data_dir = self.data_dir / "message_data"
        
        # Create all directories
        for dir_path in [self.context_data_dir, self.budget_data_dir, 
                         self.prediction_data_dir, self.action_data_dir,
                         self.protocol_data_dir, self.message_data_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components in order (critical for Apollo)
        
        # 1. Create Rhetor interface
        self.rhetor_interface = RhetorInterface()
        
        # 2. Create message handler with Hermes client
        self.hermes_client = HermesClient()
        self.message_handler = MessageHandler(
            component_name="apollo",
            hermes_client=self.hermes_client,
            data_dir=str(self.message_data_dir)
        )
        
        # 3. Create context observer
        self.context_observer = ContextObserver(
            rhetor_interface=self.rhetor_interface,
            data_dir=str(self.context_data_dir)
        )
        
        # 4. Create token budget manager
        self.token_budget_manager = TokenBudgetManager(
            data_dir=str(self.budget_data_dir)
        )
        
        # 5. Create protocol enforcer
        self.protocol_enforcer = ProtocolEnforcer(
            data_dir=str(self.protocol_data_dir),
            load_defaults=True
        )
        
        # 6. Create predictive engine
        self.predictive_engine = PredictiveEngine(
            context_observer=self.context_observer,
            data_dir=str(self.prediction_data_dir)
        )
        
        # 7. Create action planner
        self.action_planner = ActionPlanner(
            context_observer=self.context_observer,
            predictive_engine=self.predictive_engine,
            data_dir=str(self.action_data_dir)
        )
        
        # 8. Create Apollo manager
        self.apollo_manager = ApolloManager(
            rhetor_interface=self.rhetor_interface,
            data_dir=str(self.data_dir)
        )
        
        # 9. Register components with Apollo manager
        self.apollo_manager.context_observer = self.context_observer
        self.apollo_manager.token_budget_manager = self.token_budget_manager
        self.apollo_manager.protocol_enforcer = self.protocol_enforcer
        self.apollo_manager.predictive_engine = self.predictive_engine
        self.apollo_manager.action_planner = self.action_planner
        self.apollo_manager.message_handler = self.message_handler
        
        # 10. Start components that have start methods
        logger.info("Starting Apollo components...")
        await self.message_handler.start()
        await self.context_observer.start()
        await self.predictive_engine.start()
        await self.action_planner.start()
        
        # Mark apollo_manager as running
        self.apollo_manager.is_running = True
        
        logger.info("Apollo components initialized successfully")
    
    async def _component_specific_cleanup(self):
        """Cleanup Apollo-specific resources."""
        try:
            # Stop components in reverse order
            if self.apollo_manager:
                self.apollo_manager.is_running = False
            
            if self.action_planner:
                await self.action_planner.stop()
                logger.info("Action planner stopped")
                
            if self.predictive_engine:
                await self.predictive_engine.stop()
                logger.info("Predictive engine stopped")
                
            if self.context_observer:
                await self.context_observer.stop()
                logger.info("Context observer stopped")
                
            if self.message_handler:
                await self.message_handler.stop()
                logger.info("Message handler stopped")
                
            logger.info("Apollo components shut down successfully")
            
        except Exception as e:
            logger.warning(f"Error cleaning up Apollo components: {e}")
    
    def get_capabilities(self) -> List[str]:
        """Get component capabilities."""
        return [
            "llm_orchestration",
            "context_observation", 
            "token_budget_management",
            "predictive_planning",
            "protocol_enforcement"
        ]
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get component metadata."""
        metadata = {
            "description": "Local attention and prediction system for LLM orchestration",
            "category": "ai",
            "data_dir": str(self.data_dir) if self.data_dir else None
        }
        
        # Add component status if available
        if self.apollo_manager and hasattr(self.apollo_manager, 'get_system_status'):
            try:
                system_status = self.apollo_manager.get_system_status()
                metadata["system_status"] = system_status
            except:
                pass
                
        return metadata