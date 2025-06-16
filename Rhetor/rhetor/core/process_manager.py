"""
Process management for Rhetor's AI model subprocesses.
Ensures all child processes are properly tracked and terminated on shutdown.
"""

import os
import signal
import subprocess
import atexit
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import psutil

logger = logging.getLogger(__name__)


@dataclass
class ManagedProcess:
    """Information about a managed subprocess"""
    name: str
    process: subprocess.Popen
    started_at: datetime
    command: List[str]
    metadata: Dict[str, Any]


class ProcessManager:
    """
    Manages child AI processes spawned by Rhetor.
    
    Ensures all children are in the same process group and handles
    graceful shutdown of all processes when Rhetor terminates.
    """
    
    def __init__(self):
        self.processes: Dict[int, ManagedProcess] = {}
        self.pgid = os.getpgid(os.getpid())  # Our process group ID
        
        # Register shutdown handlers
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        atexit.register(self._cleanup_all)
        
        logger.info(f"ProcessManager initialized with PGID: {self.pgid}")
    
    def spawn_model(
        self, 
        name: str,
        command: List[str],
        env: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ManagedProcess:
        """
        Spawn a new AI model process as part of our process group.
        
        Args:
            name: Friendly name for the process
            command: Command and arguments to execute
            env: Optional environment variables
            metadata: Optional metadata about the process
            
        Returns:
            ManagedProcess object with process information
        """
        logger.info(f"Spawning AI model: {name} with command: {command}")
        
        # Merge environment variables
        process_env = os.environ.copy()
        if env:
            process_env.update(env)
        
        # Add process group info to environment
        process_env['RHETOR_PGID'] = str(self.pgid)
        process_env['RHETOR_MODEL_NAME'] = name
        
        try:
            # Spawn process in our process group
            process = subprocess.Popen(
                command,
                env=process_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                # Keep in same process group (don't create new session)
                preexec_fn=None
            )
            
            # Create managed process record
            managed = ManagedProcess(
                name=name,
                process=process,
                started_at=datetime.now(),
                command=command,
                metadata=metadata or {}
            )
            
            # Track the process
            self.processes[process.pid] = managed
            
            logger.info(f"Successfully spawned {name} with PID: {process.pid}")
            return managed
            
        except Exception as e:
            logger.error(f"Failed to spawn {name}: {e}")
            raise
    
    def terminate_process(self, pid: int, timeout: float = 5.0) -> bool:
        """
        Gracefully terminate a specific process.
        
        Args:
            pid: Process ID to terminate
            timeout: Seconds to wait for graceful shutdown
            
        Returns:
            True if process terminated successfully
        """
        if pid not in self.processes:
            logger.warning(f"PID {pid} not in managed processes")
            return False
        
        managed = self.processes[pid]
        process = managed.process
        
        if process.poll() is not None:
            # Already terminated
            del self.processes[pid]
            return True
        
        logger.info(f"Terminating {managed.name} (PID: {pid})")
        
        try:
            # Try graceful termination first
            process.terminate()
            process.wait(timeout=timeout)
            logger.info(f"{managed.name} terminated gracefully")
            
        except subprocess.TimeoutExpired:
            # Force kill if graceful shutdown failed
            logger.warning(f"{managed.name} did not terminate gracefully, force killing")
            process.kill()
            process.wait()
        
        del self.processes[pid]
        return True
    
    def get_active_processes(self) -> List[ManagedProcess]:
        """Get list of currently active processes"""
        active = []
        
        # Clean up terminated processes
        terminated = []
        for pid, managed in self.processes.items():
            if managed.process.poll() is None:
                active.append(managed)
            else:
                terminated.append(pid)
        
        # Remove terminated processes from tracking
        for pid in terminated:
            del self.processes[pid]
        
        return active
    
    def get_process_stats(self) -> Dict[str, Any]:
        """Get statistics about managed processes"""
        active = self.get_active_processes()
        
        stats = {
            'active_count': len(active),
            'total_spawned': len(self.processes) + len(active),
            'processes': []
        }
        
        for managed in active:
            try:
                proc = psutil.Process(managed.process.pid)
                stats['processes'].append({
                    'name': managed.name,
                    'pid': managed.process.pid,
                    'cpu_percent': proc.cpu_percent(),
                    'memory_mb': proc.memory_info().rss / 1024 / 1024,
                    'runtime_seconds': (datetime.now() - managed.started_at).total_seconds()
                })
            except psutil.NoSuchProcess:
                pass
        
        return stats
    
    def _handle_signal(self, signum: int, frame: Any):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating shutdown of all AI processes")
        self._cleanup_all()
        
        # Re-raise the signal to continue shutdown
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)
    
    def _cleanup_all(self):
        """Terminate all managed processes"""
        if not self.processes:
            return
        
        logger.info(f"Cleaning up {len(self.processes)} AI processes")
        
        # First pass: graceful termination
        for pid, managed in list(self.processes.items()):
            if managed.process.poll() is None:
                logger.info(f"Terminating {managed.name} (PID: {pid})")
                managed.process.terminate()
        
        # Wait up to 5 seconds for graceful shutdown
        import time
        deadline = time.time() + 5.0
        
        while time.time() < deadline and self.processes:
            for pid in list(self.processes.keys()):
                managed = self.processes[pid]
                if managed.process.poll() is not None:
                    # Process terminated
                    del self.processes[pid]
            
            if self.processes:
                time.sleep(0.1)
        
        # Second pass: force kill any remaining
        for pid, managed in list(self.processes.items()):
            if managed.process.poll() is None:
                logger.warning(f"Force killing {managed.name} (PID: {pid})")
                managed.process.kill()
                managed.process.wait()
        
        self.processes.clear()
        logger.info("All AI processes terminated")


# Global instance for easy access
_process_manager: Optional[ProcessManager] = None


def get_process_manager() -> ProcessManager:
    """Get or create the global process manager instance"""
    global _process_manager
    if _process_manager is None:
        _process_manager = ProcessManager()
    return _process_manager