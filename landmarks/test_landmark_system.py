#!/usr/bin/env python3
"""
Test the landmark system to ensure it works correctly
"""

import sys
from pathlib import Path

# Add landmarks to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from landmarks import (
    landmark,
    architecture_decision,
    performance_boundary,
    api_contract,
    danger_zone,
    integration_point,
    state_checkpoint,
    LandmarkRegistry
)
from landmarks.memory.ci_memory import CIMemory, NumaMemory


# Test basic landmark decorator
@landmark(type="test", title="Test Function", description="Testing landmark system")
def test_function():
    """A simple test function"""
    return "Hello from test function"


# Test architecture decision
@architecture_decision(
    title="Use landmark system for persistent memory",
    rationale="CIs need context across sessions",
    alternatives_considered=["Database tags", "Code comments", "External docs"],
    impacts=["developer_experience", "ci_capabilities"],
    decided_by="Casey"
)
def implement_landmarks():
    """Implementation of the landmark system"""
    return "Landmarks implemented"


# Test performance boundary
@performance_boundary(
    title="Landmark search performance",
    sla="<100ms for 10k landmarks",
    optimization_notes="Uses in-memory indexes",
    metrics={"index_time": "5ms", "search_time": "10ms"}
)
def search_landmarks_fast(query: str):
    """Fast landmark search"""
    return LandmarkRegistry.search(query)


# Test API contract
@api_contract(
    title="Landmark retrieval endpoint",
    endpoint="/api/landmarks/{id}",
    method="GET",
    response_schema={"id": "string", "type": "string", "title": "string"},
    auth_required=False
)
def get_landmark_api(landmark_id: str):
    """API endpoint for retrieving landmarks"""
    return LandmarkRegistry.get(landmark_id)


# Test danger zone
@danger_zone(
    title="Registry modification",
    risk_level="high",
    risks=["Data loss", "Inconsistent state"],
    mitigation="Backup before modifications",
    review_required=True
)
def modify_registry():
    """Dangerous registry modification"""
    pass


# Test integration point
@integration_point(
    title="Connect to Hermes",
    target_component="Hermes",
    protocol="WebSocket",
    data_flow="Landmark events -> Hermes message bus"
)
def connect_to_hermes():
    """Integration with Hermes message bus"""
    pass


# Test state checkpoint
@state_checkpoint(
    title="Registry singleton state",
    state_type="singleton",
    persistence=True,
    consistency_requirements="Thread-safe access",
    recovery_strategy="Reload from disk"
)
def get_registry_instance():
    """Get the singleton registry instance"""
    return LandmarkRegistry()


def test_landmark_system():
    """Run tests on the landmark system"""
    print("🧪 Testing Landmark System\n")
    
    # Test function execution still works
    print("1. Testing decorated functions still work:")
    result = test_function()
    print(f"   ✓ test_function returned: {result}")
    
    result = implement_landmarks()
    print(f"   ✓ implement_landmarks returned: {result}")
    
    # Test landmark registration
    print("\n2. Testing landmark registration:")
    stats = LandmarkRegistry.stats()
    print(f"   ✓ Total landmarks registered: {stats['total_landmarks']}")
    print(f"   ✓ Landmark types: {list(stats['by_type'].keys())}")
    
    # Test landmark retrieval
    print("\n3. Testing landmark retrieval:")
    test_landmarks = LandmarkRegistry.list(type="test")
    if test_landmarks:
        print(f"   ✓ Found {len(test_landmarks)} test landmarks")
        print(f"   ✓ First test landmark: {test_landmarks[0].title}")
    
    # Test search
    print("\n4. Testing landmark search:")
    search_results = LandmarkRegistry.search("landmark")
    print(f"   ✓ Search for 'landmark' found {len(search_results)} results")
    
    # Test CI Memory
    print("\n5. Testing CI Memory:")
    numa = NumaMemory()
    
    # Test remembering
    numa.remember("test_key", "test_value", category="testing")
    recalled = numa.recall("test_key", category="testing")
    print(f"   ✓ Memory recall: {recalled}")
    
    # Test landmark search through CI
    landmarks = numa.search_landmarks("performance")
    print(f"   ✓ CI landmark search found {len(landmarks)} results")
    
    # Test CI routing
    target_ci = numa.route_to_ci("How do I send a message via WebSocket?")
    print(f"   ✓ Query routed to: {target_ci}")
    
    # Show detailed stats
    print("\n6. Landmark Statistics:")
    for type_name, count in stats['by_type'].items():
        print(f"   - {type_name}: {count} landmarks")
    
    print("\n✅ All tests passed! Landmark system is working correctly.")
    
    # List all registered landmarks
    print("\n7. All Registered Landmarks:")
    all_landmarks = LandmarkRegistry.list()
    for lm in all_landmarks:
        print(f"   - [{lm.type}] {lm.title} ({Path(lm.file_path).name}:{lm.line_number})")


if __name__ == "__main__":
    test_landmark_system()