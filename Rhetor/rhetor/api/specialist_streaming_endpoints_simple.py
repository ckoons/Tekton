"""
Simplified streaming endpoints for CI specialists.

Uses the simple CI manager instead of discovery service.
"""
from typing import Dict, List, Optional, AsyncIterator
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
import json
import logging
import asyncio

from rhetor.core.ai_manager import CIManager

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/ai/stream", tags=["ai-streaming"])

# Global CI manager instance
ai_manager = CIManager()


async def stream_ai_response(ai_id: str, message: str) -> AsyncIterator[str]:
    """
    Stream response from an CI specialist.
    
    Note: Current AIs don't support true streaming, so this simulates it
    by sending the response in chunks.
    """
    try:
        # Get full response first (AIs don't stream yet)
        result = await ai_manager.send_to_ai(ai_id, message)
        
        if not result['success']:
            yield f"data: {json.dumps({'error': result['error']})}\n\n"
            return
        
        response = result['response']
        
        # Simulate streaming by chunking the response
        chunk_size = 50  # characters per chunk
        for i in range(0, len(response), chunk_size):
            chunk = response[i:i + chunk_size]
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            await asyncio.sleep(0.05)  # Small delay to simulate streaming
        
        # Send completion event
        yield f"data: {json.dumps({'done': True})}\n\n"
        
    except Exception as e:
        logger.error(f"Streaming error for {ai_id}: {e}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


@router.get("/chat/{ai_id}")
async def stream_chat(
    ai_id: str,
    message: str = Query(..., description="Message to send to AI"),
    simulate_streaming: bool = Query(True, description="Simulate streaming response")
):
    """
    Stream chat response from an CI specialist.
    
    Note: Since our AIs don't support true streaming yet, this endpoint
    simulates streaming by chunking the response.
    """
    # Check if CI exists and is healthy
    component_id = ai_id.replace('-ci', '')
    try:
        ai_info = ai_manager.get_ai_info(component_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"AI specialist {ai_id} not found")
    
    if not await ai_manager.check_ai_health(ai_id):
        raise HTTPException(
            status_code=503,
            detail=f"AI specialist {ai_id} is not healthy"
        )
    
    if simulate_streaming:
        return StreamingResponse(
            stream_ai_response(ai_id, message),
            media_type="text/event-stream"
        )
    else:
        # Regular non-streaming response
        result = await ai_manager.send_to_ai(ai_id, message)
        if result['success']:
            return {"response": result['response']}
        else:
            raise HTTPException(status_code=500, detail=result['error'])


@router.get("/multi-stream")
async def multi_stream_chat(
    message: str = Query(..., description="Message to broadcast"),
    ai_ids: List[str] = Query(..., description="List of CI IDs to query"),
    parallel: bool = Query(True, description="Query AIs in parallel")
):
    """
    Stream responses from multiple CI specialists.
    
    This can query multiple AIs either in parallel or sequentially.
    """
    async def multi_stream():
        if parallel:
            # Query all AIs in parallel
            tasks = []
            for ai_id in ai_ids:
                tasks.append(ai_manager.send_to_ai(ai_id, message))
            
            # Start all tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Stream results as they complete
            for ai_id, result in zip(ai_ids, results):
                if isinstance(result, Exception):
                    yield f"data: {json.dumps({'ai_id': ai_id, 'error': str(result)})}\n\n"
                elif result['success']:
                    yield f"data: {json.dumps({'ai_id': ai_id, 'response': result['response']})}\n\n"
                else:
                    yield f"data: {json.dumps({'ai_id': ai_id, 'error': result['error']})}\n\n"
        else:
            # Query AIs sequentially
            for ai_id in ai_ids:
                result = await ai_manager.send_to_ai(ai_id, message)
                
                if result['success']:
                    yield f"data: {json.dumps({'ai_id': ai_id, 'response': result['response']})}\n\n"
                else:
                    yield f"data: {json.dumps({'ai_id': ai_id, 'error': result['error']})}\n\n"
        
        # Send completion
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return StreamingResponse(
        multi_stream(),
        media_type="text/event-stream"
    )


@router.get("/health-stream")
async def stream_health_checks():
    """
    Stream real-time health status of all CI specialists.
    
    Useful for monitoring dashboards.
    """
    async def health_stream():
        while True:
            health_status = []
            
            for component_id in ai_manager.get_all_ai_components():
                ai_id = f"{component_id}-ci"
                healthy = await ai_manager.check_ai_health(ai_id)
                
                health_status.append({
                    'ai_id': ai_id,
                    'component': component_id,
                    'healthy': healthy,
                    'status': 'online' if healthy else 'offline'
                })
            
            yield f"data: {json.dumps({'health_status': health_status})}\n\n"
            
            # Wait 5 seconds before next check
            await asyncio.sleep(5)
    
    return StreamingResponse(
        health_stream(),
        media_type="text/event-stream"
    )
