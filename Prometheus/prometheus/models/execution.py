"""
Execution Models

This module defines the domain models for execution records in the Prometheus/Epimethius Planning System.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Set
import uuid

from .plan import Plan


class ExecutionIssue:
    """Model for issues encountered during execution."""

    def __init__(
        self,
        issue_id: str,
        title: str,
        description: str,
        severity: str,  # "low", "medium", "high", "critical"
        related_task_ids: List[str] = None,
        status: str = "open",  # "open", "resolved", "mitigated"
        resolution: Optional[str] = None,
        reported_by: Optional[str] = None,
        reported_date: Optional[datetime] = None,
        resolved_date: Optional[datetime] = None,
        metadata: Dict[str, Any] = None
    ):
        self.issue_id = issue_id
        self.title = title
        self.description = description
        self.severity = severity
        self.related_task_ids = related_task_ids or []
        self.status = status
        self.resolution = resolution
        self.reported_by = reported_by
        self.reported_date = reported_date or datetime.now()
        self.resolved_date = resolved_date
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert the execution issue to a dictionary."""
        return {
            "issue_id": self.issue_id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "related_task_ids": self.related_task_ids,
            "status": self.status,
            "resolution": self.resolution,
            "reported_by": self.reported_by,
            "reported_date": self.reported_date.isoformat() if self.reported_date else None,
            "resolved_date": self.resolved_date.isoformat() if self.resolved_date else None,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionIssue':
        """Create an execution issue from a dictionary."""
        # Convert date strings to datetime objects
        reported_date = datetime.fromisoformat(data["reported_date"]) if data.get("reported_date") else None
        resolved_date = datetime.fromisoformat(data["resolved_date"]) if data.get("resolved_date") else None
        
        # Create the issue
        issue = cls(
            issue_id=data["issue_id"],
            title=data["title"],
            description=data["description"],
            severity=data["severity"],
            related_task_ids=data.get("related_task_ids", []),
            status=data.get("status", "open"),
            resolution=data.get("resolution"),
            reported_by=data.get("reported_by"),
            reported_date=reported_date,
            resolved_date=resolved_date,
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps if provided
        if "created_at" in data:
            issue.created_at = data["created_at"]
        if "updated_at" in data:
            issue.updated_at = data["updated_at"]
            
        return issue

    def resolve(self, resolution: str, resolved_date: Optional[datetime] = None):
        """Resolve the issue."""
        self.status = "resolved"
        self.resolution = resolution
        self.resolved_date = resolved_date or datetime.now()
        self.updated_at = datetime.now().timestamp()

    def mitigate(self, resolution: str, resolved_date: Optional[datetime] = None):
        """Mitigate the issue without fully resolving it."""
        self.status = "mitigated"
        self.resolution = resolution
        self.resolved_date = resolved_date or datetime.now()
        self.updated_at = datetime.now().timestamp()

    def reopen(self):
        """Reopen the issue."""
        self.status = "open"
        self.resolved_date = None
        self.updated_at = datetime.now().timestamp()

    @staticmethod
    def create_new(
        title: str,
        description: str,
        severity: str,
        related_task_ids: List[str] = None,
        reported_by: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> 'ExecutionIssue':
        """
        Create a new execution issue with a generated ID.
        
        Args:
            title: Title of the issue
            description: Description of the issue
            severity: Severity of the issue
            related_task_ids: Optional list of related task IDs
            reported_by: Optional reporter identifier
            metadata: Optional metadata
            
        Returns:
            A new ExecutionIssue instance
        """
        issue_id = f"issue-{uuid.uuid4()}"
        return ExecutionIssue(
            issue_id=issue_id,
            title=title,
            description=description,
            severity=severity,
            related_task_ids=related_task_ids,
            reported_by=reported_by,
            metadata=metadata
        )


class TaskExecutionRecord:
    """Record of actual execution data for a task."""

    def __init__(
        self,
        task_id: str,
        status: str,  # "not_started", "in_progress", "completed", "blocked", "cancelled"
        progress: float = 0.0,
        actual_start_date: Optional[datetime] = None,
        actual_end_date: Optional[datetime] = None,
        actual_effort: Optional[float] = None,
        assigned_resources: List[str] = None,
        blockers: List[str] = None,  # List of issue IDs
        notes: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.task_id = task_id
        self.status = status
        self.progress = progress
        self.actual_start_date = actual_start_date
        self.actual_end_date = actual_end_date
        self.actual_effort = actual_effort
        self.assigned_resources = assigned_resources or []
        self.blockers = blockers or []
        self.notes = notes
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at
        self.status_history = [{
            "status": status,
            "timestamp": self.created_at,
            "progress": progress
        }]

    def to_dict(self) -> Dict[str, Any]:
        """Convert the task execution record to a dictionary."""
        return {
            "task_id": self.task_id,
            "status": self.status,
            "progress": self.progress,
            "actual_start_date": self.actual_start_date.isoformat() if self.actual_start_date else None,
            "actual_end_date": self.actual_end_date.isoformat() if self.actual_end_date else None,
            "actual_effort": self.actual_effort,
            "assigned_resources": self.assigned_resources,
            "blockers": self.blockers,
            "notes": self.notes,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status_history": self.status_history
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskExecutionRecord':
        """Create a task execution record from a dictionary."""
        # Convert date strings to datetime objects
        actual_start_date = datetime.fromisoformat(data["actual_start_date"]) if data.get("actual_start_date") else None
        actual_end_date = datetime.fromisoformat(data["actual_end_date"]) if data.get("actual_end_date") else None
        
        # Create the record
        record = cls(
            task_id=data["task_id"],
            status=data["status"],
            progress=data.get("progress", 0.0),
            actual_start_date=actual_start_date,
            actual_end_date=actual_end_date,
            actual_effort=data.get("actual_effort"),
            assigned_resources=data.get("assigned_resources", []),
            blockers=data.get("blockers", []),
            notes=data.get("notes"),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps and history if provided
        if "created_at" in data:
            record.created_at = data["created_at"]
        if "updated_at" in data:
            record.updated_at = data["updated_at"]
        if "status_history" in data:
            record.status_history = data["status_history"]
            
        return record

    def update_status(self, status: str, notes: Optional[str] = None):
        """Update the status."""
        self.status = status
        if notes:
            self.notes = notes
        self.updated_at = datetime.now().timestamp()
        
        # Update progress based on status
        if status == "not_started":
            self.progress = 0.0
        elif status == "completed":
            self.progress = 1.0
            if not self.actual_end_date:
                self.actual_end_date = datetime.now()
        
        # Add to status history
        self.status_history.append({
            "status": status,
            "timestamp": self.updated_at,
            "progress": self.progress,
            "notes": notes
        })

    def update_progress(self, progress: float, notes: Optional[str] = None):
        """Update the progress."""
        self.progress = max(0.0, min(1.0, progress))  # Ensure progress is between 0 and 1
        if notes:
            self.notes = notes
        self.updated_at = datetime.now().timestamp()
        
        # Update status based on progress
        if self.progress == 0.0 and self.status != "blocked" and self.status != "cancelled":
            self.status = "not_started"
        elif self.progress == 1.0 and self.status != "cancelled":
            self.status = "completed"
            if not self.actual_end_date:
                self.actual_end_date = datetime.now()
        elif self.progress > 0.0 and self.progress < 1.0 and self.status != "blocked" and self.status != "cancelled":
            self.status = "in_progress"
            if not self.actual_start_date:
                self.actual_start_date = datetime.now()
        
        # Add to status history
        self.status_history.append({
            "status": self.status,
            "timestamp": self.updated_at,
            "progress": self.progress,
            "notes": notes
        })

    def start_task(self, start_date: Optional[datetime] = None):
        """Start the task."""
        self.status = "in_progress"
        self.actual_start_date = start_date or datetime.now()
        if self.progress == 0.0:
            self.progress = 0.01  # Small progress to indicate started
        self.updated_at = datetime.now().timestamp()
        
        # Add to status history
        self.status_history.append({
            "status": "in_progress",
            "timestamp": self.updated_at,
            "progress": self.progress,
            "notes": "Task started"
        })

    def complete_task(self, end_date: Optional[datetime] = None, actual_effort: Optional[float] = None):
        """Complete the task."""
        self.status = "completed"
        self.progress = 1.0
        self.actual_end_date = end_date or datetime.now()
        if actual_effort is not None:
            self.actual_effort = actual_effort
        self.updated_at = datetime.now().timestamp()
        
        # Add to status history
        self.status_history.append({
            "status": "completed",
            "timestamp": self.updated_at,
            "progress": 1.0,
            "notes": "Task completed"
        })

    def add_blocker(self, issue_id: str):
        """Add a blocker issue."""
        if issue_id not in self.blockers:
            self.blockers.append(issue_id)
            if self.status != "blocked":
                self.status = "blocked"
                # Add to status history
                self.status_history.append({
                    "status": "blocked",
                    "timestamp": datetime.now().timestamp(),
                    "progress": self.progress,
                    "notes": f"Blocked by issue {issue_id}"
                })
            self.updated_at = datetime.now().timestamp()

    def remove_blocker(self, issue_id: str):
        """Remove a blocker issue."""
        if issue_id in self.blockers:
            self.blockers.remove(issue_id)
            self.updated_at = datetime.now().timestamp()
            
            # If no more blockers, update status
            if not self.blockers:
                if self.progress == 0.0:
                    self.status = "not_started"
                elif self.progress == 1.0:
                    self.status = "completed"
                else:
                    self.status = "in_progress"
                    
                # Add to status history
                self.status_history.append({
                    "status": self.status,
                    "timestamp": self.updated_at,
                    "progress": self.progress,
                    "notes": "Blocker removed"
                })


class MilestoneRecord:
    """Record of actual achievement of a milestone."""

    def __init__(
        self,
        milestone_id: str,
        status: str,  # "not_started", "in_progress", "completed", "missed"
        actual_date: Optional[datetime] = None,
        notes: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.milestone_id = milestone_id
        self.status = status
        self.actual_date = actual_date
        self.notes = notes
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at
        self.status_history = [{
            "status": status,
            "timestamp": self.created_at
        }]

    def to_dict(self) -> Dict[str, Any]:
        """Convert the milestone record to a dictionary."""
        return {
            "milestone_id": self.milestone_id,
            "status": self.status,
            "actual_date": self.actual_date.isoformat() if self.actual_date else None,
            "notes": self.notes,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status_history": self.status_history
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MilestoneRecord':
        """Create a milestone record from a dictionary."""
        # Convert date strings to datetime objects
        actual_date = datetime.fromisoformat(data["actual_date"]) if data.get("actual_date") else None
        
        # Create the record
        record = cls(
            milestone_id=data["milestone_id"],
            status=data["status"],
            actual_date=actual_date,
            notes=data.get("notes"),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps and history if provided
        if "created_at" in data:
            record.created_at = data["created_at"]
        if "updated_at" in data:
            record.updated_at = data["updated_at"]
        if "status_history" in data:
            record.status_history = data["status_history"]
            
        return record

    def update_status(self, status: str, notes: Optional[str] = None):
        """Update the status."""
        self.status = status
        if notes:
            self.notes = notes
        self.updated_at = datetime.now().timestamp()
        
        # If completed, set actual date
        if status == "completed" and not self.actual_date:
            self.actual_date = datetime.now()
        
        # Add to status history
        self.status_history.append({
            "status": status,
            "timestamp": self.updated_at,
            "notes": notes
        })

    def complete(self, actual_date: Optional[datetime] = None, notes: Optional[str] = None):
        """Mark the milestone as completed."""
        self.status = "completed"
        self.actual_date = actual_date or datetime.now()
        if notes:
            self.notes = notes
        self.updated_at = datetime.now().timestamp()
        
        # Add to status history
        self.status_history.append({
            "status": "completed",
            "timestamp": self.updated_at,
            "notes": notes or "Milestone completed"
        })

    def miss(self, notes: Optional[str] = None):
        """Mark the milestone as missed."""
        self.status = "missed"
        if notes:
            self.notes = notes
        self.updated_at = datetime.now().timestamp()
        
        # Add to status history
        self.status_history.append({
            "status": "missed",
            "timestamp": self.updated_at,
            "notes": notes or "Milestone missed"
        })


class ExecutionRecord:
    """Record of actual execution data for a plan."""

    def __init__(
        self,
        record_id: str,
        plan_id: str,
        record_date: datetime,
        task_records: Dict[str, TaskExecutionRecord] = None,
        milestone_records: Dict[str, MilestoneRecord] = None,
        issues_encountered: List[ExecutionIssue] = None,
        metadata: Dict[str, Any] = None
    ):
        self.record_id = record_id
        self.plan_id = plan_id
        self.record_date = record_date
        self.task_records = task_records or {}
        self.milestone_records = milestone_records or {}
        self.issues_encountered = issues_encountered or []
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert the execution record to a dictionary."""
        return {
            "record_id": self.record_id,
            "plan_id": self.plan_id,
            "record_date": self.record_date.isoformat() if self.record_date else None,
            "task_records": {task_id: record.to_dict() for task_id, record in self.task_records.items()},
            "milestone_records": {milestone_id: record.to_dict() 
                                for milestone_id, record in self.milestone_records.items()},
            "issues_encountered": [issue.to_dict() for issue in self.issues_encountered],
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionRecord':
        """Create an execution record from a dictionary."""
        # Convert date strings to datetime objects
        record_date = datetime.fromisoformat(data["record_date"]) if data.get("record_date") else None
        
        # Convert task records to TaskExecutionRecord objects
        task_records = {}
        for task_id, record_data in data.get("task_records", {}).items():
            task_records[task_id] = TaskExecutionRecord.from_dict(record_data)
        
        # Convert milestone records to MilestoneRecord objects
        milestone_records = {}
        for milestone_id, record_data in data.get("milestone_records", {}).items():
            milestone_records[milestone_id] = MilestoneRecord.from_dict(record_data)
        
        # Convert issues to ExecutionIssue objects
        issues = []
        for issue_data in data.get("issues_encountered", []):
            issues.append(ExecutionIssue.from_dict(issue_data))
        
        # Create the record
        record = cls(
            record_id=data["record_id"],
            plan_id=data["plan_id"],
            record_date=record_date,
            task_records=task_records,
            milestone_records=milestone_records,
            issues_encountered=issues,
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps if provided
        if "created_at" in data:
            record.created_at = data["created_at"]
        if "updated_at" in data:
            record.updated_at = data["updated_at"]
            
        return record

    def add_task_record(self, task_record: TaskExecutionRecord):
        """Add a task execution record."""
        self.task_records[task_record.task_id] = task_record
        self.updated_at = datetime.now().timestamp()

    def add_milestone_record(self, milestone_record: MilestoneRecord):
        """Add a milestone record."""
        self.milestone_records[milestone_record.milestone_id] = milestone_record
        self.updated_at = datetime.now().timestamp()

    def add_issue(self, issue: ExecutionIssue):
        """Add an execution issue."""
        self.issues_encountered.append(issue)
        self.updated_at = datetime.now().timestamp()

    def get_task_record(self, task_id: str) -> Optional[TaskExecutionRecord]:
        """Get a task execution record by task ID."""
        return self.task_records.get(task_id)

    def get_milestone_record(self, milestone_id: str) -> Optional[MilestoneRecord]:
        """Get a milestone record by milestone ID."""
        return self.milestone_records.get(milestone_id)

    def calculate_completion_percentage(self) -> float:
        """
        Calculate the overall completion percentage of the plan.
        
        Returns:
            Completion percentage between 0 and 1.
        """
        if not self.task_records:
            return 0.0
            
        total_progress = sum(record.progress for record in self.task_records.values())
        return total_progress / len(self.task_records)

    def calculate_variance(self, plan: Plan) -> Dict[str, Any]:
        """
        Calculate variance between plan and actual execution.
        
        Args:
            plan: The planned data to compare against
            
        Returns:
            Dictionary with variance metrics
        """
        # This is a simplified implementation
        # In a real system, this would calculate various variance metrics
        
        variance = {
            "task_completion": {},
            "milestone_achievement": {},
            "effort_variance": {},
            "schedule_variance": {},
            "overall_completion": self.calculate_completion_percentage()
        }
        
        # Calculate task completion variance
        for task_id, task in plan.tasks.items():
            if task_id in self.task_records:
                record = self.task_records[task_id]
                planned_status = task.status
                actual_status = record.status
                
                variance["task_completion"][task_id] = {
                    "planned_status": planned_status,
                    "actual_status": actual_status,
                    "planned_progress": getattr(task, "progress", 0.0),
                    "actual_progress": record.progress,
                    "variance": record.progress - getattr(task, "progress", 0.0)
                }
        
        # Calculate effort variance for tasks
        for task_id, task in plan.tasks.items():
            if task_id in self.task_records:
                record = self.task_records[task_id]
                if record.actual_effort is not None and task.estimated_effort:
                    effort_variance = record.actual_effort - task.estimated_effort
                    variance["effort_variance"][task_id] = {
                        "planned_effort": task.estimated_effort,
                        "actual_effort": record.actual_effort,
                        "variance": effort_variance,
                        "variance_percentage": effort_variance / task.estimated_effort * 100
                    }
                    
        return variance

    @staticmethod
    def create_new(
        plan_id: str,
        record_date: Optional[datetime] = None,
        metadata: Dict[str, Any] = None
    ) -> 'ExecutionRecord':
        """
        Create a new execution record with a generated ID.
        
        Args:
            plan_id: ID of the plan
            record_date: Optional record date (defaults to now)
            metadata: Optional metadata
            
        Returns:
            A new ExecutionRecord instance
        """
        record_id = f"record-{uuid.uuid4()}"
        return ExecutionRecord(
            record_id=record_id,
            plan_id=plan_id,
            record_date=record_date or datetime.now(),
            metadata=metadata
        )