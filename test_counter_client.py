#!/usr/bin/env python3
"""
Test client to read the counter from shared memory.
"""

import hashlib
import pickle
from multiprocessing import shared_memory

tekton_root = "/Users/cskoons/projects/github/Coder-A"
tekton_hash = hashlib.md5(tekton_root.encode()).hexdigest()[:8]
shm_name = f"counter_test_{tekton_hash}"

try:
    shm = shared_memory.SharedMemory(name=shm_name)
    data = pickle.loads(bytes(shm.buf[:1024]))
    print(f"Counter value: {data.get('counter', 'NOT FOUND')}")
    shm.close()
except FileNotFoundError:
    print(f"Shared memory {shm_name} not found - daemon not running?")
except Exception as e:
    print(f"Error: {e}")