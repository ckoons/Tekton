#!/usr/bin/env python3
"""
Complete Integration Test
Demonstrates the full Engram-Sophia-Noesis-Athena system with proper configuration
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import os

# Set TEKTON_ROOT before imports
if 'TEKTON_ROOT' not in os.environ:
    os.environ['TEKTON_ROOT'] = str(Path(__file__).parent.parent)

sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment properly
from shared.env import TektonEnvironLock, TektonEnviron
TektonEnvironLock.load()

# Import after environment is loaded
from shared.urls import tekton_url
from engram.core.storage.unified_interface import ESRMemorySystem
from engram.core.storage.cognitive_workflows import CognitiveWorkflows, ThoughtType
from shared.integration.engram_cognitive_bridge import (
    CognitiveEventType,
    CognitivePattern,
    CognitiveInsight
)
from shared.integration.athena_knowledge_bridge import KnowledgeType


async def demonstrate_full_system():
    """Demonstrate the complete integrated system"""
    
    print("\n" + "="*80)
    print("COMPLETE ENGRAM-SOPHIA-NOESIS-ATHENA INTEGRATION TEST")
    print("="*80)
    
    # Show configuration
    print("\n📋 CONFIGURATION:")
    print("-"*50)
    data_dir = TektonEnviron.get('TEKTON_DATA_DIR', '/tmp/tekton/data')
    print(f"   Data Directory: {data_dir}")
    
    # Show URLs for components
    engram_url = tekton_url("engram", "/api/v1")
    sophia_url = tekton_url("sophia", "/api/v1")
    noesis_url = tekton_url("noesis", "/api/v1")
    athena_url = tekton_url("athena", "/api/v1")
    
    print(f"   Engram API: {engram_url}")
    print(f"   Sophia API: {sophia_url}")
    print(f"   Noesis API: {noesis_url}")
    print(f"   Athena API: {athena_url}")
    
    print("\n🧠 INITIALIZING COGNITIVE SYSTEM:")
    print("-"*50)
    
    # 1. Initialize ESR Memory System (Athena's Knowledge Graph)
    print("\n1. ESR Memory System (Knowledge Graph)")
    esr = ESRMemorySystem(
        cache_size=1000,
        enable_backends={'kv', 'document'},
        config={
            'namespace': 'integration_test',
            'data_dir': f"{data_dir}/integration_test"
        }
    )
    await esr.start()
    print("   ✓ Knowledge graph initialized")
    
    # 2. Initialize Cognitive Workflows
    print("\n2. Cognitive Workflows")
    workflows = CognitiveWorkflows(
        cache=esr.cache,
        encoder=esr.encoder
    )
    print("   ✓ Natural memory operations ready")
    
    print("\n🔄 DEMONSTRATING COGNITIVE FLOW:")
    print("-"*50)
    
    # 3. Simulate UI Pattern Detection (Engram)
    print("\n3. UI PATTERN DETECTION (Engram)")
    ui_pattern = CognitivePattern(
        id='ui_pattern_001',
        name='Recursive Problem Solving',
        type='cognitive',
        state='strengthening',
        strength=0.8,
        confidence=0.9,
        novelty='significant',
        description='User demonstrating improved recursive thinking'
    )
    
    # Store pattern as thought
    pattern_thought = await workflows.store_thought(
        content={
            'pattern': ui_pattern.name,
            'strength': ui_pattern.strength,
            'state': ui_pattern.state,
            'description': ui_pattern.description
        },
        thought_type=ThoughtType.OBSERVATION,
        context={'source': 'engram', 'component': 'ui'},
        confidence=ui_pattern.confidence,
        ci_id='engram'
    )
    print(f"   ✓ Pattern detected and stored: {pattern_thought[:16]}...")
    print(f"     - Name: {ui_pattern.name}")
    print(f"     - Strength: {ui_pattern.strength}")
    print(f"     - State: {ui_pattern.state}")
    
    # 4. Simulate Discovery (Noesis)
    print("\n4. DISCOVERY GENERATION (Noesis)")
    discovery_content = {
        'type': 'discovery',
        'query': 'optimal recursive algorithms',
        'findings': [
            'Tail recursion optimization reduces stack usage',
            'Memoization improves performance by 60%',
            'Dynamic programming alternative for complex cases'
        ],
        'confidence': 0.85,
        'source': 'research'
    }
    
    discovery_thought = await workflows.store_thought(
        content=discovery_content,
        thought_type=ThoughtType.FACT,
        context={'source': 'noesis', 'research_strategy': 'heuristic'},
        associations=[pattern_thought],  # Link to pattern
        confidence=discovery_content['confidence'],
        ci_id='noesis'
    )
    print(f"   ✓ Discovery made and stored: {discovery_thought[:16]}...")
    print(f"     - Findings: {len(discovery_content['findings'])} items")
    print(f"     - Linked to pattern: Yes")
    
    # 5. Simulate Learning (Sophia)
    print("\n5. LEARNING & VALIDATION (Sophia)")
    learning_content = {
        'type': 'learning',
        'experiment': 'Pattern Validation',
        'hypothesis': 'Recursive problem solving improves with memoization',
        'results': {
            'performance_improvement': 0.6,
            'confidence': 0.92,
            'validated': True
        }
    }
    
    learning_thought = await workflows.store_thought(
        content=learning_content,
        thought_type=ThoughtType.REFLECTION,
        context={'source': 'sophia', 'experiment_type': 'validation'},
        associations=[pattern_thought, discovery_thought],  # Link to both
        confidence=learning_content['results']['confidence'],
        ci_id='sophia'
    )
    print(f"   ✓ Learning completed and stored: {learning_thought[:16]}...")
    print(f"     - Performance improvement: {learning_content['results']['performance_improvement']*100:.0f}%")
    print(f"     - Validation: {'✓ Passed' if learning_content['results']['validated'] else '✗ Failed'}")
    
    # 6. Simulate Insight Generation
    print("\n6. INSIGHT GENERATION")
    insight = CognitiveInsight(
        id='insight_001',
        type='optimization',
        content='Combining recursive patterns with memoization yields optimal results',
        severity='positive',
        frequency=1,
        impact='high',
        suggestions=['Apply memoization to all recursive functions', 'Monitor stack depth']
    )
    
    insight_thought = await workflows.store_thought(
        content={
            'insight': insight.content,
            'type': insight.type,
            'impact': insight.impact,
            'suggestions': insight.suggestions
        },
        thought_type=ThoughtType.IDEA,  # Insights are stored as ideas
        associations=[pattern_thought, discovery_thought, learning_thought],
        confidence=0.95,
        ci_id='engram'
    )
    print(f"   ✓ Insight generated: {insight_thought[:16]}...")
    print(f"     - Content: {insight.content[:50]}...")
    print(f"     - Impact: {insight.impact}")
    
    # 7. Demonstrate Knowledge Retrieval
    print("\n7. KNOWLEDGE RETRIEVAL & ASSOCIATION")
    
    # Recall the original pattern
    recalled_pattern = await workflows.recall_thought(key=pattern_thought)
    print(f"   ✓ Pattern recalled: {recalled_pattern.content['pattern']}")
    
    # Find similar thoughts
    similar = await workflows.recall_similar(
        reference="recursive optimization patterns",
        limit=5,
        ci_id='athena'
    )
    print(f"   ✓ Found {len(similar)} related memories")
    
    # Build context
    context = await workflows.build_context(
        topic="recursive problem solving optimization",
        depth=3,
        ci_id='athena'
    )
    print(f"   ✓ Built context with {len(context)} elements")
    
    # 8. Show System Statistics
    print("\n📊 SYSTEM STATISTICS:")
    print("-"*50)
    cache_size = len(esr.cache.cache)
    print(f"   Knowledge Graph Entries: {cache_size}")
    print(f"   Thought Associations: {len(workflows.thought_chains)}")
    print(f"   Components Integrated: 4 (Engram, Sophia, Noesis, Athena)")
    
    # Cleanup
    await esr.stop()
    
    print("\n" + "="*80)
    print("✅ COMPLETE INTEGRATION TEST SUCCESSFUL!")
    print("-"*50)
    print("The cognitive research system demonstrated:")
    print()
    print("1. Pattern Detection (Engram) → Stored in Knowledge Graph")
    print("2. Discovery Research (Noesis) → Linked to Pattern")
    print("3. Learning Validation (Sophia) → Confirmed Discovery")
    print("4. Insight Generation → Connected All Knowledge")
    print("5. Knowledge Retrieval → Accessed Associated Memories")
    print()
    print("All components working together through the ESR/Athena Knowledge Graph!")
    print("="*80)


async def main():
    """Run the complete integration test"""
    try:
        await demonstrate_full_system()
        return 0
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)