"""
Migration shim for existing LLMAdapter implementations.
This provides a compatibility layer that redirects all model selection to Rhetor.

Usage:
    Replace existing LLMAdapter imports with:
    from shared.llm_adapter_migration import LLMAdapter
    
This will maintain backward compatibility while using Rhetor's centralized model management.
"""

import os
import logging
import requests
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Get Rhetor URL from environment or default
RHETOR_HOST = os.environ.get('RHETOR_HOST', 'localhost')
RHETOR_PORT = os.environ.get('RHETOR_PORT', '8003')
RHETOR_URL = f"http://{RHETOR_HOST}:{RHETOR_PORT}"


class LLMAdapter:
    """
    Compatibility shim for existing LLMAdapter implementations.
    All model selection is delegated to Rhetor's model registry.
    
    This class maintains the same interface as existing LLMAdapters
    but uses Rhetor as the single source of truth for models.
    """
    
    def __init__(self, component_name: Optional[str] = None, **kwargs):
        """
        Initialize the LLMAdapter shim.
        
        Args:
            component_name: Name of the component using this adapter
            **kwargs: Ignored for compatibility
        """
        self.component_name = component_name or self._detect_component_name()
        
        # Ignore any model specifications in kwargs - Rhetor decides
        if 'model' in kwargs:
            logger.info(f"Ignoring model specification '{kwargs['model']}' - using Rhetor's assignment")
        if 'model_name' in kwargs:
            logger.info(f"Ignoring model_name '{kwargs['model_name']}' - using Rhetor's assignment")
    
    def _detect_component_name(self) -> str:
        """Try to detect component name from file path."""
        try:
            # Get the calling module's path
            import inspect
            frame = inspect.currentframe()
            if frame and frame.f_back and frame.f_back.f_code:
                filepath = frame.f_back.f_code.co_filename
                path = Path(filepath)
                
                # Look for component directory names
                for part in path.parts:
                    part_lower = part.lower()
                    if part_lower in ['apollo', 'athena', 'ergon', 'engram', 'sophia', 
                                      'rhetor', 'hermes', 'harmonia', 'metis', 'noesis',
                                      'numa', 'penia', 'prometheus', 'synthesis', 'telos',
                                      'terma', 'tekton']:
                        return part_lower
        except Exception as e:
            logger.debug(f"Could not detect component name: {e}")
        
        return "unknown"
    
    def get_model(self, task_type: str = "general") -> str:
        """
        Get model from Rhetor's registry.
        
        Args:
            task_type: Type of task (maps to capability)
            
        Returns:
            Model identifier
        """
        try:
            # Map task types to capabilities
            capability_map = {
                "code": "code",
                "coding": "code",
                "programming": "code",
                "planning": "planning",
                "plan": "planning",
                "strategy": "planning",
                "reasoning": "reasoning",
                "analysis": "reasoning",
                "thinking": "reasoning",
                "chat": "chat",
                "conversation": "chat",
                "dialogue": "chat",
                "general": "reasoning"
            }
            
            capability = capability_map.get(task_type.lower(), "reasoning")
            
            # Call Rhetor's model selection endpoint
            response = requests.post(
                f"{RHETOR_URL}/api/models/select",
                json={
                    "component": self.component_name,
                    "capability": capability
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("model_id", "claude-3-5-sonnet-20241022")
            else:
                logger.warning(f"Rhetor model selection failed: {response.status_code}")
                return self._get_fallback_model(capability)
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not connect to Rhetor: {e}")
            return self._get_fallback_model(task_type)
        except Exception as e:
            logger.error(f"Error getting model from Rhetor: {e}")
            return self._get_fallback_model(task_type)
    
    def _get_fallback_model(self, capability: str) -> str:
        """Fallback model selection when Rhetor is unavailable."""
        # Basic fallback models - will be removed once all components use Rhetor
        fallbacks = {
            "code": "claude-3-5-sonnet-20241022",
            "planning": "claude-3-5-sonnet-20241022",
            "reasoning": "claude-3-5-sonnet-20241022",
            "chat": "claude-3-5-haiku-20241022"
        }
        return fallbacks.get(capability, "claude-3-5-sonnet-20241022")
    
    # Compatibility methods for existing LLMAdapter interfaces
    
    @property
    def model(self) -> str:
        """Get default model for this component."""
        return self.get_model("general")
    
    @property
    def model_name(self) -> str:
        """Alias for model property."""
        return self.model
    
    def get_model_for_task(self, task: str) -> str:
        """Get model for specific task type."""
        return self.get_model(task)
    
    def resolve_model_alias(self, alias: str) -> str:
        """Resolve a model alias through Rhetor."""
        try:
            response = requests.get(
                f"{RHETOR_URL}/api/models/resolve/{alias}",
                timeout=5
            )
            if response.status_code == 200:
                return response.json().get("model_id", alias)
        except Exception as e:
            logger.debug(f"Could not resolve alias through Rhetor: {e}")
        return alias
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get model information from Rhetor."""
        try:
            response = requests.get(
                f"{RHETOR_URL}/api/models/info/{model_id}",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.debug(f"Could not get model info from Rhetor: {e}")
        
        # Return minimal info as fallback
        return {
            "id": model_id,
            "context_window": 200000,
            "max_output": 4096
        }
    
    # Deprecated methods that should not be used
    
    def set_model(self, model: str):
        """DEPRECATED: Models are managed by Rhetor only."""
        logger.warning(f"set_model() is deprecated. Model selection is managed by Rhetor. Ignoring '{model}'")
    
    def update_model(self, model: str):
        """DEPRECATED: Models are managed by Rhetor only."""
        logger.warning(f"update_model() is deprecated. Model selection is managed by Rhetor. Ignoring '{model}'")


# Additional compatibility classes for specific adapters

class MetisLLMAdapter(LLMAdapter):
    """Compatibility shim for Metis."""
    def __init__(self, **kwargs):
        super().__init__(component_name="metis", **kwargs)


class PrometheusLLMAdapter(LLMAdapter):
    """Compatibility shim for Prometheus."""
    def __init__(self, **kwargs):
        super().__init__(component_name="prometheus", **kwargs)


class RhetorLLMAdapter(LLMAdapter):
    """Compatibility shim for components using RhetorLLMAdapter."""
    def __init__(self, **kwargs):
        super().__init__(component_name="rhetor", **kwargs)


# Function to help with migration
def get_llm_adapter(component_name: Optional[str] = None) -> LLMAdapter:
    """
    Get an LLMAdapter instance for a component.
    
    Args:
        component_name: Name of the component
        
    Returns:
        LLMAdapter instance that uses Rhetor's model registry
    """
    return LLMAdapter(component_name=component_name)