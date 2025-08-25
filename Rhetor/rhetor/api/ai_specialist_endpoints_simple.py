"""
Simplified CI Specialist HTTP endpoints for Rhetor.

Uses the simple CI manager that reads from component_config (ports from environment).
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel, Field
import logging

from rhetor.core.ai_manager import CIManager

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/ai", tags=["ai-specialists"])

# Global CI manager instance
ai_manager = CIManager()


# Pydantic models
class CISpecialist(BaseModel):
    """CI Specialist information"""
    ai_id: str
    component: str
    name: str
    port: int
    host: str
    description: str
    category: str
    capabilities: List[str]
    healthy: Optional[bool] = None
    in_roster: bool = False


class RosterEntry(BaseModel):
    """Roster entry for a hired AI"""
    ai_id: str
    component: str
    role: str
    hired_at: str
    performance: Dict[str, Any]


class MessageRequest(BaseModel):
    """Request to send a message to an AI"""
    message: str
    timeout: float = Field(default=30.0, description="Timeout in seconds")


class MessageResponse(BaseModel):
    """Response from CI message"""
    success: bool
    ai_id: str
    response: Optional[str] = None
    error: Optional[str] = None


@router.get("/specialists", response_model=List[CISpecialist])
async def list_specialists(
    include_health: bool = Query(True, description="Include health status"),
    in_roster_only: bool = Query(False, description="Only show hired specialists"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """List all available CI specialists."""
    try:
        all_ais = await ai_manager.list_available_ais(include_health=include_health)
        
        # Apply filters
        filtered = []
        for ai in all_ais:
            # Roster filter
            if in_roster_only and not ai['in_roster']:
                continue
            
            # Category filter
            if category and ai['category'] != category:
                continue
                
            filtered.append(CISpecialist(**ai))
        
        return filtered
        
    except Exception as e:
        logger.error(f"Failed to list specialists: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/roster", response_model=List[RosterEntry])
async def get_roster():
    """Get Rhetor's current CI roster."""
    roster = ai_manager.get_roster()
    return [RosterEntry(**entry) for entry in roster.values()]


@router.post("/specialists/{ai_id}/hire", response_model=RosterEntry)
async def hire_specialist(
    ai_id: str = Path(..., description="AI specialist ID"),
    role: Optional[str] = Query(None, description="Role assignment")
):
    """Hire an CI specialist to Rhetor's roster."""
    try:
        # Check if CI exists and is healthy
        component_id = ai_id.replace('-ci', '')
        ai_info = ai_manager.get_ai_info(component_id)
        
        if not await ai_manager.check_ai_health(ai_id):
            raise HTTPException(
                status_code=503,
                detail=f"AI specialist {ai_id} is not healthy"
            )
        
        roster_entry = ai_manager.hire_ai(ai_id, role)
        return RosterEntry(**roster_entry)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to hire specialist {ai_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/specialists/{ai_id}/fire")
async def fire_specialist(ai_id: str = Path(..., description="AI specialist ID")):
    """Remove an CI specialist from Rhetor's roster."""
    if ai_manager.fire_ai(ai_id):
        return {"message": f"Successfully fired {ai_id}"}
    else:
        raise HTTPException(
            status_code=404,
            detail=f"AI specialist {ai_id} not in roster"
        )


@router.post("/specialists/{ai_id}/message", response_model=MessageResponse)
async def send_message(
    ai_id: str = Path(..., description="AI specialist ID"),
    request: MessageRequest = ...
):
    """Send a message to an CI specialist."""
    try:
        result = await ai_manager.send_to_ai(ai_id, request.message)
        return MessageResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to send message to {ai_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/specialists/{ai_id}/health")
async def check_health(ai_id: str = Path(..., description="AI specialist ID")):
    """Check health status of a specific CI specialist."""
    try:
        healthy = await ai_manager.check_ai_health(ai_id)
        return {
            "ai_id": ai_id,
            "healthy": healthy,
            "status": "available" if healthy else "unavailable"
        }
        
    except Exception as e:
        logger.error(f"Failed to check health of {ai_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/find/{role}")
async def find_ai_for_role(role: str = Path(..., description="Role/category needed")):
    """Find a healthy CI that can fulfill a specific role."""
    ai_id = await ai_manager.find_ai_for_role(role)
    
    if ai_id:
        component_id = ai_id.replace('-ci', '')
        ai_info = ai_manager.get_ai_info(component_id)
        return {
            "found": True,
            "ai_id": ai_id,
            "component": component_id,
            "name": ai_info['name'],
            "port": ai_info['port']
        }
    else:
        return {
            "found": False,
            "message": f"No healthy CI found for role: {role}"
        }


@router.post("/roster/clear")
async def clear_roster():
    """Clear Rhetor's entire CI roster."""
    roster = ai_manager.get_roster()
    count = len(roster)
    
    for ai_id in list(roster.keys()):
        ai_manager.fire_ai(ai_id)
    
    return {"message": f"Cleared {count} AIs from roster"}


@router.post("/cache/clear")
async def clear_cache():
    """Clear the CI health check cache."""
    ai_manager.clear_health_cache()
    return {"message": "Health cache cleared"}
