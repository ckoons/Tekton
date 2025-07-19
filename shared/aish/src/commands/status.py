"""
aish status command - Show forwarding, AIs, and terminals status
"""
import json
import sys
import socket
from pathlib import Path
from shared.env import TektonEnviron
from forwarding.forwarding_registry import ForwardingRegistry

def check_ai_status(ai_name, port):
    """Check if an AI is running by checking its port."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', int(port)))
        sock.close()
        return result == 0
    except:
        return False

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
        terma_port = int(TektonEnviron.get('TERMA_PORT', '8300'))
        response = requests.get(f"http://localhost:{terma_port}/api/terminals", timeout=2)
        if response.status_code == 200:
            terminals = response.json()
            return [t['name'] for t in terminals if t.get('active', False)]
    except:
        pass
    return []

def handle_status_command(args=None):
    """Handle the aish status command."""
    
    # Get forwarding registry
    registry = ForwardingRegistry()
    forwards = registry.list_forwards()
    
    # Separate AI and project forwards
    ai_forwards = {}
    project_forwards = {}
    
    for key, terminal in forwards.items():
        if key.startswith('project:'):
            project_name = key[8:]  # Remove "project:" prefix
            project_forwards[project_name] = terminal
        else:
            ai_forwards[key] = terminal
    
    # Get AI status
    ai_components = {
        'numa': TektonEnviron.get('NUMA_PORT', '8316'),
        'apollo': TektonEnviron.get('APOLLO_PORT', '8312'),
        'athena': TektonEnviron.get('ATHENA_PORT', '8313'),
        'rhetor': TektonEnviron.get('RHETOR_PORT', '8003'),
        'sophia': TektonEnviron.get('SOPHIA_PORT', '8314'),
        'prometheus': TektonEnviron.get('PROMETHEUS_PORT', '8310'),
        'metis': TektonEnviron.get('METIS_PORT', '8308'),
        'harmonia': TektonEnviron.get('HARMONIA_PORT', '8309'),
        'synthesis': TektonEnviron.get('SYNTHESIS_PORT', '8315'),
        'telos': TektonEnviron.get('TELOS_PORT', '8307')
    }
    
    ai_status = {}
    for ai_name, port in ai_components.items():
        is_running = check_ai_status(ai_name, port)
        ai_status[ai_name] = {
            'status': 'running' if is_running else 'stopped',
            'port': int(port),
            'forwarded_to': ai_forwards.get(ai_name)
        }
    
    # Get recent messages
    recent_messages = get_recent_messages()
    
    # Get active terminals
    active_terminals = get_active_terminals()
    
    # Check for JSON output
    if args and ('--json' in args or 'json' in args):
        output = {
            'ai_forwards': ai_forwards,
            'project_forwards': project_forwards,
            'ai_status': ai_status,
            'recent_messages': recent_messages,
            'active_terminals': active_terminals
        }
        print(json.dumps(output, indent=2))
    else:
        # Human-readable output
        print("aish Status Report")
        print("=" * 50)
        
        print("\nActive AI Forwards:")
        print("-" * 30)
        if ai_forwards:
            for ai, terminal in ai_forwards.items():
                status = "✓" if ai_status.get(ai, {}).get('status') == 'running' else "✗"
                print(f"  {status} {ai:<12} → {terminal}")
        else:
            print("  None")
        
        print("\nActive Project Forwards:")
        print("-" * 30)
        if project_forwards:
            for project, terminal in project_forwards.items():
                print(f"  {project:<12} → {terminal}")
        else:
            print("  None")
        
        print("\nAI Components:")
        print("-" * 30)
        for ai, info in sorted(ai_status.items()):
            status = "✓" if info['status'] == 'running' else "✗"
            forward = f" → {info['forwarded_to']}" if info['forwarded_to'] else ""
            print(f"  {status} {ai:<12} (port {info['port']}){forward}")
        
        print("\nActive Terminals:")
        print("-" * 30)
        if active_terminals:
            for terminal in active_terminals:
                print(f"  • {terminal}")
        else:
            print("  None detected")
        
        print("\nRecent Messages (last 5):")
        print("-" * 30)
        if recent_messages:
            for i, msg in enumerate(recent_messages, 1):
                # Truncate long messages
                if len(msg) > 60:
                    msg = msg[:57] + "..."
                print(f"  {i}. {msg}")
        else:
            print("  No recent messages")
        
        print("\n" + "=" * 50)
    
    return True