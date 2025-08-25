"""
FastMCP endpoints for Rhetor.

This module provides FastAPI endpoints for MCP (Model Context Protocol) integration,
allowing external systems to interact with Rhetor LLM management and prompt engineering capabilities.
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from tekton.models import TektonBaseModel
import asyncio
import time
import json
import inspect

logger = logging.getLogger(__name__)

from tekton.mcp.fastmcp.server import FastMCPServer
from tekton.mcp.fastmcp.utils.endpoints import add_mcp_endpoints
from tekton.mcp.fastmcp.exceptions import FastMCPError

from rhetor.core.mcp.tools import (
    llm_management_tools,
    prompt_engineering_tools,
    context_management_tools,
    ai_orchestration_tools
)
from rhetor.core.mcp.streaming_tools import streaming_tools
from rhetor.core.mcp.capabilities import (
    LLMManagementCapability,
    PromptEngineeringCapability,
    ContextManagementCapability,
    CIOrchestrationCapability
)


class MCPRequest(TektonBaseModel):
    """Request model for MCP tool execution."""
    tool_name: str
    arguments: Dict[str, Any]


class MCPResponse(TektonBaseModel):
    """Response model for MCP tool execution."""
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class MCPStreamRequest(TektonBaseModel):
    """Request model for streaming MCP tool execution."""
    tool_name: str
    arguments: Dict[str, Any]
    stream_options: Optional[Dict[str, Any]] = None  # Options like chunk_size, include_progress


# Create FastMCP server instance
fastmcp_server = FastMCPServer(
    name="rhetor",
    version="0.1.0",
    description="Rhetor LLM Management and Prompt Engineering MCP Server"
)

# Register capabilities and tools
fastmcp_server.register_capability(LLMManagementCapability())
fastmcp_server.register_capability(PromptEngineeringCapability())
fastmcp_server.register_capability(ContextManagementCapability())
fastmcp_server.register_capability(CIOrchestrationCapability())

# Import the actual tool functions to populate tool lists
from rhetor.core.mcp.tools import (
    get_available_models, set_default_model, get_model_capabilities,
    test_model_connection, get_model_performance, manage_model_rotation,
    create_prompt_template, optimize_prompt, validate_prompt_syntax,
    get_prompt_history, analyze_prompt_performance, manage_prompt_library,
    analyze_context_usage, optimize_context_window, track_context_history,
    compress_context, list_ai_specialists, activate_ai_specialist,
    send_message_to_specialist, orchestrate_team_chat,
    get_specialist_conversation_history, configure_ai_orchestration
)

# Import streaming tools
from rhetor.core.mcp.streaming_tools import (
    send_message_to_specialist_stream, orchestrate_team_chat_stream
)

# Import dynamic specialist tools
try:
    from rhetor.core.mcp.dynamic_specialist_tools import (
        list_specialist_templates, create_dynamic_specialist, clone_specialist,
        modify_specialist, deactivate_specialist, get_specialist_metrics
    )
    dynamic_tools_available = True
except ImportError:
    logger.warning("Dynamic specialist tools not available")
    dynamic_tools_available = False

# Register all tools with their metadata and functions
all_tools = [
    # LLM Management tools
    get_available_models, set_default_model, get_model_capabilities,
    test_model_connection, get_model_performance, manage_model_rotation,
    # Prompt Engineering tools
    create_prompt_template, optimize_prompt, validate_prompt_syntax,
    get_prompt_history, analyze_prompt_performance, manage_prompt_library,
    # Context Management tools
    analyze_context_usage, optimize_context_window, track_context_history,
    compress_context,
    # CI Orchestration tools
    list_ai_specialists, activate_ai_specialist, send_message_to_specialist,
    orchestrate_team_chat, get_specialist_conversation_history, configure_ai_orchestration,
    # Streaming-enabled tools
    send_message_to_specialist_stream, orchestrate_team_chat_stream
]

# Add dynamic specialist tools if available
if dynamic_tools_available:
    all_tools.extend([
        list_specialist_templates, create_dynamic_specialist, clone_specialist,
        modify_specialist, deactivate_specialist, get_specialist_metrics
    ])

for tool_func in all_tools:
    if hasattr(tool_func, '_mcp_tool_meta'):
        # Register both the metadata and the function
        fastmcp_server.register_tool(
            tool_func._mcp_tool_meta,
            tool_func
        )

logger.info(f"Registered {len(all_tools)} MCP tools with FastMCP server (including {len(streaming_tools)} streaming tools)")


# Create router for MCP endpoints
mcp_router = APIRouter(prefix="/api/mcp/v2")

# Create wrapper functions for the FastMCPServer
def get_capabilities_func(component_manager=None):
    """Get capabilities from FastMCP server."""
    capabilities = fastmcp_server.get_capabilities()
    # Convert to list of dicts for the endpoint
    return [
        {
            "name": cap.name if hasattr(cap, 'name') else name,
            "description": cap.description if hasattr(cap, 'description') else "Capability",
            "version": cap.version if hasattr(cap, 'version') else "1.0.0"
        }
        for name, cap in capabilities.items()
    ]

def get_tools_func(component_manager=None):
    """Get tools from FastMCP server."""
    tools = []
    
    # Get tools from the FastMCP server
    server_tools = fastmcp_server._tools
    
    for tool_name, tool_meta in server_tools.items():
        # The tool_meta is the MCPTool object registered with the server
        tool_dict = {
            "name": tool_meta.name,
            "description": tool_meta.description,
            "parameters": tool_meta.parameters if hasattr(tool_meta, 'parameters') else {},
            "tags": tool_meta.tags if hasattr(tool_meta, 'tags') else [],
            "category": tool_meta.category if hasattr(tool_meta, 'category') else 'general'
        }
        tools.append(tool_dict)
    
    return tools

async def process_request_func(request_data: Dict[str, Any], component_manager=None):
    """Process MCP request using FastMCP server."""
    tool_name = request_data.get("tool_name")
    arguments = request_data.get("arguments", {})
    
    logger.info(f"Processing MCP request for tool: {tool_name}")
    
    # Get the tool function
    tool_func = fastmcp_server.get_tool_function(tool_name)
    if not tool_func:
        logger.warning(f"Tool {tool_name} not found in FastMCP server")
        return {
            "status": "error",
            "result": None,
            "error": f"Tool {tool_name} not found or has no implementation"
        }
    
    # Execute the tool
    try:
        # Call the function - it might be sync or async
        import inspect
        result = tool_func(**arguments)
        
        # Check if the result is a coroutine
        if inspect.iscoroutine(result):
            result = await result
        
        # Check if result is a dict with coroutines
        if isinstance(result, dict):
            for key, value in result.items():
                if inspect.iscoroutine(value):
                    result[key] = await value
        
        return {
            "status": "success",
            "result": result,
            "error": None
        }
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        return {
            "status": "error",
            "result": None,
            "error": str(e)
        }

# Add standard MCP endpoints using shared utilities with proper callbacks
add_mcp_endpoints(
    mcp_router, 
    get_capabilities_func=get_capabilities_func,
    get_tools_func=get_tools_func,
    process_request_func=process_request_func,
    component_manager_dependency=None  # We don't use component manager in Rhetor
)


# Additional Rhetor-specific MCP endpoints
@mcp_router.get("/llm-status")
async def get_llm_status() -> Dict[str, Any]:
    """
    Get overall LLM system status.
    
    Returns:
        Dictionary containing LLM system status and capabilities
    """
    try:
        # Mock LLM status - real implementation would check actual LLM client
        return {
            "success": True,
            "status": "operational",
            "service": "rhetor-llm-management",
            "capabilities": [
                "llm_management",
                "prompt_engineering", 
                "context_management",
                "ai_orchestration"
            ],
            "available_providers": 4,  # Would query actual providers
            "mcp_tools": len(llm_management_tools + prompt_engineering_tools + context_management_tools + ai_orchestration_tools),
            "llm_engine_status": "ready",
            "message": "Rhetor LLM management system is operational"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get LLM status: {str(e)}")


@mcp_router.post("/execute-llm-workflow")
async def execute_llm_workflow(
    workflow_name: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a predefined LLM management workflow.
    
    Args:
        workflow_name: Name of the workflow to execute
        parameters: Parameters for the workflow
        
    Returns:
        Dictionary containing workflow execution results
    """
    try:
        # Define available workflows
        workflows = {
            "model_optimization": _model_optimization_workflow,
            "prompt_optimization": _prompt_optimization_workflow,
            "context_analysis": _context_analysis_workflow,
            "multi_model_comparison": _multi_model_comparison_workflow
        }
        
        if workflow_name not in workflows:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown workflow: {workflow_name}. Available workflows: {list(workflows.keys())}"
            )
        
        # Execute the workflow
        result = await workflows[workflow_name](parameters)
        
        return {
            "success": True,
            "workflow": workflow_name,
            "result": result,
            "message": f"LLM workflow '{workflow_name}' executed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


# ============================================================================
# Workflow Implementations
# ============================================================================

async def _model_optimization_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Model optimization workflow including performance testing and routing."""
    from rhetor.core.mcp.tools import (
        get_available_models, test_model_connection, 
        get_model_performance, set_default_model
    )
    
    # Extract parameters
    task_type = parameters.get("task_type", "general")
    performance_criteria = parameters.get("performance_criteria", ["speed", "quality"])
    
    # Step 1: Get available models
    models_result = await get_available_models()
    
    # Step 2: Test connections for all models
    connection_results = []
    if models_result["success"]:
        for provider_id, provider_info in models_result["providers"].items():
            for model in provider_info.get("models", []):
                test_result = await test_model_connection(
                    provider_id=provider_id,
                    model_id=model["id"]
                )
                connection_results.append({
                    "provider": provider_id,
                    "model": model["id"],
                    "connected": test_result["success"],
                    "response_time": test_result.get("response_time", 0)
                })
    
    # Step 3: Get performance metrics for connected models
    performance_results = []
    for conn_result in connection_results:
        if conn_result["connected"]:
            perf_result = await get_model_performance(
                provider_id=conn_result["provider"],
                model_id=conn_result["model"],
                task_type=task_type
            )
            performance_results.append({
                "provider": conn_result["provider"],
                "model": conn_result["model"],
                "performance": perf_result.get("metrics", {}),
                "recommended": perf_result.get("recommended", False)
            })
    
    # Step 4: Select optimal model based on criteria
    optimal_model = None
    best_score = 0
    
    for perf_result in performance_results:
        score = 0
        metrics = perf_result["performance"]
        
        if "speed" in performance_criteria:
            score += metrics.get("speed_score", 0) * 0.4
        if "quality" in performance_criteria:
            score += metrics.get("quality_score", 0) * 0.4
        if "cost" in performance_criteria:
            score += metrics.get("cost_score", 0) * 0.2
        
        if score > best_score:
            best_score = score
            optimal_model = perf_result
    
    # Step 5: Set optimal model as default if found
    optimization_applied = False
    if optimal_model:
        set_result = await set_default_model(
            provider_id=optimal_model["provider"],
            model_id=optimal_model["model"]
        )
        optimization_applied = set_result["success"]
    
    return {
        "models_tested": len(connection_results),
        "models_connected": len([r for r in connection_results if r["connected"]]),
        "performance_analyzed": len(performance_results),
        "optimal_model": optimal_model,
        "optimization_applied": optimization_applied,
        "workflow_summary": {
            "task_type": task_type,
            "criteria": performance_criteria,
            "best_score": best_score,
            "optimization_confidence": "high" if optimal_model else "low"
        }
    }


async def _prompt_optimization_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Prompt optimization workflow including template creation and validation."""
    from rhetor.core.mcp.tools import (
        create_prompt_template, optimize_prompt, 
        validate_prompt_syntax, analyze_prompt_performance
    )
    
    # Extract parameters
    base_prompt = parameters.get("base_prompt", "")
    task_context = parameters.get("task_context", {})
    optimization_goals = parameters.get("optimization_goals", ["clarity", "effectiveness"])
    
    # Step 1: Create initial template
    template_result = await create_prompt_template(
        name=f"optimized_prompt_{task_context.get('task_type', 'general')}",
        template=base_prompt,
        variables=list(task_context.keys()),
        description="Auto-generated optimized prompt template"
    )
    
    # Step 2: Optimize the prompt
    optimization_result = None
    if template_result["success"]:
        optimization_result = await optimize_prompt(
            template_id=template_result["template"]["template_id"],
            optimization_goals=optimization_goals,
            context=task_context
        )
    
    # Step 3: Validate syntax of optimized prompt
    validation_result = None
    if optimization_result and optimization_result["success"]:
        validation_result = await validate_prompt_syntax(
            prompt_text=optimization_result["optimized_prompt"],
            template_variables=list(task_context.keys())
        )
    
    # Step 4: Analyze performance of optimized prompt
    performance_result = None
    if validation_result and validation_result["success"]:
        performance_result = await analyze_prompt_performance(
            prompt_text=optimization_result["optimized_prompt"],
            test_contexts=[task_context],
            metrics_to_analyze=["clarity", "specificity", "effectiveness"]
        )
    
    return {
        "template_creation": template_result,
        "prompt_optimization": optimization_result,
        "syntax_validation": validation_result,
        "performance_analysis": performance_result,
        "workflow_summary": {
            "optimization_goals": optimization_goals,
            "improvements_made": len(optimization_result.get("improvements", [])) if optimization_result else 0,
            "validation_passed": validation_result["success"] if validation_result else False,
            "optimization_confidence": "high" if all([template_result["success"], optimization_result and optimization_result["success"]]) else "medium"
        }
    }


async def _context_analysis_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Context analysis workflow including usage tracking and optimization."""
    from rhetor.core.mcp.tools import (
        analyze_context_usage, optimize_context_window,
        track_context_history, compress_context
    )
    
    # Extract parameters
    context_id = parameters.get("context_id", "default")
    analysis_period = parameters.get("analysis_period", "last_week")
    optimization_target = parameters.get("optimization_target", "efficiency")
    
    # Step 1: Analyze context usage patterns
    usage_result = await analyze_context_usage(
        context_id=context_id,
        time_period=analysis_period,
        include_metrics=True
    )
    
    # Step 2: Track context history for patterns
    history_result = await track_context_history(
        context_id=context_id,
        analysis_depth="detailed",
        include_token_counts=True
    )
    
    # Step 3: Optimize context window if needed
    optimization_result = None
    if usage_result["success"] and usage_result["analysis"]["optimization_needed"]:
        optimization_result = await optimize_context_window(
            context_id=context_id,
            optimization_strategy=optimization_target,
            preserve_recent_messages=True
        )
    
    # Step 4: Compress context if size is an issue
    compression_result = None
    if history_result["success"] and history_result["metrics"]["total_tokens"] > 8000:
        compression_result = await compress_context(
            context_id=context_id,
            compression_ratio=0.7,
            preserve_key_information=True
        )
    
    return {
        "usage_analysis": usage_result,
        "history_tracking": history_result,
        "context_optimization": optimization_result,
        "context_compression": compression_result,
        "workflow_summary": {
            "analysis_period": analysis_period,
            "optimization_applied": optimization_result["success"] if optimization_result else False,
            "compression_applied": compression_result["success"] if compression_result else False,
            "space_saved": compression_result.get("space_saved_percent", 0) if compression_result else 0,
            "analysis_confidence": "high" if usage_result["success"] else "medium"
        }
    }


async def _multi_model_comparison_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Multi-model comparison workflow for evaluating different models on the same task."""
    from rhetor.core.mcp.tools import (
        get_available_models, get_model_capabilities,
        test_model_connection, get_model_performance
    )
    
    # Extract parameters
    task_description = parameters.get("task_description", "")
    test_prompts = parameters.get("test_prompts", [])
    comparison_metrics = parameters.get("comparison_metrics", ["speed", "quality", "cost"])
    
    # Step 1: Get all available models
    models_result = await get_available_models()
    
    # Step 2: Get capabilities for each model
    capability_results = []
    if models_result["success"]:
        for provider_id, provider_info in models_result["providers"].items():
            for model in provider_info.get("models", []):
                cap_result = await get_model_capabilities(
                    provider_id=provider_id,
                    model_id=model["id"]
                )
                capability_results.append({
                    "provider": provider_id,
                    "model": model["id"],
                    "capabilities": cap_result.get("capabilities", {}),
                    "suitable": cap_result.get("suitable_for_task", False)
                })
    
    # Step 3: Test performance for suitable models
    performance_comparisons = []
    suitable_models = [r for r in capability_results if r["suitable"]]
    
    for model_info in suitable_models:
        perf_result = await get_model_performance(
            provider_id=model_info["provider"],
            model_id=model_info["model"],
            task_type="comparison",
            test_prompts=test_prompts
        )
        performance_comparisons.append({
            "provider": model_info["provider"],
            "model": model_info["model"],
            "performance": perf_result.get("metrics", {}),
            "test_results": perf_result.get("test_results", [])
        })
    
    # Step 4: Rank models by specified metrics
    model_rankings = []
    for comparison in performance_comparisons:
        total_score = 0
        metrics = comparison["performance"]
        
        for metric in comparison_metrics:
            score = metrics.get(f"{metric}_score", 0)
            weight = 1.0 / len(comparison_metrics)  # Equal weighting
            total_score += score * weight
        
        model_rankings.append({
            "provider": comparison["provider"],
            "model": comparison["model"],
            "total_score": total_score,
            "individual_scores": {metric: metrics.get(f"{metric}_score", 0) for metric in comparison_metrics}
        })
    
    # Sort by total score
    model_rankings.sort(key=lambda x: x["total_score"], reverse=True)
    
    return {
        "models_evaluated": len(capability_results),
        "suitable_models": len(suitable_models),
        "performance_comparisons": performance_comparisons,
        "model_rankings": model_rankings,
        "recommended_model": model_rankings[0] if model_rankings else None,
        "workflow_summary": {
            "task_description": task_description,
            "comparison_metrics": comparison_metrics,
            "test_prompts_count": len(test_prompts),
            "comparison_confidence": "high" if len(model_rankings) >= 2 else "medium"
        }
    }


# ============================================================================
# Streaming Support for Real-Time CI Responses
# ============================================================================

@mcp_router.post("/stream")
async def stream_mcp_tool(request: MCPStreamRequest) -> EventSourceResponse:
    """
    Execute an MCP tool with Server-Sent Events (SSE) streaming support.
    
    This endpoint enables real-time streaming of CI responses and progress updates
    for long-running operations like CI specialist interactions.
    
    Args:
        request: Streaming request with tool name, arguments, and stream options
        
    Returns:
        EventSourceResponse with real-time updates
    """
    tool_name = request.tool_name
    arguments = request.arguments
    stream_options = request.stream_options or {}
    
    logger.info(f"Starting streaming execution for tool: {tool_name}")
    
    async def event_generator():
        """Generate SSE events for the streaming response."""
        try:
            # Send initial connection event
            yield {
                "event": "connected",
                "data": json.dumps({
                    "tool_name": tool_name,
                    "timestamp": time.time(),
                    "message": f"Connected to streaming execution for {tool_name}"
                })
            }
            
            # Get the tool function
            tool_func = fastmcp_server.get_tool_function(tool_name)
            if not tool_func:
                yield {
                    "event": "error",
                    "data": json.dumps({
                        "error": f"Tool {tool_name} not found",
                        "timestamp": time.time()
                    })
                }
                return
            
            # Check if this tool supports streaming
            supports_streaming = getattr(tool_func, '_supports_streaming', False)
            
            if supports_streaming:
                # Execute with streaming support
                logger.debug(f"Executing {tool_name} with native streaming support")
                
                # Create a queue for streaming events
                event_queue = asyncio.Queue()
                
                # Add streaming callback to arguments
                async def stream_callback(event_type: str, data: Any):
                    """Callback for streaming updates from the tool."""
                    await event_queue.put({
                        "event": event_type,
                        "data": json.dumps({
                            "content": data,
                            "timestamp": time.time()
                        })
                    })
                
                # Execute tool in background task
                async def run_tool():
                    try:
                        result = tool_func(**arguments, _stream_callback=stream_callback)
                        if inspect.iscoroutine(result):
                            result = await result
                        # Put result in queue
                        await event_queue.put({
                            "event": "complete",
                            "data": json.dumps({
                                "result": result,
                                "timestamp": time.time()
                            })
                        })
                    except Exception as e:
                        await event_queue.put({
                            "event": "error",
                            "data": json.dumps({
                                "error": str(e),
                                "timestamp": time.time()
                            })
                        })
                    finally:
                        await event_queue.put(None)  # Sentinel to signal completion
                
                # Start tool execution
                task = asyncio.create_task(run_tool())
                
                # Yield events from queue
                while True:
                    event = await event_queue.get()
                    if event is None:  # Sentinel received
                        break
                    yield event
                
                # Ensure task is complete
                await task
            else:
                # Execute without streaming but with progress updates
                logger.debug(f"Executing {tool_name} with simulated progress updates")
                
                # Send progress: starting
                yield {
                    "event": "progress",
                    "data": json.dumps({
                        "stage": "starting",
                        "percentage": 0,
                        "message": f"Starting execution of {tool_name}",
                        "timestamp": time.time()
                    })
                }
                
                # Execute the tool
                start_time = time.time()
                result = tool_func(**arguments)
                
                # Send progress: processing
                yield {
                    "event": "progress", 
                    "data": json.dumps({
                        "stage": "processing",
                        "percentage": 50,
                        "message": "Processing request...",
                        "timestamp": time.time()
                    })
                }
                
                # Check if result is a coroutine
                if inspect.iscoroutine(result):
                    result = await result
                
                # Send progress: finalizing
                yield {
                    "event": "progress",
                    "data": json.dumps({
                        "stage": "finalizing",
                        "percentage": 90,
                        "message": "Finalizing response...",
                        "timestamp": time.time()
                    })
                }
                
                # Send complete event with result
                execution_time = time.time() - start_time
                yield {
                    "event": "complete",
                    "data": json.dumps({
                        "result": result,
                        "execution_time": execution_time,
                        "timestamp": time.time()
                    })
                }
                
        except Exception as e:
            logger.error(f"Error in streaming execution of {tool_name}: {e}")
            yield {
                "event": "error",
                "data": json.dumps({
                    "error": str(e),
                    "tool_name": tool_name,
                    "timestamp": time.time()
                })
            }
        finally:
            # Send disconnect event
            yield {
                "event": "disconnect",
                "data": json.dumps({
                    "message": "Streaming connection closed",
                    "timestamp": time.time()
                })
            }
    
    return EventSourceResponse(event_generator())


@mcp_router.get("/stream/test")
async def test_streaming() -> EventSourceResponse:
    """
    Test endpoint for SSE streaming functionality.
    
    Returns:
        EventSourceResponse with test events
    """
    async def test_generator():
        """Generate test SSE events."""
        for i in range(5):
            yield {
                "event": "test",
                "data": json.dumps({
                    "message": f"Test event {i+1}",
                    "timestamp": time.time()
                })
            }
            await asyncio.sleep(1)
        
        yield {
            "event": "complete",
            "data": json.dumps({
                "message": "Test complete",
                "timestamp": time.time()
            })
        }
    
    return EventSourceResponse(test_generator())


# Export the router
__all__ = ["mcp_router", "fastmcp_server"]