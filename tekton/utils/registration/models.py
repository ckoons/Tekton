"""
Data models for component registration configuration.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union


@dataclass
class ParameterConfig:
    """Configuration for a method parameter."""
    name: str
    type: str
    required: bool = True
    description: Optional[str] = None
    default: Optional[Any] = None


@dataclass
class ReturnConfig:
    """Configuration for a method return value."""
    type: str
    description: Optional[str] = None


@dataclass
class MethodConfig:
    """Configuration for a capability method."""
    id: str
    name: str
    description: Optional[str] = None
    parameters: List[ParameterConfig] = field(default_factory=list)
    returns: Optional[ReturnConfig] = None


@dataclass
class CapabilityConfig:
    """Configuration for a component capability."""
    id: str
    name: str
    description: Optional[str] = None
    methods: List[MethodConfig] = field(default_factory=list)


@dataclass
class ComponentConfig:
    """Configuration for a Tekton component."""
    id: str
    name: str
    version: str
    port: int
    description: Optional[str] = None
    capabilities: List[CapabilityConfig] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


def dict_to_parameter_config(data: Dict[str, Any]) -> ParameterConfig:
    """Convert a dictionary to a ParameterConfig object."""
    return ParameterConfig(
        name=data["name"],
        type=data["type"],
        required=data.get("required", True),
        description=data.get("description"),
        default=data.get("default"),
    )


def dict_to_return_config(data: Dict[str, Any]) -> Optional[ReturnConfig]:
    """Convert a dictionary to a ReturnConfig object."""
    if not data:
        return None
    return ReturnConfig(
        type=data["type"],
        description=data.get("description"),
    )


def dict_to_method_config(data: Dict[str, Any]) -> MethodConfig:
    """Convert a dictionary to a MethodConfig object."""
    parameters = [dict_to_parameter_config(p) for p in data.get("parameters", [])]
    returns = dict_to_return_config(data.get("returns", {}))
    
    return MethodConfig(
        id=data["id"],
        name=data["name"],
        description=data.get("description"),
        parameters=parameters,
        returns=returns,
    )


def dict_to_capability_config(data: Dict[str, Any]) -> CapabilityConfig:
    """Convert a dictionary to a CapabilityConfig object."""
    methods = [dict_to_method_config(m) for m in data.get("methods", [])]
    
    return CapabilityConfig(
        id=data["id"],
        name=data["name"],
        description=data.get("description"),
        methods=methods,
    )


def dict_to_component_config(data: Dict[str, Any]) -> ComponentConfig:
    """Convert a dictionary to a ComponentConfig object."""
    component_data = data["component"]
    capabilities_data = data.get("capabilities", [])
    config_data = data.get("config", {})
    
    capabilities = [dict_to_capability_config(c) for c in capabilities_data]
    
    return ComponentConfig(
        id=component_data["id"],
        name=component_data["name"],
        version=component_data["version"],
        port=component_data["port"],
        description=component_data.get("description"),
        capabilities=capabilities,
        config=config_data,
    )