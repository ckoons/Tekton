"""
Unified CI Registry for aish - File-based implementation
Manages all CI types (Greek Chorus, Terma terminals, Project CIs) in a single registry.
"""

import os
import sys
import operator
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from shared.env import TektonEnviron
from shared.urls import (
    tekton_url, apollo_url, athena_url, engram_url, ergon_url, harmonia_url,
    hermes_url, metis_url, noesis_url, numa_url, penia_url, prometheus_url,
    rhetor_url, sophia_url, synthesis_url, telos_url, terma_url, hephaestus_url
)

# Try to import landmarks if available
try:
    from landmarks import (
        architecture_decision,
        api_contract,
        integration_point,
        performance_boundary,
        state_checkpoint,
        danger_zone
    )
except ImportError:
    # Create no-op decorators if landmarks not available
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def api_contract(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def danger_zone(**kwargs):
        def decorator(func):
            return func
        return decorator


# Architecture decision marker for the CI Registry pattern
@architecture_decision(
    title="Unified CI Registry Architecture",
    description="Central registry for all Conversational Interfaces (CIs) in Tekton",
    rationale="Provides single source of truth for CI discovery, context state, and Apollo-Rhetor coordination",
    alternatives_considered=["Distributed registries per component", "Database-backed registry", "In-memory only"],
    impacts=["apollo_coordination", "rhetor_context_injection", "ai_specialist_integration"],
    decided_by="Casey",
    decision_date="2025-07-30"
)
class _CIRegistryArchitecture:
    """Marker class for CI Registry architecture decision"""
    pass


@state_checkpoint(
    title="CI Registry File-Based State",
    description="File-based persistence for CI metadata and context state",
    state_type="persistent",
    persistence=True,
    consistency_requirements="Thread-safe file locking prevents concurrent write corruption",
    recovery_strategy="Reload from registry.json on startup"
)
class CIRegistry:
    """Unified CI Registry with file-based persistence."""
    
    # Static registry of all Greek Chorus CIs
    GREEK_CHORUS = {
        'apollo': {
            'description': 'Attention and prediction',
            'message_endpoint': '/api/message',
            'message_format': 'json_simple'
        },
        'athena': {
            'description': 'Strategy and wisdom',
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
        
        # Use file-based storage
        from .file_registry import FileRegistry
        tekton_root = TektonEnviron.get('TEKTON_ROOT', '/tmp')
        self._file_registry = FileRegistry(tekton_root)
        
        # Load context state from file
        self._context_state = self._file_registry.get('context_state', {})
        
        self._load_greek_chorus()
        self._load_terminals()
        self._load_projects()
        self._load_forwards()
    
    def _save_context_state(self):
        """Save context state to file."""
        self._file_registry.update('context_state', self._context_state)
    
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
                'message_endpoint': info['message_endpoint'],
                'message_format': info['message_format']
            }
    
    @integration_point(
        title="Terma Terminal Discovery",
        description="Discovers running Terma terminals from Terma API",
        target_component="Terma",
        protocol="HTTP API",
        data_flow="Terma /api/terminals → registry entries with PID and attributes",
        integration_date="2025-01-25"
    )
    def _load_terminals(self):
        """Load Terma terminals from Terma API."""
        try:
            # Get terminals from Terma API
            response = requests.get(terma_url('/api/terminals'), timeout=2)
            if response.status_code == 200:
                terminals = response.json()
                for terminal in terminals:
                    name = terminal.get('name', '').lower()
                    if name:
                        self._registry[name] = {
                            'name': name,
                            'type': 'terminal',
                            'endpoint': terma_url(),
                            'description': f"Terminal: {terminal.get('app', 'unknown')} (pid {terminal.get('pid', '?')})",
                            'message_endpoint': '/api/route',
                            'message_format': 'terma_route',
                            'pid': terminal.get('pid'),
                            'app': terminal.get('app', 'unknown'),
                            'status': terminal.get('status', 'unknown'),
                            'purpose': terminal.get('purpose', ''),
                            'working_dir': terminal.get('working_dir', ''),
                            'launched_at': terminal.get('launched_at')
                        }
        except Exception as e:
            # Terma might not be running, that's ok
            pass
    
    def _load_projects(self):
        """Load project CIs from Tekton projects."""
        # First try TektonCore API
        try:
            response = requests.get(tekton_url('tekton_core', '/api/projects/list'), timeout=2)
            if response.status_code == 200:
                projects = response.json()
                for project in projects:
                    if project.get('companion_intelligence'):
                        # Create CI entry for project's companion AI
                        ci_name = f"{project['name'].lower()}-ai"
                        self._registry[ci_name] = {
                            'name': ci_name,
                            'type': 'project',
                            'endpoint': tekton_url('tekton_core'),
                            'description': f"Project AI: {project['name']}",
                            'message_endpoint': '/api/message',
                            'message_format': 'json_simple',
                            'project': project['name'],
                            'project_id': project['id'],
                            'companion_intelligence': project['companion_intelligence'],
                            'local_directory': project.get('local_directory')
                        }
                return
        except Exception:
            # TektonCore might not be running, fall back to file
            pass
        
        # Fallback to reading projects.json directly
        try:
            tekton_root = TektonEnviron.get('TEKTON_ROOT')
            if tekton_root:
                projects_file = Path(tekton_root) / '.tekton' / 'projects' / 'projects.json'
                if projects_file.exists():
                    with open(projects_file, 'r') as f:
                        data = json.load(f)
                        for project in data.get('projects', []):
                            if project.get('companion_intelligence'):
                                # Create CI entry for project's companion AI
                                ci_name = f"{project['name'].lower()}-ai"
                                self._registry[ci_name] = {
                                    'name': ci_name,
                                    'type': 'project',
                                    'endpoint': tekton_url('tekton_core'),
                                    'description': f"Project AI: {project['name']}",
                                    'message_endpoint': '/api/message',
                                    'message_format': 'json_simple',
                                    'project': project['name'],
                                    'project_id': project['id'],
                                    'companion_intelligence': project['companion_intelligence'],
                                    'local_directory': project.get('local_directory')
                                }
        except Exception:
            # Projects file might not exist yet
            pass
    
    def _load_forwards(self):
        """Load forwarding configurations."""
        # Load saved forwards from file
        forwards = self._file_registry.get('forwards', {})
        for ci_name, forward_config in forwards.items():
            if ci_name in self._registry:
                self._registry[ci_name].update(forward_config)
    
    # Registry Access Methods
    
    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered CIs."""
        return self._registry.copy()
    
    def get_by_type(self, ci_type: str) -> List[Dict[str, Any]]:
        """Get all CIs of a specific type."""
        return [ci for ci in self._registry.values() if ci.get('type') == ci_type]
    
    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific CI by name."""
        return self._registry.get(name.lower())
    
    def exists(self, name: str) -> bool:
        """Check if a CI exists."""
        return name.lower() in self._registry
    
    def get_types(self) -> List[str]:
        """Get all unique CI types."""
        return list(set(ci.get('type', 'unknown') for ci in self._registry.values()))
    
    # Apollo-Rhetor Coordination Methods
    
    @state_checkpoint(
        title="Apollo-Rhetor Context Coordination",
        description="File-based state for Apollo planning and Rhetor execution of CI prompts",
        state_type="coordination",
        persistence=True,
        consistency_requirements="File locking ensures consistency",
        recovery_strategy="State persists in registry.json"
    )
    def set_ci_staged_context_prompt(self, ci_name: str, prompt_data: Optional[List[Dict]]) -> bool:
        """Apollo sets staged prompts for future scenarios."""
        ci_name = ci_name.lower()
        if ci_name not in self._registry:
            return False
            
        if ci_name not in self._context_state:
            self._context_state[ci_name] = {}
            
        self._context_state[ci_name]['staged_context_prompt'] = prompt_data
        self._save_context_state()
        return True
    
    def set_ci_next_context_prompt(self, ci_name: str, prompt_data: Optional[List[Dict]]) -> bool:
        """Rhetor or direct set of next prompt to inject."""
        ci_name = ci_name.lower()
        if ci_name not in self._registry:
            return False
            
        if ci_name not in self._context_state:
            self._context_state[ci_name] = {}
            
        self._context_state[ci_name]['next_context_prompt'] = prompt_data
        self._save_context_state()
        return True
    
    def get_ci_last_output(self, ci_name: str) -> Optional[Union[str, Dict]]:
        """Get the complete output from CI's last turn."""
        ci_name = ci_name.lower()
        if ci_name not in self._context_state:
            return None
            
        return self._context_state[ci_name].get('last_output')
    
    @integration_point(
        title="AI Exchange Storage",
        description="Stores complete user message and AI response exchanges",
        target_component="AI Specialists",
        protocol="Socket JSON messages",
        data_flow="AI Specialist → update_ci_last_output → registry.json",
        integration_date="2025-07-30"
    )
    def update_ci_last_output(self, ci_name: str, output: Union[str, Dict]) -> bool:
        """Store the CI's output when turn completes.
        
        Args:
            ci_name: Name of the CI
            output: Either a string (backward compatible) or dict with full exchange
        """
        ci_name = ci_name.lower()
        if ci_name not in self._registry:
            return False
            
        if ci_name not in self._context_state:
            self._context_state[ci_name] = {}
            
        self._context_state[ci_name]['last_output'] = output
        self._save_context_state()
        return True
    
    def get_ci_context_state(self, ci_name: str) -> Optional[Dict[str, Any]]:
        """Get the complete context state for a CI."""
        ci_name = ci_name.lower()
        return self._context_state.get(ci_name)
    
    def get_all_context_states(self) -> Dict[str, Dict[str, Any]]:
        """Get context states for all CIs."""
        # Reload context state from file to get latest
        self._context_state = self._file_registry.get('context_state', {})
        return self._context_state.copy()
    
    def set_ci_next_from_staged(self, ci_name: str) -> bool:
        """Move staged_context_prompt -> next_context_prompt and clear staged."""
        ci_name = ci_name.lower()
        if ci_name not in self._context_state:
            return False
            
        staged = self._context_state[ci_name].get('staged_context_prompt')
        if staged is None:
            return False
            
        # Move staged to next and clear staged
        self._context_state[ci_name]['next_context_prompt'] = staged
        self._context_state[ci_name]['staged_context_prompt'] = None
        self._save_context_state()
        return True
    
    # Terminal forwarding methods
    
    def set_forward(self, ai_name: str, terminal_name: str, json_mode: bool = False) -> bool:
        """Set up forwarding from an AI to a terminal."""
        ai_name = ai_name.lower()
        terminal_name = terminal_name.lower()
        
        if ai_name not in self._registry or terminal_name not in self._registry:
            return False
            
        self._registry[ai_name]['forward_to'] = terminal_name
        self._registry[ai_name]['forward_json'] = json_mode
        
        # Save to file
        forwards = self._file_registry.get('forwards', {})
        forwards[ai_name] = {
            'forward_to': terminal_name,
            'forward_json': json_mode
        }
        self._file_registry.update('forwards', forwards)
        return True
    
    def remove_forward(self, ai_name: str) -> bool:
        """Remove forwarding for an AI."""
        ai_name = ai_name.lower()
        if ai_name not in self._registry:
            return False
            
        self._registry[ai_name].pop('forward_to', None)
        self._registry[ai_name].pop('forward_json', None)
        
        # Remove from file
        forwards = self._file_registry.get('forwards', {})
        forwards.pop(ai_name, None)
        self._file_registry.update('forwards', forwards)
        return True
    
    def get_forwards(self) -> Dict[str, Dict[str, Any]]:
        """Get all active forwards."""
        return {
            name: {
                'forward_to': ci['forward_to'],
                'json_mode': ci.get('forward_json', False)
            }
            for name, ci in self._registry.items()
            if 'forward_to' in ci
        }
    
    def format_list(self) -> str:
        """Format registry contents for display."""
        if not self._registry:
            return "No CIs registered"
        
        # Group by type
        by_type = {}
        for ci in self._registry.values():
            ci_type = ci.get('type', 'unknown')
            if ci_type not in by_type:
                by_type[ci_type] = []
            by_type[ci_type].append(ci)
        
        output = []
        output.append("Unified CI Registry")
        output.append("=" * 60)
        output.append("")
        
        # Show Greek Chorus CIs
        if 'greek' in by_type:
            output.append("Greek Chorus CIs:")
            output.append("-" * 60)
            greek_cis = sorted(by_type['greek'], key=operator.itemgetter('name'))
            for ci in greek_cis:
                name = ci['name']
                desc = ci['description']
                endpoint = ci['endpoint']
                forward = f" → {ci['forward_to']}" if 'forward_to' in ci else ""
                json_mode = " [JSON]" if ci.get('forward_json') else ""
                output.append(f"  {name:<15} {desc:<30} {endpoint}{forward}{json_mode}")
            output.append("")
        
        # Show Terminal CIs
        if 'terminal' in by_type:
            output.append("Terminal CIs:")
            output.append("-" * 60)
            terminal_cis = sorted(by_type['terminal'], key=operator.itemgetter('name'))
            for ci in terminal_cis:
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
            project_cis = sorted(by_type['project'], key=operator.itemgetter('name'))
            for ci in project_cis:
                name = ci['name']
                project = ci.get('project', 'unknown')
                forward = f" → {ci['forward_to']}" if 'forward_to' in ci else ""
                json_mode = " [JSON]" if ci.get('forward_json') else ""
                output.append(f"  {name:<15} (project: {project}){forward}{json_mode}")
            output.append("")
        
        return "\n".join(output)


# Singleton instance
_registry_instance = None

def get_registry() -> CIRegistry:
    """Get the singleton CI registry instance."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = CIRegistry()
    return _registry_instance