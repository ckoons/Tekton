#!/usr/bin/env python3
"""
Thread-safe file-based CI registry using file locking.
"""

import os
import json
import fcntl
import time
import hashlib
from contextlib import contextmanager
from typing import Dict, Any, Optional

# Try to import landmarks if available
try:
    from landmarks import (
        architecture_decision,
        danger_zone,
        state_checkpoint,
        performance_boundary
    )
except ImportError:
    # Create no-op decorators if landmarks not available
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def danger_zone(**kwargs):
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

@state_checkpoint(
    title="Thread-Safe File Registry",
    description="File-based registry with exclusive locking for concurrent access",
    state_type="persistent",
    persistence=True,
    consistency_requirements="fcntl file locking ensures atomic operations",
    recovery_strategy="Lock acquisition with timeout prevents deadlocks"
)
class FileRegistry:
    def __init__(self, tekton_root: str):
        self.tekton_root = tekton_root
        self.registry_dir = os.path.join(tekton_root, '.tekton', 'aish', 'ci-registry')
        os.makedirs(self.registry_dir, exist_ok=True)
        
        self.data_file = os.path.join(self.registry_dir, 'registry.json')
        self.lock_file = os.path.join(self.registry_dir, 'registry.lock')
    
    @danger_zone(
        title="File Lock Acquisition",
        description="Critical section for acquiring exclusive file lock for concurrent access",
        risk_level="high",
        risks=["deadlock if process crashes", "timeout on high contention", "race conditions"],
        mitigation="Timeout mechanism, automatic lock release on process exit",
        review_required=True
    )
    @contextmanager
    def _file_lock(self, timeout=5):
        """Acquire exclusive lock for file operations."""
        lock_fd = None
        try:
            # Open lock file
            lock_fd = os.open(self.lock_file, os.O_CREAT | os.O_WRONLY)
            
            # Try to acquire exclusive lock with timeout
            start_time = time.time()
            while True:
                try:
                    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except IOError:
                    if time.time() - start_time > timeout:
                        raise TimeoutError(f"Could not acquire lock within {timeout} seconds")
                    time.sleep(0.01)
            
            yield
            
        finally:
            if lock_fd is not None:
                # Release lock and close
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
                os.close(lock_fd)
    
    def read(self) -> Dict[str, Any]:
        """Read registry data with shared lock."""
        with self._file_lock():
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            return {}
    
    @danger_zone(
        title="Atomic File Write",
        description="Writes registry data atomically using temp file and rename",
        risk_level="medium",
        risks=["partial writes if interrupted", "disk full conditions"],
        mitigation="Write to temp file first, then atomic rename",
        review_required=False
    )
    def write(self, data: Dict[str, Any]):
        """Write registry data with exclusive lock."""
        with self._file_lock():
            # Write to temp file first then rename (atomic operation)
            temp_file = self.data_file + '.tmp'
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            os.replace(temp_file, self.data_file)
    
    @performance_boundary(
        title="Registry Key Update",
        description="Read-modify-write operation for single key updates",
        sla="<10ms typical, <100ms under contention",
        optimization_notes="Uses file locking to prevent concurrent modifications",
        measured_impact="Critical for CI state updates during Apollo-Rhetor coordination"
    )
    def update(self, key: str, value: Any):
        """Update a single key in the registry."""
        with self._file_lock():
            # Read current data
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {}
            
            # Update
            data[key] = value
            
            # Write back atomically
            temp_file = self.data_file + '.tmp'
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            os.replace(temp_file, self.data_file)
    
    def get(self, key: str, default=None) -> Any:
        """Get a value from the registry."""
        data = self.read()
        return data.get(key, default)
    
    def delete(self, key: str):
        """Delete a key from the registry."""
        with self._file_lock():
            # Read current data
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                # Delete key if exists
                if key in data:
                    del data[key]
                    
                    # Write back
                    temp_file = self.data_file + '.tmp'
                    with open(temp_file, 'w') as f:
                        json.dump(data, f, indent=2)
                    os.replace(temp_file, self.data_file)


# Test script
if __name__ == "__main__":
    import sys
    import threading
    import random
    
    tekton_root = "/Users/cskoons/projects/github/Coder-A"
    registry = FileRegistry(tekton_root)
    
    # Test concurrent access
    def worker(worker_id):
        for i in range(10):
            key = f"worker_{worker_id}_item_{i}"
            registry.update(key, f"value_{i}")
            time.sleep(random.uniform(0.001, 0.01))
            
        # Read back
        data = registry.read()
        count = sum(1 for k in data.keys() if k.startswith(f"worker_{worker_id}"))
        print(f"Worker {worker_id}: wrote {count} items")
    
    # Launch multiple threads
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    # Wait for all to complete
    for t in threads:
        t.join()
    
    # Final count
    data = registry.read()
    print(f"Total items in registry: {len(data)}")