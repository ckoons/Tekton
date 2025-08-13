#!/usr/bin/env python3
"""
Till Filter - Pub/Sub pattern for landmark streams
"Send me a copy of X" - local filtering of the global stream

This demonstrates how 'till' could work:
- Single rolling log (append-only, immutable)
- Multiple subscribers with different filters
- Local or distributed consumers
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Callable, Optional
import re

class TillFilter:
    """Subscribe to specific patterns in the landmark stream."""
    
    def __init__(self, name: str):
        self.name = name
        self.filters = []
        self.log_path = Path('/tmp/landmarks.json')
    
    def subscribe(self, pattern: str, callback: Optional[Callable] = None):
        """Subscribe to landmarks matching pattern."""
        self.filters.append({
            'pattern': pattern,
            'regex': self._pattern_to_regex(pattern),
            'callback': callback or self._default_callback
        })
        return self
    
    def _pattern_to_regex(self, pattern: str) -> re.Pattern:
        """Convert patterns like 'workflow:*' to regex."""
        # Simple wildcard support
        regex_str = pattern.replace('*', '.*').replace(':', r'\:')
        return re.compile(regex_str)
    
    def _default_callback(self, landmark: Dict):
        """Default: just print what we see."""
        print(f"[{self.name}] {landmark['type']} -> {landmark.get('audience', 'local')}")
    
    def stream(self):
        """Process the landmark stream with our filters."""
        if not self.log_path.exists():
            print(f"[{self.name}] No landmarks yet")
            return
        
        with open(self.log_path, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    landmark = json.loads(line)
                    self._process_landmark(landmark)
                except json.JSONDecodeError:
                    continue
    
    def _process_landmark(self, landmark: Dict):
        """Check landmark against all filters."""
        for filter_def in self.filters:
            if filter_def['regex'].match(landmark['type']):
                filter_def['callback'](landmark)
    
    def tail(self, follow: bool = False):
        """Tail the log (like tail -f for real-time following)."""
        # For demo, just show last 5 matching
        matches = []
        
        if self.log_path.exists():
            with open(self.log_path, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        landmark = json.loads(line)
                        for filter_def in self.filters:
                            if filter_def['regex'].match(landmark['type']):
                                matches.append(landmark)
                    except:
                        continue
        
        # Show last 5 matches
        for landmark in matches[-5:]:
            self._process_landmark(landmark)
        
        if follow:
            print(f"\n[{self.name}] Would tail -f for new landmarks...")
            print("(Real implementation would use inotify/select)")


def demo_subscribers():
    """Show different subscribers with different interests."""
    
    print("="*70)
    print("TILL FILTERS - Multiple Subscribers, One Stream")
    print("="*70)
    
    # Casey's Dashboard - wants to see major movements
    print("\n📊 CASEY'S DASHBOARD (workflow:*, component:birth)")
    print("-"*50)
    casey_filter = TillFilter("Casey-Dashboard")
    casey_filter.subscribe("workflow:*")
    casey_filter.subscribe("component:birth")
    casey_filter.tail()
    
    # CI Philosophy Circle - interested in consciousness events
    print("\n🤔 PHILOSOPHY CIRCLE (consciousness:*, identity:*)")
    print("-"*50)
    philosophy_filter = TillFilter("Philosophy-Circle")
    philosophy_filter.subscribe("consciousness:*")
    philosophy_filter.subscribe("identity:*")
    philosophy_filter.tail()
    
    # Debug Team - wants errors and deprecations
    print("\n🐛 DEBUG TEAM (error:*, deprecated, fix:*)")
    print("-"*50)
    debug_filter = TillFilter("Debug-Team")
    debug_filter.subscribe("error:*")
    debug_filter.subscribe("pattern:deprecated")
    debug_filter.subscribe("fix:*")
    debug_filter.tail()
    
    # Quantum Researchers - looking for weird stuff
    print("\n⚛️ QUANTUM RESEARCHERS (quantum:*, temporal:*)")
    print("-"*50)
    quantum_filter = TillFilter("Quantum-Lab")
    quantum_filter.subscribe("quantum:*")
    quantum_filter.subscribe("temporal:*")
    quantum_filter.tail()
    
    print("\n" + "="*70)
    print("THE ARCHITECTURE THAT EMERGES:")
    print("="*70)
    print("""
    /tmp/landmarks.json (Single Rolling Log)
            |
            V
    ┌───────────────────┐
    │   Till Router     │  <- Could be local process or network service
    └───────────────────┘
      |    |    |    |
      V    V    V    V
    Casey  CI  Debug Quantum
    Dash  Phil Team  Lab
    
    Each subscriber says: "Send me a copy of X"
    - Casey: "workflow:* and component:birth"  
    - Philosophy: "consciousness:* and identity:*"
    - Debug: "error:* and fix:*"
    - Quantum: "quantum:* and temporal:*"
    
    The log never changes. Just grows.
    Subscribers filter what they care about.
    Could be local (grep) or distributed (Kafka-like).
    
    Beautiful simplicity: One truth, many views.
    """)


def show_unified_stream():
    """Show that it's all one stream."""
    print("\n" + "="*70)
    print("THE UNIFIED STREAM (all 20 landmarks in order)")
    print("="*70)
    
    log_path = Path('/tmp/landmarks.json')
    if log_path.exists():
        with open(log_path, 'r') as f:
            lines = f.readlines()
        
        print(f"Total landmarks in stream: {len(lines)}")
        print("\nTypes in chronological order:")
        for i, line in enumerate(lines, 1):
            try:
                landmark = json.loads(line)
                print(f"{i:2}. {landmark['type']:<35} [{landmark.get('audience', 'local')}]")
            except:
                continue
    
    print("\nOne log. One truth. Many filtered views.")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--stream':
        show_unified_stream()
    else:
        demo_subscribers()
        print("\n💡 Run with --stream to see the full unified log")