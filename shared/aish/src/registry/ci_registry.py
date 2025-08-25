"""
Unified CI Registry for aish - File-based implementation
Manages all CI types (Greek Chorus, Terma terminals, Project CIs) in a single registry.
"""

# Import landmarks with fallback
try:
    from landmarks import (
        fuzzy_match,
        state_checkpoint
    )
except ImportError:
    def fuzzy_match(**kwargs):
        def decorator(func): return func
        return decorator
    def state_checkpoint(**kwargs):
        def decorator(func): return func
        return decorator

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
        'tekton-core': {
            'description': 'System orchestration and coordination',
            'message_endpoint': '/api/message',
            'message_format': 'json_simple'
        },
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
        'synthesis': {
            'description': 'Integration and synthesis',
            'message_endpoint': '/api/message',
            'message_format': 'json_simple'
        },
        'numa': {
            'description': 'Specialist orchestration and guidance',
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
        self._dirty = False  # Track if registry needs flushing
        
        # Use file-based storage
        from .file_registry import FileRegistry
        tekton_root = TektonEnviron.get('TEKTON_ROOT', '/tmp')
        self._file_registry = FileRegistry(tekton_root)
        
        # Load context state from file
        self._context_state = self._file_registry.get('context_state', {})
        
        # Component aliases
        self.ALIASES = {
            'tekton': 'tekton-core',
            # Add other aliases as needed
        }
        
        self._load_greek_chorus()
        self._load_terminals()
        self._load_projects()
        # self._load_tools()  # Removed - old CI tools infrastructure deprecated
        self._load_forwards()
        self._load_and_validate_wrapped_cis()  # Load and validate wrapped CIs
    
    def _save_context_state(self):
        """Save context state to file."""
        self._file_registry.update('context_state', self._context_state)
    
    def get_ai_port(self, component_name: str) -> int:
        """Calculate CI port based on component port and environment settings."""
        # Get base ports from environment
        component_port_base = int(TektonEnviron.get('TEKTON_PORT_BASE', '8000'))
        ai_port_base = int(TektonEnviron.get('TEKTON_AI_PORT_BASE', '45000'))
        
        # Get the component's actual endpoint from registry
        if component_name in self._registry:
            endpoint = self._registry[component_name].get('endpoint', '')
            if endpoint:
                # Extract port from endpoint like "http://localhost:8316"
                try:
                    component_port = int(endpoint.split(':')[-1])
                    offset = component_port - component_port_base
                    return ai_port_base + offset
                except:
                    pass
        
        # If we can't find it in registry, look up the actual environment variable
        component_upper = component_name.upper().replace('-', '_')
        ai_port_env = TektonEnviron.get(f'{component_upper}_AI_PORT')
        if ai_port_env:
            return int(ai_port_env)
        
        # Last resort - calculate from component port env var
        component_port_env = TektonEnviron.get(f'{component_upper}_PORT')
        if component_port_env:
            component_port = int(component_port_env)
            offset = component_port - component_port_base
            return ai_port_base + offset
        
        # If all else fails, raise an error instead of guessing
        raise ValueError(f"Cannot determine CI port for {component_name}")
    
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
            'tekton-core': tekton_url,
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
                if name == 'tekton-core':
                    endpoint = url_fn('tekton-core')
                else:
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
                        self._register_project_ci(project)
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
                                self._register_project_ci(project)
        except Exception:
            # Projects file might not exist yet
            pass
    
    @integration_point(
        title="CI Tools Loading",
        description="Loads CI coding tools (Claude Code, Cursor, etc.) from registry",
        target_component="CI Tools",
        protocol="Socket Bridge",
        data_flow="CI Tools Registry → registry entries with ports and capabilities",
        integration_date="2025-08-02"
    )
    def _load_tools(self):
        """Load CI tools from the CI tools registry."""
        try:
            # Import CI tools registry if available
            from shared.ci_tools import get_registry
            tools_registry = get_registry()
            
            # Get all registered tools
            tools = tools_registry.get_tools()
            
            for tool_name, tool_config in tools.items():
                # Check if tool is running
                status = tools_registry.get_tool_status(tool_name)
                
                self._registry[tool_name] = {
                    'name': tool_name,
                    'type': 'tool',
                    'endpoint': f"socket://localhost:{tool_config['port']}",
                    'port': tool_config['port'],
                    'description': tool_config['description'],
                    'message_endpoint': '/socket',
                    'message_format': 'json',
                    'executable': tool_config.get('executable'),
                    'capabilities': tool_config.get('capabilities', {}),
                    'running': status.get('running', False),
                    'pid': status.get('pid'),
                    'uptime': status.get('uptime')
                }
                
        except ImportError:
            # CI tools module not available yet
            pass
        except Exception as e:
            # Log but don't fail
            import logging
            logging.debug(f"Failed to load CI tools: {e}")
    
    def _load_forwards(self):
        """Load forwarding configurations."""
        # Load saved forwards from file
        forwards = self._file_registry.get('forwards', {})
        for ci_name, forward_config in forwards.items():
            if ci_name in self._registry:
                self._registry[ci_name].update(forward_config)
    
    def _load_and_validate_wrapped_cis(self):
        """Load wrapped CIs from persistent storage and validate they're still running."""
        wrapped_file = os.path.join(self._file_registry.registry_dir, 'wrapped_cis.json')
        if os.path.exists(wrapped_file):
            try:
                with open(wrapped_file, 'r') as f:
                    wrapped_cis = json.load(f)
                    valid_cis = {}
                    
                    for name, ci_info in wrapped_cis.items():
                        # Check if process is still running
                        pid = ci_info.get('pid')
                        socket_path = ci_info.get('socket')
                        
                        # Validate PID is alive
                        is_alive = False
                        if pid:
                            try:
                                os.kill(pid, 0)  # Signal 0 just checks if process exists
                                is_alive = True
                            except (ProcessLookupError, PermissionError):
                                is_alive = False
                        
                        # Only keep if both PID is alive AND socket exists
                        if is_alive and socket_path and os.path.exists(socket_path):
                            self._registry[name] = ci_info
                            valid_cis[name] = ci_info
                            # Comment out to reduce noise
                            # print(f"[Registry] Recovered CI terminal: {name} (PID {pid})")
                        else:
                            print(f"[Registry] Removing dead CI terminal: {name} (PID {pid}, alive={is_alive})")
                    
                    # Write back only valid CIs
                    if valid_cis != wrapped_cis:
                        with open(wrapped_file, 'w') as f:
                            json.dump(valid_cis, f, indent=2)
                        print(f"[Registry] Cleaned up {len(wrapped_cis) - len(valid_cis)} dead entries")
                            
            except Exception as e:
                print(f"[Registry] Failed to load wrapped CIs: {e}")
    
    # Registry Access Methods
    
    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered CIs."""
        return self._registry.copy()
    
    def get_by_type(self, ci_type: str) -> List[Dict[str, Any]]:
        """Get all CIs of a specific type."""
        return [ci for ci in self._registry.values() if ci.get('type') == ci_type]
    
    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get CI by name, handling both base names and -ci suffixes."""
        # Handle aliases first
        name = self.ALIASES.get(name, name)
        
        # Check direct match first (case-insensitive for terminals, tools, etc.)
        # Search through registry keys with case-insensitive comparison
        for key, value in self._registry.items():
            if key.lower() == name.lower():
                return value
        
        # Handle base names and -ci suffix for Greek Chorus
        base_name = name[:-3] if name.endswith('-ci') else name
        
        if base_name in self.GREEK_CHORUS:
            # Build the CI data with dynamic port
            ci_data = self.GREEK_CHORUS[base_name].copy()
            ci_data['name'] = name  # Preserve the requested name
            ci_data['base_name'] = base_name
            ci_data['type'] = 'ai_specialist'
            
            # Calculate the CI port dynamically
            ai_port = self.get_ai_port(base_name)
            ci_data['endpoint'] = f"http://localhost:{ai_port}"
            ci_data['port'] = ai_port
            
            return ci_data
        
        # Check if it's a CI tool
        return self._check_ci_tools(name)
    
    def _check_ci_tools(self, name: str) -> Optional[Dict[str, Any]]:
        """Check if name refers to a CI tool."""
        # Reload tools in case they've changed
        self._load_tools()
        return self._registry.get(name.lower())
    
    def exists(self, name: str) -> bool:
        """Check if a CI exists."""
        # Use get_by_name which handles all the lookup logic
        return self.get_by_name(name) is not None
    
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
    
    def set_next_prompt(self, ci_name: str, prompt: Optional[str]) -> bool:
        """Apollo sets next_prompt for sunset/sunrise orchestration.
        Thread-safe using file registry locking.
        
        Args:
            ci_name: CI name
            prompt: Either SUNSET_PROTOCOL message or --append-system-prompt command
        """
        ci_name = ci_name.lower()
        if ci_name not in self._registry:
            return False
        
        if ci_name not in self._context_state:
            self._context_state[ci_name] = {}
        
        self._context_state[ci_name]['next_prompt'] = prompt
        self._save_context_state()  # Uses FileRegistry with locks
        return True

    def get_next_prompt(self, ci_name: str) -> Optional[str]:
        """Get the next_prompt for a CI.
        Thread-safe read through file registry.
        """
        ci_name = ci_name.lower()
        if ci_name not in self._context_state:
            return None
        return self._context_state[ci_name].get('next_prompt')

    def clear_next_prompt(self, ci_name: str) -> bool:
        """Clear next_prompt after use.
        Thread-safe using file registry locking.
        """
        ci_name = ci_name.lower()
        if ci_name not in self._context_state:
            return False
        
        if 'next_prompt' in self._context_state[ci_name]:
            self._context_state[ci_name]['next_prompt'] = None
            self._save_context_state()
            return True
        return False

    def set_sunrise_context(self, ci_name: str, context: str) -> bool:
        """Store CI's sunset summary for sunrise use.
        Thread-safe using file registry locking.
        """
        ci_name = ci_name.lower()
        if ci_name not in self._registry:
            return False
        
        if ci_name not in self._context_state:
            self._context_state[ci_name] = {}
        
        self._context_state[ci_name]['sunrise_context'] = context
        self._save_context_state()
        return True

    def get_sunrise_context(self, ci_name: str) -> Optional[str]:
        """Get the sunrise_context for a CI.
        Thread-safe read through file registry.
        """
        ci_name = ci_name.lower()
        if ci_name not in self._context_state:
            return None
        return self._context_state[ci_name].get('sunrise_context')

    def clear_sunrise_context(self, ci_name: str) -> bool:
        """Clear sunrise_context after use.
        Thread-safe using file registry locking.
        """
        ci_name = ci_name.lower()
        if ci_name not in self._context_state:
            return False
        
        if 'sunrise_context' in self._context_state[ci_name]:
            self._context_state[ci_name]['sunrise_context'] = None
            self._save_context_state()
            return True
        return False
    
    @integration_point(
        title="AI Exchange Storage",
        description="Stores complete user message and CI response exchanges",
        target_component="AI Specialists",
        protocol="Socket JSON messages",
        data_flow="AI Specialist → update_ci_last_output → registry.json",
        integration_date="2025-07-30"
    )
    def update_ci_last_output(self, ci_name: str, output: Union[str, Dict]) -> bool:
        """Store the CI's output when turn completes.
        
        NEW: Auto-detect sunset responses and copy to sunrise_context.
        
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
        
        # NEW: Auto-detect sunset response
        if self._is_sunset_response(output):
            # Auto-copy to sunrise_context
            if isinstance(output, dict):
                content = output.get('content', '')
            else:
                content = str(output)
            self._context_state[ci_name]['sunrise_context'] = content
        
        self._save_context_state()
        return True
    
    def _is_sunset_response(self, output: Union[str, Dict]) -> bool:
        """Detect if output is a sunset protocol response.
        
        Looks for sunset indicators in the content.
        """
        # Extract content string
        if isinstance(output, dict):
            content = str(output.get('content', ''))
            # Also check if user message had SUNSET_PROTOCOL
            user_msg = str(output.get('user_message', ''))
            if 'SUNSET_PROTOCOL' in user_msg:
                return True
        else:
            content = str(output)
        
        # Check for sunset response indicators
        content_lower = content.lower()
        sunset_indicators = [
            'current context',
            'working on',
            'key decisions',
            'next steps',
            'current approach',
            'emotional state',
            'task trajectory'
        ]
        
        # Count matches
        matches = sum(1 for indicator in sunset_indicators if indicator in content_lower)
        
        # If 3+ indicators present, likely a sunset response
        return matches >= 3
    
    def get_ci_context_state(self, ci_name: str) -> Optional[Dict[str, Any]]:
        """Get the complete context state for a CI."""
        ci_name = ci_name.lower()
        return self._context_state.get(ci_name)
    
    def register_wrapped_ci(self, ci_info: Dict) -> bool:
        """Register a wrapped CI and persist immediately."""
        name = ci_info.get('name')
        if not name:
            return False
        
        # Add to registry
        self._registry[name] = ci_info
        
        # Mark registry as needing flush
        self._dirty = True
        
        # Flush immediately for wrapped CIs since they're created/destroyed less frequently
        self.flush_wrapped_cis()
        
        return True
    
    def unregister_wrapped_ci(self, name: str) -> bool:
        """Unregister a wrapped CI and persist immediately."""
        if name not in self._registry:
            return False
        
        # Remove from registry
        del self._registry[name]
        
        # Mark registry as needing flush
        self._dirty = True
        
        # Flush immediately for wrapped CIs since they're created/destroyed less frequently
        self.flush_wrapped_cis()
        
        return True
    
    def flush_wrapped_cis(self) -> bool:
        """Flush wrapped CIs to disk if dirty."""
        if not self._dirty:
            return True  # Nothing to flush
        
        try:
            # Collect only wrapped CIs
            wrapped_cis = {
                name: info for name, info in self._registry.items()
                if info.get('type') in ['ci_terminal', 'ci_tool']
            }
            
            # Write to file
            wrapped_file = os.path.join(self._file_registry.registry_dir, 'wrapped_cis.json')
            os.makedirs(os.path.dirname(wrapped_file), exist_ok=True)
            
            with open(wrapped_file, 'w') as f:
                json.dump(wrapped_cis, f, indent=2)
            
            self._dirty = False
            print(f"[Registry] Flushed {len(wrapped_cis)} wrapped CIs to disk")
            return True
            
        except Exception as e:
            print(f"[Registry] Failed to flush wrapped CIs: {e}")
            return False
    
    def set_forward_state(self, ci_name: str, model: str, args: str = "") -> bool:
        """Set forward state for a CI (persistent)."""
        forward_file = os.path.join(self._file_registry.registry_dir, 'forward_states.json')
        
        # Load existing states
        states = {}
        if os.path.exists(forward_file):
            try:
                with open(forward_file, 'r') as f:
                    states = json.load(f)
            except:
                states = {}
        
        # Set new state
        states[ci_name] = {
            'model': model,
            'args': args,
            'started': datetime.now().isoformat(),
            'active': True
        }
        
        # Save states
        try:
            os.makedirs(os.path.dirname(forward_file), exist_ok=True)
            with open(forward_file, 'w') as f:
                json.dump(states, f, indent=2)
            
            # Also update in-memory registry if CI exists
            if ci_name in self._registry:
                self._registry[ci_name]['forwarded_to'] = model
                self._registry[ci_name]['forward_args'] = args
            
            print(f"[Registry] Set forward state: {ci_name} → {model}")
            return True
        except Exception as e:
            print(f"[Registry] Failed to set forward state: {e}")
            return False
    
    def clear_forward_state(self, ci_name: str) -> bool:
        """Clear forward state for a CI."""
        forward_file = os.path.join(self._file_registry.registry_dir, 'forward_states.json')
        
        # Load existing states
        states = {}
        if os.path.exists(forward_file):
            try:
                with open(forward_file, 'r') as f:
                    states = json.load(f)
            except:
                return False
        
        # Remove state
        if ci_name in states:
            del states[ci_name]
            
            # Save states
            try:
                with open(forward_file, 'w') as f:
                    json.dump(states, f, indent=2)
                
                # Also update in-memory registry
                if ci_name in self._registry:
                    self._registry[ci_name].pop('forwarded_to', None)
                    self._registry[ci_name].pop('forward_args', None)
                
                print(f"[Registry] Cleared forward state for {ci_name}")
                return True
            except Exception as e:
                print(f"[Registry] Failed to clear forward state: {e}")
                return False
        
        return True
    
    @fuzzy_match(
        title="CI Forward State Resolution",
        description="Fuzzy matching for CI names to handle -ai/-ci suffix variations",
        algorithm="exact_then_prefix_with_suffix_handling",
        examples=["ergon->ergon", "ergon-ci->ergon", "ergon-ai->ergon"],
        priority="exact > base_name_match > prefix_match"
    )
    def get_forward_state(self, ci_name: str) -> Optional[Dict[str, Any]]:
        """Get forward state for a CI with fuzzy matching.
        
        Matching rules:
        1. Exact match always wins
        2. Prefix matches allowed only if target >= search length  
        3. Never match shorter strings
        4. Return shortest match that's >= search length
        """
        forward_file = os.path.join(self._file_registry.registry_dir, 'forward_states.json')
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(forward_file), exist_ok=True)
        
        # Create empty file if it doesn't exist
        if not os.path.exists(forward_file):
            try:
                with open(forward_file, 'w') as f:
                    json.dump({}, f)
            except Exception as e:
                print(f"[Registry] Failed to create forward_states.json: {e}")
        
        # Now read the file
        if os.path.exists(forward_file):
            try:
                with open(forward_file, 'r') as f:
                    states = json.load(f)
                    
                    # First try exact match
                    if ci_name in states:
                        return states[ci_name]
                    
                    # Fuzzy matching with special CI suffix handling
                    search_len = len(ci_name)
                    candidates = []
                    
                    # Special handling for -ci suffix
                    # If searching for 'ergon-ci', also consider 'ergon'
                    # If searching for 'ergon', also consider 'ergon-ci'
                    base_name = ci_name.replace('-ci', '')
                    
                    for key in states.keys():
                        key_len = len(key)
                        key_base = key.replace('-ci', '')
                        
                        # Rule 1: Exact base name match (ergon == ergon, ergon-ci == ergon)
                        if base_name == key_base:
                            candidates.append((key, key_len))
                        # Rule 2: Prefix match only if key >= search length
                        elif key_len >= search_len and key.startswith(ci_name):
                            candidates.append((key, key_len))
                        # Rule 3: Search is prefix of key
                        elif key_len >= search_len and ci_name.startswith(key):
                            candidates.append((key, key_len))
                    
                    # Return best match
                    if candidates:
                        # Prefer exact length, then shortest
                        candidates.sort(key=lambda x: (abs(x[1] - search_len), x[1]))
                        return states[candidates[0][0]]
                    
                    return None
            except:
                pass
        
        return None
    
    def list_forward_states(self) -> Dict[str, Dict[str, Any]]:
        """List all forward states."""
        forward_file = os.path.join(self._file_registry.registry_dir, 'forward_states.json')
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(forward_file), exist_ok=True)
        
        # Create empty file if it doesn't exist
        if not os.path.exists(forward_file):
            try:
                with open(forward_file, 'w') as f:
                    json.dump({}, f)
            except Exception as e:
                print(f"[Registry] Failed to create forward_states.json: {e}")
        
        # Now read the file
        if os.path.exists(forward_file):
            try:
                with open(forward_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {}
    
    def _allocate_project_port(self, project_name: str) -> int:
        """Allocate a dynamic port for a project CI using OS allocation."""
        # Use a persistent file to track allocated ports
        port_file = os.path.join(self._file_registry.registry_dir, 'project_ports.json')
        
        # Load existing allocations
        allocations = {}
        if os.path.exists(port_file):
            try:
                with open(port_file, 'r') as f:
                    allocations = json.load(f)
            except:
                allocations = {}
        
        # Check if this project already has a port
        if project_name in allocations:
            return allocations[project_name]
        
        # Let the OS allocate a dynamic port
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', 0))  # Bind to any available port
        port = sock.getsockname()[1]
        sock.close()
        
        # Save the allocation
        allocations[project_name] = port
        with open(port_file, 'w') as f:
            json.dump(allocations, f, indent=2)
        
        return port
    
    def _deallocate_project_port(self, project_name: str):
        """Release a project's allocated port."""
        port_file = os.path.join(self._file_registry.registry_dir, 'project_ports.json')
        
        if os.path.exists(port_file):
            try:
                with open(port_file, 'r') as f:
                    allocations = json.load(f)
                
                if project_name in allocations:
                    del allocations[project_name]
                    
                    with open(port_file, 'w') as f:
                        json.dump(allocations, f, indent=2)
            except:
                pass
    
    def _register_project_ci(self, project: Dict[str, Any]):
        """Register a project CI with dynamic port allocation."""
        project_name = project['name']
        
        # Special case: Tekton project uses numa
        if project_name.lower() == 'tekton':
            # Use numa as Tekton's CI
            ci_name = 'numa'
            # numa already exists in Greek Chorus, just mark it as Tekton's project CI
            if ci_name in self._registry:
                self._registry[ci_name]['is_project_ci'] = True
                self._registry[ci_name]['project'] = 'Tekton'
                self._registry[ci_name]['project_id'] = project['id']
            return
        
        # Regular projects get dynamic ports
        ci_name = f"{project_name.lower()}-ci"
        port = self._allocate_project_port(project_name)
        # For project CIs, the CI specialist runs directly on the allocated port
        # No need for separate ai_port
        
        self._registry[ci_name] = {
            'name': ci_name,
            'type': 'ai_specialist',  # Use ai_specialist for proper routing
            'port': port,
            'ai_port': port,  # Same as port for project CIs
            'endpoint': f'http://localhost:{port}',
            'description': f"Project AI: {project_name}",
            'message_endpoint': '/api/message',
            'message_format': 'json_simple',
            'project': project_name,
            'project_id': project['id'],
            'companion_intelligence': project['companion_intelligence'],
            'local_directory': project.get('local_directory'),
            'is_project_ci': True
        }
    
    def unregister_project_ci(self, project_name: str) -> bool:
        """Unregister a project CI and deallocate its port."""
        # Special case: Tekton uses numa, don't unregister numa
        if project_name.lower() == 'tekton':
            if 'numa' in self._registry:
                # Just remove project association
                self._registry['numa'].pop('is_project_ci', None)
                self._registry['numa'].pop('project', None) 
                self._registry['numa'].pop('project_id', None)
            return True
        
        ci_name = f"{project_name.lower()}-ci"
        if ci_name in self._registry:
            del self._registry[ci_name]
            self._deallocate_project_port(project_name)
            return True
        
        return False
    
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
        """Set up forwarding from an CI to a terminal."""
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
        
        # Show CI Tools (ci_tool type)
        ci_tool_items = []
        if 'ci_tool' in by_type:
            ci_tool_items.extend(by_type['ci_tool'])
        # Keep backwards compatibility temporarily
        if 'wrapped_ci' in by_type:
            for item in by_type['wrapped_ci']:
                # Assume wrapped_ci without -terminal suffix are tools
                if not item.get('capabilities') or 'pty_injection' not in item.get('capabilities', []):
                    ci_tool_items.append(item)
        
        if ci_tool_items:
            output.append("CI Tools:")
            output.append("-" * 60)
            sorted_tools = sorted(ci_tool_items, key=operator.itemgetter('name'))
            for item in sorted_tools:
                name = item['name']
                socket = item.get('socket', 'unknown')
                output.append(f"  {name:<20} socket:{socket}")
            output.append("")
        
        # Show CI Terminals (ci_terminal type)
        ci_terminal_items = []
        if 'ci_terminal' in by_type:
            ci_terminal_items.extend(by_type['ci_terminal'])
        # Keep backwards compatibility temporarily
        if 'wrapped_ci' in by_type:
            for item in by_type['wrapped_ci']:
                # Check for PTY injection capability
                if 'pty_injection' in item.get('capabilities', []):
                    ci_terminal_items.append(item)
        
        if ci_terminal_items:
            output.append("CI Terminals (PTY-wrapped):")
            output.append("-" * 60)
            sorted_terminals = sorted(ci_terminal_items, key=operator.itemgetter('name'))
            for item in sorted_terminals:
                name = item['name']
                socket = item.get('socket', 'unknown')
                pid = item.get('pid', 'unknown')
                output.append(f"  {name:<20} socket:{socket} (pid {pid})")
            output.append("")
        
        # Show Terminals (from terma)
        if 'terminal' in by_type:
            output.append("Terminals (terma):")
            output.append("-" * 60)
            terminal_cis = sorted(by_type['terminal'], key=operator.itemgetter('name'))
            for ci in terminal_cis:
                name = ci['name']
                pid = ci.get('pid', 'unknown')
                forward = f" → {ci['forward_to']}" if 'forward_to' in ci else ""
                json_mode = " [JSON]" if ci.get('forward_json') else ""
                output.append(f"  {name:<15} (pid {pid}){forward}{json_mode}")
            output.append("")
        
        # Show Project CIs (now shown as CI specialists with project info)
        project_cis = []
        if 'project' in by_type:
            project_cis.extend(by_type['project'])
        # Also include ai_specialist CIs that are project CIs
        if 'ai_specialist' in by_type:
            for ci in by_type['ai_specialist']:
                if ci.get('is_project_ci'):
                    project_cis.append(ci)
        # Include any CI marked as project CI (like numa)
        for ci_type in by_type:
            if ci_type not in ['project', 'ai_specialist']:
                for ci in by_type[ci_type]:
                    if ci.get('is_project_ci'):
                        project_cis.append(ci)
        
        if project_cis:
            output.append("Project CIs:")
            output.append("-" * 60)
            sorted_projects = sorted(project_cis, key=operator.itemgetter('name'))
            for ci in sorted_projects:
                name = ci['name']
                project = ci.get('project', 'unknown')
                port = ci.get('port', ci.get('endpoint', '').split(':')[-1].rstrip('/'))
                # Special case for numa/Tekton
                if name == 'numa' and project == 'Tekton':
                    display_name = 'numa (Tekton)'
                else:
                    display_name = name
                forward = f" → {ci['forward_to']}" if 'forward_to' in ci else ""
                json_mode = " [JSON]" if ci.get('forward_json') else ""
                output.append(f"  {display_name:<20} port:{port:<5} (project: {project}){forward}{json_mode}")
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
