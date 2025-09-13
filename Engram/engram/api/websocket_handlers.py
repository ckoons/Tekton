"""
WebSocket handlers for real-time ESR Experience and Cognition monitoring
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from enum import Enum
import random

logger = logging.getLogger(__name__)

class BrainRegion(Enum):
    """Brain regions mapped to CI functions"""
    PREFRONTAL_CORTEX = "prefrontalCortex"
    HIPPOCAMPUS = "hippocampus"
    AMYGDALA = "amygdala"
    TEMPORAL_LOBE = "temporalLobe"
    MOTOR_CORTEX = "motorCortex"
    BROCAS_AREA = "brocasArea"
    WERNICKES_AREA = "wernickesArea"
    ANTERIOR_CINGULATE = "anteriorCingulate"
    DEFAULT_MODE_NETWORK = "defaultModeNetwork"
    DOPAMINE_PATHWAYS = "dopaminePathways"

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {
            "cognition": [],
            "experience": []
        }
        self.ci_states: Dict[str, Dict] = {}
        self.region_activations: Dict[str, Dict[str, float]] = {}
        
    async def connect(self, websocket: WebSocket, endpoint: str):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        if endpoint not in self.active_connections:
            self.active_connections[endpoint] = []
        self.active_connections[endpoint].append(websocket)
        logger.info(f"WebSocket connected to {endpoint}")
        
    def disconnect(self, websocket: WebSocket, endpoint: str):
        """Remove a WebSocket connection"""
        if endpoint in self.active_connections:
            self.active_connections[endpoint].remove(websocket)
        logger.info(f"WebSocket disconnected from {endpoint}")
        
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific connection"""
        await websocket.send_text(message)
        
    async def broadcast(self, message: str, endpoint: str):
        """Broadcast a message to all connections on an endpoint"""
        for connection in self.active_connections.get(endpoint, []):
            try:
                await connection.send_text(message)
            except:
                # Connection might be closed
                pass

manager = ConnectionManager()

async def cognition_websocket_endpoint(websocket: WebSocket, ci_id: str = "apollo"):
    """
    WebSocket endpoint for Cognition panel brain visualization
    Streams real-time cognitive state updates
    """
    await manager.connect(websocket, "cognition")
    
    try:
        # Initialize CI state if not exists
        if ci_id not in manager.ci_states:
            manager.ci_states[ci_id] = {
                "working_memory": [],
                "emotions": {"valence": 0, "arousal": 0.5, "dominance": 0.5},
                "active_regions": {},
                "thought_flow": []
            }
            manager.region_activations[ci_id] = {
                region.value: 0.0 for region in BrainRegion
            }
        
        # Send initial state
        await websocket.send_text(json.dumps({
            "type": "initial_state",
            "ci_id": ci_id,
            "regions": manager.region_activations[ci_id],
            "state": manager.ci_states[ci_id]
        }))
        
        # Start sending updates
        while True:
            try:
                # Wait for client messages or send periodic updates
                message = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                data = json.loads(message)
                
                # Handle client requests
                if data.get("action") == "subscribe":
                    selected_ci = data.get("ci", ci_id)
                    metrics = data.get("metrics", [])
                    
                    # Send current state for selected CI
                    await websocket.send_text(json.dumps({
                        "type": "subscription_update",
                        "ci_id": selected_ci,
                        "metrics": metrics,
                        "regions": manager.region_activations.get(selected_ci, {})
                    }))
                    
            except asyncio.TimeoutError:
                # Send periodic updates based on ESR activity
                await send_cognitive_update(websocket, ci_id)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, "cognition")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, "cognition")

async def send_cognitive_update(websocket: WebSocket, ci_id: str):
    """Send cognitive state update to client"""
    try:
        # Get current ESR state (integrate with actual ESR system)
        from engram.core.storage.unified_interface import ESRMemorySystem
        from engram.core.experience.experience_layer import ExperienceManager
        
        # For now, simulate updates based on ESR activity
        update_data = await generate_cognitive_update(ci_id)
        
        if update_data:
            await websocket.send_text(json.dumps(update_data))
            
    except Exception as e:
        logger.error(f"Error sending cognitive update: {e}")

async def generate_cognitive_update(ci_id: str):
    """
    Generate cognitive update based on ESR activity
    This will be integrated with the actual ESR system
    """
    import random
    
    # Simulate region activations based on current processing
    regions = manager.region_activations.get(ci_id, {})
    
    # Randomly update some regions (will be replaced with real ESR data)
    update_type = random.choice([
        "region_activation",
        "thought_flow",
        "emotional_state",
        "consolidation",
        "pattern_detected"
    ])
    
    if update_type == "region_activation":
        # Update a random region's activation
        region = random.choice(list(BrainRegion))
        activation = random.random()
        regions[region.value] = activation
        
        return {
            "type": "region_activation",
            "region": region.value,
            "activation": activation,
            "timestamp": datetime.now().isoformat()
        }
        
    elif update_type == "thought_flow":
        # Simulate thought moving between regions
        from_region = random.choice(list(BrainRegion))
        to_region = random.choice(list(BrainRegion))
        
        return {
            "type": "thought_flow",
            "from": from_region.value,
            "to": to_region.value,
            "thought": "Processing query...",
            "timestamp": datetime.now().isoformat()
        }
        
    elif update_type == "emotional_state":
        # Update emotional state
        return {
            "type": "emotional_state",
            "emotion": {
                "valence": random.uniform(-1, 1),
                "arousal": random.random(),
                "dominance": random.random(),
                "primary_emotion": random.choice(["joy", "surprise", "neutral", "focus"])
            },
            "timestamp": datetime.now().isoformat()
        }
        
    elif update_type == "consolidation":
        # Memory consolidation event
        return {
            "type": "consolidation",
            "memories": [
                {"id": f"mem_{random.randint(1000, 9999)}", "content": "Consolidated thought"}
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    elif update_type == "pattern_detected":
        # Pattern detection event
        return {
            "type": "pattern_detected",
            "pattern": {
                "name": "Recurring concept",
                "strength": random.random(),
                "regions": [BrainRegion.TEMPORAL_LOBE.value, BrainRegion.HIPPOCAMPUS.value]
            },
            "timestamp": datetime.now().isoformat()
        }
    
    return None

async def experience_websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for ESR Experience updates
    Streams working memory, consolidation events, etc.
    """
    await manager.connect(websocket, "experience")
    
    try:
        while True:
            # Wait for client messages
            message = await websocket.receive_text()
            data = json.loads(message)
            
            # Handle different message types
            if data.get("action") == "trigger_boundary":
                # Trigger a boundary event
                boundary_type = data.get("boundary_type")
                await handle_boundary_trigger(websocket, boundary_type)
                
            elif data.get("action") == "inject_emotion":
                # Inject emotional state
                emotion = data.get("emotion")
                await handle_emotion_injection(websocket, emotion)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, "experience")
    except Exception as e:
        logger.error(f"Experience WebSocket error: {e}")
        manager.disconnect(websocket, "experience")

async def handle_boundary_trigger(websocket: WebSocket, boundary_type: str):
    """Handle manual boundary trigger from UI"""
    response = {
        "type": "boundary_detected",
        "boundary_type": boundary_type,
        "confidence": 0.9,
        "timestamp": datetime.now().isoformat()
    }
    await websocket.send_text(json.dumps(response))
    
    # Trigger consolidation after boundary
    await asyncio.sleep(1)
    consolidation = {
        "type": "memory_consolidated",
        "memories": [
            {"id": f"mem_{i}", "content": f"Thought {i}"} 
            for i in range(random.randint(2, 5))
        ],
        "timestamp": datetime.now().isoformat()
    }
    await websocket.send_text(json.dumps(consolidation))

async def handle_emotion_injection(websocket: WebSocket, emotion: dict):
    """Handle emotional state injection from UI"""
    response = {
        "type": "emotion_change",
        "mood": emotion,
        "timestamp": datetime.now().isoformat()
    }
    await websocket.send_text(json.dumps(response))

def integrate_with_esr(esr_system):
    """
    Integrate WebSocket handlers with actual ESR system
    This function will be called when ESR events occur
    """
    async def on_memory_formation(memory):
        """Called when a new memory is formed"""
        await manager.broadcast(json.dumps({
            "type": "memory_formed",
            "memory": {
                "id": memory.id,
                "content": memory.content,
                "emotion": memory.emotional_context
            },
            "timestamp": datetime.now().isoformat()
        }), "experience")
    
    async def on_consolidation(memories):
        """Called when memories are consolidated"""
        await manager.broadcast(json.dumps({
            "type": "memory_consolidated",
            "memories": [{"id": m.id, "content": m.content} for m in memories],
            "timestamp": datetime.now().isoformat()
        }), "experience")
    
    async def on_thought_active(thought):
        """Called when a thought becomes active in working memory"""
        await manager.broadcast(json.dumps({
            "type": "working_memory_update",
            "thoughts": [
                {
                    "id": thought.id,
                    "content": thought.content,
                    "state": thought.state,
                    "access_count": thought.access_count
                }
            ],
            "timestamp": datetime.now().isoformat()
        }), "experience")
    
    # Return handlers for ESR to call
    return {
        "on_memory_formation": on_memory_formation,
        "on_consolidation": on_consolidation,
        "on_thought_active": on_thought_active
    }