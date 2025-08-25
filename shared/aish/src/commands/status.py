"""
aish status command - Show forwarding, AIs, and terminals status
"""
import json
import sys
import socket
import os
from pathlib import Path
from datetime import datetime
from shared.env import TektonEnviron
from shared.aish.src.forwarding.forwarding_registry import ForwardingRegistry
from shared.aish.src.registry.ci_registry import CIRegistry

# Try to import landmarks if available
try:
    from landmarks import architecture_decision, integration_point, api_contract, state_checkpoint
except ImportError:
    # Landmarks not available, create no-op decorators
    def architecture_decision(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def api_contract(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func):
            return func
        return decorator

def check_ai_status(ai_name, port):
    """Check if an CI is running by checking its port."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', int(port)))
        sock.close()
        return result == 0
    except:
        return False

def check_port_status(port):
    """Check if a port is listening."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', int(port)))
        sock.close()
        return f"{port} (listening)" if result == 0 else f"{port} (not listening)"
    except:
        return f"{port} (error)"

def check_socket_status(socket_path):
    """Check Unix socket status."""
    if not os.path.exists(socket_path):
        return f"{socket_path} (not found)"
    
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.connect(socket_path)
        sock.close()
        
        # Get last modified time
        mtime = os.path.getmtime(socket_path)
        age = int(datetime.now().timestamp() - mtime)
        if age < 60:
            return f"{socket_path} (active {age}s ago)"
        else:
            return f"{socket_path} (active {age//60}m ago)"
    except:
        return f"{socket_path} (not responding)"

def check_binary_status(binary_path):
    """Check binary file status."""
    if not os.path.exists(binary_path):
        return "Binary not found"
    
    if os.access(binary_path, os.X_OK):
        size_kb = os.path.getsize(binary_path) / 1024
        return f"Binary ({size_kb:.1f}KB)"
    else:
        return "Binary (not executable)"

def get_ci_tools_dynamic():
    """Get CI tools with dynamic status from registry and environment."""
    registry = CIRegistry()
    tools_status = []
    
    # First try to get tools from registry
    try:
        # Check if tools are in the registry
        all_entries = registry.get_all()
        registry_tools = {name: info for name, info in all_entries.items() 
                         if info.get('type') == 'tool'}
        
        if registry_tools:
            # Use registry tools
            for name, info in sorted(registry_tools.items()):
                if 'port' in info:
                    status = check_port_status(info['port'])
                elif 'socket' in info:
                    status = check_socket_status(info['socket'])
                else:
                    status = info.get('status', 'Unknown')
                tools_status.append((name, status))
            return tools_status
    except:
        pass
    
    # Fall back to environment-based detection
    
    # Echo tool
    echo_port = TektonEnviron.get('ECHO_TOOL_PORT')
    if echo_port:
        status = check_port_status(int(echo_port))
    else:
        status = "Port not configured"
    tools_status.append(('echo_tool', status))
    
    # Message bus socket
    message_bus_socket = TektonEnviron.get('CI_MESSAGE_BUS_SOCKET', '/tmp/ci_message_bus.sock')
    status = check_socket_status(message_bus_socket)
    tools_status.append(('message_bus', status))
    
    # Context manager
    context_mgr_port = TektonEnviron.get('CONTEXT_MANAGER_PORT')
    if context_mgr_port:
        status = check_port_status(int(context_mgr_port))
    else:
        status = "Port not configured"
    tools_status.append(('context_manager', status))
    
    # CI Launcher binary
    ci_tools_dir = TektonEnviron.get('CI_TOOLS_DIR', 
                                    f"{TektonEnviron.get('TEKTON_ROOT')}/ci_tools")
    launcher_path = os.path.join(ci_tools_dir, 'launcher')
    status = check_binary_status(launcher_path)
    tools_status.append(('launcher', status))
    
    return tools_status

def check_mcp_server():
    """Check if aish MCP server is running."""
    mcp_port = int(TektonEnviron.get('AISH_MCP_PORT', '8318'))
    return check_ai_status('aish-mcp', mcp_port)

def get_recent_messages():
    """Get recent messages from history."""
    # Use environment-specific history file
    tekton_root = TektonEnviron.get('TEKTON_ROOT', str(Path.home()))
    history_file = Path(tekton_root) / '.tekton' / '.aish_history'
    # Fallback to home directory if not found
    if not history_file.exists():
        history_file = Path.home() / '.aish_history'
    recent = []
    
    if history_file.exists():
        try:
            with open(history_file, 'r') as f:
                lines = f.readlines()
                # Get last 5 non-empty lines
                for line in reversed(lines):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        recent.append(line)
                        if len(recent) >= 5:
                            break
        except:
            pass
    
    return list(reversed(recent))

def get_active_terminals():
    """Get list of active terminals from Terma."""
    try:
        import requests
        terma_port = int(TektonEnviron.get('TERMA_PORT', '8304'))
        response = requests.get(f"http://localhost:{terma_port}/api/terminals", timeout=2)
        if response.status_code == 200:
            terminals = response.json()
            # Format terminal display with tty info
            formatted_terminals = []
            for t in terminals:
                if t.get('active', False):
                    name = t['name']
                    pid = t.get('pid', 'unknown')
                    tty = t.get('tty', 'unknown')
                    formatted_terminals.append(f"{name} (pid {pid}) - {tty}")
            return formatted_terminals
    except:
        pass
    return []

@api_contract(
    title="System Status Report",
    description="Provides comprehensive status of CI components, forwards, and terminals",
    endpoint="internal",
    method="function",
    request_schema={"args": "list[str]"},
    response_schema={"status": "dict", "format": "json|text"}
)
def handle_status_command(args=None):
    """Handle the aish status command."""
    
    # Get CI registry for Greek Chorus components
    registry = CIRegistry()
    
    # Get forwarding registry
    fwd_registry = ForwardingRegistry()
    forwards = fwd_registry.list_forwards()
    
    # Get environment configuration
    tekton_root = TektonEnviron.get('TEKTON_ROOT', 'Not set')
    port_base = TektonEnviron.get('TEKTON_PORT_BASE', '8300')
    ai_port_base = TektonEnviron.get('TEKTON_AI_PORT_BASE', '42000')
    mcp_port = TektonEnviron.get('AISH_MCP_PORT', '8318')
    mcp_running = check_mcp_server()
    
    # Get current coder instance (A, B, or C)
    coder_instance = 'c'  # default
    if 'Coder-A' in tekton_root:
        coder_instance = 'a'
    elif 'Coder-B' in tekton_root:
        coder_instance = 'b'
    
    # Build Greek Chorus component data
    greek_components = []
    for name in sorted(registry.GREEK_CHORUS.keys()):
        ci_info = registry.get_by_name(name)
        if ci_info:
            # Extract port from endpoint
            endpoint = ci_info.get('endpoint', '')
            port = endpoint.split(':')[-1] if ':' in endpoint else 'Unknown'
            
            # Get CI port
            try:
                ai_port = registry.get_ai_port(name)
            except:
                ai_port = 'Unknown'
            
            greek_components.append({
                'name': name,
                'port': port,
                'ai_port': str(ai_port),
                'description': registry.GREEK_CHORUS[name]['description']
            })
    
    # Get CI tools with dynamic status
    ci_tools = get_ci_tools_dynamic()
    
    # Separate CI and project forwards
    ai_forwards = {}
    project_forwards = {}
    
    for key, terminal in forwards.items():
        if key.startswith('project:'):
            project_name = key[8:]
            project_forwards[project_name] = terminal
        else:
            ai_forwards[key] = terminal
    
    # Get active terminals
    active_terminals = get_active_terminals()
    
    # Get recent messages
    recent_messages = get_recent_messages()
    
    # Check for JSON output
    if args and ('--json' in args or 'json' in args):
        output = {
            'configuration': {
                'tekton_root': tekton_root,
                'port_base': port_base,
                'ai_port_base': ai_port_base,
                'mcp_port': mcp_port,
                'mcp_running': mcp_running
            },
            'greek_chorus': greek_components,
            'ci_tools': {name: status for name, status in ci_tools},
            'ai_forwards': ai_forwards,
            'project_forwards': project_forwards,
            'active_terminals': active_terminals,
            'recent_messages': recent_messages
        }
        print(json.dumps(output, indent=2))
    else:
        # Human-readable output
        print("aish Status Report")
        print("=" * 50)
        
        # Configuration section
        print("Configuration:")
        print(f"  TEKTON_ROOT: {tekton_root}")
        print(f"  TEKTON_PORT_BASE: {port_base}")
        print(f"  TEKTON_AI_PORT_BASE: {ai_port_base}")
        print(f"  aish MCP Server: {'Running' if mcp_running else 'Stopped'} on port {mcp_port}")
        
        # Greek Chorus section
        print("\nGreek Chorus Components:")
        print("-" * 60)
        print("  Component      Port   CI Port")
        print("  ----------     ----   -------")
        for comp in greek_components:
            print(f"  {comp['name']:<14} {comp['port']:<6} {comp['ai_port']}")
        
        # CI Tools section with dynamic status
        print("\nCI Tools:")
        print("-" * 60)
        print("  Tool              Port/Socket")
        print("  ----              -----------")
        
        # Find max width for tool names
        if ci_tools:
            max_name_len = max(len(name) for name, _ in ci_tools)
            for tool_name, status in ci_tools:
                print(f"  {tool_name:<{max_name_len+2}} {status}")
        else:
            print("  No CI tools found")
        
        # Active Terminals section
        print("\nActive Terminals:")
        print("-" * 60)
        if active_terminals:
            for terminal in active_terminals:
                print(f"  • {terminal}")
        else:
            print("  None detected")
        
        # Active Forwards section
        print("\nActive Forwards:")
        print("-" * 60)
        if ai_forwards or project_forwards:
            for ai, terminal in ai_forwards.items():
                print(f"  {ai} → {terminal}")
            for project, terminal_info in project_forwards.items():
                # Handle both string and dict format
                if isinstance(terminal_info, dict):
                    terminal = terminal_info.get('terminal', 'unknown')
                    json_mode = " [JSON]" if terminal_info.get('json_mode') else ""
                    print(f"  {project} (project) → {terminal}{json_mode}")
                else:
                    print(f"  {project} (project) → {terminal_info}")
        else:
            print("  None")
        
        # Additional Status Commands
        print("\nAdditional Status Commands:")
        print("-" * 60)
        print(f"  tekton -c {coder_instance} status --json")
        
        print("\n" + "=" * 50)
    
    return True