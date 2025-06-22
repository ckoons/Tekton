#!/usr/bin/env python3
"""
Landmark Ingestion Pipeline for Athena Knowledge Graph

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


class LandmarkIngester:
    """Ingests landmarks into Athena knowledge graph"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.components_created = set()
        self.landmarks_created = 0
        self.relationships_created = 0
        
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
        
    async def ingest_all(self):
        """Main ingestion pipeline"""
        print("Starting landmark ingestion into Athena...")
        
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
            
        print(f"Created {len(self.components_created)} component entities")
        
        # Second pass: Create landmark entities
        print("\n2. Creating landmark entities...")
        
        for landmark_id in landmark_ids:
            landmark_file = LANDMARKS_DATA / f"{landmark_id}.json"
            if landmark_file.exists():
                with open(landmark_file) as f:
                    landmark = json.load(f)
                    await self._create_landmark_entity(landmark)
                    
        print(f"Created {self.landmarks_created} landmark entities")
        
        # Third pass: Create relationships
        print("\n3. Creating relationships...")
        
        # Component integration relationships
        await self._create_integration_relationships(landmark_ids)
        
        print(f"Created {self.relationships_created} relationships")
        
        print("\n✅ Ingestion complete!")
        print(f"  Components: {len(self.components_created)}")
        print(f"  Landmarks: {self.landmarks_created}")
        print(f"  Relationships: {self.relationships_created}")
        
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
        """Create a component entity in Athena"""
        
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
                f"{ATHENA_API}/entities",
                json=entity
            )
            if response.status_code == 200:
                self.components_created.add(component)
                print(f"  ✓ Created component: {component}")
            else:
                print(f"  ✗ Failed to create component {component}: {response.text}")
        except Exception as e:
            print(f"  ✗ Error creating component {component}: {e}")
            
    async def _create_landmark_entity(self, landmark: Dict):
        """Create a landmark entity in Athena"""
        
        component = self._extract_component(landmark)
        
        # Build entity
        entity = {
            "name": landmark.get("title", "Untitled"),
            "entity_type": f"landmark_{landmark.get('type', 'unknown')}",
            "properties": {
                "landmark_id": landmark.get("id"),
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
                f"{ATHENA_API}/entities",
                json=entity
            )
            if response.status_code == 200:
                self.landmarks_created += 1
                result = response.json()
                entity_id = result.get("id")
                
                # Create relationship to component
                # Note: We need to track component entity IDs properly
                # For now, skip relationship creation
            else:
                print(f"  ✗ Failed to create landmark: {response.text}")
        except Exception as e:
            print(f"  ✗ Error creating landmark: {e}")
            
    async def _create_relationship(self, source_id: str, target_id: str, 
                                 rel_type: str, properties: Dict = None):
        """Create a relationship between entities"""
        
        relationship = {
            "source_id": source_id,
            "target_id": target_id, 
            "type": rel_type,
            "properties": properties or {}
        }
        
        try:
            response = await self.client.post(
                f"{ATHENA_API}/relationships",
                json=relationship
            )
            if response.status_code == 200:
                self.relationships_created += 1
        except Exception as e:
            print(f"  ✗ Error creating relationship: {e}")
            
    async def _create_integration_relationships(self, landmark_ids: List[str]):
        """Create relationships between components based on integration_point landmarks"""
        
        for landmark_id in landmark_ids:
            landmark_file = LANDMARKS_DATA / f"{landmark_id}.json"
            if landmark_file.exists():
                with open(landmark_file) as f:
                    landmark = json.load(f)
                    
                if landmark.get("type") == "integration_point":
                    source_component = self._extract_component(landmark)
                    target_component = landmark.get("metadata", {}).get("target_component")
                    
                    if (source_component in self.components_created and 
                        target_component in self.components_created):
                        
                        await self._create_relationship(
                            f"component_{source_component}",
                            f"component_{target_component}",
                            "integrates_with",
                            {
                                "protocol": landmark.get("metadata", {}).get("protocol", ""),
                                "landmark_id": landmark_id
                            }
                        )


async def main():
    """Run the ingestion"""
    ingester = LandmarkIngester()
    try:
        await ingester.ingest_all()
    finally:
        await ingester.close()


if __name__ == "__main__":
    asyncio.run(main())