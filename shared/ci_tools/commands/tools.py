"""
CI Tools command handler for aish.
Provides lifecycle management for CI tools.
"""

import sys
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.ci_tools import get_registry, ToolLauncher


def handle_tools_command(args):
    """
    Handle CI tools commands:
    - aish tools list                          # List all CI tools
    - aish tools status [tool-name]            # Show tool status
    - aish tools launch <tool-name> [--session <name>] [--instance <name>]  # Launch a tool
    - aish tools terminate <tool-name|instance-name>  # Terminate a tool
    - aish tools capabilities <tool-name>      # Show tool capabilities
    - aish tools create <instance-name> --type <tool-type>  # Create new instance
    - aish tools instances                     # List all running instances
    - aish tools define <name> [options]       # Define a new tool type
    - aish tools defined [name]                # List/show defined tools
    - aish tools undefine <name>               # Remove tool definition
    """
    if not args:
        show_tools_help()
        return
    
    command = args[0].lower()
    
    if command == 'list':
        list_tools()
    elif command == 'status':
        tool_name = args[1] if len(args) > 1 else None
        show_status(tool_name)
    elif command == 'launch':
        if len(args) < 2:
            print("Error: launch requires a tool name")
            return
        launch_tool(args[1], args[2:])
    elif command == 'terminate':
        if len(args) < 2:
            print("Error: terminate requires a tool or instance name")
            return
        terminate_tool(args[1])
    elif command == 'capabilities':
        if len(args) < 2:
            print("Error: capabilities requires a tool name")
            return
        show_capabilities(args[1])
    elif command == 'create':
        if len(args) < 2:
            print("Error: create requires an instance name")
            return
        create_instance(args[1], args[2:])
    elif command == 'instances':
        list_instances()
    elif command == 'define':
        if len(args) < 2:
            print("Error: define requires a tool name")
            return
        define_tool(args[1], args[2:])
    elif command == 'defined':
        tool_name = args[1] if len(args) > 1 else None
        show_defined_tools(tool_name)
    elif command == 'undefine':
        if len(args) < 2:
            print("Error: undefine requires a tool name")
            return
        undefine_tool(args[1])
    elif command == 'help':
        show_tools_help()
    else:
        print(f"Unknown tools command: {command}")
        show_tools_help()


def show_tools_help():
    """Show help for tools commands."""
    print("""CI Tools Commands:

Lifecycle Management:
  aish tools list                    List available CI tools
  aish tools status [name]           Show tool/instance status
  aish tools launch <name>           Launch a tool
  aish tools terminate <name>        Terminate tool/instance
  aish tools instances               List all running instances

Instance Management:
  aish tools create <name> --type <tool>  Create named instance
  aish tools launch <name> --instance <id>  Launch with instance ID

Tool Definition:
  aish tools define <name> [options] Define a new tool type
  aish tools defined [name]          List/show defined tools
  aish tools undefine <name>         Remove tool definition
  
Tool Information:
  aish tools capabilities <name>     Show tool capabilities
  aish tools help                    Show this help

Define Options:
  --type <base>         Base adapter type (generic, claude-code, etc.)
  --executable <path>   Path to tool executable
  --description <text>  Tool description
  --port <num|auto>     Port number or 'auto' for dynamic
  --capabilities <list> Comma-separated capabilities
  --launch-args <args>  Launch arguments
  --health-check <type> Health check method
  --env <key=value>     Environment variables

Examples:
  aish tools define openai-coder --type generic --executable openai --port auto
  aish tools launch claude-code
  aish tools create review-bot --type claude-code
  aish tools instances
  aish tools terminate review-bot
""")


def list_tools():
    """List all available CI tools."""
    registry = get_registry()
    tools = registry.get_tools()
    
    print("Available CI Tools:")
    print("-" * 70)
    print(f"{'Name':<15} {'Description':<35} {'Port':<10} {'Status':<10}")
    print("-" * 70)
    
    for name, config in tools.items():
        status = registry.get_tool_status(name)
        running = "running" if status.get('running') else "stopped"
        print(f"{name:<15} {config['description']:<35} {config['port']:<10} {running:<10}")
    
    # Show instances if any
    launcher = ToolLauncher.get_instance()
    if launcher.tools:
        print("\nRunning Instances:")
        print("-" * 70)
        for instance_name, info in launcher.tools.items():
            tool_type = info['config']['display_name']
            pid = info['adapter'].process.pid if info['adapter'].process else 'N/A'
            print(f"  {instance_name:<20} ({tool_type}, PID: {pid})")


def show_status(tool_name=None):
    """Show status for a specific tool or all tools."""
    launcher = ToolLauncher.get_instance()
    registry = get_registry()
    
    if tool_name:
        # Check if it's an instance name first
        if tool_name in launcher.tools:
            # Show instance status
            info = launcher.tools[tool_name]
            status = info['adapter'].get_status()
            print(f"Instance: {tool_name}")
            print(f"Type: {info['config']['display_name']}")
            print(f"Status: {'Running' if status['running'] else 'Stopped'}")
            if status['running']:
                print(f"PID: {status['pid']}")
                print(f"Session: {status['session'] or 'default'}")
                print(f"Uptime: {status['uptime']:.1f} seconds")
                print(f"Messages sent: {status['metrics']['messages_sent']}")
                print(f"Messages received: {status['metrics']['messages_received']}")
                print(f"Errors: {status['metrics']['errors']}")
        else:
            # Show tool type status
            status = registry.get_tool_status(tool_name)
            if 'error' in status:
                print(f"Error: {status['error']}")
            else:
                print(f"Tool: {tool_name}")
                print(f"Configured: Yes")
                print(f"Port: {status['config']['port']}")
                print(f"Running: {'Yes' if status['running'] else 'No'}")
                if status['running']:
                    print(f"PID: {status['pid']}")
                    print(f"Uptime: {status['uptime']:.1f} seconds")
    else:
        # Show all status
        all_status = launcher.get_all_status()
        print("CI Tools Status:")
        print("-" * 50)
        
        # Show configured tools
        tools = registry.get_tools()
        for name in tools:
            status = registry.get_tool_status(name)
            running = "running" if status.get('running') else "stopped"
            print(f"{name:<15} {running}")
        
        # Show instances
        if launcher.tools:
            print("\nInstances:")
            for instance_name, info in launcher.tools.items():
                status = info['adapter'].get_status()
                print(f"  {instance_name:<20} ({'running' if status['running'] else 'stopped'})")


def launch_tool(tool_name, args):
    """Launch a CI tool."""
    launcher = ToolLauncher.get_instance()
    registry = get_registry()
    
    # Parse arguments
    session_id = None
    instance_name = None
    
    i = 0
    while i < len(args):
        if args[i] == '--session' and i + 1 < len(args):
            session_id = args[i + 1]
            i += 2
        elif args[i] == '--instance' and i + 1 < len(args):
            instance_name = args[i + 1]
            i += 2
        else:
            i += 1
    
    # Use instance name if provided, otherwise use tool name
    launch_name = instance_name or tool_name
    
    # Check if already running
    if launch_name in launcher.tools:
        print(f"{launch_name} is already running")
        return
    
    # Verify tool exists
    if tool_name not in registry.get_tools():
        print(f"Unknown tool: {tool_name}")
        return
    
    print(f"Launching {launch_name}...")
    if launcher.launch_tool(tool_name, session_id, instance_name):
        print(f"✓ {launch_name} launched successfully")
        
        # Show connection info
        tool_config = registry.get_tool(tool_name)
        print(f"  Port: {tool_config['port']}")
        print(f"  Session: {session_id or 'default'}")
        print(f"  Use: aish {launch_name} \"message\"")
    else:
        print(f"✗ Failed to launch {launch_name}")


def terminate_tool(name):
    """Terminate a tool or instance."""
    launcher = ToolLauncher.get_instance()
    
    if name in launcher.tools:
        print(f"Terminating {name}...")
        if launcher.terminate_tool(name):
            print(f"✓ {name} terminated")
        else:
            print(f"✗ Failed to terminate {name}")
    else:
        print(f"No running instance named '{name}'")
        
        # Show running instances
        if launcher.tools:
            print("\nRunning instances:")
            for instance_name in launcher.tools:
                print(f"  {instance_name}")


def show_capabilities(tool_name):
    """Show capabilities for a tool."""
    registry = get_registry()
    tool_config = registry.get_tool(tool_name)
    
    if not tool_config:
        print(f"Unknown tool: {tool_name}")
        return
    
    print(f"Capabilities for {tool_name}:")
    print("-" * 40)
    
    capabilities = tool_config.get('capabilities', {})
    if capabilities:
        for cap, enabled in capabilities.items():
            if enabled:
                print(f"  ✓ {cap.replace('_', ' ').title()}")
    else:
        print("  No capabilities defined")
    
    print(f"\nExecutable: {tool_config.get('executable', 'Not specified')}")
    print(f"Port: {tool_config['port']}")
    print(f"Health check: {tool_config.get('health_check', 'Not specified')}")


def create_instance(instance_name, args):
    """Create a new tool instance."""
    registry = get_registry()
    
    # Parse arguments
    tool_type = None
    i = 0
    while i < len(args):
        if args[i] == '--type' and i + 1 < len(args):
            tool_type = args[i + 1]
            i += 2
        else:
            i += 1
    
    if not tool_type:
        print("Error: --type <tool> is required")
        print("Example: aish tools create review-bot --type claude-code")
        return
    
    # Verify tool type exists
    if tool_type not in registry.get_tools():
        print(f"Unknown tool type: {tool_type}")
        print("Available tools:", ", ".join(registry.get_tools().keys()))
        return
    
    # Register the instance
    # For now, we'll use the same config but could customize later
    tool_config = registry.get_tool(tool_type).copy()
    tool_config['instance_name'] = instance_name
    tool_config['base_type'] = tool_type
    
    print(f"Created instance '{instance_name}' of type '{tool_type}'")
    print(f"Launch with: aish tools launch {tool_type} --instance {instance_name}")


def list_instances():
    """List all running tool instances."""
    launcher = ToolLauncher.get_instance()
    
    if not launcher.tools:
        print("No running tool instances")
        return
    
    print("Running Tool Instances:")
    print("-" * 80)
    print(f"{'Instance':<20} {'Type':<15} {'PID':<10} {'Session':<15} {'Uptime':<10}")
    print("-" * 80)
    
    for instance_name, info in launcher.tools.items():
        status = info['adapter'].get_status()
        tool_type = info['config'].get('base_type', info['adapter'].tool_name)
        pid = status.get('pid', 'N/A')
        session = status.get('session', 'default') or 'default'
        uptime = f"{status.get('uptime', 0):.0f}s" if status.get('uptime') else 'N/A'
        
        print(f"{instance_name:<20} {tool_type:<15} {str(pid):<10} {session:<15} {uptime:<10}")


def define_tool(tool_name, args):
    """Define a new CI tool."""
    registry = get_registry()
    
    # Parse arguments
    config = {
        'display_name': tool_name.replace('-', ' ').title(),
        'type': 'tool',
        'defined_by': 'user',
        'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }
    
    i = 0
    while i < len(args):
        if args[i] == '--type' and i + 1 < len(args):
            config['base_type'] = args[i + 1]
            i += 2
        elif args[i] == '--executable' and i + 1 < len(args):
            config['executable'] = args[i + 1]
            i += 2
        elif args[i] == '--description' and i + 1 < len(args):
            config['description'] = args[i + 1]
            i += 2
        elif args[i] == '--port' and i + 1 < len(args):
            # Handle 'auto' or numeric port
            port_value = args[i + 1]
            if port_value.lower() == 'auto':
                config['port'] = 'auto'
            else:
                try:
                    config['port'] = int(port_value)
                except ValueError:
                    print(f"Error: Invalid port value: {port_value}")
                    return
            i += 2
        elif args[i] == '--capabilities' and i + 1 < len(args):
            # Parse comma-separated capabilities
            caps = args[i + 1].split(',')
            config['capabilities'] = {cap.strip(): True for cap in caps}
            i += 2
        elif args[i] == '--launch-args' and i + 1 < len(args):
            # Parse launch arguments (space-separated or quoted)
            config['launch_args'] = args[i + 1].split()
            i += 2
        elif args[i] == '--health-check' and i + 1 < len(args):
            config['health_check'] = args[i + 1]
            i += 2
        elif args[i] == '--env' and i + 1 < len(args):
            # Parse key=value environment variables
            if 'environment' not in config:
                config['environment'] = {}
            env_pair = args[i + 1]
            if '=' in env_pair:
                key, value = env_pair.split('=', 1)
                config['environment'][key] = value
            else:
                print(f"Error: Invalid environment variable format: {env_pair}")
                print("Expected format: --env KEY=VALUE")
                return
            i += 2
        else:
            print(f"Warning: Unknown option: {args[i]}")
            i += 1
    
    # Validate required fields
    if 'executable' not in config:
        print("Error: --executable is required")
        print("Example: aish tools define my-tool --executable /usr/bin/mytool")
        return
    
    if 'description' not in config:
        config['description'] = f"User-defined {tool_name} tool"
    
    if 'port' not in config:
        # Default to auto for user-defined tools
        config['port'] = 'auto'
    
    if 'base_type' not in config:
        config['base_type'] = 'generic'
    
    # Allocate port if needed
    if config['port'] == 'auto':
        config['port'] = registry.find_available_port()
        print(f"Allocated port: {config['port']}")
    
    # Register the tool
    if registry.register_tool(tool_name, config):
        print(f"✓ Tool '{tool_name}' defined successfully")
        print(f"  Type: {config['base_type']}")
        print(f"  Executable: {config['executable']}")
        print(f"  Port: {config['port']}")
        if config.get('capabilities'):
            print(f"  Capabilities: {', '.join(config['capabilities'].keys())}")
        print(f"\nLaunch with: aish tools launch {tool_name}")
    else:
        print(f"✗ Failed to define tool '{tool_name}'")


def show_defined_tools(tool_name=None):
    """Show defined tools or details of a specific tool."""
    registry = get_registry()
    tools = registry.get_tools()
    
    # Filter for user-defined tools
    user_tools = {
        name: config for name, config in tools.items()
        if config.get('defined_by') == 'user'
    }
    
    if tool_name:
        # Show specific tool details
        if tool_name not in tools:
            print(f"Tool '{tool_name}' not found")
            return
        
        config = tools[tool_name]
        print(f"Tool: {tool_name}")
        print("-" * 40)
        print(f"Display Name: {config.get('display_name', tool_name)}")
        print(f"Description: {config.get('description', 'No description')}")
        print(f"Type: {config.get('base_type', 'N/A')}")
        print(f"Executable: {config.get('executable', 'N/A')}")
        print(f"Port: {config.get('port', 'N/A')}")
        
        if config.get('launch_args'):
            print(f"Launch Args: {' '.join(config['launch_args'])}")
        
        if config.get('capabilities'):
            print("Capabilities:")
            for cap, enabled in config['capabilities'].items():
                if enabled:
                    print(f"  - {cap}")
        
        if config.get('environment'):
            print("Environment:")
            for key, value in config['environment'].items():
                print(f"  {key}={value}")
        
        if config.get('health_check'):
            print(f"Health Check: {config['health_check']}")
        
        if config.get('defined_by') == 'user':
            print(f"Defined By: User")
            print(f"Created: {config.get('created_at', 'Unknown')}")
    else:
        # List all user-defined tools
        if not user_tools:
            print("No user-defined tools found")
            print("\nDefine a new tool with: aish tools define <name> [options]")
            return
        
        print("User-Defined Tools:")
        print("-" * 70)
        print(f"{'Name':<15} {'Type':<10} {'Port':<10} {'Description':<35}")
        print("-" * 70)
        
        for name, config in user_tools.items():
            base_type = config.get('base_type', 'generic')
            port = str(config.get('port', 'N/A'))
            desc = config.get('description', 'No description')[:35]
            print(f"{name:<15} {base_type:<10} {port:<10} {desc:<35}")
        
        print(f"\nTotal: {len(user_tools)} user-defined tools")
        print("\nFor details: aish tools defined <name>")


def undefine_tool(tool_name):
    """Remove a tool definition."""
    registry = get_registry()
    
    # Check if tool exists
    tool_config = registry.get_tool(tool_name)
    if not tool_config:
        print(f"Tool '{tool_name}' not found")
        return
    
    # Check if it's user-defined
    if tool_config.get('defined_by') != 'user':
        print(f"Cannot undefine built-in tool '{tool_name}'")
        print("Only user-defined tools can be undefined")
        return
    
    # Check if running
    launcher = ToolLauncher.get_instance()
    if tool_name in launcher.tools:
        print(f"Cannot undefine '{tool_name}' while it's running")
        print(f"First terminate with: aish tools terminate {tool_name}")
        return
    
    # Unregister the tool
    if registry.unregister_tool(tool_name):
        print(f"✓ Tool '{tool_name}' undefined successfully")
    else:
        print(f"✗ Failed to undefine tool '{tool_name}'")


# Import time at the top if not already imported
import time