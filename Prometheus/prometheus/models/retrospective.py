"""
Retrospective Models

This module defines the domain models for retrospectives in the Prometheus/Epimethius Planning System.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Set
import uuid

from shared.debug.debug_utils import debug_log, log_function


class RetroItem:
    """Model for an item in a retrospective."""

    def __init__(
        self,
        item_id: str,
        content: str,
        category: str,  # e.g., "what_went_well", "what_didnt_go_well", "action_item"
        votes: int = 0,
        author: Optional[str] = None,
        related_task_ids: List[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.item_id = item_id
        self.content = content
        self.category = category
        self.votes = votes
        self.author = author
        self.related_task_ids = related_task_ids or []
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert the retrospective item to a dictionary."""
        return {
            "item_id": self.item_id,
            "content": self.content,
            "category": self.category,
            "votes": self.votes,
            "author": self.author,
            "related_task_ids": self.related_task_ids,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RetroItem':
        """Create a retrospective item from a dictionary."""
        item = cls(
            item_id=data["item_id"],
            content=data["content"],
            category=data["category"],
            votes=data.get("votes", 0),
            author=data.get("author"),
            related_task_ids=data.get("related_task_ids", []),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps if provided
        if "created_at" in data:
            item.created_at = data["created_at"]
        if "updated_at" in data:
            item.updated_at = data["updated_at"]
            
        return item

    def add_vote(self):
        """Add a vote for this item."""
        self.votes += 1
        self.updated_at = datetime.now().timestamp()

    def remove_vote(self) -> bool:
        """Remove a vote from this item."""
        if self.votes > 0:
            self.votes -= 1
            self.updated_at = datetime.now().timestamp()
            return True
        return False

    def update_content(self, content: str):
        """Update the content of the item."""
        self.content = content
        self.updated_at = datetime.now().timestamp()

    def update_category(self, category: str):
        """Update the category of the item."""
        self.category = category
        self.updated_at = datetime.now().timestamp()

    @staticmethod
    def create_new(
        content: str,
        category: str,
        author: Optional[str] = None,
        related_task_ids: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> 'RetroItem':
        """
        Create a new retrospective item with a generated ID.
        
        Args:
            content: Content of the item
            category: Category of the item
            author: Optional author identifier
            related_task_ids: Optional list of related task IDs
            metadata: Optional metadata
            
        Returns:
            A new RetroItem instance
        """
        item_id = f"retro-item-{uuid.uuid4()}"
        return RetroItem(
            item_id=item_id,
            content=content,
            category=category,
            author=author,
            related_task_ids=related_task_ids,
            metadata=metadata
        )


class ActionItem:
    """Model for an action item from a retrospective."""

    def __init__(
        self,
        action_id: str,
        title: str,
        description: str,
        assignees: List[str] = None,
        due_date: Optional[datetime] = None,
        status: str = "open",  # "open", "in_progress", "completed", "cancelled"
        priority: str = "medium",  # "low", "medium", "high", "critical"
        related_retro_items: List[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.action_id = action_id
        self.title = title
        self.description = description
        self.assignees = assignees or []
        self.due_date = due_date
        self.status = status
        self.priority = priority
        self.related_retro_items = related_retro_items or []
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at
        self.completed_at = None
        self.status_history = [{
            "status": status,
            "timestamp": self.created_at
        }]

    def to_dict(self) -> Dict[str, Any]:
        """Convert the action item to a dictionary."""
        return {
            "action_id": self.action_id,
            "title": self.title,
            "description": self.description,
            "assignees": self.assignees,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "status": self.status,
            "priority": self.priority,
            "related_retro_items": self.related_retro_items,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "status_history": self.status_history
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActionItem':
        """Create an action item from a dictionary."""
        # Convert date strings to datetime objects
        due_date = datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None
        
        # Create the action item
        action = cls(
            action_id=data["action_id"],
            title=data["title"],
            description=data["description"],
            assignees=data.get("assignees", []),
            due_date=due_date,
            status=data.get("status", "open"),
            priority=data.get("priority", "medium"),
            related_retro_items=data.get("related_retro_items", []),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps and history if provided
        if "created_at" in data:
            action.created_at = data["created_at"]
        if "updated_at" in data:
            action.updated_at = data["updated_at"]
        if "completed_at" in data and data["completed_at"]:
            action.completed_at = data["completed_at"]
        if "status_history" in data:
            action.status_history = data["status_history"]
            
        return action

    def update_status(self, status: str, comment: Optional[str] = None):
        """Update the status of the action item."""
        self.status = status
        self.updated_at = datetime.now().timestamp()
        
        # Set completed_at if status is "completed"
        if status == "completed" and not self.completed_at:
            self.completed_at = self.updated_at
        elif status != "completed":
            self.completed_at = None
        
        # Add to status history
        self.status_history.append({
            "status": status,
            "timestamp": self.updated_at,
            "comment": comment
        })

    def assign_to(self, assignee: str):
        """Assign the action item to a person."""
        if assignee not in self.assignees:
            self.assignees.append(assignee)
            self.updated_at = datetime.now().timestamp()

    def unassign_from(self, assignee: str) -> bool:
        """Unassign the action item from a person."""
        if assignee in self.assignees:
            self.assignees.remove(assignee)
            self.updated_at = datetime.now().timestamp()
            return True
        return False

    def update_due_date(self, due_date: datetime):
        """Update the due date of the action item."""
        self.due_date = due_date
        self.updated_at = datetime.now().timestamp()

    def update_priority(self, priority: str):
        """Update the priority of the action item."""
        self.priority = priority
        self.updated_at = datetime.now().timestamp()

    def is_overdue(self) -> bool:
        """Check if the action item is overdue."""
        if not self.due_date or self.status == "completed" or self.status == "cancelled":
            return False
        return datetime.now() > self.due_date

    @staticmethod
    def create_new(
        title: str,
        description: str,
        assignees: List[str] = None,
        due_date: Optional[datetime] = None,
        priority: str = "medium",
        related_retro_items: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> 'ActionItem':
        """
        Create a new action item with a generated ID.
        
        Args:
            title: Title of the action item
            description: Description of the action item
            assignees: Optional list of assignees
            due_date: Optional due date
            priority: Optional priority
            related_retro_items: Optional list of related retrospective item IDs
            metadata: Optional metadata
            
        Returns:
            A new ActionItem instance
        """
        action_id = f"action-{uuid.uuid4()}"
        return ActionItem(
            action_id=action_id,
            title=title,
            description=description,
            assignees=assignees,
            due_date=due_date,
            priority=priority,
            related_retro_items=related_retro_items,
            metadata=metadata
        )


class Retrospective:
    """Model for a project retrospective."""

    def __init__(
        self,
        retro_id: str,
        plan_id: str,
        name: str,
        date: datetime,
        format: str,  # "start_stop_continue", "4_ls", "mad_sad_glad", etc.
        facilitator: str,
        participants: List[str] = None,
        items: List[RetroItem] = None,
        action_items: List[ActionItem] = None,
        status: str = "draft",  # "draft", "in_progress", "completed"
        metadata: Dict[str, Any] = None
    ):
        self.retro_id = retro_id
        self.plan_id = plan_id
        self.name = name
        self.date = date
        self.format = format
        self.facilitator = facilitator
        self.participants = participants or []
        self.items = items or []
        self.action_items = action_items or []
        self.status = status
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert the retrospective to a dictionary."""
        return {
            "retro_id": self.retro_id,
            "plan_id": self.plan_id,
            "name": self.name,
            "date": self.date.isoformat() if self.date else None,
            "format": self.format,
            "facilitator": self.facilitator,
            "participants": self.participants,
            "items": [item.to_dict() for item in self.items],
            "action_items": [action.to_dict() for action in self.action_items],
            "status": self.status,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Retrospective':
        """Create a retrospective from a dictionary."""
        # Convert date strings to datetime objects
        date = datetime.fromisoformat(data["date"]) if data.get("date") else None
        
        # Convert items to RetroItem objects
        items = []
        for item_data in data.get("items", []):
            items.append(RetroItem.from_dict(item_data))
        
        # Convert action items to ActionItem objects
        action_items = []
        for action_data in data.get("action_items", []):
            action_items.append(ActionItem.from_dict(action_data))
        
        # Create the retrospective
        retro = cls(
            retro_id=data["retro_id"],
            plan_id=data["plan_id"],
            name=data["name"],
            date=date,
            format=data["format"],
            facilitator=data["facilitator"],
            participants=data.get("participants", []),
            items=items,
            action_items=action_items,
            status=data.get("status", "draft"),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps if provided
        if "created_at" in data:
            retro.created_at = data["created_at"]
        if "updated_at" in data:
            retro.updated_at = data["updated_at"]
            
        return retro

    def add_item(self, item: RetroItem) -> None:
        """Add a retrospective item."""
        self.items.append(item)
        self.updated_at = datetime.now().timestamp()

    def remove_item(self, item_id: str) -> bool:
        """Remove a retrospective item."""
        for i, item in enumerate(self.items):
            if item.item_id == item_id:
                del self.items[i]
                self.updated_at = datetime.now().timestamp()
                return True
        return False

    def get_item(self, item_id: str) -> Optional[RetroItem]:
        """Get a retrospective item by ID."""
        for item in self.items:
            if item.item_id == item_id:
                return item
        return None

    def add_action_item(self, action_item: ActionItem) -> None:
        """Add an action item."""
        self.action_items.append(action_item)
        self.updated_at = datetime.now().timestamp()

    def remove_action_item(self, action_id: str) -> bool:
        """Remove an action item."""
        for i, action in enumerate(self.action_items):
            if action.action_id == action_id:
                del self.action_items[i]
                self.updated_at = datetime.now().timestamp()
                return True
        return False

    def get_action_item(self, action_id: str) -> Optional[ActionItem]:
        """Get an action item by ID."""
        for action in self.action_items:
            if action.action_id == action_id:
                return action
        return None

    def update_status(self, status: str):
        """Update the status of the retrospective."""
        self.status = status
        self.updated_at = datetime.now().timestamp()

    def start(self):
        """Start the retrospective."""
        if self.status == "draft":
            self.status = "in_progress"
            self.updated_at = datetime.now().timestamp()

    def finalize(self) -> None:
        """Finalize the retrospective."""
        self.status = "completed"
        self.updated_at = datetime.now().timestamp()

    def get_items_by_category(self, category: str) -> List[RetroItem]:
        """Get retrospective items by category."""
        return [item for item in self.items if item.category == category]

    def get_top_voted_items(self, limit: int = 5) -> List[RetroItem]:
        """Get the top voted retrospective items."""
        sorted_items = sorted(self.items, key=lambda x: x.votes, reverse=True)
        return sorted_items[:limit]

    def get_incomplete_action_items(self) -> List[ActionItem]:
        """Get incomplete action items."""
        return [action for action in self.action_items 
                if action.status != "completed" and action.status != "cancelled"]

    def get_action_items_by_priority(self, priority: str) -> List[ActionItem]:
        """Get action items by priority."""
        return [action for action in self.action_items if action.priority == priority]

    @staticmethod
    def create_new(
        plan_id: str,
        name: str,
        format: str,
        facilitator: str,
        date: Optional[datetime] = None,
        participants: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> 'Retrospective':
        """
        Create a new retrospective with a generated ID.
        
        Args:
            plan_id: ID of the plan
            name: Name of the retrospective
            format: Format of the retrospective
            facilitator: Facilitator of the retrospective
            date: Optional date of the retrospective (defaults to now)
            participants: Optional list of participants
            metadata: Optional metadata
            
        Returns:
            A new Retrospective instance
        """
        retro_id = f"retro-{uuid.uuid4()}"
        return Retrospective(
            retro_id=retro_id,
            plan_id=plan_id,
            name=name,
            date=date or datetime.now(),
            format=format,
            facilitator=facilitator,
            participants=participants,
            metadata=metadata
        )


class RetrospectiveAnalysis:
    """Model for analyzing retrospective data and generating insights."""

    @log_function()
    def __init__(
        self,
        analysis_id: str,
        retro_id: str,
        created_at: Optional[float] = None,
        updated_at: Optional[float] = None,
        insights: List[Dict[str, Any]] = None,
        metrics: Dict[str, Any] = None,
        recommendations: List[str] = None,
        comparison_data: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ):
        self.analysis_id = analysis_id
        self.retro_id = retro_id
        self.created_at = created_at or datetime.now().timestamp()
        self.updated_at = updated_at or self.created_at
        self.insights = insights or []
        self.metrics = metrics or {}
        self.recommendations = recommendations or []
        self.comparison_data = comparison_data or {}
        self.metadata = metadata or {}
        debug_log.debug("prometheus", f"RetrospectiveAnalysis initialized for retro_id: {retro_id}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the retrospective analysis to a dictionary."""
        return {
            "analysis_id": self.analysis_id,
            "retro_id": self.retro_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "insights": self.insights,
            "metrics": self.metrics,
            "recommendations": self.recommendations,
            "comparison_data": self.comparison_data,
            "metadata": self.metadata
        }

    @classmethod
    @log_function()
    def from_dict(cls, data: Dict[str, Any]) -> 'RetrospectiveAnalysis':
        """Create a retrospective analysis from a dictionary."""
        analysis = cls(
            analysis_id=data["analysis_id"],
            retro_id=data["retro_id"],
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            insights=data.get("insights", []),
            metrics=data.get("metrics", {}),
            recommendations=data.get("recommendations", []),
            comparison_data=data.get("comparison_data", {}),
            metadata=data.get("metadata", {})
        )
        debug_log.debug("prometheus", f"RetrospectiveAnalysis created from dict for retro_id: {data['retro_id']}")
        return analysis

    @log_function()
    def add_insight(self, category: str, description: str, severity: str = "medium", related_items: List[str] = None) -> None:
        """Add an insight to the analysis."""
        insight = {
            "id": f"insight-{uuid.uuid4()}",
            "category": category,
            "description": description,
            "severity": severity,
            "related_items": related_items or [],
            "created_at": datetime.now().timestamp()
        }
        self.insights.append(insight)
        self.updated_at = datetime.now().timestamp()
        debug_log.debug("prometheus", f"Added insight to analysis {self.analysis_id}: {category}")

    @log_function()
    def add_recommendation(self, recommendation: str) -> None:
        """Add a recommendation to the analysis."""
        if recommendation not in self.recommendations:
            self.recommendations.append(recommendation)
            self.updated_at = datetime.now().timestamp()
            debug_log.debug("prometheus", f"Added recommendation to analysis {self.analysis_id}")

    @log_function()
    def update_metrics(self, new_metrics: Dict[str, Any]) -> None:
        """Update the metrics with new data."""
        self.metrics.update(new_metrics)
        self.updated_at = datetime.now().timestamp()
        debug_log.debug("prometheus", f"Updated metrics for analysis {self.analysis_id}")

    @log_function()
    def compare_with_previous(self, previous_retro_data: Dict[str, Any]) -> None:
        """Compare with a previous retrospective and update comparison data."""
        # Simplified comparison logic - in a real implementation, 
        # this would contain more sophisticated analysis
        if not previous_retro_data:
            debug_log.debug("prometheus", "No previous retro data provided for comparison")
            return
            
        # Example comparison calculations
        self.comparison_data["previous_retro_id"] = previous_retro_data.get("retro_id")
        
        # Compare action item completion rates
        prev_action_items = previous_retro_data.get("action_items", [])
        prev_completed = sum(1 for item in prev_action_items if item.get("status") == "completed")
        prev_total = len(prev_action_items)
        prev_completion_rate = prev_completed / prev_total if prev_total > 0 else 0
        
        curr_action_items = self.metrics.get("action_items", {})
        curr_completed = curr_action_items.get("completed", 0)
        curr_total = curr_action_items.get("total", 0)
        curr_completion_rate = curr_completed / curr_total if curr_total > 0 else 0
        
        self.comparison_data["action_completion_rate_change"] = curr_completion_rate - prev_completion_rate
        self.updated_at = datetime.now().timestamp()
        debug_log.debug("prometheus", f"Completed comparison with previous retro {previous_retro_data.get('retro_id')}")

    @staticmethod
    @log_function()
    def create_new(retro_id: str, metrics: Dict[str, Any] = None) -> 'RetrospectiveAnalysis':
        """
        Create a new retrospective analysis with a generated ID.
        
        Args:
            retro_id: ID of the retrospective being analyzed
            metrics: Optional initial metrics
            
        Returns:
            A new RetrospectiveAnalysis instance
        """
        analysis_id = f"retro-analysis-{uuid.uuid4()}"
        debug_log.info("prometheus", f"Creating new RetrospectiveAnalysis with ID: {analysis_id}")
        return RetrospectiveAnalysis(
            analysis_id=analysis_id,
            retro_id=retro_id,
            metrics=metrics
        )


class PerformanceMetrics:
    """Model for tracking and analyzing performance metrics from retrospectives."""

    @log_function()
    def __init__(
        self,
        metrics_id: str,
        retro_id: str,
        created_at: Optional[float] = None,
        updated_at: Optional[float] = None,
        velocity: Optional[float] = None,
        completion_rate: Optional[float] = None,
        average_task_duration: Optional[float] = None,
        story_points_completed: Optional[int] = None,
        tasks_completed: Optional[int] = None,
        blockers_count: Optional[int] = None,
        lead_time: Optional[float] = None,
        cycle_time: Optional[float] = None,
        team_satisfaction: Optional[float] = None,
        custom_metrics: Dict[str, Any] = None,
        historical_data: List[Dict[str, Any]] = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize performance metrics.
        
        Args:
            metrics_id: Unique identifier for the metrics
            retro_id: ID of the related retrospective
            created_at: Creation timestamp
            updated_at: Last update timestamp
            velocity: Team velocity (story points per time period)
            completion_rate: Task completion rate (0.0-1.0)
            average_task_duration: Average time to complete tasks
            story_points_completed: Total story points completed
            tasks_completed: Number of tasks completed
            blockers_count: Number of blockers encountered
            lead_time: Average lead time (concept to delivery)
            cycle_time: Average cycle time (work start to completion)
            team_satisfaction: Team satisfaction score (0.0-10.0)
            custom_metrics: Any additional custom metrics
            historical_data: Historical performance data for trend analysis
            metadata: Additional metadata
        """
        self.metrics_id = metrics_id
        self.retro_id = retro_id
        self.created_at = created_at or datetime.now().timestamp()
        self.updated_at = updated_at or self.created_at
        self.velocity = velocity
        self.completion_rate = completion_rate
        self.average_task_duration = average_task_duration
        self.story_points_completed = story_points_completed
        self.tasks_completed = tasks_completed
        self.blockers_count = blockers_count
        self.lead_time = lead_time
        self.cycle_time = cycle_time
        self.team_satisfaction = team_satisfaction
        self.custom_metrics = custom_metrics or {}
        self.historical_data = historical_data or []
        self.metadata = metadata or {}
        debug_log.debug("prometheus", f"PerformanceMetrics initialized for retro_id: {retro_id}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the performance metrics to a dictionary."""
        return {
            "metrics_id": self.metrics_id,
            "retro_id": self.retro_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "velocity": self.velocity,
            "completion_rate": self.completion_rate,
            "average_task_duration": self.average_task_duration,
            "story_points_completed": self.story_points_completed,
            "tasks_completed": self.tasks_completed,
            "blockers_count": self.blockers_count,
            "lead_time": self.lead_time,
            "cycle_time": self.cycle_time,
            "team_satisfaction": self.team_satisfaction,
            "custom_metrics": self.custom_metrics,
            "historical_data": self.historical_data,
            "metadata": self.metadata
        }

    @classmethod
    @log_function()
    def from_dict(cls, data: Dict[str, Any]) -> 'PerformanceMetrics':
        """Create performance metrics from a dictionary."""
        metrics = cls(
            metrics_id=data["metrics_id"],
            retro_id=data["retro_id"],
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            velocity=data.get("velocity"),
            completion_rate=data.get("completion_rate"),
            average_task_duration=data.get("average_task_duration"),
            story_points_completed=data.get("story_points_completed"),
            tasks_completed=data.get("tasks_completed"),
            blockers_count=data.get("blockers_count"),
            lead_time=data.get("lead_time"),
            cycle_time=data.get("cycle_time"),
            team_satisfaction=data.get("team_satisfaction"),
            custom_metrics=data.get("custom_metrics", {}),
            historical_data=data.get("historical_data", []),
            metadata=data.get("metadata", {})
        )
        debug_log.debug("prometheus", f"PerformanceMetrics created from dict for retro_id: {data['retro_id']}")
        return metrics

    @log_function()
    def add_historical_data_point(self, data_point: Dict[str, Any]) -> None:
        """Add a historical data point for trend analysis."""
        if not data_point.get("timestamp"):
            data_point["timestamp"] = datetime.now().timestamp()
        self.historical_data.append(data_point)
        self.updated_at = datetime.now().timestamp()
        debug_log.debug("prometheus", f"Added historical data point to metrics {self.metrics_id}")

    @log_function()
    def add_custom_metric(self, name: str, value: Any) -> None:
        """Add or update a custom metric."""
        self.custom_metrics[name] = value
        self.updated_at = datetime.now().timestamp()
        debug_log.debug("prometheus", f"Added custom metric '{name}' to metrics {self.metrics_id}")

    @log_function()
    def calculate_trend(self, metric_name: str) -> Dict[str, Any]:
        """
        Calculate trend data for a specific metric.
        
        Args:
            metric_name: Name of the metric to analyze
            
        Returns:
            Trend analysis data
        """
        if not self.historical_data:
            return {"trend": "no_data", "change": 0, "data_points": 0}
            
        data_points = [point.get(metric_name) for point in sorted(
            self.historical_data, 
            key=lambda x: x.get("timestamp", 0)
        ) if point.get(metric_name) is not None]
        
        if not data_points or len(data_points) < 2:
            return {"trend": "insufficient_data", "change": 0, "data_points": len(data_points)}
            
        first_value = data_points[0]
        last_value = data_points[-1]
        
        if isinstance(first_value, (int, float)) and isinstance(last_value, (int, float)):
            change = last_value - first_value
            percent_change = (change / abs(first_value)) * 100 if first_value != 0 else 0
            
            trend = "stable"
            if percent_change > 5:
                trend = "improving"
            elif percent_change < -5:
                trend = "declining"
                
            return {
                "trend": trend,
                "change": change,
                "percent_change": percent_change,
                "first_value": first_value,
                "last_value": last_value,
                "data_points": len(data_points)
            }
        
        return {"trend": "non_numeric", "change": 0, "data_points": len(data_points)}

    @staticmethod
    @log_function()
    def create_new(retro_id: str) -> 'PerformanceMetrics':
        """
        Create new performance metrics with a generated ID.
        
        Args:
            retro_id: ID of the retrospective
            
        Returns:
            A new PerformanceMetrics instance
        """
        metrics_id = f"metrics-{uuid.uuid4()}"
        debug_log.info("prometheus", f"Creating new PerformanceMetrics with ID: {metrics_id}")
        return PerformanceMetrics(
            metrics_id=metrics_id,
            retro_id=retro_id
        )