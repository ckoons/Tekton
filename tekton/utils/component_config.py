"""
Centralized component configuration for Tekton.

This module provides access to component definitions, metadata, and dependencies
from the central tekton_components.yaml configuration file.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class ComponentInfo:
    """Information about a Tekton component"""
    id: str
    name: str
    port: int
    description: str
    category: str
    startup_priority: int = 0
    dependencies: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    

@dataclass
class ServiceInfo:
    """Information about a Tekton service"""
    id: str
    name: str
    description: str
    category: str
    port: Optional[int] = None
    http_port: Optional[int] = None
    ws_port: Optional[int] = None


class ComponentConfig:
    """Manages Tekton component configuration"""
    
    def __init__(self):
        self._config: Optional[Dict[str, Any]] = None
        self._components: Dict[str, ComponentInfo] = {}
        self._services: Dict[str, ServiceInfo] = {}
        self._load_config()
        
    def _load_config(self):
        """Load configuration from YAML file"""
        config_path = Path(__file__).parent.parent.parent / "config" / "tekton_components.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Component configuration not found at {config_path}")
            
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
            
        # Parse components
        for comp_id, comp_data in self._config.get('components', {}).items():
            # Get port from TektonEnviron (single source of truth)
            from shared.env import TektonEnviron
            env_var = f"{comp_id.upper()}_PORT"
            port_str = TektonEnviron.get(env_var)
            port = int(port_str) if port_str else comp_data['port']  # Fallback to YAML if env not set
            
            self._components[comp_id] = ComponentInfo(
                id=comp_id,
                name=comp_data['name'],
                port=port,
                description=comp_data['description'],
                category=comp_data['category'],
                startup_priority=comp_data.get('startup_priority', 0),
                dependencies=comp_data.get('dependencies', []),
                capabilities=comp_data.get('capabilities', [])
            )
            
        # Parse services
        for svc_id, svc_data in self._config.get('services', {}).items():
            # Get ports from TektonEnviron (single source of truth)
            from shared.env import TektonEnviron
            
            # Handle different port types
            port = None
            if 'port' in svc_data:
                env_var = f"{svc_id.upper()}_PORT"
                port_str = TektonEnviron.get(env_var)
                port = int(port_str) if port_str else svc_data.get('port')
            
            http_port = None
            if 'http_port' in svc_data:
                env_var = f"{svc_id.upper()}_HTTP_PORT"
                port_str = TektonEnviron.get(env_var)
                http_port = int(port_str) if port_str else svc_data.get('http_port')
            
            ws_port = None
            if 'ws_port' in svc_data:
                env_var = f"{svc_id.upper()}_WS_PORT"
                port_str = TektonEnviron.get(env_var)
                ws_port = int(port_str) if port_str else svc_data.get('ws_port')
            
            self._services[svc_id] = ServiceInfo(
                id=svc_id,
                name=svc_data['name'],
                description=svc_data['description'],
                category=svc_data['category'],
                port=port,
                http_port=http_port,
                ws_port=ws_port
            )
    
    def get_component(self, component_id: str) -> Optional[ComponentInfo]:
        """Get information about a specific component"""
        return self._components.get(component_id)
    
    def get_service(self, service_id: str) -> Optional[ServiceInfo]:
        """Get information about a specific service"""
        return self._services.get(service_id)
    
    def get_all_components(self) -> Dict[str, ComponentInfo]:
        """Get all component definitions"""
        return self._components.copy()
    
    def get_all_services(self) -> Dict[str, ServiceInfo]:
        """Get all service definitions"""
        return self._services.copy()
    
    def get_components_by_category(self, category: str) -> List[ComponentInfo]:
        """Get all components in a specific category"""
        return [c for c in self._components.values() if c.category == category]
    
    def get_component_dependencies(self, component_id: str) -> List[str]:
        """Get dependencies for a component"""
        comp = self.get_component(component_id)
        return comp.dependencies if comp else []
    
    def get_startup_order(self) -> List[List[str]]:
        """Get components grouped by startup priority"""
        # Group by priority
        priority_groups: Dict[int, List[str]] = {}
        for comp_id, comp in self._components.items():
            priority = comp.startup_priority
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(comp_id)
            
        # Return sorted by priority
        return [priority_groups[p] for p in sorted(priority_groups.keys())]
    
    def get_component_ports(self) -> Dict[str, int]:
        """Get mapping of component IDs to ports"""
        return {comp_id: comp.port for comp_id, comp in self._components.items()}
    
    def get_component_by_port(self, port: int) -> Optional[ComponentInfo]:
        """Find component by port number"""
        for comp in self._components.values():
            if comp.port == port:
                return comp
        return None
    
    def validate_dependencies(self) -> List[str]:
        """Validate that all dependencies exist"""
        errors = []
        for comp_id, comp in self._components.items():
            for dep in comp.dependencies:
                if dep not in self._components:
                    errors.append(f"{comp_id} depends on unknown component: {dep}")
        return errors


# Global instance
_component_config: Optional[ComponentConfig] = None


def get_component_config() -> ComponentConfig:
    """Get the global component configuration instance"""
    global _component_config
    if _component_config is None:
        _component_config = ComponentConfig()
    return _component_config


# Convenience functions
def get_all_component_names() -> List[str]:
    """Get list of all component IDs"""
    return list(get_component_config().get_all_components().keys())


def get_component_info(component_id: str) -> Optional[ComponentInfo]:
    """Get information about a specific component"""
    return get_component_config().get_component(component_id)


def get_component_port(component_id: str) -> Optional[int]:
    """Get port for a specific component"""
    comp = get_component_info(component_id)
    return comp.port if comp else None


def get_startup_groups() -> List[List[str]]:
    """Get components grouped by startup priority"""
    return get_component_config().get_startup_order()


__all__ = [
    'ComponentInfo',
    'ServiceInfo',
    'ComponentConfig',
    'get_component_config',
    'get_all_component_names',
    'get_component_info',
    'get_component_port',
    'get_startup_groups'
]