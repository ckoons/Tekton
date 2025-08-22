"""
API endpoints for sandbox operations.

Provides REST interface for testing Registry solutions in isolated
environments with real-time output streaming.
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import asyncio
import json
import logging

from ..sandbox.runner import SandboxRunner
from ..registry.storage import RegistryStorage

# Landmark imports with fallback
try:
    from landmarks import api_contract, integration_point
except ImportError:
    def api_contract(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func):
            return func
        return decorator

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/ergon/sandbox", tags=["sandbox"])

# Global runner instance
_runner = None

def get_runner() -> SandboxRunner:
    """Get or create sandbox runner instance"""
    global _runner
    if _runner is None:
        _runner = SandboxRunner(RegistryStorage())
    return _runner


# Request/Response models
class TestRequest(BaseModel):
    """Request to test a solution"""
    solution_id: str
    provider: Optional[str] = None
    timeout: Optional[int] = 300
    memory_limit: Optional[str] = "4g"
    cpu_limit: Optional[int] = 4
    environment: Optional[Dict[str, str]] = None


class ExecuteRequest(BaseModel):
    """Request to execute command in sandbox"""
    sandbox_id: str
    command: Optional[List[str]] = None


class SandboxInfo(BaseModel):
    """Sandbox information"""
    sandbox_id: str
    solution_id: str
    status: str
    provider: str
    started: str


# API Endpoints

@router.post("/test")
@api_contract(
    endpoint="/api/ergon/sandbox/test",
    title="Test Solution",
    description="Start testing a Registry solution in sandbox",
    request_body="TestRequest",
    response_body={"sandbox_id": "str"},
    error_codes={
        404: "Solution not found",
        503: "No sandbox provider available",
        429: "Too many concurrent sandboxes"
    }
)
async def test_solution(request: TestRequest) -> Dict[str, str]:
    """
    Test a Registry solution in an isolated sandbox.
    
    Returns sandbox_id for tracking execution.
    """
    runner = get_runner()
    
    try:
        config = {
            "provider": request.provider,
            "timeout": request.timeout,
            "memory_limit": request.memory_limit,
            "cpu_limit": request.cpu_limit,
            "environment": request.environment or {}
        }
        
        sandbox_id = await runner.test_solution(
            request.solution_id,
            config
        )
        
        return {"sandbox_id": sandbox_id}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        if "Maximum concurrent" in str(e):
            raise HTTPException(status_code=429, detail=str(e))
        else:
            raise HTTPException(status_code=503, detail=str(e))


@router.post("/execute")
async def execute_command(request: ExecuteRequest):
    """
    Execute command in sandbox and stream output.
    
    Returns Server-Sent Events stream of output.
    """
    runner = get_runner()
    
    async def generate():
        try:
            async for line in runner.execute(
                request.sandbox_id,
                request.command
            ):
                # Format as Server-Sent Event
                yield f"data: {json.dumps({'line': line})}\n\n"
        except ValueError as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': f'Execution failed: {e}'})}\n\n"
        finally:
            yield "data: {\"done\": true}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.websocket("/ws/{sandbox_id}")
@integration_point(
    title="WebSocket Execution Stream",
    description="Real-time bidirectional communication for sandbox execution",
    target_component="frontend",
    protocol="websocket",
    systems=["frontend", "sandbox_runner"],
    data_flow="Commands in, output out via WebSocket"
)
async def websocket_endpoint(websocket: WebSocket, sandbox_id: str):
    """
    WebSocket endpoint for real-time sandbox interaction.
    
    Allows sending commands and receiving output in real-time.
    """
    await websocket.accept()
    runner = get_runner()
    
    try:
        while True:
            # Wait for command from client
            data = await websocket.receive_json()
            
            if data.get("action") == "execute":
                command = data.get("command")
                
                # Stream output back
                async for line in runner.execute(sandbox_id, command):
                    await websocket.send_json({
                        "type": "output",
                        "line": line
                    })
                
                await websocket.send_json({
                    "type": "complete"
                })
            
            elif data.get("action") == "stop":
                # Stop sandbox
                break
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for sandbox {sandbox_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        await websocket.close()


@router.get("/results/{sandbox_id}")
async def get_results(sandbox_id: str):
    """
    Get execution results from sandbox.
    
    Returns SandboxResult with status, output, and metrics.
    """
    runner = get_runner()
    
    try:
        result = await runner.get_results(sandbox_id)
        
        return {
            "sandbox_id": result.sandbox_id,
            "solution_id": result.solution_id,
            "status": result.status.value,
            "exit_code": result.exit_code,
            "execution_time": result.execution_time,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "metrics": result.metrics,
            "errors": result.errors
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{sandbox_id}")
async def cleanup_sandbox(sandbox_id: str):
    """
    Clean up sandbox resources.
    
    Returns success status.
    """
    runner = get_runner()
    
    success = await runner.cleanup(sandbox_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Sandbox {sandbox_id} not found")
    
    return {"success": True}


@router.get("/active")
async def list_active_sandboxes() -> List[SandboxInfo]:
    """
    List all active sandboxes.
    
    Returns list of sandbox information.
    """
    runner = get_runner()
    
    sandboxes = []
    for sandbox_id, info in runner.active_sandboxes.items():
        sandboxes.append(SandboxInfo(
            sandbox_id=sandbox_id,
            solution_id=info["solution_id"],
            status=info["status"].value,
            provider=info["provider"].get_name(),
            started=info["started"].isoformat()
        ))
    
    return sandboxes


@router.post("/cleanup-all")
async def cleanup_all_sandboxes():
    """
    Clean up all active sandboxes.
    
    Returns number cleaned.
    """
    runner = get_runner()
    
    cleaned = await runner.cleanup_all()
    
    return {"cleaned": cleaned}


@router.get("/providers")
async def list_providers():
    """
    List available sandbox providers and their status.
    
    Returns provider information.
    """
    runner = get_runner()
    
    providers = await runner.factory.list_providers()
    
    return providers


@router.get("/health")
async def health_check():
    """
    Check sandbox system health.
    
    Returns health status of all providers.
    """
    runner = get_runner()
    
    health = await runner.factory.health_check()
    
    # Overall health
    any_available = any(health.values())
    
    return {
        "status": "healthy" if any_available else "unhealthy",
        "providers": health
    }