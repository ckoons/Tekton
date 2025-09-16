#!/usr/bin/env python3
"""
Test script for standardized memory middleware.
Verifies the memory injection patterns work correctly.
"""

import asyncio
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the standardized components
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from middleware import (
    MemoryMiddleware,
    MemoryConfig,
    InjectionStyle,
    MemoryTier,
    create_memory_middleware
)
from injection import (
    MemoryInjector,
    InjectionPattern,
    ConversationalInjector,
    inject_conversational_memory,
    select_pattern_for_task
)


async def test_basic_middleware():
    """Test basic memory middleware functionality."""
    print("\n=== Testing Basic Middleware ===")
    
    # Create middleware for Apollo
    config = MemoryConfig(
        namespace="apollo-test",
        injection_style=InjectionStyle.NATURAL,
        memory_tiers=[MemoryTier.RECENT, MemoryTier.SESSION]
    )
    
    middleware = MemoryMiddleware(config)
    
    # Test memory injection
    original_prompt = "What is the status of the system?"
    enriched = await middleware.inject_memories(original_prompt)
    
    print(f"Original: {original_prompt}")
    print(f"Enriched: {enriched}")
    
    # Test storing interaction
    success = await middleware.store_interaction({
        'type': 'test',
        'message': 'Testing memory storage',
        'timestamp': 'now'
    })
    print(f"Storage success: {success}")


async def test_injection_patterns():
    """Test different injection patterns."""
    print("\n=== Testing Injection Patterns ===")
    
    # Test conversational pattern
    conv_injector = ConversationalInjector("hermes-test")
    conv_prompt = "Hello, how are you?"
    conv_enriched = await conv_injector.inject(conv_prompt)
    print(f"\nConversational:")
    print(f"  Original: {conv_prompt}")
    print(f"  Enriched: {conv_enriched}")
    
    # Test analytical pattern
    from injection import AnalyticalInjector
    anal_injector = AnalyticalInjector("athena-test")
    anal_data = {'metrics': [1, 2, 3], 'trend': 'up'}
    anal_enriched = await anal_injector.inject_for_analysis(
        anal_data,
        "performance"
    )
    print(f"\nAnalytical:")
    print(f"  Data: {anal_data}")
    print(f"  Enriched: {anal_enriched[:100]}...")
    
    # Test coordination pattern
    from injection import CoordinationInjector
    coord_injector = CoordinationInjector("apollo-test")
    coord_enriched = await coord_injector.inject_for_coordination(
        "System optimization",
        ["athena", "metis", "prometheus"]
    )
    print(f"\nCoordination:")
    print(f"  Task: System optimization")
    print(f"  Enriched: {coord_enriched}")


async def test_injection_styles():
    """Test different injection styles."""
    print("\n=== Testing Injection Styles ===")
    
    prompt = "Analyze the recent performance metrics"
    
    styles = [
        InjectionStyle.NATURAL,
        InjectionStyle.STRUCTURED,
        InjectionStyle.MINIMAL,
        InjectionStyle.TECHNICAL,
        InjectionStyle.CREATIVE
    ]
    
    for style in styles:
        config = MemoryConfig(
            namespace=f"test-{style.value}",
            injection_style=style
        )
        middleware = MemoryMiddleware(config)
        enriched = await middleware.inject_memories(prompt)
        print(f"\n{style.value.upper()} Style:")
        print(f"  {enriched[:150]}...")


async def test_pattern_selection():
    """Test automatic pattern selection."""
    print("\n=== Testing Pattern Selection ===")
    
    test_tasks = [
        "Let's chat about the weather",
        "Analyze these performance metrics",
        "Create a new feature design",
        "Debug this error message",
        "Coordinate the team meeting",
        "Learn from this example"
    ]
    
    for task in test_tasks:
        pattern = select_pattern_for_task(task)
        print(f"Task: '{task[:40]}...' -> Pattern: {pattern.value}")


async def test_rhetor_compatibility():
    """Test Rhetor V2 compatibility."""
    print("\n=== Testing Rhetor V2 Compatibility ===")
    
    try:
        # Import Rhetor V2
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "Rhetor"))
        
        from rhetor.core.memory_middleware.memory_injector_v2 import (
            MemoryInjectorV2,
            get_memory_injector
        )
        
        # Create injector
        injector = get_memory_injector()
        
        # Test injection
        enriched = await injector.inject_memories(
            "apollo",
            "What's the system status?",
            {'project': 'tekton', 'user': 'casey'}
        )
        
        print(f"Rhetor V2 Injection successful!")
        print(f"  Enriched: {enriched[:100]}...")
        
    except ImportError as e:
        print(f"Rhetor V2 not available: {e}")
    except Exception as e:
        print(f"Rhetor V2 test failed: {e}")


async def test_performance():
    """Test middleware performance."""
    print("\n=== Testing Performance ===")
    
    import time
    
    middleware = create_memory_middleware("perf-test")
    
    # Test retrieval performance
    start = time.time()
    context = await middleware.get_memory_context("test query")
    retrieval_time = (time.time() - start) * 1000
    print(f"Context retrieval: {retrieval_time:.2f}ms")
    
    # Test injection performance
    start = time.time()
    enriched = await middleware.inject_memories(
        "This is a test prompt for performance measurement"
    )
    injection_time = (time.time() - start) * 1000
    print(f"Memory injection: {injection_time:.2f}ms")
    
    # Check SLA
    sla_ms = 200
    if retrieval_time < sla_ms and injection_time < sla_ms:
        print(f"✅ Performance within SLA (<{sla_ms}ms)")
    else:
        print(f"⚠️  Performance exceeds SLA (>{sla_ms}ms)")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("STANDARDIZED MEMORY MIDDLEWARE TEST SUITE")
    print("=" * 60)
    
    try:
        await test_basic_middleware()
    except Exception as e:
        logger.error(f"Basic middleware test failed: {e}")
    
    try:
        await test_injection_patterns()
    except Exception as e:
        logger.error(f"Injection patterns test failed: {e}")
    
    try:
        await test_injection_styles()
    except Exception as e:
        logger.error(f"Injection styles test failed: {e}")
    
    try:
        await test_pattern_selection()
    except Exception as e:
        logger.error(f"Pattern selection test failed: {e}")
    
    try:
        await test_rhetor_compatibility()
    except Exception as e:
        logger.error(f"Rhetor compatibility test failed: {e}")
    
    try:
        await test_performance()
    except Exception as e:
        logger.error(f"Performance test failed: {e}")
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())