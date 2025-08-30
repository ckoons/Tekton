#!/usr/bin/env python3
"""Test script for Apollo Landmark Integration"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add Apollo to path
apollo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(apollo_root))

from core.preparation.context_brief import (
    ContextBriefManager, MemoryItem, MemoryType, CIType
)
from core.preparation.landmark_manager import LandmarkManager, MemoryRelationship

def test_landmark_integration():
    """Test landmark integration with memory system"""
    
    print("🗺️ Testing Apollo Landmark Integration")
    print("=" * 50)
    
    # Initialize with test directory
    test_dir = Path("/tmp/apollo_landmark_test")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Create managers
    brief_manager = ContextBriefManager(storage_dir=test_dir / "preparation", enable_landmarks=True)
    print("✓ Initialized Context Brief manager with landmarks enabled")
    
    # Create sequence of related memories
    print("\n📝 Creating related memories...")
    
    memories = [
        MemoryItem(
            id="mem_001",
            timestamp=datetime.now() - timedelta(hours=3),
            ci_source="apollo-ci",
            ci_type=CIType.GREEK,
            type=MemoryType.INSIGHT,
            summary="Import order affects CI launches",
            content="Discovered that shared imports must come after sys.path setup",
            tokens=25,
            relevance_tags=["import", "bug", "shared"],
            priority=7
        ),
        MemoryItem(
            id="mem_002",
            timestamp=datetime.now() - timedelta(hours=2, minutes=30),
            ci_source="ergon-ci",
            ci_type=CIType.GREEK,
            type=MemoryType.ERROR,
            summary="ModuleNotFoundError in all CIs",
            content="All CIs failing with ModuleNotFoundError: No module named 'shared'",
            tokens=20,
            relevance_tags=["error", "import", "shared", "critical"],
            priority=9
        ),
        MemoryItem(
            id="mem_003",
            timestamp=datetime.now() - timedelta(hours=2),
            ci_source="ergon-ci",
            ci_type=CIType.GREEK,
            type=MemoryType.DECISION,
            summary="Reorder imports in launcher",
            content="Decided to move sys.path setup before shared imports in enhanced_tekton_ai_launcher.py",
            tokens=30,
            relevance_tags=["fix", "import", "launcher", "decision"],
            priority=8
        ),
        MemoryItem(
            id="mem_004",
            timestamp=datetime.now() - timedelta(hours=1),
            ci_source="athena-ci",
            ci_type=CIType.GREEK,
            type=MemoryType.PLAN,
            summary="Add import validation",
            content="Plan to add pre-launch validation to prevent import order issues",
            tokens=22,
            relevance_tags=["validation", "import", "prevention"],
            priority=6
        )
    ]
    
    # Add memories and create landmarks
    for memory in memories:
        brief_manager.add_memory(memory)
        print(f"  ✓ Added: [{memory.type.value}] {memory.summary}")
    
    # Check landmarks were created
    print("\n🏔️ Checking landmarks...")
    landmarks = brief_manager.get_landmarks()
    print(f"  Created {len(landmarks)} landmarks")
    
    for landmark in landmarks[:2]:  # Show first 2
        print(f"    - {landmark['entity_id']}: {landmark['name']}")
    
    # Analyze relationships
    print("\n🔗 Analyzing relationships...")
    if brief_manager.landmark_manager:
        # Find potential relationships
        relationships = brief_manager.landmark_manager.find_relationships(memories)
        print(f"  Found {len(relationships)} potential relationships:")
        
        for source, target, rel_type in relationships[:5]:  # Show first 5
            print(f"    {source.split('_')[-1]} -{rel_type}-> {target.split('_')[-1]}")
        
        # Create relationships
        created = brief_manager.analyze_relationships()
        print(f"  ✓ Created {created} relationships in graph")
    
    # Test landmark queries
    print("\n🔍 Testing landmark queries...")
    
    # Get landmarks for specific CI
    ergon_landmarks = brief_manager.get_landmarks(ci_name="ergon-ci")
    print(f"  Ergon CI has {len(ergon_landmarks)} landmarks")
    
    # Get error landmarks
    if brief_manager.landmark_manager:
        error_landmarks = brief_manager.landmark_manager.get_landmarks_by_type(MemoryType.ERROR)
        print(f"  Found {len(error_landmarks)} error landmarks")
        
        # Get related landmarks
        if error_landmarks:
            error_id = error_landmarks[0]["entity_id"]
            related = brief_manager.landmark_manager.get_related_landmarks(error_id)
            print(f"  Error landmark has {len(related)} related landmarks")
    
    # Export for Athena
    print("\n📤 Exporting for Athena integration...")
    if brief_manager.landmark_manager:
        export = brief_manager.landmark_manager.export_for_athena()
        print(f"  Export ready:")
        print(f"    - Namespace: {export['namespace']}")
        print(f"    - Entities: {len(export['entities'])}")
        print(f"    - Relationships: {len(export['relationships'])}")
        
        # Save export
        export_file = test_dir / "athena_export.json"
        with open(export_file, 'w') as f:
            json.dump(export, f, indent=2, default=str)
        print(f"  ✓ Saved export to {export_file}")
    
    # Test Cypher query generation
    print("\n🔍 Testing graph query generation...")
    if brief_manager.landmark_manager:
        query = brief_manager.landmark_manager.build_graph_query(
            ci_name="ergon-ci",
            context="How did we fix the import error?"
        )
        print("  Generated Cypher query:")
        print("  " + query.replace('\n', '\n  '))
    
    # Save everything
    brief_manager.save()
    print("\n💾 Saved all data")
    
    # Cleanup
    import shutil
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print("✓ Cleaned up test data")
    
    print("\n✅ Landmark integration test complete!")
    return True

if __name__ == "__main__":
    try:
        test_landmark_integration()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)