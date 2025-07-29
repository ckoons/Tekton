#!/usr/bin/env python3
"""
Simple counter daemon that just maintains a counter in shared memory.
"""

import os
import sys
import time
import signal
import hashlib
import pickle
from multiprocessing import shared_memory

class CounterDaemon:
    def __init__(self, tekton_root):
        self.tekton_root = tekton_root
        self.tekton_hash = hashlib.md5(tekton_root.encode()).hexdigest()[:8]
        self.shm_name = f"counter_test_{self.tekton_hash}"
        self.running = True
        self.shm = None
        
    def signal_handler(self, signum, frame):
        print(f"Daemon stopping...")
        self.running = False
        
    def run(self):
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Create shared memory with counter
        try:
            self.shm = shared_memory.SharedMemory(name=self.shm_name, create=True, size=1024)
            print(f"Created shared memory: {self.shm_name}")
            
            # Initialize counter
            counter_data = {'counter': 0}
            data = pickle.dumps(counter_data)
            self.shm.buf[:len(data)] = data
            print("Initialized counter to 0")
            
        except FileExistsError:
            print(f"Shared memory {self.shm_name} already exists")
            sys.exit(1)
            
        # Keep running and increment counter every 5 seconds
        while self.running:
            try:
                # Read current counter
                data = pickle.loads(bytes(self.shm.buf[:1024]))
                current = data.get('counter', 0)
                
                # Increment
                data['counter'] = current + 1
                
                # Write back
                new_data = pickle.dumps(data)
                self.shm.buf[:len(new_data)] = new_data
                
                print(f"Counter incremented to {data['counter']}")
                time.sleep(5)
                
            except Exception as e:
                print(f"Error: {e}")
                break
                
        # Cleanup
        if self.shm:
            self.shm.close()
            self.shm.unlink()
            print("Cleaned up shared memory")

if __name__ == "__main__":
    tekton_root = sys.argv[1] if len(sys.argv) > 1 else "/Users/cskoons/projects/github/Coder-A"
    daemon = CounterDaemon(tekton_root)
    
    # Fork to background
    pid = os.fork()
    if pid > 0:
        print(f"Counter daemon started with PID {pid}")
        sys.exit(0)
    
    # Child continues
    daemon.run()