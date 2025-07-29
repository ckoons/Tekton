#!/usr/bin/env python3
"""
Daemon using mmap instead of multiprocessing.shared_memory
"""

import os
import sys
import time
import signal
import hashlib
import pickle
import mmap
import tempfile

class MmapDaemon:
    def __init__(self, tekton_root):
        self.tekton_root = tekton_root
        self.tekton_hash = hashlib.md5(tekton_root.encode()).hexdigest()[:8]
        self.mmap_path = f"/tmp/tekton_shm_{self.tekton_hash}"
        self.running = True
        self.mm = None
        self.f = None
        
    def signal_handler(self, signum, frame):
        print(f"Daemon received signal {signum}, shutting down...")
        self.running = False
        
    def run(self):
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        try:
            # Create or open the mmap file
            if not os.path.exists(self.mmap_path):
                # Create new file
                self.f = open(self.mmap_path, 'w+b')
                # Make it 1MB
                self.f.write(b'\x00' * 1024 * 1024)
                self.f.flush()
                print(f"Created mmap file: {self.mmap_path}")
            else:
                # Open existing
                self.f = open(self.mmap_path, 'r+b')
                print(f"Opened existing mmap file: {self.mmap_path}")
            
            # Create memory map
            self.mm = mmap.mmap(self.f.fileno(), 1024 * 1024)
            
            # Initialize with empty dict
            data = pickle.dumps({})
            self.mm[:len(data)] = data
            self.mm.flush()
            
            print(f"Mmap daemon running (PID {os.getpid()})")
            
            # Keep running
            while self.running:
                time.sleep(1)
                
        except Exception as e:
            print(f"Daemon error: {e}")
        finally:
            if self.mm:
                self.mm.close()
            if self.f:
                self.f.close()
            print("Daemon stopped, mmap file persists")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: mmap_daemon.py <TEKTON_ROOT>")
        sys.exit(1)
        
    tekton_root = os.path.abspath(sys.argv[1])
    
    # Fork to background
    pid = os.fork()
    if pid > 0:
        print(f"Mmap daemon starting with PID {pid}")
        sys.exit(0)
        
    daemon = MmapDaemon(tekton_root)
    daemon.run()