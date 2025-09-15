"""
Noesis Discovery Engine
Full implementation of pattern discovery, research, and theory generation
"""

import asyncio
import logging
import json
import hashlib
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from collections import defaultdict, Counter
from enum import Enum
import numpy as np
from pathlib import Path
import pickle
import sqlite3
import re

logger = logging.getLogger(__name__)


class DiscoveryType(Enum):
    PATTERN = "pattern"
    CAUSALITY = "causality"
    CORRELATION = "correlation"
    ANOMALY = "anomaly"
    OPTIMIZATION = "optimization"
    THEORY = "theory"


class ResearchStrategy(Enum):
    DEPTH_FIRST = "depth_first"
    BREADTH_FIRST = "breadth_first"
    HEURISTIC = "heuristic"
    MONTE_CARLO = "monte_carlo"
    EVOLUTIONARY = "evolutionary"


@dataclass
class Discovery:
    """Represents a discovery made by Noesis"""
    id: str
    type: DiscoveryType
    query: str  # Added for compatibility
    summary: str
    findings: List[str]  # Added for compatibility
    evidence: List[Dict[str, Any]]
    confidence: float
    novelty: float  # 0-1 scale of how new this is
    impact: float  # 0-1 scale of potential impact
    sources: List[str]  # Added for compatibility
    source_query: str
    discovered_at: datetime
    timestamp: datetime = field(default_factory=datetime.now)  # Added alias
    patterns: List[str] = field(default_factory=list)  # Renamed from related_patterns
    related_patterns: List[str] = field(default_factory=list)
    causal_chain: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'type': self.type.value,
            'summary': self.summary,
            'evidence': self.evidence,
            'confidence': self.confidence,
            'novelty': self.novelty,
            'impact': self.impact,
            'source_query': self.source_query,
            'discovered_at': self.discovered_at.isoformat(),
            'related_patterns': self.related_patterns,
            'causal_chain': self.causal_chain,
            'metadata': self.metadata
        }


@dataclass
class Pattern:
    """Represents a discovered pattern"""
    id: str
    name: str
    description: str
    occurrences: List[Dict[str, Any]]
    confidence: float
    support: int
    relationships: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass  
class Theory:
    """Represents a theory generated from patterns"""
    id: str
    hypothesis: str
    description: str
    supporting_evidence: List[str]
    confidence: float
    testable_predictions: List[str]
    created_at: datetime = field(default_factory=datetime.now)
    validated: bool = False


@dataclass
class TheoryModel:
    """Represents a theoretical model built from discoveries"""
    id: str
    name: str
    hypothesis: str
    supporting_discoveries: List[str]
    predictions: List[Dict[str, Any]]
    confidence: float
    test_results: List[Dict[str, Any]] = field(default_factory=list)
    refinements: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def predict(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make a prediction based on this theory"""
        # Apply theory rules to context
        prediction = {
            'theory_id': self.id,
            'context': context,
            'predicted_outcome': None,
            'confidence': self.confidence,
            'reasoning': []
        }
        
        for pred_rule in self.predictions:
            if self._matches_context(pred_rule['condition'], context):
                prediction['predicted_outcome'] = pred_rule['outcome']
                prediction['reasoning'].append(pred_rule['reasoning'])
                
        return prediction
    
    def _matches_context(self, condition: Dict, context: Dict) -> bool:
        """Check if context matches condition"""
        for key, value in condition.items():
            if key not in context or context[key] != value:
                return False
        return True


class PatternGraph:
    """Graph structure for pattern relationships"""
    
    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: Dict[str, Set[Tuple[str, float, str]]] = defaultdict(set)
        self.reverse_edges: Dict[str, Set[str]] = defaultdict(set)
        
    def add_pattern(self, pattern_id: str, pattern_data: Dict[str, Any]):
        """Add a pattern node to the graph"""
        self.nodes[pattern_id] = {
            'data': pattern_data,
            'discovered_at': datetime.now(),
            'strength': pattern_data.get('strength', 0.5),
            'frequency': 1
        }
        
    def add_relationship(self, from_pattern: str, to_pattern: str, 
                         strength: float, relationship_type: str):
        """Add a directed edge between patterns"""
        self.edges[from_pattern].add((to_pattern, strength, relationship_type))
        self.reverse_edges[to_pattern].add(from_pattern)
        
    def find_causal_chains(self, start_pattern: str, max_depth: int = 5) -> List[List[str]]:
        """Find causal chains starting from a pattern"""
        chains = []
        
        def dfs(current: str, path: List[str], depth: int):
            if depth >= max_depth:
                chains.append(path.copy())
                return
                
            for next_pattern, strength, rel_type in self.edges.get(current, []):
                if rel_type == 'causes' and next_pattern not in path:
                    path.append(next_pattern)
                    dfs(next_pattern, path, depth + 1)
                    path.pop()
                    
        dfs(start_pattern, [start_pattern], 0)
        return chains
        
    def find_correlations(self, pattern_id: str, min_strength: float = 0.5) -> List[Tuple[str, float]]:
        """Find patterns correlated with given pattern"""
        correlations = []
        
        for other_id, edges in self.edges.items():
            for target, strength, rel_type in edges:
                if target == pattern_id and rel_type == 'correlates' and strength >= min_strength:
                    correlations.append((other_id, strength))
                    
        return sorted(correlations, key=lambda x: x[1], reverse=True)
        
    def detect_cycles(self) -> List[List[str]]:
        """Detect cyclic patterns in the graph"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for next_node, _, _ in self.edges.get(node, []):
                if next_node not in visited:
                    if dfs(next_node, path):
                        return True
                elif next_node in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(next_node)
                    cycles.append(path[cycle_start:] + [next_node])
                    
            path.pop()
            rec_stack.remove(node)
            return False
            
        for node in self.nodes:
            if node not in visited:
                dfs(node, [])
                
        return cycles


class ResearchEngine:
    """Engine for conducting research and discovery"""
    
    def __init__(self, knowledge_base_path: str = None):
        self.knowledge_base_path = knowledge_base_path or "noesis_knowledge.db"
        self.init_database()
        self.pattern_graph = PatternGraph()
        self.theories: Dict[str, TheoryModel] = {}
        self.discovery_cache: Dict[str, Discovery] = {}
        self.research_history: List[Dict[str, Any]] = []
        
    def init_database(self):
        """Initialize SQLite database for persistence"""
        self.conn = sqlite3.connect(self.knowledge_base_path)
        cursor = self.conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS discoveries (
                id TEXT PRIMARY KEY,
                type TEXT,
                summary TEXT,
                evidence TEXT,
                confidence REAL,
                novelty REAL,
                impact REAL,
                source_query TEXT,
                discovered_at TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                frequency INTEGER,
                strength REAL,
                state TEXT,
                first_seen TIMESTAMP,
                last_seen TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS theories (
                id TEXT PRIMARY KEY,
                name TEXT,
                hypothesis TEXT,
                confidence REAL,
                created_at TIMESTAMP,
                test_count INTEGER,
                success_rate REAL,
                metadata TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS causal_relationships (
                from_pattern TEXT,
                to_pattern TEXT,
                strength REAL,
                evidence_count INTEGER,
                discovered_at TIMESTAMP,
                PRIMARY KEY (from_pattern, to_pattern)
            )
        ''')
        
        self.conn.commit()
        
    async def research(self, query: str, context: Dict[str, Any], 
                       strategy: ResearchStrategy = ResearchStrategy.HEURISTIC) -> Discovery:
        """
        Conduct research based on query and context
        
        Args:
            query: Research query
            context: Context information including patterns, insights
            strategy: Research strategy to use
            
        Returns:
            Discovery object with findings
        """
        logger.info(f"Researching: {query} with strategy {strategy.value}")
        
        # Record research attempt
        self.research_history.append({
            'query': query,
            'context': context,
            'strategy': strategy.value,
            'timestamp': datetime.now()
        })
        
        # Check cache first
        query_hash = hashlib.md5(f"{query}{json.dumps(context, sort_keys=True)}".encode()).hexdigest()
        if query_hash in self.discovery_cache:
            cached = self.discovery_cache[query_hash]
            if (datetime.now() - cached.discovered_at).seconds < 3600:  # 1 hour cache
                logger.info("Returning cached discovery")
                return cached
                
        # Execute research based on strategy
        if strategy == ResearchStrategy.DEPTH_FIRST:
            discovery = await self._depth_first_search(query, context)
        elif strategy == ResearchStrategy.BREADTH_FIRST:
            discovery = await self._breadth_first_search(query, context)
        elif strategy == ResearchStrategy.HEURISTIC:
            discovery = await self._heuristic_search(query, context)
        elif strategy == ResearchStrategy.MONTE_CARLO:
            discovery = await self._monte_carlo_search(query, context)
        else:
            discovery = await self._evolutionary_search(query, context)
            
        # Cache and persist discovery
        self.discovery_cache[query_hash] = discovery
        self._persist_discovery(discovery)
        
        # Update pattern graph
        if 'pattern' in context:
            self._update_pattern_graph(context['pattern'], discovery)
            
        return discovery
        
    async def _heuristic_search(self, query: str, context: Dict[str, Any]) -> Discovery:
        """
        Heuristic-based research using pattern matching and knowledge base
        """
        # Extract key concepts from query
        concepts = self._extract_concepts(query)
        
        # Search knowledge base for related patterns
        related_patterns = self._search_patterns(concepts)
        
        # Analyze context for insights
        insights = self._analyze_context(context)
        
        # Look for causal relationships
        causal_chains = []
        if 'pattern' in context and context['pattern'].get('id'):
            pattern_id = context['pattern']['id']
            if pattern_id in self.pattern_graph.nodes:
                causal_chains = self.pattern_graph.find_causal_chains(pattern_id)
                
        # Synthesize findings
        evidence = []
        
        # Add pattern-based evidence
        for pattern in related_patterns[:5]:
            evidence.append({
                'type': 'pattern',
                'pattern_id': pattern['id'],
                'relevance': pattern['relevance'],
                'description': pattern['description']
            })
            
        # Add causal evidence
        for chain in causal_chains[:3]:
            evidence.append({
                'type': 'causal_chain',
                'chain': chain,
                'strength': self._calculate_chain_strength(chain)
            })
            
        # Add insight-based evidence
        for insight in insights:
            evidence.append({
                'type': 'insight',
                'content': insight['content'],
                'confidence': insight['confidence']
            })
            
        # Generate discovery
        discovery_type = self._determine_discovery_type(query, evidence)
        summary = self._generate_summary(query, evidence)
        confidence = self._calculate_confidence(evidence)
        novelty = self._calculate_novelty(query, related_patterns)
        impact = self._estimate_impact(context, evidence)
        
        discovery = Discovery(
            id=f"discovery_{datetime.now().timestamp()}",
            type=discovery_type,
            summary=summary,
            evidence=evidence,
            confidence=confidence,
            novelty=novelty,
            impact=impact,
            source_query=query,
            discovered_at=datetime.now(),
            related_patterns=[p['id'] for p in related_patterns[:5]],
            causal_chain=causal_chains[0] if causal_chains else [],
            metadata={
                'concepts': concepts,
                'strategy': 'heuristic',
                'insights_count': len(insights)
            }
        )
        
        return discovery
        
    async def _depth_first_search(self, query: str, context: Dict[str, Any]) -> Discovery:
        """
        Depth-first search strategy - explore one path deeply
        """
        concepts = self._extract_concepts(query)
        
        # Start with most relevant concept
        if concepts:
            primary_concept = concepts[0]
            
            # Deep dive into this concept
            deep_patterns = self._deep_search_concept(primary_concept, max_depth=10)
            
            # Find root causes
            root_causes = self._find_root_causes(primary_concept, context)
            
            evidence = [
                {'type': 'deep_pattern', 'patterns': deep_patterns},
                {'type': 'root_causes', 'causes': root_causes}
            ]
            
            return Discovery(
                id=f"discovery_{datetime.now().timestamp()}",
                type=DiscoveryType.CAUSALITY,
                summary=f"Deep analysis of {primary_concept} reveals {len(root_causes)} root causes",
                evidence=evidence,
                confidence=0.7 + (0.3 * min(len(root_causes) / 5, 1)),
                novelty=self._calculate_novelty(query, deep_patterns),
                impact=0.8,
                source_query=query,
                discovered_at=datetime.now(),
                causal_chain=root_causes[:5]
            )
            
        return await self._heuristic_search(query, context)
        
    async def _breadth_first_search(self, query: str, context: Dict[str, Any]) -> Discovery:
        """
        Breadth-first search strategy - explore many paths shallowly
        """
        concepts = self._extract_concepts(query)
        
        # Explore all concepts equally
        all_patterns = []
        for concept in concepts[:5]:
            patterns = self._search_patterns([concept])
            all_patterns.extend(patterns[:3])
            
        # Find correlations across patterns
        correlations = self._find_correlations(all_patterns)
        
        evidence = [
            {'type': 'broad_patterns', 'patterns': all_patterns},
            {'type': 'correlations', 'correlations': correlations}
        ]
        
        return Discovery(
            id=f"discovery_{datetime.now().timestamp()}",
            type=DiscoveryType.CORRELATION,
            summary=f"Broad analysis found {len(correlations)} correlations across {len(all_patterns)} patterns",
            evidence=evidence,
            confidence=0.6 + (0.4 * min(len(correlations) / 10, 1)),
            novelty=0.5,
            impact=0.6,
            source_query=query,
            discovered_at=datetime.now(),
            related_patterns=[p['id'] for p in all_patterns]
        )
        
    async def _monte_carlo_search(self, query: str, context: Dict[str, Any]) -> Discovery:
        """
        Monte Carlo search - random sampling to find patterns
        """
        concepts = self._extract_concepts(query)
        samples = []
        
        # Run random simulations
        for _ in range(100):
            sample_result = self._random_exploration(concepts, context)
            samples.append(sample_result)
            
        # Analyze sample results
        pattern_frequency = Counter()
        for sample in samples:
            for pattern in sample.get('patterns', []):
                pattern_frequency[pattern] += 1
                
        # Most frequent patterns are likely significant
        significant_patterns = pattern_frequency.most_common(5)
        
        evidence = [
            {'type': 'monte_carlo', 'samples': len(samples)},
            {'type': 'significant_patterns', 'patterns': significant_patterns}
        ]
        
        return Discovery(
            id=f"discovery_{datetime.now().timestamp()}",
            type=DiscoveryType.PATTERN,
            summary=f"Monte Carlo sampling ({len(samples)} runs) identified {len(significant_patterns)} significant patterns",
            evidence=evidence,
            confidence=0.7,
            novelty=0.6,
            impact=0.7,
            source_query=query,
            discovered_at=datetime.now()
        )
        
    async def _evolutionary_search(self, query: str, context: Dict[str, Any]) -> Discovery:
        """
        Evolutionary search - evolve solutions over generations
        """
        concepts = self._extract_concepts(query)
        
        # Initialize population of hypotheses
        population = self._generate_initial_hypotheses(concepts, context)
        
        # Evolve over generations
        for generation in range(10):
            # Evaluate fitness
            scored_pop = [(h, self._evaluate_hypothesis(h, context)) for h in population]
            scored_pop.sort(key=lambda x: x[1], reverse=True)
            
            # Select best
            survivors = [h for h, _ in scored_pop[:len(population)//2]]
            
            # Mutate and crossover
            population = self._evolve_population(survivors)
            
        # Best hypothesis is our discovery
        best_hypothesis = scored_pop[0][0]
        
        evidence = [
            {'type': 'evolved_hypothesis', 'hypothesis': best_hypothesis},
            {'type': 'generations', 'value': 10},
            {'type': 'fitness', 'value': scored_pop[0][1]}
        ]
        
        return Discovery(
            id=f"discovery_{datetime.now().timestamp()}",
            type=DiscoveryType.THEORY,
            summary=f"Evolved hypothesis: {best_hypothesis['summary']}",
            evidence=evidence,
            confidence=scored_pop[0][1],
            novelty=0.8,
            impact=0.9,
            source_query=query,
            discovered_at=datetime.now()
        )
        
    def build_theory(self, discoveries: List[Discovery], hypothesis: str) -> TheoryModel:
        """
        Build a theoretical model from discoveries
        """
        theory_id = f"theory_{datetime.now().timestamp()}"
        
        # Extract predictions from discoveries
        predictions = []
        for discovery in discoveries:
            if discovery.type == DiscoveryType.CAUSALITY:
                for cause in discovery.causal_chain:
                    predictions.append({
                        'condition': {'pattern': cause},
                        'outcome': discovery.summary,
                        'reasoning': f"Based on discovery {discovery.id}"
                    })
                    
        # Calculate theory confidence
        confidence = np.mean([d.confidence for d in discoveries])
        
        theory = TheoryModel(
            id=theory_id,
            name=f"Theory: {hypothesis[:50]}",
            hypothesis=hypothesis,
            supporting_discoveries=[d.id for d in discoveries],
            predictions=predictions,
            confidence=confidence
        )
        
        self.theories[theory_id] = theory
        self._persist_theory(theory)
        
        return theory
        
    def test_theory(self, theory: TheoryModel, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test a theory against a specific case
        """
        prediction = theory.predict(test_case)
        
        # Record test result
        test_result = {
            'test_id': f"test_{datetime.now().timestamp()}",
            'theory_id': theory.id,
            'test_case': test_case,
            'prediction': prediction,
            'timestamp': datetime.now().isoformat()
        }
        
        theory.test_results.append(test_result)
        
        # Update theory confidence based on results
        if 'actual_outcome' in test_case:
            if prediction['predicted_outcome'] == test_case['actual_outcome']:
                theory.confidence = min(1.0, theory.confidence * 1.1)
            else:
                theory.confidence = max(0.1, theory.confidence * 0.9)
                
        self._persist_theory(theory)
        
        return test_result
        
    def find_anomalies(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect anomalies in patterns
        """
        anomalies = []
        
        # Statistical anomaly detection
        if patterns:
            strengths = [p.get('strength', 0) for p in patterns]
            mean_strength = np.mean(strengths)
            std_strength = np.std(strengths)
            
            for pattern in patterns:
                strength = pattern.get('strength', 0)
                z_score = (strength - mean_strength) / (std_strength + 1e-6)
                
                if abs(z_score) > 2:  # 2 standard deviations
                    anomalies.append({
                        'pattern': pattern,
                        'anomaly_type': 'statistical',
                        'z_score': z_score,
                        'severity': min(abs(z_score) / 3, 1.0)
                    })
                    
        # Temporal anomalies
        for pattern in patterns:
            if 'timestamp' in pattern:
                # Check for unusual timing
                hour = datetime.fromisoformat(pattern['timestamp']).hour
                if hour < 6 or hour > 22:  # Unusual hours
                    anomalies.append({
                        'pattern': pattern,
                        'anomaly_type': 'temporal',
                        'unusual_hour': hour,
                        'severity': 0.3
                    })
                    
        return anomalies
        
    def optimize_approach(self, problem: Dict[str, Any], 
                         constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find optimal approach to a problem given constraints
        """
        # Search for similar problems
        similar_problems = self._find_similar_problems(problem)
        
        # Extract successful solutions
        solutions = []
        for similar in similar_problems:
            if 'solution' in similar and similar.get('success', False):
                solutions.append({
                    'approach': similar['solution'],
                    'effectiveness': similar.get('effectiveness', 0.5),
                    'cost': similar.get('cost', 1.0)
                })
                
        # Optimize based on constraints
        if 'max_time' in constraints:
            solutions = [s for s in solutions if s.get('cost', 1.0) <= constraints['max_time']]
            
        if 'min_confidence' in constraints:
            solutions = [s for s in solutions if s.get('effectiveness', 0) >= constraints['min_confidence']]
            
        # Rank solutions
        solutions.sort(key=lambda x: x['effectiveness'] / (x['cost'] + 0.1), reverse=True)
        
        if solutions:
            best_solution = solutions[0]
            return {
                'optimization': 'success',
                'recommended_approach': best_solution['approach'],
                'expected_effectiveness': best_solution['effectiveness'],
                'expected_cost': best_solution['cost'],
                'alternatives': solutions[1:3]
            }
        else:
            return {
                'optimization': 'no_solution',
                'reason': 'No solutions found within constraints',
                'suggestion': 'Relax constraints or explore novel approaches'
            }
            
    # Helper methods
    
    def _extract_concepts(self, query: str) -> List[str]:
        """Extract key concepts from query"""
        # Remove common words
        stop_words = {'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'of', 'in', 'to', 'for'}
        words = query.lower().split()
        concepts = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Look for compound concepts
        bigrams = [f"{words[i]}_{words[i+1]}" for i in range(len(words)-1)]
        
        return concepts + bigrams
        
    def _search_patterns(self, concepts: List[str]) -> List[Dict[str, Any]]:
        """Search knowledge base for patterns matching concepts"""
        cursor = self.conn.cursor()
        patterns = []
        
        for concept in concepts:
            cursor.execute('''
                SELECT id, name, description, strength, frequency
                FROM patterns
                WHERE name LIKE ? OR description LIKE ?
                ORDER BY strength DESC, frequency DESC
                LIMIT 10
            ''', (f'%{concept}%', f'%{concept}%'))
            
            for row in cursor.fetchall():
                patterns.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'strength': row[3],
                    'frequency': row[4],
                    'relevance': self._calculate_relevance(concept, row[1], row[2])
                })
                
        # Sort by relevance
        patterns.sort(key=lambda x: x['relevance'], reverse=True)
        return patterns
        
    def _calculate_relevance(self, concept: str, name: str, description: str) -> float:
        """Calculate relevance score"""
        score = 0.0
        concept_lower = concept.lower()
        
        if concept_lower in name.lower():
            score += 0.5
        if concept_lower in description.lower():
            score += 0.3
            
        # Check for partial matches
        for word in concept_lower.split('_'):
            if word in name.lower():
                score += 0.1
            if word in description.lower():
                score += 0.05
                
        return min(score, 1.0)
        
    def _analyze_context(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze context for insights"""
        insights = []
        
        # Pattern analysis
        if 'pattern' in context:
            pattern = context['pattern']
            
            # Check pattern strength
            if pattern.get('strength', 0) > 0.8:
                insights.append({
                    'content': f"Strong pattern detected: {pattern.get('name', 'Unknown')}",
                    'confidence': 0.9
                })
                
            # Check pattern state
            if pattern.get('state') == 'emerging':
                insights.append({
                    'content': 'Pattern is emerging - early intervention possible',
                    'confidence': 0.7
                })
                
        # Insight analysis
        if 'insight' in context:
            insight = context['insight']
            
            if insight.get('type') == 'blindspot':
                insights.append({
                    'content': f"Blindspot identified: {insight.get('content', '')}",
                    'confidence': 0.8
                })
                
        return insights
        
    def _calculate_chain_strength(self, chain: List[str]) -> float:
        """Calculate strength of a causal chain"""
        if not chain or len(chain) < 2:
            return 0.0
            
        total_strength = 1.0
        
        for i in range(len(chain) - 1):
            from_pattern = chain[i]
            to_pattern = chain[i + 1]
            
            # Find edge strength
            for target, strength, rel_type in self.pattern_graph.edges.get(from_pattern, []):
                if target == to_pattern and rel_type == 'causes':
                    total_strength *= strength
                    break
            else:
                total_strength *= 0.5  # Weak link
                
        return total_strength
        
    def _determine_discovery_type(self, query: str, evidence: List[Dict]) -> DiscoveryType:
        """Determine type of discovery based on evidence"""
        evidence_types = [e.get('type') for e in evidence]
        
        if 'causal_chain' in evidence_types:
            return DiscoveryType.CAUSALITY
        elif 'correlation' in evidence_types:
            return DiscoveryType.CORRELATION
        elif 'anomaly' in evidence_types:
            return DiscoveryType.ANOMALY
        elif 'optimization' in query.lower():
            return DiscoveryType.OPTIMIZATION
        elif 'theory' in evidence_types or 'hypothesis' in evidence_types:
            return DiscoveryType.THEORY
        else:
            return DiscoveryType.PATTERN
            
    def _generate_summary(self, query: str, evidence: List[Dict]) -> str:
        """Generate summary of discovery"""
        if not evidence:
            return f"No significant findings for query: {query}"
            
        evidence_count = len(evidence)
        primary_evidence = evidence[0] if evidence else {}
        
        if primary_evidence.get('type') == 'pattern':
            return f"Discovered {evidence_count} patterns related to {query}"
        elif primary_evidence.get('type') == 'causal_chain':
            chain = primary_evidence.get('chain', [])
            return f"Found causal chain: {' → '.join(chain[:3])}"
        elif primary_evidence.get('type') == 'insight':
            return primary_evidence.get('content', f"Insight discovered for {query}")
        else:
            return f"Analysis complete with {evidence_count} findings for {query}"
            
    def _calculate_confidence(self, evidence: List[Dict]) -> float:
        """Calculate confidence score based on evidence"""
        if not evidence:
            return 0.1
            
        base_confidence = 0.5
        
        # More evidence increases confidence
        evidence_bonus = min(len(evidence) * 0.1, 0.3)
        
        # Strong evidence types boost confidence
        for e in evidence:
            if e.get('type') == 'causal_chain':
                base_confidence += 0.1
            elif e.get('type') == 'pattern' and e.get('relevance', 0) > 0.8:
                base_confidence += 0.05
                
        return min(base_confidence + evidence_bonus, 0.95)
        
    def _calculate_novelty(self, query: str, patterns: List[Dict]) -> float:
        """Calculate how novel this discovery is"""
        # Check if query has been researched before
        recent_research = [r for r in self.research_history[-100:] 
                          if r['query'] == query]
        
        if recent_research:
            return 0.2  # Not novel if recently researched
            
        # Check pattern frequencies
        if patterns:
            avg_frequency = np.mean([p.get('frequency', 1) for p in patterns])
            if avg_frequency < 5:
                return 0.8  # Novel if patterns are rare
            elif avg_frequency < 20:
                return 0.5
            else:
                return 0.3
                
        return 0.6  # Default novelty
        
    def _estimate_impact(self, context: Dict, evidence: List[Dict]) -> float:
        """Estimate potential impact of discovery"""
        impact = 0.5  # Base impact
        
        # High-severity issues have high impact
        if 'insight' in context:
            severity = context['insight'].get('severity', 'medium')
            if severity == 'high':
                impact += 0.3
            elif severity == 'critical':
                impact += 0.4
                
        # Causal discoveries have high impact
        for e in evidence:
            if e.get('type') == 'causal_chain':
                impact += 0.2
                break
                
        # Optimization opportunities have high impact
        if 'inefficiency' in str(context):
            impact += 0.2
            
        return min(impact, 1.0)
        
    def _update_pattern_graph(self, pattern: Dict[str, Any], discovery: Discovery):
        """Update pattern graph with new discovery"""
        pattern_id = pattern.get('id', f"pattern_{datetime.now().timestamp()}")
        
        # Add pattern to graph if not exists
        if pattern_id not in self.pattern_graph.nodes:
            self.pattern_graph.add_pattern(pattern_id, pattern)
            
        # Add relationships from discovery
        for related_id in discovery.related_patterns:
            if related_id != pattern_id:
                self.pattern_graph.add_relationship(
                    pattern_id, related_id, 
                    discovery.confidence, 'discovered_with'
                )
                
        # Add causal relationships
        if discovery.causal_chain:
            for i in range(len(discovery.causal_chain) - 1):
                self.pattern_graph.add_relationship(
                    discovery.causal_chain[i],
                    discovery.causal_chain[i + 1],
                    discovery.confidence,
                    'causes'
                )
                
    def _deep_search_concept(self, concept: str, max_depth: int) -> List[Dict]:
        """Deep search for a concept"""
        patterns = []
        visited = set()
        
        def search(current_concept: str, depth: int):
            if depth >= max_depth or current_concept in visited:
                return
                
            visited.add(current_concept)
            
            # Search for patterns
            found = self._search_patterns([current_concept])
            patterns.extend(found)
            
            # Extract related concepts and recurse
            for pattern in found[:2]:  # Limit branching
                related = self._extract_concepts(pattern.get('description', ''))
                for rel_concept in related[:2]:
                    search(rel_concept, depth + 1)
                    
        search(concept, 0)
        return patterns
        
    def _find_root_causes(self, concept: str, context: Dict) -> List[str]:
        """Find root causes for a concept"""
        root_causes = []
        
        # Look for causal patterns in database
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT from_pattern
            FROM causal_relationships
            WHERE to_pattern LIKE ?
            ORDER BY strength DESC
            LIMIT 5
        ''', (f'%{concept}%',))
        
        for row in cursor.fetchall():
            root_causes.append(row[0])
            
        return root_causes
        
    def _find_correlations(self, patterns: List[Dict]) -> List[Dict]:
        """Find correlations between patterns"""
        correlations = []
        
        for i, p1 in enumerate(patterns):
            for p2 in patterns[i+1:]:
                # Calculate correlation based on co-occurrence
                correlation = self._calculate_correlation(p1, p2)
                if correlation > 0.5:
                    correlations.append({
                        'pattern1': p1['id'],
                        'pattern2': p2['id'],
                        'correlation': correlation
                    })
                    
        return correlations
        
    def _calculate_correlation(self, p1: Dict, p2: Dict) -> float:
        """Calculate correlation between two patterns"""
        # Simple correlation based on shared concepts
        concepts1 = set(self._extract_concepts(p1.get('description', '')))
        concepts2 = set(self._extract_concepts(p2.get('description', '')))
        
        if not concepts1 or not concepts2:
            return 0.0
            
        intersection = concepts1.intersection(concepts2)
        union = concepts1.union(concepts2)
        
        return len(intersection) / len(union)
        
    def _random_exploration(self, concepts: List[str], context: Dict) -> Dict:
        """Random exploration for Monte Carlo"""
        import random
        
        # Randomly select concepts to explore
        selected = random.sample(concepts, min(3, len(concepts)))
        
        patterns = []
        for concept in selected:
            found = self._search_patterns([concept])
            if found:
                patterns.append(found[0]['id'])
                
        return {'patterns': patterns}
        
    def _generate_initial_hypotheses(self, concepts: List[str], context: Dict) -> List[Dict]:
        """Generate initial hypotheses for evolutionary search"""
        hypotheses = []
        
        for concept in concepts[:5]:
            hypothesis = {
                'id': f"hyp_{concept}_{datetime.now().timestamp()}",
                'summary': f"{concept} is caused by system complexity",
                'concepts': [concept],
                'confidence': 0.5
            }
            hypotheses.append(hypothesis)
            
        return hypotheses
        
    def _evaluate_hypothesis(self, hypothesis: Dict, context: Dict) -> float:
        """Evaluate fitness of a hypothesis"""
        score = hypothesis.get('confidence', 0.5)
        
        # Check if hypothesis concepts appear in context
        for concept in hypothesis.get('concepts', []):
            if concept in str(context):
                score += 0.1
                
        return min(score, 1.0)
        
    def _evolve_population(self, survivors: List[Dict]) -> List[Dict]:
        """Evolve population through mutation and crossover"""
        import random
        new_population = survivors.copy()
        
        # Mutation
        for hypothesis in survivors:
            if random.random() < 0.3:  # 30% mutation rate
                mutated = hypothesis.copy()
                mutated['confidence'] *= random.uniform(0.8, 1.2)
                mutated['summary'] += " (evolved)"
                new_population.append(mutated)
                
        return new_population
        
    def _find_similar_problems(self, problem: Dict) -> List[Dict]:
        """Find similar problems in history"""
        similar = []
        
        problem_str = json.dumps(problem, sort_keys=True)
        
        for hist in self.research_history:
            if 'context' in hist and 'problem' in hist['context']:
                hist_problem_str = json.dumps(hist['context']['problem'], sort_keys=True)
                
                # Simple similarity based on string comparison
                similarity = self._string_similarity(problem_str, hist_problem_str)
                
                if similarity > 0.5:
                    similar.append(hist['context']['problem'])
                    
        return similar
        
    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity"""
        # Simple character-based similarity
        longer = max(len(s1), len(s2))
        if longer == 0:
            return 1.0
            
        # Count matching characters
        matches = sum(c1 == c2 for c1, c2 in zip(s1, s2))
        
        return matches / longer
        
    def _persist_discovery(self, discovery: Discovery):
        """Persist discovery to database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO discoveries
            (id, type, summary, evidence, confidence, novelty, impact, source_query, discovered_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            discovery.id,
            discovery.type.value,
            discovery.summary,
            json.dumps(discovery.evidence),
            discovery.confidence,
            discovery.novelty,
            discovery.impact,
            discovery.source_query,
            discovery.discovered_at.isoformat(),
            json.dumps(discovery.metadata)
        ))
        self.conn.commit()
        
    def _persist_theory(self, theory: TheoryModel):
        """Persist theory to database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO theories
            (id, name, hypothesis, confidence, created_at, test_count, success_rate, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            theory.id,
            theory.name,
            theory.hypothesis,
            theory.confidence,
            theory.created_at.isoformat(),
            len(theory.test_results),
            self._calculate_success_rate(theory),
            json.dumps({
                'predictions': theory.predictions,
                'supporting_discoveries': theory.supporting_discoveries,
                'refinements': theory.refinements
            })
        ))
        self.conn.commit()
        
    def _calculate_success_rate(self, theory: TheoryModel) -> float:
        """Calculate success rate of theory predictions"""
        if not theory.test_results:
            return 0.0
            
        successful = sum(1 for test in theory.test_results 
                        if test.get('prediction', {}).get('predicted_outcome') == 
                           test.get('test_case', {}).get('actual_outcome'))
                           
        return successful / len(theory.test_results)


# Singleton instance
_discovery_engine = None

def get_discovery_engine() -> ResearchEngine:
    """Get or create discovery engine instance"""
    global _discovery_engine
    if _discovery_engine is None:
        _discovery_engine = ResearchEngine()
    return _discovery_engine


class DiscoveryEngine:
    """Main interface for the Noesis Discovery Engine"""
    
    def __init__(self):
        self.research_engine = None
        self.pattern_graph = None
        self.theory_generator = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize all discovery components"""
        self.research_engine = get_discovery_engine()
        self.pattern_graph = PatternGraph()
        self.theory_generator = TheoryGenerator()
        
        await self.research_engine.initialize()
        await self.pattern_graph.initialize()
        await self.theory_generator.initialize()
        
        self.initialized = True
        logger.info("Discovery Engine initialized")
        
    async def research(self, query: str, context: Dict[str, Any], 
                      strategy: ResearchStrategy = ResearchStrategy.HEURISTIC) -> Discovery:
        """Conduct research on a query"""
        return await self.research_engine.research(query, context, strategy)
        
    async def discover_patterns(self, data: List[Dict[str, Any]]) -> List[Pattern]:
        """Discover patterns in data"""
        discoveries = []
        for item in data:
            pattern = await self.pattern_graph.add_pattern(
                Pattern(
                    id=f"pattern_{datetime.now().timestamp()}",
                    name=item.get('name', 'Unknown'),
                    description=item.get('description', ''),
                    occurrences=[item],
                    confidence=item.get('confidence', 0.5),
                    support=1,
                    created_at=datetime.now()
                )
            )
            discoveries.append(pattern)
        return discoveries
        
    async def generate_theory(self, patterns: List[Pattern]) -> Optional[Theory]:
        """Generate a theory from patterns"""
        if not patterns:
            return None
        return await self.theory_generator.generate_from_patterns(patterns)
        
    async def get_recent_discoveries(self, hours: int = 24) -> List[Discovery]:
        """Get recent discoveries"""
        since = datetime.now() - timedelta(hours=hours)
        return [d for d in self.research_engine.discoveries.values() 
                if d.timestamp >= since]
        
    async def shutdown(self):
        """Shutdown discovery engine"""
        logger.info("Discovery Engine shutdown")


# Export classes and functions
__all__ = [
    'DiscoveryEngine',
    'ResearchStrategy',
    'Discovery',
    'Pattern',
    'Theory',
    'ResearchEngine',
    'PatternGraph',
    'TheoryGenerator',
    'get_discovery_engine'
]