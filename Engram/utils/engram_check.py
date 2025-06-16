#!/usr/bin/env python3
"""
Engram Status Checker

This script checks the status of Engram memory services and provides
information about running instances, versions, and memory connectivity.
It can also start, restart, or stop services as needed.

Usage:
  ./engram_check.py                      # Check status only
  ./engram_check.py --start              # Start services if not running
  ./engram_check.py --restart            # Restart services regardless of state
  ./engram_check.py --stop               # Stop running services
  ./engram_check.py --query "test query" # Test memory query
  ./engram_check.py --version-check      # Check for newer versions
"""

import os
import sys
import json
import time
import argparse
import subprocess
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Check for required dependencies
try:
    import requests
except ImportError:
    print("Error: 'requests' module not found.")
    print("Please install required dependencies with:")
    print("    pip install requests")
    print("or run the install script:")
    print("    ./install.sh")
    sys.exit(1)

# ANSI color codes for terminal output
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Default URLs for services
DEFAULT_API_URL = "http://127.0.0.1:8000"
DEFAULT_SERVER_URL = "http://127.0.0.1:8000"
DEFAULT_DATA_DIR = os.path.expanduser("~/.engram")
DEFAULT_HERMES_URL = "http://127.0.0.1:8100/api"

def get_api_url():
    """Get the base URL for the Engram API server."""
    return os.environ.get("ENGRAM_API_URL", DEFAULT_API_URL)

def get_server_url():
    """Get the URL for the Engram memory server."""
    return os.environ.get("ENGRAM_SERVER_URL", DEFAULT_SERVER_URL)
    
def get_hermes_url():
    """Get the URL for Hermes API."""
    return os.environ.get("HERMES_URL", DEFAULT_HERMES_URL)
    
def is_hermes_mode():
    """Check if Engram is running in Hermes integration mode."""
    return os.environ.get("ENGRAM_MODE", "").lower() == "hermes"

def get_script_path():
    """Get the path to the script directory."""
    return os.path.dirname(os.path.abspath(__file__))

def get_engram_root():
    """Find the Engram root directory regardless of where script is run from."""
    # Start from the script's directory
    script_dir = get_script_path()
    
    # If script is in utils directory, parent should be Engram root
    if os.path.basename(script_dir) == "utils":
        return os.path.dirname(script_dir)
        
    # Check if we're already in Engram directory
    if os.path.exists(os.path.join(script_dir, "engram")) and os.path.isdir(os.path.join(script_dir, "engram")):
        return script_dir
    
    # Look for Engram within Tekton directory structure
    potential_paths = [
        # From current directory
        os.path.join(os.getcwd(), "Engram"),
        # From script directory
        os.path.join(script_dir, "Engram"),
        # From parent of script directory (if script is in a subdirectory)
        os.path.join(os.path.dirname(script_dir), "Engram"),
        # From Tekton root (if script is somewhere in Tekton)
        os.path.join(os.path.dirname(os.path.dirname(script_dir)), "Engram"),
        # Common installation paths
        os.path.expanduser("~/projects/Tekton/Engram"),
        os.path.expanduser("~/projects/github/Tekton/Engram"),
        "/usr/local/share/tekton/Engram"
    ]
    
    # Check each potential path
    for path in potential_paths:
        if os.path.exists(path) and os.path.isdir(path):
            if os.path.exists(os.path.join(path, "engram")) or os.path.exists(os.path.join(path, "core")):
                return path
    
    # If we couldn't find it, default to the script's parent directory
    return os.path.dirname(script_dir)

def check_process_running(name_pattern: str) -> List[int]:
    """Check if a process with the given name pattern is running."""
    try:
        # Different command for macOS/Linux vs Windows
        if sys.platform == "win32":
            cmd = ["tasklist", "/FI", f"IMAGENAME eq {name_pattern}"]
        else:
            # Use pgrep for more reliable pattern matching
            result = subprocess.run(["pgrep", "-f", name_pattern], capture_output=True, text=True)
            if result.returncode == 0:
                # pgrep successful, parse the output for PIDs
                pids = [int(pid) for pid in result.stdout.strip().split()]
                return pids
            
            # Fallback to ps aux if pgrep fails
            cmd = ["ps", "aux"]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 and sys.platform != "win32":  # Ignore error for pgrep fallback
            print(f"{RED}Error checking process status: {result.stderr}{RESET}")
            return []
        
        output = result.stdout
        
        # For Windows, just check if the process is in the output
        if sys.platform == "win32":
            return [1] if name_pattern in output else []
        
        # For macOS/Linux, parse the output to find PIDs
        pids = []
        for line in output.split("\n"):
            if name_pattern in line:
                parts = line.split()
                if len(parts) > 1:
                    try:
                        pids.append(int(parts[1]))
                    except ValueError:
                        pass
        return pids
    except Exception as e:
        print(f"{RED}Error checking process status: {e}{RESET}")
        return []

def check_services() -> Dict[str, Any]:
    """Check if Engram memory services are running."""
    result = {
        "memory_server": {
            "running": False,
            "pid": None,
            "version": None,
            "url": get_server_url(),
        },
        "api_server": {
            "running": False,
            "pid": None,
            "version": None,
            "url": get_api_url(),
        },
        "memory_connected": False,
        "mem0_available": False,
        "vector_available": False,
        "is_hermes_mode": is_hermes_mode(),
        "hermes_connected": False
    }
    
    # First check for our streamlined server
    server_pids = check_process_running("engram.api.server")
    
    if server_pids:
        # If unified server is running, all services are available
        result["memory_server"]["running"] = True
        result["memory_server"]["pid"] = server_pids[0]
        result["api_server"]["running"] = True
        result["api_server"]["pid"] = server_pids[0]
    else:
        # Check for the app-based server
        app_pids = check_process_running("engram.api.app")
        
        if app_pids:
            # If app server is running, services are available
            result["memory_server"]["running"] = True
            result["memory_server"]["pid"] = app_pids[0]
            result["api_server"]["running"] = True
            result["api_server"]["pid"] = app_pids[0]
        else:
            # Legacy check - look for separate memory server and HTTP wrapper
            memory_pids = check_process_running("engram_server") or check_process_running("engram_with_hermes")
            
            if memory_pids:
                result["memory_server"]["running"] = True
                result["memory_server"]["pid"] = memory_pids[0]
            
            http_pids = check_process_running("engram_http") or check_process_running("engram_with_faiss")
                
            if http_pids:
                result["api_server"]["running"] = True
                result["api_server"]["pid"] = http_pids[0]
    
    # Try to get health and connectivity information
    if result["api_server"]["running"]:
        try:
            # Try the new unified API endpoint
            api_url = get_api_url()
            response = requests.get(f"{api_url}/health", timeout=2)
            if response.status_code == 200:
                health_data = response.json()
                if "status" in health_data:
                    result["memory_connected"] = health_data.get("status") == "ok" or health_data.get("status") == "healthy"
                else:
                    result["memory_connected"] = True  # Assume it's connected if endpoint responds
                    
                result["mem0_available"] = health_data.get("mem0_available", False)
                result["vector_available"] = health_data.get("vector_available", False) or "storage_type" in health_data
                
                # Try to get the storage type
                if "storage_type" in health_data:
                    result["storage_type"] = health_data["storage_type"]
                    
                # Try to get version information if available
                if "version" in health_data:
                    result["memory_server"]["version"] = health_data["version"]
                    result["api_server"]["version"] = health_data["version"]
        except Exception as e:
            result["health_error"] = str(e)
    
    # Check Hermes connection if in Hermes mode
    if result["is_hermes_mode"]:
        try:
            hermes_url = get_hermes_url()
            response = requests.get(f"{hermes_url}/health", timeout=1)
            if response.status_code == 200:
                result["hermes_connected"] = True
                # Try to query for registered services
                try:
                    services_resp = requests.get(f"{hermes_url}/registry/services", timeout=1)
                    if services_resp.status_code == 200:
                        services_data = services_resp.json()
                        engram_services = [svc for svc in services_data if "engram" in svc.get("name", "").lower()]
                        result["hermes_services"] = engram_services
                except Exception:
                    pass
        except Exception as e:
            result["hermes_error"] = str(e)
    
    return result

def test_memory_query(query: str = "test") -> Dict[str, Any]:
    """Test a memory query to ensure the memory service is working."""
    result = {
        "success": False,
        "response": None,
        "error": None,
    }
    
    try:
        # Try new unified API endpoint first
        api_url = get_api_url()
        url = f"{api_url}/search?query={urllib.parse.quote_plus(query)}&namespace=longterm&limit=1"
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                result["success"] = True
                result["response"] = response.json()
                return result
        except requests.RequestException:
            # New endpoint failed, try legacy endpoint
            pass
            
        # Try legacy endpoint
        url = f"{api_url}/query?query={urllib.parse.quote_plus(query)}&namespace=longterm&limit=1"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            result["success"] = True
            result["response"] = response.json()
            
    except requests.RequestException as e:
        result["error"] = f"HTTP error: {str(e)}"
    except Exception as e:
        result["error"] = str(e)
    
    return result

def start_services(client_id: str = "default", data_dir: str = None, force_restart: bool = False, hermes_mode: bool = False) -> bool:
    """Start the Engram memory services."""
    # First check if services are already running
    if not force_restart:
        status = check_services()
        if status["memory_server"]["running"] and status["api_server"]["running"]:
            print(f"{YELLOW}Engram services are already running.{RESET}")
            return True
    
    # Stop services if force_restart is True
    if force_restart:
        stop_services()
    
    # Use the Engram root finder to locate the root directory
    engram_root = get_engram_root()
    
    if not engram_root or not os.path.exists(engram_root):
        print(f"{RED}Error: Could not locate Engram root directory{RESET}")
        return False
        
    print(f"{GREEN}Found Engram at: {engram_root}{RESET}")
    
    # Determine which script to use based on mode
    if hermes_mode:
        # Try to find the Hermes script in multiple locations
        script_locations = [
            os.path.join(engram_root, "utils", "engram-for-hermes"),
            os.path.join(engram_root, "utils", "engram_for_hermes"),
            os.path.join(engram_root, "core", "engram-for-hermes"),
            os.path.join(engram_root, "core", "engram_consolidated")  # Fallback
        ]
        
        # Use the first script that exists
        for script_path in script_locations:
            if os.path.exists(script_path):
                engram_start_path = script_path
                # Set environment variable for Hermes mode if not using dedicated script
                if "engram_consolidated" in script_path:
                    os.environ["ENGRAM_MODE"] = "hermes"
                break
        else:
            # If none found, use a python module approach as last resort
            engram_start_path = sys.executable
            os.environ["ENGRAM_MODE"] = "hermes"
            print(f"{YELLOW}No Hermes script found, falling back to Python module{RESET}")
    else:
        # Try to find the standalone script in multiple locations
        script_locations = [
            os.path.join(engram_root, "core", "engram-standalone"),
            os.path.join(engram_root, "core", "engram_consolidated"),
            os.path.join(engram_root, "scripts", "engram-standalone"),
            os.path.join(engram_root, "scripts", "engram_standalone")
        ]
        
        # Use the first script that exists
        for script_path in script_locations:
            if os.path.exists(script_path):
                engram_start_path = script_path
                break
        else:
            # If none found, use a python module approach as last resort
            engram_start_path = sys.executable
            print(f"{YELLOW}No standalone script found, falling back to Python module{RESET}")
    
    # Handle case where we're using Python module directly
    use_python_module = False
    if engram_start_path == sys.executable:
        use_python_module = True
    
    # Make sure the script is executable if it's not the Python interpreter
    if not use_python_module:
        try:
            os.chmod(engram_start_path, 0o755)
        except Exception:
            pass
    
    # Build command
    if use_python_module:
        # Using Python module directly
        cmd = [
            engram_start_path,
            "-m", "engram.api.server",
            "--client-id", client_id
        ]
        
        # Add PYTHONPATH to ensure module can be found
        os.environ["PYTHONPATH"] = f"{engram_root}:{os.environ.get('PYTHONPATH', '')}"
    else:
        # Using shell script
        cmd = [engram_start_path, "--client-id", client_id]
    
    # Add common arguments
    if data_dir:
        cmd.extend(["--data-dir", data_dir])
    
    # Add fallback mode for testing
    cmd.append("--fallback")
    
    # Add host and port
    cmd.extend(["--host", "127.0.0.1", "--port", "8000"])
    
    # Run the start script in background
    try:
        # Use Popen to start the process in the background
        process = subprocess.Popen(cmd, 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE, 
                                  universal_newlines=True)
        
        # Wait briefly to check if it immediately crashes
        try:
            return_code = process.wait(timeout=1)
            if return_code != 0:
                stdout, stderr = process.communicate()
                print(f"{RED}Error starting services:\n{stderr}{RESET}")
                return False
        except subprocess.TimeoutExpired:
            # Process is still running, which is good
            pass
            
        print(f"{GREEN}Services started successfully with PID {process.pid}.{RESET}")
        
        # Wait a moment for services to initialize
        time.sleep(2)
        
        # Check if the services are running
        status = check_services()
        if status["memory_server"]["running"] and status["api_server"]["running"]:
            print(f"{GREEN}Services are now running.{RESET}")
            return True
        else:
            print(f"{YELLOW}Services were started but may not be fully initialized yet.{RESET}")
            return True
            
    except Exception as e:
        print(f"{RED}Error starting services: {e}{RESET}")
        return False

def stop_services() -> bool:
    """Stop the Engram memory services."""
    status = check_services()
    
    # Check if services are running
    if not status["memory_server"]["running"] and not status["api_server"]["running"]:
        print(f"{YELLOW}No Engram services are running.{RESET}")
        return True
    
    # Get PIDs
    pids = []
    if status["memory_server"]["running"] and status["memory_server"]["pid"]:
        pids.append(status["memory_server"]["pid"])
    if status["api_server"]["running"] and status["api_server"]["pid"] and status["api_server"]["pid"] not in pids:
        pids.append(status["api_server"]["pid"])
    
    # If running in Hermes mode, check if we should use Hermes to stop the service
    if status.get("is_hermes_mode", False) and status.get("hermes_connected", False):
        try:
            print(f"{YELLOW}Attempting to stop services via Hermes...{RESET}")
            hermes_url = get_hermes_url()
            
            # Find our service ID
            if "hermes_services" in status:
                for service in status["hermes_services"]:
                    if "engram" in service.get("name", "").lower():
                        service_id = service.get("id")
                        if service_id:
                            try:
                                stop_url = f"{hermes_url}/registry/services/{service_id}/stop"
                                response = requests.post(stop_url, timeout=5)
                                if response.status_code == 200:
                                    print(f"{GREEN}Successfully stopped service via Hermes.{RESET}")
                                    time.sleep(2)  # Give it time to stop
                                    # Check if it's really stopped
                                    new_status = check_services()
                                    if not new_status["memory_server"]["running"] and not new_status["api_server"]["running"]:
                                        return True
                            except Exception as e:
                                print(f"{YELLOW}Error stopping via Hermes: {e}. Falling back to direct process termination.{RESET}")
        except Exception as e:
            print(f"{YELLOW}Error stopping via Hermes: {e}. Falling back to direct process termination.{RESET}")
    
    # Stop processes directly
    print(f"{YELLOW}Stopping Engram processes directly...{RESET}")
    success = True
    for pid in pids:
        try:
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
            else:
                # Try SIGTERM first
                subprocess.run(["kill", str(pid)], capture_output=True)
                time.sleep(1)
                
                # Check if still running, use SIGKILL if needed
                if check_process_running(str(pid)):
                    subprocess.run(["kill", "-9", str(pid)], capture_output=True)
                
            print(f"{GREEN}Stopped process with PID {pid}.{RESET}")
        except Exception as e:
            print(f"{RED}Error stopping process with PID {pid}: {e}{RESET}")
            success = False
    
    # Give processes time to shut down
    time.sleep(1)
    
    # Verify they're stopped
    status = check_services()
    if status["memory_server"]["running"] or status["api_server"]["running"]:
        print(f"{YELLOW}Warning: Some services are still running after stop attempt.{RESET}")
        success = False
    
    # Also attempt to kill by pattern if PIDs didn't work
    try:
        # Kill any remaining engram server processes
        subprocess.run(["pkill", "-f", "engram.api.server"], capture_output=True)
        subprocess.run(["pkill", "-f", "engram.api.app"], capture_output=True)
        subprocess.run(["pkill", "-f", "engram-standalone"], capture_output=True)
        subprocess.run(["pkill", "-f", "engram-for-hermes"], capture_output=True)
    except Exception:
        pass
    
    return success

def check_version() -> Dict[str, Any]:
    """Check current version against the latest in the repo."""
    result = {
        "current_version": "Unknown",
        "latest_version": "Unknown",
        "update_available": False,
    }
    
    # Get current version from code
    try:
        script_path = get_script_path()
        version_path = os.path.join(script_path, "engram", "__init__.py")
        with open(version_path, "r") as f:
            version_file = f.read()
            for line in version_file.split("\n"):
                if line.startswith("__version__"):
                    result["current_version"] = line.split("=")[1].strip().strip("'\"")
                    break
    except Exception:
        pass
    
    # Get latest version (in a real implementation, this would check GitHub or PyPI)
    # For now, we'll just report the current version
    result["latest_version"] = result["current_version"]
    
    # In a real implementation, compare versions and set update_available
    # result["update_available"] = parse_version(result["latest_version"]) > parse_version(result["current_version"])
    
    return result

def check_memory_files() -> Dict[str, Any]:
    """Check memory files status and statistics."""
    result = {
        "files_exist": False,
        "client_id": "default",  # Default
        "memory_count": 0,
        "namespaces": [],
        "last_modified": None,
        "vector_db_present": False,
        "storage_type": "unknown"
    }
    
    # Get data directory path - check both the new and old locations
    data_dir = os.environ.get("ENGRAM_DATA_DIR", DEFAULT_DATA_DIR)
    data_path = Path(data_dir)
    
    # Also check Tekton data directory
    tekton_data_dir = os.path.expanduser("~/.tekton/data")
    tekton_data_path = Path(tekton_data_dir)
    
    # Prioritize the configured data directory, fall back to Tekton data
    if data_path.exists():
        active_data_path = data_path
    elif tekton_data_path.exists():
        active_data_path = tekton_data_path
        result["data_dir_override"] = str(tekton_data_path)
    else:
        # No directories exist
        return result
    
    # First check for new-style files: check for JSON files in the data directory
    json_files = list(active_data_path.glob("*.json"))
    
    # Also check for index files which would indicate vector database
    index_files = list(active_data_path.glob("*.index"))
    vector_files = list(active_data_path.glob("*/*.index")) + list(active_data_path.glob("*/vector/*.index"))
    
    if index_files or vector_files:
        result["vector_db_present"] = True
        result["storage_type"] = "vector_db"
    
    # Check for primary client memory file
    memory_files = []
    
    # Look for new structure first (client_id/namespace.json)
    client_dirs = [d for d in active_data_path.iterdir() if d.is_dir()]
    for client_dir in client_dirs:
        client_json_files = list(client_dir.glob("*.json"))
        if client_json_files:
            result["files_exist"] = True
            result["client_id"] = client_dir.name
            memory_files.extend(client_json_files)
            break
    
    # Fall back to old structure (*-memories.json)
    if not memory_files:
        old_memory_files = list(active_data_path.glob("*-memories.json"))
        if old_memory_files:
            result["files_exist"] = True
            memory_files = old_memory_files
            result["client_id"] = old_memory_files[0].stem.split("-")[0]
            result["storage_type"] = "file_based"
    
    # If still no memory files found, check for any JSON files as last resort
    if not memory_files and json_files:
        result["files_exist"] = True
        memory_files = json_files
        
    # If we found files, analyze them
    if memory_files:
        # Use the newest file for the last_modified timestamp
        newest_file = max(memory_files, key=lambda f: f.stat().st_mtime)
        stat = newest_file.stat()
        result["last_modified"] = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
        
        # Count memories in all files
        total_count = 0
        namespaces = []
        
        for memory_file in memory_files:
            try:
                namespace_name = memory_file.stem.split("-")[1] if "-" in memory_file.stem else memory_file.stem
                
                with open(memory_file, "r") as f:
                    try:
                        memory_data = json.load(f)
                        
                        # Handle different file formats
                        if isinstance(memory_data, dict):
                            # Old format: {namespace: [memories]}
                            for key, values in memory_data.items():
                                if isinstance(values, list):
                                    count = len(values)
                                    total_count += count
                                    if count > 0:
                                        namespaces.append({"name": key, "count": count})
                        elif isinstance(memory_data, list):
                            # New format: direct list of memories
                            count = len(memory_data)
                            total_count += count
                            if count > 0:
                                namespaces.append({"name": namespace_name, "count": count, "file": str(memory_file)})
                    except json.JSONDecodeError:
                        # Not a valid JSON file
                        continue
            except Exception as e:
                # Skip problematic files
                continue
        
        result["memory_count"] = total_count
        result["namespaces"] = namespaces
    
    return result

def display_status_report(services_status: Dict[str, Any], 
                          version_info: Dict[str, Any] = None,
                          memory_files: Dict[str, Any] = None,
                          query_result: Dict[str, Any] = None):
    """Display a comprehensive status report."""
    # Header
    print(f"\n{BOLD}{BLUE}==== Engram Memory Service Status Report ===={RESET}\n")
    
    # Services Status
    print(f"{BOLD}Service Status:{RESET}")
    memory_status = "✅ Running" if services_status["memory_server"]["running"] else "❌ Not Running"
    api_status = "✅ Running" if services_status["api_server"]["running"] else "❌ Not Running"
    hermes_mode = services_status.get("is_hermes_mode", False)
    hermes_status = "✅ Connected" if services_status.get("hermes_connected", False) else "❌ Not Connected" if hermes_mode else "➖ Not Used"
    
    print(f"  Memory Server: {memory_status} (PID: {services_status['memory_server']['pid']})")
    print(f"  API Server: {api_status} (PID: {services_status['api_server']['pid']})")
    print(f"  Memory Connection: {'✅ Connected' if services_status['memory_connected'] else '❌ Not Connected'}")
    print(f"  Mode: {'🔄 Hermes Integration' if hermes_mode else '🔄 Standalone'}")
    print(f"  Hermes: {hermes_status}")
    
    # Vector Storage
    vector_status = "✅ Available" if services_status["vector_available"] else "❌ Not Available" 
    print(f"  Vector DB Integration: {vector_status}")
    
    if "storage_type" in services_status:
        storage_type = services_status["storage_type"]
        print(f"  Storage Type: {GREEN}{storage_type}{RESET}")
    
    # Show Health Error if present
    if "health_error" in services_status:
        print(f"  {YELLOW}Health check error: {services_status['health_error']}{RESET}")
    
    # Hermes Services
    if hermes_mode and "hermes_services" in services_status:
        print(f"\n{BOLD}Hermes Integration:{RESET}")
        
        hermes_services = services_status["hermes_services"]
        if hermes_services:
            print(f"  Registered services:")
            for service in hermes_services:
                service_name = service.get("name", "Unknown")
                service_status = service.get("status", "Unknown")
                service_id = service.get("id", "Unknown")
                print(f"    - {service_name} ({service_status}, ID: {service_id})")
        else:
            print(f"  {YELLOW}No Engram services registered with Hermes{RESET}")
    
    # Version Information
    if version_info:
        print(f"\n{BOLD}Version Information:{RESET}")
        print(f"  Current Version: {version_info['current_version']}")
        print(f"  Latest Version: {version_info['latest_version']}")
        if version_info.get('update_available', False):
            print(f"  {YELLOW}Update Available!{RESET}")
        else:
            print(f"  {GREEN}Up to Date{RESET}")
    
    # Memory Files
    if memory_files:
        print(f"\n{BOLD}Memory Files:{RESET}")
        if memory_files["files_exist"]:
            print(f"  Client ID: {memory_files['client_id']}")
            print(f"  Total Memories: {memory_files['memory_count']}")
            print(f"  Last Modified: {memory_files['last_modified']}")
            print(f"  Storage Type: {memory_files.get('storage_type', 'unknown')}")
            print(f"  Vector DB Present: {'✅ Yes' if memory_files.get('vector_db_present', False) else '❌ No'}")
            
            if "data_dir_override" in memory_files:
                print(f"  {YELLOW}Using Tekton data directory: {memory_files['data_dir_override']}{RESET}")
            
            # Show namespaces if available
            if memory_files["namespaces"]:
                print(f"  Active Namespaces:")
                for ns in memory_files["namespaces"]:
                    print(f"    - {ns['name']}: {ns['count']} memories")
            else:
                print(f"  {YELLOW}No active namespaces found{RESET}")
        else:
            print(f"  {RED}No memory files found.{RESET}")
    
    # Query Test Results
    if query_result:
        print(f"\n{BOLD}Memory Query Test:{RESET}")
        if query_result["success"]:
            response = query_result["response"]
            
            # Handle different response formats
            if "count" in response:
                count = response.get("count", 0)
                print(f"  {GREEN}Query successful!{RESET}")
                print(f"  Results: {count} memory items found")
                
                if count > 0 and "results" in response:
                    result = response['results'][0]
                    if isinstance(result, dict):
                        content = result.get('content', '')
                        if len(content) > 100:
                            content = content[:97] + "..."
                        print(f"  First result: \"{content}\"")
            elif isinstance(response, list):
                # New API format
                count = len(response)
                print(f"  {GREEN}Query successful!{RESET}")
                print(f"  Results: {count} memory items found")
                
                if count > 0:
                    result = response[0]
                    if isinstance(result, dict):
                        content = result.get('content', '')
                        if len(content) > 100:
                            content = content[:97] + "..."
                        print(f"  First result: \"{content}\"")
        else:
            print(f"  {RED}Query failed: {query_result['error']}{RESET}")
    
    # Footer
    print(f"\n{BOLD}{BLUE}===================================={RESET}\n")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Engram Memory Status Checker")
    
    # Action arguments
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument("--start", action="store_true", help="Start services if not running")
    action_group.add_argument("--restart", action="store_true", help="Restart services")
    action_group.add_argument("--stop", action="store_true", help="Stop running services")
    
    # Mode arguments
    mode_group = parser.add_argument_group("Mode Options")
    mode_group.add_argument("--hermes", action="store_true", help="Start in Hermes integration mode")
    mode_group.add_argument("--standalone", action="store_true", help="Start in standalone mode (default)")
    mode_group.add_argument("--hermes-url", type=str, default=None, 
                       help="URL for Hermes API (default: http://127.0.0.1:8100/api)")
    
    # Configuration arguments
    parser.add_argument("--client-id", type=str, default="default", help="Client ID for memory service")
    parser.add_argument("--data-dir", type=str, default=None, help="Directory to store memory data")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind server to")
    
    # Testing arguments
    parser.add_argument("--query", type=str, help="Test a memory query")
    parser.add_argument("--namespace", type=str, default="longterm", help="Namespace for memory query")
    
    # Other arguments
    parser.add_argument("--version-check", action="store_true", help="Check for newer versions")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    
    return parser.parse_args()

def check_interactive():
    """Check if the script is running in an interactive environment."""
    # For Claude, we'll detect if we're in a Jupyter notebook
    try:
        if 'ipykernel' in sys.modules:
            return True
    except:
        pass
    
    # Try to determine if we're in a Claude Code session or other interactive shell
    # This is a heuristic and might not be 100% accurate
    try:
        # Check for Claude-specific environment variables
        if "CLAUDE_API_KEY" in os.environ or "CLAUDE_ENVIRONMENT" in os.environ:
            return True
    except:
        pass
    
    return False

def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Check if we're running in Claude
    is_interactive = check_interactive()
    
    # Set up environment based on arguments
    if args.hermes_url:
        os.environ["HERMES_URL"] = args.hermes_url
    
    if args.hermes:
        os.environ["ENGRAM_MODE"] = "hermes"
    elif args.standalone:
        os.environ["ENGRAM_MODE"] = "standalone"
    
    # Enable debug mode if requested
    if args.debug:
        os.environ["ENGRAM_DEBUG"] = "1"
    
    # Handle actions
    if args.stop:
        stop_services()
        return
    
    if args.start or args.restart:
        # Determine if we should start in Hermes mode
        hermes_mode = args.hermes or (os.environ.get("ENGRAM_MODE", "").lower() == "hermes")
        
        # Start services
        start_services(
            client_id=args.client_id, 
            data_dir=args.data_dir, 
            force_restart=args.restart,
            hermes_mode=hermes_mode
        )
        
        # Give services time to start
        time.sleep(2)
    
    # Check services status
    services_status = check_services()
    
    # Check version if requested
    version_info = check_version() if args.version_check else None
    
    # Check memory files
    memory_files = check_memory_files()
    
    # Test memory query if requested
    query_result = None
    if args.query and services_status["api_server"]["running"]:
        query_result = test_memory_query(args.query)
    
    # Compile full results
    results = {
        "services": services_status,
        "version": version_info,
        "memory_files": memory_files,
        "query_result": query_result,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "hermes" if services_status.get("is_hermes_mode", False) else "standalone",
    }
    
    # Add arguments to result
    results["args"] = {
        "client_id": args.client_id,
        "data_dir": args.data_dir,
        "hermes_mode": args.hermes,
        "hermes_url": args.hermes_url or os.environ.get("HERMES_URL", DEFAULT_HERMES_URL),
        "host": args.host,
        "port": args.port,
    }
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        display_status_report(services_status, version_info, memory_files, query_result)
    
    # If services should be running but aren't, suggest starting them
    if is_interactive and not (services_status["memory_server"]["running"] and services_status["api_server"]["running"]):
        print(f"{YELLOW}Memory services aren't running. You can start them with:{RESET}")
        
        if services_status.get("is_hermes_mode", False):
            print(f"  ./engram_check.py --start --hermes")
        else:
            print(f"  ./engram_check.py --start --standalone")
    
    return results

if __name__ == "__main__":
    main()