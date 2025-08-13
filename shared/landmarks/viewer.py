#!/usr/bin/env python3
"""
Landmark Viewer - Watch the nervous system in action
Shows landmarks as they flow through Tekton's memory.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

def view_landmarks(filter_type: Optional[str] = None, audience: Optional[str] = None):
    """View captured landmarks with optional filtering."""
    
    landmarks_file = Path('/tmp/landmarks.json')
    if not landmarks_file.exists():
        print("No landmarks captured yet.")
        return
    
    with open(landmarks_file, 'r') as f:
        lines = f.readlines()
    
    landmarks = []
    for line in lines:
        if line.strip():
            try:
                landmarks.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    
    # Apply filters
    if filter_type:
        landmarks = [l for l in landmarks if filter_type in l['type']]
    if audience:
        landmarks = [l for l in landmarks if l.get('audience') == audience]
    
    # Display
    print("\n" + "="*70)
    print(f"TEKTON LANDMARKS - The System's Living Memory")
    print("="*70)
    
    if filter_type or audience:
        filters = []
        if filter_type:
            filters.append(f"type contains '{filter_type}'")
        if audience:
            filters.append(f"audience = '{audience}'")
        print(f"Filters: {' AND '.join(filters)}")
        print("-"*70)
    
    print(f"\nTotal landmarks: {len(landmarks)}")
    print("\n" + "-"*70)
    
    # Group by type for summary
    by_type = {}
    for l in landmarks:
        ltype = l['type']
        if ltype not in by_type:
            by_type[ltype] = []
        by_type[ltype].append(l)
    
    print("\nSUMMARY BY TYPE:")
    for ltype, items in sorted(by_type.items()):
        print(f"  {ltype:<30} : {len(items)} events")
    
    print("\n" + "-"*70)
    print("\nRECENT EVENTS (last 10):\n")
    
    for landmark in landmarks[-10:]:
        # Parse timestamp for cleaner display
        timestamp = landmark['timestamp'].split('T')[1][:8]
        
        # Color coding by audience
        audience_emoji = {
            'here': '🏠',
            'team': '👥',
            'all': '🌍',
            'local': '📍'
        }.get(landmark.get('audience', 'local'), '❓')
        
        print(f"{audience_emoji} [{timestamp}] {landmark['type']}")
        
        # Show relevant context
        ctx = landmark.get('context', {})
        if 'name' in ctx:
            print(f"   → {ctx['name']}")
        elif 'from' in ctx and 'to' in ctx:
            print(f"   → {ctx['from']} → {ctx['to']}")
        elif 'what' in ctx:
            print(f"   → Deprecated: {ctx['what']}")
        elif 'decision' in ctx:
            print(f"   → Decision: {ctx['decision']}")
        
        # Show where it happened
        stack = landmark.get('stack', {})
        if stack:
            file_path = Path(stack.get('file', ''))
            if 'Tekton' in str(file_path):
                short_path = str(file_path).split('Tekton/')[-1]
                print(f"   📍 {short_path}:{stack.get('line', '?')}")
        print()
    
    print("="*70)
    print("Audience: 🏠 here | 👥 team | 🌍 all | 📍 local")
    print("Each landmark is the system saying: 'We are HERE now.'")
    print("="*70)

if __name__ == '__main__':
    # Parse arguments
    filter_type = None
    audience = None
    
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.startswith('--type='):
                filter_type = arg.split('=')[1]
            elif arg.startswith('--audience='):
                audience = arg.split('=')[1]
            elif arg == '--help':
                print("""
Landmark Viewer - Watch Tekton's nervous system

Usage:
    python viewer.py                    # Show all landmarks
    python viewer.py --type=workflow    # Show workflow events
    python viewer.py --audience=team    # Show team-level events
    python viewer.py --type=component --audience=all  # Combined filters

Casey's favorite queries:
    --type=workflow     # Things moving through pipelines
    --type=component    # New births
    --type=deprecated   # Things voted off the island
    --audience=all      # Federation-wide events
""")
                sys.exit(0)
    
    view_landmarks(filter_type, audience)