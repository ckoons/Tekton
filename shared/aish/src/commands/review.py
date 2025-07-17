#!/usr/bin/env python3
"""
aish review command - Terminal session capture for analysis

Captures terminal sessions using the Unix 'script' command for later analysis
by Sophia and Noesis. Sessions are stored with metadata for research purposes.
"""

import os
import sys
import json
import gzip
import shutil
import tempfile
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from shared.env import TektonEnviron

def get_session_tracking_file() -> Path:
    """Get the path to the session tracking file."""
    tekton_root = TektonEnviron.get('TEKTON_ROOT')
    if not tekton_root:
        print("Error: TEKTON_ROOT not set")
        sys.exit(1)
    tracking_dir = Path(tekton_root) / '.tekton' / 'terma'
    tracking_dir.mkdir(parents=True, exist_ok=True)
    return tracking_dir / '.review_session'

def get_active_session() -> Optional[Dict[str, str]]:
    """Get info about the currently active review session."""
    tracking_file = get_session_tracking_file()
    if tracking_file.exists():
        try:
            with open(tracking_file, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

def save_session_info(session_info: Dict[str, str]):
    """Save session info to tracking file."""
    tracking_file = get_session_tracking_file()
    with open(tracking_file, 'w') as f:
        json.dump(session_info, f)

def clear_session_info():
    """Clear the session tracking file."""
    tracking_file = get_session_tracking_file()
    if tracking_file.exists():
        tracking_file.unlink()

def format_duration(seconds: float) -> str:
    """Format duration in human-readable form."""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"

def format_size(size_bytes: int) -> str:
    """Format file size in human-readable form."""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f}MB"

def check_script_running() -> Optional[int]:
    """Check if script command is already running in this shell."""
    # Check for SCRIPT environment variable that script command sets
    if TektonEnviron.get('SCRIPT'):
        return os.getppid()  # Return parent PID
    return None

def start_review() -> int:
    """Start a new review session."""
    # Check if we're already inside a script session
    if check_script_running():
        print("Already inside a script session. Use 'aish review stop' to end current session.")
        return 1
    
    # Check if session already active
    active_session = get_active_session()
    if active_session and os.path.exists(active_session['temp_file']):
        print(f"Review session already active: {active_session['temp_file']}")
        return 0
    
    # Clear any stale session info
    if active_session:
        clear_session_info()
    
    # Create temp file for script output
    temp_fd, temp_file = tempfile.mkstemp(suffix='.typescript', prefix='aish_review_', dir='/tmp')
    os.close(temp_fd)  # Close the file descriptor, script will handle the file
    
    # Get terminal metadata
    terminal_name = TektonEnviron.get('TERMA_TERMINAL_NAME', 'unknown')
    terminal_purpose = TektonEnviron.get('TEKTON_TERMINAL_PURPOSE', '')
    terminal_role = TektonEnviron.get('TEKTON_TERMINAL_ROLE', 'coding')
    
    # Save session info
    session_info = {
        'temp_file': temp_file,
        'start_time': datetime.utcnow().isoformat() + 'Z',
        'terminal_name': terminal_name,
        'terminal_purpose': terminal_purpose,
        'terminal_role': terminal_role,
        'session_version': '1.0'
    }
    
    save_session_info(session_info)
    
    # Prepare script command
    # On macOS: script -q file
    # On Linux: script -q -f file
    if sys.platform == 'darwin':
        script_cmd = ['script', '-q', temp_file]
    else:
        script_cmd = ['script', '-q', '-f', temp_file]
    
    print(f"Review session recording to: {temp_file}")
    print(f"Run this command to start recording:")
    print(f"  {' '.join(script_cmd)}")
    print(f"\nWhen done, type 'exit' to end the script session,")
    print(f"then run 'aish review stop' to save the session.")
    
    return 0

def stop_review() -> int:
    """Stop the current review session and process the file."""
    # Get active session
    active_session = get_active_session()
    if not active_session:
        print("No active review session")
        return 1
    
    temp_file = active_session['temp_file']
    
    # Check if temp file exists
    if not os.path.exists(temp_file):
        print(f"Session file not found: {temp_file}")
        clear_session_info()
        return 1
    
    # Calculate duration
    start_time = datetime.fromisoformat(active_session['start_time'].replace('Z', '+00:00'))
    end_time = datetime.utcnow().replace(tzinfo=start_time.tzinfo)
    duration = (end_time - start_time).total_seconds()
    
    # Get sessions directory
    main_root = TektonEnviron.get('TEKTON_MAIN_ROOT', TektonEnviron.get('TEKTON_ROOT'))
    if not main_root:
        print("Error: TEKTON_ROOT not set")
        return False
    sessions_dir = Path(main_root) / '.tekton' / 'terminal-sessions'
    sessions_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    terminal_name = active_session['terminal_name']
    timestamp = start_time.strftime('%Y%m%d-%H%M%S')
    final_name = f"{terminal_name}-{timestamp}.log.gz"
    final_path = sessions_dir / final_name
    
    # Add metadata trailer to temp file
    metadata = {
        'start_time': active_session['start_time'],
        'end_time': end_time.isoformat() + 'Z',
        'terminal_name': terminal_name,
        'terminal_purpose': active_session['terminal_purpose'],
        'terminal_role': active_session['terminal_role'],
        'session_version': active_session['session_version'],
        'duration_seconds': duration
    }
    
    # Append metadata to file
    with open(temp_file, 'a') as f:
        f.write('\n[END OF SESSION]\n')
        f.write('--- TEKTON SESSION METADATA ---\n')
        json.dump(metadata, f, indent=2)
        f.write('\n--- END METADATA ---\n')
    
    # Compress and move to final location
    with open(temp_file, 'rb') as f_in:
        with gzip.open(final_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    # Remove temp file
    os.unlink(temp_file)
    
    # Get final file size
    file_size = final_path.stat().st_size
    
    # Clear session tracking
    clear_session_info()
    
    # Report results
    print(f"Session saved: {final_path}")
    print(f"Size: {format_size(file_size)}  Duration: {format_duration(duration)}")
    
    return 0

def list_reviews(args: List[str]) -> int:
    """List recent review sessions."""
    # Get sessions directory
    main_root = TektonEnviron.get('TEKTON_MAIN_ROOT', TektonEnviron.get('TEKTON_ROOT'))
    if not main_root:
        print("Error: TEKTON_ROOT not set")
        return False
    sessions_dir = Path(main_root) / '.tekton' / 'terminal-sessions'
    
    if not sessions_dir.exists():
        print("No sessions found")
        return 0
    
    # Get all session files
    sessions = []
    for session_file in sessions_dir.glob('*.log.gz'):
        # Extract metadata from filename
        parts = session_file.stem.split('-')  # Remove .log.gz
        if len(parts) >= 3:
            terminal_name = parts[0]
            date_str = parts[1]
            time_str = parts[2].split('.')[0]  # Remove .log part
            
            # Get file info
            file_size = session_file.stat().st_size
            
            # Try to read duration from file metadata
            duration = None
            try:
                with gzip.open(session_file, 'rt') as f:
                    content = f.read()
                    if '--- TEKTON SESSION METADATA ---' in content:
                        metadata_start = content.find('--- TEKTON SESSION METADATA ---')
                        metadata_end = content.find('--- END METADATA ---')
                        if metadata_start != -1 and metadata_end != -1:
                            metadata_json = content[metadata_start + 32:metadata_end].strip()
                            metadata = json.loads(metadata_json)
                            duration = metadata.get('duration_seconds', 0)
            except:
                pass
            
            sessions.append({
                'file': session_file.name,
                'terminal': terminal_name,
                'timestamp': f"{date_str}-{time_str}",
                'size': file_size,
                'duration': duration or 0
            })
    
    # Sort by timestamp (newest first)
    sessions.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Display results
    if not sessions:
        print("No sessions found")
        return 0
    
    # Print header
    print(f"{'Session':<40} {'Size':<10} {'Duration':<10}")
    print("-" * 60)
    
    # Print sessions
    for session in sessions[:20]:  # Show last 20
        duration_str = format_duration(session['duration']) if session['duration'] else 'unknown'
        print(f"{session['file']:<40} {format_size(session['size']):<10} {duration_str:<10}")
    
    if len(sessions) > 20:
        print(f"\n... and {len(sessions) - 20} more sessions")
    
    return 0

def handle_command(args: List[str]) -> int:
    """Handle the review command."""
    if not args or args[0] == 'help':
        print("Usage: aish review <subcommand>")
        print()
        print("Subcommands:")
        print("  start    Start recording a new session")
        print("  stop     Stop recording and save session")
        print("  list     List recent sessions")
        print()
        print("Sessions are saved to $TEKTON_MAIN_ROOT/.tekton/terminal-sessions/")
        return 0
    
    subcommand = args[0]
    
    if subcommand == 'start':
        return start_review()
    elif subcommand == 'stop':
        return stop_review()
    elif subcommand == 'list':
        return list_reviews(args[1:])
    else:
        print(f"Unknown subcommand: {subcommand}")
        print("Use 'aish review help' for usage")
        return 1

# For aish integration
def execute(args: List[str]) -> int:
    """Entry point for aish command system."""
    return handle_command(args)