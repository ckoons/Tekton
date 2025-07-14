"""
API endpoints for Engram streaming and theoretical analysis
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

# Global router for streaming endpoints
streaming_router = APIRouter(prefix="/streaming", tags=["streaming"])


async def get_noesis_component():
    """Get the Noesis component instance - to be injected via dependency"""
    # This will be provided by the FastAPI app
    from noesis.core.noesis_component import NoesisComponent
    # In real implementation, this would be injected via FastAPI dependencies
    # For now, we'll use a placeholder that will be replaced by proper injection
    return None


@streaming_router.get("/status")
async def get_streaming_status():
    """Get current status of data streaming"""
    try:
        # Get Noesis component (in real app this would be dependency injection)
        from noesis.api.app import get_component_instance
        noesis = await get_component_instance()
        
        if not noesis:
            raise HTTPException(status_code=503, detail="Noesis component not available")
        
        status = await noesis.get_stream_status()
        return status
        
    except Exception as e:
        logger.error(f"Error getting streaming status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@streaming_router.post("/start")
async def start_streaming(background_tasks: BackgroundTasks):
    """Start Engram data streaming"""
    try:
        from noesis.api.app import get_component_instance
        noesis = await get_component_instance()
        
        if not noesis:
            raise HTTPException(status_code=503, detail="Noesis component not available")
        
        success = await noesis.start_streaming()
        if success:
            return {"status": "started", "message": "Engram data streaming started"}
        else:
            raise HTTPException(status_code=500, detail="Failed to start streaming")
            
    except Exception as e:
        logger.error(f"Error starting streaming: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@streaming_router.post("/stop")
async def stop_streaming():
    """Stop Engram data streaming"""
    try:
        from noesis.api.app import get_component_instance
        noesis = await get_component_instance()
        
        if not noesis:
            raise HTTPException(status_code=503, detail="Noesis component not available")
        
        success = await noesis.stop_streaming()
        if success:
            return {"status": "stopped", "message": "Engram data streaming stopped"}
        else:
            raise HTTPException(status_code=500, detail="Failed to stop streaming")
            
    except Exception as e:
        logger.error(f"Error stopping streaming: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@streaming_router.get("/insights")
async def get_theoretical_insights():
    """Get current theoretical insights from streaming analysis"""
    try:
        from noesis.api.app import get_component_instance
        noesis = await get_component_instance()
        
        if not noesis:
            raise HTTPException(status_code=503, detail="Noesis component not available")
        
        insights = await noesis.get_theoretical_insights()
        return insights
        
    except Exception as e:
        logger.error(f"Error getting theoretical insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@streaming_router.get("/memory/analysis")
async def get_memory_analysis():
    """Get latest memory analysis results from Engram streaming"""
    try:
        from noesis.api.app import get_component_instance
        noesis = await get_component_instance()
        
        if not noesis:
            raise HTTPException(status_code=503, detail="Noesis component not available")
        
        analysis = await noesis.get_memory_analysis()
        return analysis
        
    except Exception as e:
        logger.error(f"Error getting memory analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@streaming_router.get("/memory/history")
async def get_memory_history(limit: int = 50):
    """Get historical memory analysis results"""
    try:
        from noesis.api.app import get_component_instance
        noesis = await get_component_instance()
        
        if not noesis:
            raise HTTPException(status_code=503, detail="Noesis component not available")
        
        if not noesis.stream_manager:
            raise HTTPException(status_code=503, detail="Stream manager not available")
        
        history = noesis.stream_manager.get_analysis_history(limit=limit)
        return {"history": history, "count": len(history)}
        
    except Exception as e:
        logger.error(f"Error getting memory history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@streaming_router.get("/memory/current")
async def get_current_memory_state():
    """Get current memory state from Engram"""
    try:
        from noesis.api.app import get_component_instance
        noesis = await get_component_instance()
        
        if not noesis:
            raise HTTPException(status_code=503, detail="Noesis component not available")
        
        if not noesis.stream_manager or not noesis.stream_manager.engram_streamer:
            raise HTTPException(status_code=503, detail="Engram streamer not available")
        
        current_state = noesis.stream_manager.engram_streamer.get_current_state()
        if current_state:
            return current_state.to_dict()
        else:
            return {"message": "No current memory state available"}
        
    except Exception as e:
        logger.error(f"Error getting current memory state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@streaming_router.post("/memory/force-poll")
async def force_memory_poll():
    """Force an immediate poll of Engram memory state"""
    try:
        from noesis.api.app import get_component_instance
        noesis = await get_component_instance()
        
        if not noesis:
            raise HTTPException(status_code=503, detail="Noesis component not available")
        
        if not noesis.stream_manager or not noesis.stream_manager.engram_streamer:
            raise HTTPException(status_code=503, detail="Engram streamer not available")
        
        state = await noesis.stream_manager.engram_streamer.force_poll()
        if state:
            return {
                "status": "success",
                "message": "Memory state polled successfully",
                "state": state.to_dict()
            }
        else:
            return {
                "status": "warning", 
                "message": "No memory state retrieved from poll"
            }
        
    except Exception as e:
        logger.error(f"Error forcing memory poll: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@streaming_router.post("/analysis/update")
async def force_analysis_update():
    """Force an immediate update of analysis results"""
    try:
        from noesis.api.app import get_component_instance
        noesis = await get_component_instance()
        
        if not noesis:
            raise HTTPException(status_code=503, detail="Noesis component not available")
        
        if not noesis.stream_manager:
            raise HTTPException(status_code=503, detail="Stream manager not available")
        
        await noesis.stream_manager.force_analysis_update()
        return {"status": "success", "message": "Analysis results updated"}
        
    except Exception as e:
        logger.error(f"Error forcing analysis update: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@streaming_router.get("/statistics")
async def get_streaming_statistics():
    """Get statistics about streaming activity"""
    try:
        from noesis.api.app import get_component_instance
        noesis = await get_component_instance()
        
        if not noesis:
            raise HTTPException(status_code=503, detail="Noesis component not available")
        
        if not noesis.stream_manager:
            raise HTTPException(status_code=503, detail="Stream manager not available")
        
        stats = {}
        
        # Get stream status
        stream_status = noesis.stream_manager.get_stream_status()
        stats["stream_status"] = stream_status
        
        # Get memory analyzer statistics
        if noesis.stream_manager.memory_analyzer:
            memory_stats = noesis.stream_manager.memory_analyzer.get_memory_statistics()
            stats["memory_statistics"] = memory_stats
        
        # Get Engram streamer statistics
        if noesis.stream_manager.engram_streamer:
            streamer = noesis.stream_manager.engram_streamer
            stats["engram_statistics"] = {
                "is_streaming": streamer.is_streaming,
                "poll_interval": streamer.poll_interval,
                "listeners_count": len(streamer.listeners),
                "history_size": len(streamer.memory_history),
                "known_thoughts": len(streamer.known_thoughts),
                "last_poll": streamer.last_poll_time.isoformat() if streamer.last_poll_time else None
            }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting streaming statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@streaming_router.get("/health")
async def streaming_health_check():
    """Health check for streaming subsystem"""
    try:
        from noesis.api.app import get_component_instance
        noesis = await get_component_instance()
        
        health = {
            "status": "healthy",
            "timestamp": None,
            "components": {}
        }
        
        if not noesis:
            health["status"] = "unhealthy"
            health["components"]["noesis"] = "unavailable"
            return health
        
        health["components"]["noesis"] = "healthy"
        
        # Check stream manager
        if noesis.stream_manager:
            health["components"]["stream_manager"] = "healthy"
            
            # Check Engram streamer
            if noesis.stream_manager.engram_streamer:
                health["components"]["engram_streamer"] = (
                    "streaming" if noesis.stream_manager.engram_streamer.is_streaming 
                    else "ready"
                )
            else:
                health["components"]["engram_streamer"] = "unavailable"
            
            # Check memory analyzer
            if noesis.stream_manager.memory_analyzer:
                health["components"]["memory_analyzer"] = "healthy"
            else:
                health["components"]["memory_analyzer"] = "unavailable"
                
        else:
            health["components"]["stream_manager"] = "unavailable"
            health["status"] = "degraded"
        
        # Check theoretical framework
        if noesis.theoretical_framework:
            health["components"]["theoretical_framework"] = "healthy"
        else:
            health["components"]["theoretical_framework"] = "unavailable"
            if health["status"] == "healthy":
                health["status"] = "degraded"
        
        import datetime
        health["timestamp"] = datetime.datetime.now().isoformat()
        
        return health
        
    except Exception as e:
        logger.error(f"Error in streaming health check: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": None
        }