#!/usr/bin/env python3
"""
Simple daemon that just creates and holds shared memory.
"""

import os
import sys
import time
import signal
import hashlib
import pickle
from multiprocessing import shared_memory

class SimpleDaemon:
    def __init__(self, tekton_root):
        self.tekton_root = tekton_root
        self.tekton_hash = hashlib.md5(tekton_root.encode()).hexdigest()[:8]
        self.shm_name = f"tekton_ci_registry_{self.tekton_hash}"
        self.running = True
        self.shm = None
        
    def signal_handler(self, signum, frame):
        print(f"Daemon received signal {signum}, shutting down...")
        self.running = False
        
    def run(self):
        # Set up signal handlers
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        try:
            # Create shared memory
            self.shm = shared_memory.SharedMemory(name=self.shm_name, create=True, size=1024*1024)
            print(f"Created shared memory: {self.shm_name}")
            
            # Initialize with empty dict
            data = pickle.dumps({})
            self.shm.buf[:len(data)] = data
            
            # Force resource tracker to forget about this shared memory
            from multiprocessing import resource_tracker
            try:
                # First unregister by the object's actual name
                resource_tracker.unregister(self.shm._name, 'shared_memory')
            except:
                pass
            try:
                # Also try with our name
                resource_tracker.unregister(self.shm_name, 'shared_memory')
            except:
                pass
            
            # Hack: Clear the resource tracker's internal tracking
            if hasattr(resource_tracker, '_resource_tracker'):
                tracker = resource_tracker._resource_tracker
                if hasattr(tracker, '_cache'):
                    tracker._cache.pop(self.shm._name, None)
                    tracker._cache.pop(self.shm_name, None)
            
            print(f"Daemon running (PID {os.getpid()})")
            
            # Just keep running
            while self.running:
                time.sleep(1)
                
        except Exception as e:
            print(f"Daemon error: {e}")
        finally:
            # Don't close or unlink - just let it persist!
            print("Daemon stopped, shared memory persists")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: simple_daemon.py <TEKTON_ROOT>")
        sys.exit(1)
        
    tekton_root = os.path.abspath(sys.argv[1])
    
    # Fork to background
    pid = os.fork()
    if pid > 0:
        print(f"Daemon starting with PID {pid}")
        sys.exit(0)
        
    # Child continues
    daemon = SimpleDaemon(tekton_root)
    daemon.run()