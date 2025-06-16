"""Athena component implementation using StandardComponentBase."""
import logging
from typing import List, Dict, Any
from pathlib import Path

from shared.utils.standard_component import StandardComponentBase
from athena.core.engine import get_knowledge_engine

logger = logging.getLogger(__name__)


class AthenaComponent(StandardComponentBase):
    """Athena knowledge graph component."""
    
    def __init__(self):
        super().__init__(component_name="athena", version="0.1.0")
        self.knowledge_engine = None
        
    async def _component_specific_init(self):
        """Initialize Athena-specific services."""
        # Initialize knowledge engine
        self.knowledge_engine = await get_knowledge_engine()
        if not self.knowledge_engine.is_initialized:
            await self.knowledge_engine.initialize()
            logger.info("Knowledge engine initialized successfully")
    
    async def _component_specific_cleanup(self):
        """Cleanup Athena-specific resources."""
        if self.knowledge_engine:
            try:
                await self.knowledge_engine.cleanup()
                logger.info("Knowledge engine cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up knowledge engine: {e}")
    
    def get_capabilities(self) -> List[str]:
        """Get component capabilities."""
        return [
            "knowledge_graph_management",
            "entity_relationship_tracking", 
            "semantic_search",
            "graph_visualization",
            "llm_enhanced_analysis"
        ]
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get component metadata."""
        return {
            "description": "Knowledge Graph System for relationship tracking and semantic search",
            "graph_type": "knowledge",
            "storage": "in-memory"
        }