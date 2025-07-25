#!/usr/bin/env python3
"""
Populate Athena with discovered Tekton component relationships

This script uses proper Tekton patterns:
- TektonEnviron for environment variables
- tekton_url/athena_url for URL construction
- Dynamic port discovery
"""

import os
import sys
import asyncio
import httpx
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.env import TektonEnviron, TektonEnvironLock
from shared.urls import athena_url

# Load environment first
TektonEnvironLock.load()

# Component definitions - ports will be loaded dynamically
COMPONENTS = {
    "Hermes": {
        "description": "Central message bus and service discovery",
        "capabilities": ["messaging", "service_discovery", "health_monitoring"],
        "type": "infrastructure"
    },
    "Apollo": {
        "description": "Local attention and prediction for LLM orchestration", 
        "capabilities": ["llm_orchestration", "context_observation", "token_budget_management"],
        "type": "ai"
    },
    "Rhetor": {
        "description": "LLM service and communication hub",
        "capabilities": ["llm_access", "ai_specialists", "chat"],
        "type": "ai"
    },
    "Noesis": {
        "description": "Theoretical analysis and mathematical frameworks",
        "capabilities": ["theoretical_analysis", "manifold_analysis", "catastrophe_theory"],
        "type": "research"
    },
    "Engram": {
        "description": "Memory and knowledge storage system",
        "capabilities": ["memory_storage", "vector_search", "event_streaming"],
        "type": "storage"
    },
    "Telos": {
        "description": "Requirements management system",
        "capabilities": ["requirements_tracking", "project_management", "refinement"],
        "type": "planning"
    },
    "Prometheus": {
        "description": "Planning and monitoring engine",
        "capabilities": ["plan_generation", "monitoring", "alerting"],
        "type": "planning"
    },
    "Penia": {
        "description": "Token budget and resource management",
        "capabilities": ["budget_tracking", "resource_allocation", "cost_analysis"],
        "type": "infrastructure"
    },
    "Synthesis": {
        "description": "Plan execution and component orchestration",
        "capabilities": ["plan_execution", "task_orchestration", "integration"],
        "type": "execution"
    },
    "Athena": {
        "description": "Knowledge graph and reasoning engine",
        "capabilities": ["knowledge_graph", "reasoning", "semantic_search"],
        "type": "knowledge"
    },
    "Sophia": {
        "description": "Experimental research and collective intelligence",
        "capabilities": ["experimental_research", "team_coordination", "hypothesis_testing"],
        "type": "research"
    },
    "Metis": {
        "description": "Workflow and task management",
        "capabilities": ["workflow_management", "task_tracking", "scheduling"],
        "type": "execution"
    },
    "Terma": {
        "description": "Terminal interface and boundaries",
        "capabilities": ["terminal_interface", "boundary_management", "mcp_tools"],
        "type": "interface"
    },
    "Hephaestus": {
        "description": "Web UI and frontend layer",
        "capabilities": ["web_ui", "visualization", "user_interaction"],
        "type": "interface"
    },
    "Numa": {
        "description": "Platform AI mentor providing guidance and oversight",
        "capabilities": ["companion_chat", "team_chat", "platform_guidance"],
        "type": "ai"
    },
    "Harmonia": {
        "description": "Workflow orchestration and state management",
        "capabilities": ["workflow_orchestration", "state_management", "balance"],
        "type": "workflow"
    },
    "Ergon": {
        "description": "Agent system for specialized task execution",
        "capabilities": ["agent_creation", "agent_execution", "tool_integration"],
        "type": "execution"
    },
    "Tekton_Core": {
        "description": "Core orchestration and startup management",
        "capabilities": ["startup_management", "component_orchestration", "lifecycle"],
        "type": "infrastructure"
    }
}

# Integration relationships discovered
RELATIONSHIPS = [
    # Core Infrastructure
    {
        "source": "All Components",
        "target": "Hermes",
        "type": "registers_with",
        "properties": {
            "protocol": "HTTP REST",
            "purpose": "Service discovery and health monitoring",
            "startup": True
        }
    },
    
    # Apollo integrations
    {
        "source": "Apollo", 
        "target": "Rhetor",
        "type": "monitors",
        "properties": {
            "protocol": "HTTP REST",
            "purpose": "LLM context monitoring and control",
            "data_flow": "metrics, sessions, directives"
        }
    },
    {
        "source": "Apollo",
        "target": "Hermes", 
        "type": "publishes_to",
        "properties": {
            "protocol": "WebSocket/HTTP",
            "purpose": "Event publishing and message distribution",
            "event_types": ["context_update", "prediction", "alert"]
        }
    },
    
    # Noesis integrations
    {
        "source": "Noesis",
        "target": "Engram",
        "type": "streams_from", 
        "properties": {
            "protocol": "WebSocket/Polling",
            "purpose": "Memory data streaming for theoretical analysis",
            "data_flow": "memory events → mathematical analysis"
        }
    },
    
    # Telos integrations
    {
        "source": "Telos",
        "target": "Prometheus",
        "type": "sends_requirements_to",
        "properties": {
            "protocol": "Direct Python/HTTP",
            "purpose": "Requirements to planning transformation",
            "data_flow": "requirements → plans"
        }
    },
    
    # Penia integrations
    {
        "source": "Penia",
        "target": "Rhetor",
        "type": "monitors_usage",
        "properties": {
            "protocol": "HTTP/WebSocket",
            "purpose": "Token usage tracking and budget enforcement",
            "data_flow": "usage_metrics"
        }
    },
    
    # Synthesis integrations
    {
        "source": "Synthesis",
        "target": "Prometheus",
        "type": "executes_plans_from",
        "properties": {
            "protocol": "Direct import/HTTP",
            "purpose": "Plan retrieval and execution",
            "fallback_chain": True
        }
    },
    {
        "source": "Synthesis", 
        "target": "Athena",
        "type": "queries_knowledge_from",
        "properties": {
            "protocol": "Direct import/HTTP",
            "purpose": "Knowledge graph queries during execution",
            "fallback_chain": True
        }
    },
    
    # Harmonia integrations
    {
        "source": "Harmonia",
        "target": "Synthesis",
        "type": "orchestrates",
        "properties": {
            "protocol": "HTTP REST",
            "purpose": "Workflow orchestration and coordination",
            "data_flow": "workflow_definitions → execution_plans"
        }
    },
    
    # Shared configuration
    {
        "source": "All Components",
        "target": "Shared Infrastructure",
        "type": "uses_configuration",
        "properties": {
            "config_type": "environment",
            "key_vars": ["TEKTON_ROOT", "component_ports"],
            "shared_utils": ["urls.py", "TektonEnviron", "StandardComponentBase"]
        }
    }
]

# Integration patterns
PATTERNS = [
    {
        "name": "Service Discovery Pattern",
        "description": "Components register with Hermes at startup for discovery",
        "components": ["All"],
        "benefits": ["Loose coupling", "Dynamic discovery", "Health monitoring"]
    },
    {
        "name": "Event-Driven Messaging Pattern",
        "description": "Asynchronous communication through Hermes pub/sub",
        "components": ["All"],
        "benefits": ["Decoupling", "Scalability", "Real-time updates"]
    },
    {
        "name": "Direct API Integration Pattern",
        "description": "Synchronous HTTP REST calls between components",
        "components": ["Apollo→Rhetor", "Telos→Prometheus"],
        "benefits": ["Simple", "Request/response", "Type safety"]
    },
    {
        "name": "Fallback Chain Pattern",
        "description": "Multiple integration methods with graceful degradation",
        "components": ["Synthesis"],
        "benefits": ["Reliability", "Flexibility", "Error handling"]
    }
]


class AthenaPopulator:
    """Populate Athena with component knowledge"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self.component_entities = {}
        self.pattern_entities = {}
        
    async def close(self):
        await self.client.aclose()
        
    async def populate_all(self):
        """Main population pipeline"""
        # Print environment info
        tekton_root = TektonEnviron.get('TEKTON_ROOT')
        athena_port = TektonEnviron.get('ATHENA_PORT', '8305')
        print(f"🚀 Populating Athena Knowledge Graph")
        print(f"   TEKTON_ROOT: {tekton_root}")
        print(f"   ATHENA_PORT: {athena_port}")
        print(f"   ATHENA_URL: {athena_url('')}")
        print()
        
        # Create component entities
        print("1️⃣ Creating component entities...")
        for name, props in COMPONENTS.items():
            # Get dynamic port for each component
            port_var = f"{name.upper().replace('_', '')}_PORT"
            port = TektonEnviron.get(port_var)
            if port:
                props['port'] = int(port)
            
            entity_id = await self.create_component(name, props)
            if entity_id:
                self.component_entities[name] = entity_id
                
        print(f"   ✅ Created {len(self.component_entities)} components")
        
        # Create pattern entities
        print("\n2️⃣ Creating integration pattern entities...")
        for pattern in PATTERNS:
            entity_id = await self.create_pattern(pattern)
            if entity_id:
                self.pattern_entities[pattern['name']] = entity_id
                
        print(f"   ✅ Created {len(self.pattern_entities)} patterns")
        
        # Create relationships
        print("\n3️⃣ Creating component relationships...")
        relationships_created = 0
        
        for rel in RELATIONSHIPS:
            # Handle "All Components" source
            if rel['source'] == "All Components":
                # Create a list to avoid dictionary modification during iteration
                components = list(self.component_entities.keys())
                for comp in components:
                    if comp != rel['target']:
                        if await self.create_relationship(comp, rel['target'], rel['type'], rel['properties']):
                            relationships_created += 1
            else:
                if await self.create_relationship(rel['source'], rel['target'], rel['type'], rel['properties']):
                    relationships_created += 1
                    
        print(f"   ✅ Created {relationships_created} relationships")
        
        # Sync to disk
        print("\n4️⃣ Syncing to disk...")
        await self.sync_to_disk()
        
        print("\n✨ Population complete!")
        
    async def create_component(self, name: str, properties: Dict) -> Optional[str]:
        """Create a component entity"""
        entity = {
            "name": name,
            "entity_type": "tekton_component",
            "properties": {
                **properties,
                "component_name": name.lower().replace('_', '-')
            },
            "aliases": [name.lower(), f"tekton-{name.lower()}"]
        }
        
        try:
            url = athena_url('/api/v1/entities/')
            response = await self.client.post(url, json=entity)
            
            if response.status_code == 200:
                result = response.json()
                entity_id = result.get("entityId")
                port_info = f" (port {properties.get('port')})" if 'port' in properties else ""
                print(f"   ✓ {name} ({properties['type']}){port_info}")
                return entity_id
            else:
                print(f"   ✗ Failed to create {name}: {response.text}")
        except Exception as e:
            print(f"   ✗ Error creating {name}: {e}")
            
        return None
        
    async def create_pattern(self, pattern: Dict) -> Optional[str]:
        """Create an integration pattern entity"""
        entity = {
            "name": pattern['name'],
            "entity_type": "integration_pattern",
            "properties": pattern,
            "aliases": [pattern['name'].lower().replace(' ', '_')]
        }
        
        try:
            url = athena_url('/api/v1/entities/')
            response = await self.client.post(url, json=entity)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✓ {pattern['name']}")
                return result.get("entityId")
        except Exception as e:
            print(f"   ✗ Error creating pattern {pattern['name']}: {e}")
            
        return None
        
    async def create_relationship(self, source: str, target: str, 
                                rel_type: str, properties: Dict) -> bool:
        """Create a relationship between entities"""
        
        # Skip if entities don't exist
        if source not in self.component_entities:
            # Handle special cases
            if source == "Shared Infrastructure":
                # Create it
                entity_id = await self.create_component("Shared Infrastructure", {
                    "description": "Shared utilities and configuration",
                    "type": "infrastructure",
                    "capabilities": ["configuration", "utilities", "base_classes"]
                })
                if entity_id:
                    self.component_entities[source] = entity_id
                else:
                    return False
            else:
                return False
                
        if target not in self.component_entities:
            # Similar handling for target
            if target == "Shared Infrastructure":
                entity_id = await self.create_component("Shared Infrastructure", {
                    "description": "Shared utilities and configuration", 
                    "type": "infrastructure",
                    "capabilities": ["configuration", "utilities", "base_classes"]
                })
                if entity_id:
                    self.component_entities[target] = entity_id
                else:
                    return False
            else:
                return False
        
        relationship = {
            "source_id": self.component_entities[source],
            "target_id": self.component_entities[target],
            "relationship_type": rel_type,
            "properties": properties
        }
        
        try:
            url = athena_url('/api/v1/relationships/')
            response = await self.client.post(url, json=relationship)
            return response.status_code == 200
        except Exception as e:
            print(f"   ✗ Error creating relationship {source}→{target}: {e}")
            return False
            
    async def sync_to_disk(self):
        """Sync knowledge graph to disk"""
        try:
            url = athena_url('/api/v1/knowledge/sync/')
            response = await self.client.post(url)
            if response.status_code == 200:
                print("   ✓ Successfully synced to disk")
            else:
                print(f"   ✗ Sync failed: {response.text}")
        except Exception as e:
            print(f"   ✗ Error syncing: {e}")


async def main():
    populator = AthenaPopulator()
    try:
        await populator.populate_all()
    finally:
        await populator.close()


if __name__ == "__main__":
    asyncio.run(main())