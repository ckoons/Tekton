#!/usr/bin/env python3
"""Test script to increment counter in shared memory."""

import hashlib
import pickle
from multiprocessing import shared_memory

# Get shared memory name
tekton_root = '/Users/cskoons/projects/github/Coder-A'
tekton_hash = hashlib.md5(tekton_root.encode()).hexdigest()[:8]
shm_name = f'tekton_ci_registry_{tekton_hash}'

print(f"Connecting to shared memory: {shm_name}")

try:
    # Connect to existing shared memory
    shm = shared_memory.SharedMemory(name=shm_name)
    print(f"Connected! Size: {len(shm.buf)} bytes")
    
    # Read current state
    buf_bytes = bytes(shm.buf)
    null_start = buf_bytes.find(b'\x00\x00\x00\x00')
    if null_start == -1:
        null_start = len(buf_bytes)
    
    if null_start > 0:
        try:
            state = pickle.loads(buf_bytes[:null_start])
            print(f"Current state: {state}")
            
            # Increment counter
            old_value = state.get('test_counter', 0)
            state['test_counter'] = old_value + 1
            print(f"Incremented counter from {old_value} to {state['test_counter']}")
            
            # Write back to shared memory
            data = pickle.dumps(state)
            if len(data) <= len(shm.buf):
                # Clear and write
                shm.buf[:] = b'\x00' * len(shm.buf)
                shm.buf[:len(data)] = data
                print("Updated shared memory")
            else:
                print("Error: Data too large for shared memory")
                
        except Exception as e:
            print(f"Error processing state: {e}")
    else:
        print("Shared memory is empty")
    
    shm.close()
    
except FileNotFoundError:
    print("Shared memory not found - daemon not running?")
except Exception as e:
    print(f"Error: {e}")