#!/usr/bin/env python3
"""
Simplified aish Shared Memory Daemon

This daemon creates and maintains shared memory for CI registry persistence.
"""

import os
import sys
import time
import signal
import hashlib
import pickle
from multiprocessing import shared_memory

class AishDaemon:
    """Simple daemon that creates and maintains shared memory."""
    
    def __init__(self, tekton_root: str):
        self.tekton_root = tekton_root
        self.tekton_hash = hashlib.md5(tekton_root.encode()).hexdigest()[:8]
        self.shm_name = f"tekton_ci_registry_{self.tekton_hash}"
        self.shm_block = None
        self.running = True
        
    def check_existing_daemon(self) -> bool:
        """Check if a daemon is already running for this TEKTON_ROOT using ps."""
        import subprocess
        try:
            cmd = ['ps', 'aux']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                pattern = f"aish -s {self.tekton_root}"
                current_pid = os.getpid()
                
                for line in result.stdout.split('\n'):
                    if pattern in line and 'grep' not in line:
                        parts = line.split()
                        if len(parts) > 1:
                            try:
                                line_pid = int(parts[1])
                                if line_pid != current_pid:
                                    print(f"aish daemon already running for {self.tekton_root}")
                                    return True
                            except ValueError:
                                continue
            return False
        except Exception as e:
            print(f"Error checking for existing daemon: {e}")
            return False
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"aish daemon received signal {signum}, shutting down...")
        self.running = False
    
    def create_shared_memory(self):
        """Create the shared memory block."""
        try:
            # Try to create new shared memory
            self.shm_block = shared_memory.SharedMemory(name=self.shm_name, create=True, size=1024*1024)
            print(f"Created shared memory: {self.shm_name}")
            
            # Initialize with empty state including a test counter
            initial_state = {'test_counter': 0, 'daemon_start_time': time.time()}
            data = pickle.dumps(initial_state)
            
            # Clear the buffer and write initial data
            self.shm_block.buf[:] = b'\x00' * len(self.shm_block.buf)
            self.shm_block.buf[:len(data)] = data
            
            print(f"Initialized shared memory with test counter")
            return True
            
        except FileExistsError:
            # Shared memory already exists, try to connect
            try:
                self.shm_block = shared_memory.SharedMemory(name=self.shm_name)
                print(f"Connected to existing shared memory: {self.shm_name}")
                return True
            except Exception as e:
                print(f"Error connecting to existing shared memory: {e}")
                return False
                
        except Exception as e:
            print(f"Error creating shared memory: {e}")
            return False
    
    def run(self):
        """Run the daemon."""
        # Check if another daemon is already running
        if self.check_existing_daemon():
            sys.exit(0)
        
        # Set up signal handlers
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        print(f"Starting aish daemon for {self.tekton_root}")
        
        # Create shared memory
        if not self.create_shared_memory():
            print("Failed to create shared memory")
            sys.exit(1)
        
        print(f"aish daemon running (PID {os.getpid()})")
        
        try:
            # Main daemon loop - just keep the process alive
            while self.running:
                time.sleep(1)
                
                # Periodically check if shared memory is still valid
                if self.shm_block:
                    try:
                        # Try to read a byte to verify memory is accessible
                        _ = self.shm_block.buf[0]
                    except Exception as e:
                        print(f"Shared memory no longer accessible: {e}")
                        break
                        
        except KeyboardInterrupt:
            print("aish daemon interrupted")
        finally:
            # Cleanup
            if self.shm_block:
                try:
                    self.shm_block.close()
                    # Only unlink if we're shutting down cleanly
                    if not self.running:
                        try:
                            self.shm_block.unlink()
                            print(f"Unlinked shared memory: {self.shm_name}")
                        except:
                            pass
                except Exception as e:
                    print(f"Error during cleanup: {e}")
            
            print("aish daemon stopped")


def main():
    """Entry point for standalone daemon."""
    if len(sys.argv) != 2:
        print("Usage: python aish_daemon_simple.py <TEKTON_ROOT>")
        sys.exit(1)
    
    tekton_root = os.path.abspath(sys.argv[1])
    
    if not os.path.exists(tekton_root):
        print(f"Error: TEKTON_ROOT {tekton_root} does not exist")
        sys.exit(1)
    
    daemon = AishDaemon(tekton_root)
    daemon.run()


if __name__ == "__main__":
    main()