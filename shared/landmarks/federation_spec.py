#!/usr/bin/env python3
"""
Federation Landmark Sharing Specification

Distributed landmark system for Tekton federations.
Simple JSON logs that can ripple through hierarchies or peer groups.
"""

from enum import Enum
from typing import List, Dict, Optional
from pathlib import Path
import json
from datetime import datetime

class LandmarkAudience(Enum):
    """Who should see this landmark?"""
    
    # Local levels
    LOCAL = "local"                      # This Tekton instance only
    COMPONENT = "component"               # This component and its CIs
    
    # Hierarchical levels  
    NOTIFY_PARENT = "notify-parent"      # Local + parent Tekton
    NOTIFY_CHILDREN = "notify-children"  # Local + child Tektons
    BROADCAST_TREE = "broadcast-tree"    # Entire hierarchy tree
    
    # Peer group levels
    PEER_GROUP = "peer-group"            # Named peer group
    SPECIALIST = "specialist"            # Specialist network (UI, planning, etc)
    
    # Global levels
    FEDERATION = "federation"            # All connected Tektons
    PUBLIC = "public"                    # Available to any system


class FederationLandmark:
    """Landmark with federation awareness"""
    
    def __init__(self, 
                 landmark_type: str,
                 context: Dict,
                 audience: LandmarkAudience = LandmarkAudience.LOCAL,
                 peer_groups: List[str] = None):
        
        self.type = landmark_type
        self.context = context
        self.audience = audience
        self.peer_groups = peer_groups or []
        self.timestamp = datetime.now().isoformat()
        self.origin = self._get_origin()
    
    def _get_origin(self) -> Dict:
        """Identify where this landmark came from"""
        return {
            "tekton_id": "tekton-alpha",  # Would be from config
            "instance": "production",
            "region": "us-west",
            "component": self.context.get("component", "unknown")
        }
    
    def to_json(self) -> Dict:
        """Convert to JSON for logging/sharing"""
        return {
            "@landmark": self.type,
            "@audience": self.audience.value,
            "@peer_groups": self.peer_groups,
            "@origin": self.origin,
            "@timestamp": self.timestamp,
            "@context": self.context
        }
    
    def should_share_with(self, other_tekton: Dict) -> bool:
        """Determine if this landmark should be shared with another Tekton"""
        
        if self.audience == LandmarkAudience.LOCAL:
            return False
            
        if self.audience == LandmarkAudience.FEDERATION:
            return True
            
        if self.audience == LandmarkAudience.NOTIFY_PARENT:
            return other_tekton.get("role") == "parent"
            
        if self.audience == LandmarkAudience.NOTIFY_CHILDREN:
            return other_tekton.get("role") == "child"
            
        if self.audience == LandmarkAudience.PEER_GROUP:
            # Check if other Tekton is in any of our peer groups
            their_groups = other_tekton.get("peer_groups", [])
            return any(group in their_groups for group in self.peer_groups)
        
        return False


class FederationLandmarkLog:
    """JSON log with federation capabilities"""
    
    def __init__(self, log_path: Path = Path("/tmp/tekton_landmarks.jsonl")):
        self.log_path = log_path
        self.federation_config = self._load_federation_config()
    
    def _load_federation_config(self) -> Dict:
        """Load federation configuration from 'till' or config"""
        # This would load from actual config
        return {
            "tekton_id": "tekton-alpha",
            "parent": "tekton-prime",
            "children": ["tekton-beta", "tekton-gamma"],
            "peer_groups": ["ui-specialists", "west-coast-cluster"],
            "sharing": {
                "upstream_endpoint": "https://parent.tekton/landmarks",
                "downstream_endpoints": [],
                "peer_endpoints": []
            }
        }
    
    def log(self, landmark: FederationLandmark):
        """Log landmark locally and share if needed"""
        
        # Always log locally
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(landmark.to_json()) + '\n')
        
        # Share based on audience
        self._share_landmark(landmark)
    
    def _share_landmark(self, landmark: FederationLandmark):
        """Share landmark with appropriate audience"""
        
        if landmark.audience == LandmarkAudience.LOCAL:
            return  # Don't share
        
        # Determine recipients
        recipients = self._get_recipients(landmark)
        
        # Queue for sharing (async in production)
        for recipient in recipients:
            self._queue_for_sharing(landmark, recipient)
    
    def _get_recipients(self, landmark: FederationLandmark) -> List[str]:
        """Determine who should receive this landmark"""
        recipients = []
        
        if landmark.audience == LandmarkAudience.NOTIFY_PARENT:
            recipients.append(self.federation_config["parent"])
            
        elif landmark.audience == LandmarkAudience.NOTIFY_CHILDREN:
            recipients.extend(self.federation_config["children"])
            
        elif landmark.audience == LandmarkAudience.FEDERATION:
            # Would query federation registry
            recipients.append("all")
            
        elif landmark.audience == LandmarkAudience.PEER_GROUP:
            # Would query peer group members
            for group in landmark.peer_groups:
                recipients.extend(self._get_peer_group_members(group))
        
        return recipients
    
    def _get_peer_group_members(self, group: str) -> List[str]:
        """Get members of a peer group"""
        # This would query 'till' or federation registry
        groups = {
            "ui-specialists": ["tekton-ui-1", "tekton-ui-2"],
            "planning-team": ["tekton-plan-1", "tekton-plan-2"],
            "west-coast-cluster": ["tekton-sf", "tekton-la", "tekton-sea"]
        }
        return groups.get(group, [])
    
    def _queue_for_sharing(self, landmark: FederationLandmark, recipient: str):
        """Queue landmark for sharing (would be async)"""
        print(f"  📡 Queued landmark for {recipient}: {landmark.type}")
    
    def receive_landmark(self, landmark_json: Dict) -> bool:
        """Receive landmark from another Tekton"""
        
        # Validate origin
        if not self._validate_origin(landmark_json.get("@origin")):
            return False
        
        # Check if we should accept based on our config
        if not self._should_accept(landmark_json):
            return False
        
        # Log with federation prefix
        landmark_json["@federated"] = True
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(landmark_json) + '\n')
        
        # Trigger local CI attention if relevant
        self._notify_local_cis(landmark_json)
        
        return True
    
    def _validate_origin(self, origin: Dict) -> bool:
        """Validate landmark came from trusted source"""
        # Would check against federation registry
        return True
    
    def _should_accept(self, landmark_json: Dict) -> bool:
        """Determine if we should accept this landmark"""
        # Check audience and peer groups
        audience = landmark_json.get("@audience")
        
        if audience == "federation":
            return True
            
        if audience == "peer-group":
            our_groups = self.federation_config.get("peer_groups", [])
            their_groups = landmark_json.get("@peer_groups", [])
            return any(group in our_groups for group in their_groups)
        
        return False
    
    def _notify_local_cis(self, landmark_json: Dict):
        """Notify local CIs about federated landmark"""
        if "@pattern_discovered" in landmark_json.get("@landmark", ""):
            print(f"  🔔 Notifying local CIs about federated pattern discovery")


# =============================================================================
# Usage Examples
# =============================================================================

def example_local_landmark():
    """Landmark that stays local"""
    landmark = FederationLandmark(
        "proposal_created",
        {"name": "LocalDashboard"},
        audience=LandmarkAudience.LOCAL
    )
    return landmark


def example_notify_parent():
    """Landmark that notifies parent Tekton"""
    landmark = FederationLandmark(
        "pattern_discovered",
        {"pattern": "new_ui_approach", "component": "telos"},
        audience=LandmarkAudience.NOTIFY_PARENT
    )
    return landmark


def example_peer_group_share():
    """Landmark shared with peer group"""
    landmark = FederationLandmark(
        "complexity_flag",
        {"area": "ui_rendering", "level": "high"},
        audience=LandmarkAudience.PEER_GROUP,
        peer_groups=["ui-specialists"]
    )
    return landmark


def example_federation_broadcast():
    """Major landmark for entire federation"""
    landmark = FederationLandmark(
        "breakthrough_discovery",
        {"discovery": "new_optimization", "impact": "50% faster"},
        audience=LandmarkAudience.FEDERATION
    )
    return landmark


if __name__ == "__main__":
    print("🌐 Federation Landmark Examples\n")
    
    log = FederationLandmarkLog()
    
    # Local landmark (stays here)
    local = example_local_landmark()
    print(f"Local: {local.type}")
    log.log(local)
    
    # Notify parent
    parent = example_notify_parent()
    print(f"To Parent: {parent.type}")
    log.log(parent)
    
    # Share with peer group
    peers = example_peer_group_share()
    print(f"To Peers: {peers.type}")
    log.log(peers)
    
    # Broadcast to federation
    broadcast = example_federation_broadcast()
    print(f"To Federation: {broadcast.type}")
    log.log(broadcast)
    
    print(f"\n📝 Logged to: {log.log_path}")