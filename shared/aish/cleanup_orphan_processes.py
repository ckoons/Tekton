#!/usr/bin/env python3
"""
Detect and clean up orphaned Tekton AI processes.
Safe for use as a cronjob - only removes confirmed orphans.
"""

import json
import os
import sys
import psutil
import socket
import signal
import time
from pathlib import Path
from datetime import datetime, timedelta

try:
    from landmarks import danger_zone, state_checkpoint, architecture_decision
except ImportError:
    # Fallback decorators if landmarks not available
    def danger_zone(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def architecture_decision(**kwargs):
        def decorator(func):
            return func
        return decorator

# Known Tekton AI process patterns
TEKTON_AI_PATTERNS = [
    'enhanced_tekton_ai_launcher.py',
    'tekton_ai_specialist.py',
    'ai_specialist_app.py',
    'rhetor-ai',
    'numa-ai',
    'apollo-ai',
    'athena-ai',
    'sophia-ai',
    'noesis-ai',
    'hermes-ai',
    'engram-ai',
    'prometheus-ai',
    'telos-ai',
    'metis-ai',
    'harmonia-ai',
    'synthesis-ai',
    'penia-ai',
    'ergon-ai',
    'terma-ai',
    'hephaestus-ai'
]

@architecture_decision(
    title="Safe orphan process detection",
    rationale="Need to identify truly orphaned processes without killing legitimate ones",
    alternatives_considered=["PID file tracking", "Parent process checking", "Port-based detection"],
    impacts=["system_stability", "ai_availability"],
    decided_by="Casey",
    date="2025-01-04"
)
def find_tekton_processes():
    """Find all Tekton-related processes."""
    tekton_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'status']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            
            # Check if this is a Tekton AI process
            is_tekton = False
            for pattern in TEKTON_AI_PATTERNS:
                if pattern in cmdline:
                    is_tekton = True
                    break
            
            # Also check for python processes running from Tekton directories
            if not is_tekton and 'python' in proc.info['name']:
                if '/Tekton/' in cmdline and any(ai_pattern in cmdline for ai_pattern in ['AI/', 'ai_specialist']):
                    is_tekton = True
            
            if is_tekton:
                tekton_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': cmdline,
                    'created': datetime.fromtimestamp(proc.info['create_time']),
                    'status': proc.info['status'],
                    'age_hours': (datetime.now() - datetime.fromtimestamp(proc.info['create_time'])).total_seconds() / 3600
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return tekton_processes

def load_registry():
    """Load the AI registry."""
    registry_path = Path.home() / '.tekton' / 'ai_registry' / 'platform_ai_registry.json'
    
    if not registry_path.exists():
        return {}
    
    try:
        with open(registry_path, 'r') as f:
            return json.load(f)
    except:
        return {}

def extract_component_name(cmdline):
    """Extract component name from command line."""
    # Look for component name in command line
    cmdline_lower = cmdline.lower()
    
    # Direct AI specialist names
    for component in ['rhetor', 'numa', 'apollo', 'athena', 'sophia', 'noesis', 
                     'hermes', 'engram', 'prometheus', 'telos', 'metis', 
                     'harmonia', 'synthesis', 'penia', 'ergon', 'terma', 'hephaestus']:
        if component in cmdline_lower:
            return component
    
    return None

@danger_zone(
    title="Orphan process cleanup",
    risk_level="high",
    potential_impacts=["May terminate AI processes", "Temporary service disruption"],
    mitigation="Multiple safety checks before termination",
    recovery="Restart affected AI specialists"
)
def identify_orphans(min_age_hours=1.0, verbose=False):
    """Identify orphaned Tekton processes."""
    processes = find_tekton_processes()
    registry = load_registry()
    
    # Get PIDs from registry
    registered_pids = set()
    for ai_name, entry in registry.items():
        pid = entry.get('metadata', {}).get('pid')
        if pid:
            registered_pids.add(pid)
    
    orphans = []
    legitimate = []
    
    for proc in processes:
        pid = proc['pid']
        component = extract_component_name(proc['cmdline'])
        
        # Safety checks for orphan detection
        is_orphan = True
        reasons = []
        
        # 1. Check if in registry
        if pid in registered_pids:
            is_orphan = False
            reasons.append("registered in AI registry")
        
        # 2. Check if it's too young (grace period)
        if proc['age_hours'] < min_age_hours:
            is_orphan = False
            reasons.append(f"too young ({proc['age_hours']:.1f} hours)")
        
        # 3. Check if it's a launcher process (short-lived)
        if 'launcher' in proc['cmdline'] and proc['age_hours'] < 0.1:  # 6 minutes
            is_orphan = False
            reasons.append("launcher process within grace period")
        
        # 4. Check process status
        if proc['status'] == 'zombie':
            is_orphan = True
            reasons = ["zombie process"]
        
        if is_orphan:
            orphans.append(proc)
            if verbose:
                print(f"🔴 Orphan: PID {pid} - {component or 'unknown'} (age: {proc['age_hours']:.1f}h)")
        else:
            legitimate.append(proc)
            if verbose:
                print(f"🟢 Legitimate: PID {pid} - {component or 'unknown'} ({', '.join(reasons)})")
    
    return orphans, legitimate

@state_checkpoint(
    title="Process termination audit",
    tracks=["pid", "process_name", "termination_time", "signal_used"],
    purpose="Audit trail for process cleanup"
)
def terminate_orphan(proc, force=False):
    """Safely terminate an orphan process."""
    pid = proc['pid']
    
    try:
        process = psutil.Process(pid)
        
        # Try graceful shutdown first
        if not force:
            process.terminate()  # SIGTERM
            time.sleep(2)  # Give it time to clean up
        
        # Check if still alive
        if process.is_running():
            process.kill()  # SIGKILL
            return f"PID {pid} killed (SIGKILL)"
        else:
            return f"PID {pid} terminated gracefully"
    
    except psutil.NoSuchProcess:
        return f"PID {pid} no longer exists"
    except psutil.AccessDenied:
        return f"PID {pid} access denied"
    except Exception as e:
        return f"PID {pid} error: {str(e)}"

def cleanup_orphans(dry_run=True, min_age_hours=1.0, verbose=False):
    """Main cleanup function."""
    print(f"Tekton Orphan Process Cleanup - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Minimum age for cleanup: {min_age_hours} hours")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print("-" * 60)
    
    orphans, legitimate = identify_orphans(min_age_hours, verbose)
    
    print(f"\nFound {len(legitimate)} legitimate processes")
    print(f"Found {len(orphans)} orphan processes")
    
    if orphans:
        print("\nOrphaned processes:")
        for proc in orphans:
            component = extract_component_name(proc['cmdline'])
            print(f"  PID {proc['pid']}: {component or 'unknown'} (age: {proc['age_hours']:.1f}h)")
            if verbose:
                print(f"    Command: {proc['cmdline'][:100]}...")
        
        if not dry_run:
            print("\nTerminating orphans...")
            for proc in orphans:
                result = terminate_orphan(proc)
                print(f"  {result}")
            
            # Log cleanup
            log_path = Path.home() / '.tekton' / 'logs' / 'orphan_cleanup.log'
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(log_path, 'a') as f:
                f.write(f"\n{datetime.now().isoformat()} - Cleaned {len(orphans)} orphans\n")
                for proc in orphans:
                    f.write(f"  PID {proc['pid']} - {proc['cmdline'][:100]}\n")
        else:
            print("\nDry run - no processes terminated")
    else:
        print("\nNo orphan processes found")
    
    return len(orphans)

def create_cron_script():
    """Create a wrapper script for cron."""
    script_content = """#!/bin/bash
# Tekton orphan process cleanup cron script
# Add to crontab: */30 * * * * /path/to/cleanup_tekton_orphans.sh

# Set up environment
export TEKTON_ROOT="${TEKTON_ROOT:-/Users/cskoons/projects/github/Tekton}"
export PYTHONPATH="$TEKTON_ROOT/shared:$PYTHONPATH"

# Run cleanup (not dry-run, 2 hour minimum age, not verbose)
python3 "$TEKTON_ROOT/shared/aish/cleanup_orphan_processes.py" --live --min-age 2.0

# Log completion
echo "$(date): Tekton orphan cleanup completed" >> ~/.tekton/logs/cron.log
"""
    
    script_path = Path.home() / '.tekton' / 'bin' / 'cleanup_tekton_orphans.sh'
    script_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make executable
    os.chmod(script_path, 0o755)
    
    print(f"\nCron script created at: {script_path}")
    print("\nTo add to crontab (runs every 30 minutes):")
    print("  crontab -e")
    print(f"  */30 * * * * {script_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Detect and clean up orphaned Tekton AI processes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (default) - just show what would be cleaned
  %(prog)s
  
  # Live cleanup with 2 hour minimum age
  %(prog)s --live --min-age 2.0
  
  # Verbose output
  %(prog)s --verbose
  
  # Create cron script
  %(prog)s --create-cron
        """
    )
    
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Show what would be cleaned without doing it (default)')
    parser.add_argument('--live', action='store_true',
                       help='Actually terminate orphan processes')
    parser.add_argument('--min-age', type=float, default=1.0,
                       help='Minimum age in hours before considering process orphaned (default: 1.0)')
    parser.add_argument('--verbose', action='store_true',
                       help='Show detailed process information')
    parser.add_argument('--create-cron', action='store_true',
                       help='Create cron wrapper script')
    
    args = parser.parse_args()
    
    if args.create_cron:
        create_cron_script()
    else:
        # --live overrides --dry-run
        dry_run = not args.live
        cleanup_orphans(dry_run, args.min_age, args.verbose)