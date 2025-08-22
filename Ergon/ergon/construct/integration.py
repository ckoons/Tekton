"""
Integration module for Ergon Construct system.

Wires together all components (engine, resolver, state, publisher)
to create the complete CI-first Construct system.
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Import all Construct components
from .engine import CompositionEngine
from .chat_handler import ConstructChatHandler

# Amy's components are now ready
from .resolver import ComponentResolver
from .state import WorkspaceState, WorkspaceStatus
from .publisher import CompositionPublisher

# Import dependencies
from ..registry.storage import RegistryStorage
from ..sandbox.runner import SandboxRunner

logger = logging.getLogger(__name__)


class ConstructSystem:
    """
    Main entry point for the Construct system.
    
    Integrates all components and provides unified interface
    for both CI (JSON) and human (text) interaction.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the integrated Construct system.
        
        Args:
            config: Optional configuration overrides
        """
        config = config or {}
        
        # Initialize shared dependencies
        self.registry = RegistryStorage()
        self.sandbox = SandboxRunner(self.registry)
        
        # Initialize Construct components - Amy's modules are ready!
        # Pass the same registry path to ensure consistency
        registry_path = self.registry.db_path
        self.resolver = ComponentResolver(registry_path)
        self.state = WorkspaceState(config.get('state_dir'))
        self.publisher = CompositionPublisher(
            registry_storage=self.registry,
            state_manager=self.state,
            resolver=self.resolver
        )
        
        # Initialize engine with all components
        self.engine = CompositionEngine(
            registry_storage=self.registry,
            sandbox_runner=self.sandbox
        )
        
        # Initialize chat handler with engine
        self.chat = ConstructChatHandler(self.engine)
        
        # Wire components together
        self._wire_components()
        
        logger.info("Construct system initialized")
    
    def _wire_components(self):
        """
        Wire components together for seamless integration.
        """
        # Amy's components are ready - wire them together!
        
        # Replace engine's in-memory storage with persistent state
        self.engine.state_manager = self.state
        
        # Use resolver for validation
        self.engine.resolver = self.resolver
        
        # Use publisher for Registry operations
        self.engine.publisher = self.publisher
        
        # Override engine methods to use integrated components
        self._patch_engine_methods()
        
        logger.info("Components wired: resolver, state, publisher → engine")
    
    def _patch_engine_methods(self):
        """
        Patch engine methods to use integrated components.
        
        This keeps the engine pure while adding persistence and intelligence.
        """
        # Save original methods
        original_compose = self.engine.compose
        original_validate_connections = self.engine._validate_connections
        original_publish = self.engine.publish
        
        # Enhanced compose with state persistence
        async def compose_with_state(request: Dict[str, Any]) -> Dict[str, Any]:
            # Get or create workspace in persistent state
            workspace_id = request.get('workspace_id')
            if not workspace_id:
                workspace = self.state.create_workspace(
                    ci_owner=request.get('sender_id', 'ergon-ci'),
                    name=request.get('name', 'New Composition')
                )
                workspace_id = workspace['workspace_id']
                request['workspace_id'] = workspace_id
            
            # Process with original method
            response = await original_compose(request)
            
            # Persist to state
            if response.get('status') == 'success':
                self.state.update_composition(
                    workspace_id,
                    request.get('components', []),
                    request.get('connections', []),
                    request.get('constraints', {}),
                    ci_id=request.get('sender_id', 'ergon-ci')
                )
            
            return response
        
        # Enhanced validation with resolver
        async def validate_with_resolver(components: list, connections: list) -> Dict[str, Any]:
            result = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'scores': {}
            }
            
            # First resolve all components
            comp_map = {}  # alias -> registry_id mapping
            for comp in components:
                registry_id = comp.get('registry_id')
                alias = comp.get('alias')
                if registry_id and alias:
                    comp_map[alias] = registry_id
                    # Resolve component to populate cache
                    await self.resolver.resolve_component(registry_id)
            
            # Use resolver for intelligent validation
            for conn in connections:
                from_alias, from_port = conn['from'].split('.')
                to_alias, to_port = conn['to'].split('.')
                
                from_id = comp_map.get(from_alias)
                to_id = comp_map.get(to_alias)
                
                if from_id and to_id:
                    # validate_connection returns tuple: (valid, reason, transform, score)
                    valid, reason, transform, score = self.resolver.validate_connection(
                        from_id, from_port,
                        to_id, to_port
                    )
                    
                    if not valid:
                        result['valid'] = False
                        result['errors'].append(reason)
                    
                    # Track compatibility scores
                    result['scores'][f"{conn['from']}->{conn['to']}"] = score
                    
                    # Add transform suggestions
                    if transform:
                        result['warnings'].append(
                            f"Connection {conn['from']} -> {conn['to']} needs transform: {transform}"
                        )
                        conn['transform'] = transform  # Add to connection for later use
                else:
                    result['errors'].append(f"Component not found for connection {conn['from']} -> {conn['to']}")
                    result['valid'] = False
            
            return result
        
        # Enhanced publish with lineage
        async def publish_with_lineage(request: Dict[str, Any]) -> Dict[str, Any]:
            workspace_id = request.get('workspace_id')
            metadata = request.get('metadata', {})
            options = request.get('options', {})
            
            # Use our publisher with full lineage tracking
            return await self.publisher.publish(
                workspace_id=workspace_id,
                name=metadata.get('name', 'Unnamed'),
                version=metadata.get('version', '1.0.0'),
                description=metadata.get('description', ''),
                tags=metadata.get('tags'),
                auto_test=options.get('auto_test', True),
                check_standards=options.get('check_standards', True),
                ci_id=request.get('sender_id', 'system')
            )
        
        # Apply patches
        self.engine.compose = compose_with_state
        self.engine._validate_connections = validate_with_resolver
        self.engine.publish = publish_with_lineage
    
    async def process(self, message: str, sender_id: str = 'unknown') -> str:
        """
        Main entry point for all Construct operations.
        
        Args:
            message: JSON (from CI) or text (from human)
            sender_id: Identifier of sender
            
        Returns:
            JSON response for CIs, natural text for humans
        """
        return await self.chat.process_message(message, sender_id)
    
    async def process_json(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Direct JSON interface for CIs.
        
        Args:
            request: JSON request following protocol
            
        Returns:
            JSON response
        """
        return await self.engine.process(request)
    
    def get_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get workspace state.
        
        Args:
            workspace_id: Workspace identifier
            
        Returns:
            Workspace state or None
        """
        # Use our state manager
        return self.state.load_workspace(workspace_id)
    
    def list_workspaces(self, ci_id: Optional[str] = None) -> list:
        """
        List workspaces, optionally filtered by CI.
        
        Args:
            ci_id: Optional CI identifier to filter
            
        Returns:
            List of workspace summaries
        """
        # Use our state manager
        return self.state.list_workspaces(ci_id=ci_id)
    
    async def suggest_components(self, requirements: str) -> Dict[str, Any]:
        """
        AI-powered component suggestions.
        
        Args:
            requirements: Natural language requirements
            
        Returns:
            Suggested components and composition
        """
        # Parse requirements to extract capabilities
        # This could be enhanced with Claude/GPT-4 integration
        capabilities = []
        if 'api' in requirements.lower():
            capabilities.append('api')
        if 'database' in requirements.lower() or 'storage' in requirements.lower():
            capabilities.append('storage')
        if 'auth' in requirements.lower():
            capabilities.append('authentication')
        
        # Find compatible components
        suggested_components = []
        for capability in capabilities:
            compatible = self.resolver.find_compatible_components(capability)
            if compatible:
                # Take first match
                registry_id = compatible[0]
                resolved = await self.resolver.resolve_component(registry_id)
                if resolved:
                    suggested_components.append({
                        'registry_id': registry_id,
                        'name': resolved.name,
                        'capability': capability
                    })
        
        # Suggest connections
        if len(suggested_components) > 1:
            component_ids = [c['registry_id'] for c in suggested_components]
            connections = self.resolver.suggest_connections(component_ids)
        else:
            connections = []
        
        return {
            'suggestions': suggested_components,
            'connections': connections,
            'reasoning': f'Found {len(suggested_components)} components matching capabilities: {capabilities}'
        }
    
    def get_protocol(self) -> Dict[str, Any]:
        """
        Get the Construct protocol definition.
        
        Returns:
            Protocol JSON
        """
        protocol_path = Path(__file__).parent / 'protocol.json'
        with open(protocol_path, 'r') as f:
            return json.load(f)


# Singleton instance for easy import
_construct_system = None

def get_construct_system() -> ConstructSystem:
    """
    Get or create the singleton Construct system.
    
    Returns:
        ConstructSystem instance
    """
    global _construct_system
    if _construct_system is None:
        _construct_system = ConstructSystem()
    return _construct_system