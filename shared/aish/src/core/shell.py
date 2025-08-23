"""
AIShell - Simplified shell implementation using unified sender
"""

import os
import sys
import subprocess
import readline
import atexit
from pathlib import Path
from datetime import datetime

# Try to import landmarks if available
try:
    from landmarks import architecture_decision, integration_point, api_contract, state_checkpoint
except ImportError:
    # Landmarks not available, create no-op decorators
    def architecture_decision(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator
    
    def api_contract(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator

from parser.pipeline import PipelineParser
from core.history import AIHistory

# Add parent to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from shared.env import TektonEnviron
from shared.urls import tekton_url

class AIShell:
    """The AI Shell - orchestrates AI pipelines"""
    
    def __init__(self, rhetor_endpoint=None, debug=False, capture=False):
        self.capture = capture
        if rhetor_endpoint:
            self.rhetor_endpoint = rhetor_endpoint
        else:
            # Use tekton_url to build the endpoint properly
            self.rhetor_endpoint = tekton_url('rhetor', '')
        
        self.debug = debug
        self.parser = PipelineParser()
        tekton_root = TektonEnviron.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')
        self.history_file = Path(tekton_root) / '.tekton' / 'aish' / '.aish_history'
        self.ai_history = AIHistory()  # Conversation history tracker
        
        # Setup readline for interactive mode
        self._setup_readline()
    
    def _setup_readline(self):
        """Configure readline for better interactive experience"""
        # Load history
        if self.history_file.exists():
            readline.read_history_file(self.history_file)
        
        # Save history on exit
        def save_history():
            try:
                if self.history_file.exists():
                    readline.write_history_file(self.history_file)
            except:
                pass  # Ignore errors on exit
        atexit.register(save_history)
    
    def execute_command(self, command):
        """Execute a single AI pipeline command"""
        try:
            # Parse the command
            pipeline = self.parser.parse(command)
            
            if self.debug:
                print(f"[DEBUG] Parsed pipeline: {pipeline}")
            
            # Execute the pipeline and track responses
            result, responses = self._execute_pipeline_with_tracking(pipeline)
            
            # Add to history if we got responses
            if responses:
                self.ai_history.add_command(command, responses)
            
            # Output result
            if result:
                print(result)
                
        except Exception as e:
            print(f"aish: {e}", file=sys.stderr)
            return 1
        
        return 0
    
    def execute_script(self, script_path):
        """Execute an AI script file"""
        try:
            with open(script_path, 'r') as f:
                # Skip shebang if present
                lines = f.readlines()
                if lines and lines[0].startswith('#!'):
                    lines = lines[1:]
                
                # Execute each line
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.execute_command(line)
                        
        except FileNotFoundError:
            print(f"aish: {script_path}: No such file", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"aish: {script_path}: {e}", file=sys.stderr)
            return 1
        
        return 0
    
    def interactive(self):
        """Run interactive AI shell"""
        print("aish - The AI Shell v0.1.0")
        print(f"Connected to Rhetor at: {self.rhetor_endpoint}")
        print("Type 'help' for help, 'exit' to quit")
        print()
        
        while True:
            try:
                # Get command
                command = input("aish> ").strip()
                
                # Handle special commands
                if command == 'exit':
                    break
                elif command == 'help':
                    self._show_help()
                elif command == 'list-ais' or command == 'ais':
                    self._list_ais()
                elif command == 'list' or command == 'commands':
                    self._show_help()
                elif command == 'history':
                    self._show_history()
                elif command == '/restart' or command == 'restart':
                    self._restart_mcp_server()
                elif command == '/status' or command == 'status':
                    self._check_mcp_status()
                elif command == '/logs' or command == 'logs':
                    self._show_mcp_logs()
                elif command == '/debug-mcp' or command == 'debug-mcp':
                    self._toggle_mcp_debug()
                elif command.startswith('!'):
                    # Handle history expansion (!number)
                    if command[1:].isdigit():
                        cmd_num = int(command[1:])
                        replay_cmd = self.ai_history.replay(cmd_num)
                        if replay_cmd:
                            print(f"Replaying: {replay_cmd}")
                            self.execute_command(replay_cmd)
                        else:
                            print(f"!{cmd_num}: event not found")
                    else:
                        # Regular shell escape
                        subprocess.run(command[1:], shell=True)
                elif command:
                    self.execute_command(command)
                    
            except KeyboardInterrupt:
                print()  # New line after ^C
                continue
            except EOFError:
                print()  # New line after ^D
                break
    
    def _execute_pipeline_with_tracking(self, pipeline):
        """Execute a pipeline and track responses for history.
        
        Returns:
            Tuple of (result_string, responses_dict)
        """
        pipeline_type = pipeline.get('type')
        responses = {}
        
        if pipeline_type == 'team-chat':
            # Use the broadcast client for team chat
            from core.broadcast_client import broadcast_to_cis
            team_responses = broadcast_to_cis(pipeline['message'])
            
            # Format output
            result_lines = ["Team responses:", "-" * 40]
            for ai_name, content in team_responses.items():
                result_lines.append(f"[{ai_name}]: {content}")
                responses[ai_name] = content
            result_lines.append("-" * 40)
            
            return '\n'.join(result_lines), responses
            
        elif pipeline_type == 'pipeline':
            result, responses = self._execute_pipe_stages_with_tracking(pipeline['stages'])
            return result, responses
            
        elif pipeline_type == 'simple':
            result = self._execute_simple_command(pipeline['command'])
            return result, {}
            
        else:
            return f"Unsupported pipeline type: {pipeline_type}", {}
    
    def _execute_pipe_stages_with_tracking(self, stages):
        """Execute pipeline stages and track AI responses."""
        current_data = None
        responses = {}
        
        from core.unified_sender import send_to_ci
        import io
        from contextlib import redirect_stdout
        
        for stage in stages:
            if stage['type'] == 'echo':
                # Start of pipeline with echo
                current_data = stage['content']
            elif stage['type'] == 'ai':
                # Process through AI
                ai_name = stage['name']
                
                if current_data is not None:
                    # Capture the output from send_to_ci
                    output_buffer = io.StringIO()
                    with redirect_stdout(output_buffer):
                        success = send_to_ci(ai_name, current_data)
                    
                    if success:
                        response = output_buffer.getvalue().strip()
                        current_data = response
                        responses[ai_name] = response
                    else:
                        current_data = f"Failed to get response from {ai_name}"
                else:
                    return f"No input data for {ai_name}", responses
            else:
                # Other command types
                current_data = f"Unsupported stage type: {stage['type']}"
        
        result = current_data if current_data else "Pipeline completed"
        return result, responses
    
    def _execute_simple_command(self, command):
        """Execute a simple command"""
        return f"Simple command: {command}"
    
    def _show_help(self):
        """Display help information"""
        print("""
AI Shell Commands:
  echo "text" | ai_name    - Send text to an AI
  ai1 | ai2 | ai3         - Pipeline AIs together  
  team-chat "message"     - Broadcast to all AIs
  list-ais, ais           - List available AI specialists
  list, commands          - Show this help (all commands)
  history                 - Show recent conversation history
  !number                 - Replay command from history (e.g., !1716)
  !command                - Execute shell command
  help                    - Show this help
  exit                    - Exit aish

Examples:
  echo "analyze this" | apollo
  apollo | athena > output.txt
  team-chat "what should we optimize?"
  !1716                   - Replay command number 1716
  history                 - View recent AI conversations
  
History Management:
  aish-history            - View history (outside of shell)
  aish-history --json     - Export as JSON for processing
  aish-history --search   - Search history

MCP Server Management:
  /restart                - Restart the MCP server
  /status                 - Check MCP server status
  /logs                   - Show MCP server logs
  /debug-mcp              - Toggle MCP debug mode
        """)
    
    def _list_ais(self):
        """List available AI specialists using unified registry"""
        from registry.ci_registry import get_registry
        
        print("Available CIs (Companion Intelligences):")
        print("-" * 60)
        
        registry = get_registry()
        
        # Group by type
        by_type = {
            'greek': [],
            'terminal': [],
            'project': [],
            'tool': []
        }
        
        for ci in registry.get_all().values():
            ci_type = ci.get('type', 'unknown')
            if ci_type in by_type:
                by_type[ci_type].append(ci)
        
        # Show Greek Chorus
        if by_type['greek']:
            print("\nGreek Chorus AIs:")
            for ci in sorted(by_type['greek'], key=lambda x: x['name']):
                print(f"  {ci['name']:<15} - {ci.get('description', 'AI specialist')}")
        
        # Show Terminals
        if by_type['terminal']:
            print("\nActive Terminals:")
            for ci in sorted(by_type['terminal'], key=lambda x: x['name']):
                print(f"  {ci['name']:<15} - Terminal session")
        
        # Show Projects
        if by_type['project']:
            print("\nProject CIs:")
            for ci in sorted(by_type['project'], key=lambda x: x['name']):
                print(f"  {ci['name']:<15} - {ci.get('description', 'Project CI')}")
        
        # Show CI Tools
        if by_type['tool']:
            print("\nCI Tools:")
            for ci in sorted(by_type['tool'], key=lambda x: x['name']):
                status = "running" if ci.get('running', False) else "stopped"
                print(f"  {ci['name']:<15} - {ci.get('description', 'CI tool')} ({status})")
        
        print("\nUse any CI name in a command: aish <name> \"message\"")
    
    def _show_history(self):
        """Show recent conversation history."""
        entries = self.ai_history.get_history(20)  # Last 20 entries
        if entries:
            print("Recent conversation history:")
            print("-" * 60)
            for line in entries:
                print(line.rstrip())
            print("-" * 60)
            print("Use !<number> to replay a command (e.g., !1716)")
        else:
            print("No conversation history yet. Start chatting with AIs!")
    
    def _restart_mcp_server(self):
        """Restart the aish MCP server"""
        import subprocess
        import time
        
        print("Restarting aish MCP server...")
        
        try:
            # First, try to kill existing MCP server
            subprocess.run(['pkill', '-f', 'aish-mcp'], capture_output=True)
            time.sleep(0.5)  # Brief pause
            
            # Start new MCP server
            from pathlib import Path
            tekton_root = TektonEnviron.get('TEKTON_ROOT', str(Path.home() / 'projects/github/Coder-A'))
            mcp_script = Path(tekton_root) / 'shared' / 'aish' / 'aish-mcp'
            
            if mcp_script.exists():
                env = os.environ.copy()
                # Add all TektonEnviron variables to subprocess
                for key in ['TEKTON_ROOT', 'AISH_MCP_PORT', 'AISH_PORT', 'AISH_DEBUG_MCP']:
                    value = TektonEnviron.get(key)
                    if value:
                        env[key] = str(value)
                
                # Start MCP server
                process = subprocess.Popen(
                    [sys.executable, str(mcp_script)],
                    env=env,
                    stdout=subprocess.PIPE if TektonEnviron.get('AISH_DEBUG_MCP') else subprocess.DEVNULL,
                    stderr=subprocess.PIPE if TektonEnviron.get('AISH_DEBUG_MCP') else subprocess.DEVNULL,
                    start_new_session=True
                )
                
                # Give it a moment to start
                time.sleep(1)
                
                # Check if it's running
                if process.poll() is None:
                    print("✓ MCP server restarted successfully")
                    # Check health
                    self._check_mcp_status()
                else:
                    print("✗ MCP server failed to start")
                    if TektonEnviron.get('AISH_DEBUG_MCP'):
                        stdout, stderr = process.communicate()
                        if stderr:
                            print(f"Error: {stderr.decode()}")
            else:
                print(f"✗ MCP script not found: {mcp_script}")
                
        except Exception as e:
            print(f"✗ Error restarting MCP server: {e}")
    
    def _check_mcp_status(self):
        """Check MCP server status"""
        import requests
        
        try:
            port = int(TektonEnviron.get('AISH_MCP_PORT', '8118'))
            response = requests.get(f'http://localhost:{port}/api/mcp/v2/health', timeout=2)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ MCP server is {data.get('status', 'unknown')}")
                print(f"  Service: {data.get('service', 'unknown')}")
                print(f"  Version: {data.get('version', 'unknown')}")
                print(f"  Port: {port}")
                if data.get('capabilities'):
                    print(f"  Capabilities: {', '.join(data['capabilities'])}")
            else:
                print(f"✗ MCP server returned status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"✗ MCP server is not running (port {TektonEnviron.get('AISH_MCP_PORT', '8118')})")
        except Exception as e:
            print(f"✗ Error checking MCP status: {e}")
    
    def _show_mcp_logs(self, lines=20):
        """Show recent MCP server logs"""
        import subprocess
        
        # Look for the MCP process and its output
        try:
            # Try to find the process
            result = subprocess.run(['pgrep', '-f', 'aish-mcp'], capture_output=True, text=True)
            if result.stdout.strip():
                pid = result.stdout.strip().split('\n')[0]
                print(f"MCP server process: PID {pid}")
            else:
                print("MCP server is not running")
                return
                
            # For now, suggest using debug mode
            if not TektonEnviron.get('AISH_DEBUG_MCP'):
                print("\nTo see MCP logs, restart aish with debug mode:")
                print("  AISH_DEBUG_MCP=1 aish")
            else:
                print("\nMCP debug mode is enabled - check terminal output")
                
        except Exception as e:
            print(f"Error checking MCP logs: {e}")
    
    def _toggle_mcp_debug(self):
        """Toggle MCP debug mode"""
        current = TektonEnviron.get('AISH_DEBUG_MCP', '0')
        new_value = '0' if current == '1' else '1'
        
        # Set using TektonEnviron for consistency
        TektonEnviron.set('AISH_DEBUG_MCP', new_value)
        
        if new_value == '1':
            print("✓ MCP debug mode enabled")
            print("  Restart MCP server with /restart to see debug output")
        else:
            print("✓ MCP debug mode disabled")
            print("  Restart MCP server with /restart to hide debug output")
    
    def _capture_output(self, ai_name, message, response):
        """Capture command output to .tekton/aish/captures/"""
        try:
            # Create captures directory if it doesn't exist
            tekton_root = TektonEnviron.get('TEKTON_ROOT')
            if not tekton_root:
                print("[DEBUG] Warning: TEKTON_ROOT not set, cannot capture output")
                return
            captures_dir = Path(tekton_root) / '.tekton' / 'aish' / 'captures'
            captures_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate timestamp and filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{ai_name}.txt"
            filepath = captures_dir / filename
            
            # Write capture file
            with open(filepath, 'w') as f:
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"AI: {ai_name}\n")
                f.write(f"Message: {message}\n")
                f.write(f"{'='*60}\n")
                f.write(f"Response:\n{response}\n")
            
            # Create/update symlink to latest
            latest_link = captures_dir / 'last_output.txt'
            if latest_link.exists() or latest_link.is_symlink():
                latest_link.unlink()
            latest_link.symlink_to(filename)
            
            if self.debug:
                print(f"[DEBUG] Output captured to: {filepath}")
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Failed to capture output: {e}")


if __name__ == '__main__':
    # Test shell
    shell = AIShell(debug=True)
    shell.interactive()