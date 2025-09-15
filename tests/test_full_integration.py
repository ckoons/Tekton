#!/usr/bin/env python3
"""
Full Integration Test for Engram-Sophia-Noesis-Athena System

Tests the complete cognitive research pipeline:
1. Pattern detection in Engram
2. Research through Noesis Discovery Engine
3. Learning through Sophia Learning Engine
4. Knowledge storage in Athena/ESR Knowledge Graph
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import components
from shared.integration.engram_cognitive_bridge import (
    get_cognitive_bridge,
    CognitiveEventType,
    CognitivePattern,
    CognitiveInsight
)
from shared.integration.athena_knowledge_bridge import (
    get_knowledge_bridge,
    KnowledgeType
)
from Noesis.noesis.core.discovery_engine import ResearchStrategy
from Sophia.sophia.core.learning_engine import ExperimentType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_pattern_to_knowledge_flow():
    """Test the complete flow from pattern detection to knowledge storage"""
    
    print("\n" + "="*60)
    print("FULL INTEGRATION TEST: Engram → Noesis → Sophia → Athena")
    print("="*60 + "\n")
    
    # Initialize bridges
    print("1. Initializing bridges...")
    cognitive_bridge = await get_cognitive_bridge()
    knowledge_bridge = await get_knowledge_bridge()
    
    # Check status
    status = await cognitive_bridge.get_status()
    print(f"   Cognitive Bridge Status:")
    print(f"   - Discovery Engine: {status['engines']['discovery']}")
    print(f"   - Learning Engine: {status['engines']['learning']}")
    print(f"   - Knowledge Graph: {status['engines']['knowledge_graph']}")
    print()
    
    # Simulate pattern detection from Engram
    print("2. Simulating pattern detection from Engram UI...")
    test_pattern = {
        'id': 'test_pattern_001',
        'name': 'Recursive Problem Solving',
        'type': 'cognitive',
        'state': 'strengthening',
        'strength': 0.75,
        'confidence': 0.85,
        'novelty': 'significant',
        'description': 'User showing improved recursive thinking patterns',
        'concepts': ['recursion', 'problem-solving', 'abstraction']
    }
    
    await cognitive_bridge.process_cognitive_event(
        CognitiveEventType.PATTERN_DETECTED,
        test_pattern
    )
    print(f"   ✓ Pattern detected: {test_pattern['name']}")
    print()
    
    # Wait for processing
    await asyncio.sleep(2)
    
    # Test blindspot detection
    print("3. Simulating blindspot detection...")
    test_blindspot = {
        'text': 'Assuming synchronous operations without checking',
        'severity': 'high',
        'frequency': 5,
        'impact': 'high',
        'suggestions': ['Always check for async/await', 'Use proper error handling']
    }
    
    await cognitive_bridge.process_cognitive_event(
        CognitiveEventType.BLINDSPOT_FOUND,
        test_blindspot
    )
    print(f"   ✓ Blindspot detected: {test_blindspot['text'][:50]}...")
    print()
    
    # Direct research test
    print("4. Testing direct research through Noesis...")
    if cognitive_bridge.discovery_engine:
        discovery = await cognitive_bridge.discovery_engine.research(
            query="best practices for async programming error handling",
            context={'source': 'integration_test'},
            strategy=ResearchStrategy.BREADTH_FIRST
        )
        
        if discovery:
            print(f"   ✓ Discovery made: {discovery.id}")
            print(f"     - Confidence: {discovery.confidence:.2f}")
            print(f"     - Findings: {len(discovery.findings)} items")
            
            # Store in knowledge graph
            knowledge_id = await knowledge_bridge.store_discovery(discovery)
            print(f"   ✓ Stored in knowledge graph: {knowledge_id}")
    print()
    
    # Direct learning test
    print("5. Testing direct learning through Sophia...")
    if cognitive_bridge.learning_engine:
        experiment = await cognitive_bridge.learning_engine.create_experiment(
            name="Test Pattern Validation",
            type=ExperimentType.PATTERN_VALIDATION,
            hypothesis="Recursive problem solving improves with practice",
            control_config={'pattern': test_pattern}
        )
        
        print(f"   ✓ Experiment created: {experiment.id}")
        
        # Run experiment
        await cognitive_bridge.learning_engine.run_experiment(experiment.id)
        
        # Get results
        experiment = await cognitive_bridge.learning_engine.get_experiment(experiment.id)
        if experiment.results:
            print(f"   ✓ Experiment completed")
            print(f"     - Performance: {experiment.results.get('performance', 'N/A')}")
            
            # Store in knowledge graph
            knowledge_id = await knowledge_bridge.store_experiment(experiment)
            print(f"   ✓ Stored in knowledge graph: {knowledge_id}")
    print()
    
    # Test knowledge retrieval
    print("6. Testing knowledge retrieval...")
    related = await knowledge_bridge.retrieve_related_knowledge(
        query="recursive problem solving",
        limit=5
    )
    print(f"   ✓ Retrieved {len(related)} related knowledge items")
    for item in related[:3]:
        thought = item['thought']
        if hasattr(thought, 'content'):
            content = thought.content
            if isinstance(content, dict):
                print(f"     - Type: {content.get('type', 'unknown')}")
    print()
    
    # Test concept formation
    print("7. Simulating concept formation...")
    test_concept = {
        'id': 'concept_001',
        'name': 'Async-First Architecture',
        'vertices': [
            {'id': 'v1', 'label': 'Promise', 'type': 'technical'},
            {'id': 'v2', 'label': 'Event Loop', 'type': 'system'},
            {'id': 'v3', 'label': 'Callback', 'type': 'pattern'}
        ],
        'edges': [
            {'source': 'v1', 'target': 'v2', 'type': 'enables'},
            {'source': 'v2', 'target': 'v3', 'type': 'triggers'}
        ],
        'confidence': 0.9
    }
    
    await cognitive_bridge.process_cognitive_event(
        CognitiveEventType.CONCEPT_FORMED,
        test_concept
    )
    print(f"   ✓ Concept formed: {test_concept['name']}")
    print()
    
    # Final status check
    print("8. Final Status Check...")
    final_status = await cognitive_bridge.get_status()
    kb_status = await knowledge_bridge.get_status()
    
    print(f"   Cognitive Bridge Statistics:")
    print(f"   - Patterns Processed: {final_status['statistics']['patterns_processed']}")
    print(f"   - Insights Generated: {final_status['statistics']['insights_generated']}")
    print(f"   - Research Requests: {final_status['statistics']['research_requests']}")
    print(f"   - Learning Cycles: {final_status['statistics']['learning_cycles']}")
    print(f"   - Discoveries Made: {final_status['statistics']['discoveries_made']}")
    print()
    
    print(f"   Knowledge Graph Statistics:")
    print(f"   - Total Entries: {kb_status['knowledge_graph'].get('total_entries', 0)}")
    print(f"   - Relationships: {kb_status['knowledge_graph'].get('relationships', 0)}")
    print(f"   - Discoveries Stored: {kb_status['statistics']['discoveries_stored']}")
    print(f"   - Patterns Stored: {kb_status['statistics']['patterns_stored']}")
    print(f"   - Experiments Stored: {kb_status['statistics']['experiments_stored']}")
    print()
    
    print("="*60)
    print("INTEGRATION TEST COMPLETE")
    print("="*60)
    
    return True


async def test_cross_engine_collaboration():
    """Test collaboration between engines"""
    
    print("\n" + "="*60)
    print("CROSS-ENGINE COLLABORATION TEST")
    print("="*60 + "\n")
    
    knowledge_bridge = await get_knowledge_bridge()
    
    print("1. Testing Discovery → Learning sync...")
    await knowledge_bridge.sync_discovery_to_learning()
    print("   ✓ Discoveries synced to learning engine")
    
    print("2. Testing Learning → Discovery sync...")
    await knowledge_bridge.sync_learning_to_discovery()
    print("   ✓ Learning results synced to discovery engine")
    
    print("3. Building knowledge context...")
    context = await knowledge_bridge.build_knowledge_context(
        focal_point="async programming",
        depth=2
    )
    print(f"   ✓ Built context with {len(context)} elements")
    
    print("\n" + "="*60)
    print("COLLABORATION TEST COMPLETE")
    print("="*60)
    
    return True


async def main():
    """Run all integration tests"""
    try:
        # Run pattern to knowledge flow test
        success = await test_pattern_to_knowledge_flow()
        if not success:
            print("ERROR: Pattern to knowledge flow test failed")
            return 1
            
        # Run cross-engine collaboration test
        success = await test_cross_engine_collaboration()
        if not success:
            print("ERROR: Cross-engine collaboration test failed")
            return 1
            
        print("\n" + "="*60)
        print("ALL INTEGRATION TESTS PASSED ✓")
        print("="*60)
        return 0
        
    except Exception as e:
        logger.error(f"Integration test failed: {e}", exc_info=True)
        print(f"\nERROR: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)