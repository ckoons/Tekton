"""Sophia component implementation using StandardComponentBase."""
import logging
from typing import List, Dict, Any

from shared.utils.standard_component import StandardComponentBase
from landmarks import architecture_decision, state_checkpoint, danger_zone

logger = logging.getLogger(__name__)


@architecture_decision(
    title="Multi-engine ML system",
    rationale="Sophia provides comprehensive ML capabilities with separate engines for metrics, analysis, experiments, recommendations, intelligence measurement, and core ML",
    alternatives_considered=["Single ML framework", "External ML services", "Simple analytics only"])
@state_checkpoint(
    title="ML engine ensemble state",
    state_type="ephemeral",
    persistence=False,
    consistency_requirements="Engine states must be synchronized",
    recovery_strategy="Restart all engines on recovery"
)
class SophiaComponent(StandardComponentBase):
    """Sophia machine learning and continuous improvement component."""
    
    def __init__(self):
        super().__init__(component_name="sophia", version="0.1.0")
        self.metrics_engine = None
        self.analysis_engine = None
        self.experiment_framework = None
        self.recommendation_system = None
        self.intelligence_measurement = None
        self.ml_engine = None
        self.llm_integration = None
        self.mcp_bridge = None
        self.chorus_tracker = None
        self.active_connections = []
        self.initialized = False
        
    @danger_zone(
        title="Complex multi-engine initialization",
        risk_level="high",
        risks=["Engine dependency conflicts", "Resource exhaustion", "Partial initialization"],
        mitigations=["Sequential initialization", "Resource monitoring", "Graceful degradation"],
        review_required=True
    )
    async def _component_specific_init(self):
        """Initialize Sophia-specific services."""
        # Import here to avoid circular imports
        from sophia.core.metrics_engine import get_metrics_engine
        from sophia.core.analysis_engine import get_analysis_engine
        from sophia.core.experiment_framework import get_experiment_framework
        from sophia.core.recommendation_system import get_recommendation_system
        from sophia.core.intelligence_measurement import get_intelligence_measurement
        from sophia.core.ml_engine import get_ml_engine
        
        try:
            # Initialize core engines
            self.metrics_engine = await get_metrics_engine()
            await self.metrics_engine.start()
            logger.info("Metrics engine started")
            
            self.analysis_engine = await get_analysis_engine()
            await self.analysis_engine.start()
            logger.info("Analysis engine started")
            
            self.experiment_framework = await get_experiment_framework()
            await self.experiment_framework.start()
            logger.info("Experiment framework started")
            
            self.recommendation_system = await get_recommendation_system()
            await self.recommendation_system.start()
            logger.info("Recommendation system started")
            
            self.intelligence_measurement = await get_intelligence_measurement()
            await self.intelligence_measurement.start()
            logger.info("Intelligence measurement started")
            
            self.ml_engine = await get_ml_engine()
            await self.ml_engine.start()
            logger.info("ML engine started")
            
            # Initialize LLM integration if available
            try:
                from sophia.utils.llm_integration import get_llm_integration
                self.llm_integration = await get_llm_integration()
                await self.llm_integration.initialize()
                logger.info("LLM Integration initialized successfully")
            except Exception as llm_error:
                logger.warning(f"Failed to initialize LLM Integration: {llm_error}")
                # LLM integration is optional
            
            # Initialize Greek Chorus cognition tracking
            try:
                from sophia.core.chorus_cognition import initialize_chorus_cognition_tracking
                self.chorus_tracker = await initialize_chorus_cognition_tracking(self)
                logger.info("Greek Chorus cognition tracking initialized")
            except Exception as chorus_error:
                logger.warning(f"Failed to initialize Greek Chorus tracking: {chorus_error}")
                # Greek Chorus tracking is optional
            
            # Mark as initialized
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing Sophia services: {e}")
            raise
    
    async def _component_specific_cleanup(self):
        """Cleanup Sophia-specific resources."""
        # Stop core engines
        if self.metrics_engine:
            try:
                await self.metrics_engine.stop()
                logger.info("Metrics engine stopped")
            except Exception as e:
                logger.warning(f"Error stopping metrics engine: {e}")
        
        if self.analysis_engine:
            try:
                await self.analysis_engine.stop()
                logger.info("Analysis engine stopped")
            except Exception as e:
                logger.warning(f"Error stopping analysis engine: {e}")
        
        if self.experiment_framework:
            try:
                await self.experiment_framework.stop()
                logger.info("Experiment framework stopped")
            except Exception as e:
                logger.warning(f"Error stopping experiment framework: {e}")
        
        if self.recommendation_system:
            try:
                await self.recommendation_system.stop()
                logger.info("Recommendation system stopped")
            except Exception as e:
                logger.warning(f"Error stopping recommendation system: {e}")
        
        if self.intelligence_measurement:
            try:
                await self.intelligence_measurement.stop()
                logger.info("Intelligence measurement stopped")
            except Exception as e:
                logger.warning(f"Error stopping intelligence measurement: {e}")
        
        if self.ml_engine:
            try:
                await self.ml_engine.stop()
                logger.info("ML engine stopped")
            except Exception as e:
                logger.warning(f"Error stopping ML engine: {e}")
        
        # Shutdown LLM integration if available
        if self.llm_integration:
            try:
                await self.llm_integration.shutdown()
                logger.info("LLM Integration shut down successfully")
            except Exception as llm_error:
                logger.warning(f"Error shutting down LLM Integration: {llm_error}")
        
        # Close any active WebSocket connections
        for connection in self.active_connections:
            try:
                await connection.close()
            except Exception:
                pass
        self.active_connections.clear()
        
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
            "metrics",
            "analysis", 
            "experiments",
            "recommendations",
            "intelligence",
            "ml",
            "advanced_analytics",
            "pattern_detection",
            "causal_analysis",
            "predictions",
            "collective_intelligence"
        ]
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get component metadata."""
        return {
            "description": "Machine learning and continuous improvement system for Tekton ecosystem",
            "category": "analytics"
        }
    
    def get_component_status(self) -> Dict[str, Any]:
        """Get detailed component status."""
        status = {
            "metrics_engine": self.metrics_engine is not None,
            "analysis_engine": self.analysis_engine is not None,
            "experiment_framework": self.experiment_framework is not None,
            "recommendation_system": self.recommendation_system is not None,
            "intelligence_measurement": self.intelligence_measurement is not None,
            "ml_engine": self.ml_engine is not None,
            "llm_integration": self.llm_integration is not None,
            "mcp_bridge": self.mcp_bridge is not None,
            "active_connections": len(self.active_connections)
        }
        
        # Add engine initialization status if available
        if self.metrics_engine and hasattr(self.metrics_engine, 'is_initialized'):
            status["metrics_engine_initialized"] = self.metrics_engine.is_initialized
        if self.analysis_engine and hasattr(self.analysis_engine, 'is_initialized'):
            status["analysis_engine_initialized"] = self.analysis_engine.is_initialized
        if self.experiment_framework and hasattr(self.experiment_framework, 'is_initialized'):
            status["experiment_framework_initialized"] = self.experiment_framework.is_initialized
        if self.recommendation_system and hasattr(self.recommendation_system, 'is_initialized'):
            status["recommendation_system_initialized"] = self.recommendation_system.is_initialized
        if self.intelligence_measurement and hasattr(self.intelligence_measurement, 'is_initialized'):
            status["intelligence_measurement_initialized"] = self.intelligence_measurement.is_initialized
        if self.ml_engine and hasattr(self.ml_engine, 'is_initialized'):
            status["ml_engine_initialized"] = self.ml_engine.is_initialized
        
        return status
    
    def check_all_engines_initialized(self) -> bool:
        """Check if all engines are initialized."""
        try:
            return (
                self.metrics_engine and hasattr(self.metrics_engine, 'is_initialized') and self.metrics_engine.is_initialized and
                self.analysis_engine and hasattr(self.analysis_engine, 'is_initialized') and self.analysis_engine.is_initialized and
                self.experiment_framework and hasattr(self.experiment_framework, 'is_initialized') and self.experiment_framework.is_initialized and
                self.recommendation_system and hasattr(self.recommendation_system, 'is_initialized') and self.recommendation_system.is_initialized and
                self.intelligence_measurement and hasattr(self.intelligence_measurement, 'is_initialized') and self.intelligence_measurement.is_initialized and
                self.ml_engine and hasattr(self.ml_engine, 'is_initialized') and self.ml_engine.is_initialized
            )
        except:
            return False
    
    async def initialize_mcp_bridge(self):
        """Initialize the MCP bridge after component startup."""
        try:
            from sophia.core.mcp.hermes_bridge import SophiaMCPBridge
            self.mcp_bridge = SophiaMCPBridge(self.ml_engine)
            await self.mcp_bridge.initialize()
            logger.info("Initialized Hermes MCP Bridge for FastMCP tools")
        except Exception as e:
            logger.warning(f"Failed to initialize MCP Bridge: {e}")
            # MCP bridge is optional