"""
Metrics Models

This module defines the domain models for metrics and analysis in the Prometheus/Epimethius Planning System.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple, Union
import uuid


class PerformanceMetric:
    """Model for a performance metric."""

    def __init__(
        self,
        metric_id: str,
        name: str,
        description: str,
        value: Union[float, int, str],
        metric_type: str,  # "velocity", "quality", "efficiency", "predictability", etc.
        unit: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        context: Dict[str, Any] = None,
        source: Optional[str] = None,  # "plan", "execution", "retrospective", etc.
        source_id: Optional[str] = None,  # ID of the source entity
        metadata: Dict[str, Any] = None
    ):
        self.metric_id = metric_id
        self.name = name
        self.description = description
        self.value = value
        self.metric_type = metric_type
        self.unit = unit
        self.timestamp = timestamp or datetime.now()
        self.context = context or {}
        self.source = source
        self.source_id = source_id
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the performance metric to a dictionary."""
        return {
            "metric_id": self.metric_id,
            "name": self.name,
            "description": self.description,
            "value": self.value,
            "metric_type": self.metric_type,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "context": self.context,
            "source": self.source,
            "source_id": self.source_id,
            "metadata": self.metadata,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PerformanceMetric':
        """Create a performance metric from a dictionary."""
        # Convert date strings to datetime objects
        timestamp = datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None
        
        # Create the metric
        metric = cls(
            metric_id=data["metric_id"],
            name=data["name"],
            description=data["description"],
            value=data["value"],
            metric_type=data["metric_type"],
            unit=data.get("unit"),
            timestamp=timestamp,
            context=data.get("context", {}),
            source=data.get("source"),
            source_id=data.get("source_id"),
            metadata=data.get("metadata", {})
        )
        
        # Set created_at if provided
        if "created_at" in data:
            metric.created_at = data["created_at"]
            
        return metric

    @staticmethod
    def create_new(
        name: str,
        description: str,
        value: Union[float, int, str],
        metric_type: str,
        unit: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        context: Dict[str, Any] = None,
        source: Optional[str] = None,
        source_id: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> 'PerformanceMetric':
        """
        Create a new performance metric with a generated ID.
        
        Args:
            name: Name of the metric
            description: Description of the metric
            value: Value of the metric
            metric_type: Type of the metric
            unit: Optional unit of the metric
            timestamp: Optional timestamp (defaults to now)
            context: Optional context
            source: Optional source
            source_id: Optional source ID
            metadata: Optional metadata
            
        Returns:
            A new PerformanceMetric instance
        """
        metric_id = f"metric-{uuid.uuid4()}"
        return PerformanceMetric(
            metric_id=metric_id,
            name=name,
            description=description,
            value=value,
            metric_type=metric_type,
            unit=unit,
            timestamp=timestamp,
            context=context,
            source=source,
            source_id=source_id,
            metadata=metadata
        )


class MetricSeries:
    """Model for a series of metrics over time."""

    def __init__(
        self,
        series_id: str,
        name: str,
        description: str,
        metric_type: str,
        unit: Optional[str] = None,
        data_points: List[Dict[str, Any]] = None,
        aggregation_method: Optional[str] = None,  # "average", "sum", "min", "max", etc.
        source: Optional[str] = None,
        source_id: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.series_id = series_id
        self.name = name
        self.description = description
        self.metric_type = metric_type
        self.unit = unit
        self.data_points = data_points or []
        self.aggregation_method = aggregation_method
        self.source = source
        self.source_id = source_id
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert the metric series to a dictionary."""
        return {
            "series_id": self.series_id,
            "name": self.name,
            "description": self.description,
            "metric_type": self.metric_type,
            "unit": self.unit,
            "data_points": self.data_points,
            "aggregation_method": self.aggregation_method,
            "source": self.source,
            "source_id": self.source_id,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetricSeries':
        """Create a metric series from a dictionary."""
        series = cls(
            series_id=data["series_id"],
            name=data["name"],
            description=data["description"],
            metric_type=data["metric_type"],
            unit=data.get("unit"),
            data_points=data.get("data_points", []),
            aggregation_method=data.get("aggregation_method"),
            source=data.get("source"),
            source_id=data.get("source_id"),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps if provided
        if "created_at" in data:
            series.created_at = data["created_at"]
        if "updated_at" in data:
            series.updated_at = data["updated_at"]
            
        return series

    def add_data_point(self, timestamp: datetime, value: Union[float, int, str], context: Dict[str, Any] = None):
        """Add a data point to the series."""
        self.data_points.append({
            "timestamp": timestamp.isoformat(),
            "value": value,
            "context": context or {}
        })
        self.updated_at = datetime.now().timestamp()

    def get_data_points(self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get data points within a time range.
        
        Args:
            start_time: Optional start time
            end_time: Optional end time
            
        Returns:
            List of data points
        """
        if not start_time and not end_time:
            return self.data_points
            
        filtered_points = []
        for point in self.data_points:
            point_time = datetime.fromisoformat(point["timestamp"])
            if start_time and point_time < start_time:
                continue
            if end_time and point_time > end_time:
                continue
            filtered_points.append(point)
            
        return filtered_points

    def calculate_aggregation(self, method: Optional[str] = None) -> Optional[float]:
        """
        Calculate an aggregation of the series.
        
        Args:
            method: Aggregation method (defaults to self.aggregation_method)
            
        Returns:
            Aggregated value
        """
        method = method or self.aggregation_method
        if not method or not self.data_points:
            return None
            
        # Extract numerical values
        values = []
        for point in self.data_points:
            value = point["value"]
            if isinstance(value, (int, float)):
                values.append(value)
        
        if not values:
            return None
            
        # Calculate aggregation
        if method == "average":
            return sum(values) / len(values)
        elif method == "sum":
            return sum(values)
        elif method == "min":
            return min(values)
        elif method == "max":
            return max(values)
        elif method == "median":
            sorted_values = sorted(values)
            mid = len(sorted_values) // 2
            if len(sorted_values) % 2 == 0:
                return (sorted_values[mid-1] + sorted_values[mid]) / 2
            else:
                return sorted_values[mid]
        else:
            return None

    @staticmethod
    def create_new(
        name: str,
        description: str,
        metric_type: str,
        unit: Optional[str] = None,
        aggregation_method: Optional[str] = None,
        source: Optional[str] = None,
        source_id: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> 'MetricSeries':
        """
        Create a new metric series with a generated ID.
        
        Args:
            name: Name of the series
            description: Description of the series
            metric_type: Type of the metric
            unit: Optional unit
            aggregation_method: Optional aggregation method
            source: Optional source
            source_id: Optional source ID
            metadata: Optional metadata
            
        Returns:
            A new MetricSeries instance
        """
        series_id = f"series-{uuid.uuid4()}"
        return MetricSeries(
            series_id=series_id,
            name=name,
            description=description,
            metric_type=metric_type,
            unit=unit,
            aggregation_method=aggregation_method,
            source=source,
            source_id=source_id,
            metadata=metadata
        )


class PerformanceAnalysis:
    """Model for a performance analysis."""

    def __init__(
        self,
        analysis_id: str,
        name: str,
        description: str,
        analysis_type: str,  # "velocity", "bottleneck", "trend", "comparison", etc.
        metrics: List[str] = None,  # IDs of metrics
        series: List[str] = None,  # IDs of metric series
        results: Dict[str, Any] = None,
        recommendations: List[Dict[str, Any]] = None,
        source: Optional[str] = None,
        source_id: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.analysis_id = analysis_id
        self.name = name
        self.description = description
        self.analysis_type = analysis_type
        self.metrics = metrics or []
        self.series = series or []
        self.results = results or {}
        self.recommendations = recommendations or []
        self.source = source
        self.source_id = source_id
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert the performance analysis to a dictionary."""
        return {
            "analysis_id": self.analysis_id,
            "name": self.name,
            "description": self.description,
            "analysis_type": self.analysis_type,
            "metrics": self.metrics,
            "series": self.series,
            "results": self.results,
            "recommendations": self.recommendations,
            "source": self.source,
            "source_id": self.source_id,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PerformanceAnalysis':
        """Create a performance analysis from a dictionary."""
        analysis = cls(
            analysis_id=data["analysis_id"],
            name=data["name"],
            description=data["description"],
            analysis_type=data["analysis_type"],
            metrics=data.get("metrics", []),
            series=data.get("series", []),
            results=data.get("results", {}),
            recommendations=data.get("recommendations", []),
            source=data.get("source"),
            source_id=data.get("source_id"),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps if provided
        if "created_at" in data:
            analysis.created_at = data["created_at"]
        if "updated_at" in data:
            analysis.updated_at = data["updated_at"]
            
        return analysis

    def add_metric(self, metric_id: str):
        """Add a metric to the analysis."""
        if metric_id not in self.metrics:
            self.metrics.append(metric_id)
            self.updated_at = datetime.now().timestamp()

    def add_series(self, series_id: str):
        """Add a metric series to the analysis."""
        if series_id not in self.series:
            self.series.append(series_id)
            self.updated_at = datetime.now().timestamp()

    def update_results(self, results: Dict[str, Any]):
        """Update the analysis results."""
        self.results = results
        self.updated_at = datetime.now().timestamp()

    def add_recommendation(self, title: str, description: str, priority: str = "medium", action_items: List[str] = None):
        """Add a recommendation to the analysis."""
        self.recommendations.append({
            "title": title,
            "description": description,
            "priority": priority,
            "action_items": action_items or [],
            "created_at": datetime.now().timestamp()
        })
        self.updated_at = datetime.now().timestamp()

    @staticmethod
    def create_new(
        name: str,
        description: str,
        analysis_type: str,
        metrics: List[str] = None,
        series: List[str] = None,
        results: Dict[str, Any] = None,
        recommendations: List[Dict[str, Any]] = None,
        source: Optional[str] = None,
        source_id: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> 'PerformanceAnalysis':
        """
        Create a new performance analysis with a generated ID.
        
        Args:
            name: Name of the analysis
            description: Description of the analysis
            analysis_type: Type of the analysis
            metrics: Optional list of metric IDs
            series: Optional list of metric series IDs
            results: Optional results
            recommendations: Optional recommendations
            source: Optional source
            source_id: Optional source ID
            metadata: Optional metadata
            
        Returns:
            A new PerformanceAnalysis instance
        """
        analysis_id = f"analysis-{uuid.uuid4()}"
        return PerformanceAnalysis(
            analysis_id=analysis_id,
            name=name,
            description=description,
            analysis_type=analysis_type,
            metrics=metrics,
            series=series,
            results=results,
            recommendations=recommendations,
            source=source,
            source_id=source_id,
            metadata=metadata
        )