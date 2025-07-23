#!/usr/bin/env python3
"""
Landmark Ingestion Pipeline for Athena Knowledge Graph - Version 2

This ingests landmark data from the landmark system into Athena,
creating entities and relationships for architectural knowledge.
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import httpx
from datetime import datetime


# Paths
TEKTON_ROOT = Path(__file__).parent.parent.parent
LANDMARKS_DATA = TEKTON_ROOT / "landmarks" / "data"
ATHENA_API = "http://localhost:8005/api/v1"


class LandmarkIngesterV2:
    """Ingests landmarks into Athena knowledge graph with proper ID tracking"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self.component_entities = {}  # component_name -> entity_id
        self.landmark_entities = {}   # landmark_id -> entity_id
        self.relationships_created = 0
        
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
        
    async def ingest_all(self):
        """Main ingestion pipeline"""
        print("Starting landmark ingestion into Athena (v2)...")
        
        # Load registry to get active landmarks
        registry_file = LANDMARKS_DATA / "registry.json"
        if not registry_file.exists():
            print("No registry.json found!")
            return
            
        with open(registry_file) as f:
            registry = json.load(f)
            
        landmark_ids = registry.get("landmark_ids", [])
        print(f"Found {len(landmark_ids)} landmarks to ingest")
        
        # First pass: Create component entities
        print("\n1. Creating component entities...")
        components = set()
        
        for landmark_id in landmark_ids:
            landmark_file = LANDMARKS_DATA / f"{landmark_id}.json"
            if landmark_file.exists():
                with open(landmark_file) as f:
                    landmark = json.load(f)
                    component = self._extract_component(landmark)
                    if component and component != "unknown":
                        components.add(component)
                        
        for component in components:
            await self._create_component_entity(component)
            
        print(f"Created {len(self.component_entities)} component entities")
        
        # Second pass: Create landmark entities and relationships
        print("\n2. Creating landmark entities and relationships...")
        
        for landmark_id in landmark_ids:
            landmark_file = LANDMARKS_DATA / f"{landmark_id}.json"
            if landmark_file.exists():
                with open(landmark_file) as f:
                    landmark = json.load(f)
                    await self._create_landmark_entity_with_relationships(landmark)
                    
        print(f"Created {len(self.landmark_entities)} landmark entities")
        
        # Third pass: Create component-to-component relationships
        print("\n3. Creating component integration relationships...")
        await self._create_integration_relationships(landmark_ids)
        
        print(f"\n✅ Ingestion complete!")
        print(f"  Components: {len(self.component_entities)}")
        print(f"  Landmarks: {len(self.landmark_entities)}")
        print(f"  Relationships: {self.relationships_created}")
        
        # Sync to disk
        print("\n📁 Syncing to disk...")
        try:
            response = await self.client.post(f"{ATHENA_API}/knowledge/sync/")
            if response.status_code == 200:
                print("  ✓ Successfully synced knowledge graph to disk")
            else:
                print(f"  ✗ Failed to sync: {response.text}")
        except Exception as e:
            print(f"  ✗ Error syncing: {e}")
        
    def _extract_component(self, landmark: Dict) -> str:
        """Extract component name from landmark"""
        file_path = landmark.get("file_path", "")
        
        # Try to extract from path
        parts = Path(file_path).parts
        
        # Look for known component names
        components = ["Hermes", "Engram", "Rhetor", "Athena", "Prometheus", 
                     "Sophia", "Metis", "Budget", "Synthesis", "Harmonia", 
                     "Terma", "Hephaestus", "Telos", "Ergon"]
        
        for part in parts:
            if part in components:
                return part
                
        # Check if it's in shared
        if "shared" in parts or "utils" in parts or "tekton/core" in file_path:
            return "shared"
            
        return "unknown"
        
    async def _create_component_entity(self, component: str):
        """Create a component entity in Athena and store its ID"""
        
        entity = {
            "name": component,
            "entity_type": "component",
            "properties": {
                "category": "tekton_component",
                "description": f"Tekton {component} component",
                "created_at": datetime.now().isoformat()
            },
            "aliases": [component.lower()]
        }
        
        try:
            response = await self.client.post(
                f"{ATHENA_API}/entities/",
                json=entity
            )
            if response.status_code == 200:
                result = response.json()
                entity_id = result.get("entityId")
                self.component_entities[component] = entity_id
                print(f"  ✓ Created component: {component} (ID: {entity_id})")
            else:
                print(f"  ✗ Failed to create component {component}: Status {response.status_code}, {response.text}")
        except Exception as e:
            print(f"  ✗ Error creating component {component}: {e}")
            
    async def _create_landmark_entity_with_relationships(self, landmark: Dict):
        """Create a landmark entity and its relationships"""
        
        component = self._extract_component(landmark)
        landmark_id = landmark.get("id")
        
        # Build entity
        entity = {
            "name": landmark.get("title", "Untitled"),
            "entity_type": f"landmark_{landmark.get('type', 'unknown')}",
            "properties": {
                "landmark_id": landmark_id,
                "landmark_type": landmark.get("type"),
                "description": landmark.get("description", ""),
                "file_path": landmark.get("file_path"),
                "line_number": landmark.get("line_number"),
                "component": component,
                "author": landmark.get("author", "system"),
                "created_at": landmark.get("timestamp"),
                **landmark.get("metadata", {})
            },
            "aliases": []
        }
        
        try:
            response = await self.client.post(
                f"{ATHENA_API}/entities/",
                json=entity
            )
            if response.status_code == 200:
                result = response.json()
                entity_id = result.get("entityId")
                self.landmark_entities[landmark_id] = entity_id
                
                # Create relationship to component
                if component in self.component_entities:
                    await self._create_relationship(
                        self.component_entities[component],
                        entity_id,
                        "contains_landmark",
                        {
                            "landmark_type": landmark.get("type"),
                            "file_path": landmark.get("file_path")
                        }
                    )
            else:
                print(f"  ✗ Failed to create landmark {landmark_id}: Status {response.status_code}, {response.text}")
        except Exception as e:
            print(f"  ✗ Error creating landmark {landmark_id}: {e}")
            
    async def _create_relationship(self, source_id: str, target_id: str, 
                                 rel_type: str, properties: Dict = None):
        """Create a relationship between entities"""
        
        relationship = {
            "source_id": source_id,
            "target_id": target_id, 
            "relationship_type": rel_type,
            "properties": properties or {}
        }
        
        try:
            response = await self.client.post(
                f"{ATHENA_API}/relationships/",
                json=relationship
            )
            if response.status_code == 200:
                self.relationships_created += 1
            else:
                print(f"  ✗ Failed to create relationship: {response.text}")
        except Exception as e:
            print(f"  ✗ Error creating relationship: {e}")
            
    async def _create_integration_relationships(self, landmark_ids: List[str]):
        """Create relationships between components based on integration_point landmarks"""
        
        print("  Looking for integration point landmarks...")
        integration_count = 0
        
        for landmark_id in landmark_ids:
            landmark_file = LANDMARKS_DATA / f"{landmark_id}.json"
            if landmark_file.exists():
                with open(landmark_file) as f:
                    landmark = json.load(f)
                    
                if landmark.get("type") == "integration_point":
                    source_component = self._extract_component(landmark)
                    metadata = landmark.get("metadata", {})
                    target_component = metadata.get("target_component")
                    
                    # Also check for protocol and integration type
                    protocol = metadata.get("protocol", "unknown")
                    integration_type = metadata.get("integration_type", "unknown")
                    
                    if (source_component in self.component_entities and 
                        target_component and
                        target_component in self.component_entities):
                        
                        await self._create_relationship(
                            self.component_entities[source_component],
                            self.component_entities[target_component],
                            "integrates_with",
                            {
                                "protocol": protocol,
                                "integration_type": integration_type,
                                "landmark_id": landmark_id,
                                "description": landmark.get("description", "")
                            }
                        )
                        integration_count += 1
                        print(f"    ✓ {source_component} -> {target_component} ({protocol})")
                        
        print(f"  Created {integration_count} integration relationships")


async def main():
    """Run the ingestion"""
    ingester = LandmarkIngesterV2()
    try:
        await ingester.ingest_all()
    finally:
        await ingester.close()


if __name__ == "__main__":
    asyncio.run(main())