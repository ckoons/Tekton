"""
Pure JSON composition engine for Ergon Construct.

This is the CI-native engine that processes all composition operations
as pure data transformations. No UI dependencies, just JSON in/out.
"""

import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class WorkspaceStatus(Enum):
    """Workspace status states"""
    DRAFT = "draft"
    COMPOSING = "composing"
    VALIDATING = "validating"
    TESTING = "testing"
    READY = "ready"
    PUBLISHED = "published"


class CompositionEngine:
    """
    Pure JSON composition engine for CI-first operations.
    
    All methods accept and return JSON-serializable dictionaries.
    This enables direct CI communication without UI coupling.
    """
    
    def __init__(self, registry_storage=None, sandbox_runner=None):
        """
        Initialize engine with optional dependencies.
        
        Args:
            registry_storage: Registry for component lookup
            sandbox_runner: Sandbox for testing compositions
        """
        self.workspaces = {}  # In-memory workspace storage
        self.registry = registry_storage
        self.sandbox = sandbox_runner
        
        # Load protocol definition
        with open('ergon/construct/protocol.json', 'r') as f:
            self.protocol = json.load(f)
    
    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for all operations.
        
        Args:
            request: JSON request following protocol.json spec
            
        Returns:
            JSON response following protocol.json spec
        """
        try:
            # Validate request has required action
            if 'action' not in request:
                return self._error_response("COMP001", "Missing 'action' field")
            
            action = request['action']
            
            # Route to appropriate handler
            if action == 'compose':
                return await self.compose(request)
            elif action == 'validate':
                return await self.validate(request)
            elif action == 'test':
                return await self.test(request)
            elif action == 'publish':
                return await self.publish(request)
            elif action == 'get_state':
                return await self.get_state(request)
            elif action == 'collaborate':
                return await self.handle_collaboration(request)
            else:
                return self._error_response("COMP006", f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Engine error: {e}")
            return self._error_response("COMP999", str(e))
    
    async def compose(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or modify a composition.
        
        Pure data transformation - no UI updates.
        """
        # Extract components and connections
        components = request.get('components', [])
        connections = request.get('connections', [])
        constraints = request.get('constraints', {})
        workspace_id = request.get('workspace_id', str(uuid.uuid4()))
        
        # Create or update workspace
        if workspace_id not in self.workspaces:
            self.workspaces[workspace_id] = self._create_workspace(workspace_id)
        
        workspace = self.workspaces[workspace_id]
        
        # Update composition
        workspace['composition'] = {
            'components': components,
            'connections': connections,
            'constraints': constraints
        }
        workspace['status'] = WorkspaceStatus.COMPOSING.value
        workspace['updated_at'] = datetime.utcnow().isoformat()
        
        # Validate connections
        validation = await self._validate_connections(components, connections)
        
        return {
            'status': 'success',
            'workspace_id': workspace_id,
            'validation': validation,
            'warnings': validation.get('warnings', []),
            'next_steps': ['validate', 'test', 'add_components']
        }
    
    async def validate(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a composition without executing.
        """
        workspace_id = request.get('workspace_id')
        if not workspace_id or workspace_id not in self.workspaces:
            return self._error_response("COMP007", "Workspace not found")
        
        workspace = self.workspaces[workspace_id]
        checks = request.get('checks', ['connections', 'dependencies', 'standards'])
        mode = request.get('mode', 'strict')
        
        # Run validation checks
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        composition = workspace.get('composition', {})
        
        # Check connections
        if 'connections' in checks:
            conn_result = await self._validate_connections(
                composition.get('components', []),
                composition.get('connections', [])
            )
            if not conn_result['valid']:
                results['valid'] = False
                results['errors'].extend(conn_result.get('errors', []))
        
        # Check dependencies
        if 'dependencies' in checks:
            dep_result = await self._check_dependencies(composition)
            if dep_result.get('conflicts'):
                results['warnings'].extend(dep_result['conflicts'])
        
        # Check standards (if registry available)
        if 'standards' in checks and self.registry:
            std_result = await self._check_standards(composition)
            if not std_result.get('compliant'):
                if mode == 'strict':
                    results['valid'] = False
                results['warnings'].append("Standards non-compliance detected")
        
        # Update workspace
        workspace['validation_results'] = results
        workspace['status'] = WorkspaceStatus.VALIDATING.value
        
        return results
    
    async def test(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test composition in sandbox.
        """
        workspace_id = request.get('workspace_id')
        if not workspace_id or workspace_id not in self.workspaces:
            return self._error_response("COMP007", "Workspace not found")
        
        if not self.sandbox:
            return self._error_response("COMP008", "Sandbox not available")
        
        workspace = self.workspaces[workspace_id]
        sandbox_config = request.get('sandbox_config', {})
        assertions = request.get('assertions', [])
        
        # Create test solution from composition
        test_solution = await self._create_test_solution(workspace['composition'])
        
        # Store in registry temporarily
        solution_id = str(uuid.uuid4())
        # ... store logic ...
        
        # Run in sandbox
        sandbox_id = await self.sandbox.test_solution(solution_id, sandbox_config)
        
        # Update workspace
        workspace['status'] = WorkspaceStatus.TESTING.value
        workspace['test_results'] = {
            'sandbox_id': sandbox_id,
            'status': 'running',
            'started_at': datetime.utcnow().isoformat()
        }
        
        return {
            'sandbox_id': sandbox_id,
            'status': 'running',
            'results': None,
            'logs': None
        }
    
    async def publish(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish composition to Registry.
        """
        workspace_id = request.get('workspace_id')
        if not workspace_id or workspace_id not in self.workspaces:
            return self._error_response("COMP007", "Workspace not found")
        
        if not self.registry:
            return self._error_response("COMP009", "Registry not available")
        
        workspace = self.workspaces[workspace_id]
        metadata = request.get('metadata', {})
        options = request.get('options', {})
        
        # Validate before publishing
        if options.get('auto_test', True):
            validation = await self.validate({
                'workspace_id': workspace_id,
                'checks': ['connections', 'dependencies', 'standards']
            })
            if not validation['valid']:
                return self._error_response("COMP010", "Validation failed")
        
        # Create Registry entry
        registry_entry = {
            'type': 'solution',
            'name': metadata.get('name', 'Composed Solution'),
            'version': metadata.get('version', '1.0.0'),
            'content': {
                'description': metadata.get('description', ''),
                'composition': workspace['composition'],
                'tags': metadata.get('tags', []),
                'created_by': 'construct'
            },
            'lineage': workspace.get('lineage', [])
        }
        
        # Store in Registry
        registry_id = self.registry.store(registry_entry)
        
        # Update workspace
        workspace['status'] = WorkspaceStatus.PUBLISHED.value
        workspace['registry_id'] = registry_id
        
        return {
            'registry_id': registry_id,
            'published': True,
            'lineage': registry_entry['lineage'],
            'published_at': datetime.utcnow().isoformat()
        }
    
    async def get_state(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get current workspace state.
        """
        workspace_id = request.get('workspace_id')
        if not workspace_id or workspace_id not in self.workspaces:
            return self._error_response("COMP007", "Workspace not found")
        
        return {
            'status': 'success',
            'state': self.workspaces[workspace_id]
        }
    
    async def handle_collaboration(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle CI collaboration messages.
        """
        workspace_id = request.get('workspace_id')
        if not workspace_id or workspace_id not in self.workspaces:
            return self._error_response("COMP007", "Workspace not found")
        
        workspace = self.workspaces[workspace_id]
        collab_type = request.get('type')
        
        if collab_type == 'claim_task':
            task_type = request.get('task_type')
            ci_id = request.get('ci_id')
            
            # Track task assignment
            if 'tasks' not in workspace:
                workspace['tasks'] = {}
            workspace['tasks'][task_type] = {
                'assigned_to': ci_id,
                'claimed_at': datetime.utcnow().isoformat()
            }
            
            return {'status': 'success', 'task_claimed': True}
            
        elif collab_type == 'merge_work':
            changes = request.get('changes', {})
            ci_id = request.get('ci_id')
            
            # Merge changes into composition
            # ... merge logic ...
            
            return {'status': 'success', 'merged': True}
            
        else:
            return self._error_response("COMP011", f"Unknown collaboration type: {collab_type}")
    
    # Helper methods
    
    def _create_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """Create a new workspace"""
        return {
            'workspace_id': workspace_id,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'status': WorkspaceStatus.DRAFT.value,
            'ci_owner': 'ergon-ci',
            'collaborators': [],
            'composition': {
                'components': [],
                'connections': [],
                'constraints': {}
            },
            'validation_results': None,
            'test_results': None,
            'messages': []
        }
    
    async def _validate_connections(self, components: List, connections: List) -> Dict[str, Any]:
        """Validate component connections"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check each connection
        for conn in connections:
            from_port = conn.get('from')
            to_port = conn.get('to')
            
            # Basic validation (would be enhanced with Registry data)
            if not from_port or not to_port:
                result['valid'] = False
                result['errors'].append(f"Invalid connection: {conn}")
        
        return result
    
    async def _check_dependencies(self, composition: Dict) -> Dict[str, Any]:
        """Check for dependency conflicts"""
        return {
            'conflicts': [],
            'resolutions': []
        }
    
    async def _check_standards(self, composition: Dict) -> Dict[str, Any]:
        """Check standards compliance"""
        # Would integrate with standards engine
        return {
            'compliant': True,
            'score': 85,
            'issues': []
        }
    
    async def _create_test_solution(self, composition: Dict) -> Dict[str, Any]:
        """Create a test solution from composition"""
        # Generate executable code from composition
        return {
            'code': '# Generated composition code',
            'requirements': [],
            'run_command': ['python', 'composed.py']
        }
    
    def _error_response(self, code: str, message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            'status': 'error',
            'error': {
                'code': code,
                'message': message
            }
        }