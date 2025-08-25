"""
Unified CI Specialist HTTP endpoints for Rhetor.

This replaces the old internal specialist system with registry-based discovery.
Rhetor acts as the hiring manager for platform AIs.
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel, Field
import logging
import asyncio
import os
import sys

# Add Tekton root to path
script_path = os.path.realpath(__file__)
tekton_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_path))))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

from shared.ai.simple_ai import ai_send, ai_send_sync
from shared.ai.ai_discovery_service import AIDiscoveryService

logger = logging.getLogger(__name__)

# Pydantic models for requests/responses
class SpecialistResponse(BaseModel):
    """AI Specialist information from registry"""
    id: str
    name: str
    type: str  # role
    component_id: str
    active: bool
    status: str
    model: str
    capabilities: List[str]
    roles: List[str]
    connection: Dict[str, Any]
    performance: Optional[Dict[str, Any]] = None

class SpecialistListResponse(BaseModel):
    """List of CI specialists"""
    count: int
    specialists: List[SpecialistResponse]

class HireRequest(BaseModel):
    """Request to hire an CI specialist"""
    ai_id: str
    role: str
    reason: Optional[str] = None

class FireRequest(BaseModel):
    """Request to fire an CI specialist"""
    ai_id: str
    reason: Optional[str] = None

class CreateRoleRequest(BaseModel):
    """Request to create a new role"""
    role_name: str
    description: str
    required_capabilities: List[str]

# Create router
router = APIRouter(prefix="/api/ai", tags=["AI Specialists"])

# Initialize services
# Registry removed - using simple_ai
discovery = AIDiscoveryService()

# Rhetor's hired CI roster (runtime state)
# In production, this would be stored in rhetor_component
hired_roster: Dict[str, Dict[str, Any]] = {}

def get_rhetor_roster():
    """Get Rhetor's current CI roster"""
    from ..api.app import component
    
    # Check if component has roster, if not initialize
    if not hasattr(component, 'ai_roster'):
        component.ai_roster = {}
    
    return component.ai_roster

@router.get("/specialists", response_model=SpecialistListResponse)
async def list_specialists(
    active_only: bool = Query(False, description="Only show hired specialists"),
    role_filter: Optional[str] = Query(None, description="Filter by role")
):
    """List CI specialists - shows Rhetor's current roster from the registry"""
    try:
        # Get all available AIs from registry
        all_ais = await discovery.list_ais(role=role_filter)
        roster = get_rhetor_roster()
        
        specialists = []
        for ai in all_ais['ais']:
            # Convert to expected format
            specialist = SpecialistResponse(
                id=ai['id'],
                name=ai['name'],
                type=ai['roles'][0] if ai['roles'] else 'general',
                component_id=ai['component'],
                active=ai['id'] in roster,  # Active = hired by Rhetor
                status=ai['status'],
                model=ai.get('model', 'unknown'),
                capabilities=ai.get('capabilities', []),
                roles=ai.get('roles', []),
                connection=ai.get('connection', {}),
                performance=ai.get('performance')
            )
            
            # Filter if requested
            if not active_only or specialist.active:
                specialists.append(specialist)
        
        return SpecialistListResponse(
            count=len(specialists),
            specialists=specialists
        )
        
    except Exception as e:
        logger.error(f"Failed to list specialists: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/specialists/{ai_id}/hire")
async def hire_specialist(
    ai_id: str = Path(..., description="AI specialist ID"),
    request: HireRequest = ...
):
    """Hire an CI specialist - Rhetor adds them to the active roster"""
    try:
        roster = get_rhetor_roster()
        
        # Check if already hired
        if ai_id in roster:
            return {"status": "already_hired", "ai_id": ai_id}
        
        # Verify CI exists and is healthy
        ai_info = await discovery.get_ai_info(ai_id)
        if ai_info.get('status') != 'healthy':
            raise HTTPException(status_code=400, detail=f"AI {ai_id} is not healthy")
        
        # Add to roster
        roster[ai_id] = {
            'role': request.role,
            'hired_at': asyncio.get_event_loop().time(),
            'reason': request.reason,
            'performance': {'requests': 0, 'failures': 0}
        }
        
        # Mark registry for config sync
        registry.mark_config_update_needed()
        
        logger.info(f"Hired CI specialist: {ai_id} for role: {request.role}")
        return {"status": "hired", "ai_id": ai_id, "role": request.role}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to hire specialist {ai_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/specialists/{ai_id}/fire")
async def fire_specialist(
    ai_id: str = Path(..., description="AI specialist ID"),
    request: FireRequest = ...
):
    """Fire an CI specialist - Rhetor removes them from the active roster"""
    try:
        roster = get_rhetor_roster()
        
        # Check if hired
        if ai_id not in roster:
            return {"status": "not_hired", "ai_id": ai_id}
        
        # Remove from roster
        fired_info = roster.pop(ai_id)
        
        # Mark registry for config sync
        registry.mark_config_update_needed()
        
        logger.info(f"Fired CI specialist: {ai_id} (reason: {request.reason})")
        return {"status": "fired", "ai_id": ai_id, "previous_role": fired_info['role']}
        
    except Exception as e:
        logger.error(f"Failed to fire specialist {ai_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/roster")
async def get_roster():
    """Get Rhetor's current hired CI roster"""
    roster = get_rhetor_roster()
    
    # Enrich with current info
    enriched_roster = {}
    for ai_id, hire_info in roster.items():
        try:
            ai_info = await discovery.get_ai_info(ai_id)
            enriched_roster[ai_id] = {
                **hire_info,
                'name': ai_info.get('name'),
                'status': ai_info.get('status'),
                'model': ai_info.get('model'),
                'connection': ai_info.get('connection')
            }
        except Exception as e:
            logger.warning(f"Could not get info for hired CI {ai_id}: {e}")
            enriched_roster[ai_id] = {**hire_info, 'status': 'unknown'}
    
    return {
        'roster_size': len(roster),
        'hired_ais': enriched_roster
    }

@router.post("/roles")
async def create_role(request: CreateRoleRequest):
    """Create a new role that Rhetor can hire for"""
    # In a full implementation, this would update role mappings
    # For now, we'll just acknowledge
    logger.info(f"Created new role: {request.role_name}")
    
    return {
        'status': 'created',
        'role': request.role_name,
        'description': request.description,
        'capabilities': request.required_capabilities
    }

@router.get("/candidates/{role}")
async def find_candidates(
    role: str = Path(..., description="Role to find candidates for")
):
    """Find CI candidates for a specific role"""
    try:
        candidates = await discovery.list_ais(role=role)
        roster = get_rhetor_roster()
        
        # Mark which ones are already hired
        for ai in candidates['ais']:
            ai['hired'] = ai['id'] in roster
        
        return {
            'role': role,
            'candidate_count': len(candidates['ais']),
            'candidates': candidates['ais']
        }
        
    except Exception as e:
        logger.error(f"Failed to find candidates for role {role}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/specialists/{ai_id}/reassign")
async def reassign_specialist(
    ai_id: str = Path(..., description="AI specialist ID"),
    new_role: str = Query(..., description="New role to assign")
):
    """Reassign a hired CI to a new role"""
    try:
        roster = get_rhetor_roster()
        
        if ai_id not in roster:
            raise HTTPException(status_code=404, detail=f"AI {ai_id} not in roster")
        
        old_role = roster[ai_id]['role']
        roster[ai_id]['role'] = new_role
        roster[ai_id]['reassigned_at'] = asyncio.get_event_loop().time()
        
        # Mark registry for config sync
        registry.mark_config_update_needed()
        
        logger.info(f"Reassigned {ai_id} from {old_role} to {new_role}")
        return {
            'status': 'reassigned',
            'ai_id': ai_id,
            'old_role': old_role,
            'new_role': new_role
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reassign specialist {ai_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Backward compatibility endpoint that maps to new system
@router.post("/specialists/{specialist_id}/activate")
async def activate_specialist_compat(specialist_id: str):
    """Backward compatibility - maps to hire"""
    # Map old specialist IDs to new CI IDs
    mapping = {
        'rhetor-orchestrator': 'rhetor-ci',
        'apollo-coordinator': 'apollo-ci',
        'hermes-messenger': 'hermes-ci',
        'engram-memory': 'engram-ci',
        'prometheus-strategist': 'prometheus-ci'
    }
    
    ai_id = mapping.get(specialist_id, specialist_id)
    
    # Try to hire with appropriate role
    role = 'general'
    if 'rhetor' in ai_id:
        role = 'orchestration'
    elif 'apollo' in ai_id:
        role = 'code-analysis'
    elif 'hermes' in ai_id:
        role = 'messaging'
    elif 'engram' in ai_id:
        role = 'memory'
    elif 'prometheus' in ai_id:
        role = 'planning'
    
    request = HireRequest(ai_id=ai_id, role=role, reason="Legacy activation")
    return await hire_specialist(ai_id, request)
