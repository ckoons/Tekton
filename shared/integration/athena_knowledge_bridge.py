"""
Athena Knowledge Bridge - Integration between Noesis/Sophia and ESR Knowledge Graph

This bridge connects:
- Noesis Discovery Engine → ESR Knowledge Graph (storage of discoveries)
- Sophia Learning Engine → ESR Knowledge Graph (storage of learned patterns)
- ESR Knowledge Graph → Both engines (retrieval for context and validation)

The bridge implements bidirectional flow between discovery/learning and knowledge storage.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import json
import sys
from pathlib import Path

# Import environment handling
from shared.env import TektonEnviron
from shared.urls import tekton_url

# Add necessary paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "Engram"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "Noesis"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "Sophia"))

# Import ESR system
from engram.core.storage.unified_interface import ESRMemorySystem
from engram.core.storage.cognitive_workflows import CognitiveWorkflows, ThoughtType, Thought

# Import Noesis Discovery Engine
from noesis.core.discovery_engine import (
    DiscoveryEngine,
    Discovery,
    Pattern,
    Theory,
    ResearchStrategy
)

# Import Sophia Learning Engine
from sophia.core.learning_engine import (
    LearningEngine,
    Experiment,
    ExperimentType,
    Model,
    LearningEvent
)

logger = logging.getLogger(__name__)


class KnowledgeType(Enum):
    """Types of knowledge stored in the graph"""
    DISCOVERY = "discovery"
    PATTERN = "pattern"
    THEORY = "theory"
    EXPERIMENT = "experiment"
    MODEL = "model"
    INSIGHT = "insight"
    CONCEPT = "concept"
    RELATIONSHIP = "relationship"
    LEARNING = "learning"


class AthenaKnowledgeBridge:
    """
    Bridge between Noesis/Sophia engines and ESR Knowledge Graph.
    
    Implements the knowledge flow:
    1. Discoveries from Noesis → Stored as FACT thoughts in ESR
    2. Patterns from Sophia → Stored as PATTERN thoughts in ESR
    3. Theories → Stored with associations to supporting evidence
    4. Learning events → Create memory chains in ESR
    """
    
    def __init__(self):
        self.esr_system = None
        self.cognitive_workflows = None
        self.discovery_engine = None
        self.learning_engine = None
        
        # Track knowledge relationships
        self.knowledge_graph = {}  # id -> knowledge_entry
        self.relationships = {}    # id -> [related_ids]
        
        # Queue for processing
        self.processing_queue = asyncio.Queue()
        self.sync_task = None
        
        # Statistics
        self.stats = {
            'discoveries_stored': 0,
            'patterns_stored': 0,
            'theories_stored': 0,
            'experiments_stored': 0,
            'relationships_created': 0,
            'retrievals': 0
        }
        
    async def initialize(self):
        """Initialize all components and establish connections"""
        try:
            # Get data directory from environment
            data_dir = TektonEnviron.get('TEKTON_DATA_DIR', '/tmp/tekton/data')
            
            # Initialize ESR memory system
            self.esr_system = ESRMemorySystem(
                cache_size=100000,
                enable_backends={'vector', 'graph', 'sql', 'document', 'kv'},
                config={
                    'namespace': 'athena',
                    'data_dir': f"{data_dir}/athena/knowledge"
                }
            )
            await self.esr_system.start()
            
            # Initialize cognitive workflows
            self.cognitive_workflows = CognitiveWorkflows(
                cache=self.esr_system.cache,
                encoder=self.esr_system.encoder
            )
            
            # Initialize discovery engine
            self.discovery_engine = DiscoveryEngine()
            await self.discovery_engine.initialize()
            
            # Initialize learning engine
            self.learning_engine = LearningEngine()
            await self.learning_engine.initialize()
            
            # Start sync task
            self.sync_task = asyncio.create_task(self._sync_knowledge_loop())
            
            logger.info("Athena Knowledge Bridge initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Athena Knowledge Bridge: {e}")
            raise
    
    async def store_discovery(self, discovery: Discovery) -> str:
        """
        Store a discovery from Noesis in the knowledge graph.
        
        Args:
            discovery: Discovery object from Noesis
            
        Returns:
            Knowledge ID
        """
        # Convert discovery to thought
        thought_content = {
            'type': 'discovery',
            'query': discovery.query,
            'findings': discovery.findings,
            'confidence': discovery.confidence,
            'sources': discovery.sources,
            'timestamp': discovery.timestamp.isoformat()
        }
        
        # Determine associations (link to related patterns)
        associations = []
        if discovery.patterns:
            for pattern_id in discovery.patterns:
                # Store pattern reference
                pattern_key = await self.cognitive_workflows.store_thought(
                    content={'pattern_id': pattern_id, 'from_discovery': discovery.id},
                    thought_type=ThoughtType.OBSERVATION,
                    confidence=discovery.confidence,
                    ci_id='noesis'
                )
                associations.append(pattern_key)
        
        # Store as FACT thought
        knowledge_id = await self.cognitive_workflows.store_thought(
            content=thought_content,
            thought_type=ThoughtType.FACT,
            context={
                'source': 'noesis',
                'strategy': discovery.metadata.get('strategy', 'unknown'),
                'engine': 'discovery'
            },
            associations=associations,
            confidence=discovery.confidence,
            ci_id='noesis'
        )
        
        # Track in local graph
        self.knowledge_graph[knowledge_id] = {
            'type': KnowledgeType.DISCOVERY,
            'content': discovery,
            'stored_at': datetime.now(),
            'associations': associations
        }
        
        self.stats['discoveries_stored'] += 1
        logger.info(f"Stored discovery {discovery.id} as knowledge {knowledge_id}")
        
        return knowledge_id
    
    async def store_pattern(self, pattern: Dict[str, Any], source: str = 'sophia') -> str:
        """
        Store a pattern from Sophia or Engram in the knowledge graph.
        
        Args:
            pattern: Pattern dictionary
            source: Source system ('sophia', 'engram', etc.)
            
        Returns:
            Knowledge ID
        """
        # Store as IDEA thought (patterns are conceptual)
        knowledge_id = await self.cognitive_workflows.store_thought(
            content=pattern,
            thought_type=ThoughtType.IDEA,
            context={
                'source': source,
                'pattern_type': pattern.get('type', 'unknown'),
                'engine': 'pattern_recognition'
            },
            confidence=pattern.get('confidence', 0.5),
            ci_id=source
        )
        
        # Track in local graph
        self.knowledge_graph[knowledge_id] = {
            'type': KnowledgeType.PATTERN,
            'content': pattern,
            'stored_at': datetime.now()
        }
        
        self.stats['patterns_stored'] += 1
        logger.info(f"Stored pattern as knowledge {knowledge_id}")
        
        return knowledge_id
    
    async def store_theory(self, theory: Theory) -> str:
        """
        Store a theory from Noesis with all supporting evidence.
        
        Args:
            theory: Theory object from Noesis
            
        Returns:
            Knowledge ID
        """
        # First store supporting evidence as associations
        evidence_keys = []
        for evidence in theory.supporting_evidence:
            evidence_key = await self.cognitive_workflows.store_thought(
                content={'evidence': evidence, 'for_theory': theory.id},
                thought_type=ThoughtType.FACT,
                confidence=theory.confidence * 0.8,  # Evidence slightly less confident
                ci_id='noesis'
            )
            evidence_keys.append(evidence_key)
        
        # Store theory as OPINION (theories are interpretations)
        theory_content = {
            'type': 'theory',
            'description': theory.description,
            'hypothesis': theory.hypothesis,
            'evidence_count': len(theory.supporting_evidence),
            'confidence': theory.confidence,
            'timestamp': theory.created_at.isoformat()
        }
        
        knowledge_id = await self.cognitive_workflows.store_thought(
            content=theory_content,
            thought_type=ThoughtType.OPINION,
            context={
                'source': 'noesis',
                'theory_id': theory.id,
                'engine': 'theory_generation'
            },
            associations=evidence_keys,
            confidence=theory.confidence,
            ci_id='noesis'
        )
        
        # Track in local graph
        self.knowledge_graph[knowledge_id] = {
            'type': KnowledgeType.THEORY,
            'content': theory,
            'stored_at': datetime.now(),
            'evidence': evidence_keys
        }
        
        self.stats['theories_stored'] += 1
        logger.info(f"Stored theory {theory.id} with {len(evidence_keys)} evidence pieces")
        
        return knowledge_id
    
    async def store_experiment(self, experiment: Experiment) -> str:
        """
        Store an experiment from Sophia with results.
        
        Args:
            experiment: Experiment object from Sophia
            
        Returns:
            Knowledge ID
        """
        # Store experiment as PLAN (experiments are intentions)
        experiment_content = {
            'type': 'experiment',
            'name': experiment.name,
            'hypothesis': experiment.hypothesis,
            'experiment_type': experiment.type.value,
            'status': experiment.status,
            'results': experiment.results,
            'started_at': experiment.created_at.isoformat()
        }
        
        knowledge_id = await self.cognitive_workflows.store_thought(
            content=experiment_content,
            thought_type=ThoughtType.PLAN if experiment.status == 'pending' else ThoughtType.MEMORY,
            context={
                'source': 'sophia',
                'experiment_id': experiment.id,
                'engine': 'learning'
            },
            confidence=1.0 if experiment.results else 0.5,
            ci_id='sophia'
        )
        
        # Track in local graph
        self.knowledge_graph[knowledge_id] = {
            'type': KnowledgeType.EXPERIMENT,
            'content': experiment,
            'stored_at': datetime.now()
        }
        
        self.stats['experiments_stored'] += 1
        logger.info(f"Stored experiment {experiment.id} as knowledge {knowledge_id}")
        
        return knowledge_id
    
    async def retrieve_related_knowledge(self, 
                                        query: str,
                                        knowledge_type: Optional[KnowledgeType] = None,
                                        limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve related knowledge from the graph.
        
        Args:
            query: Search query
            knowledge_type: Optional filter by type
            limit: Maximum results
            
        Returns:
            List of related knowledge entries
        """
        # Use cognitive workflows for natural recall
        similar_thoughts = await self.cognitive_workflows.recall_similar(
            reference=query,
            limit=limit * 2,  # Get more to filter
            ci_id='athena'
        )
        
        results = []
        for thought in similar_thoughts:
            # Filter by type if specified
            if knowledge_type:
                content = thought.content if isinstance(thought, Thought) else thought
                if isinstance(content, dict) and content.get('type') != knowledge_type.value:
                    continue
            
            results.append({
                'thought': thought,
                'associations': thought.associations if hasattr(thought, 'associations') else []
            })
            
            if len(results) >= limit:
                break
        
        self.stats['retrievals'] += 1
        logger.info(f"Retrieved {len(results)} related knowledge items for query: {query[:50]}...")
        
        return results
    
    async def create_relationship(self,
                                 source_id: str,
                                 target_id: str,
                                 relationship_type: str,
                                 confidence: float = 0.8) -> bool:
        """
        Create a relationship between two knowledge entries.
        
        Args:
            source_id: Source knowledge ID
            target_id: Target knowledge ID
            relationship_type: Type of relationship
            confidence: Confidence in relationship
            
        Returns:
            Success status
        """
        # Store relationship as thought
        relationship_content = {
            'type': 'relationship',
            'source': source_id,
            'target': target_id,
            'relationship': relationship_type,
            'confidence': confidence
        }
        
        rel_id = await self.cognitive_workflows.store_thought(
            content=relationship_content,
            thought_type=ThoughtType.OBSERVATION,
            associations=[source_id, target_id],
            confidence=confidence,
            ci_id='athena'
        )
        
        # Track in relationships
        if source_id not in self.relationships:
            self.relationships[source_id] = []
        self.relationships[source_id].append({
            'target': target_id,
            'type': relationship_type,
            'id': rel_id
        })
        
        self.stats['relationships_created'] += 1
        logger.info(f"Created {relationship_type} relationship: {source_id[:8]} -> {target_id[:8]}")
        
        return True
    
    async def build_knowledge_context(self, 
                                     focal_point: str,
                                     depth: int = 2) -> Dict[str, Any]:
        """
        Build a context graph around a focal knowledge point.
        
        Args:
            focal_point: Central knowledge ID or query
            depth: How many relationship levels to traverse
            
        Returns:
            Context graph with related knowledge
        """
        context = await self.cognitive_workflows.build_context(
            keys=[focal_point] if focal_point in self.knowledge_graph else None,
            query=focal_point if focal_point not in self.knowledge_graph else None,
            ci_id='athena'
        )
        
        # Enhance with local graph information
        if focal_point in self.knowledge_graph:
            entry = self.knowledge_graph[focal_point]
            context['local_type'] = entry['type'].value
            context['stored_at'] = entry['stored_at'].isoformat()
            
            # Add relationships
            if focal_point in self.relationships:
                context['relationships'] = self.relationships[focal_point]
        
        return context
    
    async def sync_discovery_to_learning(self):
        """Sync discoveries from Noesis to Sophia for validation"""
        # Get recent discoveries
        recent = await self.discovery_engine.get_recent_discoveries(hours=1)
        
        for discovery in recent:
            # Create validation experiment in Sophia
            experiment = await self.learning_engine.create_experiment(
                name=f"Validate discovery: {discovery.query[:50]}",
                type=ExperimentType.PATTERN_VALIDATION,
                hypothesis=f"Discovery findings are valid: {discovery.findings[0] if discovery.findings else 'unknown'}",
                control_config={'discovery_id': discovery.id}
            )
            
            # Store the experiment
            await self.store_experiment(experiment)
            
            # Create relationship
            discovery_key = f"discovery_{discovery.id}"
            experiment_key = f"experiment_{experiment.id}"
            await self.create_relationship(
                discovery_key,
                experiment_key,
                "validates",
                confidence=0.9
            )
    
    async def sync_learning_to_discovery(self):
        """Sync successful patterns from Sophia to Noesis for exploration"""
        # Get successful models
        models = await self.learning_engine.get_models(min_performance=0.8)
        
        for model in models:
            # Create research query for further exploration
            query = f"explore applications and extensions of {model.name}"
            
            # Trigger discovery research
            discovery = await self.discovery_engine.research(
                query=query,
                context={'model_id': model.id, 'performance': model.performance},
                strategy=ResearchStrategy.BREADTH_FIRST
            )
            
            # Store the discovery
            await self.store_discovery(discovery)
            
            # Create relationship
            model_key = f"model_{model.id}"
            discovery_key = f"discovery_{discovery.id}"
            await self.create_relationship(
                model_key,
                discovery_key,
                "explores",
                confidence=0.85
            )
    
    async def _sync_knowledge_loop(self):
        """Background task to sync knowledge between systems"""
        while True:
            try:
                # Sync discoveries to learning every 5 minutes
                await asyncio.sleep(300)
                await self.sync_discovery_to_learning()
                
                # Sync learning to discovery
                await self.sync_learning_to_discovery()
                
                # Clean up old entries (memory metabolism)
                await self.cognitive_workflows.memory_metabolism()
                
            except Exception as e:
                logger.error(f"Error in knowledge sync loop: {e}")
                await asyncio.sleep(60)
    
    async def get_status(self) -> Dict[str, Any]:
        """Get bridge status and statistics"""
        return {
            'status': 'active',
            'components': {
                'esr_system': 'connected' if self.esr_system else 'disconnected',
                'discovery_engine': 'connected' if self.discovery_engine else 'disconnected',
                'learning_engine': 'connected' if self.learning_engine else 'disconnected'
            },
            'knowledge_graph': {
                'total_entries': len(self.knowledge_graph),
                'relationships': len(self.relationships)
            },
            'statistics': self.stats,
            'timestamp': datetime.now().isoformat()
        }
    
    async def shutdown(self):
        """Clean shutdown of all components"""
        if self.sync_task:
            self.sync_task.cancel()
        
        if self.discovery_engine:
            await self.discovery_engine.shutdown()
        
        if self.learning_engine:
            await self.learning_engine.shutdown()
        
        if self.esr_system:
            await self.esr_system.stop()
        
        logger.info("Athena Knowledge Bridge shutdown complete")


# Singleton instance
_bridge_instance = None


async def get_knowledge_bridge() -> AthenaKnowledgeBridge:
    """Get or create the global knowledge bridge instance"""
    global _bridge_instance
    
    if _bridge_instance is None:
        _bridge_instance = AthenaKnowledgeBridge()
        await _bridge_instance.initialize()
    
    return _bridge_instance


# Export for use
__all__ = ['AthenaKnowledgeBridge', 'get_knowledge_bridge', 'KnowledgeType']