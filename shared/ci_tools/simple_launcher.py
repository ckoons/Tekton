"""
Simple Tool Launcher - No singletons, uses C launcher and filesystem.
"""

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Dict, Optional, Any

from .base_adapter import BaseCIToolAdapter
from .socket_bridge import SocketBridge
from .adapters import ClaudeCodeAdapter, GenericAdapter


class SimpleToolLauncher:
    """
    Simple tool launcher that uses filesystem for state.
    Each instance is independent - no singleton pattern.
    """
    
    def __init__(self):
        """Initialize launcher with paths."""
        self.logger = logging.getLogger("ci_tools.launcher")
        
        # Set up paths
        tekton_root = os.environ.get('TEKTON_ROOT', os.getcwd())
        self.base_dir = Path(tekton_root) / '.tekton' / 'ci_tools'
        self.running_dir = self.base_dir / 'running'
        self.running_dir.mkdir(parents=True, exist_ok=True)
        
        # Load tool configurations
        self.tools_file = self.base_dir / 'tools.json'
        self.tools_config = self._load_tools_config()
    
    def _load_tools_config(self) -> Dict[str, Any]:
        """Load tool configurations from file."""
        if self.tools_file.exists():
            with open(self.tools_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _write_pid_file(self, tool_name: str, pid: int, port: int, session_id: Optional[str] = None):
        """Write PID file for running tool."""
        pid_file = self.running_dir / f"{tool_name}.json"
        import time
        info = {
            'pid': pid,
            'port': port,
            'session_id': session_id,
            'start_time': time.time()
        }
        with open(pid_file, 'w') as f:
            json.dump(info, f)
    
    def _read_pid_file(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Read PID file for tool."""
        pid_file = self.running_dir / f"{tool_name}.json"
        if pid_file.exists():
            try:
                with open(pid_file, 'r') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def _remove_pid_file(self, tool_name: str):
        """Remove PID file."""
        pid_file = self.running_dir / f"{tool_name}.json"
        if pid_file.exists():
            pid_file.unlink()
    
    def _is_process_running(self, pid: int) -> bool:
        """Check if process is running."""
        try:
            os.kill(pid, 0)
            return True
        except (ProcessLookupError, PermissionError, OSError):
            return False
    
    def _find_available_port(self, start_port: int = 50000) -> int:
        """Find an available port."""
        import socket
        for port in range(start_port, 60000):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('', port))
                    return port
                except:
                    continue
        raise RuntimeError("No available ports")
    
    def launch_tool(self, tool_name: str, session_id: Optional[str] = None, instance_name: Optional[str] = None) -> bool:
        """
        Launch a CI tool using C launcher.
        """
        launch_key = instance_name or tool_name
        
        # Check if already running
        pid_info = self._read_pid_file(launch_key)
        if pid_info and self._is_process_running(pid_info['pid']):
            self.logger.info(f"{launch_key} is already running (PID: {pid_info['pid']})")
            return True
        
        # Get tool configuration
        tool_config = self.tools_config.get(tool_name)
        if not tool_config:
            self.logger.error(f"Unknown tool: {tool_name}")
            return False
        
        # Allocate port
        port = tool_config.get('port')
        if port == 'auto' or port is None:
            port = self._find_available_port()
            self.logger.info(f"Allocated port {port} for {tool_name}")
        
        # Create socket bridge first
        bridge = SocketBridge(tool_name, port)
        if not bridge.start():
            self.logger.error(f"Failed to start socket bridge for {tool_name}")
            return False
        
        # Use C launcher WITHOUT socket mode for now
        launcher_path = Path(__file__).parent / 'bin' / 'ci_tool_launcher'
        if not launcher_path.exists():
            self.logger.error(f"C launcher not found at {launcher_path}")
            bridge.stop()
            return False
        
        # Build command - NO --port option so it uses stdio mode
        cmd = [
            str(launcher_path),
            '--tool', tool_name,
            '--executable', tool_config.get('executable', 'python')
        ]
        
        # Add launch args
        launch_args = tool_config.get('launch_args', [])
        if launch_args:
            cmd.append('--args')
            cmd.extend(launch_args)
        
        # Set environment
        env = os.environ.copy()
        env['TEKTON_CI_TOOL'] = tool_name
        env['TEKTON_CI_PORT'] = str(port)
        if session_id:
            env['TEKTON_SESSION_ID'] = session_id
        
        # Add tool-specific environment
        tool_env = tool_config.get('environment', {})
        env.update(tool_env)
        
        try:
            # Launch with C launcher
            self.logger.info(f"Launching {tool_name} with C launcher: {' '.join(cmd)}")
            process = subprocess.Popen(cmd, env=env)
            
            # Write PID file
            try:
                self._write_pid_file(launch_key, process.pid, port, session_id)
                self.logger.info(f"Wrote PID file for {launch_key}")
            except Exception as e:
                self.logger.error(f"Failed to write PID file: {e}")
            
            self.logger.info(f"Successfully launched {tool_name} (PID: {process.pid}, Port: {port})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to launch {tool_name}: {e}")
            bridge.stop()
            return False
    
    def terminate_tool(self, tool_name: str) -> bool:
        """
        Terminate a CI tool.
        """
        pid_info = self._read_pid_file(tool_name)
        if not pid_info:
            self.logger.info(f"No PID file for {tool_name}")
            return True
        
        pid = pid_info['pid']
        if not self._is_process_running(pid):
            self.logger.info(f"{tool_name} not running, cleaning up")
            self._remove_pid_file(tool_name)
            return True
        
        try:
            # Send SIGTERM
            os.kill(pid, 15)
            self.logger.info(f"Sent SIGTERM to {tool_name} (PID: {pid})")
            
            # Wait a bit
            import time
            for _ in range(50):  # 5 seconds
                if not self._is_process_running(pid):
                    break
                time.sleep(0.1)
            
            # Force kill if needed
            if self._is_process_running(pid):
                os.kill(pid, 9)
                self.logger.warning(f"Force killed {tool_name} (PID: {pid})")
            
            self._remove_pid_file(tool_name)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to terminate {tool_name}: {e}")
            return False
    
    def get_running_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get all running tools."""
        running = {}
        
        for pid_file in self.running_dir.glob("*.json"):
            tool_name = pid_file.stem
            pid_info = self._read_pid_file(tool_name)
            
            if pid_info:
                pid = pid_info['pid']
                if self._is_process_running(pid):
                    running[tool_name] = pid_info
                else:
                    # Clean up stale PID file
                    self._remove_pid_file(tool_name)
        
        return running
    
    def get_tool_status(self, tool_name: str) -> Dict[str, Any]:
        """Get status for a specific tool."""
        pid_info = self._read_pid_file(tool_name)
        
        if not pid_info:
            return {'running': False, 'tool': tool_name}
        
        if self._is_process_running(pid_info['pid']):
            status = {
                'running': True,
                'tool': tool_name,
                'pid': pid_info['pid'],
                'port': pid_info['port'],
                'session': pid_info.get('session_id', 'default')
            }
            
            # Calculate uptime if start_time available
            if pid_info.get('start_time'):
                import time
                status['uptime'] = time.time() - pid_info['start_time']
            
            return status
        else:
            # Clean up stale PID file
            self._remove_pid_file(tool_name)
            return {'running': False, 'tool': tool_name}