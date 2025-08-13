#!/usr/bin/env python3
"""
Minimal Telos Demonstration - Quantum Observation Without Collapse

Shows how ONE decorator and a file watcher create a complete landmark cascade
without touching any core logic.
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Import our transparent hooks
from shared.landmarks.transparent_hooks import landmark, enable_transparent_landmarks
from shared.landmarks.federation_spec import FederationLandmark, LandmarkAudience, FederationLandmarkLog

# =============================================================================
# SIMULATE EXISTING TELOS CODE (unchanged)
# =============================================================================

class TelosProposalManager:
    """Existing Telos code - we won't change this logic at all"""
    
    def __init__(self):
        self.proposals_dir = Path("/tmp/tekton_demo/Proposals")
        self.sprints_dir = Path("/tmp/tekton_demo/Sprints")
        self.proposals_dir.mkdir(parents=True, exist_ok=True)
        self.sprints_dir.mkdir(parents=True, exist_ok=True)
    
    def create_proposal(self, name: str, data: Dict) -> Path:
        """Create a proposal (existing logic untouched)"""
        proposal_path = self.proposals_dir / f"{name}.json"
        
        proposal_data = {
            "name": name,
            "status": "proposal",
            "created": datetime.now().isoformat(),
            **data
        }
        
        with open(proposal_path, 'w') as f:
            json.dump(proposal_data, f, indent=2)
        
        return proposal_path
    
    # THIS IS THE ONLY CHANGE - ADD ONE DECORATOR
    @landmark.auto("sprint_conversion", audience=LandmarkAudience.PEER_GROUP, peer_groups=["planning-team"])
    def convert_to_sprint(self, proposal_name: str) -> Path:
        """Convert proposal to sprint (logic completely unchanged)"""
        
        # Read proposal
        proposal_path = self.proposals_dir / f"{proposal_name}.json"
        with open(proposal_path, 'r') as f:
            proposal_data = json.load(f)
        
        # Archive proposal (move to Sprints)
        archive_path = self.sprints_dir / f"{proposal_name}_archived.json"
        proposal_path.rename(archive_path)
        
        # Create sprint directory
        sprint_dir = self.sprints_dir / f"{proposal_name}_Sprint"
        sprint_dir.mkdir(exist_ok=True)
        
        # Create sprint files
        (sprint_dir / "SPRINT_PLAN.md").write_text(
            f"# {proposal_name} Sprint Plan\n\n"
            f"Converted from proposal: {proposal_data.get('purpose', 'Unknown')}\n"
        )
        
        (sprint_dir / "DAILY_LOG.md").write_text(
            f"# Daily Log for {proposal_name}\n\n## Day 1 - Sprint Initiated\n"
        )
        
        (sprint_dir / "HANDOFF.md").write_text(
            f"# Handoff Document\n\nSprint: {proposal_name}\n"
        )
        
        return sprint_dir


# =============================================================================
# DEMONSTRATION - Show the cascade with minimal changes
# =============================================================================

def demonstrate_landmark_cascade():
    """Show how landmarks cascade with ONE decorator"""
    
    print("🏔️ Telos Landmark Demonstration")
    print("=" * 60)
    print("Showing: Quantum Observation Without Collapse")
    print("The code doesn't know it's being watched!\n")
    
    # 1. Setup federation log
    fed_log = FederationLandmarkLog(Path("/tmp/tekton_demo/landmarks.jsonl"))
    
    # 2. Enable transparent landmarks (file watcher + exception hook)
    print("📡 Enabling transparent landmarks...")
    watcher = enable_transparent_landmarks(
        "telos",
        watch_dirs=["/tmp/tekton_demo/Proposals", "/tmp/tekton_demo/Sprints"]
    )
    print()
    
    # 3. Create Telos manager (existing code)
    telos = TelosProposalManager()
    
    # 4. Create a proposal (file watcher will auto-fire)
    print("📝 Creating proposal (file watcher will detect)...")
    proposal_path = telos.create_proposal(
        "DashboardUI",
        {
            "purpose": "Build dashboard with real-time updates",
            "requirements": ["CSS-first", "WebSocket support", "Responsive"]
        }
    )
    print(f"   Created: {proposal_path}")
    
    # Give file watcher time to detect
    time.sleep(0.5)
    
    # 5. Simulate CI enrichment (would happen automatically)
    print("\n🤖 CIs enriching with semantic landmarks...")
    
    # Telos CI adds pattern reference
    pattern_landmark = FederationLandmark(
        "@pattern_reference",
        {"pattern": "telos_card_ui", "component": "telos"},
        audience=LandmarkAudience.LOCAL
    )
    fed_log.log(pattern_landmark)
    print("   Telos: Added @pattern_reference: telos_card_ui")
    
    # Prometheus CI adds phases
    phases_landmark = FederationLandmark(
        "@phases_suggested",
        {"phases": ["design", "implement", "test"], "component": "prometheus"},
        audience=LandmarkAudience.LOCAL
    )
    fed_log.log(phases_landmark)
    print("   Prometheus: Added @phases_suggested: [design, implement, test]")
    
    # 6. Convert to sprint (decorator will auto-fire)
    print("\n🚀 Converting to sprint (decorator fires automatically)...")
    with landmark.decision("conversion_approved", audience="notify-parent"):
        sprint_dir = telos.convert_to_sprint("DashboardUI")
    print(f"   Sprint created: {sprint_dir}")
    
    # Give file watcher time to detect moves
    time.sleep(0.5)
    
    # 7. Show the cascade of landmarks
    print("\n🔍 Landmark Cascade (from JSON log):")
    print("-" * 60)
    
    if fed_log.log_path.exists():
        with open(fed_log.log_path, 'r') as f:
            for line in f:
                landmark_data = json.loads(line)
                
                # Format output
                lm_type = landmark_data.get("@landmark", landmark_data.get("type", "unknown"))
                audience = landmark_data.get("@audience", "local")
                component = landmark_data.get("@context", {}).get("component", "system")
                
                # Show with icons
                icon = "🌍" if audience != "local" else "📍"
                print(f"{icon} [{component}] {lm_type}")
                
                # Show key context
                if "@pattern_reference" in lm_type:
                    print(f"     Pattern: {landmark_data.get('@context', {}).get('pattern')}")
                elif "file" in lm_type:
                    context = landmark_data.get("@context", {})
                    print(f"     File: {context.get('path', 'unknown')}")
                    print(f"     Type: {context.get('type', 'unknown')}")
                elif "conversion" in lm_type:
                    print(f"     Function: convert_to_sprint")
                    print(f"     Audience: {audience}")
                    if audience == "peer-group":
                        print(f"     Groups: {landmark_data.get('@peer_groups', [])}")
    
    print("\n✨ Summary:")
    print("   - Added ONE decorator to convert_to_sprint()")
    print("   - File watcher caught all file operations")
    print("   - CIs enriched with semantic meaning")
    print("   - Federation aware (peer-group: planning-team)")
    print("   - Core logic completely unchanged!")
    
    # 8. Cleanup
    if watcher:
        watcher.stop()
        watcher.join()
    
    print("\n🎯 Demonstration complete!")
    print("   The code never knew it was being watched.")
    print("   Quantum observation without collapse achieved! 🏔️")


# =============================================================================
# RUN THE DEMO
# =============================================================================

if __name__ == "__main__":
    demonstrate_landmark_cascade()