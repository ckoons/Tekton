#!/usr/bin/env python3
"""
Terminal Launcher Service
Launches native terminal applications with aish-proxy as the shell.

Philosophy: Use native terminals, enhance with AI. Simple Unix approach - 
track terminals by PID, use signals for control.
"""

import os
import sys
import subprocess
import platform
import shutil
import json
import time
import signal
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

# Add landmarks to Python path if needed
try:
    from landmarks import (
        architecture_decision,
        integration_point,
        api_contract,
        state_checkpoint
    )
except ImportError:
    # Landmarks not available, define no-op decorators
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def api_contract(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator


@dataclass
class TerminalConfig:
    """Configuration for launching a terminal."""
    name: str = "aish Terminal"
    app: Optional[str] = None  # Auto-detect if None
    working_dir: Optional[str] = None
    env: Dict[str, str] = field(default_factory=dict)
    shell_args: List[str] = field(default_factory=list)
    purpose: Optional[str] = None  # AI context
    template: Optional[str] = None  # Template name


@dataclass
class TerminalInfo:
    """Information about a launched terminal."""
    pid: int
    config: TerminalConfig
    launched_at: datetime
    status: str = "running"
    platform: str = ""
    terminal_app: str = ""


@architecture_decision(
    title="Native Terminal Integration with aish",
    rationale="Use native terminal apps (Terminal.app, iTerm, etc.) enhanced with aish-proxy for AI capabilities",
    alternatives_considered=["Custom terminal emulator", "Web-based terminal", "PTY manipulation"],
    impacts=["platform_compatibility", "user_experience", "maintenance"],
    decision_date="2025-07-02"
)
class TerminalLauncher:
    """
    Launches and manages native terminal applications with aish enhancement.
    
    Follows Engram's pattern for platform detection and capability discovery.
    Simple PID-based tracking like Unix process management.
    """
    
    def __init__(self, aish_path: Optional[str] = None):
        self.platform = platform.system().lower()
        try:
            self.aish_path = aish_path or self._find_aish_proxy()
            print(f"Found aish-proxy at: {self.aish_path}")
        except FileNotFoundError:
            print("aish-proxy not found. Terminal launching will use basic shells.")
            self.aish_path = None
        self.terminals: Dict[int, TerminalInfo] = {}
        
        # Platform-specific terminal detection
        self.available_terminals = self._detect_terminals()
        
        if not self.available_terminals:
            raise RuntimeError(f"No supported terminal applications found on {self.platform}")
    
    @integration_point(
        title="aish-proxy Path Resolution",
        target_component="aish",
        protocol="File system lookup",
        data_flow="Terma finds aish-proxy executable at Tekton/shared/aish",
        integration_date="2025-07-02"
    )
    def _find_aish_proxy(self) -> str:
        """Find the aish-proxy executable."""
        # Check common locations - Tekton/shared/aish first
        locations = [
            # Check Tekton/shared/aish first (new standard location)
            Path(__file__).parent.parent.parent.parent / "shared" / "aish" / "aish-proxy",
            # Other possible locations
            Path(__file__).parent.parent.parent / "aish-proxy",
            Path.home() / "utils" / "aish-proxy",
            Path("/usr/local/bin/aish-proxy"),
            # Check system PATH last (might point to old location)
            shutil.which("aish-proxy"),
            # Legacy location - commented out to prevent confusion
            # Path.home() / "projects" / "github" / "aish" / "aish-proxy",
        ]
        
        for loc in locations:
            if loc and Path(loc).exists():
                return str(Path(loc).absolute())
        
        raise FileNotFoundError("aish-proxy not found. Please specify path.")
    
    def _detect_terminals(self) -> List[Tuple[str, str]]:
        """
        Detect available terminal applications.
        
        Returns list of (app_id, display_name) tuples.
        Follows Engram's hardware detection pattern.
        """
        terminals = []
        
        if self.platform == "darwin":  # macOS
            # Check for macOS terminals in multiple locations
            macos_terminals = [
                # System locations
                ("/System/Applications/Utilities/Terminal.app", "Terminal.app", "native"),
                # User Applications
                ("/Applications/Terminal.app", "Terminal.app", "native"),
                ("/Applications/iTerm.app", "iTerm.app", "advanced"),
                ("/Applications/Warp.app", "Warp.app", "modern"),
                ("/Applications/WarpPreview.app", "WarpPreview.app", "modern preview"),
                ("/Applications/Alacritty.app", "Alacritty.app", "fast"),
                # Homebrew installations
                ("/Applications/kitty.app", "kitty.app", "GPU accelerated"),
                # Claude Code would be detected differently
            ]
            
            for path, name, category in macos_terminals:
                if os.path.exists(path):
                    terminals.append((name, f"{name} ({category})"))
            
            # Also check if we have AppleScript (required for Terminal.app)
            if not shutil.which("osascript"):
                terminals = [(t[0], t[1]) for t in terminals if t[0] != "Terminal.app"]
                
        elif self.platform == "linux":
            # Check for Linux terminals using 'which'
            linux_terminals = [
                ("gnome-terminal", "GNOME Terminal"),
                ("konsole", "Konsole (KDE)"),
                ("xterm", "XTerm (fallback)"),
                ("alacritty", "Alacritty"),
                ("terminator", "Terminator"),
                ("tilix", "Tilix"),
            ]
            
            for cmd, name in linux_terminals:
                if shutil.which(cmd):
                    terminals.append((cmd, name))
        
        return terminals
    
    def get_default_terminal(self) -> str:
        """Get the default terminal for the platform."""
        if not self.available_terminals:
            raise RuntimeError("No terminals available")
        
        # Platform-specific preferences
        if self.platform == "darwin":
            # Prefer native Terminal.app first (as requested)
            preferred = ["Terminal.app", "iTerm.app", "WarpPreview.app", "Warp.app"]
            for pref in preferred:
                if any(t[0] == pref for t in self.available_terminals):
                    return pref
        
        elif self.platform == "linux":
            # Prefer in order: gnome-terminal, konsole, xterm
            preferred = ["gnome-terminal", "konsole", "alacritty", "xterm"]
            for pref in preferred:
                if any(t[0] == pref for t in self.available_terminals):
                    return pref
        
        # Return first available
        return self.available_terminals[0][0]
    
    @api_contract(
        title="Terminal Launch API",
        endpoint="launch_terminal",
        method="CALL",
        request_schema={"config": "TerminalConfig"},
        response_schema={"pid": "int"},
        description="Launches aish-enabled terminal in user's home directory with their shell"
    )
    def launch_terminal(self, config: Optional[TerminalConfig] = None) -> int:
        """
        Launch a native terminal with aish-proxy.
        
        Returns the PID of the launched terminal process.
        """
        if config is None:
            config = TerminalConfig()
        
        # Auto-detect terminal if not specified
        if not config.app:
            config.app = self.get_default_terminal()
        
        # Set working directory to user's home directory
        if not config.working_dir:
            config.working_dir = os.path.expanduser("~")
        
        # Launch based on platform
        if self.platform == "darwin":
            pid = self._launch_macos_terminal(config)
        elif self.platform == "linux":
            pid = self._launch_linux_terminal(config)
        else:
            raise NotImplementedError(f"Platform {self.platform} not supported")
        
        # Track the terminal
        self.terminals[pid] = TerminalInfo(
            pid=pid,
            config=config,
            launched_at=datetime.now(),
            platform=self.platform,
            terminal_app=config.app
        )
        
        return pid
    
    def _launch_macos_terminal(self, config: TerminalConfig) -> int:
        """Launch terminal on macOS."""
        env_exports = " ".join([f"export {k}='{v}';" for k, v in config.env.items()])
        
        # Add Tekton context if purpose specified
        if config.purpose:
            env_exports += f" export TEKTON_TERMINAL_PURPOSE='{config.purpose}';"
        
        # Build shell command
        if self.aish_path:
            shell_cmd = f"cd '{config.working_dir}'; {env_exports} '{self.aish_path}'"
        else:
            # Fall back to user's shell when aish-proxy not available
            shell_to_use = os.environ.get('SHELL', '/bin/bash')
            shell_cmd = f"cd '{config.working_dir}'; {env_exports} {shell_to_use}"
        
        if config.shell_args:
            shell_cmd += " " + " ".join(config.shell_args)
        
        if config.app == "Terminal.app":
            # Use AppleScript for Terminal.app
            script = f'''
            tell application "Terminal"
                activate
                set newWindow to do script "{shell_cmd}"
                set windowID to id of window 1
                return windowID
            end tell
            '''
            
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True
            )
            
            # Get the Terminal process PID (approximate)
            # In reality, we'd need more sophisticated PID tracking
            time.sleep(0.5)  # Let Terminal start
            ps_result = subprocess.run(
                ["pgrep", "-n", "Terminal"],
                capture_output=True,
                text=True
            )
            return int(ps_result.stdout.strip()) if ps_result.stdout else 0
            
        elif config.app == "iTerm.app":
            # iTerm2 AppleScript
            script = f'''
            tell application "iTerm"
                activate
                create window with default profile
                tell current session of current window
                    write text "{shell_cmd}"
                end tell
                return id of current window
            end tell
            '''
            
            subprocess.run(["osascript", "-e", script])
            
            # Get iTerm PID
            time.sleep(0.5)
            ps_result = subprocess.run(
                ["pgrep", "-n", "iTerm"],
                capture_output=True,
                text=True
            )
            return int(ps_result.stdout.strip()) if ps_result.stdout else 0
            
        elif config.app in ["Warp.app", "WarpPreview.app"]:
            # Warp uses command line interface
            app_name = "WarpPreview" if config.app == "WarpPreview.app" else "Warp"
            cmd = [
                "open", "-a", app_name, "-n",
                "--args", "--new-window",
                "--working-directory", config.working_dir
            ]
            
            # Warp doesn't support direct command execution on launch
            # We'll need to configure it to use aish-proxy as default shell
            process = subprocess.Popen(cmd)
            return process.pid
            
        else:
            # Generic open command
            process = subprocess.Popen(["open", "-a", config.app])
            return process.pid
    
    def _launch_linux_terminal(self, config: TerminalConfig) -> int:
        """Launch terminal on Linux."""
        env_exports = " ".join([f"export {k}='{v}';" for k, v in config.env.items()])
        
        if config.purpose:
            env_exports += f" export TEKTON_TERMINAL_PURPOSE='{config.purpose}';"
        
        shell_cmd = f"cd '{config.working_dir}'; {env_exports} '{self.aish_path}'"
        if config.shell_args:
            shell_cmd += " " + " ".join(config.shell_args)
        
        if config.app == "gnome-terminal":
            cmd = [
                "gnome-terminal",
                "--",
                "bash", "-c",
                f"{shell_cmd}; exec bash"
            ]
        elif config.app == "konsole":
            cmd = [
                "konsole",
                "-e", "bash", "-c",
                shell_cmd
            ]
        elif config.app == "xterm":
            cmd = [
                "xterm",
                "-e", shell_cmd
            ]
        elif config.app == "alacritty":
            cmd = [
                "alacritty",
                "-e", "bash", "-c",
                shell_cmd
            ]
        else:
            # Generic terminal
            cmd = [config.app, "-e", shell_cmd]
        
        process = subprocess.Popen(cmd)
        return process.pid
    
    def is_terminal_running(self, pid: int) -> bool:
        """Check if a terminal process is still running."""
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False
    
    def show_terminal(self, pid: int) -> bool:
        """Bring terminal to foreground (macOS only for now)."""
        if self.platform != "darwin":
            return False
        
        terminal_info = self.terminals.get(pid)
        if not terminal_info:
            return False
        
        # Use AppleScript to activate window by PID
        script = f'''
        tell application "System Events"
            set frontProcess to first process whose unix id is {pid}
            set frontmost of frontProcess to true
        end tell
        '''
        
        try:
            subprocess.run(["osascript", "-e", script], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def terminate_terminal(self, pid: int) -> bool:
        """Terminate a terminal process."""
        try:
            os.kill(pid, signal.SIGTERM)
            if pid in self.terminals:
                self.terminals[pid].status = "terminated"
            return True
        except ProcessLookupError:
            if pid in self.terminals:
                self.terminals[pid].status = "not_found"
            return False
    
    def list_terminals(self) -> List[TerminalInfo]:
        """List all tracked terminals and update their status."""
        for pid, info in self.terminals.items():
            if info.status == "running":
                if not self.is_terminal_running(pid):
                    info.status = "stopped"
        
        return list(self.terminals.values())
    
    def cleanup_stopped(self):
        """Remove stopped terminals from tracking."""
        stopped_pids = [
            pid for pid, info in self.terminals.items()
            if info.status in ("stopped", "terminated", "not_found")
        ]
        for pid in stopped_pids:
            del self.terminals[pid]


class TerminalTemplates:
    """Pre-configured terminal templates."""
    
    DEFAULT_TEMPLATES = {
        "default": TerminalConfig(
            name="Default aish Terminal",
            env={"TEKTON_ENABLED": "true"}
        ),
        
        "development": TerminalConfig(
            name="Development Terminal",
            working_dir=os.path.expandvars("$TEKTON_ROOT"),
            env={
                "TEKTON_MODE": "development",
                "NODE_ENV": "development"
            }
        ),
        
        "ai_workspace": TerminalConfig(
            name="AI Workspace",
            purpose="AI-assisted development with full Tekton integration",
            env={
                "TEKTON_AI_WORKSPACE": "true",
                "AISH_AI_PRIORITY": "high"
            }
        ),
        
        "data_science": TerminalConfig(
            name="Data Science Terminal",
            env={
                "JUPYTER_ENABLE": "true",
                "PYTHONPATH": "$PYTHONPATH:$TEKTON_ROOT"
            }
        )
    }
    
    @classmethod
    def get_template(cls, name: str) -> Optional[TerminalConfig]:
        """Get a terminal configuration template."""
        template = cls.DEFAULT_TEMPLATES.get(name)
        if template:
            # Return a copy to avoid modifying the template
            import copy
            return copy.deepcopy(template)
        return None


def main():
    """CLI for terminal launcher."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Launch native terminals with aish enhancement",
        epilog="""
Commands:
  list               List available terminal types (default if no command given)
  list-terminals     List active/running terminals  
  launch             Launch a new terminal
  show               Bring terminal to foreground (requires --pid)
  terminate          Close a terminal (requires --pid)

Examples:
  aish-terminal                    # List available terminal types
  aish-terminal list               # List available terminal types
  aish-terminal list-terminals     # Show active terminals
  aish-terminal launch             # Launch default terminal
  aish-terminal launch --template development
  aish-terminal show --pid 12345
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "command",
        nargs='?',
        default="list",
        choices=["launch", "list", "list-terminals", "show", "terminate"],
        help="Command to execute (default: list)"
    )
    
    parser.add_argument(
        "--app", "-a",
        help="Terminal application to use"
    )
    
    parser.add_argument(
        "--dir", "-d",
        help="Working directory"
    )
    
    parser.add_argument(
        "--template", "-t",
        help="Use a configuration template"
    )
    
    parser.add_argument(
        "--purpose", "-p",
        help="Purpose/context for AI assistance"
    )
    
    parser.add_argument(
        "--pid",
        type=int,
        help="Process ID for show/terminate commands"
    )
    
    args = parser.parse_args()
    
    try:
        launcher = TerminalLauncher()
        
        if args.command == "list":
            # Show available terminal types
            print(f"Available terminal types on {launcher.platform}:")
            for app_id, display_name in launcher.available_terminals:
                default = " (default)" if app_id == launcher.get_default_terminal() else ""
                print(f"  {app_id:<20} - {display_name}{default}")
            
            # Also show active terminals
            print("\nActive terminals:")
            terminals = launcher.list_terminals()
            if not terminals:
                print("  No tracked terminals")
            else:
                for info in terminals:
                    print(f"  PID {info.pid}: {info.terminal_app} - {info.status}")
                    if info.config.purpose:
                        print(f"    Purpose: {info.config.purpose}")
                
        elif args.command == "list-terminals":
            # List only active terminals (detailed view)
            terminals = launcher.list_terminals()
            if not terminals:
                print("No tracked terminals")
            else:
                print("Active terminals:")
                for info in terminals:
                    print(f"  PID: {info.pid}")
                    print(f"    App: {info.terminal_app}")
                    print(f"    Status: {info.status}")
                    print(f"    Launched: {info.launched_at}")
                    if info.config.purpose:
                        print(f"    Purpose: {info.config.purpose}")
                    print()
                
        elif args.command == "launch":
            # Create config
            config = TerminalConfig()
            
            if args.template:
                template = TerminalTemplates.get_template(args.template)
                if template:
                    config = template
                else:
                    print(f"Template '{args.template}' not found")
                    return 1
            
            if args.app:
                config.app = args.app
            if args.dir:
                config.working_dir = args.dir
            if args.purpose:
                config.purpose = args.purpose
            
            # Launch terminal
            pid = launcher.launch_terminal(config)
            print(f"Launched terminal with PID: {pid}")
            print(f"Terminal app: {config.app or launcher.get_default_terminal()}")
            
        elif args.command == "show":
            if not args.pid:
                print("Error: --pid required for show command")
                return 1
            
            if launcher.show_terminal(args.pid):
                print(f"Brought terminal {args.pid} to foreground")
            else:
                print(f"Failed to show terminal {args.pid}")
                
        elif args.command == "terminate":
            if not args.pid:
                print("Error: --pid required for terminate command")
                return 1
            
            if launcher.terminate_terminal(args.pid):
                print(f"Terminated terminal {args.pid}")
            else:
                print(f"Failed to terminate terminal {args.pid}")
                
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())