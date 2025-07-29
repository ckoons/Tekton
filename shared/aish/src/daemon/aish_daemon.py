"""
aish Shared Memory Daemon

This daemon manages the shared memory CI registry for a specific TEKTON_ROOT.
It ensures that CI output capture persists across aish command invocations.
"""

import os
import sys
import time
import signal
import hashlib
import threading
from pathlib import Path
from multiprocessing import shared_memory

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from registry.ci_registry import get_registry


class AishDaemon:
    """Daemon that manages shared memory CI registry for a Tekton installation."""
    
    def __init__(self, tekton_root: str):
        self.tekton_root = tekton_root
        self.tekton_hash = hashlib.md5(tekton_root.encode()).hexdigest()[:8]
        self.registry = None
        self.running = True
        
    def check_existing_daemon(self) -> bool:
        """Check if a daemon is already running for this TEKTON_ROOT using ps."""
        import subprocess
        try:
            # Look for existing aish daemon with this TEKTON_ROOT
            cmd = ['ps', 'aux']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Look for "aish -s /path/to/tekton/root" pattern
                pattern = f"aish -s {self.tekton_root}"
                for line in result.stdout.split('\n'):
                    if pattern in line and 'grep' not in line:
                        print(f"aish daemon already running for {self.tekton_root}")
                        return True
            return False
        except Exception as e:
            print(f"Error checking for existing daemon: {e}")
            return False
    
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"aish daemon received signal {signum}, shutting down...")
        self.running = False
    
    def monitor_components(self):
        """Monitor running components and exit when none are running."""
        while self.running:
            try:
                # Check if any components are running by looking at process list
                # Look for python processes running component modules
                import subprocess
                component_patterns = [
                    'python.*-m apollo',
                    'python.*-m athena', 
                    'python.*-m rhetor',
                    'python.*-m terma',
                    'python.*-m numa',
                    'python.*-m prometheus',
                    'python.*-m metis',
                    'python.*-m harmonia',
                    'python.*-m synthesis',
                    'python.*-m engram',
                    'python.*-m ergon',
                    'python.*-m penia',
                    'python.*-m hermes',
                    'python.*-m sophia',
                    'python.*-m noesis',
                    'python.*-m telos',
                    'python.*-m hephaestus'
                ]
                
                components_found = False
                for pattern in component_patterns:
                    result = subprocess.run(
                        ['pgrep', '-f', pattern],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:  # Found at least one component
                        components_found = True
                        break
                
                if not components_found:
                    # Wait a bit and check again to avoid race conditions
                    time.sleep(5)
                    components_found = False
                    for pattern in component_patterns:
                        result = subprocess.run(
                            ['pgrep', '-f', pattern],
                            capture_output=True,
                            text=True
                        )
                        if result.returncode == 0:
                            components_found = True
                            break
                    
                    if not components_found:
                        print("No Tekton components running, shutting down daemon")
                        self.running = False
                        break
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"Error monitoring components: {e}")
                time.sleep(10)
    
    def run(self):
        """Run the daemon."""
        # Check if another daemon is already running
        if self.check_existing_daemon():
            sys.exit(0)
        
        # Set up signal handlers
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        try:
            print(f"Starting aish daemon for {self.tekton_root}")
            
            # Initialize the CI registry (this creates/connects to shared memory)
            os.environ['TEKTON_ROOT'] = self.tekton_root
            self.registry = get_registry()
            
            print(f"aish daemon running (PID {os.getpid()})")
            
            # Start monitoring thread
            monitor_thread = threading.Thread(target=self.monitor_components, daemon=True)
            monitor_thread.start()
            
            # Main daemon loop - just keep the process alive
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("aish daemon interrupted")
        except Exception as e:
            print(f"aish daemon error: {e}")
        finally:
            # Close shared memory connection (but don't unlink - leave it for other processes)
            if self.registry:
                try:
                    # Get the shared memory block to close it properly
                    shm_block = getattr(self.registry, '_shm_block', None)
                    if shm_block:
                        shm_block.close()  # Close connection but don't unlink
                        print(f"Closed shared memory connection: {getattr(self.registry, '_shm_name', 'unknown')}")
                except Exception as cleanup_error:
                    print(f"Error closing shared memory: {cleanup_error}")
            
            print("aish daemon stopped")


def run_daemon(tekton_root: str):
    """Entry point for daemon mode."""
    # Ensure TEKTON_ROOT is absolute
    tekton_root = os.path.abspath(tekton_root)
    
    # Validate TEKTON_ROOT
    if not os.path.exists(tekton_root):
        print(f"Error: TEKTON_ROOT {tekton_root} does not exist")
        sys.exit(1)
    
    # Create and run daemon
    daemon = AishDaemon(tekton_root)
    daemon.run()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python aish_daemon.py <TEKTON_ROOT>")
        sys.exit(1)
    
    run_daemon(sys.argv[1])