#!/usr/bin/env python3
"""
Simple test for Discovery and Learning Engines
Tests basic functionality without full integration
"""

import asyncio
import sys
from pathlib import Path
import numpy as np

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_discovery_engine():
    """Test Discovery Engine basic functionality"""
    print("\n" + "="*50)
    print("TESTING NOESIS DISCOVERY ENGINE")
    print("="*50)
    
    try:
        from Noesis.noesis.core.discovery_engine import (
            ResearchEngine,
            PatternGraph,
            TheoryGenerator,
            Discovery,
            Pattern,
            Theory,
            ResearchStrategy
        )
        
        # Test ResearchEngine
        print("\n1. Testing ResearchEngine...")
        engine = ResearchEngine()
        await engine.initialize()
        print("   ✓ ResearchEngine initialized")
        
        # Test discovery
        discovery = await engine.research(
            query="test query for async programming",
            context={"test": True},
            strategy=ResearchStrategy.HEURISTIC
        )
        print(f"   ✓ Research completed: {discovery.id}")
        print(f"     - Confidence: {discovery.confidence:.2f}")
        
        # Test PatternGraph
        print("\n2. Testing PatternGraph...")
        graph = PatternGraph()
        await graph.initialize()
        print("   ✓ PatternGraph initialized")
        
        # Add a pattern
        pattern = Pattern(
            id="test_pattern_1",
            name="Test Pattern",
            description="A test pattern",
            occurrences=[{"data": "test"}],
            confidence=0.8,
            support=1,
            created_at=discovery.timestamp
        )
        await graph.add_pattern(pattern)
        print(f"   ✓ Pattern added: {pattern.name}")
        
        # Test TheoryGenerator
        print("\n3. Testing TheoryGenerator...")
        generator = TheoryGenerator()
        await generator.initialize()
        print("   ✓ TheoryGenerator initialized")
        
        # Generate theory
        theory = await generator.generate_from_patterns([pattern])
        if theory:
            print(f"   ✓ Theory generated: {theory.id}")
            print(f"     - Confidence: {theory.confidence:.2f}")
        
        print("\n✓ Discovery Engine tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Discovery Engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_learning_engine():
    """Test Learning Engine basic functionality"""
    print("\n" + "="*50)
    print("TESTING SOPHIA LEARNING ENGINE")
    print("="*50)
    
    try:
        from Sophia.sophia.core.learning_engine import (
            ExperimentRunner,
            ModelTrainer,
            LearningOrchestrator,
            Experiment,
            ExperimentType,
            LearningModel,
            LearningStrategy
        )
        
        # Test ExperimentRunner
        print("\n1. Testing ExperimentRunner...")
        runner = ExperimentRunner()
        await runner.initialize()
        print("   ✓ ExperimentRunner initialized")
        
        # Create experiment
        experiment = await runner.create_experiment(
            name="Test Experiment",
            type=ExperimentType.AB_TEST,
            hypothesis="Test hypothesis",
            control_config={"test": "control"}
        )
        print(f"   ✓ Experiment created: {experiment.id}")
        
        # Run experiment
        results = await runner.run_experiment(experiment.id)
        print(f"   ✓ Experiment run completed")
        if results:
            print(f"     - Results: {list(results.keys())}")
        
        # Test ModelTrainer
        print("\n2. Testing ModelTrainer...")
        trainer = ModelTrainer()
        await trainer.initialize()
        print("   ✓ ModelTrainer initialized")
        
        # Train a model
        data = np.random.randn(100, 5)
        labels = np.random.randint(0, 2, 100)
        
        model = await trainer.train(
            name="Test Model",
            data=data,
            labels=labels,
            strategy=LearningStrategy.SUPERVISED
        )
        print(f"   ✓ Model trained: {model.id}")
        print(f"     - Performance: {model.performance:.2f}")
        
        # Test LearningOrchestrator
        print("\n3. Testing LearningOrchestrator...")
        orchestrator = LearningOrchestrator()
        await orchestrator.initialize()
        print("   ✓ LearningOrchestrator initialized")
        
        # Learn from pattern
        test_pattern = {
            "name": "Test Pattern",
            "strength": 0.8,
            "confidence": 0.9
        }
        event = await orchestrator.learn_from_pattern(test_pattern)
        print(f"   ✓ Learning from pattern completed")
        print(f"     - Event: {event.id}")
        
        print("\n✓ Learning Engine tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Learning Engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_knowledge_bridge():
    """Test Athena Knowledge Bridge basic functionality"""
    print("\n" + "="*50)
    print("TESTING ATHENA KNOWLEDGE BRIDGE")
    print("="*50)
    
    try:
        from shared.integration.athena_knowledge_bridge import (
            AthenaKnowledgeBridge,
            KnowledgeType
        )
        
        print("\n1. Testing AthenaKnowledgeBridge initialization...")
        bridge = AthenaKnowledgeBridge()
        
        # Note: Full initialization requires ESR which might not be available
        print("   ✓ AthenaKnowledgeBridge created")
        
        # Test basic structure
        print("\n2. Testing bridge structure...")
        assert hasattr(bridge, 'knowledge_graph')
        assert hasattr(bridge, 'relationships')
        assert hasattr(bridge, 'stats')
        print("   ✓ Bridge structure verified")
        
        print("\n3. Testing KnowledgeType enum...")
        types = [
            KnowledgeType.DISCOVERY,
            KnowledgeType.PATTERN,
            KnowledgeType.THEORY,
            KnowledgeType.EXPERIMENT
        ]
        print(f"   ✓ Found {len(types)} knowledge types")
        
        print("\n✓ Knowledge Bridge basic tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Knowledge Bridge test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all simple tests"""
    print("\n" + "="*60)
    print("SIMPLE ENGINE TESTS")
    print("="*60)
    
    success = True
    
    # Test Discovery Engine
    if not await test_discovery_engine():
        success = False
    
    # Test Learning Engine
    if not await test_learning_engine():
        success = False
    
    # Test Knowledge Bridge
    if not await test_knowledge_bridge():
        success = False
    
    print("\n" + "="*60)
    if success:
        print("ALL SIMPLE TESTS PASSED ✓")
    else:
        print("SOME TESTS FAILED ✗")
    print("="*60)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)