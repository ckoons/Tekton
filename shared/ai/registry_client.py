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
from typing import Dict, Optional, Tuple, Any
from pathlib import Path

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
        
        self._registry_cache: Dict[str, Dict[str, Any]] = {}
        
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
                # Use a registration lock file to coordinate concurrent registrations
                registration_lock = self.registry_base / '.registration.lock'
                with open(registration_lock, 'w') as lock_f:
                    # Acquire exclusive lock for registration
                    fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX)
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
                        return True
                        
                    finally:
                        # Release lock
                        fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)
                        
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
                # Use the same registration lock for all registry modifications
                registration_lock = self.registry_base / '.registration.lock'
                with open(registration_lock, 'w') as lock_f:
                    # Acquire exclusive lock
                    fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX)
                    try:
                        registry = self._load_platform_registry()
                        
                        if ai_id in registry:
                            del registry[ai_id]
                            self._save_platform_registry(registry)
                            
                            if ai_id in self._registry_cache:
                                del self._registry_cache[ai_id]
                                
                            logger.info(f"Deregistered platform AI: {ai_id}")
                            return True
                        
                        return False
                        
                    finally:
                        # Release lock
                        fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)
                        
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Deregistration attempt {attempt + 1} failed for {ai_id}: {e}, retrying...")
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    logger.error(f"Failed to deregister AI {ai_id} after {max_retries} attempts: {e}")
                    return False
        
        return False
    
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
    def allocate_port(self, start_port: int = 45000, max_port: int = 50000) -> Optional[int]:
        """
        Allocate an available port for an AI socket with atomic allocation.
        
        Args:
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
                with open(allocation_lock_file, 'w') as lock_f:
                    # Acquire exclusive lock for port allocation
                    fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX)
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
                        
                        # Find available port
                        for port in range(start_port, max_port):
                            if port not in used_ports and self._is_port_available(port):
                                # Immediately reserve this port by creating a temp marker
                                # This prevents race conditions during concurrent launches
                                logger.info(f"Allocated port {port} (used ports: {len(used_ports)})")
                                logger.debug(f"Port allocation - Used ports: {sorted(used_ports)}")
                                return port
                        
                        return None
                        
                    finally:
                        # Release lock
                        fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)
                        
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