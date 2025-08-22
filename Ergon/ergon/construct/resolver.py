"""
Registry Component Resolver for Ergon Construct System.

Resolves Registry components, validates interfaces, and suggests connections.
Part of the CI-first Construct system designed for JSON-native interaction.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# Import landmarks
try:
    from landmarks import architecture_decision, integration_point, api_contract
except ImportError:
    def architecture_decision(**kwargs):
        def decorator(func): return func
        return decorator
    def integration_point(**kwargs):
        def decorator(func): return func
        return decorator
    def api_contract(**kwargs):
        def decorator(func): return func
        return decorator

# Import Registry storage
from ..registry.storage import RegistryStorage

logger = logging.getLogger(__name__)


@dataclass
class ComponentInterface:
    """Represents a component's input/output interface."""
    name: str
    type: str  # http, grpc, socket, file, event
    schema: Dict[str, Any]  # JSON schema or protocol definition
    direction: str  # input, output, bidirectional


@dataclass
class ResolvedComponent:
    """A Registry component with resolved metadata."""
    registry_id: str
    name: str
    version: str
    type: str
    interfaces: List[ComponentInterface]
    requirements: Dict[str, Any]
    capabilities: List[str]
    config_schema: Dict[str, Any]


@architecture_decision(
    title="Component Resolution Strategy",
    description="Resolver deeply understands component capabilities for intelligent composition",
    rationale="CI-first design requires the resolver to make smart decisions without human guidance",
    alternatives_considered=["Simple ID lookup", "Manual interface definition", "Type-only matching"],
    impacts=["composition_quality", "ci_autonomy", "error_prevention"],
    decided_by="Amy",
    decision_date="2025-08-22"
)
class ComponentResolver:
    """Resolves and validates Registry components for composition."""
    
    def __init__(self, registry_path: Optional[str] = None):
        """Initialize resolver with Registry connection."""
        # Use default Registry path if not provided
        if not registry_path:
            import os
            ergon_dir = Path(__file__).parent.parent
            registry_path = ergon_dir / "ergon_registry.db"
        
        self.storage = RegistryStorage(str(registry_path))
        self._interface_cache: Dict[str, List[ComponentInterface]] = {}
        logger.info(f"ComponentResolver initialized with registry at {registry_path}")
    
    @integration_point(
        title="Registry Component Resolution",
        description="Resolves component from Registry with full metadata",
        target_component="Registry",
        protocol="Direct DB access",
        data_flow="Registry ID → Component metadata → Interface extraction",
        integration_date="2025-08-22"
    )
    async def resolve_component(self, registry_id: str) -> Optional[ResolvedComponent]:
        """
        Resolve a component from Registry by ID.
        
        Args:
            registry_id: Registry entry UUID
            
        Returns:
            ResolvedComponent with full metadata, or None if not found
        """
        try:
            # Fetch from Registry
            entry = self.storage.retrieve(registry_id)
            if not entry:
                logger.warning(f"Component {registry_id} not found in Registry")
                return None
            
            # Ensure entry is a dict
            if not isinstance(entry, dict):
                logger.warning(f"Component {registry_id} returned non-dict: {type(entry)}")
                return None
            
            # Extract interfaces from content
            interfaces = self._extract_interfaces(entry)
            
            # Build resolved component
            resolved = ResolvedComponent(
                registry_id=registry_id,
                name=entry.get('name', 'Unknown'),
                version=entry.get('version', '1.0.0'),
                type=entry.get('type', 'solution'),
                interfaces=interfaces,
                requirements=self._extract_requirements(entry),
                capabilities=self._extract_capabilities(entry),
                config_schema=self._extract_config_schema(entry)
            )
            
            # Cache interfaces for connection validation
            self._interface_cache[registry_id] = interfaces
            
            logger.info(f"Resolved component {resolved.name} v{resolved.version}")
            return resolved
            
        except Exception as e:
            logger.error(f"Failed to resolve component {registry_id}: {e}")
            return None
    
    def _extract_interfaces(self, entry: Dict[str, Any]) -> List[ComponentInterface]:
        """Extract component interfaces from Registry entry."""
        interfaces = []
        # Handle both dict and string entries
        if not isinstance(entry, dict):
            logger.warning(f"Entry is not a dict: {type(entry)}")
            return [ComponentInterface(
                name='default',
                type='http',
                schema={},
                direction='bidirectional'
            )]
        content = entry.get('content', {})
        
        # Check for explicit interface definitions
        if 'interfaces' in content:
            ifaces = content['interfaces']
            
            # Handle list format (new style)
            if isinstance(ifaces, list):
                for iface in ifaces:
                    interfaces.append(ComponentInterface(
                        name=iface.get('name', 'default'),
                        type=iface.get('type', 'http'),
                        schema=iface.get('schema', {}),
                        direction=iface.get('direction', 'bidirectional')
                    ))
            
            # Handle dict format with inputs/outputs (old style)
            elif isinstance(ifaces, dict):
                # Process inputs
                for inp in ifaces.get('inputs', []):
                    interfaces.append(ComponentInterface(
                        name=inp.get('name', 'input'),
                        type=inp.get('type', 'http'),
                        schema=inp.get('schema', {}),
                        direction='input'
                    ))
                # Process outputs
                for out in ifaces.get('outputs', []):
                    interfaces.append(ComponentInterface(
                        name=out.get('name', 'output'),
                        type=out.get('type', 'http'),
                        schema=out.get('schema', {}),
                        direction='output'
                    ))
        
        # Infer interfaces from component type
        elif entry.get('type') == 'container':
            # Containers typically expose HTTP endpoints
            interfaces.append(ComponentInterface(
                name='main',
                type='http',
                schema={'port': 8080, 'protocol': 'http'},
                direction='input'
            ))
        elif entry.get('type') == 'tool':
            # Tools might have CLI interfaces
            interfaces.append(ComponentInterface(
                name='cli',
                type='file',
                schema={'input': 'stdin', 'output': 'stdout'},
                direction='bidirectional'
            ))
        
        # Default interface if none found
        if not interfaces:
            interfaces.append(ComponentInterface(
                name='default',
                type='http',
                schema={},
                direction='bidirectional'
            ))
        
        return interfaces
    
    def _extract_requirements(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Extract resource requirements from Registry entry."""
        if not isinstance(entry, dict):
            return {'memory': '512MB', 'cpu': '0.5', 'disk': '1GB'}
        content = entry.get('content', {})
        return content.get('requirements', {
            'memory': '512MB',
            'cpu': '0.5',
            'disk': '1GB'
        })
    
    def _extract_capabilities(self, entry: Dict[str, Any]) -> List[str]:
        """Extract component capabilities."""
        if not isinstance(entry, dict):
            return []
        # From tags and content
        capabilities = entry.get('tags', []).copy()
        content = entry.get('content', {})
        
        if 'capabilities' in content:
            capabilities.extend(content['capabilities'])
        
        # Infer from type
        comp_type = entry.get('type', 'solution')
        if comp_type not in capabilities:
            capabilities.append(comp_type)
        
        return list(set(capabilities))  # Unique
    
    def _extract_config_schema(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Extract configuration schema."""
        if not isinstance(entry, dict):
            return {'type': 'object', 'properties': {}, 'required': []}
        content = entry.get('content', {})
        return content.get('config_schema', {
            'type': 'object',
            'properties': {},
            'required': []
        })
    
    @api_contract(
        title="Connection Validation",
        description="Validates if two components can be connected",
        endpoint="validate_connection",
        method="internal",
        request_schema={"from": "component.port", "to": "component.port"},
        response_schema={"valid": "bool", "reason": "str", "transform": "object"},
        performance_requirements="<10ms for validation"
    )
    def validate_connection(
        self, 
        from_component: str, 
        from_port: str,
        to_component: str,
        to_port: str
    ) -> Tuple[bool, str, Optional[Dict], float]:
        """
        Validate if two component ports can be connected with scoring.
        
        Args:
            from_component: Source component Registry ID
            from_port: Source port name
            to_component: Target component Registry ID
            to_port: Target port name
            
        Returns:
            Tuple of (valid, reason, transform_needed, compatibility_score)
        """
        # Get interfaces from cache
        from_interfaces = self._interface_cache.get(from_component, [])
        to_interfaces = self._interface_cache.get(to_component, [])
        
        # Find specific interfaces
        from_iface = next((i for i in from_interfaces if i.name == from_port), None)
        to_iface = next((i for i in to_interfaces if i.name == to_port), None)
        
        if not from_iface:
            return False, f"Port {from_port} not found on source component", None, 0.0
        if not to_iface:
            return False, f"Port {to_port} not found on target component", None, 0.0
        
        # Check compatibility
        if from_iface.direction == 'input':
            return False, f"Cannot connect from input port {from_port}", None, 0.0
        if to_iface.direction == 'output':
            return False, f"Cannot connect to output port {to_port}", None, 0.0
        
        # Check type compatibility and calculate score
        score = 0.0
        if from_iface.type == to_iface.type:
            # Perfect match
            score = 1.0
            return True, "Connection valid - perfect match", None, score
        else:
            # Check for compatible transforms
            transform_scores = {
                ('http', 'grpc'): 0.9,      # Easy protocol conversion
                ('grpc', 'http'): 0.9,
                ('file', 'socket'): 0.8,    # Stream adaptation
                ('socket', 'file'): 0.8,
                ('http', 'socket'): 0.7,    # More complex conversion
                ('json', 'xml'): 0.85,       # Format conversion
                ('xml', 'json'): 0.85,
            }
            
            type_pair = (from_iface.type, to_iface.type)
            if type_pair in transform_scores:
                score = transform_scores[type_pair]
                transform = {
                    'type': 'protocol_adapter',
                    'from': from_iface.type,
                    'to': to_iface.type,
                    'confidence': score
                }
                return True, f"Connection valid with transform (score: {score})", transform, score
            else:
                # Incompatible
                return False, f"Incompatible types: {from_iface.type} → {to_iface.type}", None, 0.0
    
    def suggest_connections(
        self, 
        components: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Suggest valid connections between components.
        
        Args:
            components: List of Registry IDs
            
        Returns:
            List of suggested connections
        """
        suggestions = []
        
        # Check all pairs
        for i, comp1 in enumerate(components):
            for comp2 in components[i+1:]:
                # Get interfaces
                ifaces1 = self._interface_cache.get(comp1, [])
                ifaces2 = self._interface_cache.get(comp2, [])
                
                # Find compatible connections
                for if1 in ifaces1:
                    if if1.direction in ['output', 'bidirectional']:
                        for if2 in ifaces2:
                            if if2.direction in ['input', 'bidirectional']:
                                valid, reason, transform, score = self.validate_connection(
                                    comp1, if1.name, comp2, if2.name
                                )
                                if valid:
                                    suggestions.append({
                                        'from': f"{comp1}.{if1.name}",
                                        'to': f"{comp2}.{if2.name}",
                                        'confidence': score,
                                        'reason': reason,
                                        'transform': transform
                                    })
        
        return suggestions
    
    def find_compatible_components(
        self, 
        capability: str,
        exclude: Optional[List[str]] = None
    ) -> List[str]:
        """
        Find Registry components with a specific capability.
        
        Args:
            capability: Required capability
            exclude: Registry IDs to exclude
            
        Returns:
            List of compatible Registry IDs
        """
        exclude = exclude or []
        compatible = []
        
        # Search Registry
        results = self.storage.search(limit=100)
        for entry in results:
            if entry['id'] in exclude:
                continue
            
            # Check capabilities
            caps = self._extract_capabilities(entry)
            if capability in caps:
                compatible.append(entry['id'])
        
        return compatible