"""
Base adapter class for CI tool integration.
All CI tool adapters must inherit from this class.
"""

import abc
import json
import logging
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, Optional, Any, List

try:
    from landmarks import (
        architecture_decision, 
        integration_point,
        state_checkpoint
    )
except ImportError:
    def architecture_decision(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func):
            return func
        return decorator


@architecture_decision(
    title="CI Tool Adapter Base Class",
    description="Base adapter provides common interface for all CI tools",
    rationale="Ensures consistent behavior and simplifies tool integration",
    alternatives_considered=["Direct subprocess management", "Tool-specific implementations", "External tool managers"],
    impacts=["tool_integration", "socket_communication", "lifecycle_management"],
    decided_by="Casey",
    decision_date="2025-08-02"
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
        protocol="Subprocess",
        data_flow="adapter.launch() → subprocess.Popen → tool process → socket bridge",
        integration_date="2025-08-02"
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
        self.logger.debug(f"Executable path for {self.tool_name}: {exe_path}")
        if not exe_path or not exe_path.exists():
            self.logger.error(f"Executable not found for {self.tool_name} at path: {exe_path}")
            return False
        
        try:
            # Prepare environment
            env = self._prepare_environment(session_id)
            self.logger.debug(f"Environment prepared with {len(env)} variables")
            
            # Get launch arguments
            args = [str(exe_path)] + self.get_launch_args(session_id)
            
            self.logger.info(f"Launching {self.tool_name}: {' '.join(args)}")
            self.logger.debug(f"Working directory: {os.getcwd()}")
            
            # Launch process
            self.logger.debug("Creating subprocess.Popen...")
            self.process = subprocess.Popen(
                args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                bufsize=-1  # Use default buffering
            )
            
            self.logger.debug(f"Process created with PID: {self.process.pid}")
            
            # Check if process started properly
            time.sleep(0.1)  # Brief pause to let process initialize
            poll_result = self.process.poll()
            if poll_result is not None:
                self.logger.error(f"Process exited immediately with code: {poll_result}")
                # Try to read any error output
                try:
                    stderr_output = self.process.stderr.read().decode()
                    if stderr_output:
                        self.logger.error(f"Process stderr: {stderr_output}")
                except:
                    pass
                return False
            
            self.running = True
            self.current_session = session_id
            self.metrics['start_time'] = time.time()
            
            # Keep a reference to stdin to prevent garbage collection
            self._stdin = self.process.stdin
            self.logger.debug(f"stdin pipe: {self._stdin}")
            
            # Ensure stdin stays open - write a newline to establish the pipe
            # This prevents immediate EOF in the child process
            try:
                self._stdin.write(b'\n')
                self._stdin.flush()
                self.logger.debug("Sent initial newline to keep stdin alive")
            except Exception as e:
                self.logger.warning(f"Could not send initial newline to stdin: {e}")
            
            self.logger.debug("Starting monitor threads...")
            # Start output monitoring threads
            self._start_monitors()
            
            self.logger.debug("Performing health check...")
            # Perform health check
            if not self._health_check():
                self.logger.error("Health check failed")
                self.terminate()
                return False
            
            self.logger.info(f"{self.tool_name} launched successfully with PID {self.process.pid}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to launch {self.tool_name}: {e}", exc_info=True)
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
            
            # Send to process stdin (use stored reference)
            if hasattr(self, '_stdin') and self._stdin:
                self._stdin.write(f"{tool_command}\n".encode())
                self._stdin.flush()
            else:
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
            self.logger.debug(f"Starting stdout monitor thread for {self.tool_name}")
            try:
                for line in iter(self.process.stdout.readline, b''):
                    if line:
                        decoded_line = line.decode().strip()
                        self.logger.debug(f"stdout: {decoded_line}")
                        self._handle_output(decoded_line)
                    else:
                        self.logger.debug("Empty line received from stdout")
                self.logger.debug("stdout monitor thread exiting - stream closed")
            except Exception as e:
                self.logger.error(f"Error in stdout monitor: {e}", exc_info=True)
        
        def monitor_stderr():
            self.logger.debug(f"Starting stderr monitor thread for {self.tool_name}")
            try:
                for line in iter(self.process.stderr.readline, b''):
                    if line:
                        decoded_line = line.decode().strip()
                        self.logger.debug(f"stderr: {decoded_line}")
                        self._handle_error(decoded_line)
                    else:
                        self.logger.debug("Empty line received from stderr")
                self.logger.debug("stderr monitor thread exiting - stream closed")
            except Exception as e:
                self.logger.error(f"Error in stderr monitor: {e}", exc_info=True)
        
        stdout_thread = threading.Thread(target=monitor_stdout, daemon=True, name=f"{self.tool_name}-stdout")
        stderr_thread = threading.Thread(target=monitor_stderr, daemon=True, name=f"{self.tool_name}-stderr")
        
        stdout_thread.start()
        stderr_thread.start()
        self.logger.debug(f"Monitor threads started: {stdout_thread.name}, {stderr_thread.name}")
    
    @state_checkpoint(
        title="Tool Output Processing",
        description="Processes and translates tool output maintaining message state",
        state_type="message_flow",
        persistence=False,
        consistency_requirements="Ordered message delivery, no dropped messages",
        recovery_strategy="Log errors and continue processing"
    )
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
        # Check if tool defines no health check
        if self.config.get('health_check') == 'none':
            self.logger.debug("Health check disabled by config")
            return True
            
        # Default implementation - override in subclass
        self.logger.debug("Performing default health check...")
        time.sleep(0.5)  # Give process time to start
        poll_result = self.process.poll()
        if poll_result is None:
            self.logger.debug(f"Health check passed - process still running (PID: {self.process.pid})")
            return True
        else:
            self.logger.error(f"Health check failed - process exited with code: {poll_result}")
            # Try to capture any final output
            try:
                remaining_stdout = self.process.stdout.read().decode()
                remaining_stderr = self.process.stderr.read().decode()
                if remaining_stdout:
                    self.logger.error(f"Remaining stdout: {remaining_stdout}")
                if remaining_stderr:
                    self.logger.error(f"Remaining stderr: {remaining_stderr}")
            except:
                pass
            return False
    
    # Override these in subclasses
    def on_output(self, message: Dict[str, Any]):
        """Override to handle tool output."""
        pass
    
    def on_error(self, error: str):
        """Override to handle tool errors."""
        pass