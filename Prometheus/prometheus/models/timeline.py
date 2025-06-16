"""
Timeline Models

This module defines the domain models for timelines in the Prometheus/Epimethius Planning System.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
import uuid
from pydantic import Field
from tekton.models.base import TektonBaseModel


class TimelineEvent(TektonBaseModel):
    """Event on a timeline representing a significant occurrence or action."""
    event_id: str = Field(default_factory=lambda: f"event-{uuid.uuid4()}")
    entry_id: Optional[str] = None  # Associated timeline entry, if any
    event_type: str  # "start", "end", "milestone_reached", "delay", "update", etc.
    timestamp: datetime = Field(default_factory=datetime.now)
    description: str
    actor: Optional[str] = None  # Who/what triggered the event
    impact: Optional[str] = None  # "high", "medium", "low", "none"
    metadata: Dict[str, Any] = Field(default_factory=dict)



class TimelineEntry:
    """Timeline entry representing a scheduled task or milestone."""

    def __init__(
        self,
        entry_id: str,
        entity_id: str,  # Task ID or milestone ID
        entity_type: str,  # "task" or "milestone"
        start_date: datetime,
        end_date: datetime,
        status: str = "scheduled",  # "scheduled", "in_progress", "completed", "delayed"
        dependencies: List[str] = None,  # IDs of entries this entry depends on
        metadata: Dict[str, Any] = None
    ):
        self.entry_id = entry_id
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.dependencies = dependencies or []
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert the timeline entry to a dictionary."""
        return {
            "entry_id": self.entry_id,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "status": self.status,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimelineEntry':
        """Create a timeline entry from a dictionary."""
        # Convert date strings to datetime objects
        start_date = datetime.fromisoformat(data["start_date"]) if data.get("start_date") else None
        end_date = datetime.fromisoformat(data["end_date"]) if data.get("end_date") else None
        
        # Create the entry
        entry = cls(
            entry_id=data["entry_id"],
            entity_id=data["entity_id"],
            entity_type=data["entity_type"],
            start_date=start_date,
            end_date=end_date,
            status=data.get("status", "scheduled"),
            dependencies=data.get("dependencies", []),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps if provided
        if "created_at" in data:
            entry.created_at = data["created_at"]
        if "updated_at" in data:
            entry.updated_at = data["updated_at"]
            
        return entry

    def update_dates(self, start_date: datetime, end_date: datetime):
        """Update the start and end dates."""
        self.start_date = start_date
        self.end_date = end_date
        self.updated_at = datetime.now().timestamp()

    def update_status(self, status: str):
        """Update the status."""
        self.status = status
        self.updated_at = datetime.now().timestamp()

    def add_dependency(self, entry_id: str):
        """Add a dependency."""
        if entry_id not in self.dependencies:
            self.dependencies.append(entry_id)
            self.updated_at = datetime.now().timestamp()

    def remove_dependency(self, entry_id: str) -> bool:
        """Remove a dependency."""
        if entry_id in self.dependencies:
            self.dependencies.remove(entry_id)
            self.updated_at = datetime.now().timestamp()
            return True
        return False

    def duration_days(self) -> int:
        """Calculate the duration in days."""
        if not self.start_date or not self.end_date:
            return 0
        return (self.end_date - self.start_date).days + 1  # Including both start and end day

    @staticmethod
    def create_new(
        entity_id: str,
        entity_type: str,
        start_date: datetime,
        end_date: datetime,
        status: str = "scheduled",
        dependencies: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> 'TimelineEntry':
        """
        Create a new timeline entry with a generated ID.
        
        Args:
            entity_id: ID of the entity (task or milestone)
            entity_type: Type of the entity ("task" or "milestone")
            start_date: Start date
            end_date: End date
            status: Status of the entry
            dependencies: Optional list of dependency entry IDs
            metadata: Optional metadata
            
        Returns:
            A new TimelineEntry instance
        """
        entry_id = f"entry-{uuid.uuid4()}"
        return TimelineEntry(
            entry_id=entry_id,
            entity_id=entity_id,
            entity_type=entity_type,
            start_date=start_date,
            end_date=end_date,
            status=status,
            dependencies=dependencies,
            metadata=metadata
        )


class Timeline:
    """Timeline model representing the schedule for a plan."""

    def __init__(
        self,
        timeline_id: str,
        plan_id: str,
        entries: Dict[str, TimelineEntry] = None,
        critical_path: List[str] = None,  # List of entry IDs in the critical path
        metadata: Dict[str, Any] = None
    ):
        self.timeline_id = timeline_id
        self.plan_id = plan_id
        self.entries = entries or {}
        self.critical_path = critical_path or []
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at
        self.version = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert the timeline to a dictionary."""
        return {
            "timeline_id": self.timeline_id,
            "plan_id": self.plan_id,
            "entries": {entry_id: entry.to_dict() for entry_id, entry in self.entries.items()},
            "critical_path": self.critical_path,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Timeline':
        """Create a timeline from a dictionary."""
        # Convert entries to TimelineEntry objects
        entries = {}
        for entry_id, entry_data in data.get("entries", {}).items():
            entries[entry_id] = TimelineEntry.from_dict(entry_data)
        
        # Create the timeline
        timeline = cls(
            timeline_id=data["timeline_id"],
            plan_id=data["plan_id"],
            entries=entries,
            critical_path=data.get("critical_path", []),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps and version if provided
        if "created_at" in data:
            timeline.created_at = data["created_at"]
        if "updated_at" in data:
            timeline.updated_at = data["updated_at"]
        if "version" in data:
            timeline.version = data["version"]
            
        return timeline

    def update_version(self):
        """Update the timeline version and updated_at timestamp."""
        self.version += 1
        self.updated_at = datetime.now().timestamp()

    def add_entry(self, entry: TimelineEntry):
        """Add an entry to the timeline."""
        self.entries[entry.entry_id] = entry
        self.update_version()

    def remove_entry(self, entry_id: str) -> bool:
        """Remove an entry from the timeline."""
        if entry_id in self.entries:
            del self.entries[entry_id]
            # Remove this entry from dependency lists
            for entry in self.entries.values():
                if entry_id in entry.dependencies:
                    entry.dependencies.remove(entry_id)
            # Remove this entry from critical path if present
            if entry_id in self.critical_path:
                self.critical_path.remove(entry_id)
            self.update_version()
            return True
        return False

    def get_entry(self, entry_id: str) -> Optional[TimelineEntry]:
        """Get an entry by ID."""
        return self.entries.get(entry_id)

    def get_entry_by_entity(self, entity_id: str, entity_type: str) -> Optional[TimelineEntry]:
        """Get an entry by entity ID and type."""
        for entry in self.entries.values():
            if entry.entity_id == entity_id and entry.entity_type == entity_type:
                return entry
        return None

    def update_entry(self, entry: TimelineEntry) -> bool:
        """Update an entry in the timeline."""
        if entry.entry_id in self.entries:
            self.entries[entry.entry_id] = entry
            self.update_version()
            return True
        return False

    def update_critical_path(self, critical_path: List[str]):
        """Update the critical path."""
        self.critical_path = critical_path
        self.update_version()

    def calculate_critical_path(self) -> List[str]:
        """
        Calculate the critical path of the timeline.
        
        Returns:
            List of entry IDs in the critical path.
        """
        # This is a placeholder for the critical path calculation
        # In a real implementation, this would use a graph algorithm
        # to find the longest path from start to end
        
        # For now, we'll return a simple implementation
        if not self.entries:
            return []
            
        # Find all entries with no dependencies
        start_entries = [entry_id for entry_id, entry in self.entries.items() if not entry.dependencies]
        
        # If no start entries, return empty list
        if not start_entries:
            return []
            
        # Find all entries with no dependents
        end_entries = set(self.entries.keys())
        for entry in self.entries.values():
            for dep in entry.dependencies:
                if dep in end_entries:
                    end_entries.remove(dep)
        
        # If no end entries, return empty list
        if not end_entries:
            return []
            
        # For simplicity, just return a path from the first start to the first end
        # In a real implementation, we would calculate the critical path properly
        self.critical_path = [start_entries[0], list(end_entries)[0]]
        return self.critical_path

    def get_start_date(self) -> Optional[datetime]:
        """Get the earliest start date in the timeline."""
        if not self.entries:
            return None
        return min((entry.start_date for entry in self.entries.values() if entry.start_date), default=None)

    def get_end_date(self) -> Optional[datetime]:
        """Get the latest end date in the timeline."""
        if not self.entries:
            return None
        return max((entry.end_date for entry in self.entries.values() if entry.end_date), default=None)

    def get_duration_days(self) -> int:
        """Get the total duration of the timeline in days."""
        start_date = self.get_start_date()
        end_date = self.get_end_date()
        if not start_date or not end_date:
            return 0
        return (end_date - start_date).days + 1  # Including both start and end day

    @staticmethod
    def create_new(plan_id: str, metadata: Dict[str, Any] = None) -> 'Timeline':
        """
        Create a new timeline with a generated ID.
        
        Args:
            plan_id: ID of the plan
            metadata: Optional metadata
            
        Returns:
            A new Timeline instance
        """
        timeline_id = f"timeline-{uuid.uuid4()}"
        return Timeline(
            timeline_id=timeline_id,
            plan_id=plan_id,
            metadata=metadata
        )