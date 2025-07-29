#!/usr/bin/env python3
"""
Test shared memory creation and immediate connection
"""

import sys
import os
import hashlib
import time
from pathlib import Path
from multiprocessing import shared_memory

# Set up environment
os.environ['TEKTON_ROOT'] = '/Users/cskoons/projects/github/Coder-A'
sys.path.insert(0, str(Path('shared/aish/src')))
sys.path.insert(0, str(Path('shared/aish/src').parent.parent))

from shared.env import TektonEnviron, TektonEnvironLock
TektonEnvironLock.load()

def test_creation_and_connection():
    """Create shared memory and immediately try to connect from different processes."""
    
    tekton_root = TektonEnviron.get('TEKTON_ROOT', '/default')
    tekton_hash = hashlib.md5(tekton_root.encode()).hexdigest()[:8]
    shm_name = f"test_shm_{tekton_hash}"
    
    print(f"Testing with shared memory name: {shm_name}")
    
    # Create shared memory
    print("Creating shared memory...")
    try:
        shm_create = shared_memory.SharedMemory(name=shm_name, create=True, size=1024*1024)
        print(f"✓ Created: {shm_name}, size: {len(shm_create.buf)}")
        
        # Write test data
        test_data = b"HELLO_FROM_CREATOR"
        shm_create.buf[:len(test_data)] = test_data
        print(f"✓ Wrote test data: {test_data}")
        
        # DON'T close yet - try to connect while it's still open
        print("\nTrying to connect while creator still has it open...")
        try:
            shm_connect = shared_memory.SharedMemory(name=shm_name)
            print(f"✓ Connected! Size: {len(shm_connect.buf)}")
            
            # Read the data
            read_data = bytes(shm_connect.buf[:len(test_data)])
            print(f"✓ Read data: {read_data}")
            
            shm_connect.close()
            print("✓ Connection closed")
            
        except Exception as e:
            print(f"✗ Connection failed: {e}")
        
        # Now close the creator
        shm_create.close()
        print("✓ Creator closed")
        
        # Try to connect after creator closed but before unlink
        print("\nTrying to connect after creator closed...")
        try:
            shm_reconnect = shared_memory.SharedMemory(name=shm_name)
            print(f"✓ Reconnected! Size: {len(shm_reconnect.buf)}")
            
            # Clean up
            shm_reconnect.close()
            shm_reconnect.unlink()
            print("✓ Cleaned up shared memory")
            
        except Exception as e:
            print(f"✗ Reconnection failed: {e}")
            
            # Try to unlink anyway
            try:
                temp_shm = shared_memory.SharedMemory(name=shm_name)
                temp_shm.unlink()
                temp_shm.close()
            except:
                pass
        
    except Exception as e:
        print(f"✗ Creation failed: {e}")
        import traceback
        traceback.print_exc()

def test_daemon_simulation():
    """Simulate what the daemon does vs what clients do."""
    
    tekton_root = TektonEnviron.get('TEKTON_ROOT', '/default')
    tekton_hash = hashlib.md5(tekton_root.encode()).hexdigest()[:8]
    shm_name = f"daemon_sim_{tekton_hash}"
    
    print(f"\n=== Daemon Simulation ===")
    print(f"Shared memory name: {shm_name}")
    
    # Simulate daemon: create shared memory and keep it alive
    print("DAEMON: Creating shared memory...")
    try:
        daemon_shm = shared_memory.SharedMemory(name=shm_name, create=True, size=1024*1024)
        print(f"DAEMON: ✓ Created and holding shared memory")
        
        # Fork a subprocess to simulate client
        import subprocess
        client_code = f'''
import sys
from multiprocessing import shared_memory

try:
    print("CLIENT: Attempting to connect to {shm_name}")
    client_shm = shared_memory.SharedMemory(name="{shm_name}")
    print(f"CLIENT: ✓ Connected! Size: {{len(client_shm.buf)}}")
    client_shm.close()
    print("CLIENT: ✓ Connection closed")
except Exception as e:
    print(f"CLIENT: ✗ Connection failed: {{e}}")
'''
        
        result = subprocess.run([sys.executable, '-c', client_code], 
                              capture_output=True, text=True, timeout=5)
        
        print("CLIENT OUTPUT:")
        print(result.stdout)
        if result.stderr:
            print("CLIENT STDERR:")
            print(result.stderr)
        
        # Clean up
        daemon_shm.close()
        daemon_shm.unlink()
        print("DAEMON: ✓ Cleaned up")
        
    except Exception as e:
        print(f"DAEMON: ✗ Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== Shared Memory Connection Test ===")
    
    test_creation_and_connection()
    test_daemon_simulation()