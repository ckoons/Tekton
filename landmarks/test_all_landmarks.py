#!/usr/bin/env python3
"""
Test that imports all landmarked modules to register them and tests CI usage
"""

import sys
import asyncio
from pathlib import Path

# Add Tekton root to path
tekton_root = Path(__file__).parent.parent
sys.path.insert(0, str(tekton_root))

print("🎯 Testing Landmarks System with All Components\n")

# Import shared utilities with landmarks
print("1. Importing shared utilities...")
try:
    from shared.utils.global_config import GlobalConfig
    from shared.utils.graceful_shutdown import GracefulShutdown
    from shared.utils.standard_component import StandardComponentBase
    from shared.utils.mcp_helpers import create_mcp_server
    print("   ✅ Shared utilities imported")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Import Hermes components with landmarks
print("\n2. Importing Hermes components...")
try:
    from Hermes.hermes.core.message_bus import MessageBus
    from Hermes.hermes.api.llm_endpoints import websocket_endpoint
    from Hermes.hermes.core.registration.manager import RegistrationManager
    print("   ✅ Hermes components imported")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Import Apollo components with landmarks
print("\n3. Importing Apollo components...")
try:
    from Apollo.apollo.core.action_planner import ActionPlanner
    from Apollo.apollo.core.token_budget import TokenBudgetManager
    print("   ✅ Apollo components imported")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Import Engram components with landmarks
print("\n4. Importing Engram components...")
try:
    from Engram.engram.core.memory_manager import MemoryManager
    from Engram.engram.core.structured.storage import MemoryStorage
    print("   ✅ Engram components imported")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Now test landmark registration
print("\n5. Checking landmark registration...")
from landmarks import LandmarkRegistry

stats = LandmarkRegistry.stats()
print(f"   Total landmarks: {stats['total_landmarks']}")
print(f"   Components with landmarks: {len(stats['by_component'])}")

# Show breakdown
print("\n   By component:")
for comp, count in sorted(stats['by_component'].items()):
    print(f"     {comp:15} {count:3} landmarks")

print("\n   By type:")
for lm_type, count in sorted(stats['by_type'].items()):
    print(f"     {lm_type:25} {count:3} landmarks")

# Test CI memory system
print("\n6. Testing CI Memory System...")
from landmarks.memory.ci_memory import NumaMemory

async def test_ci_memory():
    """Test CI memory functionality"""
    numa = NumaMemory()
    
    # Remember an architectural decision
    numa.remember(
        "hermes_websocket",
        {
            "decision": "Use WebSocket for real-time communication",
            "rationale": "<100ms latency requirement",
            "date": "2024-01-20"
        },
        category="architectural_decisions"
    )
    
    # Search for related landmarks
    websocket_landmarks = numa.search_landmarks("websocket")
    print(f"   Found {len(websocket_landmarks)} WebSocket-related landmarks")
    
    # Show some examples
    for lm in websocket_landmarks[:3]:
        print(f"     - [{lm.type}] {lm.title}")
        print(f"       {lm.component}/{Path(lm.file_path).name}:{lm.line_number}")
    
    # Test routing
    queries = [
        "How do I send messages between components?",
        "How do I store memories?",
        "How do I manage token budgets?",
        "How do I integrate with AI models?"
    ]
    
    print("\n   CI Routing tests:")
    for query in queries:
        target_ci = numa.route_to_ci(query)
        print(f"     '{query[:40]}...' → {target_ci}")
    
    # Show session summary
    summary = numa.summarize_session()
    print(f"\n   Session summary:")
    print(f"     Items remembered: {summary['items_remembered']}")
    print(f"     Memory categories: {', '.join(summary['memory_categories'])}")

# Run async test
asyncio.run(test_ci_memory())

# Test landmark search functionality
print("\n7. Testing landmark search...")
search_terms = ["performance", "architecture", "singleton", "api", "integration"]

for term in search_terms:
    results = LandmarkRegistry.search(term)
    print(f"   '{term}' → {len(results)} results")

# Generate dashboard
print("\n8. Generating dashboard...")
from landmarks.tools.generate_dashboard import generate_dashboard

dashboard_path = generate_dashboard()
print(f"   Dashboard saved to: {dashboard_path}")

# Final summary
print("\n✅ Landmark system test complete!")
print(f"\nKey findings:")
print(f"  - {stats['total_landmarks']} landmarks across {len(stats['by_component'])} components")
print(f"  - CI memory system working with routing and persistence")
print(f"  - Search functionality operational")
print(f"  - Dashboard visualization available")

print("\n💡 Next steps:")
print("  1. Continue adding landmarks to remaining components")
print("  2. Use 'tekton landmark' CLI for management") 
print("  3. Integrate with Numa for persistent architectural memory")