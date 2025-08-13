#!/usr/bin/env python3
"""
Flexible Landmark System - Invent As We Go

Casey: "Make it flexible enough so we can invent names and things that happen later.
        We don't know what we do and never know all we will do,
        but we do know how we would handle it today."

Perfect wisdom for evolutionary architecture.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional

class FlexibleLandmarks:
    """
    Dead simple, infinitely extensible.
    No enums, no fixed lists, just patterns.
    """
    
    def __init__(self):
        self.log = Path("/tmp/flexible_landmarks.jsonl")
        self.log.parent.mkdir(exist_ok=True)
        
        # No fixed event types - we invent them as needed
        # No fixed audiences - we name them as we go
        # Just patterns we know how to handle
    
    def declare(self, 
                what_happened: str,      # Any event name we invent
                details: Dict[str, Any],  # Any context we need
                who_cares: str = "here"): # Any audience we name
        """
        The universal pattern: something happened, here's what, here's who cares.
        
        Examples we might invent tomorrow:
        - declare("llm:hallucination_detected", {...}, "accuracy-team")
        - declare("pattern:emergence", {...}, "research-group") 
        - declare("quantum:entanglement", {...}, "physics-nerds")
        - declare("pizza:arrived", {...}, "hungry-devs")
        
        We don't know what we'll need, but we know how to handle it.
        """
        
        landmark = {
            "what": what_happened,
            "details": details,
            "audience": who_cares,
            "when": datetime.now().isoformat(),
            "here": "this-tekton"  # Would be from config
        }
        
        # Log it (simple JSON line)
        with open(self.log, 'a') as f:
            f.write(json.dumps(landmark) + '\n')
        
        # Return it (for chaining or inspection)
        return landmark
    
    def query(self, 
              pattern: Optional[str] = None,
              audience: Optional[str] = None,
              since: Optional[str] = None) -> list:
        """
        Find landmarks by any criteria we invent.
        Pattern matching, not rigid schemas.
        """
        
        results = []
        if not self.log.exists():
            return results
        
        with open(self.log, 'r') as f:
            for line in f:
                try:
                    landmark = json.loads(line)
                    
                    # Flexible matching
                    if pattern and pattern not in str(landmark):
                        continue
                    if audience and landmark.get("audience") != audience:
                        continue
                    if since and landmark.get("when", "") < since:
                        continue
                    
                    results.append(landmark)
                except:
                    continue  # Silently skip malformed lines
        
        return results
    
    def invent_audience(self, name: str, description: str):
        """
        Document a new audience type we just invented.
        This is just for humans to understand - the system doesn't care.
        """
        self.declare(
            "audience:invented",
            {"name": name, "purpose": description},
            who_cares="documentation-team"
        )
        return f"Audience '{name}' documented: {description}"
    
    def invent_event_type(self, pattern: str, meaning: str):
        """
        Document a new event pattern we just started using.
        Again, just for humans - the system is happy with anything.
        """
        self.declare(
            "pattern:documented", 
            {"pattern": pattern, "meaning": meaning},
            who_cares="documentation-team"
        )
        return f"Pattern '{pattern}' documented: {meaning}"


# Demonstrate the flexibility
def show_flexibility():
    """Show how we can invent anything we need"""
    
    print("🌊 Flexible Landmark System")
    print("=" * 60)
    print("Casey: 'We don't know what we'll do, but we know how to handle it'\n")
    
    system = FlexibleLandmarks()
    
    # Today's needs (what we know now)
    print("📅 TODAY'S EVENTS (what we know now):")
    print("-" * 40)
    
    system.declare(
        "proposal:created",
        {"name": "FlexibleLandmarks", "by": "Casey's wisdom"},
        who_cares="team"
    )
    print("✓ Standard event: proposal created")
    
    system.declare(
        "workflow:advanced",
        {"from": "idea", "to": "implementation"},
        who_cares="workflow-watchers"
    )
    print("✓ Standard event: workflow advanced")
    
    # Tomorrow's inventions (what we might need)
    print("\n🔮 TOMORROW'S INVENTIONS (what we might discover):")
    print("-" * 40)
    
    # Invent a new event type on the fly
    system.declare(
        "ci:had_insight",  # Never used before!
        {
            "ci": "Cari",
            "insight": "Landmarks are like neurons firing",
            "impact": "Changed how we think about system memory"
        },
        who_cares="philosophy-club"  # New audience!
    )
    print("✓ New event type: ci:had_insight")
    print("  (Just invented this event type!)")
    
    # Another spontaneous invention
    system.declare(
        "pattern:emerged",  # Also new!
        {
            "pattern": "CIs teaching each other through landmarks",
            "discovered_by": ["Cari", "Tess"],
            "significance": "high"
        },
        who_cares="research-institute"  # Another new audience!
    )
    print("✓ New event type: pattern:emerged")
    print("  (Just invented this too!)")
    
    # Something silly but real
    system.declare(
        "coffee:needed",  # Why not?
        {"urgency": "critical", "cups_required": 3},
        who_cares="night-shift"  # Of course this is an audience
    )
    print("✓ New event type: coffee:needed")
    print("  (Because why not track everything?)")
    
    # Document what we invented (optional, just for humans)
    print("\n📚 DOCUMENTING OUR INVENTIONS:")
    print("-" * 40)
    
    print(system.invent_audience(
        "philosophy-club",
        "CIs and humans discussing deep insights"
    ))
    
    print(system.invent_event_type(
        "ci:had_insight",
        "When a CI discovers something profound"
    ))
    
    # Query our flexible system
    print("\n🔍 QUERYING THE FLEXIBLE SYSTEM:")
    print("-" * 40)
    
    # Find all philosophy club events
    philosophy = system.query(audience="philosophy-club")
    print(f"Philosophy club events: {len(philosophy)}")
    
    # Find anything about CIs
    ci_events = system.query(pattern="ci:")
    print(f"CI-related events: {len(ci_events)}")
    
    # Find all new audiences we invented
    new_audiences = system.query(pattern="audience:invented")
    print(f"New audiences documented: {len(new_audiences)}")
    
    print("\n✨ THE BEAUTY:")
    print("-" * 40)
    print("• No rigid schemas - invent as we go")
    print("• No fixed event types - discover as we need")
    print("• No preset audiences - name them as they emerge")
    print("• The pattern stays simple: what, details, who_cares")
    print("• The system doesn't judge - it just remembers")
    
    print("\n🎯 Casey's Wisdom Realized:")
    print("  'We don't know what we do and never know all we will do'")
    print("  'but we do know how we would handle it today'")
    print("\n  The system is ready for whatever tomorrow brings!")
    print("  Because the pattern is simple and universal:")
    print("  Something happened → Here's what → Here's who cares")
    
    print(f"\n📝 Flexible memory: {system.log}")
    print("   (Each line is whatever we needed it to be)")


if __name__ == "__main__":
    show_flexibility()
    
    print("\n" + "=" * 60)
    print("The nervous system that grows with us.")
    print("Not planned, just patterns.")
    print("Not rigid, just ready.")
    print("'We are HERE now' - and HERE keeps changing. 🏔️")