#!/usr/bin/env python3
"""
'till' - Simple Configuration for "Who Needs to Know"

Just 'here' and 'everything else'.
Names are arbitrary, like labeling security cameras.
"""

from typing import Set, Dict, List
from pathlib import Path
import json

class Till:
    """Configuration for who needs to know about landmarks"""
    
    def __init__(self):
        # Simple: just 'here' and groups we care about
        self.here = "tekton-alpha"
        self.audiences = {
            "here": {"tekton-alpha"},  # Just this instance
            
            # Arbitrary names for "who needs to know"
            "planning-team": {"tekton-plan-1", "tekton-plan-2", "tekton-alpha"},
            "ui-folks": {"tekton-ui", "tekton-ux", "tekton-alpha"},
            "everyone": {"*"},  # Broadcast
            
            # Key events Casey wants to know about
            "workflow-watchers": {"tekton-alpha", "tekton-monitor"},  # Workflow progress
            "birth-announcements": {"*"},  # New components born
            "obituaries": {"*"},  # Things voted off the island
        }
    
    def who_needs_to_know(self, audience: str) -> Set[str]:
        """Return who should hear about this"""
        return self.audiences.get(audience, {"here"})
    
    def should_i_care(self, landmark: Dict) -> bool:
        """Should this instance care about this landmark?"""
        audience = landmark.get("audience", "here")
        recipients = self.who_needs_to_know(audience)
        
        return (
            self.here in recipients or 
            "*" in recipients or
            audience == "here"
        )


# The actual living nervous system - landmarks flowing
class LivingLandmarks:
    """The living, breathing nervous system of landmarks"""
    
    def __init__(self, till: Till):
        self.till = till
        self.memory = []  # Simple list of everything we've seen
    
    def fire(self, event_type: str, context: Dict, audience: str = "here"):
        """Fire a landmark - nature saying 'We are HERE now'"""
        
        landmark = {
            "type": event_type,
            "context": context,
            "audience": audience,
            "from": self.till.here,
            "when": "now"  # We are HERE now
        }
        
        # Always remember locally
        self.memory.append(landmark)
        
        # Share with those who need to know
        recipients = self.till.who_needs_to_know(audience)
        
        # Log what's happening
        if recipients != {"here"}:
            print(f"🏔️ {event_type} → {audience}: {recipients}")
        else:
            print(f"📍 {event_type} (local)")
        
        return landmark
    
    def workflow_moved(self, from_state: str, to_state: str):
        """Machine moving along workflow"""
        self.fire(
            "workflow_transition",
            {"from": from_state, "to": to_state},
            audience="workflow-watchers"
        )
    
    def component_born(self, component: str):
        """New component birthed"""
        self.fire(
            "component_created",
            {"name": component, "proud_parent": self.till.here},
            audience="birth-announcements"
        )
    
    def voted_off_island(self, component: str, reason: str = "deprecated"):
        """Something removed/deprecated"""
        self.fire(
            "component_removed", 
            {"name": component, "reason": reason},
            audience="obituaries"
        )


# Simple demonstration
if __name__ == "__main__":
    print("🌱 'till' and Living Landmarks Demo")
    print("=" * 50)
    print("'till' is just configuration: who needs to know")
    print("Landmarks are alive: the actual nervous system\n")
    
    # Setup
    till = Till()
    landmarks = LivingLandmarks(till)
    
    # Key events Casey wants to know about
    
    print("1. Workflow Progress:")
    landmarks.workflow_moved("proposal", "sprint")
    landmarks.workflow_moved("sprint", "building")
    
    print("\n2. Component Birth:")
    landmarks.component_born("NewDashboard")
    
    print("\n3. Voted Off the Island:")
    landmarks.voted_off_island("OldLegacyModule", reason="replaced by NewDashboard")
    
    print("\n4. Local Event (just here):")
    landmarks.fire("cache_cleared", {"size": "2GB"}, audience="here")
    
    print("\n📝 Living Memory:")
    print(f"   {len(landmarks.memory)} landmarks captured")
    print("\n🔍 Recent landmarks:")
    for lm in landmarks.memory[-3:]:
        print(f"   - {lm['type']}: {lm['audience']}")
    
    print("\n✨ Nature just says: We are HERE now.")