"""
Base adapter class for CI tool integration.
All CI tool adapters must inherit from this class.
"""

import abc
import json
import logging
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, Optional, Any, List

try:
    from landmarks import architecture_decision, integration_point
except ImportError:
    def architecture_decision(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func):
            return func
        return decorator


@architecture_decision(
    title="CI Tool Adapter Base Class",
    description="Base adapter provides common interface for all CI tools",
    rationale="Ensures consistent behavior and simplifies tool integration",
    tags=["ci-tools", "adapter-pattern"]
)
class BaseCIToolAdapter(abc.ABC):
    """
    Abstract base class for CI tool adapters.
    
    Each CI tool (Claude Code, Cursor, etc.) must implement this interface
    to integrate with Tekton's socket-based communication system.
    """
    
    def __init__(self, tool_name: str, port: int, config: Dict[str, Any]):
        """
        Initialize the adapter.
        
        Args:
            tool_name: Unique identifier for the tool
            port: Port number for socket communication
            config: Tool-specific configuration
        """
        self.tool_name = tool_name
        self.port = port
        self.config = config
        self.process = None
        self.running = False
        self.logger = logging.getLogger(f"ci_tools.{tool_name}")
        
        # Session management
        self.sessions = {}
        self.current_session = None
        
        # Performance tracking
        self.metrics = {
            'messages_sent': 0,
            'messages_received': 0,
            'errors': 0,
            'start_time': None,
            'total_latency': 0
        }
    
    @abc.abstractmethod
    def get_executable_path(self) -> Optional[Path]:
        """
        Get the path to the tool's executable.
        
        Returns:
            Path to executable or None if not found
        """
        pass
    
    @abc.abstractmethod
    def get_launch_args(self, session_id: Optional[str] = None) -> List[str]:
        """
        Get command line arguments for launching the tool.
        
        Args:
            session_id: Optional session identifier
            
        Returns:
            List of command line arguments
        """
        pass
    
    @abc.abstractmethod
    def translate_to_tool(self, message: Dict[str, Any]) -> str:
        """
        Translate Tekton message format to tool-specific format.
        
        Args:
            message: Standard Tekton message
            
        Returns:
            Tool-specific command string
        """
        pass
    
    @abc.abstractmethod
    def translate_from_tool(self, output: str) -> Dict[str, Any]:
        """
        Translate tool output to Tekton message format.
        
        Args:
            output: Raw output from tool
            
        Returns:
            Standard Tekton message
        """
        pass
    
    @integration_point(
        title="CI Tool Launch",
        description="Launches CI tool process with proper environment",
        target_component="CI Tool Process",
        protocol="Subprocess"
    )
    def launch(self, session_id: Optional[str] = None) -> bool:
        """
        Launch the CI tool process.
        
        Args:
            session_id: Optional session identifier
            
        Returns:
            True if launch successful
        """
        if self.running:
            self.logger.warning(f"{self.tool_name} is already running")
            return True
        
        exe_path = self.get_executable_path()
        if not exe_path or not exe_path.exists():
            self.logger.error(f"Executable not found for {self.tool_name}")
            return False
        
        try:
            # Prepare environment
            env = self._prepare_environment(session_id)
            
            # Get launch arguments
            args = [str(exe_path)] + self.get_launch_args(session_id)
            
            self.logger.info(f"Launching {self.tool_name}: {' '.join(args)}")
            
            # Launch process
            self.process = subprocess.Popen(
                args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                bufsize=0  # Unbuffered
            )
            
            self.running = True
            self.current_session = session_id
            self.metrics['start_time'] = time.time()
            
            # Start output monitoring threads
            self._start_monitors()
            
            # Perform health check
            if not self._health_check():
                self.terminate()
                return False
            
            self.logger.info(f"{self.tool_name} launched successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to launch {self.tool_name}: {e}")
            self.metrics['errors'] += 1
            return False
    
    def send_message(self, message: Dict[str, Any]) -> bool:
        """
        Send a message to the tool.
        
        Args:
            message: Message to send
            
        Returns:
            True if sent successfully
        """
        if not self.running or not self.process:
            self.logger.error(f"{self.tool_name} is not running")
            return False
        
        try:
            # Translate to tool format
            tool_command = self.translate_to_tool(message)
            
            # Send to process stdin
            self.process.stdin.write(f"{tool_command}\n".encode())
            self.process.stdin.flush()
            
            self.metrics['messages_sent'] += 1
            self.logger.debug(f"Sent to {self.tool_name}: {tool_command}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            self.metrics['errors'] += 1
            return False
    
    def terminate(self) -> bool:
        """
        Terminate the tool process.
        
        Returns:
            True if terminated successfully
        """
        if not self.running or not self.process:
            return True
        
        try:
            # Send graceful shutdown if supported
            if hasattr(self, 'send_shutdown_command'):
                self.send_shutdown_command()
                time.sleep(1)  # Give it time to shutdown
            
            # Terminate process
            if self.process.poll() is None:
                self.process.terminate()
                self.process.wait(timeout=5)
            
            self.running = False
            self.process = None
            self.current_session = None
            
            self.logger.info(f"{self.tool_name} terminated")
            return True
            
        except subprocess.TimeoutExpired:
            # Force kill if needed
            self.process.kill()
            self.running = False
            self.process = None
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to terminate {self.tool_name}: {e}")
            return False
    
    def get_capabilities(self) -> Dict[str, bool]:
        """
        Get tool capabilities.
        
        Returns:
            Dictionary of capability flags
        """
        return self.config.get('capabilities', {})
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current tool status.
        
        Returns:
            Status information
        """
        status = {
            'running': self.running,
            'session': self.current_session,
            'pid': self.process.pid if self.process else None,
            'uptime': None,
            'metrics': self.metrics
        }
        
        if self.running and self.metrics['start_time']:
            status['uptime'] = time.time() - self.metrics['start_time']
        
        return status
    
    def _prepare_environment(self, session_id: Optional[str]) -> Dict[str, str]:
        """Prepare environment variables for tool launch."""
        import os
        env = os.environ.copy()
        
        # Add Tekton-specific variables
        env['TEKTON_CI_TOOL'] = self.tool_name
        env['TEKTON_CI_PORT'] = str(self.port)
        
        if session_id:
            env['TEKTON_SESSION_ID'] = session_id
        
        # Add tool-specific environment
        tool_env = self.config.get('environment', {})
        env.update(tool_env)
        
        return env
    
    def _start_monitors(self):
        """Start threads to monitor stdout and stderr."""
        def monitor_stdout():
            for line in iter(self.process.stdout.readline, b''):
                if line:
                    self._handle_output(line.decode().strip())
        
        def monitor_stderr():
            for line in iter(self.process.stderr.readline, b''):
                if line:
                    self._handle_error(line.decode().strip())
        
        stdout_thread = threading.Thread(target=monitor_stdout, daemon=True)
        stderr_thread = threading.Thread(target=monitor_stderr, daemon=True)
        
        stdout_thread.start()
        stderr_thread.start()
    
    def _handle_output(self, output: str):
        """Handle output from tool stdout."""
        try:
            # Translate and store
            message = self.translate_from_tool(output)
            self.metrics['messages_received'] += 1
            
            # Override in subclass to handle output
            self.on_output(message)
            
        except Exception as e:
            self.logger.error(f"Error handling output: {e}")
            self.metrics['errors'] += 1
    
    def _handle_error(self, error: str):
        """Handle output from tool stderr."""
        self.logger.error(f"{self.tool_name} error: {error}")
        self.on_error(error)
    
    def _health_check(self) -> bool:
        """Perform health check after launch."""
        # Default implementation - override in subclass
        time.sleep(0.5)  # Give process time to start
        return self.process.poll() is None
    
    # Override these in subclasses
    def on_output(self, message: Dict[str, Any]):
        """Override to handle tool output."""
        pass
    
    def on_error(self, error: str):
        """Override to handle tool errors."""
        pass