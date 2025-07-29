#!/usr/bin/env python3
"""
Simple file-based daemon for CI registry persistence.
Uses a JSON file instead of shared memory to avoid Python's resource tracker issues.
"""

import os
import sys
import time
import signal
import hashlib
import json
import fcntl
import tempfile

class FileDaemon:
    def __init__(self, tekton_root):
        self.tekton_root = tekton_root
        self.tekton_hash = hashlib.md5(tekton_root.encode()).hexdigest()[:8]
        
        # Create directory structure in TEKTON_ROOT
        self.registry_dir = os.path.join(tekton_root, '.tekton', 'aish', 'ci-registry')
        os.makedirs(self.registry_dir, exist_ok=True)
        
        self.data_file = os.path.join(self.registry_dir, 'registry.json')
        self.lock_file = os.path.join(self.registry_dir, 'registry.lock')
        self.running = True
        
    def signal_handler(self, signum, frame):
        print(f"Daemon received signal {signum}, shutting down...")
        self.running = False
        
    def run(self):
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        try:
            # Create initial data file
            if not os.path.exists(self.data_file):
                with open(self.data_file, 'w') as f:
                    json.dump({}, f)
                print(f"Created data file: {self.data_file}")
            else:
                print(f"Using existing data file: {self.data_file}")
            
            print(f"File daemon running (PID {os.getpid()})")
            
            # Just keep running
            while self.running:
                time.sleep(1)
                
        except Exception as e:
            print(f"Daemon error: {e}")
        finally:
            print("Daemon stopped, data file persists")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: file_daemon.py <TEKTON_ROOT>")
        sys.exit(1)
        
    tekton_root = os.path.abspath(sys.argv[1])
    
    # Check if already running
    import subprocess
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    pattern = f"file_daemon.py {tekton_root}"
    current_pid = os.getpid()
    
    for line in result.stdout.split('\n'):
        if pattern in line and 'grep' not in line:
            parts = line.split()
            if len(parts) > 1:
                try:
                    pid = int(parts[1])
                    if pid != current_pid:
                        print(f"File daemon already running (PID {pid})")
                        sys.exit(0)
                except ValueError:
                    continue
    
    # Fork to background
    pid = os.fork()
    if pid > 0:
        print(f"File daemon starting with PID {pid}")
        sys.exit(0)
        
    daemon = FileDaemon(tekton_root)
    daemon.run()