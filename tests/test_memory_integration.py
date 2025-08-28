#!/usr/bin/env python3
"""
Test Runner for Memory Integration Experiments
Run memory tests with Ergon and other CIs to evaluate memory system.
"""

import asyncio
import sys
from pathlib import Path
import argparse
import logging
from datetime import datetime

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment
from shared.env import TektonEnvironLock
TektonEnvironLock.load()

# Import memory components
from Rhetor.rhetor.core.memory_middleware.integration import (
    MemoryIntegratedClaudeHandler,
    get_memory_integrated_handler
)
from Rhetor.rhetor.core.memory_middleware.test_framework import (
    MemoryTestFramework,
    TestDepth
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_basic_test(ci_name: str = 'ergon'):
    """Run a basic memory test with a single CI."""
    print(f"\n{'='*60}")
    print(f"BASIC MEMORY TEST - {ci_name.upper()}")
    print(f"{'='*60}\n")
    
    # Initialize handler with memory
    handler = get_memory_integrated_handler()
    
    # Enable memory
    handler.toggle_memory(True)
    
    print("Phase 1: Initial interaction")
    response1 = await handler.handle_forwarded_message(
        ci_name,
        "Let's work on implementing a caching system. What are the key components we need?"
    )
    print(f"Response 1: {response1[:200]}...")
    
    await asyncio.sleep(3)
    
    print("\nPhase 2: Follow-up (should reference previous)")
    response2 = await handler.handle_forwarded_message(
        ci_name,
        "What specific cache invalidation strategies should we consider?"
    )
    print(f"Response 2: {response2[:200]}...")
    
    # Check if memory was referenced
    memory_used = any(
        term in response2.lower() 
        for term in ['earlier', 'mentioned', 'discussed', 'cache', 'components']
    )
    
    print(f"\nMemory referenced: {'✓' if memory_used else '✗'}")
    
    # Get metrics
    metrics = handler.get_memory_metrics(ci_name)
    print(f"\nMemory Metrics:")
    print(f"  Total injections: {metrics.get('total_injections', 0)}")
    print(f"  Total extractions: {metrics.get('total_extractions', 0)}")
    print(f"  Memories stored: {metrics.get('memories_stored', 0)}")
    print(f"  Habit stage: {metrics.get('habit_stage', 'unknown')}")
    
    return memory_used


async def run_scenario_test(scenario: str = 'context_persistence', ci_name: str = 'ergon'):
    """Run a specific test scenario."""
    print(f"\n{'='*60}")
    print(f"SCENARIO TEST: {scenario.upper()}")
    print(f"CI: {ci_name}")
    print(f"{'='*60}\n")
    
    # Initialize components
    handler = get_memory_integrated_handler()
    test_framework = MemoryTestFramework(handler)
    
    # Run scenario
    result = await test_framework.run_scenario(scenario, ci_name, with_memory=True)
    
    # Display results
    print(f"\nScenario: {result.scenario_name}")
    print(f"Success rate: {result.calculate_success_rate():.1%}")
    print(f"Questions with memory refs: {sum(result.memory_references)}/{len(result.memory_references)}")
    print(f"Pattern matches: {sum(result.pattern_matches)}/{len(result.pattern_matches)}")
    print(f"Avg response time: {sum(result.response_times)/len(result.response_times):.2f}s")
    
    # Show sample Q&A
    print("\nSample interactions:")
    for i in range(min(2, len(result.questions_asked))):
        print(f"\nQ{i+1}: {result.questions_asked[i]}")
        print(f"A{i+1}: {result.responses[i][:150]}...")
        print(f"Memory ref: {'✓' if result.memory_references[i] else '✗'}")
    
    return result


async def run_ab_test(scenario: str = 'pattern_recognition', ci_name: str = 'ergon'):
    """Run A/B test comparing with and without memory."""
    print(f"\n{'='*60}")
    print(f"A/B TEST: {scenario.upper()}")
    print(f"CI: {ci_name}")
    print(f"{'='*60}\n")
    
    # Initialize components
    handler = get_memory_integrated_handler()
    test_framework = MemoryTestFramework(handler)
    
    # Run A/B test
    print("Running tests WITH memory...")
    print("Running tests WITHOUT memory...")
    print("(This will take a few minutes)")
    
    comparison = await test_framework.run_ab_test(scenario, ci_name, runs_per_condition=2)
    
    # Display comparison
    print("\n" + "="*40)
    print("A/B TEST RESULTS")
    print("="*40)
    
    print("\nWith Memory:")
    print(f"  Success rate: {comparison['with_memory']['avg_success_rate']:.1%}")
    print(f"  Pattern matches: {comparison['with_memory']['pattern_match_rate']:.1%}")
    print(f"  Avg response time: {comparison['with_memory']['avg_response_time']:.2f}s")
    
    print("\nWithout Memory:")
    print(f"  Success rate: {comparison['without_memory']['avg_success_rate']:.1%}")
    print(f"  Pattern matches: {comparison['without_memory']['pattern_match_rate']:.1%}")
    print(f"  Avg response time: {comparison['without_memory']['avg_response_time']:.2f}s")
    
    print("\nImprovements with Memory:")
    print(f"  Success rate: {comparison['improvements']['success_rate_increase']:+.1%}")
    print(f"  Pattern matches: {comparison['improvements']['pattern_match_increase']:+.1%}")
    print(f"  Response time: {comparison['improvements']['response_time_diff']:+.2f}s")
    
    return comparison


async def run_training_progression(ci_name: str = 'ergon'):
    """Test habit training progression."""
    print(f"\n{'='*60}")
    print(f"HABIT TRAINING PROGRESSION TEST")
    print(f"CI: {ci_name}")
    print(f"{'='*60}\n")
    
    handler = get_memory_integrated_handler()
    
    # Test at different training stages
    stages = ['explicit', 'shortened', 'minimal', 'occasional', 'autonomous']
    
    for stage in stages:
        print(f"\nTesting stage: {stage}")
        handler.set_training_stage(ci_name, stage)
        
        # Send test message
        response = await handler.handle_forwarded_message(
            ci_name,
            "Tell me about the Tekton architecture."
        )
        
        # Check training progress
        progress = handler.get_training_progress(ci_name)
        print(f"  Current stage: {progress['current_stage']}")
        print(f"  Memory usage rate: {progress['memory_usage_rate']}")
        print(f"  Ready for next: {progress['ready_for_advancement']}")
        
        # Check if response shows memory usage
        has_memory = any(
            term in response.lower()
            for term in ['remember', 'recall', 'earlier', 'discussed']
        )
        print(f"  Memory in response: {'✓' if has_memory else '✗'}")
        
        await asyncio.sleep(2)
    
    print("\n" + "="*40)
    print("Training progression complete!")
    

async def run_collaborative_test():
    """Test memory sharing between CIs."""
    print(f"\n{'='*60}")
    print(f"COLLABORATIVE MEMORY TEST")
    print(f"{'='*60}\n")
    
    handler = get_memory_integrated_handler()
    test_framework = MemoryTestFramework(handler)
    
    print("CI 1 (Ergon) learning something new...")
    await handler.handle_forwarded_message(
        'ergon',
        "I've discovered that using connection pooling with a size of 20 works best for our database load."
    )
    
    await asyncio.sleep(3)
    
    print("\nCI 2 (Ami) encountering related problem...")
    response = await handler.handle_forwarded_message(
        'ami',
        "What's the optimal database connection pool size for our application?"
    )
    
    # Check if knowledge transferred
    knowledge_shared = 'pool' in response.lower() and '20' in response
    
    print(f"\nResponse: {response[:200]}...")
    print(f"Knowledge transferred: {'✓' if knowledge_shared else '✗'}")
    
    return knowledge_shared


async def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description='Test Memory Integration')
    parser.add_argument('--test', choices=[
        'basic', 'scenario', 'ab', 'training', 'collaborative', 'all'
    ], default='basic', help='Test type to run')
    parser.add_argument('--scenario', default='context_persistence',
                       help='Scenario name for scenario/ab tests')
    parser.add_argument('--ci', default='ergon', help='CI name to test')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("MEMORY INTEGRATION TEST SUITE")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    try:
        if args.test == 'basic' or args.test == 'all':
            await run_basic_test(args.ci)
        
        if args.test == 'scenario' or args.test == 'all':
            await run_scenario_test(args.scenario, args.ci)
        
        if args.test == 'ab':
            await run_ab_test(args.scenario, args.ci)
        
        if args.test == 'training' or args.test == 'all':
            await run_training_progression(args.ci)
        
        if args.test == 'collaborative' or args.test == 'all':
            await run_collaborative_test()
        
        print("\n" + "="*60)
        print("TEST SUITE COMPLETE")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))