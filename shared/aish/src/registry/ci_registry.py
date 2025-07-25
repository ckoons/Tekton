"""
Unified CI Registry for aish
Manages all CI types (Greek Chorus, Terma terminals, Project CIs) in a single registry.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from shared.env import TektonEnviron
from shared.urls import tekton_url

# Import landmarks with fallback
try:
    from landmarks import (
        architecture_decision,
        state_checkpoint,
        integration_point,
        performance_boundary
    )
except ImportError:
    # Define no-op decorators when landmarks not available
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator


@architecture_decision(
    title="Unified CI Registry Architecture",
    description="Single registry manages all CI types (Greek Chorus, Terma, Projects)",
    rationale="Eliminates three separate lists, enables federation, simplifies discovery",
    alternatives_considered=["Separate registries per type", "Hard-coded CI lists", "Service mesh discovery"],
    impacts=["ci_discovery", "federation_readiness", "dynamic_routing"],
    decided_by="Casey",
    decision_date="2025-01-25"
)
@state_checkpoint(
    title="CI Registry State",
    description="In-memory registry of all available CIs with their configuration",
    state_type="registry",
    persistence=False,
    consistency_requirements="Refresh on demand, tolerates stale data",
    recovery_strategy="Rebuild from sources on restart"
)
class CIRegistry:
    """Unified registry for all CI types in Tekton."""
    
    # Greek Chorus CIs with their standard ports and messaging configuration
    GREEK_CHORUS = {
        'numa': {
            'port': 8316, 
            'description': 'Companion AI for Tekton Project',
            'message_endpoint': '/rhetor/socket',  # Through Rhetor for now
            'message_format': 'rhetor_socket'
        },
        'prometheus': {
            'port': 8306, 
            'description': 'Forward planning and foresight',
            'message_endpoint': '/rhetor/socket',
            'message_format': 'rhetor_socket'
        },
        'athena': {
            'port': 8305, 
            'description': 'Strategic wisdom and decision making',
            'message_endpoint': '/rhetor/socket',
            'message_format': 'rhetor_socket'
        },
        'synthesis': {
            'port': 8309, 
            'description': 'Integration and coordination',
            'message_endpoint': '/rhetor/socket',
            'message_format': 'rhetor_socket'
        },
        'apollo': {
            'port': 8312, 
            'description': 'Predictive intelligence and attention',
            'message_endpoint': '/rhetor/socket',
            'message_format': 'rhetor_socket'
        },
        'rhetor': {
            'port': 8303, 
            'description': 'Communication and prompt optimization',
            'message_endpoint': '/api/message',  # Direct to Rhetor
            'message_format': 'json_simple'
        },
        'metis': {
            'port': 8311, 
            'description': 'Analysis and insight',
            'message_endpoint': '/rhetor/socket',
            'message_format': 'rhetor_socket'
        },
        'harmonia': {
            'port': 8307, 
            'description': 'Balance and system harmony',
            'message_endpoint': '/rhetor/socket',
            'message_format': 'rhetor_socket'
        },
        'noesis': {
            'port': 8315, 
            'description': 'Understanding and comprehension',
            'message_endpoint': '/rhetor/socket',
            'message_format': 'rhetor_socket'
        },
        'engram': {
            'port': 8300, 
            'description': 'Memory and persistence',
            'message_endpoint': '/rhetor/socket',
            'message_format': 'rhetor_socket'
        },
        'penia': {
            'port': 8313, 
            'description': 'Resource management',
            'message_endpoint': '/rhetor/socket',
            'message_format': 'rhetor_socket'
        },
        'hermes': {
            'port': 8301, 
            'description': 'Messaging and communication',
            'message_endpoint': '/rhetor/socket',
            'message_format': 'rhetor_socket'
        },
        'ergon': {
            'port': 8302, 
            'description': 'Work execution and tools',
            'message_endpoint': '/rhetor/socket',
            'message_format': 'rhetor_socket'
        },
        'sophia': {
            'port': 8314, 
            'description': 'Wisdom and knowledge',
            'message_endpoint': '/rhetor/socket',
            'message_format': 'rhetor_socket'
        },
        'telos': {
            'port': 8308, 
            'description': 'Purpose and completion',
            'message_endpoint': '/rhetor/socket',
            'message_format': 'rhetor_socket'
        },
        'terma': {
            'port': 8304, 
            'description': 'Terminal management',
            'message_endpoint': '/api/message',
            'message_format': 'json_simple'
        },
        'hephaestus': {
            'port': 8080, 
            'description': 'User interface',
            'message_endpoint': '/api/message',
            'message_format': 'json_simple'
        },
    }
    
    def __init__(self):
        """Initialize the unified CI registry."""
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._load_greek_chorus()
        self._load_terminals()
        self._load_projects()
        self._load_forwards()
    
    @integration_point(
        title="Greek Chorus CI Loading",
        description="Loads all Greek Chorus AIs from static configuration",
        target_component="Greek Chorus AIs",
        protocol="Static Configuration",
        data_flow="GREEK_CHORUS dict → registry entries with ports and endpoints",
        integration_date="2025-01-25"
    )
    def _load_greek_chorus(self):
        """Load Greek Chorus CIs into registry."""
        for name, info in self.GREEK_CHORUS.items():
            self._registry[name] = {
                'name': name,
                'port': info['port'],
                'type': 'greek',
                'host': 'localhost',
                'endpoint': f"http://localhost:{info['port']}",
                'description': info['description'],
                'message_endpoint': info.get('message_endpoint', '/rhetor/socket'),
                'message_format': info.get('message_format', 'rhetor_socket'),
                'created': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat()
            }
    
    @integration_point(
        title="Terma Terminal Discovery",
        description="Dynamically discovers active terminals from Terma registry",
        target_component="Terma",
        protocol="HTTP GET /api/terminals",
        data_flow="Terma API → terminal list → registry entries with routing info",
        integration_date="2025-01-25"
    )
    def _load_terminals(self):
        """Load active Terma terminals from the terminal registry."""
        try:
            # Get terminal registry from Terma
            terma_url = tekton_url('terma', '/api/terminals')
            import urllib.request
            import urllib.error
            
            req = urllib.request.Request(terma_url)
            with urllib.request.urlopen(req, timeout=2) as response:
                terminals = json.loads(response.read().decode())
                
            for terminal in terminals:
                name = terminal.get('name', '').lower()
                if name:
                    self._registry[name] = {
                        'name': name,
                        'port': terminal.get('port', 0),
                        'type': 'terminal',
                        'host': 'localhost',
                        'endpoint': f"http://localhost:{terminal.get('port', 0)}",
                        'message_endpoint': '/api/mcp/v2/terminals/route-message',
                        'message_format': 'terma_route',
                        'pid': terminal.get('pid'),
                        'session_id': terminal.get('session_id'),
                        'created': terminal.get('created', datetime.now().isoformat()),
                        'last_seen': datetime.now().isoformat()
                    }
        except Exception:
            # If Terma isn't available, that's OK
            pass
    
    @integration_point(
        title="Project CI Discovery",
        description="Loads project-specific CIs from Tekton project registry",
        target_component="Project Registry",
        protocol="File-based JSON",
        data_flow="registry.json → project CIs → registry entries",
        integration_date="2025-01-25"
    )
    def _load_projects(self):
        """Load project CIs from the project registry."""
        try:
            tekton_root = Path(TektonEnviron.get('TEKTON_ROOT', ''))
            project_file = tekton_root / '.tekton' / 'project' / 'registry.json'
            
            if project_file.exists():
                with open(project_file, 'r') as f:
                    projects = json.load(f)
                    
                for project_name, project_info in projects.items():
                    # Add project CI if it has one
                    if 'ci' in project_info and project_info['ci']:
                        ci_name = project_info['ci'].lower()
                        self._registry[ci_name] = {
                            'name': ci_name,
                            'port': project_info.get('port', 0),
                            'type': 'project',
                            'host': 'localhost',
                            'endpoint': f"http://localhost:{project_info.get('port', 0)}",
                            'message_endpoint': '/api/message',  # Assume standard endpoint
                            'message_format': 'json_simple',
                            'project': project_name,
                            'created': project_info.get('created', datetime.now().isoformat()),
                            'last_seen': datetime.now().isoformat()
                        }
        except Exception:
            # If project registry isn't available, that's OK
            pass
    
    def _load_forwards(self):
        """Load forwarding information and add to CI entries."""
        try:
            from forwarding.forwarding_registry import ForwardingRegistry
            registry = ForwardingRegistry()
            forwards = registry.list_forwards()
            
            # Add forward_to information to CIs
            for source, target_info in forwards.items():
                if source in self._registry:
                    self._registry[source]['forward_to'] = target_info.get('terminal')
                    self._registry[source]['forward_json'] = target_info.get('json_mode', False)
        except Exception:
            # If forwarding registry isn't available, that's OK
            pass
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all CIs in the registry."""
        return list(self._registry.values())
    
    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific CI by name."""
        return self._registry.get(name.lower())
    
    def get_by_type(self, ci_type: str) -> List[Dict[str, Any]]:
        """Get all CIs of a specific type."""
        ci_type = ci_type.lower()
        if ci_type == 'greek':
            ci_type = 'greek'
        elif ci_type == 'terminal':
            ci_type = 'terminal'
        elif ci_type == 'project':
            ci_type = 'project'
        elif ci_type == 'forward':
            # Special case: CIs that have forwarding set up
            return [ci for ci in self._registry.values() if 'forward_to' in ci]
        elif ci_type == 'local':
            return [ci for ci in self._registry.values() if ci.get('host') == 'localhost']
        elif ci_type == 'remote':
            return [ci for ci in self._registry.values() if ci.get('host') != 'localhost']
        else:
            return []
        
        return [ci for ci in self._registry.values() if ci.get('type') == ci_type]
    
    def get_by_purpose(self, purpose: str) -> List[Dict[str, Any]]:
        """Get all CIs with a specific purpose (requires querying each CI)."""
        # This would need to query each CI for its current purpose
        # For now, return empty list as this is a future enhancement
        return []
    
    @performance_boundary(
        title="Registry Refresh",
        description="Rebuilds entire CI registry from all sources",
        sla="<100ms total refresh time",
        optimization_notes="Parallel loading could improve performance",
        measured_impact="Enables dynamic CI discovery without restart"
    )
    def refresh(self):
        """Refresh the registry with latest information."""
        self._registry.clear()
        self._load_greek_chorus()
        self._load_terminals()
        self._load_projects()
        self._load_forwards()
    
    def to_json(self) -> str:
        """Return the registry as JSON."""
        return json.dumps(self.get_all(), indent=2)
    
    def format_text_output(self, cis: Optional[List[Dict[str, Any]]] = None) -> str:
        """Format CIs for text display."""
        if cis is None:
            cis = self.get_all()
        
        if not cis:
            return "No CIs found"
        
        # Group by type
        by_type = {}
        for ci in cis:
            ci_type = ci.get('type', 'unknown')
            if ci_type not in by_type:
                by_type[ci_type] = []
            by_type[ci_type].append(ci)
        
        output = []
        
        # Show Greek Chorus first
        if 'greek' in by_type:
            output.append("Greek Chorus AIs:")
            output.append("-" * 60)
            for ci in sorted(by_type['greek'], key=lambda x: x['name']):
                name = ci['name']
                port = ci['port']
                desc = ci.get('description', '')
                forward = f" → {ci['forward_to']}" if 'forward_to' in ci else ""
                json_mode = " [JSON]" if ci.get('forward_json') else ""
                output.append(f"  {name:<15} (port {port:<5}){forward}{json_mode}")
                if desc:
                    output.append(f"    {desc}")
            output.append("")
        
        # Show Terminals
        if 'terminal' in by_type:
            output.append("Active Terminals:")
            output.append("-" * 60)
            for ci in sorted(by_type['terminal'], key=lambda x: x['name']):
                name = ci['name']
                pid = ci.get('pid', 'unknown')
                forward = f" → {ci['forward_to']}" if 'forward_to' in ci else ""
                json_mode = " [JSON]" if ci.get('forward_json') else ""
                output.append(f"  {name:<15} (pid {pid}){forward}{json_mode}")
            output.append("")
        
        # Show Project CIs
        if 'project' in by_type:
            output.append("Project CIs:")
            output.append("-" * 60)
            for ci in sorted(by_type['project'], key=lambda x: x['name']):
                name = ci['name']
                project = ci.get('project', 'unknown')
                forward = f" → {ci['forward_to']}" if 'forward_to' in ci else ""
                json_mode = " [JSON]" if ci.get('forward_json') else ""
                output.append(f"  {name:<15} (project: {project}){forward}{json_mode}")
            output.append("")
        
        return "\n".join(output)


# Singleton instance
_registry = None

def get_registry() -> CIRegistry:
    """Get or create the singleton CI registry."""
    global _registry
    if _registry is None:
        _registry = CIRegistry()
    return _registry