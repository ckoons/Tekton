#!/usr/bin/env python3
"""
Visualize Athena Knowledge Graph as ASCII tree
"""

import httpx
import json
from collections import defaultdict

try:
    from shared.urls import athena_url
    BASE_URL = athena_url("/api/v1")
except ImportError:
    # Fallback if shared module not available
    import os
    port = os.environ.get("ATHENA_PORT", "8105")
    BASE_URL = f"http://localhost:{port}/api/v1"

def get_all_data():
    """Fetch all entities and relationships"""
    client = httpx.Client(base_url=BASE_URL, follow_redirects=True)
    
    # Get all entities
    response = client.get("/entities/entities?limit=1000")
    entities = response.json() if response.status_code == 200 else []
    
    # Get stats
    response = client.get("/knowledge/stats")
    stats = response.json() if response.status_code == 200 else {}
    
    return entities, stats

def build_component_tree(entities):
    """Build tree structure of components and their landmarks"""
    components = {}
    landmarks_by_component = defaultdict(list)
    
    for entity in entities:
        if entity.get('entityType') == 'component':
            components[entity['name']] = entity
        elif 'landmark_' in entity.get('entityType', ''):
            component = entity.get('properties', {}).get('component', 'unknown')
            landmarks_by_component[component].append(entity)
    
    return components, landmarks_by_component

def print_tree():
    """Print ASCII tree visualization"""
    entities, stats = get_all_data()
    components, landmarks_by_component = build_component_tree(entities)
    
    print("\n🌳 ATHENA KNOWLEDGE GRAPH")
    print(f"   📊 {stats.get('entity_count', 0)} entities, {stats.get('relationship_count', 0)} relationships")
    print("="*70)
    
    # Print each component and its landmarks
    for comp_name in sorted(components.keys()):
        comp = components[comp_name]
        landmarks = landmarks_by_component[comp_name]
        
        print(f"\n📦 {comp_name}")
        print(f"   ID: {comp['entityId'][:8]}...")
        
        # Group landmarks by type
        by_type = defaultdict(list)
        for lm in landmarks:
            lm_type = lm['entityType'].replace('landmark_', '')
            by_type[lm_type].append(lm)
        
        # Print landmarks by type
        for lm_type, items in sorted(by_type.items()):
            print(f"   │")
            print(f"   ├── 🏷️  {lm_type} ({len(items)})")
            for i, item in enumerate(items[:3]):  # Show first 3
                is_last = (i == len(items)-1) or (i == 2)
                prefix = "       └──" if is_last else "       ├──"
                print(f"{prefix} {item['name'][:50]}...")
            if len(items) > 3:
                print(f"       └── ... and {len(items)-3} more")
    
    # Print integration relationships
    print("\n\n🔗 INTEGRATION POINTS")
    print("="*70)
    
    integrations = [e for e in entities 
                   if e.get('entityType') == 'landmark_integration_point']
    
    for integ in integrations:
        props = integ.get('properties', {})
        source = props.get('component', '?')
        target = props.get('target_component', '?')
        protocol = props.get('protocol', '?')
        print(f"   {source} ══► {target} [{protocol}]")

def print_graph_analysis():
    """Print graph analysis"""
    entities, stats = get_all_data()
    
    print("\n\n📈 GRAPH ANALYSIS")
    print("="*70)
    
    # Entity type distribution
    type_counts = defaultdict(int)
    for e in entities:
        type_counts[e.get('entityType', 'unknown')] += 1
    
    print("\n📊 Entity Distribution:")
    for entity_type, count in sorted(type_counts.items()):
        bar = "█" * (count // 2)
        print(f"   {entity_type:.<35} {count:3d} {bar}")
    
    # Component landmark density
    components, landmarks_by_component = build_component_tree(entities)
    
    print("\n🎯 Landmark Density by Component:")
    densities = []
    for comp_name, landmarks in landmarks_by_component.items():
        if comp_name != 'unknown':
            densities.append((comp_name, len(landmarks)))
    
    for comp_name, count in sorted(densities, key=lambda x: x[1], reverse=True):
        bar = "▓" * (count // 2)
        print(f"   {comp_name:.<20} {count:3d} {bar}")

def main():
    print_tree()
    print_graph_analysis()
    
    # Print raw JSON for one example
    print("\n\n🔍 EXAMPLE ENTITY (First Architectural Decision)")
    print("="*70)
    entities, _ = get_all_data()
    arch_decisions = [e for e in entities 
                     if e.get('entityType') == 'landmark_architecture_decision']
    if arch_decisions:
        print(json.dumps(arch_decisions[0], indent=2))

if __name__ == "__main__":
    main()