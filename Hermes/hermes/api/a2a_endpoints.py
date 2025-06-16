"""
A2A JSON-RPC Endpoints - Agent-to-Agent Protocol v0.2.1 Implementation

This module provides the JSON-RPC 2.0 endpoint for A2A communication,
compliant with the A2A Protocol v0.2.1 specification.
"""

import os
import sys
import logging
import json
from typing import Dict, Any, Optional, Union, List
from datetime import datetime

from fastapi import APIRouter, Request, HTTPException, Depends, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import JSONResponse, StreamingResponse
from tekton.models import TektonBaseModel

# Add Tekton root to path for shared imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.utils.env_config import get_component_config

# Import A2A protocol from tekton
from tekton.a2a import (
    JSONRPCRequest, JSONRPCResponse, JSONRPCBatch,
    parse_jsonrpc_message, create_error_response,
    AgentCard, AgentRegistry, AgentStatus,
    TaskManager, TaskState,
    DiscoveryService,
    MethodDispatcher, create_standard_dispatcher,
    ParseError, InvalidRequestError,
    create_sse_response, SSEManager,
    Subscription, SubscriptionManager,
    websocket_manager, handle_websocket
)

logger = logging.getLogger(__name__)

# Create router
a2a_router = APIRouter(
    prefix="/a2a/v1",
    tags=["a2a"],
    responses={404: {"description": "Not found"}}
)

# Pydantic models for request/response
class JSONRPCRequestModel(TektonBaseModel):
    """JSON-RPC 2.0 Request model"""
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Union[Dict[str, Any], List[Any]]] = None
    id: Optional[Union[str, int]] = None


class JSONRPCResponseModel(TektonBaseModel):
    """JSON-RPC 2.0 Response model"""
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[Union[str, int]] = None


async def get_a2a_service(request: Request):
    """Get A2A service from request state"""
    if not hasattr(request.app.state, "a2a_service"):
        raise HTTPException(status_code=500, detail="A2A service not initialized")
    
    return request.app.state.a2a_service


async def get_a2a_components(request: Request) -> Dict[str, Any]:
    """Get A2A components from the A2A service"""
    a2a_service = await get_a2a_service(request)
    
    return {
        "agent_registry": a2a_service.get_agent_registry(),
        "task_manager": a2a_service.get_task_manager(),
        "discovery_service": a2a_service.get_discovery_service(),
        "method_dispatcher": a2a_service.get_dispatcher(),
        "sse_manager": a2a_service.get_sse_manager(),
        "subscription_manager": a2a_service.get_subscription_manager()
    }




# Main JSON-RPC endpoint
@a2a_router.post("/")
async def handle_jsonrpc(
    request: Request,
    components: Dict[str, Any] = Depends(get_a2a_components)
) -> Union[JSONRPCResponseModel, List[JSONRPCResponseModel]]:
    """
    Main JSON-RPC 2.0 endpoint for A2A communication.
    
    Handles single requests and batch requests according to JSON-RPC 2.0 spec.
    """
    try:
        # Get request body
        body = await request.json()
        
        # Parse the JSON-RPC message
        parsed = parse_jsonrpc_message(body)
        
        # Get dispatcher
        dispatcher = components["method_dispatcher"]
        
        # Extract headers for security middleware
        headers = dict(request.headers)
        
        # Handle batch requests
        if isinstance(parsed, JSONRPCBatch):
            responses = []
            for req in parsed.messages:
                if isinstance(req, JSONRPCRequest):
                    # Try to pass headers if the dispatcher supports it (security enabled)
                    try:
                        response = await dispatcher.dispatch(req, headers=headers)
                    except TypeError:
                        # Fall back to original signature if headers not supported
                        response = await dispatcher.dispatch(req)
                    # Only include response if request had an ID (not a notification)
                    if req.id is not None:
                        responses.append(response.to_dict())
            
            # Return empty array if all were notifications
            return responses if responses else []
        
        # Handle single request
        elif isinstance(parsed, JSONRPCRequest):
            # Try to pass headers if the dispatcher supports it (security enabled)
            try:
                response = await dispatcher.dispatch(parsed, headers=headers)
            except TypeError:
                # Fall back to original signature if headers not supported
                response = await dispatcher.dispatch(parsed)
            
            # Don't return response for notifications (no ID)
            if parsed.id is None:
                return JSONResponse(content="", status_code=204)
            
            return response.to_dict()
        
        else:
            # Should not happen if parse_jsonrpc_message works correctly
            error_response = create_error_response(
                None,
                InvalidRequestError().code,
                "Invalid request"
            )
            return error_response.to_dict()
    
    except ParseError as e:
        error_response = create_error_response(None, e.code, e.message, e.data)
        return error_response.to_dict()
    
    except InvalidRequestError as e:
        error_response = create_error_response(None, e.code, e.message, e.data)
        return error_response.to_dict()
    
    except Exception as e:
        logger.error(f"Unexpected error in JSON-RPC handler: {e}", exc_info=True)
        error_response = create_error_response(
            None,
            -32603,  # Internal error
            "Internal server error",
            str(e)
        )
        return error_response.to_dict()


# Well-known agent card endpoint
def _get_hermes_port() -> int:
    """Get Hermes port from configuration."""
    config = get_component_config()
    try:
        return config.hermes.port
    except (AttributeError, TypeError):
        return int(os.environ.get('HERMES_PORT'))


@a2a_router.get("/.well-known/agent.json")
async def get_agent_card(request: Request) -> Dict[str, Any]:
    """
    Return Hermes's agent card at the well-known URI.
    
    This endpoint provides information about Hermes's A2A capabilities.
    """
    # Get Hermes's capabilities from app state
    capabilities = []
    if hasattr(request.app.state, "service_registry"):
        capabilities.append("service_discovery")
    if hasattr(request.app.state, "message_bus"):
        capabilities.append("message_routing")
    if hasattr(request.app.state, "registration_manager"):
        capabilities.append("agent_registration")
    
    # Create Hermes's agent card
    agent_card = AgentCard.create(
        name="Hermes",
        description="Central hub for Tekton Agent-to-Agent communication",
        version="0.1.0",
        capabilities=capabilities,
        supported_methods=[
            # Standard A2A methods
            "agent.register",
            "agent.unregister",
            "agent.heartbeat",
            "agent.update_status",
            "agent.get",
            "agent.list",
            "discovery.query",
            "discovery.find_for_method",
            "discovery.find_for_capability",
            "discovery.capability_map",
            "discovery.method_map",
            "task.create",
            "task.assign",
            "task.update_state",
            "task.update_progress",
            "task.complete",
            "task.fail",
            "task.cancel",
            "task.get",
            "task.list",
            # Hermes-specific methods
            "agent.forward",
            "channel.subscribe",
            "channel.unsubscribe",
            "channel.publish"
        ],
        endpoint=f"http://localhost:{_get_hermes_port()}/api/a2a/v1/",
        tags=["infrastructure", "messaging", "discovery"],
        metadata={
            "protocol_version": "0.2.1",
            "tekton_component": "hermes"
        }
    )
    
    return agent_card.model_dump()


# Legacy compatibility endpoints (will forward to JSON-RPC)
@a2a_router.post("/register")
async def legacy_register_agent(
    request: Request,
    agent_data: Dict[str, Any],
    components: Dict[str, Any] = Depends(get_a2a_components)
) -> Dict[str, Any]:
    """
    Legacy agent registration endpoint for backwards compatibility.
    
    Forwards to the JSON-RPC method internally.
    """
    # Create JSON-RPC request
    rpc_request = JSONRPCRequest(
        method="agent.register",
        params={"agent_card": agent_data},
        id="legacy-register"
    )
    
    # Dispatch through the method dispatcher
    dispatcher = components["method_dispatcher"]
    # Try to dispatch with security context if available, otherwise use original signature
    try:
        headers = dict(request.headers)
        response = await dispatcher.dispatch(rpc_request, headers=headers)
    except TypeError:
        response = await dispatcher.dispatch(rpc_request)
    
    if response.error:
        raise HTTPException(status_code=400, detail=response.error["message"])
    
    return response.result


@a2a_router.get("/agents")
async def legacy_list_agents(
    request: Request,
    components: Dict[str, Any] = Depends(get_a2a_components)
) -> List[Dict[str, Any]]:
    """
    Legacy agent listing endpoint for backwards compatibility.
    
    Forwards to the JSON-RPC method internally.
    """
    # Create JSON-RPC request
    rpc_request = JSONRPCRequest(
        method="agent.list",
        params={},
        id="legacy-list"
    )
    
    # Dispatch through the method dispatcher
    dispatcher = components["method_dispatcher"]
    # Try to dispatch with security context if available, otherwise use original signature
    try:
        headers = dict(request.headers)
        response = await dispatcher.dispatch(rpc_request, headers=headers)
    except TypeError:
        response = await dispatcher.dispatch(rpc_request)
    
    if response.error:
        raise HTTPException(status_code=400, detail=response.error["message"])
    
    return response.result


# Import os for environment variables
import os

# =========================
# SSE Streaming Endpoints
# =========================

@a2a_router.get("/stream/events")
async def stream_events(
    request: Request,
    task_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    channel: Optional[str] = None,
    event_types: Optional[str] = None
):
    """
    Server-Sent Events endpoint for real-time event streaming.
    
    Query parameters:
    - task_id: Filter events for a specific task
    - agent_id: Filter events for a specific agent
    - channel: Filter events for a specific channel
    - event_types: Comma-separated list of event types to filter
    """
    # Get A2A components
    components = await get_a2a_components(request)
    sse_manager: SSEManager = components["sse_manager"]
    
    # Build filters
    filters = {}
    if task_id:
        filters["task_id"] = task_id
    if agent_id:
        filters["agent_id"] = agent_id
    if channel:
        filters["channel"] = channel
    if event_types:
        filters["event_types"] = event_types.split(",")
    
    # Create SSE response
    return create_sse_response(sse_manager, filters)


@a2a_router.post("/subscriptions")
async def create_subscription(
    request: Request,
    subscription_data: Dict[str, Any]
):
    """
    Create a subscription for events.
    
    Example request body:
    {
        "subscriber_id": "agent-123",
        "subscription_type": "task",
        "target": "task-456",
        "event_types": ["task.state_changed", "task.progress"]
    }
    """
    components = await get_a2a_components(request)
    subscription_manager: SubscriptionManager = components["subscription_manager"]
    
    try:
        # Create subscription based on type
        sub_type = subscription_data.get("subscription_type")
        subscriber_id = subscription_data.get("subscriber_id")
        target = subscription_data.get("target")
        
        if not subscriber_id or not sub_type:
            raise ValueError("subscriber_id and subscription_type are required")
        
        if sub_type == "task":
            subscription = Subscription.create_task_subscription(
                subscriber_id=subscriber_id,
                task_id=target,
                event_types=subscription_data.get("event_types")
            )
        elif sub_type == "agent":
            subscription = Subscription.create_agent_subscription(
                subscriber_id=subscriber_id,
                agent_id=target,
                event_types=subscription_data.get("event_types")
            )
        elif sub_type == "channel":
            subscription = Subscription.create_channel_subscription(
                subscriber_id=subscriber_id,
                channel=target,
                filters=subscription_data.get("filters")
            )
        else:
            raise ValueError(f"Unknown subscription type: {sub_type}")
        
        # Add subscription
        sub_id = await subscription_manager.add_subscription(subscription)
        
        return {
            "subscription_id": sub_id,
            "subscription": subscription.model_dump()
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@a2a_router.delete("/subscriptions/{subscription_id}")
async def remove_subscription(
    request: Request,
    subscription_id: str
):
    """Remove a subscription"""
    components = await get_a2a_components(request)
    subscription_manager: SubscriptionManager = components["subscription_manager"]
    
    removed = await subscription_manager.remove_subscription(subscription_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return {"success": True, "subscription_id": subscription_id}


@a2a_router.get("/subscriptions/{subscriber_id}")
async def get_subscriber_subscriptions(
    request: Request,
    subscriber_id: str
):
    """Get all subscriptions for a subscriber"""
    components = await get_a2a_components(request)
    subscription_manager: SubscriptionManager = components["subscription_manager"]
    
    subscriptions = await subscription_manager.get_subscriber_subscriptions(subscriber_id)
    
    return {
        "subscriber_id": subscriber_id,
        "subscriptions": [sub.model_dump() for sub in subscriptions]
    }


@a2a_router.get("/stream/connections")
async def get_active_connections(request: Request):
    """Get information about active SSE connections"""
    components = await get_a2a_components(request)
    sse_manager: SSEManager = components["sse_manager"]
    
    connections = await sse_manager.get_active_connections()
    
    return {
        "total_connections": len(connections),
        "connections": connections
    }


@a2a_router.websocket("/stream/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    agent_id: Optional[str] = Query(None),
    task_id: Optional[str] = Query(None),
    event_types: Optional[str] = Query(None),
    channel: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for bidirectional A2A streaming
    
    Query parameters:
    - agent_id: Filter events for specific agent
    - task_id: Filter events for specific task
    - event_types: Comma-separated list of event types to receive
    - channel: Subscribe to specific channel (for pub/sub)
    
    The WebSocket accepts JSON-RPC 2.0 messages and supports:
    - Bidirectional JSON-RPC requests/responses
    - Event streaming via notifications
    - Channel-based pub/sub messaging
    """
    # Parse filters
    filters = {}
    if agent_id:
        filters['agent_id'] = agent_id
    if task_id:
        filters['task_id'] = task_id
    if event_types:
        filters['event_types'] = event_types.split(',')
    if channel:
        filters['channel'] = channel
    
    # Get A2A components directly from websocket app
    app = websocket.scope.get("app")
    # Create a mock request object with app reference
    class MockRequest:
        def __init__(self, app):
            self.app = app
    
    request = MockRequest(app)
    components = await get_a2a_components(request)
    dispatcher = components["method_dispatcher"]
    
    # Define handlers for incoming messages
    async def on_request(connection, request: JSONRPCRequest):
        """Handle incoming JSON-RPC requests"""
        try:
            # Create a dispatch request with proper format
            dispatch_request = JSONRPCRequest(
                method=request.method,
                params=request.params,
                id=request.id
            )
            # Dispatch the request through standard dispatcher
            response = await dispatcher.dispatch(dispatch_request)
            # Extract the result or error from the response
            if hasattr(response, 'error') and response.error:
                raise Exception(response.error.get('message', 'Unknown error'))
            return response.result
        except Exception as e:
            logger.error(f"Error handling WebSocket request: {e}")
            raise
    
    async def on_notification(connection, notification):
        """Handle incoming JSON-RPC notifications"""
        logger.info(f"Received notification: {notification.method}")
        # Notifications don't require a response
        # Could be used for client-side events, heartbeats, etc.
    
    # Handle the WebSocket connection
    await handle_websocket(
        websocket=websocket,
        agent_id=agent_id,
        filters=filters,
        on_request=on_request,
        on_notification=on_notification
    )