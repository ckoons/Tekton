# @tekton-module: AI Registry Client for thread-safe socket management
# @tekton-depends: fcntl, json, socket, asyncio
# @tekton-provides: thread-safe-registry, port-allocation, socket-management
# @tekton-version: 2.0.0
# @tekton-modified: 2025-06-28 - Added thread-safe file locking for concurrent access
# @tekton-critical: true

"""
AI Registry Client for platform-wide AI socket management.

This client extends the existing AI socket registry to support
platform-wide AI specialists like Numa and Noesis.
"""
import os
import json
import socket
import logging
import asyncio
import fcntl
import time
from typing import Dict, Optional, Tuple, Any, List
from pathlib import Path
from datetime import datetime

# Import landmarks for architectural documentation
try:
    from landmarks import (
        architecture_decision,
        performance_boundary,
        api_contract,
        danger_zone,
        integration_point,
        state_checkpoint
    )
except ImportError:
    # If landmarks not available, create no-op decorators
    def architecture_decision(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def api_contract(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def danger_zone(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func):
            return func
        return decorator

logger = logging.getLogger(__name__)


# @tekton-class: Main registry client for AI socket management
# @tekton-singleton: false
# @tekton-lifecycle: component
# @tekton-thread-safe: true
@architecture_decision(
    title="Thread-safe AI Registry Architecture",
    rationale="Prevent race conditions in concurrent AI launches using file locking",
    alternatives_considered=["In-memory locks", "Database storage", "Redis"],
    impacts=["reliability", "concurrent_access", "file_io_overhead"]
)
@state_checkpoint(
    title="AI Registry State Management",
    state_type="persistent",
    persistence=True,
    consistency_requirements="Atomic file operations with fcntl locks"
)
class AIRegistryClient:
    """Client for managing platform-wide AI socket connections."""
    
    def __init__(self, registry_base_path: Optional[str] = None):
        """
        Initialize AI Registry Client.
        
        Args:
            registry_base_path: Base path for socket registry files.
                               Defaults to ~/.tekton/ai_registry/
        """
        if registry_base_path is None:
            registry_base_path = os.path.join(
                os.path.expanduser('~'), '.tekton', 'ai_registry'
            )
        
        self.registry_base = Path(registry_base_path)
        self.registry_base.mkdir(parents=True, exist_ok=True)
        
        # Platform AI registry file
        self.platform_registry_file = self.registry_base / 'platform_ai_registry.json'
        
        # Component AI registry files (like Rhetor's)
        self.component_registry_base = self.registry_base / 'components'
        self.component_registry_base.mkdir(exist_ok=True)
        
        # Audit log for state transitions
        self.audit_log_file = self.registry_base / 'ai_registry_audit.log'
        
        # Role mapping file
        self.role_mapping_file = self.registry_base / 'ai_role_mapping.json'
        
        self._registry_cache: Dict[str, Dict[str, Any]] = {}
        self._state_cache: Dict[str, str] = {}  # Track previous states
        
        # Clean up any stale locks on initialization
        self._cleanup_stale_locks()
        
    def _cleanup_stale_locks(self):
        """Clean up stale lock files older than 60 seconds."""
        lock_files = [
            self.registry_base / '.registration.lock',
            self.registry_base / '.port_allocation.lock'
        ]
        
        for lock_file in lock_files:
            if lock_file.exists():
                try:
                    lock_age = time.time() - lock_file.stat().st_mtime
                    if lock_age > 60:  # Lock older than 60 seconds
                        logger.warning(f"Removing stale lock file (age: {lock_age:.1f}s): {lock_file}")
                        lock_file.unlink()
                except Exception as e:
                    logger.error(f"Failed to clean up stale lock {lock_file}: {e}")
    
    def _acquire_lock_with_timeout(self, lock_file_path: Path, timeout: float = 5.0, exclusive: bool = True):
        """
        Acquire a file lock with timeout.
        
        Args:
            lock_file_path: Path to lock file
            timeout: Maximum time to wait for lock
            exclusive: True for exclusive lock, False for shared
            
        Returns:
            File handle with lock acquired
            
        Raises:
            TimeoutError: If lock cannot be acquired within timeout
        """
        start_time = time.time()
        lock_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # First check for stale lock
        if lock_file_path.exists():
            try:
                lock_age = time.time() - lock_file_path.stat().st_mtime
                if lock_age > 60:
                    logger.warning(f"Removing stale lock (age: {lock_age:.1f}s): {lock_file_path}")
                    lock_file_path.unlink()
            except:
                pass
        
        while time.time() - start_time < timeout:
            f = None
            try:
                f = open(lock_file_path, 'w')
                lock_flag = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
                fcntl.flock(f.fileno(), lock_flag | fcntl.LOCK_NB)
                # Write PID to help identify lock owner
                f.write(f"{os.getpid()}\n")
                f.flush()
                return f
            except IOError:
                if f:
                    f.close()
                time.sleep(0.05)  # 50ms retry interval
        
        raise TimeoutError(f"Could not acquire lock on {lock_file_path} within {timeout} seconds")
        
    # @tekton-method: Register platform AI with atomic updates
    # @tekton-critical: true
    # @tekton-modifies: platform-ai-registry
    # @tekton-thread-safe: true
    @api_contract(
        title="Platform AI Registration",
        endpoint="register_platform_ai",
        method="CALL",
        request_schema={"ai_id": "string", "port": "int", "component": "string", "metadata": "dict"}
    )
    @danger_zone(
        title="Concurrent registry modification",
        risk_level="high",
        risks=["Registry corruption", "Port conflicts", "Race conditions"],
        mitigation="Exclusive file locking with retries"
    )
    def register_platform_ai(self, ai_id: str, port: int, 
                           component: str, metadata: Optional[Dict] = None) -> bool:
        """
        Register a platform-wide AI specialist with atomic updates.
        
        Args:
            ai_id: Unique identifier for the AI (e.g., 'numa', 'noesis')
            port: Socket port the AI is listening on
            component: Component name (e.g., 'Numa', 'Noesis')
            metadata: Optional metadata (model, role, etc.)
            
        Returns:
            True if registration successful
        """
        max_retries = 5
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                # Use the new lock mechanism with timeout
                registration_lock = self.registry_base / '.registration.lock'
                lock_f = self._acquire_lock_with_timeout(registration_lock, timeout=5.0)
                try:
                    # Load existing registry while holding lock
                    registry = self._load_platform_registry()
                    
                    # Check if port is already in use by another AI
                    for existing_ai_id, existing_data in registry.items():
                        if existing_ai_id != ai_id and existing_data['port'] == port:
                            logger.error(f"Port {port} already in use by {existing_ai_id}")
                            return False
                    
                    # Add or update AI entry
                    registry[ai_id] = {
                        'port': port,
                        'component': component,
                        'metadata': metadata or {},
                        'registered_at': asyncio.get_event_loop().time()
                    }
                    
                    # Save registry while still holding lock
                    self._save_platform_registry(registry)
                    
                    # Update cache
                    self._registry_cache[ai_id] = registry[ai_id]
                    
                    logger.info(f"Registered platform AI: {ai_id} on port {port}")
                    
                    # Log the registration event
                    self.log_transition(ai_id, 'registered', {
                        'port': port,
                        'component': component,
                        'metadata': metadata,
                        'trigger': 'api_call'
                    })
                    
                    return True
                    
                finally:
                    # Release lock and close file
                    fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)
                    lock_f.close()
                        
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Registration attempt {attempt + 1} failed for {ai_id}: {e}, retrying...")
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    logger.error(f"Failed to register AI {ai_id} after {max_retries} attempts: {e}")
                    return False
        
        return False
    
    def deregister_platform_ai(self, ai_id: str) -> bool:
        """
        Deregister a platform AI specialist with atomic updates.
        
        Args:
            ai_id: AI identifier to deregister
            
        Returns:
            True if deregistration successful
        """
        max_retries = 5
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                # Use the new lock mechanism with timeout
                registration_lock = self.registry_base / '.registration.lock'
                lock_f = self._acquire_lock_with_timeout(registration_lock, timeout=5.0)
                try:
                        registry = self._load_platform_registry()
                        
                        if ai_id in registry:
                            del registry[ai_id]
                            self._save_platform_registry(registry)
                            
                            if ai_id in self._registry_cache:
                                del self._registry_cache[ai_id]
                                
                            logger.info(f"Deregistered platform AI: {ai_id}")
                            
                            # Log the deregistration event
                            self.log_transition(ai_id, 'deregistered', {
                                'trigger': 'api_call',
                                'final_state': 'removed'
                            })
                            
                            return True
                        
                        return False
                        
                finally:
                    # Release lock and close file
                    fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)
                    lock_f.close()
                        
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Deregistration attempt {attempt + 1} failed for {ai_id}: {e}, retrying...")
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    logger.error(f"Failed to deregister AI {ai_id} after {max_retries} attempts: {e}")
                    return False
        
        return False
    
    def log_transition(self, ai_id: str, event: str, details: Dict[str, Any] = None):
        """
        Log AI state transitions and events to audit log.
        
        Args:
            ai_id: AI identifier
            event: Event type (registered, deregistered, state_change, etc.)
            details: Additional event details
        """
        timestamp = time.time()
        log_entry = {
            'timestamp': timestamp,
            'iso_time': datetime.fromtimestamp(timestamp).isoformat(),
            'ai_id': ai_id,
            'event': event,
            'details': details or {},
            'previous_state': self._state_cache.get(ai_id),
            'trigger': details.get('trigger', 'unknown') if details else 'unknown'
        }
        
        try:
            # Append to audit log file
            with open(self.audit_log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            # Update state cache if this is a state change
            if event == 'state_change' and details and 'new_state' in details:
                self._state_cache[ai_id] = details['new_state']
                
            logger.debug(f"Logged transition for {ai_id}: {event}")
            
        except Exception as e:
            logger.error(f"Failed to log transition for {ai_id}: {e}")
    
    def get_ai_socket(self, ai_id: str) -> Optional[Tuple[str, int]]:
        """
        Get socket information for an AI with thread-safe access.
        
        Args:
            ai_id: AI identifier
            
        Returns:
            Tuple of (host, port) or None if not found
        """
        # Check cache first (read-only, no lock needed)
        if ai_id in self._registry_cache:
            return ('localhost', self._registry_cache[ai_id]['port'])
        
        # Load from registry with shared lock
        try:
            # Use shared lock for reading
            registration_lock = self.registry_base / '.registration.lock'
            with open(registration_lock, 'w') as lock_f:
                fcntl.flock(lock_f.fileno(), fcntl.LOCK_SH)
                try:
                    registry = self._load_platform_registry()
                    if ai_id in registry:
                        self._registry_cache[ai_id] = registry[ai_id]
                        return ('localhost', registry[ai_id]['port'])
                finally:
                    fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)
        except Exception as e:
            logger.error(f"Failed to get socket for {ai_id}: {e}")
        
        return None
    
    def list_platform_ais(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered platform AIs with thread-safe access.
        
        Returns:
            Dictionary of AI entries
        """
        try:
            # Use shared lock for reading
            registration_lock = self.registry_base / '.registration.lock'
            with open(registration_lock, 'w') as lock_f:
                fcntl.flock(lock_f.fileno(), fcntl.LOCK_SH)
                try:
                    return self._load_platform_registry()
                finally:
                    fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)
        except Exception as e:
            logger.error(f"Failed to list platform AIs: {e}")
            return {}
    
    # @tekton-method: Allocate available port atomically
    # @tekton-critical: true
    # @tekton-thread-safe: true
    # @tekton-performance: port-scanning
    @performance_boundary(
        title="Port allocation scanning",
        sla="<500ms for 5000 port range",
        optimization_notes="Caches used ports, atomic allocation with locks"
    )
    @danger_zone(
        title="Port allocation race conditions",
        risk_level="medium",
        risks=["Duplicate port allocation", "Socket bind failures"],
        mitigation="Exclusive locking during entire allocation process"
    )
    def allocate_port(self, preferred_port: Optional[int] = None,
                      start_port: int = 45000, max_port: int = 50000) -> Optional[int]:
        """
        Allocate an available port for an AI socket with atomic allocation.
        
        Args:
            preferred_port: Try this port first if specified
            start_port: Starting port to scan from
            max_port: Maximum port to try
            
        Returns:
            Available port number or None if none found
        """
        # Use file locking to ensure atomic port allocation
        allocation_lock_file = self.registry_base / '.port_allocation.lock'
        max_retries = 5
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                # Use the new lock mechanism with timeout for port allocation
                lock_f = self._acquire_lock_with_timeout(allocation_lock_file, timeout=5.0)
                try:
                        # Get all used ports while holding the lock
                        used_ports = set()
                        
                        # Platform AIs
                        platform_registry = self._load_platform_registry()
                        for ai_data in platform_registry.values():
                            used_ports.add(ai_data['port'])
                        
                        # Component AIs (scan component registries)
                        for registry_file in self.component_registry_base.glob('*_registry.json'):
                            try:
                                with open(registry_file, 'r') as f:
                                    component_registry = json.load(f)
                                    for ai_data in component_registry.values():
                                        if isinstance(ai_data, dict) and 'port' in ai_data:
                                            used_ports.add(ai_data['port'])
                            except Exception:
                                pass
                        
                        # Try preferred port first if specified
                        if preferred_port and preferred_port not in used_ports:
                            logger.info(f"Allocated preferred port {preferred_port} (used ports: {len(used_ports)})")
                            logger.debug(f"Port allocation - Used ports: {sorted(used_ports)}")
                            return preferred_port
                        
                        # Find available port - just check registry, don't bind
                        # This eliminates TOCTOU race - the actual service will try to bind
                        # and fail gracefully if something else grabbed the port
                        for port in range(start_port, max_port):
                            if port not in used_ports:
                                if preferred_port:
                                    logger.warning(f"Preferred port {preferred_port} unavailable, allocated {port} instead")
                                else:
                                    logger.info(f"Allocated port {port} (used ports: {len(used_ports)})")
                                logger.debug(f"Port allocation - Used ports: {sorted(used_ports)}")
                                return port
                        
                        return None
                        
                finally:
                    # Release lock and close file
                    fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)
                    lock_f.close()
                        
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Port allocation attempt {attempt + 1} failed: {e}, retrying...")
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    logger.error(f"Failed to allocate port after {max_retries} attempts: {e}")
                    return None
        
        return None
    
    def _is_port_available(self, port: int) -> bool:
        """Check if a port is available for binding."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return True
        except OSError:
            return False
    
    def _load_platform_registry(self) -> Dict[str, Dict[str, Any]]:
        """Load platform AI registry from file with file locking."""
        if self.platform_registry_file.exists():
            max_retries = 5
            retry_delay = 0.1
            
            for attempt in range(max_retries):
                try:
                    with open(self.platform_registry_file, 'r') as f:
                        # Acquire shared lock for reading
                        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                        try:
                            return json.load(f)
                        finally:
                            # Release lock
                            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                            
                except json.JSONDecodeError as e:
                    logger.error(f"Registry file corrupted: {e}")
                    # If file is corrupted, return empty dict
                    return {}
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Registry load attempt {attempt + 1} failed: {e}, retrying...")
                        time.sleep(retry_delay * (attempt + 1))
                    else:
                        logger.error(f"Failed to load platform registry after {max_retries} attempts: {e}")
        
        return {}
    
    def _save_platform_registry(self, registry: Dict[str, Dict[str, Any]]):
        """Save platform AI registry to file with file locking."""
        max_retries = 5
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                # Use atomic write with file locking
                temp_file = self.platform_registry_file.with_suffix('.tmp')
                
                with open(temp_file, 'w') as f:
                    # Acquire exclusive lock
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    try:
                        json.dump(registry, f, indent=2)
                        f.flush()
                        os.fsync(f.fileno())
                    finally:
                        # Release lock
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                
                # Atomic rename
                temp_file.replace(self.platform_registry_file)
                return
                
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Registry save attempt {attempt + 1} failed: {e}, retrying...")
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    logger.error(f"Failed to save platform registry after {max_retries} attempts: {e}")
                    raise
    
    # @tekton-method: Wait for AI readiness with timeout
    # @tekton-async: true
    # @tekton-timeout: 30s
    # @tekton-integration: socket-connection
    @performance_boundary(
        title="AI readiness check",
        sla="<30s timeout",
        optimization_notes="Async polling with exponential backoff"
    )
    @integration_point(
        title="AI socket connection verification",
        target_component="AI specialists",
        protocol="TCP socket",
        data_flow="Connection test only"
    )
    async def wait_for_ai(self, ai_id: str, timeout: float = 30.0) -> bool:
        """
        Wait for an AI to be registered and responding.
        
        Args:
            ai_id: AI identifier to wait for
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if AI is available, False if timeout
        """
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            socket_info = self.get_ai_socket(ai_id)
            if socket_info:
                # Try to connect
                try:
                    reader, writer = await asyncio.wait_for(
                        asyncio.open_connection(socket_info[0], socket_info[1]),
                        timeout=2.0
                    )
                    writer.close()
                    await writer.wait_closed()
                    return True
                except Exception:
                    pass
            
            await asyncio.sleep(0.5)
        
        return False
    
    def discover_by_role(self, role: str) -> List[Dict[str, Any]]:
        """
        Discover AI specialists by role/capability.
        
        Args:
            role: Role or capability to search for (e.g., 'code-analysis', 'planning')
            
        Returns:
            List of AI specialists matching the role
        """
        matching_ais = []
        
        # Load role mappings
        role_mappings = self._load_role_mappings()
        
        # Get all registered AIs
        registry = self.list_platform_ais()
        
        for ai_id, ai_data in registry.items():
            # Check if AI has this role in mappings
            ai_roles = role_mappings.get(ai_id, {}).get('roles', [])
            if role in ai_roles:
                matching_ais.append({
                    'ai_id': ai_id,
                    'component': ai_data['component'],
                    'port': ai_data['port'],
                    'roles': ai_roles,
                    'capabilities': role_mappings.get(ai_id, {}).get('capabilities', []),
                    'performance': self._get_ai_performance(ai_id)
                })
            
            # Also check component-based roles
            component_role = self._component_to_role(ai_data['component'])
            if component_role == role:
                matching_ais.append({
                    'ai_id': ai_id,
                    'component': ai_data['component'],
                    'port': ai_data['port'],
                    'roles': [component_role],
                    'capabilities': self._get_component_capabilities(ai_data['component']),
                    'performance': self._get_ai_performance(ai_id)
                })
        
        return matching_ais
    
    def select_best_ai(self, role: str, requirements: Dict[str, Any] = None) -> Optional[str]:
        """
        Select the best AI for a given role based on availability and performance.
        
        Args:
            role: Required role/capability
            requirements: Additional requirements (e.g., min_performance, max_latency)
            
        Returns:
            AI ID of the best match, or None if no suitable AI found
        """
        candidates = self.discover_by_role(role)
        
        if not candidates:
            logger.warning(f"No AI specialists found for role: {role}")
            return None
        
        # Score each candidate
        scored_candidates = []
        for candidate in candidates:
            score = 0.0
            
            # Availability check (can we connect?)
            if self._is_ai_available(candidate['ai_id']):
                score += 50.0  # Base score for being available
                
                # Performance scoring
                perf = candidate.get('performance', {})
                if perf.get('success_rate', 0) > 0:
                    score += perf['success_rate'] * 30  # Up to 30 points for success rate
                
                if perf.get('avg_response_time'):
                    # Faster is better (inverse scoring)
                    score += max(0, 20 - perf['avg_response_time'])  # Up to 20 points for speed
                
                # Role match scoring
                if role == candidate['roles'][0]:  # Primary role match
                    score += 10
                
                scored_candidates.append((candidate['ai_id'], score))
        
        if not scored_candidates:
            logger.warning(f"No available AI specialists for role: {role}")
            return None
        
        # Sort by score and return the best
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        best_ai = scored_candidates[0][0]
        
        logger.info(f"Selected AI {best_ai} for role {role} (score: {scored_candidates[0][1]:.1f})")
        self.log_transition(best_ai, 'selected', {
            'role': role,
            'score': scored_candidates[0][1],
            'alternatives': len(scored_candidates) - 1
        })
        
        return best_ai
    
    def _load_role_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Load AI role mappings from file."""
        if self.role_mapping_file.exists():
            try:
                with open(self.role_mapping_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load role mappings: {e}")
        return {}
    
    def _component_to_role(self, component: str) -> str:
        """Map component name to primary role."""
        role_map = {
            'apollo': 'code-analysis',
            'athena': 'knowledge-synthesis',
            'prometheus': 'planning',
            'hermes': 'messaging',
            'engram': 'memory',
            'rhetor': 'orchestration',
            'numa': 'specialist-management',
            'sophia': 'learning',
            'ergon': 'agent-coordination',
            'metis': 'workflow-design'
        }
        return role_map.get(component.lower(), 'general')
    
    def _get_component_capabilities(self, component: str) -> List[str]:
        """Get capabilities for a component."""
        capability_map = {
            'apollo': ['code-analysis', 'static-analysis', 'metrics', 'quality-assessment'],
            'athena': ['knowledge-synthesis', 'query-resolution', 'semantic-search', 'reasoning'],
            'prometheus': ['planning', 'task-breakdown', 'resource-optimization', 'scheduling'],
            'rhetor': ['orchestration', 'prompt-engineering', 'llm-routing', 'response-optimization']
        }
        return capability_map.get(component.lower(), ['general'])
    
    def _get_ai_performance(self, ai_id: str) -> Dict[str, float]:
        """Get performance metrics for an AI (placeholder for now)."""
        # TODO: Implement actual performance tracking
        return {
            'success_rate': 0.95,
            'avg_response_time': 0.5,
            'total_requests': 0
        }
    
    def mark_config_update_needed(self):
        """
        Mark that the registry has been updated and config sync is needed.
        This is called by Rhetor when it makes changes to the AI roster.
        """
        update_marker = self.registry_base / '.config_update_needed'
        try:
            with open(update_marker, 'w') as f:
                json.dump({
                    'timestamp': time.time(),
                    'iso_time': datetime.now().isoformat()
                }, f)
            logger.debug("Marked config update needed")
        except Exception as e:
            logger.error(f"Failed to mark config update: {e}")
    
    def _is_ai_available(self, ai_id: str) -> bool:
        """Check if an AI is currently available."""
        socket_info = self.get_ai_socket(ai_id)
        if not socket_info:
            return False
        
        # Quick connection test
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.0)
            result = sock.connect_ex((socket_info[0], socket_info[1]))
            sock.close()
            return result == 0
        except:
            return False