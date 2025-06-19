#!/usr/bin/env python3
"""
Test script for Phase 3 Component Architecture Mapping
Run this to see the component mapper in action!
"""

import asyncio
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))  # Hephaestus root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))  # Tekton root

from hephaestus.mcp.component_mapper import ComponentMapper
from hephaestus.mcp.component_mapper_tools import ui_component_map, ui_architecture_scan, ui_dependency_graph


async def test_phase3():
    print("=" * 80)
    print("PHASE 3 COMPONENT ARCHITECTURE MAPPING TEST".center(80))
    print("=" * 80)
    print()
    
    # Test 1: Single component analysis
    print("Test 1: Analyzing rhetor component...")
    print("-" * 80)
    result = await ui_component_map("rhetor")
    if "error" not in result:
        print(f"Files found: {len(result['files']['scripts'])} JavaScript files")
        print(f"Summary: {result['summary']}")
        print("\nVisualization:")
        print(result['visualization'])
    else:
        print(f"Error: {result['error']}")
    
    input("\nPress Enter to continue to Test 2...")
    
    # Test 2: Multi-component scan
    print("\n\nTest 2: Scanning rhetor, hermes, and prometheus...")
    print("-" * 80)
    result = await ui_architecture_scan(["rhetor", "hermes", "prometheus"])
    if "error" not in result:
        print(f"Analyzed {result['analyzed_components']} components")
        print(f"Found {len(result['circular_dependencies'])} circular dependencies")
        print("\nStatistics:")
        stats = result['statistics']
        print(f"  - Total relationships: {stats['total_relationships']}")
        print(f"  - Most connected: {stats['most_connected'][0] if stats['most_connected'] else 'None'}")
        print(f"  - Isolated components: {len(stats['isolated_components'])}")
        print("\nRecommendations:")
        for rec in result['recommendations'][:3]:
            print(f"  {rec}")
    else:
        print(f"Error: {result['error']}")
    
    input("\nPress Enter to continue to Test 3...")
    
    # Test 3: Dependency graph visualization
    print("\n\nTest 3: Generating dependency graph (ASCII format)...")
    print("-" * 80)
    result = await ui_dependency_graph(format="ascii", focus="rhetor")
    if "error" not in result:
        print(result['visualization'])
    else:
        print(f"Error: {result['error']}")
    
    print("\n" + "=" * 80)
    print("PHASE 3 TESTING COMPLETE!".center(80))
    print("=" * 80)
    
    # Direct test of component mapper
    print("\n\nBonus: Direct component mapper test...")
    print("-" * 80)
    mapper = ComponentMapper()
    
    # Find all components
    components = []
    if mapper.components_path.exists():
        for item in mapper.components_path.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name not in ["shared", "test"]:
                components.append(item.name)
    
    print(f"Found {len(components)} components: {', '.join(sorted(components)[:10])}")
    
    # Analyze event patterns
    print("\nAnalyzing event patterns in rhetor...")
    files = mapper.find_component_files("rhetor")
    if "html" in files:
        with open(files["html"], 'r') as f:
            content = f.read()
        events = mapper.analyze_event_flow(content, "rhetor")
        print(f"  - Event listeners: {len(events['listeners'])}")
        print(f"  - Event emitters: {len(events['emitters'])}")
        print(f"  - Click handlers: {len(events['handlers'])}")
        if events['handlers']:
            print(f"    Examples: {list(events['handlers'])[:3]}")


if __name__ == "__main__":
    asyncio.run(test_phase3())