#!/usr/bin/env python3
"""
Test adding values using mmap.
"""

import sys
import hashlib
import pickle
import mmap

tekton_root = "/Users/cskoons/projects/github/Coder-A"
tekton_hash = hashlib.md5(tekton_root.encode()).hexdigest()[:8]
mmap_path = f"/tmp/tekton_shm_{tekton_hash}"

key = sys.argv[1] if len(sys.argv) > 1 else "test_key"
value = sys.argv[2] if len(sys.argv) > 2 else "test_value"

try:
    # Open the mmap file
    with open(mmap_path, 'r+b') as f:
        mm = mmap.mmap(f.fileno(), 1024 * 1024)
        
        # Find end of data (first null bytes)
        data_end = mm.find(b'\x00\x00\x00\x00')
        if data_end == -1:
            data_end = len(mm)
        
        # Read current data
        if data_end > 0:
            data = pickle.loads(mm[:data_end])
        else:
            data = {}
            
        print(f"Current data: {data}")
        
        # Add new value
        data[key] = value
        
        # Write back
        new_data = pickle.dumps(data)
        mm[:len(new_data)] = new_data
        mm.flush()
        
        print(f"Added {key} = {value}")
        print(f"New data: {data}")
        
        mm.close()
        
except FileNotFoundError:
    print(f"Mmap file {mmap_path} not found - daemon not running?")
except Exception as e:
    print(f"Error: {e}")