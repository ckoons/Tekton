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
import threading
import uuid
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

# Import simple mailbox cleanup function
from simple_mailbox import remove_terminal as remove_terminal_mailbox

# Add parent to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from shared.env import TektonEnviron
from shared.urls import tekton_url

# Add landmarks to Python path if needed
try:
    from landmarks import (
        architecture_decision,
        integration_point,
        api_contract,
        state_checkpoint,
        danger_zone,
        performance_boundary
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
    
    def danger_zone(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def performance_boundary(**kwargs):
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
    purpose: Optional[str] = None  # CI context
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
    terma_id: Optional[str] = None
    last_heartbeat: Optional[datetime] = None


@state_checkpoint(
    title="Active Terminal Roster",
    state_type="runtime",
    persistence=False,
    consistency_requirements="Thread-safe roster tracking terminal health via heartbeats",
    recovery_strategy="Rebuild from aish heartbeats after restart"
)
class ActiveTerminalRoster:
    """Thread-safe roster of active terminals with heartbeat tracking."""
    
    def __init__(self):
        self._terminals: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self.heartbeat_timeout = timedelta(seconds=90)  # 3 missed heartbeats
        self.degraded_timeout = timedelta(seconds=180)  # Remove after 6 missed
        
        # Start health check thread
        self._running = True
        self._health_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self._health_thread.start()
    
    def update_heartbeat(self, terma_id: str, heartbeat_data: Dict[str, Any]):
        """Update heartbeat for a terminal."""
        import logging
        logger = logging.getLogger("terma.roster")
        
        with self._lock:
            # Check if terminal is explicitly terminated
            if heartbeat_data.get("status") == "terminated":
                # Remove terminal immediately
                if terma_id in self._terminals:
                    terminal_name = self._terminals[terma_id].get("name", "")
                    del self._terminals[terma_id]
                    logger.info(f"Terminal {terma_id} terminated, removed from roster")
                    # Clean up mailboxes
                    if terminal_name:
                        remove_terminal_mailbox(terminal_name)
                    # Clean up inbox snapshot
                    self._cleanup_terminal_inbox(terma_id)
                return
            
            if terma_id not in self._terminals:
                # New terminal registering
                logger.info(f"New terminal {terma_id} registering via heartbeat")
                self._terminals[terma_id] = {}
            
            self._terminals[terma_id].update({
                **heartbeat_data,
                "last_heartbeat": datetime.now(),
                "status": "active"
            })
            logger.debug(f"Updated heartbeat for terminal {terma_id}, total terminals: {len(self._terminals)}")
            # No storage sync - heartbeats control the roster
    
    def pre_register(self, terma_id: str, pid: int, config: TerminalConfig):
        """Pre-register a terminal before first heartbeat."""
        import logging
        logger = logging.getLogger("terma.roster")
        
        with self._lock:
            self._terminals[terma_id] = {
                "terma_id": terma_id,
                "pid": pid,
                "name": config.name,
                "working_dir": config.working_dir or os.path.expanduser("~"),
                "terminal_app": config.app,
                "purpose": config.purpose,
                "template": getattr(config, 'template', None),  # Safe access to template
                "launched_at": datetime.now().isoformat(),
                "last_heartbeat": datetime.now(),
                "status": "launching"
            }
            logger.info(f"Pre-registered terminal {terma_id} with PID {pid}, total terminals: {len(self._terminals)}")
    
    def get_terminals(self) -> List[Dict[str, Any]]:
        """Get list of all terminals with current status."""
        with self._lock:
            return list(self._terminals.values())
    
    def get_terminal(self, terma_id: str) -> Optional[Dict[str, Any]]:
        """Get info for a specific terminal."""
        with self._lock:
            return self._terminals.get(terma_id)
    
    def remove_terminal(self, terma_id: str):
        """Remove a terminal from the roster."""
        with self._lock:
            if terma_id in self._terminals:
                terminal_name = self._terminals[terma_id].get("name", "")
                del self._terminals[terma_id]
                # Clean up mailboxes
                if terminal_name:
                    remove_terminal_mailbox(terminal_name)
                # Clean up inbox snapshot
                self._cleanup_terminal_inbox(terma_id)
    
    @performance_boundary(
        title="Terminal Health Check Loop",
        sla="<100ms per check cycle",
        optimization_notes="Check every 10 seconds, process all terminals in single pass",
        metrics={"check_interval": "10s", "max_terminals": "1000"}
    )
    def _health_check_loop(self):
        """Periodically check terminal health."""
        while self._running:
            try:
                self._check_health()
            except Exception:
                pass  # Don't crash health checker
            time.sleep(10)  # Check every 10 seconds
    
    def _check_health(self):
        """Check health of all terminals."""
        now = datetime.now()
        to_remove = []
        
        with self._lock:
            for terma_id, info in self._terminals.items():
                last_heartbeat = info.get("last_heartbeat")
                if isinstance(last_heartbeat, str):
                    last_heartbeat = datetime.fromisoformat(last_heartbeat)
                elif not last_heartbeat:
                    last_heartbeat = now
                
                time_since = now - last_heartbeat
                
                if time_since > self.degraded_timeout:
                    # No heartbeat for 3 minutes - remove
                    to_remove.append(terma_id)
                elif time_since > self.heartbeat_timeout:
                    # No heartbeat for 90 seconds - mark degraded
                    info["status"] = "degraded"
                elif info["status"] == "degraded":
                    # Got heartbeat, mark active again
                    info["status"] = "active"
        
        # Remove outside lock to avoid deadlock
        for terma_id in to_remove:
            self.remove_terminal(terma_id)
    
    
    
    def _cleanup_terminal_inbox(self, terma_id: str):
        """Clean up inbox data for a terminated terminal."""
        try:
            tekton_root = TektonEnviron.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')
            
            # Clean up shared inbox snapshot if it belongs to this terminal
            snapshot_file = os.path.join(tekton_root, ".tekton", "terma", ".inbox_snapshot")
            if os.path.exists(snapshot_file):
                try:
                    with open(snapshot_file, 'r') as f:
                        data = json.load(f)
                    # Check if this snapshot belongs to the terminated terminal
                    if data.get('session_id', '').startswith(terma_id[:8]):
                        os.remove(snapshot_file)
                        import logging
                        logger = logging.getLogger("terma.roster")
                        logger.info(f"Cleaned up inbox snapshot for terminal {terma_id[:8]}")
                except Exception:
                    # Best effort - file might be locked or corrupted
                    pass
            
            # Clean up any command files from this terminal
            cmd_dir = os.path.join(tekton_root, ".tekton", "terma", "commands")
            if os.path.exists(cmd_dir):
                for cmd_file in os.listdir(cmd_dir):
                    if terma_id[:8] in cmd_file:
                        try:
                            os.remove(os.path.join(cmd_dir, cmd_file))
                        except:
                            pass
                            
        except Exception as e:
            # Don't let cleanup errors affect terminal removal
            import logging
            logger = logging.getLogger("terma.roster")
            logger.warning(f"Failed to clean up inbox for terminal {terma_id}: {e}")
    
    def stop(self):
        """Stop the health check thread."""
        self._running = False


# Global roster instance
_terminal_roster = None

def get_terminal_roster() -> ActiveTerminalRoster:
    """Get the global terminal roster instance."""
    global _terminal_roster
    if _terminal_roster is None:
        _terminal_roster = ActiveTerminalRoster()
    return _terminal_roster


@architecture_decision(
    title="Native Terminal Integration with aish",
    rationale="Use native terminal apps (Terminal.app, iTerm, etc.) enhanced with aish-proxy for CI capabilities",
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
        
        # Setup logging
        import logging
        self.logger = logging.getLogger("terma.launcher")
        self.logger.info(f"Initializing TerminalLauncher on {self.platform}")
        
        try:
            self.aish_path = aish_path or self._find_aish_proxy()
            self.logger.info(f"Found aish-proxy at: {self.aish_path}")
        except FileNotFoundError:
            self.logger.warning("aish-proxy not found. Terminal launching will use basic shells.")
            self.aish_path = None
        self.terminals: Dict[int, TerminalInfo] = {}
        
        # Get the active terminal roster
        self.roster = get_terminal_roster()
        
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
        response_schema={"pid": "int"}
    )
    @danger_zone(
        title="Native Terminal Launch",
        risk_level="low",
        risks=["Resource consumption", "Process tracking issues", "Terminal app compatibility"],
        mitigations=["PID tracking", "Heartbeat monitoring", "Platform-specific handling"],
        review_required=False
    )
    def launch_terminal(self, config: Optional[TerminalConfig] = None) -> int:
        """
        Launch a native terminal with aish-proxy.
        
        Returns the PID of the launched terminal process.
        """
        self.logger.info("=" * 60)
        self.logger.info("TERMINAL LAUNCH INITIATED")
        self.logger.info("=" * 60)
        
        if config is None:
            config = TerminalConfig()
            self.logger.info("Using default TerminalConfig")
        
        # Generate unique Terma session ID
        terma_id = str(uuid.uuid4())[:8]
        self.logger.info(f"Generated Terma session ID: {terma_id}")
        
        # Add Terma environment variables
        config.env["TERMA_SESSION_ID"] = terma_id
        # Use tekton_url to get the correct endpoint for this environment
        config.env["TERMA_ENDPOINT"] = tekton_url('terma', '')
        config.env["TERMA_TERMINAL_NAME"] = config.name
        # Debug: Log the session ID we're using
        self.logger.info(f"DEBUG: Setting TERMA_SESSION_ID={terma_id}")
        self.logger.info(f"DEBUG: Setting TERMA_TERMINAL_NAME={config.name}")
        self.logger.info(f"Terminal name: {config.name}")
        self.logger.info(f"Terminal endpoint: {config.env['TERMA_ENDPOINT']}")
        
        # Always include TEKTON_ROOT and TEKTON_CI_TRAINING
        config.env["TEKTON_ROOT"] = TektonEnviron.get("TEKTON_ROOT", "/Users/cskoons/projects/github/Tekton")
        config.env["TEKTON_CI_TRAINING"] = os.path.join(config.env["TEKTON_ROOT"], "MetaData/TektonDocumentation/CITraining")
        self.logger.info(f"TEKTON_ROOT: {config.env['TEKTON_ROOT']}")
        
        # Auto-detect terminal if not specified
        if not config.app:
            config.app = self.get_default_terminal()
            self.logger.info(f"Auto-detected terminal app: {config.app}")
        else:
            self.logger.info(f"Using specified terminal app: {config.app}")
        
        # Expand and set working directory
        if config.working_dir:
            # Expand environment variables and ~ in the path
            config.working_dir = os.path.expandvars(os.path.expanduser(config.working_dir))
            self.logger.info(f"Working directory expanded to: {config.working_dir}")
        else:
            config.working_dir = os.path.expanduser("~")
            self.logger.info(f"Using default working directory: {config.working_dir}")
        
        # Log all environment variables
        self.logger.info("Environment variables for terminal:")
        for key, value in config.env.items():
            self.logger.info(f"  {key}={value}")
        
        # Launch based on platform
        self.logger.info(f"Launching terminal on platform: {self.platform}")
        if self.platform == "darwin":
            pid = self._launch_macos_terminal(config)
        elif self.platform == "linux":
            pid = self._launch_linux_terminal(config)
        else:
            raise NotImplementedError(f"Platform {self.platform} not supported")
        
        self.logger.info(f"Terminal launched with PID: {pid}")
        
        # Track the terminal locally
        self.terminals[pid] = TerminalInfo(
            pid=pid,
            config=config,
            launched_at=datetime.now(),
            platform=self.platform,
            terminal_app=config.app,
            terma_id=terma_id
        )
        self.logger.info(f"Terminal tracked locally with PID {pid}")
        
        # Pre-register in the active roster
        self.roster.pre_register(terma_id, pid, config)
        self.logger.info(f"Terminal pre-registered in roster with ID {terma_id}")
        
        self.logger.info("=" * 60)
        self.logger.info("TERMINAL LAUNCH COMPLETED")
        self.logger.info(f"Session ID: {terma_id}, PID: {pid}, App: {config.app}")
        self.logger.info("=" * 60)
        
        return pid
    
    @integration_point(
        title="macOS Terminal Application Launch",
        target_component="Terminal.app, iTerm2, Warp via AppleScript/open",
        protocol="AppleScript for Terminal.app, open command for others",
        data_flow="Terma -> AppleScript/open -> Terminal App -> aish-proxy shell"
    )
    def _launch_macos_terminal(self, config: TerminalConfig) -> int:
        """Launch terminal on macOS."""
        self.logger.info("-" * 40)
        self.logger.info("macOS TERMINAL LAUNCH")
        self.logger.info("-" * 40)
        self.logger.info(f"Terminal app: {config.app}")
        self.logger.info(f"Terminal name: {config.name}")
        self.logger.info(f"Working dir: {config.working_dir}")
        self.logger.info(f"Session ID: {config.env.get('TERMA_SESSION_ID', 'unknown')}")
        self.logger.info(f"Purpose: {config.purpose or 'Not specified'}")
        self.logger.info(f"Template: {getattr(config, 'template', 'None')}")
        
        env_exports = " ".join([f"export {k}='{v}';" for k, v in config.env.items()])
        
        # Add Tekton context if purpose specified
        if config.purpose:
            env_exports += f" export TEKTON_TERMINAL_PURPOSE='{config.purpose}';"
        
        # Build shell command - just export vars and run aish-proxy
        # Let aish-proxy handle the cd and startup command after shell init
        if self.aish_path:
            # Pass working dir and startup cmd as environment variables
            if config.working_dir and config.working_dir != os.path.expanduser("~"):
                env_exports += f" export TERMA_WORKING_DIR='{config.working_dir}';"
            shell_cmd = f"{env_exports} '{self.aish_path}'"
        else:
            # Fall back to user's shell when aish-proxy not available
            shell_to_use = TektonEnviron.get('SHELL', '/bin/bash')
            shell_cmd = f"cd '{config.working_dir}'; {env_exports} {shell_to_use}"
        
        if config.shell_args:
            shell_cmd += " " + " ".join(config.shell_args)
        
        if config.app == "Terminal.app":
            # Use AppleScript for Terminal.app - simple version
            self.logger.info("Using Terminal.app - simple AppleScript approach")
            script = f'''
            tell application "Terminal"
                do script "{shell_cmd}"
                activate
                set windowID to id of window 1
                return windowID
            end tell
            '''
            
            self.logger.info("Executing AppleScript...")
            self.logger.info(f"Full shell command: {shell_cmd}")
            self.logger.debug(f"Shell command length: {len(shell_cmd)} chars")
            
            # Log AppleScript (abbreviated)
            script_lines = script.strip().split('\n')
            self.logger.debug(f"AppleScript has {len(script_lines)} lines")
            
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True
            )
            
            self.logger.info(f"AppleScript execution completed")
            self.logger.info(f"Return code: {result.returncode}")
            self.logger.info(f"AppleScript stdout: {result.stdout}")
            if result.stderr:
                self.logger.warning(f"AppleScript stderr: {result.stderr}")
            
            if result.returncode != 0:
                self.logger.error(f"AppleScript failed with code: {result.returncode}")
                self.logger.error("Failed AppleScript:")
                for i, line in enumerate(script_lines[:10]):  # First 10 lines
                    self.logger.error(f"  {i+1}: {line}")
            
            # For now, return a synthetic PID based on the roster pre-registration
            # The real PID will be updated when the first heartbeat arrives
            # This avoids the timing issue with pgrep
            import random
            synthetic_pid = random.randint(10000, 99999)
            
            self.logger.info(f"Using synthetic PID {synthetic_pid} until first heartbeat")
            
            # Store session ID for termination
            if not hasattr(self, '_session_mapping'):
                self._session_mapping = {}
            self._session_mapping[synthetic_pid] = config.env['TERMA_SESSION_ID']
            
            return synthetic_pid
            
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
        
        # First, try to find session ID from pid
        session_id = None
        
        # Check if we have a session mapping
        if hasattr(self, '_session_mapping') and pid in self._session_mapping:
            session_id = self._session_mapping[pid]
        else:
            # Try to find from roster
            for term in self.roster.get_terminals():
                if term.get("pid") == pid:
                    session_id = term.get("terma_id")
                    break
        
        if not session_id:
            # Fall back to trying System Events with PID
            script = f'''
            tell application "System Events"
                try
                    set frontProcess to first process whose unix id is {pid}
                    set frontmost of frontProcess to true
                    return "success"
                on error
                    return "failed"
                end try
            end tell
            '''
        else:
            # Use session ID to find and activate Terminal window
            script = f'''
            tell application "Terminal"
                activate
                set windowList to every window
                repeat with aWindow in windowList
                    set tabList to every tab of aWindow
                    repeat with aTab in tabList
                        if (history of aTab as string) contains "{session_id}" then
                            set frontmost of aWindow to true
                            set selected of aTab to true
                            return "success"
                        end if
                    end repeat
                end repeat
                return "not found"
            end tell
            '''
        
        try:
            result = subprocess.run(["osascript", "-e", script], 
                                  capture_output=True, text=True)
            self.logger.info(f"Show terminal result: {result.stdout}")
            return result.returncode == 0 and "success" in result.stdout
        except subprocess.CalledProcessError:
            return False
    
    @danger_zone(
        title="Terminal Process Termination",
        risk_level="medium",
        risks=["Data loss if terminal has unsaved work", "Process cleanup issues", "Window close failures"],
        mitigations=["Graceful SIGTERM first", "3s timeout before SIGKILL", "AppleScript window cleanup"],
        review_required=False
    )
    def terminate_terminal(self, pid: int) -> bool:
        """Terminate a terminal process and close the window."""
        try:
            self.logger.info("=" * 60)
            self.logger.info("TERMINAL TERMINATION INITIATED")
            self.logger.info("=" * 60)
            self.logger.info(f"Target PID: {pid}")
            
            # First find the terminal and get the real PID
            session_id = None
            real_pid = None
            
            # Check if this is a synthetic PID
            if hasattr(self, '_session_mapping') and pid in self._session_mapping:
                session_id = self._session_mapping[pid]
                self.logger.info(f"Found session {session_id} for synthetic PID {pid}")
                
                # Get the real PID from the roster
                for term in self.roster.get_terminals():
                    if term.get("terma_id") == session_id:
                        real_pid = term.get("pid")
                        self.logger.info(f"Found real PID {real_pid} for session {session_id}")
                        break
            else:
                # This might be a real PID, search roster
                for term in self.roster.get_terminals():
                    if term.get("pid") == pid:
                        session_id = term.get("terma_id")
                        real_pid = pid
                        self.logger.info(f"Using provided PID {pid} for session {session_id}")
                        break
            
            if not session_id or not real_pid:
                self.logger.warning(f"No terminal found for PID {pid}")
                return False
            
            # Remove from roster immediately (UI updates)
            self.roster.remove_terminal(session_id)
            self.logger.info(f"Removed session {session_id} from roster")
            
            # Try graceful shutdown first with SIGTERM using the REAL PID
            try:
                os.kill(real_pid, signal.SIGTERM)
                self.logger.info(f"Sent SIGTERM to aish-proxy process {real_pid}")
                
                # Wait up to 3 seconds for process to terminate gracefully
                # Check every 0.5 seconds to see if process is gone
                for i in range(6):  # 6 * 0.5 = 3 seconds
                    time.sleep(0.5)
                    try:
                        os.kill(real_pid, 0)  # Check if process still exists
                        # Process still alive, continue waiting
                    except ProcessLookupError:
                        self.logger.info(f"Process {real_pid} terminated gracefully")
                        break
                else:
                    # Process didn't terminate after 3 seconds, use SIGKILL
                    try:
                        os.kill(real_pid, signal.SIGKILL)
                        self.logger.info(f"Had to use SIGKILL on process {real_pid} after SIGTERM timeout")
                    except ProcessLookupError:
                        # Process died between checks
                        pass
                        
            except ProcessLookupError:
                self.logger.info(f"Process {real_pid} already gone")
            
            # Now close the Terminal window
            # For macOS Terminal.app, we need to close windows containing our session
            if self.platform == "darwin" and session_id:
                # Use AppleScript to close windows with our session ID
                # Try a more aggressive approach
                script = f'''
                tell application "Terminal"
                    set windowList to every window
                    repeat with aWindow in windowList
                        try
                            set tabList to every tab of aWindow
                            repeat with aTab in tabList
                                if (history of aTab as string) contains "{session_id}" then
                                    close aWindow saving no
                                    return "closed"
                                end if
                            end repeat
                        end try
                    end repeat
                    return "not found"
                end tell
                '''
                
                self.logger.info(f"Closing Terminal window for session {session_id}")
                result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
                self.logger.info(f"AppleScript result: {result.stdout}")
                if result.stderr:
                    self.logger.warning(f"AppleScript stderr: {result.stderr}")
            
            if pid in self.terminals:
                self.terminals[pid].status = "terminated"
                self.logger.info(f"Updated local terminal status to terminated")
            
            self.logger.info("=" * 60)
            self.logger.info("TERMINAL TERMINATION COMPLETED")
            self.logger.info(f"Successfully terminated session {session_id}")
            self.logger.info("=" * 60)
            return True
        except Exception as e:
            self.logger.error("=" * 60)
            self.logger.error("TERMINAL TERMINATION FAILED")
            self.logger.error(f"Error: {e}")
            self.logger.error(f"Stack trace:", exc_info=True)
            self.logger.error("=" * 60)
            return False
    
    def list_terminals(self) -> List[TerminalInfo]:
        """List all tracked terminals from the active roster."""
        # Get terminals from roster
        roster_terminals = self.roster.get_terminals()
        
        # Convert roster format to TerminalInfo objects
        terminals = []
        for term_data in roster_terminals:
            # Create config from stored data
            config = TerminalConfig(
                name=term_data.get("name", "Terminal"),
                app=term_data.get("terminal_app"),
                working_dir=term_data.get("working_dir"),
                purpose=term_data.get("purpose"),
                template=term_data.get("template")
            )
            
            # Create TerminalInfo
            # Handle launched_at which might be datetime or string
            launched_at = term_data.get("launched_at")
            if isinstance(launched_at, str):
                launched_at = datetime.fromisoformat(launched_at)
            elif not isinstance(launched_at, datetime):
                launched_at = datetime.now()  # Default to now if missing or invalid
            
            info = TerminalInfo(
                pid=term_data.get("pid", 0),
                config=config,
                launched_at=launched_at,
                status=term_data.get("status", "unknown"),
                platform=self.platform,
                terminal_app=term_data.get("terminal_app", ""),
                terma_id=term_data.get("terma_id", ""),
                last_heartbeat=term_data.get("last_heartbeat")
            )
            terminals.append(info)
        
        return terminals
    
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
            name="CI Workspace",
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
        help="Purpose/context for CI assistance"
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