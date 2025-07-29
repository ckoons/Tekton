#!/usr/bin/env python3
"""
Debug script to test shared memory connection issues
"""

import sys
import os
import hashlib
from pathlib import Path
from multiprocessing import shared_memory

# Set up environment
os.environ['TEKTON_ROOT'] = '/Users/cskoons/projects/github/Coder-A'
sys.path.insert(0, str(Path('shared/aish/src')))
sys.path.insert(0, str(Path('shared/aish/src').parent.parent))

from shared.env import TektonEnviron, TektonEnvironLock
TektonEnvironLock.load()

def test_shared_memory_connection():
    """Test the exact shared memory connection logic."""
    
    # Calculate expected shared memory name
    tekton_root = TektonEnviron.get('TEKTON_ROOT', '/default')
    tekton_hash = hashlib.md5(tekton_root.encode()).hexdigest()[:8]
    shm_name = f"tekton_ci_registry_{tekton_hash}"
    
    print(f"TEKTON_ROOT: {tekton_root}")
    print(f"Hash: {tekton_hash}")
    print(f"Shared memory name: {shm_name}")
    print()
    
    # First, try to connect to existing
    print("1. Trying to connect to existing shared memory...")
    try:
        shm_block = shared_memory.SharedMemory(name=shm_name)
        print(f"✓ Successfully connected to existing shared memory!")
        print(f"  Size: {len(shm_block.buf)} bytes")
        
        # Try to read some data
        buf_bytes = bytes(shm_block.buf[:100])
        non_zero_count = sum(1 for b in buf_bytes if b != 0)
        print(f"  Non-zero bytes in first 100: {non_zero_count}")
        
        shm_block.close()
        return True
        
    except FileNotFoundError as e:
        print(f"✗ Shared memory not found: {e}")
        print(f"  Errno: {e.errno}")
        
    except PermissionError as e:
        print(f"✗ Permission denied: {e}")
        
    except Exception as e:
        print(f"✗ Other error: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Second, try to create new
    print("2. Trying to create new shared memory...")
    try:
        shm_block = shared_memory.SharedMemory(name=shm_name, create=True, size=1024*1024)
        print(f"✓ Successfully created new shared memory!")
        print(f"  Size: {len(shm_block.buf)} bytes")
        
        # Write some test data
        test_data = b"TEST_DATA_FROM_CLIENT"
        shm_block.buf[:len(test_data)] = test_data
        
        shm_block.close()
        return True
        
    except FileExistsError as e:
        print(f"✗ Shared memory already exists: {e}")
        print("  This confirms daemon created it, but we can't connect!")
        
        # Try connecting again
        print("3. Trying to connect again after FileExistsError...")
        try:
            shm_block = shared_memory.SharedMemory(name=shm_name)
            print(f"✓ Connected after FileExistsError!")
            shm_block.close()
            return True
        except Exception as e2:
            print(f"✗ Still can't connect: {e2}")
        
    except Exception as e:
        print(f"✗ Other error creating: {e}")
        import traceback
        traceback.print_exc()
    
    return False

def list_shared_memory():
    """Try to list all shared memory objects."""
    print("4. Attempting to list shared memory objects...")
    
    # On macOS, shared memory lives under /tmp/
    import glob
    shm_files = glob.glob('/tmp/*.psm') + glob.glob('/tmp/shm.*') + glob.glob('/tmp/*shm*')
    if shm_files:
        print(f"Found potential shared memory files: {shm_files}")
    else:
        print("No obvious shared memory files found in /tmp/")
    
    # Check /dev/shm (Linux style)
    try:
        shm_files = glob.glob('/dev/shm/*')
        if shm_files:
            print(f"Found /dev/shm files: {shm_files}")
    except:
        print("/dev/shm not available (expected on macOS)")

if __name__ == "__main__":
    print("=== Shared Memory Debug Test ===")
    print()
    
    success = test_shared_memory_connection()
    print()
    
    list_shared_memory()
    print()
    
    if not success:
        print("❌ SHARED MEMORY CONNECTION FAILED")
        print("This explains why aish clients can't connect to daemon shared memory")
    else:
        print("✅ SHARED MEMORY CONNECTION SUCCESSFUL")