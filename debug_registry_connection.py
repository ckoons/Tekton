#!/usr/bin/env python3
"""
Debug the exact difference between raw shared memory connection and CI registry connection
"""

import sys
import os
import hashlib
from pathlib import Path

# Minimal setup like test_daemon_shm.py
print("=== RAW CONNECTION TEST ===")
from multiprocessing import shared_memory

shm_name = 'tekton_ci_registry_5f58f9e9'
print(f'Testing raw connection to: {shm_name}')

try:
    shm = shared_memory.SharedMemory(name=shm_name)
    print(f'RAW: SUCCESS - Connected to {shm_name}!')
    print(f'RAW: Size: {len(shm.buf)} bytes')
    
    # Check for data
    data = bytes(shm.buf[:50])
    non_zero_count = sum(1 for b in data if b != 0)
    print(f'RAW: Non-zero bytes in first 50: {non_zero_count}')
    
    shm.close()
    
except Exception as e:
    print(f'RAW: FAILED - {e}')

print()
print("=== CI REGISTRY CONNECTION TEST ===")

# Now set up environment like the CI registry would
os.environ['TEKTON_ROOT'] = '/Users/cskoons/projects/github/Coder-A'
sys.path.insert(0, str(Path('shared/aish/src')))
sys.path.insert(0, str(Path('shared/aish/src').parent.parent))

try:
    from shared.env import TektonEnviron, TektonEnvironLock
    TektonEnvironLock.load()
    
    print(f'REGISTRY: TEKTON_ROOT from env: {TektonEnviron.get("TEKTON_ROOT")}')
    
    # Calculate name the same way CI registry does
    tekton_root = TektonEnviron.get('TEKTON_ROOT', '/default')
    tekton_hash = hashlib.md5(tekton_root.encode()).hexdigest()[:8]
    registry_shm_name = f"tekton_ci_registry_{tekton_hash}"
    
    print(f'REGISTRY: Calculated shared memory name: {registry_shm_name}')
    print(f'REGISTRY: Names match: {shm_name == registry_shm_name}')
    
    # Try direct connection with registry-calculated name
    try:
        registry_shm = shared_memory.SharedMemory(name=registry_shm_name)
        print(f'REGISTRY: SUCCESS - Direct connection to {registry_shm_name}!')
        registry_shm.close()
    except Exception as e:
        print(f'REGISTRY: FAILED - Direct connection: {e}')
    
    # Now try through the actual CI registry
    print('REGISTRY: Testing through CI registry...')
    from registry.ci_registry import CIRegistry
    
    # Create a NEW registry instance (like clients do)  
    print('REGISTRY: Creating new CIRegistry instance...')
    registry = CIRegistry()
    print('REGISTRY: CI registry created successfully!')
    
    if hasattr(registry, '_shm_name'):
        print(f'REGISTRY: Registry shared memory name: {registry._shm_name}')
    if hasattr(registry, '_shm_block'):
        print(f'REGISTRY: Registry has shared memory block: {len(registry._shm_block.buf)} bytes')
    
except Exception as e:
    print(f'REGISTRY: FAILED - {e}')
    import traceback
    traceback.print_exc()