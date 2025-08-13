#!/usr/bin/env python3
"""
Example integration of automatic landmarks with Telos proposal system.
Shows how minimal the changes are to instrument existing code.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from shared.landmarks.auto_capture import landmark


@landmark.auto('proposal_conversion')
def convert_proposal_to_sprint(proposal_name: str, proposal_data: dict) -> dict:
    """
    Original Telos function with minimal landmark instrumentation.
    Just add the decorator - that's it!
    """
    # Base paths
    base_path = "/Users/cskoons/projects/github/Tekton"
    proposals_path = Path(base_path) / "MetaData/DevelopmentSprints/Proposals"
    sprints_path = proposals_path / "Sprints"
    sprint_dir = Path(base_path) / "MetaData/DevelopmentSprints" / f"{proposal_name}_Sprint"
    
    # File lifecycle landmark
    landmark.watch_file(sprint_dir, 'creating')
    
    # Create sprint directory
    sprint_dir.mkdir(parents=True, exist_ok=True)
    
    # Decision point landmark
    with landmark.decision('file_structure', reason='standard sprint template'):
        # Create DAILY_LOG.md
        daily_log = sprint_dir / "DAILY_LOG.md"
        daily_log.write_text(f"# {proposal_name} Sprint - Daily Log\n\n")
        landmark.watch_file(daily_log, 'created')
        
        # Create HANDOFF.md
        handoff = sprint_dir / "HANDOFF.md"
        handoff.write_text(f"# {proposal_name} Sprint - Handoff Document\n\n")
        landmark.watch_file(handoff, 'created')
        
        # Create SPRINT_PLAN.md
        sprint_plan = sprint_dir / "SPRINT_PLAN.md"
        sprint_plan.write_text(f"# {proposal_name} Sprint Plan\n\n")
        landmark.watch_file(sprint_plan, 'created')
    
    # Move proposal to archive
    source = proposals_path / f"{proposal_name}.json"
    target = sprints_path / f"{proposal_name}.json"
    
    if source.exists():
        landmark.watch_file(source, 'moving')
        source.rename(target)
        landmark.watch_file(target, 'moved')
    
    # State transition landmark (automatic from decorator)
    return {
        'status': 'success',
        'sprint_dir': str(sprint_dir),
        'files_created': ['DAILY_LOG.md', 'HANDOFF.md', 'SPRINT_PLAN.md']
    }


def notify_planning_team(sprint_name: str) -> None:
    """
    Notify Planning Team CIs about new sprint.
    Shows API boundary landmarks.
    """
    components = ['prometheus', 'metis', 'harmonia']
    
    for component in components:
        # API call landmark
        landmark.api_call('telos', component, '/api/v1/workflow', 'POST')
        
        # In real code, would make actual API call here
        print(f"Notifying {component} about {sprint_name}")


# Example of watching for patterns to suggest new landmarks
class PatternDetector:
    """Detect repeated patterns that could become landmarks."""
    
    def __init__(self):
        self.patterns = {}
    
    def observe(self, text: str) -> None:
        """Watch for repeated phrases that might be landmarks."""
        # Simple pattern detection
        if 'this is tricky' in text.lower():
            self.suggest_landmark('@complexity_flag')
        if 'similar to' in text.lower():
            self.suggest_landmark('@pattern_reference')
        if 'be careful' in text.lower() or 'watch out' in text.lower():
            self.suggest_landmark('@coaching_moment')
    
    def suggest_landmark(self, landmark_type: str) -> None:
        """Suggest a new landmark type based on patterns."""
        self.patterns[landmark_type] = self.patterns.get(landmark_type, 0) + 1
        
        # After seeing pattern 3 times, suggest it
        if self.patterns[landmark_type] == 3:
            landmark.emit('pattern:suggested', {
                'suggested_type': landmark_type,
                'frequency': self.patterns[landmark_type]
            })
            print(f"Suggestion: Consider using {landmark_type} landmark")


if __name__ == '__main__':
    # Test the integration
    print("Testing landmark integration...")
    
    # Test proposal conversion with automatic landmarks
    result = convert_proposal_to_sprint(
        "Test_Proposal",
        {"description": "Test proposal for landmark system"}
    )
    print(f"Conversion result: {result}")
    
    # Test Planning Team notification
    notify_planning_team("Test_Proposal_Sprint")
    
    # Test pattern detection
    detector = PatternDetector()
    detector.observe("This is tricky to implement")
    detector.observe("This is tricky but manageable")
    detector.observe("This is tricky, needs review")  # Triggers suggestion
    
    print(f"\nTotal landmarks captured: {len(landmark.landmarks)}")
    print("Landmarks are being written to:", landmark.registry_path)