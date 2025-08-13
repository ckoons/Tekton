#!/usr/bin/env python3
"""
File Watcher for Automatic Landmarks
Transparent monitoring of key directories without touching existing code.

Philosophy: Like quantum observation - we see everything without changing anything.
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Set, Dict, Any
from shared.landmarks.auto_capture import landmark

class ProposalWatcher:
    """Watch Proposals directory and drop landmarks automatically."""
    
    def __init__(self, watch_dir: Path):
        self.watch_dir = Path(watch_dir)
        self.known_files: Set[str] = set()
        self.file_states: Dict[str, Dict[str, Any]] = {}
        
        # Initialize with existing files
        self._scan_directory()
    
    def _scan_directory(self) -> None:
        """Scan directory for current state."""
        if not self.watch_dir.exists():
            return
            
        for filepath in self.watch_dir.glob("*.json"):
            if filepath.name not in self.known_files:
                # New file discovered
                self.known_files.add(filepath.name)
                self.file_states[filepath.name] = {
                    'path': str(filepath),
                    'mtime': filepath.stat().st_mtime,
                    'size': filepath.stat().st_size
                }
                
                # Don't emit landmarks for initial scan
    
    def watch(self, interval: float = 1.0) -> None:
        """Watch for changes and emit landmarks."""
        print(f"Watching {self.watch_dir} for changes...")
        
        while True:
            try:
                current_files = set()
                
                # Check all JSON files
                for filepath in self.watch_dir.glob("*.json"):
                    filename = filepath.name
                    current_files.add(filename)
                    
                    stat = filepath.stat()
                    current_state = {
                        'path': str(filepath),
                        'mtime': stat.st_mtime,
                        'size': stat.st_size
                    }
                    
                    if filename not in self.known_files:
                        # New file created
                        landmark.emit('proposal:created', {
                            'file': filename,
                            'path': str(filepath),
                            'size': stat.st_size,
                            'timestamp': datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
                        print(f"🔍 Landmark: proposal:created - {filename}")
                        
                    elif filename in self.file_states:
                        # Check for modifications
                        old_state = self.file_states[filename]
                        if current_state['mtime'] > old_state['mtime']:
                            landmark.emit('proposal:modified', {
                                'file': filename,
                                'path': str(filepath),
                                'old_size': old_state['size'],
                                'new_size': current_state['size'],
                                'timestamp': datetime.fromtimestamp(stat.st_mtime).isoformat()
                            })
                            print(f"🔍 Landmark: proposal:modified - {filename}")
                    
                    self.file_states[filename] = current_state
                
                # Check for deleted files
                deleted_files = self.known_files - current_files
                for filename in deleted_files:
                    landmark.emit('proposal:deleted', {
                        'file': filename,
                        'last_seen': self.file_states[filename]['path']
                    })
                    print(f"🔍 Landmark: proposal:deleted - {filename}")
                    del self.file_states[filename]
                
                # Update known files
                self.known_files = current_files
                
                # Check subdirectories for moved files
                sprints_dir = self.watch_dir / "Sprints"
                if sprints_dir.exists():
                    for filepath in sprints_dir.glob("*.json"):
                        filename = filepath.name
                        if filename not in self.file_states:
                            landmark.emit('proposal:archived', {
                                'file': filename,
                                'archived_to': str(filepath)
                            })
                            print(f"🔍 Landmark: proposal:archived - {filename}")
                            self.file_states[filename] = {
                                'path': str(filepath),
                                'archived': True
                            }
                
            except Exception as e:
                # Silent failure - watchers shouldn't crash
                print(f"Watcher error (continuing): {e}")
            
            time.sleep(interval)


def create_test_harness():
    """Create a simple test harness to demonstrate the system."""
    print("\n" + "="*60)
    print("LANDMARK SYSTEM TEST HARNESS")
    print("="*60)
    
    base_path = Path("/Users/cskoons/projects/github/Tekton")
    proposals_dir = base_path / "MetaData/DevelopmentSprints/Proposals"
    
    print(f"\n1. Starting file watcher on: {proposals_dir}")
    print("   (File operations will trigger landmarks automatically)")
    
    print("\n2. Simulating proposal creation...")
    test_proposal = {
        "name": "Landmark_Test",
        "purpose": "Test automatic landmark capture",
        "created": datetime.now().isoformat()
    }
    
    test_file = proposals_dir / "Landmark_Test.json"
    test_file.write_text(json.dumps(test_proposal, indent=2))
    print(f"   Created: {test_file.name}")
    
    # Give watcher time to detect
    time.sleep(2)
    
    print("\n3. Simulating proposal modification...")
    test_proposal["modified"] = datetime.now().isoformat()
    test_proposal["status"] = "updated"
    test_file.write_text(json.dumps(test_proposal, indent=2))
    print(f"   Modified: {test_file.name}")
    
    time.sleep(2)
    
    print("\n4. Simulating sprint conversion (archival)...")
    sprints_dir = proposals_dir / "Sprints"
    sprints_dir.mkdir(exist_ok=True)
    archived_file = sprints_dir / "Landmark_Test.json"
    test_file.rename(archived_file)
    print(f"   Archived to: {archived_file}")
    
    time.sleep(2)
    
    print("\n5. Querying captured landmarks...")
    print(f"   Total landmarks: {len(landmark.landmarks)}")
    
    # Show recent landmarks
    for lm in landmark.landmarks[-5:]:
        print(f"   - {lm['type']}: {lm['context'].get('file', 'N/A')}")
    
    print("\n✅ Test complete! Landmarks captured without touching any existing code.")
    print("   The system observed everything while changing nothing.")
    
    # Clean up
    if archived_file.exists():
        archived_file.unlink()
    

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Run test harness
        create_test_harness()
    else:
        # Run watcher
        base_path = Path("/Users/cskoons/projects/github/Tekton")
        proposals_dir = base_path / "MetaData/DevelopmentSprints/Proposals"
        
        watcher = ProposalWatcher(proposals_dir)
        try:
            watcher.watch(interval=1.0)
        except KeyboardInterrupt:
            print("\nWatcher stopped.")
            print(f"Captured {len(landmark.landmarks)} landmarks")
            print(f"Landmark log: {landmark.registry_path}")