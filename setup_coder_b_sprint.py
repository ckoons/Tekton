#!/usr/bin/env python3
"""Set up Claude Code as Coder-B for Memory Evolution Sprint."""

import json
import sys
import os
import time
from pathlib import Path

# Add shared to path
sys.path.insert(0, str(Path(__file__).parent))

from shared.ci_tools.simple_launcher_v2 import SimpleToolLauncherV2
from shared.ci_tools import get_registry
from tekton.core.sprint_manager import SprintManager

def setup_coder_b_sprint():
    """Set up Claude Code to work as Coder-B on Memory Evolution Sprint."""
    
    print("=== Setting up Claude Code for Coder-B Sprint Work ===\n")
    
    # 1. Initialize components
    launcher = SimpleToolLauncherV2()
    registry = get_registry()
    sprint_manager = SprintManager()
    
    # 2. Launch Claude Code
    print("1. Launching Claude Code CI tool...")
    if launcher.launch_tool('claude-code', session_id='memory-evolution-sprint'):
        print("✓ Claude Code launched successfully")
    else:
        print("✗ Failed to launch Claude Code")
        return False
    
    # Give it time to start
    time.sleep(2)
    
    # 3. Verify it's running
    status = launcher.get_tool_status('claude-code')
    if status['running']:
        print(f"✓ Claude Code running on port {status['port']}")
    else:
        print("✗ Claude Code not running")
        return False
    
    # 4. Assign sprint to Coder-B
    print("\n2. Assigning Memory Evolution Sprint to Coder-B...")
    try:
        sprint_manager.assign_sprint('Memory_Evolution_Sprint', 'Coder-B', priority='high')
        print("✓ Sprint assigned to Coder-B")
    except Exception as e:
        print(f"Note: Sprint assignment via API failed ({e}), updating registry directly")
        
        # Update registry directly
        registry.update_ci('Coder-B', {
            'active-sprint': 'Memory_Evolution_Sprint',
            'current-phase': 'Phase 1: Memory Evolution Foundation',
            'current-task': 'Conversation Memory System',
            'tool': 'claude-code',
            'status': 'active',
            'last-update': time.time()
        })
        print("✓ Updated Coder-B registry with sprint assignment")
    
    # 5. Create initial context message
    print("\n3. Preparing sprint context for Claude Code...")
    
    sprint_context = {
        'role': 'Coder-B',
        'sprint': 'Memory_Evolution_Sprint',
        'phase': 'Phase 1: Memory Evolution Foundation',
        'primary_task': 'Conversation Memory System',
        'objectives': [
            'Implement conversation memory with pattern recognition',
            'Create memory indexing and retrieval system',
            'Build pattern engine for insight extraction',
            'Integrate with existing Engram system'
        ],
        'sprint_plan': 'MetaData/DevelopmentSprints/Memory_Evolution_Sprint/SPRINT_PLAN.md',
        'working_branch': 'sprint/coder-b/memory-evolution-sprint'
    }
    
    # 6. Send context to Claude Code (would need actual messaging)
    print("\n4. Sprint context prepared:")
    print(json.dumps(sprint_context, indent=2))
    
    # 7. Update Coder-B's DAILY_LOG.md
    print("\n5. Updating Coder-B's daily log...")
    daily_log_path = Path("CIs/Coder-B/DAILY_LOG.md")
    
    if daily_log_path.exists():
        with open(daily_log_path, 'r') as f:
            content = f.read()
        
        # Add new entry
        new_entry = f"""
## Sprint Assignment - Memory Evolution Sprint

**Date**: {time.strftime('%Y-%m-%d %H:%M')}
**Sprint**: Memory Evolution Sprint  
**Phase**: Phase 1 - Memory Evolution Foundation
**Task**: Conversation Memory System
**Tool**: Claude Code (via ci-tools)
**Status**: Sprint initialized, Claude Code launched

### Objectives:
1. Implement conversation memory with pattern recognition
2. Create memory indexing and retrieval system  
3. Build pattern engine for insight extraction
4. Integrate with existing Engram system

### Next Steps:
- Review sprint plan in detail
- Analyze existing Engram architecture
- Design conversation memory schema
- Begin implementation of core memory structures

---
"""
        
        # Prepend to log
        with open(daily_log_path, 'w') as f:
            f.write(new_entry + content)
        
        print("✓ Updated Coder-B's DAILY_LOG.md")
    
    # 8. Display next steps
    print("\n=== Setup Complete! ===")
    print("\nNext steps to start working:")
    print("1. Create sprint branch: git checkout -b sprint/coder-b/memory-evolution-sprint")
    print("2. Communicate with Claude Code: aish claude-code \"Review Memory Evolution Sprint plan\"")
    print("3. Or forward terminal: aish forward claude-code term3")
    print("\nClaude Code is now running as Coder-B and ready to work on the Memory Evolution Sprint!")
    
    return True

if __name__ == '__main__':
    if setup_coder_b_sprint():
        print("\n✓ Setup completed successfully!")
    else:
        print("\n✗ Setup failed!")
        sys.exit(1)