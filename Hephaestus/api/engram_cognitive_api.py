"""
Engram Cognitive API
WebSocket and HTTP endpoints for Engram-Sophia-Noesis integration
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from shared.integration.engram_cognitive_bridge import (
    get_cognitive_bridge,
    CognitiveEventType,
    CognitivePattern,
    CognitiveInsight
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/engram", tags=["engram"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.pattern_subscribers: List[WebSocket] = []
        self.insight_subscribers: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.pattern_subscribers:
            self.pattern_subscribers.remove(websocket)
        if websocket in self.insight_subscribers:
            self.insight_subscribers.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")
        
    async def broadcast(self, message: dict):
        """Broadcast to all connections"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")
                
    async def broadcast_to_subscribers(self, message: dict, subscriber_type: str):
        """Broadcast to specific subscribers"""
        subscribers = []
        if subscriber_type == "patterns":
            subscribers = self.pattern_subscribers
        elif subscriber_type == "insights":
            subscribers = self.insight_subscribers
            
        for connection in subscribers:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {subscriber_type}: {e}")

manager = ConnectionManager()


@router.websocket("/cognitive-stream")
async def cognitive_stream_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint for Engram cognitive data stream
    Handles bidirectional communication between UI and backend
    """
    await manager.connect(websocket)
    bridge = await get_cognitive_bridge()
    
    try:
        while True:
            # Receive data from client
            data = await websocket.receive_json()
            
            # Process based on message type
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                # Handle subscription requests
                channels = data.get('channels', [])
                if 'patterns' in channels:
                    manager.pattern_subscribers.append(websocket)
                if 'insights' in channels:
                    manager.insight_subscribers.append(websocket)
                    
                await websocket.send_json({
                    'type': 'subscription_confirmed',
                    'channels': channels
                })
                
            elif message_type == 'pattern_detected':
                # Process pattern detection
                await bridge.process_cognitive_event(
                    CognitiveEventType.PATTERN_DETECTED,
                    data.get('pattern', {})
                )
                
                # Broadcast to pattern subscribers
                await manager.broadcast_to_subscribers({
                    'type': 'pattern_processed',
                    'pattern': data.get('pattern'),
                    'timestamp': datetime.now().isoformat()
                }, 'patterns')
                
            elif message_type == 'blindspot_found':
                # Process blindspot
                await bridge.process_cognitive_event(
                    CognitiveEventType.BLINDSPOT_FOUND,
                    data.get('blindspot', {})
                )
                
                # Trigger immediate research
                await websocket.send_json({
                    'type': 'research_initiated',
                    'target': 'blindspot',
                    'status': 'processing'
                })
                
            elif message_type == 'inefficiency_detected':
                # Process inefficiency
                await bridge.process_cognitive_event(
                    CognitiveEventType.INEFFICIENCY_DETECTED,
                    data.get('inefficiency', {})
                )
                
            elif message_type == 'strength_identified':
                # Process strength
                await bridge.process_cognitive_event(
                    CognitiveEventType.STRENGTH_IDENTIFIED,
                    data.get('strength', {})
                )
                
            elif message_type == 'evolution_observed':
                # Process evolution
                await bridge.process_cognitive_event(
                    CognitiveEventType.EVOLUTION_OBSERVED,
                    data.get('evolution', {})
                )
                
            elif message_type == 'concept_formed':
                # Process concept formation
                await bridge.process_cognitive_event(
                    CognitiveEventType.CONCEPT_FORMED,
                    data.get('concept', {})
                )
                
            elif message_type == 'insight_generated':
                # Process insight
                await bridge.process_cognitive_event(
                    CognitiveEventType.INSIGHT_GENERATED,
                    data.get('insight', {})
                )
                
            elif message_type == 'research_request':
                # Handle direct research request
                research = data.get('research', {})
                # Queue research in bridge
                await bridge.research_queue.put(research)
                
                await websocket.send_json({
                    'type': 'research_queued',
                    'request_id': research.get('id'),
                    'priority': research.get('priority', 'medium')
                })
                
            elif message_type == 'get_status':
                # Return bridge status
                status = await bridge.get_status()
                await websocket.send_json({
                    'type': 'status_update',
                    'status': status
                })
                
            elif message_type == 'ping':
                # Health check
                await websocket.send_json({'type': 'pong'})
                
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.websocket("/patterns/stream")
async def patterns_stream_endpoint(websocket: WebSocket):
    """
    Dedicated WebSocket for pattern updates
    """
    await manager.connect(websocket)
    manager.pattern_subscribers.append(websocket)
    bridge = await get_cognitive_bridge()
    
    try:
        # Send initial patterns
        await websocket.send_json({
            'type': 'patterns_snapshot',
            'patterns': [
                pattern.__dict__ for pattern in bridge.active_patterns.values()
            ]
        })
        
        while True:
            # Keep connection alive
            await asyncio.sleep(30)
            await websocket.send_json({'type': 'heartbeat'})
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/insights/stream")
async def insights_stream_endpoint(websocket: WebSocket):
    """
    Dedicated WebSocket for insight updates
    """
    await manager.connect(websocket)
    manager.insight_subscribers.append(websocket)
    bridge = await get_cognitive_bridge()
    
    try:
        # Send initial insights
        await websocket.send_json({
            'type': 'insights_snapshot',
            'insights': [
                insight.__dict__ for insight in bridge.insights_cache.values()
            ]
        })
        
        while True:
            # Keep connection alive
            await asyncio.sleep(30)
            await websocket.send_json({'type': 'heartbeat'})
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# HTTP Endpoints for non-streaming operations

@router.get("/status")
async def get_status():
    """Get cognitive bridge status"""
    bridge = await get_cognitive_bridge()
    status = await bridge.get_status()
    return JSONResponse(content=status)


@router.get("/patterns")
async def get_patterns():
    """Get all active patterns"""
    bridge = await get_cognitive_bridge()
    patterns = [
        {
            'id': p.id,
            'name': p.name,
            'state': p.state,
            'strength': p.strength,
            'confidence': p.confidence
        }
        for p in bridge.active_patterns.values()
    ]
    return JSONResponse(content={'patterns': patterns})


@router.get("/insights")
async def get_insights():
    """Get all cached insights"""
    bridge = await get_cognitive_bridge()
    insights = [
        {
            'id': i.id,
            'type': i.type,
            'content': i.content,
            'severity': i.severity,
            'impact': i.impact
        }
        for i in bridge.insights_cache.values()
    ]
    return JSONResponse(content={'insights': insights})


@router.post("/pattern")
async def submit_pattern(pattern_data: dict):
    """Submit a new pattern for processing"""
    bridge = await get_cognitive_bridge()
    
    try:
        await bridge.process_cognitive_event(
            CognitiveEventType.PATTERN_DETECTED,
            pattern_data
        )
        
        # Broadcast to subscribers
        await manager.broadcast_to_subscribers({
            'type': 'pattern_submitted',
            'pattern': pattern_data
        }, 'patterns')
        
        return JSONResponse(
            content={'status': 'success', 'message': 'Pattern submitted for processing'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/insight")
async def submit_insight(insight_data: dict):
    """Submit a new insight for processing"""
    bridge = await get_cognitive_bridge()
    
    try:
        await bridge.process_cognitive_event(
            CognitiveEventType.INSIGHT_GENERATED,
            insight_data
        )
        
        # Broadcast to subscribers
        await manager.broadcast_to_subscribers({
            'type': 'insight_submitted',
            'insight': insight_data
        }, 'insights')
        
        return JSONResponse(
            content={'status': 'success', 'message': 'Insight submitted for processing'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/research")
async def request_research(research_data: dict):
    """Request research through Noesis"""
    bridge = await get_cognitive_bridge()
    
    try:
        # Queue research request
        await bridge.research_queue.put(research_data)
        
        return JSONResponse(
            content={
                'status': 'success',
                'message': 'Research request queued',
                'queue_size': bridge.research_queue.qsize()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learn")
async def request_learning(learning_data: dict):
    """Request learning through Sophia"""
    bridge = await get_cognitive_bridge()
    
    try:
        # Queue learning request
        await bridge.learning_queue.put(learning_data)
        
        return JSONResponse(
            content={
                'status': 'success',
                'message': 'Learning request queued',
                'queue_size': bridge.learning_queue.qsize()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Broadcast helper for bridge to UI communication
async def broadcast_to_engram_ui(data: dict):
    """Helper function to broadcast from bridge to UI"""
    await manager.broadcast(data)


# Export router for inclusion in main app
__all__ = ['router', 'broadcast_to_engram_ui']