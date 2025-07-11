#!/usr/bin/env python3
"""
Enhanced Tekton Status Checker - Next Generation

Advanced status monitoring with metrics, trends, and detailed reporting.
"""
import asyncio
import aiohttp
import argparse
import json
import sys
import os
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from tabulate import tabulate
from dataclasses import dataclass, asdict
import psutil
import statistics

# Try to import colorama for colored output
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    # Fallback - no colors
    HAS_COLOR = False
    class Fore:
        GREEN = ''
        RED = ''
        YELLOW = ''
        BLUE = ''
        CYAN = ''
        MAGENTA = ''
        RESET = ''
    class Style:
        BRIGHT = ''
        RESET_ALL = ''

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

from tekton.utils.component_config import get_component_config, ComponentInfo
from shared.utils.env_config import get_component_config as get_env_config
# Registry client removed - using direct port checks
# from shared.ai.registry_client import AIRegistryClient


@dataclass
class ComponentMetrics:
    """Extended component metrics"""
    name: str
    port: int
    status: str
    version: str
    response_time: Optional[float]
    uptime: Optional[float]
    cpu_percent: Optional[float]
    memory_mb: Optional[float]
    request_count: Optional[int]
    error_count: Optional[int]
    last_error: Optional[str]
    registered_with_hermes: bool
    health_score: float  # 0-100 health score
    process_info: Optional[Dict[str, Any]]
    endpoint_health: Dict[str, bool]  # Health of individual endpoints
    dependencies_healthy: bool
    ready: bool = False  # From /ready endpoint
    capabilities: List[str] = None  # Component capabilities
    ai_status: Optional[str] = None  # AI model name or None
    ai_health: Optional[str] = None  # green/yellow/red/none
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON output"""
        return asdict(self)


@dataclass
class SystemMetrics:
    """System-wide metrics"""
    total_components: int
    healthy_components: int
    running_components: int
    registered_components: int
    average_response_time: float
    total_memory_mb: float
    total_cpu_percent: float
    system_health_score: float
    hermes_connectivity: bool
    last_check_time: datetime


class MetricsStorage:
    """SQLite-based metrics storage for trends"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Use tekton_root directory for persistent storage
            tekton_dir = os.path.join(tekton_root, ".tekton")
            os.makedirs(tekton_dir, exist_ok=True)
            db_path = os.path.join(tekton_dir, "metrics.db")
            
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            # Use timestamp format that doesn't trigger deprecation warning
            conn.execute("""
                CREATE TABLE IF NOT EXISTS component_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    component_name TEXT,
                    status TEXT,
                    response_time REAL,
                    cpu_percent REAL,
                    memory_mb REAL,
                    health_score REAL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    total_components INTEGER,
                    healthy_components INTEGER,
                    system_health_score REAL,
                    average_response_time REAL
                )
            """)
            
    def store_component_metrics(self, metrics: ComponentMetrics):
        """Store component metrics"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO component_metrics
                (timestamp, component_name, status, response_time, cpu_percent, memory_mb, health_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                metrics.name,
                metrics.status,
                metrics.response_time,
                metrics.cpu_percent,
                metrics.memory_mb,
                metrics.health_score
            ))

    def store_system_metrics(self, metrics: SystemMetrics):
        """Store system metrics"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO system_metrics
                (timestamp, total_components, healthy_components, system_health_score, average_response_time)
                VALUES (?, ?, ?, ?, ?)
            """, (
                metrics.last_check_time.isoformat(),
                metrics.total_components,
                metrics.healthy_components,
                metrics.system_health_score,
                metrics.average_response_time
            ))
            
    def get_component_trends(self, component_name: str, hours: int = 24) -> List[Tuple]:
        """Get component metrics trends"""
        since = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT timestamp, status, response_time, health_score
                FROM component_metrics 
                WHERE component_name = ? AND timestamp > ?
                ORDER BY timestamp
            """, (component_name, since))
            return cursor.fetchall()
            
    def get_system_trends(self, hours: int = 24) -> List[Tuple]:
        """Get system metrics trends"""
        since = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT timestamp, healthy_components, system_health_score, average_response_time
                FROM system_metrics 
                WHERE timestamp > ?
                ORDER BY timestamp
            """, (since,))
            return cursor.fetchall()


class EnhancedStatusChecker:
    """Advanced status checker with comprehensive monitoring"""
    
    def __init__(self, store_metrics: bool = True, timeout: float = 2.0, quick_mode: bool = False):
        self.config = get_component_config()
        self.env_config = get_env_config()  # For AI port calculations
        self.storage = MetricsStorage() if store_metrics else None
        self.session = None
        self.timeout = timeout
        self.quick_mode = quick_mode
        # AI registry removed - using fixed port calculations
        self.model_display_names = self._load_model_display_names()
    
    def _load_model_display_names(self) -> Dict[str, str]:
        """Load model display names from config."""
        config_path = os.path.join(tekton_root, 'config', 'ai_model_display_names.json')
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
                return data.get('model_display_names', {})
        except Exception:
            return {}
    
    def _get_display_model_name(self, model: str) -> str:
        """Get display name for a model."""
        if not model:
            return "None"
        # Check mapping first
        if model in self.model_display_names:
            return self.model_display_names[model]
        # Clean up raw model name
        if ':' in model:
            # Ollama format: llama3:70b -> Llama3 70B
            base, variant = model.split(':', 1)
            return f"{base.title()} {variant.upper()}"
        return model
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            connector=aiohttp.TCPConnector(limit=20)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    async def check_ui_devtools_status(self) -> ComponentMetrics:
        """Check UI DevTools MCP status"""
        # UI DevTools is a special case - it's an MCP server on port 8088
        metrics = ComponentMetrics(
            name="ui_dev_tools",
            port=8088,
            status="unknown",
            version="unknown",
            response_time=None,
            uptime=None,
            cpu_percent=None,
            memory_mb=None,
            request_count=None,
            error_count=None,
            last_error=None,
            registered_with_hermes=False,
            health_score=0.0,
            process_info=None,
            endpoint_health={},
            dependencies_healthy=True
        )
        
        start_time = time.time()
        
        # Check process information
        process_info = self.get_process_info(8088)
        metrics.process_info = process_info
        
        if not process_info:
            metrics.status = "not_running"
            metrics.response_time = time.time() - start_time
            return metrics
            
        # Extract process metrics
        if "cpu_percent" in process_info:
            metrics.cpu_percent = process_info["cpu_percent"]
        if "memory_mb" in process_info:
            metrics.memory_mb = process_info["memory_mb"]
            
        # Check health endpoint
        try:
            url = "http://localhost:8088/health"
            async with self.session.get(url) as resp:
                metrics.response_time = time.time() - start_time
                if resp.status == 200:
                    try:
                        data = await resp.json()
                        metrics.status = "healthy"
                        metrics.version = data.get("version", "unknown")
                        # UI DevTools doesn't register with Hermes
                        metrics.registered_with_hermes = False
                    except:
                        metrics.status = "healthy"
                else:
                    metrics.status = "unhealthy"
        except asyncio.TimeoutError:
            metrics.status = "timeout"
            metrics.response_time = time.time() - start_time
        except Exception as e:
            metrics.status = "error"
            metrics.last_error = str(e)
            metrics.response_time = time.time() - start_time
            
        # Calculate health score
        metrics.health_score = self.calculate_health_score(metrics)
        
        return metrics
    
    async def check_component_comprehensive(self, comp_name: str, comp_info: ComponentInfo) -> ComponentMetrics:
        """Comprehensive component health check"""
        start_time = time.time()
        
        # Initialize metrics with defaults
        metrics = ComponentMetrics(
            name=comp_name,
            port=comp_info.port,
            status="unknown",
            version="unknown",
            response_time=None,
            uptime=None,
            cpu_percent=None,
            memory_mb=None,
            request_count=None,
            error_count=None,
            last_error=None,
            registered_with_hermes=False,
            health_score=0.0,
            process_info=None,
            endpoint_health={},
            dependencies_healthy=True
        )
        
        # Check process information
        process_info = self.get_process_info(comp_info.port)
        metrics.process_info = process_info
        
        if not process_info:
            metrics.status = "not_running"
            metrics.response_time = time.time() - start_time
            return metrics
            
        # Extract process metrics
        if "cpu_percent" in process_info:
            metrics.cpu_percent = process_info["cpu_percent"]
        if "memory_mb" in process_info:
            metrics.memory_mb = process_info["memory_mb"]
            
        # Check main health endpoint
        health_result = await self.check_health_endpoint(comp_info.port)
        metrics.response_time = time.time() - start_time
        
        if health_result["healthy"]:
            metrics.status = "healthy"
            metrics.version = health_result.get("version", "unknown")
            
            # Skip additional checks in quick mode
            if not self.quick_mode:
                # Check additional endpoints
                endpoints_to_check = ["/health", "/api", "/status"]
                if comp_name == "hermes":
                    endpoints_to_check.extend(["/api/components", "/api/database"])
                elif comp_name == "sophia":
                    endpoints_to_check.extend(["/mcp", "/api/metrics"])
                    
                for endpoint in endpoints_to_check:
                    endpoint_healthy = await self.check_endpoint(comp_info.port, endpoint)
                    metrics.endpoint_health[endpoint] = endpoint_healthy
                
        else:
            metrics.status = health_result.get("status", "unhealthy")
            metrics.last_error = health_result.get("error")
            
        # Skip some checks in quick mode or if component is down
        if not self.quick_mode and metrics.status != "not_running":
            # Check Hermes registration
            if comp_name != "hermes":  # Hermes can't register with itself
                metrics.registered_with_hermes = await self.check_hermes_registration(comp_name)
                
            # Check ready status
            ready_result = await self.check_ready_endpoint(comp_info.port)
            metrics.ready = ready_result.get("ready", False)
            if ready_result.get("version"):
                metrics.version = ready_result["version"]
                
            # Get capabilities
            metrics.capabilities = await self.get_component_capabilities(comp_name, comp_info.port)
        
        # Check AI status
        ai_info = await self.check_ai_status(comp_name)
        metrics.ai_status = ai_info['model']
        metrics.ai_health = ai_info['health']
            
        # Calculate health score
        metrics.health_score = self.calculate_health_score(metrics)
        
        return metrics
    
    async def check_ai_status(self, component_name: str) -> Dict[str, str]:
        """Check AI status for a component."""
        # AI is always enabled with fixed ports
        
        # Calculate AI port from component port
        component_port = self.env_config.get_port(component_name.lower())
        if not component_port:
            return {'model': None, 'health': 'none'}
        
        # Calculate AI port using configurable bases
        from shared.utils.ai_port_utils import get_ai_port
        ai_port = get_ai_port(component_port)
        ai_id = f"{component_name.lower()}-ai"
        
        # Try to connect to AI
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection('localhost', ai_port),
                timeout=1.0
            )
            
            # Send info request
            writer.write(b'{"type": "info"}\n')
            await writer.drain()
            
            # Get response
            response = await asyncio.wait_for(reader.readline(), timeout=1.0)
            
            writer.close()
            await writer.wait_closed()
            
            if response:
                data = json.loads(response.decode())
                model = data.get('model_name', 'Unknown')
                display_model = self._get_display_model_name(model)
                return {'model': display_model, 'health': 'green'}
            else:
                return {'model': 'Unknown', 'health': 'yellow'}
                
        except asyncio.TimeoutError:
            return {'model': 'Unknown', 'health': 'yellow'}
        except Exception:
            return {'model': 'Unknown', 'health': 'red'}
        
    async def check_health_endpoint(self, port: int) -> Dict[str, Any]:
        """Check the /health endpoint"""
        try:
            url = f"http://localhost:{port}/health"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    try:
                        data = await resp.json()
                        return {
                            "healthy": True,
                            "status": data.get("status", "healthy"),
                            "version": data.get("version", "unknown"),
                            "details": data
                        }
                    except json.JSONDecodeError:
                        return {"healthy": True, "status": "healthy"}
                else:
                    return {
                        "healthy": False,
                        "status": "unhealthy",
                        "error": f"HTTP {resp.status}"
                    }
                    
        except asyncio.TimeoutError:
            return {"healthy": False, "status": "timeout", "error": "Health check timeout"}
        except Exception as e:
            return {"healthy": False, "status": "error", "error": str(e)}
            
    async def check_endpoint(self, port: int, endpoint: str) -> bool:
        """Check if a specific endpoint is responding"""
        try:
            url = f"http://localhost:{port}{endpoint}"
            async with self.session.get(url) as resp:
                return resp.status < 500  # Accept 4xx but not 5xx
        except:
            return False
            
    async def check_hermes_registration(self, component_name: str) -> bool:
        """Check if component is registered with Hermes"""
        try:
            async with self.session.get("http://localhost:8001/api/components") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    registered_names = [
                        comp.get("name", "").lower() 
                        for comp in data.get("components", [])
                    ]
                    # Check both underscore and hyphen versions of the name
                    component_name_lower = component_name.lower()
                    component_name_hyphen = component_name_lower.replace('_', '-')
                    component_name_underscore = component_name_lower.replace('-', '_')
                    
                    return (component_name_lower in registered_names or 
                            component_name_hyphen in registered_names or
                            component_name_underscore in registered_names)
        except:
            pass
        return False
        
    async def check_ready_endpoint(self, port: int) -> Dict[str, Any]:
        """Check the /ready endpoint for readiness status"""
        try:
            url = f"http://localhost:{port}/ready"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    try:
                        data = await resp.json()
                        return {
                            "ready": data.get("ready", False),
                            "version": data.get("version", "unknown"),
                            "uptime": data.get("uptime", 0),
                            "checks": data.get("checks", {})
                        }
                    except json.JSONDecodeError:
                        return {"ready": False}
                else:
                    return {"ready": False}
        except:
            return {"ready": False}
            
    async def get_component_capabilities(self, component_name: str, port: int) -> List[str]:
        """Get component capabilities from MCP or API endpoints"""
        capabilities = []
        
        # Try MCP tools endpoint first
        try:
            async with self.session.get(f"http://localhost:{port}/mcp/tools") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    tools = data.get("tools", [])
                    # Extract capability names from MCP tools
                    for tool in tools:
                        if isinstance(tool, dict) and "name" in tool:
                            capabilities.append(tool["name"])
        except:
            pass
            
        # If no MCP tools, try API endpoints
        if not capabilities:
            try:
                async with self.session.get(f"http://localhost:{port}/api") as resp:
                    if resp.status == 200:
                        # Try to parse available endpoints
                        # This is component-specific and may need enhancement
                        if component_name == "apollo":
                            capabilities = ["prediction", "context", "protocol"]
                        elif component_name == "hermes":
                            capabilities = ["messaging", "registration", "discovery"]
                        elif component_name == "engram":
                            capabilities = ["memory", "storage", "retrieval"]
                        elif component_name == "rhetor":
                            capabilities = ["llm", "streaming", "models"]
                        elif component_name == "athena":
                            capabilities = ["knowledge", "query", "graph"]
                        elif component_name == "synthesis":
                            capabilities = ["analysis", "synthesis", "transform"]
                        elif component_name == "ergon":
                            capabilities = ["agents", "workflows", "coordination"]
                        elif component_name == "sophia":
                            capabilities = ["embedding", "search", "similarity"]
                        elif component_name == "prometheus":
                            capabilities = ["metrics", "monitoring", "analytics"]
                        elif component_name == "harmonia":
                            capabilities = ["workflow", "orchestration", "state"]
                        elif component_name == "budget":
                            capabilities = ["cost", "allocation", "tracking"]
                        elif component_name == "metis":
                            capabilities = ["planning", "strategy", "optimization"]
                        elif component_name == "telos":
                            capabilities = ["goals", "objectives", "alignment"]
            except:
                pass
                
        return capabilities
    
    def get_recent_logs(self, component_name: str, lines: int = 5) -> List[str]:
        """Get recent log lines for a component"""
        # Use the global tekton_root that was found at startup
        log_file_path = os.path.join(tekton_root, ".tekton", "logs", f"{component_name}.log")
        
        if not os.path.exists(log_file_path):
            return []
            
        try:
            with open(log_file_path, 'r') as f:
                # Read all lines and get the last N
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                # Clean up the lines (remove extra whitespace)
                return [line.strip() for line in recent_lines if line.strip()]
        except Exception:
            return []
        
    def get_process_info(self, port: int) -> Optional[Dict[str, Any]]:
        """Get detailed process information"""
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    try:
                        proc = psutil.Process(conn.pid)
                        
                        # Get additional process metrics
                        cpu_times = proc.cpu_times()
                        memory_info = proc.memory_info()
                        
                        return {
                            "pid": conn.pid,
                            "name": proc.name(),
                            "cmdline": " ".join(proc.cmdline()[:3]) + "..." if len(proc.cmdline()) > 3 else " ".join(proc.cmdline()),
                            "cpu_percent": proc.cpu_percent(),
                            "memory_mb": memory_info.rss / 1024 / 1024,
                            "memory_percent": proc.memory_percent(),
                            "num_threads": proc.num_threads(),
                            "create_time": proc.create_time(),
                            "status": proc.status(),
                            "connections": len(proc.connections()),
                        }
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        return {"pid": conn.pid, "name": "unknown"}
        except psutil.AccessDenied:
            return {"error": "Access denied to process information"}
        return None
        
    def calculate_health_score(self, metrics: ComponentMetrics) -> float:
        """Calculate a health score from 0-100"""
        score = 0.0
        
        # Base score for being responsive
        if metrics.status == "healthy":
            score += 40
        elif metrics.status in ["starting", "unhealthy"]:
            score += 20
        elif metrics.status == "not_running":
            score += 0
            
        # Response time bonus (up to 20 points)
        if metrics.response_time is not None:
            if metrics.response_time < 0.1:
                score += 20
            elif metrics.response_time < 0.5:
                score += 15
            elif metrics.response_time < 1.0:
                score += 10
            elif metrics.response_time < 2.0:
                score += 5
                
        # Process health bonus (up to 20 points)
        if metrics.process_info:
            if metrics.cpu_percent is not None and metrics.cpu_percent < 50:
                score += 10
            if metrics.memory_mb is not None and metrics.memory_mb < 500:
                score += 10
                
        # Registration bonus (10 points)
        if metrics.registered_with_hermes:
            score += 10
            
        # Endpoint health bonus (up to 10 points)
        if metrics.endpoint_health:
            healthy_endpoints = sum(1 for h in metrics.endpoint_health.values() if h)
            total_endpoints = len(metrics.endpoint_health)
            if total_endpoints > 0:
                score += 10 * (healthy_endpoints / total_endpoints)
                
        return min(100.0, max(0.0, score))
        
    async def check_all_components_comprehensive(self, show_progress: bool = True) -> Tuple[List[ComponentMetrics], SystemMetrics]:
        """Check all components with comprehensive metrics"""
        components = self.config.get_all_components()
        
        # Add UI DevTools to the count
        total_count = len(components) + 1  # +1 for UI DevTools

        if show_progress:
            mode_str = " (quick mode)" if self.quick_mode else ""
            timeout_str = f" with {self.timeout}s timeout" if self.timeout != 2.0 else ""
            print(f"🔍 Checking {total_count} components{mode_str}{timeout_str}...")

        # Check all components in parallel with progress updates
        tasks = [
            asyncio.create_task(self.check_component_comprehensive(comp_name, comp_info))
            for comp_name, comp_info in components.items()
        ]
        
        # Add UI DevTools check
        tasks.append(asyncio.create_task(self.check_ui_devtools_status()))

        if show_progress:
            print(f"  📋 Checking all {total_count} components in parallel", end="", flush=True)

            # Show progress dots as components complete
            done_tasks = []
            pending_tasks = set(tasks)

            while pending_tasks:
                # Wait for next completion or timeout
                done, pending_tasks = await asyncio.wait(pending_tasks, timeout=0.5, return_when=asyncio.FIRST_COMPLETED)
                done_tasks.extend(done)

                # Print a dot for each completed task
                for _ in done:
                    print(".", end="", flush=True)

                # If nothing completed in 0.5s, print a dot anyway to show activity
                if not done and pending_tasks:
                    print(".", end="", flush=True)

            print(" ✓")  # Final checkmark
            component_metrics = [task.result() for task in done_tasks]
        else:
            component_metrics = await asyncio.gather(*tasks)
        
        # Calculate system metrics
        total = len(component_metrics)
        healthy = sum(1 for m in component_metrics if m.status == "healthy")
        running = sum(1 for m in component_metrics if m.status != "not_running")
        registered = sum(1 for m in component_metrics if m.registered_with_hermes)
        
        response_times = [m.response_time for m in component_metrics if m.response_time is not None]
        avg_response_time = statistics.mean(response_times) if response_times else 0.0
        
        total_memory = sum(m.memory_mb for m in component_metrics if m.memory_mb is not None)
        total_cpu = sum(m.cpu_percent for m in component_metrics if m.cpu_percent is not None)
        
        health_scores = [m.health_score for m in component_metrics]
        system_health_score = statistics.mean(health_scores) if health_scores else 0.0
        
        # Check Hermes connectivity
        hermes_healthy = any(m.name == "hermes" and m.status == "healthy" for m in component_metrics)
        
        system_metrics = SystemMetrics(
            total_components=total,
            healthy_components=healthy,
            running_components=running,
            registered_components=registered,
            average_response_time=avg_response_time,
            total_memory_mb=total_memory,
            total_cpu_percent=total_cpu,
            system_health_score=system_health_score,
            hermes_connectivity=hermes_healthy,
            last_check_time=datetime.now()
        )
        
        # Store metrics if enabled
        if self.storage:
            for metrics in component_metrics:
                self.storage.store_component_metrics(metrics)
            self.storage.store_system_metrics(system_metrics)
            
        return component_metrics, system_metrics
        
    def format_default_table(self, component_metrics: List[ComponentMetrics]) -> str:
        """Format default status table (simplified view)"""
        table_data = []
        
        for metrics in component_metrics:
            # Status with emoji
            status_symbols = {
                "healthy": "✅",
                "unhealthy": "❌", 
                "not_running": "⭕",
                "timeout": "⏱️",
                "error": "⚠️",
                "starting": "🟡"
            }
            status_display = f"{status_symbols.get(metrics.status, '❓')} {metrics.status}"
            
            # AI status - with color based on component health
            if metrics.ai_status:
                # Color based on component status
                if metrics.status == "healthy":
                    ai_display = f"{Fore.GREEN}{metrics.ai_status}{Style.RESET_ALL}"
                elif metrics.status in ["unhealthy", "not_running", "error"]:
                    ai_display = f"{Fore.RED}{metrics.ai_status}{Style.RESET_ALL}"
                else:  # timeout, starting, unknown
                    ai_display = f"{Fore.YELLOW}{metrics.ai_status}{Style.RESET_ALL}"
            else:
                ai_display = "None"
                
            # Response time
            response_str = f"{metrics.response_time:.3f}s" if metrics.response_time else "-"
            
            # Registration status
            if metrics.name.lower() == "hermes":
                reg_symbol = "♻️"  # Hermes recycles itself
            elif metrics.name == "ui_dev_tools":
                reg_symbol = "🛠️"  # UI DevTools uses wrench icon
            else:
                reg_symbol = "✅" if metrics.registered_with_hermes else "❌"
            
            # Component name from config
            if metrics.name == "ui_dev_tools":
                display_name = "UI DevTools"
            else:
                comp_info = self.config.get_component(metrics.name)
                display_name = comp_info.name if comp_info else metrics.name.title()
            
            row = [
                display_name,
                metrics.port,
                status_display,
                metrics.version,
                ai_display,
                response_str,
                reg_symbol
            ]
            
            table_data.append(row)
            
        # Sort by port number
        table_data.sort(key=lambda x: x[1])
        
        headers = ["Component", "Port", "Status", "Version", "AI Status", "Response", "Reg"]
        return tabulate(table_data, headers=headers, tablefmt="fancy_grid")
        
    def format_full_table(self, component_metrics: List[ComponentMetrics]) -> str:
        """Format full status table with enhanced information"""
        table_data = []
        
        for metrics in component_metrics:
            # Status with emoji
            status_symbols = {
                "healthy": "✅",
                "unhealthy": "❌", 
                "not_running": "⭕",
                "timeout": "⏱️",
                "error": "⚠️",
                "starting": "🟡"
            }
            status_display = f"{status_symbols.get(metrics.status, '❓')} {metrics.status}"
            
            # AI status - with color based on component health
            if metrics.ai_status:
                # Color based on component status
                if metrics.status == "healthy":
                    ai_display = f"{Fore.GREEN}{metrics.ai_status}{Style.RESET_ALL}"
                elif metrics.status in ["unhealthy", "not_running", "error"]:
                    ai_display = f"{Fore.RED}{metrics.ai_status}{Style.RESET_ALL}"
                else:  # timeout, starting, unknown
                    ai_display = f"{Fore.YELLOW}{metrics.ai_status}{Style.RESET_ALL}"
            else:
                ai_display = "None"
                
            # Response time
            response_str = f"{metrics.response_time:.3f}s" if metrics.response_time else "-"
            
            # Registration status
            if metrics.name.lower() == "hermes":
                reg_symbol = "♻️"  # Hermes recycles itself
            elif metrics.name == "ui_dev_tools":
                reg_symbol = "🛠️"  # UI DevTools uses wrench icon
            else:
                reg_symbol = "✅" if metrics.registered_with_hermes else "❌"
            
            # Capabilities
            capabilities_str = ", ".join(metrics.capabilities[:3])  # Show first 3
            if len(metrics.capabilities) > 3:
                capabilities_str += f" +{len(metrics.capabilities) - 3}"
            
            # Component name from config
            if metrics.name == "ui_dev_tools":
                display_name = "UI DevTools"
            else:
                comp_info = self.config.get_component(metrics.name)
                display_name = comp_info.name if comp_info else metrics.name.title()
            
            row = [
                display_name,
                metrics.port,
                status_display,
                metrics.version,
                ai_display,
                response_str,
                reg_symbol,
                capabilities_str or "-"
            ]
            
            table_data.append(row)
            
        # Sort by status (healthy first)
        status_order = {"healthy": 0, "unhealthy": 1, "error": 2, "timeout": 3, "not_running": 4}
        table_data.sort(key=lambda x: status_order.get(x[2].split()[-1], 5))
        
        headers = ["Component", "Port", "Status", "Version", "AI Model", "Response", "Reg", "Capabilities"]
        return tabulate(table_data, headers=headers, tablefmt="fancy_grid")
    
    def format_log_output(self, component_metrics: List[ComponentMetrics], lines: int = 5) -> str:
        """Format log output for components"""
        output = ["", "📋 Recent Logs:"]
        
        for metrics in component_metrics:
            if metrics.status == "not_running":
                continue
                
            recent_logs = self.get_recent_logs(metrics.name, lines)
            if recent_logs:
                if metrics.name == "ui_dev_tools":
                    display_name = "UI DevTools"
                else:
                    comp_info = self.config.get_component(metrics.name)
                    display_name = comp_info.name if comp_info else metrics.name.title()
                output.append(f"\n{display_name} (last {lines} lines):")
                for log_line in recent_logs:
                    # Truncate long lines
                    if len(log_line) > 120:
                        log_line = log_line[:117] + "..."
                    output.append(f"    {log_line}")
                    
        return "\n".join(output) if len(output) > 2 else ""
    
    def format_comprehensive_table(self, component_metrics: List[ComponentMetrics], verbose: bool = False) -> str:
        """Format comprehensive status table"""
        table_data = []
        
        for metrics in component_metrics:
            # Status with emoji
            status_symbols = {
                "healthy": "✅",
                "unhealthy": "❌", 
                "not_running": "⭕",
                "timeout": "⏱️",
                "error": "⚠️",
                "starting": "🟡"
            }
            status_display = f"{status_symbols.get(metrics.status, '❓')} {metrics.status}"
            
            # Health score with color coding
            score = metrics.health_score
            if score >= 80:
                score_display = f"🟢 {score:.0f}"
            elif score >= 60:
                score_display = f"🟡 {score:.0f}"
            else:
                score_display = f"🔴 {score:.0f}"
                
            # Response time
            response_str = f"{metrics.response_time:.3f}s" if metrics.response_time else "-"
            
            # Registration status
            if metrics.name.lower() == "hermes":
                reg_symbol = "♻️"  # Hermes recycles itself
            elif metrics.name == "ui_dev_tools":
                reg_symbol = "🛠️"  # UI DevTools uses wrench icon
            else:
                reg_symbol = "✅" if metrics.registered_with_hermes else "❌"
            
            # Process info
            if metrics.process_info and "pid" in metrics.process_info:
                process_str = f"PID:{metrics.process_info['pid']}"
                if "memory_mb" in metrics.process_info:
                    process_str += f" ({metrics.process_info['memory_mb']:.0f}MB)"
            else:
                process_str = "-"
                
            # Component name from config
            if metrics.name == "ui_dev_tools":
                display_name = "UI DevTools"
            else:
                comp_info = self.config.get_component(metrics.name)
                display_name = comp_info.name if comp_info else metrics.name.upper()
            
            row = [
                display_name,
                metrics.port,
                status_display,
                metrics.version,
                score_display,
                response_str,
                reg_symbol
            ]
            
            if verbose:
                row.extend([
                    process_str,
                    f"{metrics.cpu_percent:.1f}%" if metrics.cpu_percent else "-",
                    len([h for h in metrics.endpoint_health.values() if h]) if metrics.endpoint_health else 0
                ])
                
            table_data.append(row)
            
        # Sort by health score (descending)
        table_data.sort(key=lambda x: float(x[4].split()[-1]), reverse=True)
        
        headers = ["Component", "Port", "Status", "Version", "Health", "Response", "Reg"]
        if verbose:
            headers.extend(["Process", "CPU", "Endpoints"])
            
        return tabulate(table_data, headers=headers, tablefmt="fancy_grid")
        
    def format_system_summary(self, system_metrics: SystemMetrics) -> str:
        """Format system summary"""
        health_emoji = "🟢" if system_metrics.system_health_score >= 80 else "🟡" if system_metrics.system_health_score >= 60 else "🔴"
        
        lines = [
            f"📊 System Health Summary:",
            f"   Overall Health: {health_emoji} {system_metrics.system_health_score:.1f}/100",
            f"   Components: {system_metrics.healthy_components}/{system_metrics.total_components} healthy ({system_metrics.healthy_components/system_metrics.total_components*100:.0f}%)",
            f"   Running: {system_metrics.running_components}/{system_metrics.total_components} ({system_metrics.running_components/system_metrics.total_components*100:.0f}%)",
            f"   Registered: {system_metrics.registered_components}/{system_metrics.total_components} ({system_metrics.registered_components/system_metrics.total_components*100:.0f}%)",
            f"   Avg Response: {system_metrics.average_response_time:.3f}s",
            f"   Memory Usage: {system_metrics.total_memory_mb:.0f}MB",
            f"   CPU Usage: {system_metrics.total_cpu_percent:.1f}%",
            f"   Hermes: {'✅ Connected' if system_metrics.hermes_connectivity else '❌ Disconnected'}"
        ]
        
        return "\n".join(lines)
        
    def get_trends_summary(self, component_name: str = None, hours: int = 24) -> str:
        """Get trends summary"""
        if not self.storage:
            return "Metrics storage not enabled"
            
        if component_name:
            trends = self.storage.get_component_trends(component_name, hours)
            if not trends:
                return f"No trend data for {component_name}"
                
            # Calculate trend statistics
            response_times = [t[2] for t in trends if t[2] is not None]
            health_scores = [t[3] for t in trends if t[3] is not None]
            
            if response_times:
                avg_response = statistics.mean(response_times)
                return f"📈 {component_name} trends ({hours}h): Avg response {avg_response:.3f}s, Avg health {statistics.mean(health_scores):.1f}"
            else:
                return f"📈 {component_name}: No metrics in last {hours}h"
        else:
            trends = self.storage.get_system_trends(hours)
            if not trends:
                return f"No system trend data"
                
            health_scores = [t[2] for t in trends]
            if health_scores:
                current_health = health_scores[-1] if health_scores else 0
                avg_health = statistics.mean(health_scores)
                return f"📈 System trends ({hours}h): Current {current_health:.1f}, Average {avg_health:.1f}"
            else:
                return f"📈 System: No metrics in last {hours}h"


async def main():
    """Enhanced main entry point"""
    parser = argparse.ArgumentParser(description="Enhanced Tekton status checker")
    parser.add_argument("--json", "-j", action="store_true", help="Output in JSON format")
    parser.add_argument("--component", "-c", help="Check specific component(s) - single component or comma-separated list")
    parser.add_argument("--full", "-f", action="store_true", help="Full output with enhanced table and capabilities")
    parser.add_argument("--log", "-l", nargs='?', const=5, type=int, metavar='N', help="Show recent log lines for each component (default: 5 lines)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output (equivalent to --full --log)")
    parser.add_argument("--trends", "-t", action="store_true", help="Show trend information")
    parser.add_argument("--no-storage", "-n", action="store_true", help="Disable metrics storage")
    parser.add_argument("--watch", "-w", type=int, help="Watch mode - refresh every N seconds")
    parser.add_argument("--timeout", type=float, default=2.0, help="HTTP request timeout in seconds (default: 2.0)")
    parser.add_argument("--quick", "-q", action="store_true", help="Quick mode - skip detailed checks for faster results")
    
    args = parser.parse_args()
    
    # Handle --verbose flag as --full --log
    if args.verbose:
        args.full = True
        if args.log is None:
            args.log = 5
    
    async with EnhancedStatusChecker(store_metrics=not args.no_storage, timeout=args.timeout, quick_mode=args.quick) as checker:
        
        async def check_and_display():
            # Determine which components to check
            components_to_check = None
            if args.component:
                # Handle comma-separated components
                if ',' in args.component:
                    components_to_check = [c.strip().lower().replace("-", "_") for c in args.component.split(",")]
                else:
                    components_to_check = [args.component.lower().replace("-", "_")]
                
            if components_to_check:
                # Check specific components
                component_metrics = []
                for component_name in components_to_check:
                    # Special handling for ui-dev-tools
                    if component_name in ["ui_dev_tools", "ui-dev-tools", "ui-devtools", "ui_devtools"]:
                        metrics = await checker.check_ui_devtools_status()
                        component_metrics.append(metrics)
                        continue
                        
                    comp_info = checker.config.get_component(component_name)
                    
                    if not comp_info:
                        print(f"❌ Unknown component: {component_name}")
                        available = list(checker.config.get_all_components().keys())
                        available.append("ui-dev-tools")
                        print(f"Available: {', '.join(sorted(available))}")
                        continue
                        
                    metrics = await checker.check_component_comprehensive(component_name, comp_info)
                    component_metrics.append(metrics)
                
                if not component_metrics:
                    return
                    
                if args.json:
                    if len(component_metrics) == 1:
                        print(json.dumps(component_metrics[0].to_dict(), indent=2, default=str))
                    else:
                        output = {"components": [m.to_dict() for m in component_metrics]}
                        print(json.dumps(output, indent=2, default=str))
                else:
                    # Display table based on mode
                    if args.full:
                        print(f"\n{checker.format_full_table(component_metrics)}")
                    else:
                        print(f"\n{checker.format_default_table(component_metrics)}")
                    
                    # Add logs if requested
                    if args.log:
                        log_lines = args.log if isinstance(args.log, int) else 5
                        log_output = checker.format_log_output(component_metrics, lines=log_lines)
                        if log_output:
                            print(log_output)
                            
                    if args.trends:
                        for metrics in component_metrics:
                            print(f"\n{checker.get_trends_summary(metrics.name)}")
                        
            else:
                # Check all components
                component_metrics, system_metrics = await checker.check_all_components_comprehensive(show_progress=not args.json)
                
                if args.json:
                    output = {
                        "system": system_metrics.to_dict() if hasattr(system_metrics, 'to_dict') else asdict(system_metrics),
                        "components": [m.to_dict() for m in component_metrics]
                    }
                    print(json.dumps(output, indent=2, default=str))
                else:
                    # Display table based on mode
                    if args.full:
                        print(f"\n{checker.format_full_table(component_metrics)}")
                    else:
                        print(f"\n{checker.format_default_table(component_metrics)}")
                        
                    # Skip system summary per Casey's request
                    # print(f"\n{checker.format_system_summary(system_metrics)}")
                    
                    # Add logs if requested
                    if args.log:
                        log_lines = args.log if isinstance(args.log, int) else 5
                        log_output = checker.format_log_output(component_metrics, lines=log_lines)
                        if log_output:
                            print(log_output)
                    
                    if args.trends:
                        print(f"\n{checker.get_trends_summary()}")
                        
        if args.watch:
            print(f"👁️  Watching Tekton status (refresh every {args.watch}s). Press Ctrl+C to stop.")
            try:
                while True:
                    os.system('clear' if os.name == 'posix' else 'cls')  # Clear screen
                    await check_and_display()
                    await asyncio.sleep(args.watch)
            except KeyboardInterrupt:
                print("\n\nWatch stopped by user")
        else:
            await check_and_display()


if __name__ == "__main__":
    asyncio.run(main())
