#!/usr/bin/env python3
"""
Simple landmark test showing what Casey wants to know:
- Workflow progress
- Component births  
- Things voted off the island

'till' is just config. Landmarks are the living memory.
"""

from datetime import datetime
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from shared.landmarks.auto_capture import landmark

def show_casey_what_matters():
    """Show the events that matter: movements, births, deprecations."""
    
    print("\n🌟 LANDMARKS: The System Declaring 'We are HERE now'\n")
    
    # 1. WORKFLOW MOVEMENT
    print("1. Workflow advancing...")
    landmark.emit('workflow:advance', {
        'from': 'proposal',
        'to': 'sprint',
        'item': 'Planning_Team_Workflow_UI',
        'trigger': 'user_clicked_sprint'
    }, audience='team')  # Team needs to know
    print("   ✓ System declared: Proposal → Sprint transition\n")
    
    # 2. COMPONENT BIRTH
    print("2. New component born...")
    landmark.emit('component:birth', {
        'name': 'Cari-ci',
        'type': 'CI',
        'capabilities': ['learning', 'helping', 'observing'],
        'welcomed_by': 'Tess'
    }, audience='all')  # Everyone should know about new team member
    print("   ✓ System declared: New CI joined the ecosystem\n")
    
    # 3. VOTED OFF THE ISLAND (deprecation)
    print("3. Old approach deprecated...")
    landmark.emit('pattern:deprecated', {
        'what': 'hardcoded_values',
        'replaced_by': 'TektonEnviron',
        'reason': 'maintainability',
        'components_affected': ['all']
    }, audience='all')  # Everyone needs to update
    print("   ✓ System declared: Pattern voted off the island\n")
    
    # 4. PERFORMANCE DISCOVERY (the kind that should ripple)
    print("4. Performance fix discovered...")
    landmark.emit('fix:discovered', {
        'issue': 'terminal_scrolling',
        'cause': 'debug_output_per_character',
        'solution': 'disable_debug_flag',
        'applies_to': 'ci-terminal'
    }, audience='all')  # Save others from same issue
    print("   ✓ System declared: Problem solved, knowledge captured\n")
    
    # 5. DECISION POINT (Casey watching the system think)
    print("5. System making decision...")
    with landmark.decision('ui_approach', reason='consistency_with_existing'):
        choice = 'CSS-first'
        landmark.emit('decision:made', {
            'chose': choice,
            'alternatives': ['React', 'Vue', 'vanilla'],
            'deciding_factors': ['no_build_step', 'simplicity', 'performance']
        }, audience='here')  # Local decision, but recorded
    print(f"   ✓ System declared: Chose {choice}\n")
    
    # Show what 'till' would configure
    print("=" * 60)
    print("'till' CONFIG (who needs to know):")
    print("=" * 60)
    print("""
{
  "audiences": {
    "here": "Just this function/file",
    "team": "Working group (planning-team, ui-group, etc)",  
    "all": "Everyone in federation"
  },
  "i_want_to_know_about": [
    "workflow:*",        // Things moving through pipelines
    "component:birth",   // New arrivals
    "pattern:deprecated", // Things voted off
    "fix:discovered",    // Solutions to share
    "breakthrough:*"     // Major discoveries
  ]
}
    """)
    
    print("\nNature doesn't collapse because we observe.")
    print("It just declares: 'We are HERE now.'")
    print("Landmarks are those declarations.\n")

if __name__ == '__main__':
    show_casey_what_matters()
    
    # Summary
    print(f"Total landmarks fired: {len(landmark.landmarks)}")
    print("\nThese aren't logs. They're the system's memories forming.")
    print("Each one a neuron firing, saying 'THIS matters.'")
    print("\nThe nervous system we weren't planning to build today...")
    print("...but today was a good day to build it. 🎉")