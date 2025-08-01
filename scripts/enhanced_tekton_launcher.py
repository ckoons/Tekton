#!/usr/bin/env python3
"""
Enhanced Tekton Component Launcher - Next Generation

Advanced launcher with health monitoring, auto-recovery, and improved reliability.
Now with proper logging to $TEKTON_ROOT/.tekton/logs/
"""
import os
import sys
import asyncio
import subprocess
import argparse
import signal
import time
import psutil
import aiohttp
import json
from typing import List, Dict, Optional, Set, Tuple, Any
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from enum import Enum
import platform
from datetime import datetime, timedelta
import threading
import queue
from pathlib import Path

# Find the Tekton root directory by looking for a marker file
def find_tekton_root():
    """Find the Tekton root directory by looking for marker files"""
    # If __file__ is a symlink, resolve it first
    script_path = os.path.realpath(__file__)
    current_dir = os.path.dirname(script_path)
    
    # Look for Tekton root markers
    markers = ['setup.py', 'tekton', 'README.md']
    
    while current_dir != '/':
        # Check if all markers exist in this directory
        if all(os.path.exists(os.path.join(current_dir, marker)) for marker in markers):
            # Additional check: make sure tekton is a directory
            if os.path.isdir(os.path.join(current_dir, 'tekton')):
                return current_dir
        
        # Move up one directory
        parent = os.path.dirname(current_dir)
        if parent == current_dir:  # Reached root
            break
        current_dir = parent
    
    # Fallback: check TEKTON_ROOT env variable
    if 'TEKTON_ROOT' in os.environ:
        return os.environ['TEKTON_ROOT']
    
    raise RuntimeError("Could not find Tekton root directory. Please set TEKTON_ROOT environment variable.")

# Add Tekton root to Python path
tekton_root = find_tekton_root()
sys.path.insert(0, tekton_root)

# Check if environment is loaded
from shared.env import TektonEnviron
if not TektonEnviron.is_loaded():
    # We're running as a subprocess with environment passed via env=
    # The environment is already correct, just not "loaded" in Python's memory
    # Don't exit - just continue
    pass
else:
    # Use frozen environment if loaded
    os.environ = TektonEnviron.all()

from tekton.utils.component_config import get_component_config
from shared.utils.env_config import get_component_config as get_env_config
from tekton.utils.port_config import get_component_port
from landmarks import architecture_decision, performance_boundary, integration_point, danger_zone


class ComponentState(Enum):
    """Component state enumeration"""
    NOT_RUNNING = "not_running"
    STARTING = "starting"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    FAILED = "failed"
    STOPPED = "stopped"


@dataclass
class LaunchResult:
    """Result of a component launch operation"""
    component_name: str
    success: bool
    state: ComponentState
    pid: Optional[int] = None
    port: Optional[int] = None
    message: str = ""
    startup_time: float = 0.0
    health_check_time: Optional[float] = None
    error: Optional[str] = None
    log_file: Optional[str] = None


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    component_name: str
    healthy: bool
    response_time: float
    status_code: Optional[int] = None
    version: Optional[str] = None
    details: Dict[str, Any] = None
    error: Optional[str] = None
    endpoint: Optional[str] = None


class LogReader(threading.Thread):
    """Background thread to read from a stream and write to log file"""
    
    def __init__(self, stream, log_file, component_name, stream_name="output"):
        super().__init__(daemon=True)
        self.stream = stream
        self.log_file = log_file
        self.component_name = component_name
        self.stream_name = stream_name
        self.running = True
        
    def run(self):
        """Read lines from stream and write to log file"""
        import re
        
        # Compile regex patterns once
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        python_log_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(.+)')
        
        try:
            while self.running:
                line = self.stream.readline()
                if not line:
                    break
                    
                # Decode and strip trailing newline
                decoded_line = line.decode('utf-8', errors='replace').rstrip('\n')
                
                # Strip ANSI color codes
                clean_line = ansi_escape.sub('', decoded_line)
                
                # Skip empty lines
                if not clean_line.strip():
                    self.log_file.write('\n')
                    self.log_file.flush()
                    continue
                
                # Detect if it's a Python log line (has timestamp + formatted content)
                match = python_log_pattern.match(clean_line)
                
                if match:
                    # It's already a Python log with timestamp - preserve as-is
                    log_line = clean_line + '\n'
                else:
                    # Add timestamp and source prefix
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    source = "STDERR" if self.stream_name == "stderr" else "STDOUT"
                    log_line = f"{timestamp} [{source}] {clean_line}\n"
                
                self.log_file.write(log_line)
                self.log_file.flush()
                
                # Also print to console if verbose (for errors)
                if self.stream_name == "stderr" and "ERROR" in clean_line:
                    print(f"[{self.component_name}] ERROR: {clean_line}")
                    
        except Exception as e:
            print(f"[{self.component_name}] Log reader error: {e}")
        finally:
            self.running = False


@architecture_decision(
    title="Enhanced component launcher",
    rationale="Centralized launcher with health monitoring, auto-recovery, and proper logging for all Tekton components",
    alternatives_considered=["Manual component startup", "systemd services", "Docker Compose"],
    decided_by="team"
)
@integration_point(
    title="Component startup orchestration",
    target_component="All Tekton components",
    protocol="Process management",
    data_flow="Launcher → Component processes → Health checks → Logs"
)
class EnhancedComponentLauncher:
    """Advanced component launcher with monitoring and recovery"""
    
    def __init__(self, verbose: bool = False, health_check_retries: int = 3):
        self.verbose = verbose
        self.health_check_retries = health_check_retries
        self.config = get_component_config()
        self.launched_components: Dict[str, LaunchResult] = {}
        self.health_monitor_task: Optional[asyncio.Task] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.log_readers: List[LogReader] = []
        
        # Setup log directory
        self.tekton_root = tekton_root  # Use the globally found tekton_root
        self.log_dir = os.environ.get('TEKTON_LOG_DIR', 
                                      os.path.join(self.tekton_root, ".tekton", "logs"))
        os.makedirs(self.log_dir, exist_ok=True)
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            connector=aiohttp.TCPConnector(limit=50)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
        if self.health_monitor_task:
            self.health_monitor_task.cancel()
            
        # Stop all log readers
        for reader in self.log_readers:
            reader.running = False
            
    def log(self, message: str, level: str = "info", component: str = None):
        """Enhanced logging with component context"""
        symbols = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "launch": "🚀",
            "health": "🏥",
            "monitor": "👁️",
            "log": "📋"
        }
        symbol = symbols.get(level, "•")
        timestamp = datetime.now().strftime("%H:%M:%S")
        comp_prefix = f"[{component}] " if component else ""
        print(f"{symbol} {timestamp} {comp_prefix}{message}")
        
    def get_log_file_path(self, component_name: str) -> str:
        """Get the log file path for a component"""
        return os.path.join(self.log_dir, f"{component_name}.log")
        
    @danger_zone(
        title="Health check retry logic",
        risk_level="medium",
        risks=["false_positives", "startup_delays"],
        mitigation="Multiple endpoint attempts with exponential backoff",
        review_required=True
    )
    async def enhanced_health_check(self, component_name: str, port: int) -> HealthCheckResult:
        """Enhanced health check with multiple endpoints and retries"""
        start_time = time.time()

        # Try multiple health endpoints in order of preference
        health_endpoints = ["/health", "/api/health", "/status", "/api/status", "/"]

        for attempt in range(self.health_check_retries):
            # Try each endpoint until one works
            for endpoint in health_endpoints:
                try:
                    url = f"http://localhost:{port}{endpoint}"

                    async with self.session.get(url) as resp:
                        response_time = time.time() - start_time

                        if resp.status == 200:
                            try:
                                data = await resp.json()
                                return HealthCheckResult(
                                    component_name=component_name,
                                    healthy=True,
                                    response_time=response_time,
                                    status_code=resp.status,
                                    version=data.get("version", "unknown"),
                                    details=data,
                                    endpoint=endpoint
                                )
                            except json.JSONDecodeError:
                                # Health endpoint returns non-JSON but is responsive
                                return HealthCheckResult(
                                    component_name=component_name,
                                    healthy=True,
                                    response_time=response_time,
                                    status_code=resp.status,
                                    endpoint=endpoint
                                )
                        elif resp.status in [404, 405]:
                            # Try next endpoint
                            continue
                        else:
                            # Bad status, but only return error on last attempt/endpoint
                            if attempt == self.health_check_retries - 1 and endpoint == health_endpoints[-1]:
                                return HealthCheckResult(
                                    component_name=component_name,
                                    healthy=False,
                                    response_time=response_time,
                                    status_code=resp.status,
                                    error=f"HTTP {resp.status}",
                                    endpoint=endpoint
                                )

                except (aiohttp.ClientConnectorError, ConnectionRefusedError):
                    # Connection refused - try next endpoint or retry
                    continue
                except asyncio.TimeoutError:
                    # Timeout - try next endpoint
                    continue
                except Exception as e:
                    # Other error - try next endpoint
                    continue

            # If we're here, no endpoint worked this attempt
            if attempt == self.health_check_retries - 1:
                return HealthCheckResult(
                    component_name=component_name,
                    healthy=False,
                    response_time=time.time() - start_time,
                    error=f"No working endpoint found among {health_endpoints}"
                )

            # Wait before retry
            if attempt < self.health_check_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

        # Should never reach here, but just in case
        return HealthCheckResult(
            component_name=component_name,
            healthy=False,
            response_time=time.time() - start_time,
            error="All retries failed"
        )
        
    async def wait_for_healthy(self, component_name: str, port: int, timeout: int = 10) -> bool:
        """Wait for component to become healthy with progress updates"""
        start_time = time.time()
        last_update = 0

        # Start with shorter intervals for faster feedback
        check_interval = 0.5  # Check every 500ms initially

        while time.time() - start_time < timeout:
            health = await self.enhanced_health_check(component_name, port)

            if health.healthy:
                self.log(
                    f"Health check passed in {health.response_time:.3f}s",
                    "health",
                    component_name
                )
                return True

            # Progress update every 3 seconds (faster feedback)
            elapsed = time.time() - start_time
            if elapsed - last_update >= 3:
                remaining = max(0, timeout - elapsed)  # Don't show negative time
                if remaining > 0:
                    self.log(
                        f"Waiting for health check ({remaining:.0f}s remaining)...",
                        "info",
                        component_name
                    )
                else:
                    self.log(
                        f"Waiting for health check (timeout imminent)...",
                        "warning",
                        component_name
                    )
                last_update = elapsed

            await asyncio.sleep(check_interval)

        return False
    
    def is_port_in_use(self, port: int) -> bool:
        """Check if a port is in use"""
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Try to bind to the port
            sock.bind(('', port))
            sock.close()
            return False  # Port is free
        except OSError:
            return True  # Port is in use
    
    async def launch_ui_devtools_mcp(self) -> LaunchResult:
        """Launch the UI DevTools MCP server"""
        launch_start = time.time()
        # Get port from environment
        port = int(TektonEnviron.get('HEPHAESTUS_MCP_PORT', '8088'))
        
        # Check if already running
        if not self.check_port_available(port):
            health = await self.enhanced_health_check("ui_dev_tools", port)
            if health.healthy:
                self.log(f"Already running and healthy", "success", "ui_dev_tools")
                result = LaunchResult(
                    component_name="ui_dev_tools",
                    success=True,
                    state=ComponentState.HEALTHY,
                    port=port,
                    message=f"Already running on port {port}",
                    startup_time=0,
                    health_check_time=health.response_time,
                    log_file=self.get_log_file_path("ui_dev_tools")
                )
                # Register with monitoring so it counts as successful
                self.launched_components["ui_dev_tools"] = result
                return result
            else:
                # Kill unhealthy process
                self.log(f"Killing unhealthy process on port {port}", "warning", "ui_dev_tools")
                if not self.kill_port_process(port):
                    return LaunchResult(
                        component_name="ui_dev_tools",
                        success=False,
                        state=ComponentState.FAILED,
                        message=f"Could not free port {port}",
                        startup_time=time.time() - launch_start
                    )
                await asyncio.sleep(2)
        
        # Get the run script path
        hephaestus_dir = os.path.join(self.tekton_root, "Hephaestus")
        run_script = os.path.join(hephaestus_dir, "run_mcp.sh")
        
        if not os.path.exists(run_script):
            return LaunchResult(
                component_name="ui_dev_tools",
                success=False,
                state=ComponentState.FAILED,
                message=f"Run script not found: {run_script}",
                startup_time=time.time() - launch_start
            )
        
        # Set environment variables
        env = os.environ.copy()
        env["UI_DEV_TOOLS_PORT"] = str(port)
        
        # Add Tekton root to PYTHONPATH
        current_pythonpath = env.get('PYTHONPATH', '')
        if current_pythonpath:
            env['PYTHONPATH'] = f"{self.tekton_root}:{current_pythonpath}"
        else:
            env['PYTHONPATH'] = self.tekton_root
        
        # Open log file
        log_file_path = self.get_log_file_path("ui_dev_tools")
        log_file = open(log_file_path, 'a')
        
        # Write launch header to log
        log_file.write(f"\n{'='*60}\n")
        log_file.write(f"Component: ui_dev_tools\n")
        log_file.write(f"Started: {datetime.now()}\n")
        log_file.write(f"Command: bash {run_script}\n")
        log_file.write(f"Directory: {hephaestus_dir}\n")
        log_file.write(f"Port: {port}\n")
        log_file.write(f"{'='*60}\n\n")
        log_file.flush()
        
        # Launch the MCP server
        if self.verbose:
            self.log(f"Executing: bash {run_script}", "launch", "ui_dev_tools")
        
        # Use subprocess.Popen with PIPE to capture output
        if platform.system() == "Windows":
            process = subprocess.Popen(
                ["bash", run_script],
                cwd=hephaestus_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            process = subprocess.Popen(
                ["bash", run_script],
                cwd=hephaestus_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )
        
        # Start log reader threads
        stdout_reader = LogReader(process.stdout, log_file, "ui_dev_tools", "stdout")
        stderr_reader = LogReader(process.stderr, log_file, "ui_dev_tools", "stderr")
        stdout_reader.start()
        stderr_reader.start()
        
        # Keep track of readers for cleanup
        self.log_readers.extend([stdout_reader, stderr_reader])
        
        # Check if process started successfully
        await asyncio.sleep(1)
        if process.poll() is not None:
            # Process exited immediately
            stdout_reader.join(timeout=1)
            stderr_reader.join(timeout=1)
            
            # Read last few lines from log file for error message
            log_file.close()
            with open(log_file_path, 'r') as f:
                lines = f.readlines()
                error_lines = lines[-10:] if len(lines) > 10 else lines
                error_msg = ''.join(error_lines)
            
            return LaunchResult(
                component_name="ui_dev_tools",
                success=False,
                state=ComponentState.FAILED,
                message=f"Process exited immediately: {error_msg[-200:]}",
                error=error_msg[-500:],
                log_file=log_file_path
            )
        
        # Wait for it to become healthy
        self.log(f"Waiting for health check...", "info", "ui_dev_tools")
        health_start = time.time()
        
        if await self.wait_for_healthy("ui_dev_tools", port, timeout=10):
            final_health = await self.enhanced_health_check("ui_dev_tools", port)
            return LaunchResult(
                component_name="ui_dev_tools",
                success=True,
                state=ComponentState.HEALTHY,
                pid=process.pid,
                port=port,
                message=f"Successfully launched and healthy on port {port}",
                startup_time=time.time() - launch_start,
                health_check_time=time.time() - health_start,
                log_file=log_file_path
            )
        else:
            return LaunchResult(
                component_name="ui_dev_tools",
                success=False,
                state=ComponentState.UNHEALTHY,
                pid=process.pid,
                port=port,
                message=f"Launched but failed health check",
                error="Health check timeout",
                startup_time=time.time() - launch_start,
                log_file=log_file_path
            )
        
    async def enhanced_launch_component(self, component_name: str) -> LaunchResult:
        """Enhanced component launch with detailed monitoring"""
        launch_start = time.time()
        
        try:
            # Special handling for UI DevTools MCP
            if component_name == "ui_dev_tools":
                return await self.launch_ui_devtools_mcp()
            
            comp_info = self.config.get_component(component_name)
            if not comp_info:
                return LaunchResult(
                    component_name=component_name,
                    success=False,
                    state=ComponentState.FAILED,
                    message=f"Unknown component: {component_name}",
                    startup_time=time.time() - launch_start
                )
                
            port = comp_info.port
            
            # Check if already running and healthy
            if not self.check_port_available(port):
                health = await self.enhanced_health_check(component_name, port)
                if health.healthy:
                    self.log(f"Already running and healthy", "success", component_name)
                    result = LaunchResult(
                        component_name=component_name,
                        success=True,
                        state=ComponentState.HEALTHY,
                        port=port,
                        message=f"Already running on port {port}",
                        startup_time=0,
                        health_check_time=health.response_time,
                        log_file=self.get_log_file_path(component_name)
                    )
                    # Register with monitoring so it counts as successful
                    self.launched_components[component_name] = result
                    return result
                else:
                    # Kill unhealthy process
                    self.log(f"Killing unhealthy process on port {port}", "warning", component_name)
                    if not self.kill_port_process(port):
                        return LaunchResult(
                            component_name=component_name,
                            success=False,
                            state=ComponentState.FAILED,
                            message=f"Could not free port {port}",
                            startup_time=time.time() - launch_start
                        )
                    await asyncio.sleep(2)
                    
            # Launch the component
            result = await self.launch_component_process(component_name)
            if not result.success:
                return result
                
            # Wait for component to become healthy (reduced timeout)
            self.log(f"Waiting for health check...", "info", component_name)
            health_start = time.time()

            # Use component-specific timeouts - be more aggressive
            timeout = 8 if component_name in ["hermes", "engram", "rhetor"] else 5

            if await self.wait_for_healthy(component_name, port, timeout=timeout):
                final_health = await self.enhanced_health_check(component_name, port)
                result.state = ComponentState.HEALTHY
                result.health_check_time = time.time() - health_start
                result.message = f"Successfully launched and healthy on port {port}"
                
                # Register with monitoring
                self.launched_components[component_name] = result
                
                self.log(
                    f"Launch completed in {result.startup_time:.1f}s, health in {result.health_check_time:.1f}s",
                    "success",
                    component_name
                )
                self.log(
                    f"Logging to: {result.log_file}",
                    "log",
                    component_name
                )
                
                # Always launch AI - components and AIs are paired with fixed ports
                await self.launch_component_ai(component_name)
            else:
                result.state = ComponentState.UNHEALTHY
                result.message = f"Launched but failed health check within {timeout}s"
                result.error = "Health check timeout"
                
                self.log(result.message, "warning", component_name)
                
            result.startup_time = time.time() - launch_start
            return result
            
        except Exception as e:
            return LaunchResult(
                component_name=component_name,
                success=False,
                state=ComponentState.FAILED,
                message=f"Launch failed: {str(e)}",
                error=str(e),
                startup_time=time.time() - launch_start
            )
            
    async def launch_component_process(self, component_name: str) -> LaunchResult:
        """Launch the actual component process with logging"""
        try:
            comp_info = self.config.get_component(component_name)
            port = comp_info.port
            
            # Get launch command (using original logic)
            cmd = self.get_component_command(component_name)
            
            # Check if we got a valid command
            if not cmd:
                return LaunchResult(
                    component_name=component_name,
                    success=False,
                    state=ComponentState.FAILED,
                    message=f"No run script found for component: {component_name}"
                )
            
            # Set environment variables
            env = os.environ.copy()
            env[f"{component_name.upper()}_PORT"] = str(port)
            
            # Add Tekton root to PYTHONPATH for shared imports
            tekton_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            current_pythonpath = env.get('PYTHONPATH', '')
            
            # Special case for tekton-core: add component directory to PYTHONPATH too
            normalized_name = self.normalize_component_name(component_name)
            if normalized_name == "tekton_core":
                component_dir = self.get_component_directory(component_name)
                if current_pythonpath:
                    env['PYTHONPATH'] = f"{component_dir}:{tekton_root}:{current_pythonpath}"
                else:
                    env['PYTHONPATH'] = f"{component_dir}:{tekton_root}"
            else:
                if current_pythonpath:
                    env['PYTHONPATH'] = f"{tekton_root}:{current_pythonpath}"
                else:
                    env['PYTHONPATH'] = tekton_root
            
            # Change to component directory
            component_dir = self.get_component_directory(component_name)
                
            if not os.path.exists(component_dir):
                return LaunchResult(
                    component_name=component_name,
                    success=False,
                    state=ComponentState.FAILED,
                    message=f"Component directory not found: {component_dir}"
                )
                
            # Open log file
            log_file_path = self.get_log_file_path(component_name)
            log_file = open(log_file_path, 'a')
            
            # Write launch header to log
            log_file.write(f"\n{'='*60}\n")
            log_file.write(f"Component: {component_name}\n")
            log_file.write(f"Started: {datetime.now()}\n")
            log_file.write(f"Command: {' '.join(cmd)}\n")
            log_file.write(f"Directory: {component_dir}\n")
            log_file.write(f"Port: {port}\n")
            log_file.write(f"{'='*60}\n\n")
            log_file.flush()
                
            # Launch the component
            if self.verbose:
                self.log(f"Executing: {' '.join(cmd)}", "launch", component_name)
                
            # Use subprocess.Popen with PIPE to capture output
            if platform.system() == "Windows":
                process = subprocess.Popen(
                    cmd,
                    cwd=component_dir,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                process = subprocess.Popen(
                    cmd,
                    cwd=component_dir,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setsid
                )
                
            # Start log reader threads
            stdout_reader = LogReader(process.stdout, log_file, component_name, "stdout")
            stderr_reader = LogReader(process.stderr, log_file, component_name, "stderr")
            stdout_reader.start()
            stderr_reader.start()
            
            # Keep track of readers for cleanup
            self.log_readers.extend([stdout_reader, stderr_reader])
                
            # Check if process started successfully (faster check)
            await asyncio.sleep(1)  # Reduced from 2s to 1s
            if process.poll() is not None:
                # Process exited immediately - wait for readers to capture output
                stdout_reader.join(timeout=1)
                stderr_reader.join(timeout=1)
                
                # Read last few lines from log file for error message
                log_file.close()
                with open(log_file_path, 'r') as f:
                    lines = f.readlines()
                    error_lines = lines[-10:] if len(lines) > 10 else lines
                    error_msg = ''.join(error_lines)

                # Try to extract meaningful error from output
                if "ModuleNotFoundError" in error_msg:
                    clean_error = "Missing Python dependencies"
                elif "Permission denied" in error_msg:
                    clean_error = "Permission denied"
                elif "Address already in use" in error_msg:
                    clean_error = "Port already in use"
                elif "ImportError" in error_msg:
                    clean_error = "Import error - check dependencies"
                else:
                    clean_error = error_msg[-200:] if error_msg.strip() else "Process exited without output"

                return LaunchResult(
                    component_name=component_name,
                    success=False,
                    state=ComponentState.FAILED,
                    message=f"Process exited immediately: {clean_error}",
                    error=error_msg[-500:],
                    log_file=log_file_path
                )
                
            return LaunchResult(
                component_name=component_name,
                success=True,
                state=ComponentState.STARTING,
                pid=process.pid,
                port=port,
                message=f"Process started with PID {process.pid}",
                log_file=log_file_path
            )
            
        except Exception as e:
            return LaunchResult(
                component_name=component_name,
                success=False,
                state=ComponentState.FAILED,
                message=f"Failed to start process: {str(e)}",
                error=str(e)
            )
    
    # Include original helper methods
    def check_port_available(self, port: int) -> bool:
        """Check if a port is available or only has TIME_WAIT sockets"""
        import socket
        
        # First check if there's an actual listening process
        if platform.system() == "Darwin":
            # On macOS, check for LISTEN state specifically
            result = subprocess.run(
                ["lsof", "-i", f":{port}", "-sTCP:LISTEN"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                # There's an actual listening process
                return False
                
            # No listening process, but might have TIME_WAIT sockets
            # With SO_REUSEPORT, we can bind anyway
            return True
        else:
            # Fallback to original logic for other platforms
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return True
            except OSError:
                return False
        
    def kill_port_process(self, port: int) -> bool:
        """Kill process listening on a port (only LISTEN state, not TIME_WAIT)"""
        try:
            if platform.system() == "Darwin":
                # Only get PIDs of processes in LISTEN state
                result = subprocess.run(
                    ["lsof", "-ti", f":{port}", "-sTCP:LISTEN"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0 and result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        try:
                            os.kill(int(pid), signal.SIGTERM)
                            time.sleep(1)
                            try:
                                os.kill(int(pid), 0)
                                os.kill(int(pid), signal.SIGKILL)
                            except ProcessLookupError:
                                pass
                            return True
                        except Exception as e:
                            if self.verbose:
                                self.log(f"Error killing PID {pid}: {e}", "warning")
            else:
                for conn in psutil.net_connections(kind='inet'):
                    if conn.laddr.port == port and conn.status == 'LISTEN':
                        try:
                            proc = psutil.Process(conn.pid)
                            proc.terminate()
                            proc.wait(timeout=3)
                            return True
                        except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                            try:
                                proc.kill()
                                return True
                            except:
                                pass
        except Exception as e:
            if self.verbose:
                self.log(f"Error killing process on port {port}: {e}", "warning")
        return False
    
    def normalize_component_name(self, component_name: str) -> str:
        """Normalize component name for internal processing"""
        # Handle special cases where CLI name differs from internal name
        name_mappings = {
            "tekton-core": "tekton_core",
            "penia": "budget",  # Penia is Greek name for Budget
        }
        return name_mappings.get(component_name, component_name)
    
    def get_component_directory(self, component_name: str) -> str:
        """Get the directory for a component"""
        # Use the globally found tekton_root instead of calculating from __file__
        base_dir = tekton_root
        
        # Normalize the component name first
        normalized_name = self.normalize_component_name(component_name)
        
        dir_mappings = {
            "tekton_core": "tekton-core",
            # "llm_adapter": "LLMAdapter", # Removed - use Rhetor with tekton-llm-client
        }
        
        if normalized_name in dir_mappings:
            return os.path.join(base_dir, dir_mappings[normalized_name])
        else:
            dir_name = normalized_name.replace("_", "-")
            dir_name = dir_name[0].upper() + dir_name[1:] if dir_name else ""
            return os.path.join(base_dir, dir_name)
            
    def get_component_command(self, component_name: str) -> List[str]:
        """Get the launch command for a component"""
        component_dir = self.get_component_directory(component_name)
        
        # Normalize component name for internal logic
        normalized_name = self.normalize_component_name(component_name)
        
        # Components that should use python -m (have __main__.py and proper initialization)
        module_components = [
            'apollo', 'athena', 'numa', 'noesis', 'terma',  # Already migrated
            'budget', 'engram', 'ergon', 'hephaestus', 'harmonia', 
            'metis', 'prometheus', 'rhetor', 'sophia', 'synthesis', 
            'telos', 'hermes', 'tekton_core'  # All migrated to Python modules
        ]
        
        if normalized_name in module_components:
            # Use Python module execution with normalized name
            if normalized_name == "tekton_core":
                # Special handling for tekton_core - use the original working approach
                return [sys.executable, "-m", "tekton.api.app"]
            else:
                # Standard module execution
                return [sys.executable, "-m", normalized_name]
            
        # For other components, look for run scripts
        run_script = None
        for script_name in [f"run_{component_name}.sh", f"run_{component_name}.py"]:
            script_path = os.path.join(component_dir, script_name)
            if os.path.exists(script_path):
                run_script = script_path
                break
                
        if run_script and run_script.endswith('.sh'):
            return ["bash", run_script]
        elif run_script and run_script.endswith('.py'):
            return [sys.executable, run_script]
        else:
            # All components should have run scripts now
            self.log(f"Warning: No run script found for {component_name}", "warning", component_name)
            self.log(f"Expected to find: run_{component_name}.sh in {component_dir}", "warning", component_name)
            
            # Return empty list to indicate failure
            return []
    
    async def pre_launch_check(self, target_components: Optional[List[str]] = None):
        """Check for lingering processes before launch
        
        Args:
            target_components: List of specific components to check. If None, check all.
        """
        conflicts = []
        
        # Check configured ports - only for target components if specified
        all_components = self.config.get_all_components()
        
        # Filter components if specific targets provided
        if target_components:
            components_to_check = {name: info for name, info in all_components.items() 
                                 if name in target_components}
        else:
            components_to_check = all_components
            
        for comp_name, comp_info in components_to_check.items():
            port = comp_info.port
            if self.is_port_in_use(port):
                conflicts.append((comp_name, port))
        
        if conflicts:
            self.log("⚠️ Found processes on ports from previous run:", "warning")
            for comp_name, port in conflicts:
                self.log(f"  - {comp_name} on port {port}", "warning")
            
            self.log("Waiting 3 seconds for socket cleanup...", "info")
            await asyncio.sleep(3)  # Match the SO_LINGER + buffer time
            
            # Re-check
            still_blocked = []
            for comp_name, port in conflicts:
                if self.is_port_in_use(port):
                    still_blocked.append((comp_name, port))
            
            if still_blocked:
                self.log("❌ Ports still blocked after wait:", "error")
                for comp_name, port in still_blocked:
                    self.log(f"  - {comp_name} on port {port}", "error")
                self.log("Consider running 'tekton-kill' first", "error")
                # Continue anyway - let individual components fail if needed
        else:
            self.log("✅ All ports are clear", "success")
    
    async def launch_with_monitoring(self, components: List[str], enable_monitoring: bool = True):
        """Launch components with optional continuous monitoring"""
        if not components:
            self.log("No components to launch", "warning")
            return
        
        # Pre-launch check for lingering processes - only for components we're launching
        await self.pre_launch_check(target_components=components)
            
        # Group by priority
        launch_groups = self.get_launch_groups(components)
        
        self.log(f"Launching {len(components)} components in {len(launch_groups)} groups", "info")
        self.log(f"Logs will be written to: {self.log_dir}", "log")
        
        # Launch each priority group
        for priority, group_components in launch_groups.items():
            self.log(f"Priority {priority}: {', '.join(group_components)}", "info")
            
            # Launch in parallel within the group
            tasks = [
                self.enhanced_launch_component(comp)
                for comp in group_components
            ]
            
            results = await asyncio.gather(*tasks)
            
            # Process results
            for result in results:
                if result.success:
                    self.log(result.message, "success", result.component_name)
                else:
                    self.log(result.message, "error", result.component_name)
                    
            # Wait a bit between priority groups
            if priority < max(launch_groups.keys()):
                await asyncio.sleep(2)
                
        # Start health monitoring if requested
        if enable_monitoring:
            self.start_health_monitoring()
            
    @performance_boundary(
        title="Component startup orchestration",
        sla="<30s for full stack startup",
        metrics={"hermes": "2s", "engram": "3s", "rhetor": "5s", "others": "2-5s each"},
        optimization_notes="Parallel launch within priority groups, sequential between groups"
    )
    def get_launch_groups(self, components: List[str]) -> Dict[int, List[str]]:
        """Group components by startup priority with dependency hierarchy:
        Hermes → Everything else (including Engram + Rhetor) → UI DevTools
        """
        groups = defaultdict(list)
        
        # Define explicit priority hierarchy
        priority_map = {
            "hermes": 1,        # First - message bus (must be first)
            "ui_dev_tools": 3,  # Last - after all other components
        }
        
        for comp_name in components:
            # Special handling for ui_dev_tools which isn't in component config
            if comp_name == "ui_dev_tools":
                priority = priority_map.get(comp_name, 3)
                groups[priority].append(comp_name)
                continue
                
            comp_info = self.config.get_component(comp_name)
            if comp_info:
                # Use explicit priority if defined, otherwise use priority 2 (everything else)
                if comp_name in priority_map:
                    priority = priority_map[comp_name]
                else:
                    priority = 2  # Everything else (including engram and rhetor) launches after hermes
                    
                groups[priority].append(comp_name)
                
        return dict(sorted(groups.items()))
    
    async def launch_component_ai(self, component_name: str):
        """Launch AI specialist for a component if configured"""
        try:
            # Check if component is excluded from AI support
            if component_name.lower() in ['ui_dev_tools', 'ui-dev-tools', 'ui_devtools']:
                self.log(f"Component does not support AI specialists", "info", component_name)
                return
            
            self.log(f"AI support enabled, checking AI configuration...", "info", component_name)
            
            # Use the AI launcher script
            cmd = [
                sys.executable,
                os.path.join(self.tekton_root, 'scripts', 'enhanced_tekton_ai_launcher.py'),
                component_name,
                '-v',  # Verbose for better logging
                '--no-cleanup'  # Don't kill the AI when script exits
            ]
            
            self.log(f"Launching AI specialist...", "launch", component_name)
            
            # Run the AI launcher and capture output
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,  # Combine stdout and stderr
                env=TektonEnviron.all()  # Pass frozen environment so AI launcher can read port variables
            )
            
            # Wait for it to complete and get output
            stdout, _ = await process.communicate()
            output = stdout.decode() if stdout else ""
            
            if process.returncode == 0:
                if "Successfully launched" in output:
                    self.log(f"AI specialist launched successfully", "success", component_name)
                elif "already running" in output:
                    self.log(f"AI specialist already running", "info", component_name)
                else:
                    self.log(f"AI launch completed (check ai_status for details)", "info", component_name)
            else:
                # Extract error message from output
                error_lines = [line for line in output.split('\n') if 'error' in line.lower() or 'failed' in line.lower()]
                error_msg = error_lines[0] if error_lines else "Check logs for details"
                self.log(f"AI launch failed: {error_msg}", "warning", component_name)
                
        except Exception as e:
            self.log(f"AI launch error: {str(e)}", "error", component_name)
    
    

    def start_health_monitoring(self, interval: int = 30):
        """Start continuous health monitoring"""
        async def monitor():
            while True:
                try:
                    await asyncio.sleep(interval)
                    
                    # Check health of all launched components
                    for comp_name in list(self.launched_components.keys()):
                        result = self.launched_components[comp_name]
                        if result.state == ComponentState.HEALTHY:
                            health = await self.enhanced_health_check(comp_name, result.port)
                            
                            if not health.healthy:
                                self.log(
                                    f"Component became unhealthy: {health.error}",
                                    "warning",
                                    comp_name
                                )
                                # Could implement auto-restart here
                                
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.log(f"Health monitoring error: {e}", "error")
                    
        self.health_monitor_task = asyncio.create_task(monitor())
        self.log("Health monitoring started", "monitor")


async def main():
    """Enhanced main entry point"""
    parser = argparse.ArgumentParser(description="Enhanced Tekton component launcher")
    parser.add_argument(
        "--components", "-c",
        help="Components to launch (comma-separated) or 'all'",
        default=None
    )
    parser.add_argument(
        "--launch-all", "-a",
        action="store_true",
        help="Launch all available components"
    )
    parser.add_argument(
        "--monitor", "-m",
        action="store_true",
        help="Enable continuous health monitoring"
    )
    parser.add_argument(
        "--health-retries", "-r",
        type=int,
        default=3,
        help="Number of health check retries"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--save-logs", "-s",
        action="store_true",
        help="Preserve existing log files (default: delete logs on startup)"
    )
    parser.add_argument(
        "--full", "-f",
        action="store_true",
        help="Launch with full development environment (includes UI DevTools MCP)"
    )
    parser.add_argument(
        "--ai",
        nargs='*',
        help="Launch only AI specialists for components (optionally specify which)"
    )
    parser.add_argument(
        "--no-populate-athena",
        action="store_true",
        help="Skip automatic Athena population after startup"
    )
    
    args = parser.parse_args()
    
    async with EnhancedComponentLauncher(
        verbose=args.verbose,
        health_check_retries=args.health_retries
    ) as launcher:
        
        # Determine components to launch
        if args.launch_all:
            components = list(launcher.config.get_all_components().keys())
            if args.full:
                components.append("ui_dev_tools")
        elif args.components:
            if args.components.lower() == 'all':
                components = list(launcher.config.get_all_components().keys())
                if args.full:
                    components.append("ui_dev_tools")
            else:
                components = [c.strip().lower().replace("-", "_")
                             for c in args.components.split(",")]
        else:
            components = list(launcher.config.get_all_components().keys())
            if args.full:
                components.append("ui_dev_tools")
        
        # Delete logs only for components we're launching (unless --save-logs is specified)
        if not args.save_logs:
            log_dir = os.path.join(tekton_root, ".tekton", "logs")
            if os.path.exists(log_dir):
                cleared_count = 0
                for component in components:
                    log_file = f"{component}.log"
                    log_path = os.path.join(log_dir, log_file)
                    if os.path.exists(log_path):
                        try:
                            os.remove(log_path)
                            cleared_count += 1
                        except Exception as e:
                            print(f"Warning: Could not delete log file {log_file}: {e}")
                if cleared_count > 0:
                    print(f"✅ Cleared {cleared_count} log files for components being launched")
            
        # Handle AI-only mode
        if args.ai is not None:
            # Launch only AI specialists
            if args.ai == []:  # --ai with no arguments means all AIs
                ai_components = components
            else:
                ai_components = [c.strip().lower() for c in args.ai]
            
            # Use the AI launcher directly
            ai_cmd = [
                sys.executable,
                os.path.join(tekton_root, 'scripts', 'enhanced_tekton_ai_launcher.py')
            ] + ai_components
            
            launcher.log(f"Launching AI specialists only: {', '.join(ai_components)}", "info")
            
            process = await asyncio.create_subprocess_exec(
                *ai_cmd,
                stdout=None,
                stderr=None,
                env=TektonEnviron.all()  # Pass frozen environment so AI launcher can read port variables
            )
            
            await process.wait()
            return
        
        
        if not components:
            launcher.log("No components selected", "warning")
            return
            
        
        # Launch components
        start_time = time.time()
        await launcher.launch_with_monitoring(components, enable_monitoring=args.monitor)
        
        
        # Report results
        elapsed = time.time() - start_time
        successful = len([r for r in launcher.launched_components.values() if r.success])
        failed = len([r for r in launcher.launched_components.values() if not r.success])
        
        print(f"\n{'='*60}")
        print(f"Launch completed in {elapsed:.1f} seconds")
        print(f"✅ Successful: {successful}")
        if failed > 0:
            print(f"❌ Failed: {failed}")
            
        # Check if Athena was successfully launched and populate it (unless disabled)
        if not args.no_populate_athena and 'athena' in launcher.launched_components and launcher.launched_components['athena'].success:
            launcher.log("Athena launched successfully, populating with component relationships...", "info")
            try:
                # Run the populate script
                populate_script = os.path.join(tekton_root, "scripts", "populate_athena_relationships.py")
                if os.path.exists(populate_script):
                    launcher.log("Running Athena population script...", "info")
                    process = await asyncio.create_subprocess_exec(
                        sys.executable,
                        populate_script,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await process.communicate()
                    
                    if process.returncode == 0:
                        launcher.log("✅ Athena populated with component relationships", "success")
                    else:
                        error_msg = stderr.decode() if stderr else "Unknown error"
                        launcher.log(f"⚠️ Failed to populate Athena: {error_msg}", "warning")
                else:
                    launcher.log("⚠️ Athena population script not found", "warning")
            except Exception as e:
                launcher.log(f"⚠️ Error populating Athena: {str(e)}", "warning")
            
        # Keep monitoring if requested
        if args.monitor and launcher.health_monitor_task:
            launcher.log("Monitoring active. Press Ctrl+C to stop.", "info")
            try:
                await launcher.health_monitor_task
            except asyncio.CancelledError:
                pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nLauncher stopped by user")
        sys.exit(0)