"""
API Routes for Apollo.

This module implements the HTTP routes for the Apollo API.
"""

import os
import json
import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union

from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from apollo.api.models import (
    APIResponse,
    ResponseStatus,
    MonitoringStatus,
    MonitoringMetrics,
    SessionInfo,
    BudgetRequest,
    BudgetResponse,
    ProtocolRule,
    DirectiveMessage,
    ComponentMessage,
    PredictionRequest
)
from apollo.models.context import (
    ContextState,
    ContextHealth,
    ContextAction
)
from apollo.models.protocol import (
    ProtocolDefinition,
    ProtocolViolation,
    ProtocolType,
    ProtocolSeverity,
    ProtocolScope,
    EnforcementMode
)
from apollo.models.message import (
    TektonMessage,
    MessageType,
    MessagePriority
)

# Configure logging
logger = logging.getLogger("apollo.api.routes")

# Create API router
api_router = APIRouter()  # Remove prefix here - it's added when mounting

# Create WebSocket router
ws_router = APIRouter()

# Create metrics router
metrics_router = APIRouter()  # Remove prefix here too - it's added when mounting


# Import the Apollo manager dependency
from apollo.api.dependencies import get_apollo_manager


# Context Management Routes

@api_router.get("/contexts", response_model=APIResponse)
async def get_all_contexts(
    apollo_manager = Depends(get_apollo_manager),
    status: Optional[str] = Query(None, description="Filter contexts by health status")
):
    """
    Get all active contexts.
    
    Returns information about all contexts currently being monitored by Apollo.
    Optionally filter by health status.
    """
    try:
        # Get all contexts
        contexts = apollo_manager.get_all_context_states()
        
        # Filter by status if provided
        if status:
            try:
                # Convert string to enum
                health_status = ContextHealth(status.lower())
                contexts = [c for c in contexts if c.health == health_status]
            except ValueError:
                return APIResponse(
                    status=ResponseStatus.ERROR,
                    message=f"Invalid health status: {status}",
                    errors=[f"Valid status values: {', '.join([s.value for s in ContextHealth])}"]
                )
        
        # Convert to dict for response
        context_data = [context.model_dump() for context in contexts]
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Found {len(context_data)} contexts",
            data=context_data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving contexts: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message="Error retrieving contexts",
            errors=[str(e)]
        )


@api_router.get("/contexts/{context_id}", response_model=APIResponse)
async def get_context(
    context_id: str = Path(..., description="Context identifier"),
    apollo_manager = Depends(get_apollo_manager),
    include_history: bool = Query(False, description="Include context history"),
    history_limit: int = Query(10, description="Limit history records")
):
    """
    Get details for a specific context.
    
    Returns detailed information about a specific context identified by ID.
    Optionally includes context history.
    """
    try:
        # Get context
        context = apollo_manager.get_context_state(context_id)
        
        if not context:
            return APIResponse(
                status=ResponseStatus.ERROR,
                message=f"Context {context_id} not found",
                errors=[f"No context found with ID {context_id}"]
            )
        
        # Convert to dict
        context_data = context.model_dump()
        
        # Include history if requested
        if include_history:
            history = apollo_manager.get_context_history(context_id, limit=history_limit)
            context_data["history"] = [h.model_dump() for h in history]
        
        # Include prediction if available
        prediction = apollo_manager.get_prediction(context_id)
        if prediction:
            context_data["prediction"] = prediction.model_dump()
            
        # Include actions if available
        actions = apollo_manager.get_actions(context_id)
        if actions:
            context_data["actions"] = [a.model_dump() for a in actions]
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Context {context_id} found",
            data=context_data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving context {context_id}: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message=f"Error retrieving context {context_id}",
            errors=[str(e)]
        )


@api_router.get("/contexts/{context_id}/dashboard", response_model=APIResponse)
async def get_context_dashboard(
    context_id: str = Path(..., description="Context identifier"),
    apollo_manager = Depends(get_apollo_manager)
):
    """
    Get dashboard data for a specific context.
    
    Returns comprehensive dashboard data for a specific context,
    including metrics, predictions, and actions.
    """
    try:
        # Get dashboard data
        dashboard = apollo_manager.get_context_dashboard(context_id)
        
        if "error" in dashboard:
            return APIResponse(
                status=ResponseStatus.ERROR,
                message=dashboard["error"],
                errors=[dashboard["error"]]
            )
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Dashboard for context {context_id}",
            data=dashboard
        )
        
    except Exception as e:
        logger.error(f"Error retrieving dashboard for context {context_id}: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message=f"Error retrieving dashboard for context {context_id}",
            errors=[str(e)]
        )


# Prediction Routes

@api_router.get("/predictions", response_model=APIResponse)
async def get_all_predictions(
    apollo_manager = Depends(get_apollo_manager),
    health: Optional[str] = Query(None, description="Filter predictions by health status")
):
    """
    Get all predictions.
    
    Returns all context predictions currently maintained by Apollo.
    Optionally filter by predicted health status.
    """
    try:
        # Get all predictions
        if health:
            try:
                # Convert string to enum
                health_status = ContextHealth(health.lower())
                predictions = apollo_manager.get_predictions_by_health(health_status)
            except ValueError:
                return APIResponse(
                    status=ResponseStatus.ERROR,
                    message=f"Invalid health status: {health}",
                    errors=[f"Valid status values: {', '.join([s.value for s in ContextHealth])}"]
                )
        else:
            predictions = list(apollo_manager.get_all_predictions().values())
        
        # Convert to dict for response
        prediction_data = [prediction.model_dump() for prediction in predictions]
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Found {len(prediction_data)} predictions",
            data=prediction_data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving predictions: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message="Error retrieving predictions",
            errors=[str(e)]
        )


@api_router.get("/predictions/{context_id}", response_model=APIResponse)
async def get_prediction(
    context_id: str = Path(..., description="Context identifier"),
    apollo_manager = Depends(get_apollo_manager)
):
    """
    Get prediction for a specific context.
    
    Returns the latest prediction for a specific context identified by ID.
    """
    try:
        # Get prediction
        prediction = apollo_manager.get_prediction(context_id)
        
        if not prediction:
            return APIResponse(
                status=ResponseStatus.ERROR,
                message=f"No prediction found for context {context_id}",
                errors=[f"No prediction found for context {context_id}"]
            )
        
        # Convert to dict
        prediction_data = prediction.model_dump()
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Prediction found for context {context_id}",
            data=prediction_data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving prediction for context {context_id}: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message=f"Error retrieving prediction for context {context_id}",
            errors=[str(e)]
        )


@api_router.post("/predictions/request", response_model=APIResponse)
async def request_prediction(
    request: PredictionRequest,
    apollo_manager = Depends(get_apollo_manager)
):
    """
    Request a new prediction for a context.
    
    Creates a new prediction based on provided metrics and context info.
    """
    # This would typically trigger the prediction engine to create a new prediction
    # For now, we'll just return a message since prediction creation is automatic
    return APIResponse(
        status=ResponseStatus.SUCCESS,
        message=f"Prediction request received for context {request.context_id}",
        data={"message": "Predictions are created automatically by Apollo. Check back soon for updated predictions."}
    )


# Action Routes

@api_router.get("/actions", response_model=APIResponse)
async def get_all_actions(
    apollo_manager = Depends(get_apollo_manager),
    critical_only: bool = Query(False, description="Only return critical actions"),
    actionable_now: bool = Query(False, description="Only return actions that should be taken now")
):
    """
    Get all actions.
    
    Returns all actions currently recommended by Apollo.
    Optionally filter by critical priority or actionable now.
    """
    try:
        # Get actions based on filters
        if critical_only:
            actions = apollo_manager.get_critical_actions()
        elif actionable_now:
            actions = apollo_manager.get_actionable_now()
        else:
            # Get all actions for all contexts
            actions = []
            for context_actions in apollo_manager.get_all_actions().values():
                actions.extend(context_actions)
        
        # Convert to dict for response
        action_data = [action.model_dump() for action in actions]
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Found {len(action_data)} actions",
            data=action_data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving actions: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message="Error retrieving actions",
            errors=[str(e)]
        )


@api_router.get("/actions/{context_id}", response_model=APIResponse)
async def get_actions_for_context(
    context_id: str = Path(..., description="Context identifier"),
    apollo_manager = Depends(get_apollo_manager),
    highest_priority_only: bool = Query(False, description="Only return highest priority action")
):
    """
    Get actions for a specific context.
    
    Returns actions recommended for a specific context identified by ID.
    Optionally returns only the highest priority action.
    """
    try:
        # Get actions
        if highest_priority_only:
            action = apollo_manager.get_highest_priority_action(context_id)
            if not action:
                return APIResponse(
                    status=ResponseStatus.SUCCESS,
                    message=f"No actions found for context {context_id}",
                    data=[]
                )
            actions = [action]
        else:
            actions = apollo_manager.get_actions(context_id)
        
        # Convert to dict for response
        action_data = [action.model_dump() for action in actions]
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Found {len(action_data)} actions for context {context_id}",
            data=action_data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving actions for context {context_id}: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message=f"Error retrieving actions for context {context_id}",
            errors=[str(e)]
        )


@api_router.post("/actions/{action_id}/applied", response_model=APIResponse)
async def mark_action_applied(
    action_id: str = Path(..., description="Action identifier"),
    apollo_manager = Depends(get_apollo_manager)
):
    """
    Mark an action as applied.
    
    Notifies Apollo that an action has been applied by a component.
    """
    try:
        # Mark action as applied
        await apollo_manager.mark_action_applied(action_id)
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Action {action_id} marked as applied"
        )
        
    except Exception as e:
        logger.error(f"Error marking action {action_id} as applied: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message=f"Error marking action {action_id} as applied",
            errors=[str(e)]
        )


# Budget Routes

@api_router.post("/budget/allocate", response_model=APIResponse)
async def allocate_budget(
    request: BudgetRequest,
    apollo_manager = Depends(get_apollo_manager)
):
    """
    Allocate a token budget.
    
    Requests a token budget allocation for an operation.
    """
    try:
        # Get token budget manager from Apollo manager
        if not hasattr(apollo_manager, "token_budget_manager"):
            return APIResponse(
                status=ResponseStatus.ERROR,
                message="Token budget manager not initialized",
                errors=["Token budget management is not available"]
            )
            
        # Allocate budget
        budget = await apollo_manager.token_budget_manager.allocate_budget(
            context_id=request.context_id,
            task_type=request.task_type,
            component=request.component,
            provider=request.provider,
            model=request.model,
            priority=request.priority,
            requested_tokens=request.token_count
        )
        
        # Convert to response model
        response = BudgetResponse(
            context_id=request.context_id,
            allocated_tokens=budget.allocated_tokens,
            expiration=budget.expiration,
            policy=budget.policy.model_dump() if hasattr(budget.policy, "dict") else budget.policy
        )
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Budget allocated for context {request.context_id}",
            data=response
        )
        
    except Exception as e:
        logger.error(f"Error allocating budget: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message="Error allocating budget",
            errors=[str(e)]
        )


# Protocol Routes

@api_router.get("/protocols", response_model=APIResponse)
async def get_all_protocols(
    apollo_manager = Depends(get_apollo_manager),
    type: Optional[str] = Query(None, description="Filter protocols by type"),
    scope: Optional[str] = Query(None, description="Filter protocols by scope")
):
    """
    Get all protocol definitions.
    
    Returns all protocol definitions currently managed by Apollo.
    Optionally filter by type or scope.
    """
    try:
        # Get protocol enforcer from Apollo manager
        if not hasattr(apollo_manager, "protocol_enforcer"):
            return APIResponse(
                status=ResponseStatus.ERROR,
                message="Protocol enforcer not initialized",
                errors=["Protocol enforcement is not available"]
            )
            
        # Get all protocols
        protocols = apollo_manager.protocol_enforcer.get_all_protocols()
        
        # Filter by type if provided
        if type:
            try:
                # Convert string to enum
                protocol_type = ProtocolType(type.lower())
                protocols = [p for p in protocols if p.type == protocol_type]
            except ValueError:
                return APIResponse(
                    status=ResponseStatus.ERROR,
                    message=f"Invalid protocol type: {type}",
                    errors=[f"Valid type values: {', '.join([t.value for t in ProtocolType])}"]
                )
                
        # Filter by scope if provided
        if scope:
            try:
                # Convert string to enum
                protocol_scope = ProtocolScope(scope.lower())
                protocols = [p for p in protocols if p.scope == protocol_scope]
            except ValueError:
                return APIResponse(
                    status=ResponseStatus.ERROR,
                    message=f"Invalid protocol scope: {scope}",
                    errors=[f"Valid scope values: {', '.join([s.value for s in ProtocolScope])}"]
                )
        
        # Convert to dict for response
        protocol_data = [protocol.model_dump() for protocol in protocols]
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Found {len(protocol_data)} protocols",
            data=protocol_data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving protocols: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message="Error retrieving protocols",
            errors=[str(e)]
        )


@api_router.get("/protocols/{protocol_id}", response_model=APIResponse)
async def get_protocol(
    protocol_id: str = Path(..., description="Protocol identifier"),
    apollo_manager = Depends(get_apollo_manager)
):
    """
    Get a specific protocol definition.
    
    Returns a specific protocol definition identified by ID.
    """
    try:
        # Get protocol enforcer from Apollo manager
        if not hasattr(apollo_manager, "protocol_enforcer"):
            return APIResponse(
                status=ResponseStatus.ERROR,
                message="Protocol enforcer not initialized",
                errors=["Protocol enforcement is not available"]
            )
            
        # Get protocol
        protocol = apollo_manager.protocol_enforcer.get_protocol(protocol_id)
        
        if not protocol:
            return APIResponse(
                status=ResponseStatus.ERROR,
                message=f"Protocol {protocol_id} not found",
                errors=[f"No protocol found with ID {protocol_id}"]
            )
        
        # Get stats
        stats = apollo_manager.protocol_enforcer.get_protocol_stats(protocol_id)
        
        # Combine data
        protocol_data = protocol.model_dump()
        if stats:
            protocol_data["stats"] = stats.model_dump()
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Protocol {protocol_id} found",
            data=protocol_data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving protocol {protocol_id}: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message=f"Error retrieving protocol {protocol_id}",
            errors=[str(e)]
        )


@api_router.post("/protocols", response_model=APIResponse)
async def create_protocol(
    protocol: ProtocolDefinition,
    apollo_manager = Depends(get_apollo_manager)
):
    """
    Create a new protocol definition.
    
    Adds a new protocol to be enforced by Apollo.
    """
    try:
        # Get protocol enforcer from Apollo manager
        if not hasattr(apollo_manager, "protocol_enforcer"):
            return APIResponse(
                status=ResponseStatus.ERROR,
                message="Protocol enforcer not initialized",
                errors=["Protocol enforcement is not available"]
            )
            
        # Add protocol
        success = apollo_manager.protocol_enforcer.add_protocol(protocol)
        
        if not success:
            return APIResponse(
                status=ResponseStatus.ERROR,
                message="Failed to add protocol",
                errors=["Protocol could not be added"]
            )
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Protocol {protocol.protocol_id} created",
            data=protocol.model_dump()
        )
        
    except Exception as e:
        logger.error(f"Error creating protocol: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message="Error creating protocol",
            errors=[str(e)]
        )


@api_router.put("/protocols/{protocol_id}", response_model=APIResponse)
async def update_protocol(
    protocol_id: str = Path(..., description="Protocol identifier"),
    protocol: ProtocolDefinition = Body(...),
    apollo_manager = Depends(get_apollo_manager)
):
    """
    Update a protocol definition.
    
    Updates an existing protocol definition.
    """
    try:
        # Get protocol enforcer from Apollo manager
        if not hasattr(apollo_manager, "protocol_enforcer"):
            return APIResponse(
                status=ResponseStatus.ERROR,
                message="Protocol enforcer not initialized",
                errors=["Protocol enforcement is not available"]
            )
            
        # Ensure protocol ID matches
        if protocol_id != protocol.protocol_id:
            return APIResponse(
                status=ResponseStatus.ERROR,
                message="Protocol ID mismatch",
                errors=["Protocol ID in path does not match protocol ID in body"]
            )
            
        # Update protocol
        success = apollo_manager.protocol_enforcer.update_protocol(protocol)
        
        if not success:
            return APIResponse(
                status=ResponseStatus.ERROR,
                message=f"Protocol {protocol_id} not found",
                errors=[f"No protocol found with ID {protocol_id}"]
            )
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Protocol {protocol_id} updated",
            data=protocol.model_dump()
        )
        
    except Exception as e:
        logger.error(f"Error updating protocol {protocol_id}: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message=f"Error updating protocol {protocol_id}",
            errors=[str(e)]
        )


@api_router.delete("/protocols/{protocol_id}", response_model=APIResponse)
async def delete_protocol(
    protocol_id: str = Path(..., description="Protocol identifier"),
    apollo_manager = Depends(get_apollo_manager)
):
    """
    Delete a protocol definition.
    
    Removes a protocol from enforcement.
    """
    try:
        # Get protocol enforcer from Apollo manager
        if not hasattr(apollo_manager, "protocol_enforcer"):
            return APIResponse(
                status=ResponseStatus.ERROR,
                message="Protocol enforcer not initialized",
                errors=["Protocol enforcement is not available"]
            )
            
        # Remove protocol
        success = apollo_manager.protocol_enforcer.remove_protocol(protocol_id)
        
        if not success:
            return APIResponse(
                status=ResponseStatus.ERROR,
                message=f"Protocol {protocol_id} not found",
                errors=[f"No protocol found with ID {protocol_id}"]
            )
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Protocol {protocol_id} deleted"
        )
        
    except Exception as e:
        logger.error(f"Error deleting protocol {protocol_id}: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message=f"Error deleting protocol {protocol_id}",
            errors=[str(e)]
        )


@api_router.get("/protocols/violations", response_model=APIResponse)
async def get_protocol_violations(
    apollo_manager = Depends(get_apollo_manager),
    component: Optional[str] = Query(None, description="Filter by component"),
    protocol_id: Optional[str] = Query(None, description="Filter by protocol ID"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(100, description="Maximum number of violations to return")
):
    """
    Get protocol violations.
    
    Returns protocol violations recorded by Apollo.
    Optionally filter by component, protocol ID, or severity.
    """
    try:
        # Get protocol enforcer from Apollo manager
        if not hasattr(apollo_manager, "protocol_enforcer"):
            return APIResponse(
                status=ResponseStatus.ERROR,
                message="Protocol enforcer not initialized",
                errors=["Protocol enforcement is not available"]
            )
            
        # Convert severity to enum if provided
        severity_enum = None
        if severity:
            try:
                severity_enum = ProtocolSeverity(severity.lower())
            except ValueError:
                return APIResponse(
                    status=ResponseStatus.ERROR,
                    message=f"Invalid severity: {severity}",
                    errors=[f"Valid severity values: {', '.join([s.value for s in ProtocolSeverity])}"]
                )
        
        # Get violations
        violations = apollo_manager.protocol_enforcer.get_violations(
            component=component,
            protocol_id=protocol_id,
            severity=severity_enum,
            limit=limit
        )
        
        # Convert to dict for response
        violation_data = [violation.model_dump() for violation in violations]
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Found {len(violation_data)} violations",
            data=violation_data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving protocol violations: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message="Error retrieving protocol violations",
            errors=[str(e)]
        )


# Message Routes

@api_router.post("/message")
async def handle_message(
    request: dict,
    apollo_manager = Depends(get_apollo_manager)
):
    """
    Handle simple message requests (for aish compatibility).
    
    Accepts JSON with 'message' field and returns response.
    """
    try:
        message = request.get("message", "")
        if not message:
            return {"error": "No message provided"}
        
        # Process the message through Apollo's AI specialist
        # For now, return a simple response indicating Apollo received it
        response = f"Apollo received: {message}"
        
        return {"response": response}
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        return {"error": str(e)}

@api_router.post("/messages", response_model=APIResponse)
async def send_message(
    message: TektonMessage,
    apollo_manager = Depends(get_apollo_manager)
):
    """
    Send a message from Apollo.
    
    Sends a message to other components via the message handler.
    """
    try:
        # Get message handler from Apollo manager
        if not hasattr(apollo_manager, "message_handler"):
            return APIResponse(
                status=ResponseStatus.ERROR,
                message="Message handler not initialized",
                errors=["Message handling is not available"]
            )
            
        # Send message
        success = await apollo_manager.message_handler.send_message(message)
        
        if not success:
            return APIResponse(
                status=ResponseStatus.ERROR,
                message="Failed to send message",
                errors=["Message could not be queued for sending"]
            )
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Message {message.message_id} sent",
            data={"message_id": message.message_id}
        )
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message="Error sending message",
            errors=[str(e)]
        )


@api_router.post("/messages/subscription", response_model=APIResponse)
async def create_subscription(
    message_types: List[str] = Body(..., description="Message types to subscribe to"),
    filter_expression: Optional[str] = Body(None, description="Filter expression"),
    callback_url: Optional[str] = Body(None, description="Callback URL for messages"),
    apollo_manager = Depends(get_apollo_manager)
):
    """
    Create a message subscription.
    
    Subscribes to messages of specific types.
    """
    try:
        # Get message handler from Apollo manager
        if not hasattr(apollo_manager, "message_handler"):
            return APIResponse(
                status=ResponseStatus.ERROR,
                message="Message handler not initialized",
                errors=["Message handling is not available"]
            )
            
        # Convert message types to enum
        try:
            message_type_enums = [MessageType(mt) for mt in message_types]
        except ValueError as e:
            return APIResponse(
                status=ResponseStatus.ERROR,
                message=f"Invalid message type: {str(e)}",
                errors=[f"Valid message types: {', '.join([mt.value for mt in MessageType])}"]
            )
            
        # Create subscription
        subscription_id = await apollo_manager.message_handler.subscribe_remote(
            message_types=message_type_enums,
            callback_url=callback_url,
            filter_expression=filter_expression
        )
        
        if not subscription_id:
            return APIResponse(
                status=ResponseStatus.ERROR,
                message="Failed to create subscription",
                errors=["Subscription could not be created"]
            )
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Subscription {subscription_id} created",
            data={"subscription_id": subscription_id}
        )
        
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message="Error creating subscription",
            errors=[str(e)]
        )


@api_router.delete("/messages/subscription/{subscription_id}", response_model=APIResponse)
async def delete_subscription(
    subscription_id: str = Path(..., description="Subscription identifier"),
    apollo_manager = Depends(get_apollo_manager)
):
    """
    Delete a message subscription.
    
    Unsubscribes from messages.
    """
    try:
        # Get message handler from Apollo manager
        if not hasattr(apollo_manager, "message_handler"):
            return APIResponse(
                status=ResponseStatus.ERROR,
                message="Message handler not initialized",
                errors=["Message handling is not available"]
            )
            
        # Delete subscription
        success = await apollo_manager.message_handler.unsubscribe_remote(subscription_id)
        
        if not success:
            return APIResponse(
                status=ResponseStatus.ERROR,
                message=f"Subscription {subscription_id} not found",
                errors=[f"No subscription found with ID {subscription_id}"]
            )
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Subscription {subscription_id} deleted"
        )
        
    except Exception as e:
        logger.error(f"Error deleting subscription {subscription_id}: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message=f"Error deleting subscription {subscription_id}",
            errors=[str(e)]
        )


# System Status Routes

@api_router.get("/status", response_model=APIResponse)
async def get_system_status(
    apollo_manager = Depends(get_apollo_manager)
):
    """
    Get Apollo system status.
    
    Returns comprehensive status information about Apollo components.
    """
    try:
        # Get system status
        status = apollo_manager.get_system_status()
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message="Apollo system status",
            data=status
        )
        
    except Exception as e:
        logger.error(f"Error retrieving system status: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message="Error retrieving system status",
            errors=[str(e)]
        )


# WebSocket Routes

@ws_router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = None
):
    """
    WebSocket endpoint for real-time communication.
    
    Provides real-time updates for context monitoring, actions, and predictions.
    """
    # TODO: Implement authentication if needed
    # if token != "your_secret_token":
    #     await websocket.close(code=1008, reason="Invalid token")
    #     return
    
    # Accept the connection
    await websocket.accept()
    
    try:
        # Send initial message
        await websocket.send_json({
            "type": "connection_established",
            "message": "Connected to Apollo WebSocket",
            "timestamp": datetime.now().isoformat()
        })
        
        # Get Apollo manager from app state
        request = websocket.scope.get("request", None)
        if not request or not hasattr(request.app.state, "apollo_manager"):
            await websocket.send_json({
                "type": "error",
                "message": "Apollo manager not initialized",
                "timestamp": datetime.now().isoformat()
            })
            await websocket.close(code=1011, reason="Apollo manager not initialized")
            return
            
        apollo_manager = request.app.state.apollo_manager
        
        # Subscribe to WebSocket updates
        # This would typically involve registering callbacks with various components
        # For now, we'll just keep the connection open
        
        # Keep connection alive and handle messages
        while True:
            # Wait for message from client
            data = await websocket.receive_text()
            
            try:
                # Parse message
                message = json.loads(data)
                
                # Handle message based on type
                message_type = message.get("type")
                
                if message_type == "ping":
                    # Send pong response
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                elif message_type == "subscribe":
                    # TODO: Handle subscription request
                    await websocket.send_json({
                        "type": "subscription_ack",
                        "subscription_id": str(uuid.uuid4()),
                        "timestamp": datetime.now().isoformat()
                    })
                elif message_type == "command":
                    # TODO: Handle command
                    await websocket.send_json({
                        "type": "command_result",
                        "command_id": message.get("command_id"),
                        "success": True,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    # Unknown message type
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except json.JSONDecodeError:
                # Invalid JSON
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON message",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                # Generic error
                await websocket.send_json({
                    "type": "error",
                    "message": f"Error processing message: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })
                
    except WebSocketDisconnect:
        # Client disconnected
        logger.info("WebSocket client disconnected")
    except Exception as e:
        # Generic error
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"WebSocket error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
        except:
            pass
            
        try:
            await websocket.close(code=1011, reason="Server error")
        except:
            pass


# Metrics Routes

@metrics_router.get("/health", response_model=APIResponse)
async def get_health_metrics(
    apollo_manager = Depends(get_apollo_manager)
):
    """
    Get context health metrics.
    
    Returns metrics on context health distribution.
    """
    try:
        # Get health distribution
        distribution = apollo_manager.get_health_distribution()
        
        # Convert enum keys to strings
        health_distribution = {str(k): v for k, v in distribution.items()}
        
        # Calculate total
        total = sum(distribution.values())
        
        # Calculate percentages
        percentages = {}
        for health, count in distribution.items():
            if total > 0:
                percentages[str(health)] = round((count / total) * 100, 2)
            else:
                percentages[str(health)] = 0
        
        # Create response data
        data = {
            "health_distribution": health_distribution,
            "health_percentages": percentages,
            "total_contexts": total,
            "critical_contexts": distribution.get(ContextHealth.CRITICAL, 0),
            "timestamp": datetime.now().isoformat()
        }
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message="Context health metrics",
            data=data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving health metrics: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message="Error retrieving health metrics",
            errors=[str(e)]
        )


@metrics_router.get("/predictions", response_model=APIResponse)
async def get_prediction_metrics(
    apollo_manager = Depends(get_apollo_manager)
):
    """
    Get prediction metrics.
    
    Returns metrics on prediction accuracy and distribution.
    """
    try:
        # Get prediction engine from Apollo manager
        if not hasattr(apollo_manager, "predictive_engine"):
            return APIResponse(
                status=ResponseStatus.ERROR,
                message="Predictive engine not initialized",
                errors=["Predictive capabilities are not available"]
            )
            
        # Get prediction accuracy
        accuracy = apollo_manager.predictive_engine.get_prediction_accuracy()
        
        # Get critical predictions count
        critical_predictions = len(apollo_manager.predictive_engine.get_critical_predictions())
        
        # Get all predictions
        all_predictions = apollo_manager.predictive_engine.get_all_predictions()
        
        # Count predictions by health
        health_distribution = {str(h): 0 for h in ContextHealth}
        for prediction in all_predictions.values():
            health_distribution[str(prediction.predicted_health)] += 1
        
        # Create response data
        data = {
            "prediction_accuracy": accuracy,
            "critical_predictions": critical_predictions,
            "total_predictions": len(all_predictions),
            "health_distribution": health_distribution,
            "timestamp": datetime.now().isoformat()
        }
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message="Prediction metrics",
            data=data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving prediction metrics: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message="Error retrieving prediction metrics",
            errors=[str(e)]
        )


@metrics_router.get("/actions", response_model=APIResponse)
async def get_action_metrics(
    apollo_manager = Depends(get_apollo_manager)
):
    """
    Get action metrics.
    
    Returns metrics on recommended actions.
    """
    try:
        # Get action planner from Apollo manager
        if not hasattr(apollo_manager, "action_planner"):
            return APIResponse(
                status=ResponseStatus.ERROR,
                message="Action planner not initialized",
                errors=["Action planning is not available"]
            )
            
        # Get all actions
        all_actions = []
        for context_actions in apollo_manager.action_planner.get_all_actions().values():
            all_actions.extend(context_actions)
            
        # Count actions by type
        type_distribution = {}
        for action in all_actions:
            action_type = action.action_type
            if action_type not in type_distribution:
                type_distribution[action_type] = 0
            type_distribution[action_type] += 1
            
        # Count actions by priority
        priority_distribution = {}
        for action in all_actions:
            priority = action.priority
            if priority not in priority_distribution:
                priority_distribution[priority] = 0
            priority_distribution[priority] += 1
            
        # Get action stats
        action_stats = apollo_manager.action_planner.get_action_stats()
        
        # Create response data
        data = {
            "total_actions": len(all_actions),
            "critical_actions": len(apollo_manager.action_planner.get_critical_actions()),
            "actionable_now": len(apollo_manager.action_planner.get_actionable_now()),
            "type_distribution": type_distribution,
            "priority_distribution": priority_distribution,
            "action_stats": action_stats,
            "timestamp": datetime.now().isoformat()
        }
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message="Action metrics",
            data=data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving action metrics: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message="Error retrieving action metrics",
            errors=[str(e)]
        )


@metrics_router.get("/protocols", response_model=APIResponse)
async def get_protocol_metrics(
    apollo_manager = Depends(get_apollo_manager)
):
    """
    Get protocol metrics.
    
    Returns metrics on protocol enforcement.
    """
    try:
        # Get protocol enforcer from Apollo manager
        if not hasattr(apollo_manager, "protocol_enforcer"):
            return APIResponse(
                status=ResponseStatus.ERROR,
                message="Protocol enforcer not initialized",
                errors=["Protocol enforcement is not available"]
            )
            
        # Get all stats
        all_stats = apollo_manager.protocol_enforcer.get_all_stats()
        
        # Calculate total evaluations and violations
        total_evaluations = sum(stats.total_evaluations for stats in all_stats.values())
        total_violations = sum(stats.total_violations for stats in all_stats.values())
        
        # Get violation summary
        violation_summary = apollo_manager.protocol_enforcer.get_violation_summary()
        
        # Create response data
        data = {
            "total_protocols": len(all_stats),
            "total_evaluations": total_evaluations,
            "total_violations": total_violations,
            "violation_rate": round((total_violations / total_evaluations) * 100, 2) if total_evaluations > 0 else 0,
            "violation_summary": violation_summary,
            "timestamp": datetime.now().isoformat()
        }
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message="Protocol metrics",
            data=data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving protocol metrics: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message="Error retrieving protocol metrics",
            errors=[str(e)]
        )


@metrics_router.get("/messages", response_model=APIResponse)
async def get_message_metrics(
    apollo_manager = Depends(get_apollo_manager)
):
    """
    Get message metrics.
    
    Returns metrics on message handling.
    """
    try:
        # Get message handler from Apollo manager
        if not hasattr(apollo_manager, "message_handler"):
            return APIResponse(
                status=ResponseStatus.ERROR,
                message="Message handler not initialized",
                errors=["Message handling is not available"]
            )
            
        # Get queue stats
        queue_stats = apollo_manager.message_handler.get_queue_stats()
        
        # Get delivery stats
        delivery_stats = apollo_manager.message_handler.get_delivery_stats()
        
        # Create response data
        data = {
            "queue_stats": queue_stats,
            "delivery_stats": delivery_stats,
            "timestamp": datetime.now().isoformat()
        }
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message="Message metrics",
            data=data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving message metrics: {e}")
        return APIResponse(
            status=ResponseStatus.ERROR,
            message="Error retrieving message metrics",
            errors=[str(e)]
        )