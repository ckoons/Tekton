#!/usr/bin/env python3
"""
Athena Knowledge Graph Test Suite
Tests the ingested landmark data without visualization
"""

import httpx
import json
from typing import Dict, List, Any

try:
    from shared.urls import athena_url
    BASE_URL = athena_url("/api/v1")
except ImportError:
    # Fallback if shared module not available
    from shared.env import TektonEnviron
    env = TektonEnviron()
    port = env.get_port("ATHENA_PORT", 8105)
    BASE_URL = f"http://localhost:{port}/api/v1"

class AthenaTestSuite:
    def __init__(self):
        self.client = httpx.Client(base_url=BASE_URL, follow_redirects=True)
        self.results = []
        
    def run_test(self, name: str, func):
        """Run a test and collect results"""
        print(f"\n{'='*60}")
        print(f"TEST: {name}")
        print('='*60)
        try:
            result = func()
            self.results.append((name, "PASS", result))
            return result
        except Exception as e:
            print(f"❌ FAILED: {e}")
            self.results.append((name, "FAIL", str(e)))
            return None
    
    def test_basic_stats(self):
        """Test 1: Basic statistics"""
        response = self.client.get("/knowledge/stats")
        stats = response.json()
        print(f"✓ Entities: {stats['entity_count']}")
        print(f"✓ Relationships: {stats['relationship_count']}")
        print(f"✓ Storage: {stats['adapter_type']}")
        return stats
    
    def test_component_inventory(self):
        """Test 2: List all components"""
        # Direct entity access since search has a bug
        response = self.client.get("/entities/entities?limit=100")
        if response.status_code == 200:
            all_entities = response.json()
            components = [e for e in all_entities if e.get('entityType') == 'component']
            print(f"✓ Found {len(components)} components:")
            for comp in sorted(components, key=lambda x: x['name']):
                print(f"  - {comp['name']} (ID: {comp['entityId'][:8]}...)")
            return components
        return []
    
    def test_landmark_types(self):
        """Test 3: Analyze landmark types"""
        response = self.client.get("/entities/entities?limit=100")
        if response.status_code == 200:
            all_entities = response.json()
            landmarks = [e for e in all_entities if 'landmark_' in e.get('entityType', '')]
            
            # Count by type
            type_counts = {}
            for lm in landmarks:
                lm_type = lm['entityType'].replace('landmark_', '')
                type_counts[lm_type] = type_counts.get(lm_type, 0) + 1
            
            print(f"✓ Total landmarks: {len(landmarks)}")
            print("✓ Landmark types:")
            for lm_type, count in sorted(type_counts.items()):
                print(f"  - {lm_type}: {count}")
            return type_counts
        return {}
    
    def test_architectural_decisions(self):
        """Test 4: Extract architectural decisions"""
        response = self.client.get("/entities/entities?limit=100")
        if response.status_code == 200:
            all_entities = response.json()
            decisions = [e for e in all_entities 
                        if e.get('entityType') == 'landmark_architectural_decision']
            
            print(f"✓ Found {len(decisions)} architectural decisions:")
            for dec in decisions[:5]:  # Show first 5
                print(f"\n  Decision: {dec['name']}")
                props = dec.get('properties', {})
                if props.get('description'):
                    print(f"  Description: {props['description'][:100]}...")
                if props.get('component'):
                    print(f"  Component: {props['component']}")
            return decisions
        return []
    
    def test_integration_points(self):
        """Test 5: Find integration points between components"""
        response = self.client.get("/entities/entities?limit=100")
        if response.status_code == 200:
            all_entities = response.json()
            integrations = [e for e in all_entities 
                           if e.get('entityType') == 'landmark_integration_point']
            
            print(f"✓ Found {len(integrations)} integration points:")
            for integ in integrations:
                props = integ.get('properties', {})
                source = props.get('component', 'unknown')
                target = props.get('target_component', 'unknown')
                protocol = props.get('protocol', 'unknown')
                print(f"  - {source} → {target} ({protocol})")
            return integrations
        return []
    
    def test_component_relationships(self):
        """Test 6: Analyze component relationships"""
        # First get a component
        response = self.client.get("/entities/entities?limit=100")
        if response.status_code == 200:
            all_entities = response.json()
            components = [e for e in all_entities if e.get('entityType') == 'component']
            
            if components:
                # Test with Hermes
                hermes = next((c for c in components if c['name'] == 'Hermes'), None)
                if hermes:
                    print(f"✓ Analyzing relationships for Hermes (ID: {hermes['entityId'][:8]}...)")
                    
                    # Get relationships
                    rel_response = self.client.get(
                        f"/knowledge/entities/{hermes['entityId']}/relationships"
                    )
                    if rel_response.status_code == 200:
                        relationships = rel_response.json()
                        print(f"  Found {len(relationships)} relationships")
                        
                        # Count by type
                        rel_types = {}
                        for rel in relationships:
                            rel_type = rel['relationship']['relationship_type']
                            rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
                        
                        for rel_type, count in rel_types.items():
                            print(f"  - {rel_type}: {count}")
                        return relationships
        return []
    
    def test_shared_utilities(self):
        """Test 7: Analyze shared utilities usage"""
        response = self.client.get("/entities/entities?limit=100")
        if response.status_code == 200:
            all_entities = response.json()
            shared_landmarks = [e for e in all_entities 
                               if e.get('properties', {}).get('component') == 'shared']
            
            print(f"✓ Found {len(shared_landmarks)} shared/utility landmarks:")
            
            # Group by type
            by_type = {}
            for lm in shared_landmarks:
                lm_type = lm['entityType'].replace('landmark_', '')
                if lm_type not in by_type:
                    by_type[lm_type] = []
                by_type[lm_type].append(lm['name'])
            
            for lm_type, names in by_type.items():
                print(f"\n  {lm_type} ({len(names)}):")
                for name in names[:3]:  # First 3
                    print(f"    - {name}")
            return shared_landmarks
        return []
    
    def test_query_paths(self):
        """Test 8: Find paths between components"""
        # Get two components
        response = self.client.get("/entities/entities?limit=100")
        if response.status_code == 200:
            all_entities = response.json()
            components = [e for e in all_entities if e.get('entityType') == 'component']
            
            hermes = next((c for c in components if c['name'] == 'Hermes'), None)
            rhetor = next((c for c in components if c['name'] == 'Rhetor'), None)
            
            if hermes and rhetor:
                print(f"✓ Finding paths: Rhetor → Hermes")
                path_response = self.client.get(
                    f"/knowledge/path?source_id={rhetor['entityId']}&target_id={hermes['entityId']}"
                )
                if path_response.status_code == 200:
                    paths = path_response.json()
                    print(f"  Found {len(paths)} paths")
                    return paths
        return []
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print('='*60)
        passed = sum(1 for _, status, _ in self.results if status == "PASS")
        failed = sum(1 for _, status, _ in self.results if status == "FAIL")
        print(f"✓ Passed: {passed}")
        print(f"✗ Failed: {failed}")
        print(f"Total: {len(self.results)}")


def main():
    suite = AthenaTestSuite()
    
    # Run all tests
    suite.run_test("Basic Statistics", suite.test_basic_stats)
    suite.run_test("Component Inventory", suite.test_component_inventory)
    suite.run_test("Landmark Type Analysis", suite.test_landmark_types)
    suite.run_test("Architectural Decisions", suite.test_architectural_decisions)
    suite.run_test("Integration Points", suite.test_integration_points)
    suite.run_test("Component Relationships", suite.test_component_relationships)
    suite.run_test("Shared Utilities Analysis", suite.test_shared_utilities)
    suite.run_test("Path Finding", suite.test_query_paths)
    
    suite.print_summary()


if __name__ == "__main__":
    main()