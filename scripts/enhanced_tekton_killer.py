#!/usr/bin/env python3
"""
Enhanced Tekton Component Killer - Next Generation 💀

Advanced shutdown system with graceful termination, dependency management, and safety features.
Because sometimes you need to kill things... responsibly.
"""
import os
import sys
import asyncio
import psutil
import signal
import socket
import time
import argparse
import aiohttp
import subprocess
import json
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed

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

from tekton.utils.component_config import get_component_config
from tekton.utils.port_config import get_component_port


class KillMethod(Enum):
    """Methods for terminating processes"""
    GRACEFUL_HTTP = "graceful_http"      # Send HTTP shutdown signal
    GRACEFUL_SIGNAL = "graceful_signal"   # Send SIGTERM
    FORCE_KILL = "force_kill"            # Send SIGKILL
    NUCLEAR = "nuclear"                   # Kill all on ports + cleanup


class KillResult(Enum):
    """Result of kill operation"""
    SUCCESS = "success"
    NOT_RUNNING = "not_running"
    FORCE_KILLED = "force_killed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class TerminationResult:
    """Result of a component termination"""
    component_name: str
    port: int
    result: KillResult
    method_used: KillMethod
    pid: Optional[int] = None
    termination_time: float = 0.0
    message: str = ""
    error: Optional[str] = None
    cleanup_performed: bool = False


@dataclass
class ProcessInfo:
    """Detailed process information"""
    pid: int
    name: str
    cmdline: List[str]
    cpu_percent: float
    memory_mb: float
    create_time: float
    connections: int
    children: List[int]


class EnhancedComponentKiller:
    """Advanced component termination system with safety features"""
    
    def __init__(self, verbose: bool = False, dry_run: bool = False, skip_graceful: bool = False):
        self.verbose = verbose
        self.dry_run = dry_run
        self.skip_graceful = skip_graceful
        try:
            self.config = get_component_config()
        except Exception as e:
            print(f"❌ Error: Could not load component config: {e}")
            print("   This usually means Hermes is not running.")
            print("   Please start Hermes first: tekton-launch hermes")
            sys.exit(1)
        self.termination_results: Dict[str, TerminationResult] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Safety features
        self.protected_processes = {"init", "kernel", "systemd", "launchd"}
        self.max_termination_time = 30  # seconds
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=5),
            connector=aiohttp.TCPConnector(limit=10)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    def log(self, message: str, level: str = "info", component: str = None):
        """Enhanced logging with timestamps and component context"""
        symbols = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "kill": "💀",
            "nuclear": "☢️",
            "safety": "🛡️",
            "cleanup": "🧹"
        }
        symbol = symbols.get(level, "•")
        timestamp = datetime.now().strftime("%H:%M:%S")
        comp_prefix = f"[{component}] " if component else ""
        dry_run_prefix = "[DRY-RUN] " if self.dry_run else ""
        print(f"{symbol} {timestamp} {dry_run_prefix}{comp_prefix}{message}")
        
    def get_detailed_process_info(self, port: int) -> Optional[ProcessInfo]:
        """Get comprehensive process information"""
        try:
            # First try platform-specific approach for better accuracy
            if platform.system() == "Darwin":  # macOS
                # Use more specific lsof command to get only LISTEN state
                result = subprocess.run(
                    ["lsof", "-i", f":{port}", "-sTCP:LISTEN"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0 and result.stdout.strip():
                    # Parse lsof output properly
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:  # Skip header
                        # Extract PID from second column
                        parts = lines[1].split()
                        if len(parts) > 1:
                            pid = int(parts[1])
                        else:
                            return None
                    else:
                        return None
                else:
                    return None
            else:
                # Use psutil for other platforms
                pid = None
                for conn in psutil.net_connections(kind='inet'):
                    if conn.laddr.port == port and conn.status == 'LISTEN':
                        pid = conn.pid
                        break
                        
                if not pid:
                    return None
                    
            # Get detailed process information
            try:
                proc = psutil.Process(pid)
                
                # Get child processes
                children = [child.pid for child in proc.children(recursive=True)]
                
                return ProcessInfo(
                    pid=pid,
                    name=proc.name(),
                    cmdline=proc.cmdline(),
                    cpu_percent=proc.cpu_percent(),
                    memory_mb=proc.memory_info().rss / 1024 / 1024,
                    create_time=proc.create_time(),
                    connections=len(proc.net_connections()),  # Use net_connections() instead of deprecated connections()
                    children=children
                )
                
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                self.log(f"Cannot access process {pid}: {e}", "warning")
                return None
                
        except Exception as e:
            if self.verbose:
                self.log(f"Error getting process info for port {port}: {e}", "warning")
        return None
        
    def is_process_safe_to_kill(self, process_info: ProcessInfo) -> Tuple[bool, str]:
        """Safety check before killing a process"""
        # Check if it's a protected system process
        if process_info.name.lower() in self.protected_processes:
            return False, f"Protected system process: {process_info.name}"
            
        # Check if PID is too low (system processes)
        if process_info.pid < 100:
            return False, f"System-level PID: {process_info.pid}"
            
        # Check if it's been running for a very long time (system service)
        uptime_hours = (time.time() - process_info.create_time) / 3600
        if uptime_hours > 24 * 7:  # More than a week
            return False, f"Long-running system service (uptime: {uptime_hours:.1f}h)"
            
        # Check command line for system indicators
        cmdline_str = " ".join(process_info.cmdline).lower()
        dangerous_patterns = ["system", "kernel", "root", "/usr/sbin", "/sbin"]
        for pattern in dangerous_patterns:
            if pattern in cmdline_str and "tekton" not in cmdline_str:
                return False, f"System process detected: {pattern}"
                
        return True, "Safe to terminate"
        
    async def send_graceful_shutdown_signal(self, component_name: str, port: int) -> bool:
        """Send HTTP shutdown signal to component"""
        # All components should now have shutdown endpoints
        # No need to skip any components

        try:
            endpoints_to_try = [
                f"http://localhost:{port}/shutdown",
                f"http://localhost:{port}/api/shutdown",
                f"http://localhost:{port}/admin/shutdown"
            ]

            for endpoint in endpoints_to_try:
                try:
                    async with self.session.post(endpoint, timeout=aiohttp.ClientTimeout(total=2)) as resp:
                        if resp.status in [200, 202, 204]:
                            self.log(f"Graceful shutdown signal sent via {endpoint}", "info", component_name)
                            return True
                except:
                    continue
                    
            # Try sending a custom shutdown message via WebSocket
            try:
                import websockets
                ws_url = f"ws://localhost:{port}/ws"
                
                async with websockets.connect(ws_url, timeout=2) as websocket:
                    shutdown_message = json.dumps({
                        "type": "shutdown",
                        "reason": "Administrative shutdown",
                        "timestamp": datetime.now().isoformat()
                    })
                    await websocket.send(shutdown_message)
                    self.log(f"Shutdown signal sent via WebSocket", "info", component_name)
                    return True
                    
            except ImportError:
                pass  # websockets not available
            except:
                pass  # WebSocket failed
                
        except Exception as e:
            if self.verbose:
                self.log(f"Could not send graceful shutdown: {e}", "warning", component_name)
                
        return False
        
    async def terminate_process_gracefully(self, process_info: ProcessInfo, component_name: str) -> Tuple[bool, str]:
        """Attempt graceful process termination - children first, then parent"""
        try:
            # First terminate all children
            if process_info.children:
                self.log(f"Terminating {len(process_info.children)} child processes first", "info", component_name)
                for child_pid in process_info.children:
                    try:
                        child_proc = psutil.Process(child_pid)
                        child_proc.terminate()
                        self.log(f"Sent SIGTERM to child PID {child_pid}", "info", component_name)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                # Brief wait for children to exit
                await asyncio.sleep(0.5)
            
            # Now terminate parent
            proc = psutil.Process(process_info.pid)
            
            # Send SIGTERM (graceful termination)
            if platform.system() == "Windows":
                proc.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                proc.terminate()
                
            self.log(f"Sent SIGTERM to PID {process_info.pid}", "info", component_name)
            
            # Wait for graceful shutdown
            try:
                proc.wait(timeout=10)
                return True, "Terminated gracefully"
            except psutil.TimeoutExpired:
                return False, "Graceful termination timeout"
                
        except psutil.NoSuchProcess:
            return True, "Process already terminated"
        except psutil.AccessDenied:
            return False, "Access denied"
        except Exception as e:
            return False, f"Error during graceful termination: {e}"
            
    async def force_kill_process(self, process_info: ProcessInfo, component_name: str) -> Tuple[bool, str]:
        """Force kill process and children"""
        killed_pids = []
        
        try:
            # Kill child processes first
            for child_pid in process_info.children:
                try:
                    child_proc = psutil.Process(child_pid)
                    child_proc.kill()
                    killed_pids.append(child_pid)
                    self.log(f"Force killed child PID {child_pid}", "kill", component_name)
                except:
                    pass
                    
            # Kill main process
            try:
                proc = psutil.Process(process_info.pid)
                proc.kill()
                proc.wait(timeout=3)
                killed_pids.append(process_info.pid)
                
                return True, f"Force killed PID {process_info.pid} and {len(killed_pids)-1} children"
                
            except psutil.NoSuchProcess:
                return True, "Process already terminated"
            except Exception as e:
                return False, f"Force kill failed: {e}"
                
        except Exception as e:
            return False, f"Error during force kill: {e}"
            
    async def cleanup_component_resources(self, component_name: str) -> bool:
        """Cleanup component-specific resources"""
        if self.dry_run:
            self.log(f"Would cleanup resources for {component_name}", "cleanup", component_name)
            return True
            
        try:
            cleanup_performed = False
            
            # Clean up log files if specified
            log_dir = os.environ.get('TEKTON_LOG_DIR', 
                                    os.path.join(os.environ.get('TEKTON_ROOT', os.path.expanduser('~')), 
                                                '.tekton', 'logs'))
            log_patterns = [
                f"/tmp/{component_name}*.log",
                f"/var/log/tekton/{component_name}*.log",
                os.path.join(log_dir, f"{component_name}*.log")
            ]
            
            # Clean up PID files
            pid_patterns = [
                f"/tmp/{component_name}.pid",
                f"/var/run/{component_name}.pid",
                f"~/.tekton/pids/{component_name}.pid"
            ]
            
            # Clean up socket files
            socket_patterns = [
                f"/tmp/{component_name}.sock",
                f"/var/run/{component_name}.sock"
            ]
            
            for pattern_list in [pid_patterns, socket_patterns]:
                for pattern in pattern_list:
                    expanded_pattern = os.path.expanduser(pattern)
                    if os.path.exists(expanded_pattern):
                        try:
                            os.remove(expanded_pattern)
                            cleanup_performed = True
                            self.log(f"Removed {expanded_pattern}", "cleanup", component_name)
                        except Exception as e:
                            self.log(f"Could not remove {expanded_pattern}: {e}", "warning", component_name)
                            
            return cleanup_performed
            
        except Exception as e:
            self.log(f"Error during cleanup: {e}", "warning", component_name)
            return False
            
    async def terminate_component_advanced(self, component_name: str) -> TerminationResult:
        """Advanced component termination with multiple strategies"""
        start_time = time.time()
        
        comp_info = self.config.get_component(component_name)
        if not comp_info:
            return TerminationResult(
                component_name=component_name,
                port=0,
                result=KillResult.FAILED,
                method_used=KillMethod.GRACEFUL_HTTP,
                message=f"Unknown component: {component_name}",
                error="Component not found in config"
            )
            
        port = comp_info.port
        
        # Get process information
        process_info = self.get_detailed_process_info(port)
        if not process_info:
            return TerminationResult(
                component_name=component_name,
                port=port,
                result=KillResult.NOT_RUNNING,
                method_used=KillMethod.GRACEFUL_HTTP,
                message=f"No process running on port {port}",
                termination_time=time.time() - start_time
            )
            
        # Safety check
        safe, safety_reason = self.is_process_safe_to_kill(process_info)
        if not safe:
            return TerminationResult(
                component_name=component_name,
                port=port,
                result=KillResult.FAILED,
                method_used=KillMethod.GRACEFUL_HTTP,
                pid=process_info.pid,
                message=f"Safety check failed: {safety_reason}",
                error=safety_reason,
                termination_time=time.time() - start_time
            )
            
        self.log(f"Found process PID {process_info.pid} ({process_info.memory_mb:.1f}MB, {len(process_info.children)} children)", "info", component_name)
        
        if self.dry_run:
            return TerminationResult(
                component_name=component_name,
                port=port,
                result=KillResult.SUCCESS,
                method_used=KillMethod.GRACEFUL_HTTP,
                pid=process_info.pid,
                message="DRY RUN: Would terminate process",
                termination_time=time.time() - start_time
            )
            
        # Strategy 1: Try graceful HTTP shutdown (unless skip_graceful is set)
        if not self.skip_graceful:
            self.log("Attempting graceful HTTP shutdown...", "info", component_name)
            if await self.send_graceful_shutdown_signal(component_name, port):
                # Wait a moment for graceful shutdown
                await asyncio.sleep(3)
                
                # Check if process is still running
                if not self.get_detailed_process_info(port):
                    cleanup_performed = await self.cleanup_component_resources(component_name)
                    return TerminationResult(
                        component_name=component_name,
                        port=port,
                        result=KillResult.SUCCESS,
                        method_used=KillMethod.GRACEFUL_HTTP,
                        pid=process_info.pid,
                        message="Gracefully shutdown via HTTP",
                        cleanup_performed=cleanup_performed,
                        termination_time=time.time() - start_time
                    )
        else:
            self.log("Skipping HTTP graceful shutdown (--skip-graceful flag set)", "info", component_name)
                
        # Strategy 2: Try graceful signal termination
        self.log("Attempting graceful signal termination...", "info", component_name)
        success, message = await self.terminate_process_gracefully(process_info, component_name)
        if success:
            cleanup_performed = await self.cleanup_component_resources(component_name)
            return TerminationResult(
                component_name=component_name,
                port=port,
                result=KillResult.SUCCESS,
                method_used=KillMethod.GRACEFUL_SIGNAL,
                pid=process_info.pid,
                message=f"Gracefully terminated: {message}",
                cleanup_performed=cleanup_performed,
                termination_time=time.time() - start_time
            )
            
        # Strategy 3: Force kill
        self.log("Graceful termination failed, force killing...", "warning", component_name)
        success, message = await self.force_kill_process(process_info, component_name)
        
        cleanup_performed = await self.cleanup_component_resources(component_name)
        
        return TerminationResult(
            component_name=component_name,
            port=port,
            result=KillResult.FORCE_KILLED if success else KillResult.FAILED,
            method_used=KillMethod.FORCE_KILL,
            pid=process_info.pid,
            message=message,
            cleanup_performed=cleanup_performed,
            termination_time=time.time() - start_time,
            error=None if success else message
        )
        
    async def nuclear_option(self) -> Dict[int, TerminationResult]:
        """☢️ NUCLEAR OPTION: Kill everything on all Tekton ports"""
        self.log("☢️  INITIATING NUCLEAR PROTOCOL", "nuclear")
        self.log("This will terminate ALL processes on Tekton ports", "warning")
        
        if not self.dry_run:
            # Give user one last chance to abort
            for i in range(3, 0, -1):
                self.log(f"Nuclear launch in {i}... (Ctrl+C to abort)", "nuclear")
                await asyncio.sleep(1)
                
        results = {}
        all_components = self.config.get_all_components()
        
        for comp_name, comp_info in all_components.items():
            result = await self.terminate_component_advanced(comp_name)
            results[comp_info.port] = result
            
        # Additional cleanup - kill any remaining processes on our ports
        if not self.dry_run:
            for comp_name, comp_info in all_components.items():
                remaining_process = self.get_detailed_process_info(comp_info.port)
                if remaining_process:
                    self.log(f"Nuclear cleanup: force killing remaining PID {remaining_process.pid}", "nuclear")
                    try:
                        os.kill(remaining_process.pid, signal.SIGKILL)
                    except:
                        pass
                        
        self.log("☢️  Nuclear protocol complete", "nuclear")
        return results
        
    def get_shutdown_order(self, components: List[str]) -> Tuple[List[str], List[str]]:
        """Determine optimal shutdown order: (non_core_components, core_components)"""
        # Core infrastructure components that should be killed last
        core_components = ["hermes", "engram", "rhetor"]

        non_core = []
        core = []

        for comp_name in components:
            if comp_name in core_components:
                core.append(comp_name)
            else:
                non_core.append(comp_name)

        # Sort core components by dependency order (rhetor -> engram -> hermes)
        core_order = []
        for core_comp in ["rhetor", "engram", "hermes"]:
            if core_comp in core:
                core_order.append(core_comp)

        return non_core, core_order
        
    async def terminate_multiple_components(self, components: List[str], parallel: bool = False) -> Dict[str, TerminationResult]:
        """Terminate multiple components with smart dependency management"""
        if not components:
            self.log("No components to terminate", "warning")
            return {}

        # Get optimal shutdown order
        non_core_components, core_components = self.get_shutdown_order(components)

        self.log(f"Terminating {len(components)} components", "info")
        if non_core_components:
            self.log(f"Non-core components: {', '.join(non_core_components)} (parallel)", "info")
        if core_components:
            self.log(f"Core components: {' → '.join(core_components)} (sequential, last)", "info")

        results = {}

        # Phase 1: Terminate non-core components in parallel
        if non_core_components:
            self.log("🔄 Phase 1: Terminating non-core components in parallel...", "info")
            tasks = [
                self.terminate_component_advanced(comp_name)
                for comp_name in non_core_components
            ]

            termination_results = await asyncio.gather(*tasks)
            for result in termination_results:
                results[result.component_name] = result

            # Brief pause before core shutdown
            if core_components:
                await asyncio.sleep(2)

        # Phase 2: Terminate core components sequentially
        if core_components:
            self.log("🔄 Phase 2: Terminating core infrastructure sequentially...", "info")
            for comp_name in core_components:
                result = await self.terminate_component_advanced(comp_name)
                results[comp_name] = result

                # Brief pause between core shutdowns
                if result.result in [KillResult.SUCCESS, KillResult.FORCE_KILLED]:
                    await asyncio.sleep(1)

        return results
        
    def get_running_components(self) -> List[str]:
        """Get list of currently running Tekton components"""
        running = []
        all_components = self.config.get_all_components()
        
        for comp_name, comp_info in all_components.items():
            if self.get_detailed_process_info(comp_info.port):
                running.append(comp_name)
                
        return running
        
    def format_termination_report(self, results: Dict[str, TerminationResult]) -> str:
        """Format termination results report"""
        if not results:
            return "No termination operations performed"
            
        lines = ["", "💀 Termination Report:", "=" * 60]
        
        success_count = 0
        force_count = 0
        failed_count = 0
        
        for comp_name, result in results.items():
            if result.result == KillResult.SUCCESS:
                success_count += 1
                status = "✅ SUCCESS"
            elif result.result == KillResult.FORCE_KILLED:
                force_count += 1
                status = "💀 FORCE KILLED"
            elif result.result == KillResult.NOT_RUNNING:
                status = "⭕ NOT RUNNING"
            else:
                failed_count += 1
                status = "❌ FAILED"
                
            # Get component display name
            comp_info = self.config.get_component(comp_name)
            display_name = comp_info.name if comp_info else comp_name.upper()
            
            line = f"  {display_name:20} | {status:15} | {result.termination_time:.2f}s"
            if result.method_used:
                line += f" | {result.method_used.value}"
            if result.cleanup_performed:
                line += " | 🧹"
                
            lines.append(line)
            
            if result.error and self.verbose:
                lines.append(f"    Error: {result.error}")
                
        lines.extend([
            "=" * 60,
            f"Summary: {success_count} successful, {force_count} force killed, {failed_count} failed"
        ])
        
        return "\n".join(lines)
    
    async def final_cleanup_phase(self, target_components: Optional[List[str]] = None):
        """Nuclear cleanup - ensure everything is dead and ports are free
        
        Args:
            target_components: List of specific components to cleanup. If None, cleanup all.
        """
        self.log("Waiting 3 seconds for socket cleanup (SO_LINGER + buffer)...", "cleanup")
        await asyncio.sleep(3)  # 2 second linger + 1 second buffer
        
        cleanup_performed = False
        all_components = self.config.get_all_components()
        
        # Filter components if specific targets provided
        if target_components:
            components_to_check = {name: info for name, info in all_components.items() 
                                 if name in target_components}
        else:
            components_to_check = all_components
        
        for comp_name, comp_info in components_to_check.items():
            port = comp_info.port
            
            # Check if port is still in use
            process_info = self.get_detailed_process_info(port)
            if process_info:
                cleanup_performed = True
                self.log(f"Port {port} still has process PID {process_info.pid}", "warning", comp_name)
                
                # Force kill any remaining processes
                try:
                    # Kill children first
                    for child_pid in process_info.children:
                        try:
                            os.kill(child_pid, signal.SIGKILL)
                            self.log(f"Force killed zombie child PID {child_pid}", "nuclear", comp_name)
                        except ProcessLookupError:
                            pass
                    
                    # Then kill parent
                    os.kill(process_info.pid, signal.SIGKILL)
                    self.log(f"Force killed zombie PID {process_info.pid}", "nuclear", comp_name)
                except ProcessLookupError:
                    pass
                except Exception as e:
                    self.log(f"Failed to kill zombie PID {process_info.pid}: {e}", "error", comp_name)
            
            # Verify port is free
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(('', port))
                sock.close()
                if self.verbose:
                    self.log(f"Port {port} is now free", "success", comp_name)
            except OSError:
                self.log(f"Port {port} still blocked after cleanup!", "error", comp_name)
        
        if cleanup_performed:
            self.log("Nuclear cleanup completed - some zombies were eliminated", "nuclear")
        else:
            self.log("All ports clear - no cleanup needed", "success")


async def main():
    """Enhanced killer main entry point"""
    parser = argparse.ArgumentParser(
        description="Enhanced Tekton component killer 💀",
        epilog="⚠️  Use with caution! This tool can terminate running services."
    )
    parser.add_argument(
        "--components", "-c",
        help="Components to kill (comma-separated) or 'all'",
        default=None
    )
    parser.add_argument(
        "--nuclear", "-n",
        action="store_true",
        help="☢️  NUCLEAR OPTION: Kill everything on all Tekton ports"
    )
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="⚠️  Kill components in parallel (faster but potentially unstable)"
    )
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="🛡️  Dry run mode - show what would be killed without actually doing it"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Skip safety confirmations"
    )
    parser.add_argument(
        "--skip-graceful", "-sg",
        action="store_true",
        help="⚡ Skip HTTP graceful shutdown and go straight to SIGTERM"
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Automatically answer yes to all prompts"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--ui-dev-tools", "-u",
        action="store_true",
        help="Kill UI DevTools MCP server only"
    )
    
    args = parser.parse_args()
    
    async with EnhancedComponentKiller(verbose=args.verbose, dry_run=args.dry_run, skip_graceful=args.skip_graceful) as killer:
        
        # UI DevTools only option
        if args.ui_dev_tools:
            killer.log("🛠️  Killing UI DevTools MCP server", "info")
            # Use the force kill approach since MCP doesn't have graceful shutdown
            process_info = killer.get_detailed_process_info(8088)
            if process_info:
                killer.log(f"Found UI DevTools MCP on port 8088, PID {process_info.pid}", "info")
                success, message = await killer.force_kill_process(process_info, "ui_dev_tools")
                if success:
                    killer.log("✅ UI DevTools MCP server terminated", "success")
                else:
                    killer.log(f"❌ Failed to kill UI DevTools MCP: {message}", "error")
            else:
                killer.log("UI DevTools MCP not running on port 8088", "info")
            return
        
        # Nuclear option
        if args.nuclear:
            if not args.force and not args.yes and not args.dry_run:
                print("☢️  NUCLEAR OPTION SELECTED")
                print("This will terminate ALL Tekton components and cleanup resources.")
                confirm = input("Are you absolutely sure? Type 'NUCLEAR' to confirm: ")
                if confirm != "NUCLEAR":
                    print("Nuclear option aborted.")
                    return
                    
            results = await killer.nuclear_option()
            print(killer.format_termination_report(results))
            return
            
        # Determine components to kill
        if args.components:
            if args.components.lower() == 'all':
                components = killer.get_running_components()
            else:
                components = [c.strip().lower().replace("-", "_") 
                             for c in args.components.split(",")]
        else:
            # Default to all running components + UI DevTools MCP
            components = killer.get_running_components()
            
            # Check if UI DevTools MCP is running on port 8088
            ui_devtools_process = killer.get_detailed_process_info(8088)
            if ui_devtools_process:
                killer.log("🛠️  UI DevTools MCP detected on port 8088 - will be killed", "info")
            
        if not components:
            killer.log("No running components found", "info")
            return
            
        # Show what we're about to kill
        killer.log(f"Found {len(components)} target components:", "info")
        for comp in components:
            comp_info = killer.config.get_component(comp)
            process_info = killer.get_detailed_process_info(comp_info.port) if comp_info else None
            
            if comp_info and process_info:
                print(f"  💀 {comp_info.name} (port {comp_info.port}, PID {process_info.pid}, {process_info.memory_mb:.1f}MB)")
            elif comp_info:
                print(f"  ⭕ {comp_info.name} (port {comp_info.port}) - not running")
                
        # Safety confirmation
        if not args.force and not args.yes and not args.dry_run:
            confirm = input(f"\nProceed with termination? [y/N]: ")
            if confirm.lower() not in ['y', 'yes']:
                print("Termination aborted.")
                return
                
        # Perform termination
        start_time = time.time()
        results = await killer.terminate_multiple_components(components, parallel=args.parallel)
        
        # Report results
        elapsed = time.time() - start_time
        print(f"\n🕐 Total operation time: {elapsed:.1f} seconds")
        print(killer.format_termination_report(results))
        
        # Kill UI DevTools MCP if no args or killing hephaestus
        if not args.components or args.components.lower() == 'all' or 'hephaestus' in components:
            ui_devtools_process = killer.get_detailed_process_info(8088)
            if ui_devtools_process:
                print("\n🛠️  Cleaning up UI DevTools MCP server...")
                success, message = await killer.force_kill_process(ui_devtools_process, "ui_dev_tools")
                if success:
                    print("✅ UI DevTools MCP server terminated")
                else:
                    print(f"❌ Failed to kill UI DevTools MCP: {message}")
        
        # Final cleanup phase
        if args.nuclear or not args.components or args.components.lower() == 'all':
            # Full cleanup for nuclear or all components
            print("\n🔥 Starting final cleanup phase for all components...")
            await killer.final_cleanup_phase()
        elif args.force:
            # Targeted cleanup only for specific components when using --force
            print(f"\n🔥 Starting cleanup phase for {', '.join(components)}...")
            await killer.final_cleanup_phase(target_components=components)
        
        # Exit with appropriate code
        failed_count = sum(1 for r in results.values() if r.result == KillResult.FAILED)
        if failed_count > 0:
            sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n💀 Termination operation cancelled by user")
        sys.exit(1)