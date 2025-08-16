#!/usr/bin/env python3
"""
Window detection for CI terminals.

This module detects terminal window information for proper OS injection targeting.
"""

import os
import sys
import subprocess
import re
from typing import Optional, Dict, Any

def get_terminal_window_info() -> Dict[str, Any]:
    """
    Detect terminal window information for the current process.
    
    Returns:
        Dictionary containing window information:
        - window_id: Unique window identifier
        - app_name: Application name (Terminal, iTerm, etc.)
        - tty: Terminal device
        - title: Window title (if available)
        - platform: Operating system
    """
    info = {
        'platform': sys.platform,
        'tty': os.ttyname(0) if os.isatty(0) else None,
        'pid': os.getpid(),
        'ppid': os.getppid()
    }
    
    if sys.platform == 'darwin':
        info.update(_get_macos_window_info())
    elif sys.platform.startswith('linux'):
        info.update(_get_linux_window_info())
    elif sys.platform == 'win32':
        info.update(_get_windows_window_info())
    
    return info

def _get_macos_window_info() -> Dict[str, Any]:
    """Get window information on macOS."""
    info = {}
    
    # Try to get the terminal application name
    try:
        # Get the parent process info to find the terminal app
        result = subprocess.run(
            ['ps', '-p', str(os.getppid()), '-o', 'comm='],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            comm = result.stdout.strip()
            # Terminal apps on macOS
            if 'Terminal' in comm:
                info['app_name'] = 'Terminal'
            elif 'iTerm' in comm:
                info['app_name'] = 'iTerm2'
            else:
                info['app_name'] = comm
    except:
        pass
    
    # Try to get window ID using AppleScript
    try:
        # Get the frontmost window ID (when this script is run, it should be frontmost)
        script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            set windowTitle to ""
            try
                tell process frontApp
                    set windowTitle to title of front window
                end tell
            end try
            return frontApp & "|" & windowTitle
        end tell
        '''
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            parts = result.stdout.strip().split('|')
            if len(parts) >= 1:
                info['app_name'] = parts[0]
            if len(parts) >= 2:
                info['window_title'] = parts[1]
    except:
        pass
    
    # Get TTY session ID which can help identify the window
    if 'TTY' in os.environ:
        info['tty_session'] = os.environ['TTY']
    
    # Store the TERM_SESSION_ID if available (Terminal.app specific)
    if 'TERM_SESSION_ID' in os.environ:
        info['term_session_id'] = os.environ['TERM_SESSION_ID']
    
    # Store iTerm2 specific variables if available
    if 'ITERM_SESSION_ID' in os.environ:
        info['iterm_session_id'] = os.environ['ITERM_SESSION_ID']
    if 'ITERM_PROFILE' in os.environ:
        info['iterm_profile'] = os.environ['ITERM_PROFILE']
    
    return info

def _get_linux_window_info() -> Dict[str, Any]:
    """Get window information on Linux."""
    info = {}
    
    # Check if running under X11
    if 'DISPLAY' in os.environ:
        info['display'] = os.environ['DISPLAY']
        
        # Try to get window ID using xdotool
        try:
            result = subprocess.run(['xdotool', 'getactivewindow'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                info['window_id'] = result.stdout.strip()
                
                # Get window title
                result = subprocess.run(['xdotool', 'getwindowname', info['window_id']],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    info['window_title'] = result.stdout.strip()
        except:
            pass
    
    # Check for Wayland
    if 'WAYLAND_DISPLAY' in os.environ:
        info['wayland_display'] = os.environ['WAYLAND_DISPLAY']
        # Wayland window detection is more complex and less standardized
    
    # Get terminal emulator from environment
    if 'TERM_PROGRAM' in os.environ:
        info['app_name'] = os.environ['TERM_PROGRAM']
    elif 'TERMINAL_EMULATOR' in os.environ:
        info['app_name'] = os.environ['TERMINAL_EMULATOR']
    
    return info

def _get_windows_window_info() -> Dict[str, Any]:
    """Get window information on Windows."""
    info = {}
    # Windows Terminal specific
    if 'WT_SESSION' in os.environ:
        info['wt_session'] = os.environ['WT_SESSION']
    if 'WT_PROFILE_ID' in os.environ:
        info['wt_profile_id'] = os.environ['WT_PROFILE_ID']
    return info

def focus_window(window_info: Dict[str, Any]) -> bool:
    """
    Attempt to focus a window based on stored window information.
    
    Args:
        window_info: Window information dictionary from get_terminal_window_info()
        
    Returns:
        True if window was successfully focused, False otherwise
    """
    platform = window_info.get('platform', sys.platform)
    
    if platform == 'darwin':
        return _focus_macos_window(window_info)
    elif platform.startswith('linux'):
        return _focus_linux_window(window_info)
    elif platform == 'win32':
        return _focus_windows_window(window_info)
    
    return False

def _focus_macos_window(window_info: Dict[str, Any]) -> bool:
    """Focus a window on macOS."""
    app_name = window_info.get('app_name')
    if not app_name:
        return False
    
    try:
        # First, activate the application
        script = f'tell application "{app_name}" to activate'
        result = subprocess.run(['osascript', '-e', script],
                              capture_output=True, text=True)
        if result.returncode != 0:
            return False
        
        # If we have a window title, try to focus that specific window
        window_title = window_info.get('window_title')
        if window_title:
            # This is more complex and app-specific
            # For Terminal.app, we might use window ID
            # For iTerm2, we might use session ID
            pass
        
        return True
    except:
        return False

def _focus_linux_window(window_info: Dict[str, Any]) -> bool:
    """Focus a window on Linux."""
    window_id = window_info.get('window_id')
    if not window_id:
        return False
    
    try:
        # Use xdotool to focus the window
        result = subprocess.run(['xdotool', 'windowactivate', window_id],
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def _focus_windows_window(window_info: Dict[str, Any]) -> bool:
    """Focus a window on Windows."""
    # Would need pywinauto or similar
    return False

if __name__ == '__main__':
    # Test window detection
    info = get_terminal_window_info()
    print("Window Information:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test if we can focus back to this window
    print("\nTesting window focus...")
    print("Switching to another window in 3 seconds...")
    import time
    time.sleep(3)
    
    if focus_window(info):
        print("Successfully focused window!")
    else:
        print("Could not focus window")