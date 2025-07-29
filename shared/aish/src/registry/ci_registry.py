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
from shared.urls import (
    tekton_url, apollo_url, athena_url, engram_url, ergon_url, harmonia_url,
    hermes_url, metis_url, noesis_url, numa_url, penia_url, prometheus_url,
    rhetor_url, sophia_url, synthesis_url, telos_url, terma_url, hephaestus_url
)

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
    
    # Greek Chorus CIs with their messaging configuration
    GREEK_CHORUS = {
        'numa': {
            'description': 'Companion AI for Tekton Project',
            'message_endpoint': '/api/message',
            'message_format': 'json_simple'
        },
        'prometheus': {
            'description': 'Forward planning and foresight',
            'message_endpoint': '/api/message',
            'message_format': 'json_simple'
        },
        'athena': {
            'description': 'Strategic wisdom and decision making',
            'message_endpoint': '/api/message',
            'message_format': 'json_simple'
        },
        'synthesis': {
            'description': 'Integration and coordination',
            'message_endpoint': '/api/message',
            'message_format': 'json_simple'
        },
        'apollo': {
            'description': 'Predictive intelligence and attention',
            'message_endpoint': '/api/message',
            'message_format': 'json_simple'
        },
        'rhetor': {
            'description': 'Communication and prompt optimization',
            'message_endpoint': '/api/message',
            'message_format': 'json_simple'
        },
        'metis': {
            'description': 'Analysis and insight',
            'message_endpoint': '/api/message',
            'message_format': 'json_simple'
        },
        'harmonia': {
            'description': 'Balance and system harmony',
            'message_endpoint': '/api/message',
            'message_format': 'json_simple'
        },
        'noesis': {
            'description': 'Understanding and comprehension',
            'message_endpoint': '/api/message',
            'message_format': 'json_simple'
        },
        'engram': {
            'description': 'Memory and persistence',
            'message_endpoint': '/api/message',
            'message_format': 'json_simple'
        },
        'penia': {
            'description': 'Resource management',
            'message_endpoint': '/api/message',
            'message_format': 'json_simple'
        },
        'hermes': {
            'description': 'Messaging and communication',
            'message_endpoint': '/api/message',
            'message_format': 'json_simple'
        },
        'ergon': {
            'description': 'Work execution and tools',
            'message_endpoint': '/api/message',
            'message_format': 'json_simple'
        },
        'sophia': {
            'description': 'Wisdom and knowledge',
            'message_endpoint': '/api/message',
            'message_format': 'json_simple'
        },
        'telos': {
            'description': 'Purpose and completion',
            'message_endpoint': '/api/message',
            'message_format': 'json_simple'
        },
        'terma': {
            'description': 'Terminal management',
            'message_endpoint': '/api/message',
            'message_format': 'json_simple'
        },
        'hephaestus': {
            'description': 'User interface',
            'message_endpoint': '/api/message',
            'message_format': 'json_simple'
        },
    }
    
    def __init__(self):
        """Initialize the unified CI registry."""
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._context_state: Dict[str, Dict[str, Any]] = {}  # Apollo-Rhetor coordination state
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
        # Map component names to their URL functions
        url_functions = {
            'apollo': apollo_url,
            'athena': athena_url,
            'engram': engram_url,
            'ergon': ergon_url,
            'harmonia': harmonia_url,
            'hermes': hermes_url,
            'metis': metis_url,
            'noesis': noesis_url,
            'numa': numa_url,
            'penia': penia_url,
            'prometheus': prometheus_url,
            'rhetor': rhetor_url,
            'sophia': sophia_url,
            'synthesis': synthesis_url,
            'telos': telos_url,
            'terma': terma_url,
            'hephaestus': hephaestus_url
        }
        
        for name, info in self.GREEK_CHORUS.items():
            # Get the URL function for this component
            url_fn = url_functions.get(name)
            if url_fn:
                endpoint = url_fn()
            else:
                # Fallback to tekton_url if specific function not found
                endpoint = tekton_url(name)
            
            self._registry[name] = {
                'name': name,
                'type': 'greek',
                'endpoint': endpoint,
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
                endpoint = ci.get('endpoint', '')
                # Extract port from endpoint for display
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(endpoint)
                    port = parsed.port or 80
                except:
                    port = 'unknown'
                desc = ci.get('description', '')
                forward = f" → {ci['forward_to']}" if 'forward_to' in ci else ""
                json_mode = " [JSON]" if ci.get('forward_json') else ""
                output.append(f"  {name:<15} (port {port}){forward}{json_mode}")
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
    
    # Apollo-Rhetor Coordination Methods
    @state_checkpoint(
        title="Apollo-Rhetor Context Coordination",
        description="In-memory state for Apollo planning and Rhetor execution of CI prompts",
        state_type="coordination",
        persistence=False,
        consistency_requirements="Real-time coordination, no persistence needed",
        recovery_strategy="State cleared on restart"
    )
    def set_ci_staged_context_prompt(self, ci_name: str, prompt_data: Optional[List[Dict]]) -> bool:
        """
        Apollo sets staged prompts for future scenarios.
        
        Args:
            ci_name: Name of the CI
            prompt_data: List of dicts with prompt data, or None to clear
            
        Returns:
            bool: True if successful, False if CI not found
        """
        ci_name = ci_name.lower()
        if ci_name not in self._registry:
            return False
            
        if ci_name not in self._context_state:
            self._context_state[ci_name] = {}
            
        self._context_state[ci_name]['staged_context_prompt'] = prompt_data
        return True
    
    def set_ci_next_context_prompt(self, ci_name: str, prompt_data: Optional[List[Dict]]) -> bool:
        """
        Rhetor or direct set of next prompt to inject.
        
        Args:
            ci_name: Name of the CI
            prompt_data: List of dicts with prompt data, or None to clear
            
        Returns:
            bool: True if successful, False if CI not found
        """
        ci_name = ci_name.lower()
        if ci_name not in self._registry:
            return False
            
        if ci_name not in self._context_state:
            self._context_state[ci_name] = {}
            
        self._context_state[ci_name]['next_context_prompt'] = prompt_data
        return True
    
    def get_ci_last_output(self, ci_name: str) -> Optional[str]:
        """
        Get the complete output from CI's last turn.
        
        Args:
            ci_name: Name of the CI
            
        Returns:
            Optional[str]: Last output string (could be text or JSON), or None
        """
        ci_name = ci_name.lower()
        if ci_name not in self._context_state:
            return None
            
        return self._context_state[ci_name].get('last_output')
    
    def set_ci_next_from_staged(self, ci_name: str) -> bool:
        """
        Move staged_context_prompt -> next_context_prompt and clear staged.
        This is Rhetor's main action to promote Apollo's plan.
        
        Args:
            ci_name: Name of the CI
            
        Returns:
            bool: True if successful, False if CI not found or no staged prompt
        """
        ci_name = ci_name.lower()
        if ci_name not in self._registry:
            return False
            
        if ci_name not in self._context_state:
            return False
            
        staged = self._context_state[ci_name].get('staged_context_prompt')
        if staged is None:
            return False
            
        # Move staged to next and clear staged
        self._context_state[ci_name]['next_context_prompt'] = staged
        self._context_state[ci_name]['staged_context_prompt'] = None
        return True
    
    def update_ci_last_output(self, ci_name: str, output: str) -> bool:
        """
        Store the CI's output when turn completes.
        
        Args:
            ci_name: Name of the CI
            output: Complete output string from the CI's turn
            
        Returns:
            bool: True if successful, False if CI not found
        """
        ci_name = ci_name.lower()
        if ci_name not in self._registry:
            return False
            
        if ci_name not in self._context_state:
            self._context_state[ci_name] = {}
            
        self._context_state[ci_name]['last_output'] = output
        return True
    
    def get_ci_context_state(self, ci_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the complete context state for a CI (for debugging/monitoring).
        
        Args:
            ci_name: Name of the CI
            
        Returns:
            Optional[Dict]: Complete context state or None
        """
        ci_name = ci_name.lower()
        return self._context_state.get(ci_name)
    
    def get_all_context_states(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all CI context states (for Apollo/Rhetor global view).
        
        Returns:
            Dict: All context states keyed by CI name
        """
        return self._context_state.copy()


# Singleton instance
_registry = None

def get_registry() -> CIRegistry:
    """Get or create the singleton CI registry."""
    global _registry
    if _registry is None:
        _registry = CIRegistry()
    return _registry