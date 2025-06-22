#!/usr/bin/env python3
"""
Display statistics about landmarks in the Tekton system
"""

import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from landmarks import LandmarkRegistry
from landmarks.memory.ci_memory import NumaMemory


def display_stats():
    """Display comprehensive landmark statistics"""
    print("🎯 Tekton Landmark Statistics")
    print("=" * 50)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Get overall stats
    stats = LandmarkRegistry.stats()
    
    print(f"📊 Total Landmarks: {stats['total_landmarks']}")
    print(f"📁 Files with Landmarks: {stats['total_files']}")
    print(f"🏷️  Total Tags: {stats['total_tags']}\n")
    
    # Breakdown by type
    print("📋 Landmarks by Type:")
    print("-" * 30)
    for lm_type, count in sorted(stats['by_type'].items()):
        emoji = {
            'architecture_decision': '🏛️',
            'performance_boundary': '⚡',
            'api_contract': '📄',
            'danger_zone': '⚠️',
            'integration_point': '🔗',
            'state_checkpoint': '💾',
            'test': '🧪'
        }.get(lm_type, '📌')
        print(f"{emoji} {lm_type:25} {count:3}")
    
    # Breakdown by component
    print("\n🧩 Landmarks by Component:")
    print("-" * 30)
    for component, count in sorted(stats['by_component'].items()):
        print(f"   {component:25} {count:3}")
    
    # Recent landmarks
    print("\n🕐 Recent Landmarks (last 5):")
    print("-" * 50)
    recent = LandmarkRegistry.list()[:5]
    for lm in recent:
        print(f"   [{lm.type}] {lm.title}")
        print(f"   📍 {Path(lm.file_path).name}:{lm.line_number}")
        print(f"   🕐 {lm.timestamp.strftime('%Y-%m-%d %H:%M')}\n")
    
    # Search examples
    print("🔍 Example Searches:")
    print("-" * 30)
    
    # Search for specific patterns
    searches = [
        ("websocket", "WebSocket-related"),
        ("performance", "Performance-critical"),
        ("singleton", "Singleton patterns"),
        ("api", "API contracts")
    ]
    
    for query, description in searches:
        results = LandmarkRegistry.search(query)
        print(f"   '{query}' → {len(results)} {description} landmarks")
    
    # Numa's memory stats
    print("\n🧠 Numa's Memory Stats:")
    print("-" * 30)
    try:
        numa = NumaMemory()
        session_summary = numa.summarize_session()
        print(f"   Session started: {session_summary['session_start']}")
        print(f"   Items remembered: {session_summary['items_remembered']}")
        print(f"   Memory categories: {', '.join(session_summary['memory_categories'])}")
    except:
        print("   (Numa memory not initialized)")


def check_component_coverage():
    """Check which components have landmarks"""
    print("\n📈 Component Coverage Analysis:")
    print("-" * 50)
    
    # Expected components
    expected_components = [
        'shared', 'Hermes', 'Apollo', 'Engram', 'Athena', 
        'Prometheus', 'Budget', 'Harmonia', 'Rhetor', 'Sophia', 
        'Telos', 'Ergon', 'Synthesis', 'Metis', 'Terma'
    ]
    
    # Get actual coverage
    stats = LandmarkRegistry.stats()
    covered = set(stats['by_component'].keys())
    
    for comp in expected_components:
        if comp in covered:
            count = stats['by_component'][comp]
            status = f"✅ {count} landmarks"
        else:
            status = "❌ No landmarks yet"
        print(f"   {comp:15} {status}")
    
    # Coverage percentage
    coverage_pct = (len(covered) / len(expected_components)) * 100
    print(f"\n   Coverage: {coverage_pct:.1f}% ({len(covered)}/{len(expected_components)} components)")


if __name__ == "__main__":
    display_stats()
    check_component_coverage()
    
    print("\n💡 Tip: Use 'from landmarks import LandmarkRegistry' to query landmarks in your code!")
    print("📚 See INTEGRATION_GUIDE.md for how to add landmarks to components.")