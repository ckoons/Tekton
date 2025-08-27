"""
Model Registry - Central authority for all model management in Tekton.
This is the ONLY place where models are configured and selected.
No environment variables, no scattered LLMAdapters - just Rhetor.
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
from dataclasses import dataclass, asdict

# Configure logging
logger = logging.getLogger(__name__)

# Type definitions
CapabilityType = Literal["code", "planning", "reasoning", "chat"]
ProviderType = Literal["anthropic", "openai", "ollama", "groq", "together"]


@dataclass
class ModelInfo:
    """Complete information about a model."""
    id: str
    provider: str
    name: str
    aliases: List[str]
    capabilities: List[str]
    context_window: int
    max_output: int
    deprecated: bool
    fallback: Optional[str] = None
    
    def supports_capability(self, capability: str) -> bool:
        """Check if model supports a capability."""
        return capability in self.capabilities
    
    def matches_alias(self, alias: str) -> bool:
        """Check if model matches an alias."""
        return alias.lower() in [a.lower() for a in self.aliases] or alias.lower() == self.id.lower()


class ModelRegistry:
    """
    Central model registry for all of Tekton.
    This is the single source of truth for model management.
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the model registry.
        
        Args:
            config_dir: Path to configuration directory (defaults to Rhetor/config)
        """
        if config_dir is None:
            config_dir = Path(__file__).parent.parent.parent / "config"
        
        self.config_dir = config_dir
        self.model_catalog: Dict[str, Any] = {}
        self.model_assignments: Dict[str, Any] = {}
        self._model_cache: Dict[str, ModelInfo] = {}
        
        # Load configurations
        self._load_configurations()
    
    def _load_configurations(self):
        """Load model catalog and assignments from configuration files."""
        # Load model catalog (YAML)
        catalog_path = self.config_dir / "model_catalog.yaml"
        if catalog_path.exists():
            try:
                with open(catalog_path, 'r') as f:
                    self.model_catalog = yaml.safe_load(f)
                    logger.info(f"Loaded model catalog from {catalog_path}")
                    self._build_model_cache()
            except Exception as e:
                logger.error(f"Failed to load model catalog: {e}")
                self.model_catalog = {"providers": {}}
        else:
            logger.warning(f"Model catalog not found at {catalog_path}")
            self.model_catalog = {"providers": {}}
        
        # Load model assignments (JSON)
        assignments_path = self.config_dir / "model_assignments.json"
        if assignments_path.exists():
            try:
                with open(assignments_path, 'r') as f:
                    self.model_assignments = json.load(f)
                    logger.info(f"Loaded model assignments from {assignments_path}")
            except Exception as e:
                logger.error(f"Failed to load model assignments: {e}")
                self.model_assignments = {"defaults": {}, "components": {}}
        else:
            logger.warning(f"Model assignments not found at {assignments_path}")
            self.model_assignments = {"defaults": {}, "components": {}}
    
    def _build_model_cache(self):
        """Build a cache of ModelInfo objects from the catalog."""
        self._model_cache.clear()
        
        for provider_name, provider_data in self.model_catalog.get("providers", {}).items():
            if provider_data.get("status") != "active":
                continue
                
            for model_data in provider_data.get("models", []):
                model_id = model_data["id"]
                model_info = ModelInfo(
                    id=model_id,
                    provider=provider_name,
                    name=model_data.get("name", model_id),
                    aliases=model_data.get("aliases", []),
                    capabilities=model_data.get("capabilities", []),
                    context_window=model_data.get("context_window", 4096),
                    max_output=model_data.get("max_output", 4096),
                    deprecated=model_data.get("deprecated", False),
                    fallback=model_data.get("fallback")
                )
                self._model_cache[model_id] = model_info
                
                # Also index by aliases for quick lookup
                for alias in model_info.aliases:
                    self._model_cache[alias.lower()] = model_info
    
    def reload_configurations(self):
        """Reload configurations from disk."""
        logger.info("Reloading model configurations")
        self._load_configurations()
    
    def save_assignments(self):
        """Save current assignments back to disk."""
        assignments_path = self.config_dir / "model_assignments.json"
        try:
            self.model_assignments["last_updated"] = datetime.now().isoformat()
            with open(assignments_path, 'w') as f:
                json.dump(self.model_assignments, f, indent=2)
            logger.info(f"Saved model assignments to {assignments_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save model assignments: {e}")
            return False
    
    # Core Model Selection Methods
    
    def get_model_for_component(
        self,
        component: str,
        capability: CapabilityType,
        allow_deprecated: bool = False
    ) -> Optional[str]:
        """
        Get the assigned model for a component and capability.
        This is the PRIMARY method that all components should use.
        
        Args:
            component: Component name (e.g., "ergon", "sophia")
            capability: Capability type (code, planning, reasoning, chat)
            allow_deprecated: Whether to allow deprecated models
            
        Returns:
            Model ID or None if no model found
        """
        component = component.lower()
        
        # Check component-specific assignment
        comp_config = self.model_assignments.get("components", {}).get(component, {})
        assigned = comp_config.get("assignments", {}).get(capability)
        
        # Handle "use_default" or missing assignment
        if not assigned or assigned == "use_default":
            assigned = self.model_assignments.get("defaults", {}).get(capability)
        
        if not assigned:
            logger.warning(f"No model assigned for {component}/{capability}")
            return None
        
        # Validate model exists and handle deprecation
        model = self.get_model_info(assigned)
        if not model:
            logger.error(f"Assigned model {assigned} not found in catalog")
            return None
        
        if model.deprecated and not allow_deprecated:
            if model.fallback:
                logger.info(f"Model {assigned} is deprecated, using fallback {model.fallback}")
                return model.fallback
            else:
                logger.warning(f"Model {assigned} is deprecated with no fallback")
                return None
        
        return model.id
    
    def resolve_model_alias(self, alias: str) -> Optional[str]:
        """
        Resolve a model alias to its actual model ID.
        
        Args:
            alias: Model alias (e.g., "sonnet", "gpt4", "claude-latest")
            
        Returns:
            Actual model ID or None if not found
        """
        alias_lower = alias.lower()
        
        # Check cache first (includes aliases)
        if alias_lower in self._model_cache:
            return self._model_cache[alias_lower].id
        
        # Search through all models
        for model in self._model_cache.values():
            if model.matches_alias(alias):
                return model.id
        
        return None
    
    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """
        Get complete information about a model.
        
        Args:
            model_id: Model ID or alias
            
        Returns:
            ModelInfo object or None
        """
        # Try direct lookup
        if model_id in self._model_cache:
            return self._model_cache[model_id]
        
        # Try alias resolution
        resolved = self.resolve_model_alias(model_id)
        if resolved and resolved in self._model_cache:
            return self._model_cache[resolved]
        
        return None
    
    def get_available_models(
        self,
        provider: Optional[str] = None,
        capability: Optional[str] = None,
        include_deprecated: bool = False
    ) -> List[ModelInfo]:
        """
        Get all available models matching criteria.
        
        Args:
            provider: Filter by provider
            capability: Filter by capability
            include_deprecated: Include deprecated models
            
        Returns:
            List of ModelInfo objects
        """
        models = []
        
        for model_id, model in self._model_cache.items():
            # Skip aliases (they point to same object)
            if model_id != model.id:
                continue
            
            # Apply filters
            if provider and model.provider != provider.lower():
                continue
            
            if capability and not model.supports_capability(capability):
                continue
            
            if not include_deprecated and model.deprecated:
                continue
            
            models.append(model)
        
        return models
    
    def get_providers(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all providers.
        
        Returns:
            Dictionary of provider information
        """
        providers = {}
        for name, data in self.model_catalog.get("providers", {}).items():
            providers[name] = {
                "name": data.get("name", name),
                "status": data.get("status", "unknown"),
                "model_count": len(data.get("models", []))
            }
        return providers
    
    # Assignment Management Methods
    
    def update_component_assignment(
        self,
        component: str,
        capability: CapabilityType,
        model_id: str
    ) -> bool:
        """
        Update model assignment for a component and capability.
        
        Args:
            component: Component name
            capability: Capability type
            model_id: Model ID or "use_default"
            
        Returns:
            True if successful
        """
        component = component.lower()
        
        # Validate model exists (unless it's "use_default")
        if model_id != "use_default":
            model = self.get_model_info(model_id)
            if not model:
                logger.error(f"Cannot assign non-existent model {model_id}")
                return False
            
            if not model.supports_capability(capability):
                logger.warning(f"Model {model_id} does not declare support for {capability}")
        
        # Ensure component structure exists
        if "components" not in self.model_assignments:
            self.model_assignments["components"] = {}
        
        if component not in self.model_assignments["components"]:
            self.model_assignments["components"][component] = {
                "assignments": {}
            }
        
        # Update assignment
        self.model_assignments["components"][component]["assignments"][capability] = model_id
        
        # Save to disk
        return self.save_assignments()
    
    def update_default_assignment(self, capability: CapabilityType, model_id: str) -> bool:
        """
        Update default model assignment for a capability.
        
        Args:
            capability: Capability type
            model_id: Model ID
            
        Returns:
            True if successful
        """
        # Validate model exists
        model = self.get_model_info(model_id)
        if not model:
            logger.error(f"Cannot assign non-existent model {model_id}")
            return False
        
        if not model.supports_capability(capability):
            logger.warning(f"Model {model_id} does not declare support for {capability}")
        
        # Update default
        if "defaults" not in self.model_assignments:
            self.model_assignments["defaults"] = {}
        
        self.model_assignments["defaults"][capability] = model_id
        
        # Save to disk
        return self.save_assignments()
    
    def get_assignments_matrix(self) -> Dict[str, Any]:
        """
        Get the complete assignments matrix for UI display.
        
        Returns:
            Dictionary with defaults and component assignments
        """
        return {
            "defaults": self.model_assignments.get("defaults", {}),
            "components": {
                name: data.get("assignments", {})
                for name, data in self.model_assignments.get("components", {}).items()
            }
        }
    
    # Utility Methods
    
    def select_best_model(
        self,
        capability: CapabilityType,
        requirements: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Automatically select the best model for given requirements.
        
        Args:
            capability: Required capability
            requirements: Additional requirements (context_window, cost_tier, etc.)
            
        Returns:
            Model ID or None
        """
        requirements = requirements or {}
        
        # Get capability priority from catalog
        priorities = self.model_catalog.get("selection_rules", {}).get("capability_priority", {})
        priority_list = priorities.get(capability, [])
        
        # Filter by requirements
        min_context = requirements.get("min_context_window", 0)
        max_cost_tier = requirements.get("max_cost_tier", "expensive")
        
        for model_id in priority_list:
            model = self.get_model_info(model_id)
            if not model:
                continue
            
            if model.deprecated:
                continue
            
            if model.context_window < min_context:
                continue
            
            # Check cost tier if specified
            if max_cost_tier:
                cost_tiers = self.model_catalog.get("selection_rules", {}).get("cost_tiers", {})
                if max_cost_tier == "free" and model_id not in cost_tiers.get("free", []):
                    continue
                elif max_cost_tier == "cheap" and model_id not in cost_tiers.get("free", []) + cost_tiers.get("cheap", []):
                    continue
            
            return model.id
        
        # Fallback to default
        return self.model_assignments.get("defaults", {}).get(capability)
    
    def validate_all_assignments(self) -> List[str]:
        """
        Validate all current assignments and return list of issues.
        
        Returns:
            List of validation issues (empty if all valid)
        """
        issues = []
        
        # Check defaults
        for capability, model_id in self.model_assignments.get("defaults", {}).items():
            model = self.get_model_info(model_id)
            if not model:
                issues.append(f"Default {capability}: model {model_id} not found")
            elif model.deprecated:
                issues.append(f"Default {capability}: model {model_id} is deprecated")
        
        # Check component assignments
        for component, data in self.model_assignments.get("components", {}).items():
            for capability, model_id in data.get("assignments", {}).items():
                if model_id == "use_default":
                    continue
                
                model = self.get_model_info(model_id)
                if not model:
                    issues.append(f"{component}/{capability}: model {model_id} not found")
                elif model.deprecated:
                    issues.append(f"{component}/{capability}: model {model_id} is deprecated")
        
        return issues


# Global registry instance
_registry: Optional[ModelRegistry] = None


def get_model_registry() -> ModelRegistry:
    """Get or create the global model registry instance."""
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry


# Convenience functions for common operations

def get_model_for_component(component: str, capability: str) -> Optional[str]:
    """Get model for a component and capability."""
    return get_model_registry().get_model_for_component(component, capability)


def resolve_model(alias: str) -> Optional[str]:
    """Resolve a model alias to its ID."""
    return get_model_registry().resolve_model_alias(alias)