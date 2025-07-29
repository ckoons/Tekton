#!/usr/bin/env python3
"""
Test adding values to shared memory.
"""

import sys
import hashlib
import pickle
from multiprocessing import shared_memory

tekton_root = "/Users/cskoons/projects/github/Coder-A"
tekton_hash = hashlib.md5(tekton_root.encode()).hexdigest()[:8]
shm_name = f"tekton_ci_registry_{tekton_hash}"

key = sys.argv[1] if len(sys.argv) > 1 else "test_key"
value = sys.argv[2] if len(sys.argv) > 2 else "test_value"

try:
    # Connect to shared memory
    shm = shared_memory.SharedMemory(name=shm_name)
    
    # Read current data
    data = pickle.loads(bytes(shm.buf[:1024*1024]))
    print(f"Current data: {data}")
    
    # Add new value
    data[key] = value
    
    # Write back
    new_data = pickle.dumps(data)
    shm.buf[:len(new_data)] = new_data
    
    print(f"Added {key} = {value}")
    print(f"New data: {data}")
    
    shm.close()
    
except FileNotFoundError:
    print(f"Shared memory {shm_name} not found - daemon not running?")
except Exception as e:
    print(f"Error: {e}")