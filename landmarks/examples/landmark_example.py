#!/usr/bin/env python3
"""
Example of how to add landmarks to Tekton components
"""

import sys
from pathlib import Path

# In actual use, this would be: from landmarks import architecture_decision, performance_boundary, etc.
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from landmarks import (
    architecture_decision,
    performance_boundary,
    integration_point,
    state_checkpoint
)


# Example 1: Marking an architectural decision in Hermes
@architecture_decision(
    title="WebSocket for real-time messaging",
    rationale="Need <100ms latency for UI updates, REST polling would be too slow",
    alternatives_considered=["REST with polling", "Server-sent events", "gRPC streaming"],
    impacts=["scalability", "client_complexity", "infrastructure"],
    decided_by="Casey",
    date="2024-01-15"
)
class HermesWebSocketServer:
    """Main WebSocket server for inter-component communication"""
    
    @performance_boundary(
        title="Message processing pipeline",
        sla="<50ms per message",
        optimization_notes="Async processing, message batching for broadcasts",
        metrics={"throughput": "10k msg/sec", "p99_latency": "45ms"}
    )
    async def process_message(self, message):
        """Process incoming WebSocket messages"""
        # Implementation here
        pass


# Example 2: Marking a singleton pattern
@state_checkpoint(
    title="Global configuration singleton",
    state_type="singleton",
    persistence=True,
    consistency_requirements="Thread-safe, immutable after init",
    recovery_strategy="Reload from disk on restart"
)
class GlobalConfig:
    """Global configuration manager"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


# Example 3: Marking integration points
@integration_point(
    title="Hermes registration",
    target_component="Hermes",
    protocol="REST",
    data_flow="Component metadata -> Hermes registry"
)
async def register_with_hermes(component_name: str, capabilities: list):
    """Register this component with Hermes message bus"""
    # Registration logic here
    pass


# Example 4: Using landmarks programmatically
def demonstrate_landmark_usage():
    """Show how to work with landmarks at runtime"""
    
    # Access landmark from decorated function
    if hasattr(register_with_hermes, '_landmark'):
        landmark = register_with_hermes._landmark
        print(f"Function landmark: {landmark.title}")
        print(f"  Type: {landmark.type}")
        print(f"  Target: {landmark.metadata.get('target_component')}")
    
    # Search for landmarks
    from landmarks import LandmarkRegistry
    
    # Find all WebSocket-related landmarks
    websocket_landmarks = LandmarkRegistry.search("websocket")
    print(f"\nFound {len(websocket_landmarks)} WebSocket-related landmarks")
    
    # Get all landmarks for a component
    hermes_landmarks = LandmarkRegistry.list(component="Hermes")
    print(f"\nHermes component has {len(hermes_landmarks)} landmarks")
    
    # Use CI memory to remember findings
    from landmarks.memory.ci_memory import NumaMemory
    
    numa = NumaMemory()
    numa.remember(
        "websocket_decision",
        {
            "component": "Hermes",
            "rationale": "Low latency requirement",
            "decided": "2024-01-15"
        },
        category="architectural_decisions"
    )
    
    # Recall the decision later
    decision = numa.recall("websocket_decision", category="architectural_decisions")
    print(f"\nRecalled decision: {decision}")


if __name__ == "__main__":
    print("🎯 Landmark Usage Examples\n")
    
    # Show the class has a landmark
    print(f"1. HermesWebSocketServer landmark: {hasattr(HermesWebSocketServer, '_landmark')}")
    
    # Show the method has a landmark
    server = HermesWebSocketServer()
    print(f"2. process_message landmark: {hasattr(server.process_message, '_landmark')}")
    
    # Demonstrate usage
    print("\n3. Programmatic landmark usage:")
    demonstrate_landmark_usage()
    
    print("\n✅ Examples complete!")