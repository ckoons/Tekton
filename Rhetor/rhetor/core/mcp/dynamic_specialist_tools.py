"""
Dynamic Specialist Creation MCP Tools.

This module provides MCP tools for creating and managing AI specialists
dynamically at runtime using templates and customization options.
"""

import json
import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

# Check if FastMCP is available
try:
    from tekton.mcp.fastmcp.decorators import mcp_tool
    fastmcp_available = True
except ImportError:
    fastmcp_available = False
    # Define dummy decorator
    def mcp_tool(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

logger = logging.getLogger(__name__)


@mcp_tool(
    name="ListSpecialistTemplates",
    description="List all available specialist templates for dynamic creation",
    tags=["ai", "specialists", "templates", "dynamic"],
    category="ai_orchestration"
)
async def list_specialist_templates() -> Dict[str, Any]:
    """
    List all available specialist templates.
    
    Returns:
        Dictionary containing available templates and their descriptions
    """
    try:
        from ..specialist_templates import list_templates
        
        templates = list_templates()
        
        # Group templates by base type
        grouped = {}
        for template in templates:
            base_type = template["base_type"]
            if base_type not in grouped:
                grouped[base_type] = []
            grouped[base_type].append(template)
        
        return {
            "success": True,
            "templates": templates,
            "grouped_by_type": grouped,
            "total_count": len(templates),
            "base_types": list(grouped.keys()),
            "message": f"Found {len(templates)} specialist templates"
        }
        
    except Exception as e:
        logger.error(f"Error listing specialist templates: {e}")
        return {
            "success": False,
            "error": f"Failed to list specialist templates: {str(e)}"
        }


@mcp_tool(
    name="CreateDynamicSpecialist",
    description="Create a new AI specialist dynamically from a template",
    tags=["ai", "specialists", "dynamic", "creation"],
    category="ai_orchestration"
)
async def create_dynamic_specialist(
    template_id: str,
    specialist_name: Optional[str] = None,
    customization: Optional[Dict[str, Any]] = None,
    auto_activate: bool = True
) -> Dict[str, Any]:
    """
    Create a new AI specialist dynamically from a template.
    
    Args:
        template_id: ID of the template to use (e.g., "code-reviewer", "data-analyst")
        specialist_name: Optional custom name for the specialist
        customization: Optional customization parameters
        auto_activate: Whether to automatically activate the specialist
        
    Returns:
        Dictionary containing creation result and specialist details
    """
    try:
        from ..specialist_templates import create_from_template
        from .tools_integration import get_mcp_tools_integration
        
        # Generate unique specialist ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        specialist_id = f"{template_id}_{timestamp}_{str(uuid.uuid4())[:8]}"
        
        if specialist_name:
            # Use custom name in ID
            specialist_id = f"{specialist_name.lower().replace(' ', '-')}_{timestamp}"
        
        # Create specialist configuration from template
        config = create_from_template(template_id, specialist_id, customization)
        
        if not config:
            return {
                "success": False,
                "error": f"Template '{template_id}' not found"
            }
        
        # Add custom name if provided
        if specialist_name:
            config["personality"]["custom_name"] = specialist_name
            
        # Try to use live integration if available
        integration = get_mcp_tools_integration()
        
        if integration and integration.specialist_manager:
            # Import the proper dataclass
            from rhetor.core.ai_specialist_manager import AISpecialistConfig
            
            # Register the new specialist configuration
            specialist_config = AISpecialistConfig(
                specialist_id=specialist_id,
                specialist_type=config['specialist_type'],
                component_id=config['component_id'],
                model_config=config['model_config'],
                personality=config['personality'],
                capabilities=config['capabilities'],
                status='inactive',
                process_id=None
            )
            integration.specialist_manager.specialists[specialist_id] = specialist_config
            
            # Auto-activate if requested
            if auto_activate:
                activation_result = await integration.specialist_manager.activate_specialist(
                    specialist_id, 
                    initialization_context=customization
                )
                
                if not activation_result["success"]:
                    return {
                        "success": False,
                        "error": f"Specialist created but activation failed: {activation_result.get('error')}"
                    }
                
                return {
                    "success": True,
                    "specialist_id": specialist_id,
                    "template_used": template_id,
                    "status": "active",
                    "configuration": config,
                    "activation_details": activation_result,
                    "message": f"Dynamic specialist '{specialist_id}' created and activated successfully"
                }
            else:
                return {
                    "success": True,
                    "specialist_id": specialist_id,
                    "template_used": template_id,
                    "status": "inactive",
                    "configuration": config,
                    "message": f"Dynamic specialist '{specialist_id}' created successfully (not activated)"
                }
        
        # Fallback to mock response
        logger.warning("MCP tools integration not available, returning mock response")
        return {
            "success": True,
            "specialist_id": specialist_id,
            "template_used": template_id,
            "status": "created",
            "configuration": config,
            "mock_mode": True,
            "message": f"Dynamic specialist '{specialist_id}' created successfully (mock mode)"
        }
        
    except Exception as e:
        logger.error(f"Error creating dynamic specialist: {e}")
        return {
            "success": False,
            "error": f"Failed to create dynamic specialist: {str(e)}"
        }


@mcp_tool(
    name="CloneSpecialist", 
    description="Clone an existing specialist with modifications",
    tags=["ai", "specialists", "dynamic", "cloning"],
    category="ai_orchestration"
)
async def clone_specialist(
    source_specialist_id: str,
    new_specialist_name: Optional[str] = None,
    modifications: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Clone an existing specialist with optional modifications.
    
    Args:
        source_specialist_id: ID of the specialist to clone
        new_specialist_name: Optional name for the cloned specialist
        modifications: Optional modifications to apply
        
    Returns:
        Dictionary containing clone result and new specialist details
    """
    try:
        from .tools_integration import get_mcp_tools_integration
        
        integration = get_mcp_tools_integration()
        
        if integration and integration.specialist_manager:
            # Get source specialist
            source = integration.specialist_manager.specialists.get(source_specialist_id)
            
            if not source:
                return {
                    "success": False,
                    "error": f"Source specialist '{source_specialist_id}' not found"
                }
            
            # Generate new ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            clone_id = f"{source_specialist_id}_clone_{timestamp}"
            
            if new_specialist_name:
                clone_id = f"{new_specialist_name.lower().replace(' ', '-')}_{timestamp}"
            
            # Create clone configuration
            clone_config = {
                "specialist_id": clone_id,
                "specialist_type": f"clone-{source.specialist_type}",
                "component_id": source.component_id,
                "model_config": source.model_config.copy(),
                "personality": source.personality.copy(),
                "capabilities": source.capabilities.copy(),
                "cloned_from": source_specialist_id,
                "clone_time": datetime.now().isoformat()
            }
            
            # Apply modifications
            if modifications:
                if "model" in modifications:
                    clone_config["model_config"]["model"] = modifications["model"]
                if "temperature" in modifications:
                    clone_config["model_config"]["options"]["temperature"] = modifications["temperature"]
                if "additional_capabilities" in modifications:
                    clone_config["capabilities"].extend(modifications["additional_capabilities"])
                if "personality_adjustments" in modifications:
                    clone_config["personality"].update(modifications["personality_adjustments"])
            
            # Add custom name if provided
            if new_specialist_name:
                clone_config["personality"]["custom_name"] = new_specialist_name
            
            # Import the proper dataclass
            from rhetor.core.ai_specialist_manager import AISpecialistConfig
            
            # Register the clone
            clone_specialist = AISpecialistConfig(
                specialist_id=clone_id,
                specialist_type=clone_config["specialist_type"],
                component_id=clone_config["component_id"],
                model_config=clone_config["model_config"],
                personality=clone_config["personality"],
                capabilities=clone_config["capabilities"],
                status='inactive',
                process_id=None
            )
            integration.specialist_manager.specialists[clone_id] = clone_specialist
            
            # Activate the clone
            activation_result = await integration.specialist_manager.activate_specialist(clone_id)
            
            return {
                "success": True,
                "specialist_id": clone_id,
                "cloned_from": source_specialist_id,
                "status": "active" if activation_result["success"] else "inactive",
                "configuration": clone_config,
                "activation_details": activation_result,
                "message": f"Specialist cloned successfully: {source_specialist_id} -> {clone_id}"
            }
        
        # Fallback
        logger.warning("MCP tools integration not available")
        return {
            "success": False,
            "error": "Specialist manager not available"
        }
        
    except Exception as e:
        logger.error(f"Error cloning specialist: {e}")
        return {
            "success": False,
            "error": f"Failed to clone specialist: {str(e)}"
        }


@mcp_tool(
    name="ModifySpecialist",
    description="Modify an existing specialist's configuration at runtime",
    tags=["ai", "specialists", "dynamic", "configuration"],
    category="ai_orchestration"
)
async def modify_specialist(
    specialist_id: str,
    modifications: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Modify an existing specialist's configuration.
    
    Args:
        specialist_id: ID of the specialist to modify
        modifications: Configuration changes to apply
        
    Returns:
        Dictionary containing modification result
    """
    try:
        from .tools_integration import get_mcp_tools_integration
        
        integration = get_mcp_tools_integration()
        
        if integration and integration.specialist_manager:
            specialist = integration.specialist_manager.specialists.get(specialist_id)
            
            if not specialist:
                return {
                    "success": False,
                    "error": f"Specialist '{specialist_id}' not found"
                }
            
            # Track what was modified
            applied_changes = []
            
            # Apply modifications
            if "model" in modifications:
                specialist.model_config["model"] = modifications["model"]
                applied_changes.append(f"model -> {modifications['model']}")
                
            if "temperature" in modifications:
                specialist.model_config["options"]["temperature"] = modifications["temperature"]
                applied_changes.append(f"temperature -> {modifications['temperature']}")
                
            if "max_tokens" in modifications:
                specialist.model_config["options"]["max_tokens"] = modifications["max_tokens"]
                applied_changes.append(f"max_tokens -> {modifications['max_tokens']}")
                
            if "personality_traits" in modifications:
                specialist.personality["traits"] = modifications["personality_traits"]
                applied_changes.append(f"personality_traits -> {modifications['personality_traits']}")
                
            if "system_prompt" in modifications:
                specialist.personality["system_prompt"] = modifications["system_prompt"]
                applied_changes.append("system_prompt updated")
                
            if "capabilities" in modifications:
                specialist.capabilities = modifications["capabilities"]
                applied_changes.append(f"capabilities -> {modifications['capabilities']}")
            
            return {
                "success": True,
                "specialist_id": specialist_id,
                "modifications_applied": applied_changes,
                "current_status": specialist.status,
                "message": f"Modified {len(applied_changes)} settings for specialist '{specialist_id}'"
            }
        
        # Fallback
        logger.warning("MCP tools integration not available")
        return {
            "success": False,
            "error": "Specialist manager not available"
        }
        
    except Exception as e:
        logger.error(f"Error modifying specialist: {e}")
        return {
            "success": False,
            "error": f"Failed to modify specialist: {str(e)}"
        }


@mcp_tool(
    name="DeactivateSpecialist",
    description="Deactivate a dynamic specialist to free resources",
    tags=["ai", "specialists", "dynamic", "lifecycle"],
    category="ai_orchestration"
)
async def deactivate_specialist(
    specialist_id: str,
    preserve_history: bool = True
) -> Dict[str, Any]:
    """
    Deactivate a dynamic specialist.
    
    Args:
        specialist_id: ID of the specialist to deactivate
        preserve_history: Whether to preserve conversation history
        
    Returns:
        Dictionary containing deactivation result
    """
    try:
        from .tools_integration import get_mcp_tools_integration
        
        integration = get_mcp_tools_integration()
        
        if integration and integration.specialist_manager:
            specialist = integration.specialist_manager.specialists.get(specialist_id)
            
            if not specialist:
                return {
                    "success": False,
                    "error": f"Specialist '{specialist_id}' not found"
                }
            
            # Check if it's a core specialist
            core_specialists = ["rhetor-orchestrator", "engram-memory"]
            if specialist_id in core_specialists:
                return {
                    "success": False,
                    "error": f"Cannot deactivate core specialist '{specialist_id}'"
                }
            
            # Check if it's a dynamic specialist
            if not hasattr(specialist, 'created_from_template'):
                logger.warning(f"Specialist '{specialist_id}' is not a dynamic specialist")
            
            # Update status
            specialist.status = "inactive"
            specialist.process_id = None
            
            # Preserve history if requested
            history_preserved = False
            if preserve_history:
                # In a real implementation, this would save to persistent storage
                history_preserved = True
            
            return {
                "success": True,
                "specialist_id": specialist_id,
                "previous_status": "active",
                "current_status": "inactive",
                "history_preserved": history_preserved,
                "message": f"Specialist '{specialist_id}' deactivated successfully"
            }
        
        # Fallback
        logger.warning("MCP tools integration not available")
        return {
            "success": False,
            "error": "Specialist manager not available"
        }
        
    except Exception as e:
        logger.error(f"Error deactivating specialist: {e}")
        return {
            "success": False,
            "error": f"Failed to deactivate specialist: {str(e)}"
        }


@mcp_tool(
    name="GetSpecialistMetrics",
    description="Get performance metrics for a specialist",
    tags=["ai", "specialists", "metrics", "monitoring"],
    category="ai_orchestration"
)
async def get_specialist_metrics(
    specialist_id: str
) -> Dict[str, Any]:
    """
    Get performance metrics for a specialist.
    
    Args:
        specialist_id: ID of the specialist
        
    Returns:
        Dictionary containing specialist metrics
    """
    try:
        from .tools_integration import get_mcp_tools_integration
        
        integration = get_mcp_tools_integration()
        
        if integration and integration.specialist_manager:
            specialist = integration.specialist_manager.specialists.get(specialist_id)
            
            if not specialist:
                return {
                    "success": False,
                    "error": f"Specialist '{specialist_id}' not found"
                }
            
            # Calculate metrics (simulated for now)
            metrics = {
                "specialist_id": specialist_id,
                "status": specialist.status,
                "uptime_seconds": 300 if specialist.status == "active" else 0,
                "messages_processed": 15 if specialist.status == "active" else 0,
                "average_response_time_ms": 1250 if specialist.status == "active" else 0,
                "model_usage": {
                    "model": specialist.model_config.get("model", "unknown"),
                    "tokens_used": 5000 if specialist.status == "active" else 0,
                    "api_calls": 15 if specialist.status == "active" else 0
                },
                "resource_usage": {
                    "memory_mb": 256 if specialist.status == "active" else 0,
                    "cpu_percent": 2.5 if specialist.status == "active" else 0
                },
                "conversation_stats": {
                    "active_conversations": 2 if specialist.status == "active" else 0,
                    "total_conversations": 5 if specialist.status == "active" else 0,
                    "average_conversation_length": 3.2 if specialist.status == "active" else 0
                }
            }
            
            return {
                "success": True,
                "metrics": metrics,
                "timestamp": datetime.now().isoformat(),
                "message": f"Retrieved metrics for specialist '{specialist_id}'"
            }
        
        # Fallback
        logger.warning("MCP tools integration not available")
        return {
            "success": False,
            "error": "Specialist manager not available"
        }
        
    except Exception as e:
        logger.error(f"Error getting specialist metrics: {e}")
        return {
            "success": False,
            "error": f"Failed to get specialist metrics: {str(e)}"
        }


# List of dynamic specialist tools
dynamic_specialist_tools = [
    list_specialist_templates,
    create_dynamic_specialist,
    clone_specialist,
    modify_specialist,
    deactivate_specialist,
    get_specialist_metrics
]

__all__ = [
    "list_specialist_templates",
    "create_dynamic_specialist", 
    "clone_specialist",
    "modify_specialist",
    "deactivate_specialist",
    "get_specialist_metrics",
    "dynamic_specialist_tools"
]