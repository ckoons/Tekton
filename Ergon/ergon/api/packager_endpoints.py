"""
API endpoints for Solution Packager

Provides REST API and SSE endpoints for the packager UI.
"""

from fastapi import APIRouter, HTTPException, Request, Form, Body
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Dict, Any, Optional
import json
import asyncio
import logging
from datetime import datetime
import uuid

from ..construct.solution_packager import get_packager

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/ergon/packager", tags=["packager"])

# Store sessions
sessions = {}


@router.post("/analyze")
async def analyze_repository(
    github_url: str = Form(...),
    session_id: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """
    Analyze a GitHub repository.

    Returns analysis and recommendations.
    """
    try:
        # Create session if needed
        if not session_id:
            session_id = str(uuid.uuid4())

        packager = get_packager()

        # Analyze repository
        result = await packager.analyze_repository(github_url, session_id)

        # Store in session
        sessions[session_id] = {
            'github_url': github_url,
            'analysis': result['analysis'],
            'recommendations': result['recommendations'],
            'repo_path': result['repo_path']
        }

        return {
            'success': True,
            'session_id': session_id,
            'analysis': result['analysis'],
            'recommendations': result['recommendations']
        }

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plan")
async def create_plan(config: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """
    Create execution plan based on configuration.
    """
    try:
        session_id = config.get('session_id')
        if not session_id or session_id not in sessions:
            raise ValueError("Invalid session")

        packager = get_packager()

        # Create plan
        plan = await packager.create_plan(config, session_id)

        # Store plan in session
        sessions[session_id]['plan'] = plan
        sessions[session_id]['config'] = config

        return {
            'success': True,
            'plan': plan
        }

    except Exception as e:
        logger.error(f"Plan creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream/{session_id}")
async def stream_events(session_id: str):
    """
    Server-Sent Events endpoint for real-time updates.
    """
    async def event_generator():
        """Generate SSE events."""
        try:
            # Send initial connection event
            yield f"event: connected\ndata: {json.dumps({'session_id': session_id})}\n\n"

            # Keep connection alive and send updates
            while True:
                # Check if session has updates
                if session_id in sessions:
                    session = sessions[session_id]

                    # Send any pending events
                    if 'events' in session:
                        while session['events']:
                            event = session['events'].pop(0)
                            yield f"event: {event['type']}\ndata: {json.dumps(event['data'])}\n\n"

                # Wait before checking again
                await asyncio.sleep(0.5)

        except asyncio.CancelledError:
            logger.info(f"SSE connection closed for session {session_id}")
            raise

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/build")
async def build_solution(request: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """
    Execute the build plan.
    """
    try:
        session_id = request.get('session_id')
        if not session_id or session_id not in sessions:
            raise ValueError("Invalid session")

        session = sessions[session_id]
        plan = session.get('plan')
        if not plan:
            raise ValueError("No plan found")

        packager = get_packager()

        # Initialize events list for SSE
        if 'events' not in session:
            session['events'] = []

        # Send build started event
        session['events'].append({
            'type': 'build_started',
            'data': {'total_steps': len(plan['steps'])}
        })

        # Execute plan with progress updates
        for i, step in enumerate(plan['steps']):
            # Send progress event
            session['events'].append({
                'type': 'build_progress',
                'data': {
                    'step': i + 1,
                    'total': len(plan['steps']),
                    'description': step['description']
                }
            })

            # Small delay to show progress
            await asyncio.sleep(0.5)

        # Execute the actual plan
        results = await packager.execute_plan(plan, session_id)

        # Send completion event
        session['events'].append({
            'type': 'build_complete',
            'data': {
                'success': results['success'],
                'repo_url': plan['output_repo']
            }
        })

        return {
            'success': results['success'],
            'results': results,
            'output_repo': plan['output_repo']
        }

    except Exception as e:
        logger.error(f"Build failed: {e}")

        # Send error event if session exists
        if session_id in sessions and 'events' in sessions[session_id]:
            sessions[session_id]['events'].append({
                'type': 'build_error',
                'data': {'error': str(e)}
            })

        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apply-recommendations")
async def apply_recommendations(request: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """
    Apply CI recommendations to configuration.
    """
    try:
        session_id = request.get('session_id')
        if not session_id or session_id not in sessions:
            raise ValueError("Invalid session")

        recommendations = sessions[session_id].get('recommendations', [])

        # Convert recommendations to config updates
        updates = {
            'standards': [],
            'config_values': {}
        }

        for rec in recommendations:
            if rec.get('auto_apply'):
                updates['standards'].append(rec['standard_id'])

        return {
            'success': True,
            'updates': updates
        }

    except Exception as e:
        logger.error(f"Apply recommendations failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/standards")
async def get_standards() -> Dict[str, Any]:
    """
    Get available programming standards.
    """
    from ..construct.solution_packager import StandardsEngine

    return {
        'standards': StandardsEngine.STANDARDS
    }


@router.get("/session/{session_id}")
async def get_session(session_id: str) -> Dict[str, Any]:
    """
    Get session state.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    return {
        'github_url': session.get('github_url'),
        'has_analysis': 'analysis' in session,
        'has_plan': 'plan' in session,
        'recommendations_count': len(session.get('recommendations', []))
    }