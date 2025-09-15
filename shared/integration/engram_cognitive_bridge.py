"""
Engram Cognitive Bridge
Integrates Engram UI cognitive patterns with Sophia learning and Noesis discovery
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum

# Import existing Sophia and Noesis components
from Sophia.sophia.core.sophia_component import SophiaComponent
from Sophia.sophia.core.learning_engine import LearningEngine, ExperimentType
from Noesis.noesis.core.noesis_component import NoesisComponent
from Noesis.noesis.core.discovery_engine import DiscoveryEngine, ResearchStrategy
from Noesis.noesis.core.integration.sophia_bridge import SophiaBridge, TheoryExperimentProtocol
from shared.integration.athena_knowledge_bridge import get_knowledge_bridge, KnowledgeType
from shared.utils.standard_component import StandardComponentBase
# from landmarks import integration_point, performance_boundary

# Mock decorators if landmarks not available
def integration_point(**kwargs):
    def decorator(cls):
        return cls
    return decorator

def performance_boundary(**kwargs):
    def decorator(cls):
        return cls
    return decorator

logger = logging.getLogger(__name__)


class CognitiveEventType(Enum):
    """Types of cognitive events from Engram"""
    PATTERN_DETECTED = "pattern_detected"
    BLINDSPOT_FOUND = "blindspot_found"
    INEFFICIENCY_DETECTED = "inefficiency_detected"
    STRENGTH_IDENTIFIED = "strength_identified"
    EVOLUTION_OBSERVED = "evolution_observed"
    CONCEPT_FORMED = "concept_formed"
    MEMORY_FORMED = "memory_formed"
    INSIGHT_GENERATED = "insight_generated"


@dataclass
class CognitivePattern:
    """Represents a cognitive pattern from Engram"""
    id: str
    name: str
    type: str
    state: str  # emerging, strengthening, stable, fading
    strength: float
    confidence: float
    novelty: str
    description: str
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "engram"
    related_concepts: List[str] = field(default_factory=list)
    

@dataclass
class CognitiveInsight:
    """Represents an insight from Engram"""
    id: str
    type: str  # blindspot, inefficiency, strength, evolution
    content: str
    severity: str
    frequency: int
    impact: str
    suggestions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ResearchRequest:
    """Request for research from Noesis"""
    id: str
    query: str
    context: Dict[str, Any]
    priority: str
    source_pattern: Optional[CognitivePattern] = None
    source_insight: Optional[CognitiveInsight] = None
    requested_at: datetime = field(default_factory=datetime.now)


@dataclass 
class LearningRequest:
    """Request for learning from Sophia"""
    id: str
    pattern: CognitivePattern
    validation_data: Dict[str, Any]
    metrics: List[str]
    experiment_type: str
    requested_at: datetime = field(default_factory=datetime.now)


@integration_point(
    name="Engram-Sophia-Noesis Bridge",
    description="Bidirectional integration between cognitive UI and backend ML/discovery",
    protocols=["WebSocket", "HTTP", "Event-driven"],
    data_flow="Engram → Noesis (discovery) → Sophia (learning) → Engram (memory)"
)
@performance_boundary(
    title="Cognitive Processing Pipeline",
    sla="<500ms for pattern detection, <2s for research, <5s for learning",
    optimization_notes="Async processing, caching, batch operations"
)
class EngramCognitiveBridge(StandardComponentBase):
    """
    Bridge between Engram UI and Sophia/Noesis backend services
    Enables cognitive pattern analysis, automated research, and continuous learning
    """
    
    def __init__(self):
        super().__init__(component_name="engram_cognitive_bridge", version="0.1.0")
        
        # Component connections
        self.sophia_component: Optional[SophiaComponent] = None
        self.noesis_component: Optional[NoesisComponent] = None
        self.sophia_bridge: Optional[SophiaBridge] = None
        self.athena_bridge = None  # Will be initialized in _component_specific_init
        self.discovery_engine: Optional[DiscoveryEngine] = None
        self.learning_engine: Optional[LearningEngine] = None
        
        # Pattern tracking
        self.active_patterns: Dict[str, CognitivePattern] = {}
        self.insights_cache: Dict[str, CognitiveInsight] = {}
        self.research_queue: asyncio.Queue = asyncio.Queue()
        self.learning_queue: asyncio.Queue = asyncio.Queue()
        
        # Active protocols
        self.active_protocols: Dict[str, TheoryExperimentProtocol] = {}
        
        # Statistics
        self.stats = {
            'patterns_processed': 0,
            'insights_generated': 0,
            'research_requests': 0,
            'learning_cycles': 0,
            'discoveries_made': 0
        }
        
    async def _component_specific_init(self):
        """Initialize bridge connections"""
        logger.info("Initializing Engram Cognitive Bridge with full engine integration")
        
        # Initialize Athena Knowledge Bridge FIRST (provides ESR access)
        try:
            self.athena_bridge = await get_knowledge_bridge()
            logger.info("Connected to Athena Knowledge Bridge (ESR)")
        except Exception as e:
            logger.error(f"Failed to connect to Athena Knowledge Bridge: {e}")
            
        # Initialize Discovery Engine (Noesis)
        try:
            self.discovery_engine = DiscoveryEngine()
            await self.discovery_engine.initialize()
            logger.info("Initialized Noesis Discovery Engine")
        except Exception as e:
            logger.error(f"Failed to initialize Discovery Engine: {e}")
            
        # Initialize Learning Engine (Sophia)
        try:
            self.learning_engine = LearningEngine()
            await self.learning_engine.initialize()
            logger.info("Initialized Sophia Learning Engine")
        except Exception as e:
            logger.error(f"Failed to initialize Learning Engine: {e}")
            
        # Initialize legacy components for backward compatibility
        try:
            self.sophia_component = SophiaComponent()
            await self.sophia_component.initialize()
            logger.info("Connected to Sophia component (legacy)")
        except Exception as e:
            logger.warning(f"Failed to connect to legacy Sophia: {e}")
            
        try:
            self.noesis_component = NoesisComponent()
            await self.noesis_component.initialize()
            logger.info("Connected to Noesis component (legacy)")
        except Exception as e:
            logger.warning(f"Failed to connect to legacy Noesis: {e}")
            
        # Initialize Sophia-Noesis bridge
        try:
            self.sophia_bridge = SophiaBridge()
            logger.info("Initialized Sophia-Noesis bridge")
        except Exception as e:
            logger.warning(f"Failed to initialize Sophia bridge: {e}")
            
        # Start processing queues
        asyncio.create_task(self._process_research_queue())
        asyncio.create_task(self._process_learning_queue())
        
    async def process_cognitive_event(self, event_type: CognitiveEventType, data: Dict[str, Any]):
        """
        Process cognitive event from Engram UI
        
        Args:
            event_type: Type of cognitive event
            data: Event data from Engram
        """
        logger.info(f"Processing cognitive event: {event_type.value}")
        
        if event_type == CognitiveEventType.PATTERN_DETECTED:
            await self._handle_pattern_detection(data)
        elif event_type == CognitiveEventType.BLINDSPOT_FOUND:
            await self._handle_blindspot(data)
        elif event_type == CognitiveEventType.INEFFICIENCY_DETECTED:
            await self._handle_inefficiency(data)
        elif event_type == CognitiveEventType.STRENGTH_IDENTIFIED:
            await self._handle_strength(data)
        elif event_type == CognitiveEventType.EVOLUTION_OBSERVED:
            await self._handle_evolution(data)
        elif event_type == CognitiveEventType.CONCEPT_FORMED:
            await self._handle_concept_formation(data)
        elif event_type == CognitiveEventType.INSIGHT_GENERATED:
            await self._handle_insight_generation(data)
            
        self.stats['patterns_processed'] += 1
        
    async def _handle_pattern_detection(self, data: Dict[str, Any]):
        """Handle detected pattern from Engram"""
        pattern = CognitivePattern(
            id=data.get('id', f"pattern_{datetime.now().timestamp()}"),
            name=data['name'],
            type=data.get('type', 'general'),
            state=data.get('state', 'emerging'),
            strength=data.get('strength', 0.5),
            confidence=data.get('confidence', 0.5),
            novelty=data.get('novelty', 'interesting'),
            description=data.get('description', ''),
            related_concepts=data.get('concepts', [])
        )
        
        self.active_patterns[pattern.id] = pattern
        
        # Store pattern in knowledge graph
        if self.athena_bridge:
            pattern_dict = asdict(pattern)
            pattern_dict['timestamp'] = pattern.timestamp.isoformat()
            knowledge_id = await self.athena_bridge.store_pattern(pattern_dict, source='engram')
            logger.info(f"Stored pattern {pattern.id} in knowledge graph as {knowledge_id}")
        
        # If pattern is significant, trigger research
        if pattern.strength > 0.6 and pattern.state in ['emerging', 'strengthening']:
            await self._trigger_pattern_research(pattern)
            
        # If pattern is stable and strong, trigger learning
        if pattern.state == 'stable' and pattern.strength > 0.8:
            await self._trigger_pattern_learning(pattern)
            
    async def _handle_blindspot(self, data: Dict[str, Any]):
        """Handle blindspot detection"""
        insight = CognitiveInsight(
            id=f"blindspot_{datetime.now().timestamp()}",
            type='blindspot',
            content=data.get('text', ''),
            severity=data.get('severity', 'medium'),
            frequency=data.get('frequency', 1),
            impact=data.get('impact', 'medium'),
            suggestions=data.get('suggestions', [])
        )
        
        self.insights_cache[insight.id] = insight
        
        # Create immediate research request for blindspot correction
        research = ResearchRequest(
            id=f"research_{insight.id}",
            query=self._generate_blindspot_query(insight),
            context={'insight': asdict(insight)},
            priority='high',
            source_insight=insight
        )
        
        await self.research_queue.put(research)
        
    async def _handle_inefficiency(self, data: Dict[str, Any]):
        """Handle inefficiency detection"""
        insight = CognitiveInsight(
            id=f"inefficiency_{datetime.now().timestamp()}",
            type='inefficiency',
            content=data.get('text', ''),
            severity=data.get('severity', 'medium'),
            frequency=data.get('frequency', 1),
            impact=data.get('timeWasted', 'unknown'),
            suggestions=data.get('suggestions', [])
        )
        
        self.insights_cache[insight.id] = insight
        
        # Research optimization strategies
        research = ResearchRequest(
            id=f"research_{insight.id}",
            query=f"optimize {insight.content} best practices efficiency",
            context={'insight': asdict(insight)},
            priority='medium',
            source_insight=insight
        )
        
        await self.research_queue.put(research)
        
    async def _handle_strength(self, data: Dict[str, Any]):
        """Handle strength identification"""
        insight = CognitiveInsight(
            id=f"strength_{datetime.now().timestamp()}",
            type='strength',
            content=data.get('text', ''),
            severity='positive',
            frequency=data.get('consistency', 80),
            impact=data.get('impact', 'high'),
            suggestions=["Amplify this strength", "Apply to other areas"]
        )
        
        self.insights_cache[insight.id] = insight
        
        # Create pattern from strength for learning
        pattern = CognitivePattern(
            id=f"strength_pattern_{insight.id}",
            name=f"Strength: {insight.content[:30]}",
            type='strength',
            state='stable',
            strength=insight.frequency / 100,
            confidence=0.9,
            novelty='proven',
            description=insight.content
        )
        
        await self._trigger_pattern_learning(pattern)
        
    async def _handle_evolution(self, data: Dict[str, Any]):
        """Handle pattern evolution observation"""
        # Track evolution and predict next steps
        evolution_data = {
            'from': data.get('from', ''),
            'to': data.get('to', ''),
            'improvement': data.get('improvement', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        # Research next evolution steps
        research = ResearchRequest(
            id=f"evolution_{datetime.now().timestamp()}",
            query=f"next evolution after {evolution_data['to']} advanced techniques",
            context={'evolution': evolution_data},
            priority='low'
        )
        
        await self.research_queue.put(research)
        
    async def _handle_concept_formation(self, data: Dict[str, Any]):
        """Handle new concept formation"""
        # Create pattern from concept
        pattern = CognitivePattern(
            id=f"concept_{data.get('id', datetime.now().timestamp())}",
            name=data.get('thought', '')[:50],
            type=data.get('type', 'concept'),
            state='emerging',
            strength=0.5,
            confidence=self._map_confidence(data.get('confidence', 'exploring')),
            novelty=data.get('novelty', 'interesting'),
            description=data.get('thought', '')
        )
        
        self.active_patterns[pattern.id] = pattern
        
        # Trigger discovery research for novel concepts
        if pattern.novelty in ['breakthrough', 'revolutionary']:
            await self._trigger_pattern_research(pattern)
            
    async def _handle_insight_generation(self, data: Dict[str, Any]):
        """Handle insight generation"""
        self.stats['insights_generated'] += 1
        
        # Process based on insight type
        insight_type = data.get('type', 'general')
        if insight_type == 'blindspot':
            await self._handle_blindspot(data)
        elif insight_type == 'inefficiency':
            await self._handle_inefficiency(data)
        elif insight_type == 'strength':
            await self._handle_strength(data)
            
    async def _trigger_pattern_research(self, pattern: CognitivePattern):
        """Trigger Noesis research for pattern"""
        if not self.noesis_component:
            logger.warning("Noesis component not available for research")
            return
            
        research = ResearchRequest(
            id=f"pattern_research_{pattern.id}",
            query=f"{pattern.name} {pattern.description}",
            context={'pattern': asdict(pattern)},
            priority='medium' if pattern.strength > 0.7 else 'low',
            source_pattern=pattern
        )
        
        await self.research_queue.put(research)
        self.stats['research_requests'] += 1
        
    async def _trigger_pattern_learning(self, pattern: CognitivePattern):
        """Trigger Sophia learning for pattern"""
        if not self.sophia_component:
            logger.warning("Sophia component not available for learning")
            return
            
        learning = LearningRequest(
            id=f"learning_{pattern.id}",
            pattern=pattern,
            validation_data={'pattern_strength': pattern.strength},
            metrics=['accuracy', 'consistency', 'impact'],
            experiment_type='pattern_validation'
        )
        
        await self.learning_queue.put(learning)
        self.stats['learning_cycles'] += 1
        
    async def _process_research_queue(self):
        """Process research requests with Noesis Discovery Engine"""
        while True:
            try:
                research = await self.research_queue.get()
                
                # Use new Discovery Engine
                if self.discovery_engine:
                    # Execute research with appropriate strategy
                    strategy = ResearchStrategy.HEURISTIC
                    if research.priority == 'high':
                        strategy = ResearchStrategy.DEPTH_FIRST
                    elif research.source_insight and research.source_insight.type == 'blindspot':
                        strategy = ResearchStrategy.BREADTH_FIRST
                        
                    discovery = await self.discovery_engine.research(
                        query=research.query,
                        context=research.context,
                        strategy=strategy
                    )
                    
                    # Store in knowledge graph
                    if self.athena_bridge and discovery:
                        knowledge_id = await self.athena_bridge.store_discovery(discovery)
                        logger.info(f"Stored discovery {discovery.id} as knowledge {knowledge_id}")
                        
                        # Create relationships if source pattern exists
                        if research.source_pattern:
                            pattern_key = f"pattern_{research.source_pattern.id}"
                            await self.athena_bridge.create_relationship(
                                pattern_key,
                                knowledge_id,
                                "discovered_from",
                                confidence=0.85
                            )
                    
                    # Process results
                    if discovery:
                        await self._process_research_results(research, discovery)
                        self.stats['discoveries_made'] += 1
                        
                # Fallback to legacy component
                elif self.noesis_component:
                    results = await self._execute_noesis_research(research)
                    if results:
                        await self._process_research_results(research, results)
                        
            except Exception as e:
                logger.error(f"Error processing research queue: {e}")
                
            await asyncio.sleep(1)
            
    async def _process_learning_queue(self):
        """Process learning requests with Sophia Learning Engine"""
        while True:
            try:
                learning = await self.learning_queue.get()
                
                # Use new Learning Engine
                if self.learning_engine:
                    # Create experiment based on pattern type
                    experiment_type = ExperimentType.PATTERN_VALIDATION
                    if learning.experiment_type == 'performance':
                        experiment_type = ExperimentType.PERFORMANCE_TEST
                    elif learning.experiment_type == 'comparison':
                        experiment_type = ExperimentType.AB_TEST
                        
                    experiment = await self.learning_engine.create_experiment(
                        name=f"Validate {learning.pattern.name}",
                        type=experiment_type,
                        hypothesis=f"Pattern {learning.pattern.name} has strength {learning.pattern.strength}",
                        control_config={
                            'pattern': asdict(learning.pattern),
                            'validation_data': learning.validation_data
                        }
                    )
                    
                    # Run the experiment
                    await self.learning_engine.run_experiment(experiment.id)
                    
                    # Get results
                    experiment = await self.learning_engine.get_experiment(experiment.id)
                    
                    # Store in knowledge graph
                    if self.athena_bridge and experiment:
                        knowledge_id = await self.athena_bridge.store_experiment(experiment)
                        logger.info(f"Stored experiment {experiment.id} as knowledge {knowledge_id}")
                        
                        # Create relationship to pattern
                        pattern_key = f"pattern_{learning.pattern.id}"
                        await self.athena_bridge.create_relationship(
                            pattern_key,
                            knowledge_id,
                            "validated_by",
                            confidence=experiment.results.get('confidence', 0.8) if experiment.results else 0.5
                        )
                    
                    # Process results
                    if experiment and experiment.results:
                        await self._process_learning_results(learning, experiment.results)
                        self.stats['learning_cycles'] += 1
                        
                # Fallback to legacy component
                elif self.sophia_component:
                    results = await self._execute_sophia_learning(learning)
                    if results:
                        await self._process_learning_results(learning, results)
                        
            except Exception as e:
                logger.error(f"Error processing learning queue: {e}")
                
            await asyncio.sleep(1)
            
    async def _execute_noesis_research(self, research: ResearchRequest) -> Optional[Dict[str, Any]]:
        """Execute research through Noesis discovery engine"""
        try:
            # Call Noesis discovery methods
            if hasattr(self.noesis_component, 'discovery_engine'):
                discovery = await self.noesis_component.discovery_engine.discover(
                    query=research.query,
                    context=research.context
                )
                
                self.stats['discoveries_made'] += 1
                return discovery
                
        except Exception as e:
            logger.error(f"Noesis research failed: {e}")
            
        return None
        
    async def _execute_sophia_learning(self, learning: LearningRequest) -> Optional[Dict[str, Any]]:
        """Execute learning through Sophia ML engine"""
        try:
            # Create experiment through Sophia-Noesis bridge
            if self.sophia_bridge:
                protocol = await self.sophia_bridge.create_theory_validation_protocol(
                    theoretical_prediction={
                        'pattern': learning.pattern.name,
                        'strength': learning.pattern.strength,
                        'confidence': learning.pattern.confidence
                    },
                    confidence_intervals={'lower': 0.7, 'upper': 0.95},
                    suggested_metrics=learning.metrics
                )
                
                self.active_protocols[protocol.protocol_id] = protocol
                
                # Execute experiment
                results = await self.sophia_bridge.execute_experiment(protocol)
                return results
                
        except Exception as e:
            logger.error(f"Sophia learning failed: {e}")
            
        return None
        
    async def _process_research_results(self, request: ResearchRequest, results: Dict[str, Any]):
        """Process research results from Noesis"""
        logger.info(f"Processing research results for {request.id}")
        
        # Send results back to Engram UI
        await self.broadcast_to_engram({
            'type': 'research_complete',
            'request_id': request.id,
            'results': results,
            'pattern': asdict(request.source_pattern) if request.source_pattern else None,
            'insight': asdict(request.source_insight) if request.source_insight else None
        })
        
    async def _process_learning_results(self, request: LearningRequest, results: Dict[str, Any]):
        """Process learning results from Sophia"""
        logger.info(f"Processing learning results for {request.id}")
        
        # Update pattern with learning results
        if request.pattern.id in self.active_patterns:
            pattern = self.active_patterns[request.pattern.id]
            pattern.strength = results.get('validated_strength', pattern.strength)
            pattern.confidence = results.get('confidence', pattern.confidence)
            
        # Send results back to Engram UI
        await self.broadcast_to_engram({
            'type': 'learning_complete',
            'request_id': request.id,
            'pattern': asdict(request.pattern),
            'results': results
        })
        
    async def broadcast_to_engram(self, data: Dict[str, Any]):
        """Broadcast data to Engram UI"""
        # This would send data through WebSocket to Engram UI
        logger.info(f"Broadcasting to Engram: {data.get('type')}")
        # Implementation would depend on actual WebSocket setup
        
    def _generate_blindspot_query(self, insight: CognitiveInsight) -> str:
        """Generate query to address blindspot"""
        keywords = insight.content.split()[:5]
        return f"avoid {' '.join(keywords)} common mistakes best practices"
        
    def _map_confidence(self, confidence_str: str) -> float:
        """Map confidence string to float value"""
        mapping = {
            'random_thought': 0.2,
            'exploring': 0.4,
            'developing': 0.6,
            'confident': 0.8,
            'certain': 1.0
        }
        return mapping.get(confidence_str, 0.5)
        
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive bridge status including all engines"""
        athena_status = {}
        if self.athena_bridge:
            athena_status = await self.athena_bridge.get_status()
            
        return {
            'connected': {
                'sophia_legacy': self.sophia_component is not None,
                'noesis_legacy': self.noesis_component is not None,
                'sophia_engine': self.learning_engine is not None,
                'noesis_engine': self.discovery_engine is not None,
                'athena_bridge': self.athena_bridge is not None,
                'sophia_bridge': self.sophia_bridge is not None
            },
            'engines': {
                'discovery': 'active' if self.discovery_engine else 'inactive',
                'learning': 'active' if self.learning_engine else 'inactive',
                'knowledge_graph': athena_status.get('status', 'unknown')
            },
            'statistics': self.stats,
            'active_patterns': len(self.active_patterns),
            'cached_insights': len(self.insights_cache),
            'research_queue_size': self.research_queue.qsize(),
            'learning_queue_size': self.learning_queue.qsize(),
            'active_protocols': len(self.active_protocols),
            'knowledge_graph': athena_status.get('knowledge_graph', {})
        }


# Singleton instance
_bridge_instance: Optional[EngramCognitiveBridge] = None


async def get_cognitive_bridge() -> EngramCognitiveBridge:
    """Get or create the cognitive bridge instance"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = EngramCognitiveBridge()
        await _bridge_instance.initialize()
    return _bridge_instance