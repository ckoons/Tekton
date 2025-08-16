#!/usr/bin/env python3
"""
OS-level keystroke injection for CI terminals.

This module provides cross-platform keystroke injection to send input
to programs that bypass stdin (like TUI applications).
"""

import os
import sys
import subprocess
import time
import shutil
from typing import Optional, List, Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Programs that typically need OS-level injection (TUI/interactive)
TUI_PROGRAMS = {
    'claude': True,         # Claude Code in interactive mode
    'vim': True,            # Vim editor
    'nvim': True,           # Neovim
    'emacs': True,          # Emacs
    'nano': True,           # Nano editor
    'less': True,           # Less pager
    'more': True,           # More pager
    'htop': True,           # Process viewer
    'top': True,            # Process viewer
    'tmux': True,           # Terminal multiplexer
    'screen': True,         # Terminal multiplexer
    'fzf': True,            # Fuzzy finder
    'tig': True,            # Git interface
    'lazygit': True,        # Git TUI
    'mc': True,             # Midnight Commander
    'ranger': True,         # File manager
    'ncdu': True,           # Disk usage analyzer
}

class OSInjector:
    """Handles OS-level keystroke injection."""
    
    def __init__(self):
        """Initialize the injector and detect available methods."""
        self.platform = sys.platform
        self.injection_method = self._detect_injection_method()
        
    def _detect_injection_method(self) -> Optional[str]:
        """Detect which injection method is available on this system."""
        if self.platform == 'darwin':
            # macOS - use osascript
            if shutil.which('osascript'):
                return 'osascript'
                
        elif self.platform.startswith('linux'):
            # Linux - try xdotool first (X11)
            if shutil.which('xdotool'):
                # Check if X11 is running
                if os.environ.get('DISPLAY'):
                    return 'xdotool'
            
            # Try ydotool (Wayland)
            if shutil.which('ydotool'):
                return 'ydotool'
                
        elif self.platform == 'win32':
            # Windows - would need pywinauto or similar
            # Not implemented yet
            pass
            
        return None
        
    def is_available(self) -> bool:
        """Check if OS injection is available on this system."""
        return self.injection_method is not None
        
    def inject_text(self, text: str) -> bool:
        """
        Inject text as keystrokes.
        
        Args:
            text: Text to type
            
        Returns:
            True if successful, False otherwise
        """
        if not self.injection_method:
            logger.warning("No OS injection method available")
            return False
            
        try:
            if self.injection_method == 'osascript':
                return self._inject_osascript(text)
            elif self.injection_method == 'xdotool':
                return self._inject_xdotool(text)
            elif self.injection_method == 'ydotool':
                return self._inject_ydotool(text)
            else:
                return False
        except Exception as e:
            logger.error(f"OS injection failed: {e}")
            return False
            
    def inject_key(self, key: str) -> bool:
        """
        Inject a special key (like Return, Tab, Escape).
        
        Args:
            key: Key name (Return, Tab, Escape, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.injection_method:
            logger.warning("No OS injection method available")
            return False
            
        try:
            if self.injection_method == 'osascript':
                return self._inject_key_osascript(key)
            elif self.injection_method == 'xdotool':
                return self._inject_key_xdotool(key)
            elif self.injection_method == 'ydotool':
                return self._inject_key_ydotool(key)
            else:
                return False
        except Exception as e:
            logger.error(f"OS key injection failed: {e}")
            return False
            
    def _inject_osascript(self, text: str) -> bool:
        """Inject text using macOS osascript."""
        # Escape quotes and backslashes for AppleScript
        text = text.replace('\\', '\\\\').replace('"', '\\"')
        
        cmd = ['osascript', '-e', f'tell application "System Events" to keystroke "{text}"']
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
        
    def _inject_key_osascript(self, key: str) -> bool:
        """Inject special key using macOS osascript."""
        # Map key names to AppleScript key codes
        key_codes = {
            'Return': '36',
            'Enter': '36',
            'Tab': '48',
            'Escape': '53',
            'Space': '49',
            'Delete': '51',
            'Up': '126',
            'Down': '125',
            'Left': '123',
            'Right': '124',
        }
        
        if key in key_codes:
            cmd = ['osascript', '-e', f'tell application "System Events" to key code {key_codes[key]}']
        else:
            # Try as a regular key
            cmd = ['osascript', '-e', f'tell application "System Events" to key code "{key}"']
            
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
        
    def _inject_xdotool(self, text: str) -> bool:
        """Inject text using Linux xdotool."""
        cmd = ['xdotool', 'type', text]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
        
    def _inject_key_xdotool(self, key: str) -> bool:
        """Inject special key using Linux xdotool."""
        # xdotool uses X11 key names
        key_map = {
            'Enter': 'Return',
            'Escape': 'Escape',
            'Tab': 'Tab',
            'Space': 'space',
            'Delete': 'BackSpace',
        }
        
        key_name = key_map.get(key, key)
        cmd = ['xdotool', 'key', key_name]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
        
    def _inject_ydotool(self, text: str) -> bool:
        """Inject text using Linux ydotool (Wayland)."""
        cmd = ['ydotool', 'type', text]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
        
    def _inject_key_ydotool(self, key: str) -> bool:
        """Inject special key using Linux ydotool."""
        # ydotool uses kernel key codes
        # These are approximate mappings
        key_codes = {
            'Return': '28:1 28:0',  # Press and release
            'Enter': '28:1 28:0',
            'Tab': '15:1 15:0',
            'Escape': '1:1 1:0',
            'Space': '57:1 57:0',
            'Delete': '14:1 14:0',
        }
        
        if key in key_codes:
            cmd = ['ydotool', 'key'] + key_codes[key].split()
        else:
            # Try as text
            return self._inject_ydotool(key)
            
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0


def should_use_os_injection(program: str, force: Optional[bool] = None) -> bool:
    """
    Determine if a program should use OS injection.
    
    Args:
        program: Program name or path
        force: Force injection on (True) or off (False), or auto-detect (None)
        
    Returns:
        True if OS injection should be used
    """
    if force is not None:
        return force
        
    # Extract program name from path
    prog_name = os.path.basename(program).lower()
    
    # Remove common suffixes
    for suffix in ['.exe', '.app', '.sh', '.py']:
        if prog_name.endswith(suffix):
            prog_name = prog_name[:-len(suffix)]
            
    # Check against known TUI programs
    return prog_name in TUI_PROGRAMS


def inject_message_with_delimiter(
    message: str,
    delimiter: str = '\n',
    use_injection: bool = True,
    window_info: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Inject a message followed by a delimiter using OS injection.
    
    Args:
        message: Message to send
        delimiter: Delimiter to send after message
        use_injection: Whether to use OS injection
        window_info: Optional window information for focusing
        
    Returns:
        True if successful, False otherwise
    """
    if not use_injection:
        return False
        
    injector = OSInjector()
    if not injector.is_available():
        logger.warning("OS injection not available on this system")
        return False
    
    # Try to focus the target window if window info provided
    if window_info:
        try:
            from window_detector import focus_window
            if focus_window(window_info):
                logger.info(f"Focused window: {window_info.get('app_name', 'unknown')}")
                # Small delay to ensure focus completes
                time.sleep(0.1)
            else:
                logger.warning(f"Could not focus window: {window_info}")
        except Exception as e:
            logger.warning(f"Error focusing window: {e}")
        
    # Send the message
    if message:
        if not injector.inject_text(message):
            return False
            
        # Small delay between text and delimiter
        time.sleep(0.01)
        
    # Send delimiter
    if delimiter:
        # Handle special delimiters
        if delimiter in ['\n', '\r\n', '\r']:
            return injector.inject_key('Return')
        elif delimiter == '\t':
            return injector.inject_key('Tab')
        elif delimiter == '\x1b':  # ESC
            return injector.inject_key('Escape')
        else:
            # Send as text
            return injector.inject_text(delimiter)
            
    return True


def get_injection_info() -> dict:
    """
    Get information about OS injection capabilities.
    
    Returns:
        Dictionary with injection information
    """
    injector = OSInjector()
    return {
        'available': injector.is_available(),
        'platform': injector.platform,
        'method': injector.injection_method,
        'tui_programs': list(TUI_PROGRAMS.keys()),
    }


if __name__ == '__main__':
    # Test/demo mode
    import argparse
    
    parser = argparse.ArgumentParser(description='OS-level keystroke injection utility')
    parser.add_argument('--info', action='store_true', help='Show injection capabilities')
    parser.add_argument('--test', action='store_true', help='Test injection (3 test messages)')
    parser.add_argument('--inject', metavar='TEXT', help='Inject text')
    parser.add_argument('--key', metavar='KEY', help='Inject special key (Return, Tab, Escape)')
    
    args = parser.parse_args()
    
    if args.info:
        info = get_injection_info()
        print(f"OS Injection Available: {info['available']}")
        print(f"Platform: {info['platform']}")
        print(f"Method: {info['method']}")
        print(f"Known TUI Programs: {', '.join(info['tui_programs'])}")
        
    elif args.test:
        print("Testing OS injection in 3 seconds...")
        print("Make sure your target window is active!")
        time.sleep(3)
        
        injector = OSInjector()
        if not injector.is_available():
            print("OS injection not available on this system")
            sys.exit(1)
            
        for i in range(3):
            print(f"Sending test {i+1}")
            if injector.inject_text(f"Test message {i+1}"):
                injector.inject_key('Return')
                print("✓ Sent successfully")
            else:
                print("✗ Failed to send")
            time.sleep(1)
            
    elif args.inject:
        injector = OSInjector()
        if injector.inject_text(args.inject):
            print("Text injected successfully")
        else:
            print("Failed to inject text")
            sys.exit(1)
            
    elif args.key:
        injector = OSInjector()
        if injector.inject_key(args.key):
            print(f"Key '{args.key}' injected successfully")
        else:
            print(f"Failed to inject key '{args.key}'")
            sys.exit(1)
            
    else:
        parser.print_help()