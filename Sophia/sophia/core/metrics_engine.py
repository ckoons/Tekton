"""
Metrics Engine for Sophia

This module provides a comprehensive metrics collection, storage, and retrieval system
for monitoring and analyzing performance across the Tekton ecosystem.
"""

import os
import json
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Set, Tuple
from math import ceil
from .database import get_database

logger = logging.getLogger("sophia.metrics_engine")

class MetricsStore:
    """
    Storage system for metrics with time-series capabilities.
    
    Provides in-memory storage with efficient retrieval and
    aggregation capabilities.
    """
    
    def __init__(self, max_memory_records: int = 10000):
        """
        Initialize the metrics store.
        
        Args:
            max_memory_records: Maximum number of records to keep in memory
        """
        self.memory_store = []
        self.max_memory_records = max_memory_records
        self.indices = {
            "metric_id": {},
            "source": {},
            "tags": {}
        }
        self.aggregation_cache = {}
        self.cache_expiry = {}
        
    async def store_metric(self, metric: Dict[str, Any]) -> bool:
        """
        Store a metric in the metrics store.
        
        Args:
            metric: The metric to store
            
        Returns:
            True if storage was successful
        """
        # Ensure the metric has all required fields
        required_fields = ["metric_id", "value", "timestamp"]
        for field in required_fields:
            if field not in metric:
                if field == "timestamp":
                    metric["timestamp"] = datetime.utcnow().isoformat() + "Z"
                else:
                    logger.error(f"Missing required field in metric: {field}")
                    return False
                    
        # Add the metric to the memory store
        record_id = len(self.memory_store)
        self.memory_store.append(metric)
        
        # Update indices
        self._update_indices(record_id, metric)
        
        # Clear aggregation cache for this metric type
        self._invalidate_cache(metric["metric_id"])
        
        # Trim the memory store if needed
        if len(self.memory_store) > self.max_memory_records:
            self._trim_memory_store()
            
        return True
        
    async def query_metrics(
        self,
        metric_id: Optional[str] = None,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 1000,
        offset: int = 0,
        sort: str = "timestamp:desc"
    ) -> List[Dict[str, Any]]:
        """
        Query metrics from the store.
        
        Args:
            metric_id: Filter by metric ID
            source: Filter by source
            tags: Filter by tags (any match)
            start_time: Filter by start time (ISO format)
            end_time: Filter by end time (ISO format)
            limit: Maximum number of results to return
            offset: Offset for pagination
            sort: Sorting specification (field:direction)
            
        Returns:
            List of matching metrics
        """
        # Find candidate record IDs based on indices
        candidate_ids = await self._find_candidate_ids(metric_id, source, tags)
        
        # Apply additional filters
        results = []
        for record_id in candidate_ids:
            if record_id >= len(self.memory_store):
                continue
                
            metric = self.memory_store[record_id]
            
            # Apply time filters
            if not self._matches_time_filters(metric, start_time, end_time):
                continue
                
            results.append(metric)
            
        # Apply sorting
        if sort:
            field, direction = sort.split(":")
            reverse = direction.lower() == "desc"
            results.sort(key=lambda m: m.get(field, ""), reverse=reverse)
            
        # Apply pagination
        return results[offset:offset+limit]
        
    async def aggregate_metrics(
        self,
        metric_id: str,
        aggregation: str = "avg",
        interval: Optional[str] = None,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Aggregate metrics for analysis.
        
        Args:
            metric_id: The metric ID to aggregate
            aggregation: Aggregation function (avg, sum, min, max, count)
            interval: Time interval for time-series aggregation (e.g., "1h", "1d")
            source: Filter by source
            tags: Filter by tags
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            Aggregation results
        """
        # Check the cache first
        cache_key = f"{metric_id}:{aggregation}:{interval}:{source}:{tags}:{start_time}:{end_time}"
        if cache_key in self.aggregation_cache and cache_key in self.cache_expiry:
            if datetime.utcnow() < self.cache_expiry[cache_key]:
                return self.aggregation_cache[cache_key]
        
        # Get the metrics
        metrics = await self.query_metrics(
            metric_id=metric_id,
            source=source,
            tags=tags,
            start_time=start_time,
            end_time=end_time,
            limit=100000  # Large limit for aggregation
        )
        
        # If no interval is specified, return a single aggregation
        if not interval:
            result = self._compute_aggregation(metrics, aggregation)
            self._cache_aggregation(cache_key, result)
            return {
                "metric_id": metric_id,
                "aggregation": aggregation,
                "value": result,
                "count": len(metrics)
            }
            
        # Time-series aggregation
        intervals = self._create_time_intervals(start_time, end_time, interval)
        
        # Group metrics by interval
        interval_metrics = {interval_start: [] for interval_start, _ in intervals}
        for metric in metrics:
            timestamp = metric.get("timestamp")
            if not timestamp:
                continue
                
            for interval_start, interval_end in intervals:
                if interval_start <= timestamp <= interval_end:
                    interval_metrics[interval_start].append(metric)
                    break
                    
        # Compute aggregation for each interval
        time_series = []
        for interval_start, interval_end in intervals:
            interval_data = interval_metrics[interval_start]
            if interval_data:
                value = self._compute_aggregation(interval_data, aggregation)
            else:
                value = None
                
            time_series.append({
                "start_time": interval_start,
                "end_time": interval_end,
                "value": value,
                "count": len(interval_data)
            })
            
        result = {
            "metric_id": metric_id,
            "aggregation": aggregation,
            "interval": interval,
            "time_series": time_series
        }
        
        # Cache the result
        self._cache_aggregation(cache_key, result)
        
        return result
        
    def _compute_aggregation(self, metrics: List[Dict[str, Any]], aggregation: str) -> Optional[float]:
        """
        Compute an aggregation function on metrics.
        
        Args:
            metrics: List of metrics to aggregate
            aggregation: Aggregation function name
            
        Returns:
            Aggregation result or None if no metrics
        """
        if not metrics:
            return None
            
        values = [float(m["value"]) for m in metrics if "value" in m]
        if not values:
            return None
            
        if aggregation == "avg":
            return sum(values) / len(values)
        elif aggregation == "sum":
            return sum(values)
        elif aggregation == "min":
            return min(values)
        elif aggregation == "max":
            return max(values)
        elif aggregation == "count":
            return len(values)
        elif aggregation == "p50":
            return self._percentile(values, 50)
        elif aggregation == "p95":
            return self._percentile(values, 95)
        elif aggregation == "p99":
            return self._percentile(values, 99)
        else:
            logger.warning(f"Unknown aggregation function: {aggregation}")
            return None
            
    def _percentile(self, values: List[float], percentile: int) -> float:
        """
        Calculate a percentile value from a list of values.
        
        Args:
            values: List of numerical values
            percentile: Percentile to calculate (0-100)
            
        Returns:
            Percentile value
        """
        if not values:
            return 0
            
        sorted_values = sorted(values)
        k = (len(sorted_values) - 1) * (percentile/100.0)
        f = int(k)
        c = ceil(k)
        if f == c:
            return sorted_values[int(k)]
        return sorted_values[f] * (c-k) + sorted_values[c] * (k-f)
            
    def _create_time_intervals(
        self, 
        start_time: Optional[str], 
        end_time: Optional[str], 
        interval: str
    ) -> List[Tuple[str, str]]:
        """
        Create time intervals for time-series aggregation.
        
        Args:
            start_time: Start time (ISO format)
            end_time: End time (ISO format)
            interval: Interval specification (e.g., "1h", "1d")
            
        Returns:
            List of (interval_start, interval_end) tuples
        """
        # Parse interval
        if interval.endswith("m"):
            delta = timedelta(minutes=int(interval[:-1]))
        elif interval.endswith("h"):
            delta = timedelta(hours=int(interval[:-1]))
        elif interval.endswith("d"):
            delta = timedelta(days=int(interval[:-1]))
        else:
            # Default to hours
            delta = timedelta(hours=int(interval))
            
        # Determine start and end times
        if start_time:
            try:
                start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            except ValueError:
                start = datetime.utcnow() - timedelta(days=1)
        else:
            start = datetime.utcnow() - timedelta(days=1)
            
        if end_time:
            try:
                end = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            except ValueError:
                end = datetime.utcnow()
        else:
            end = datetime.utcnow()
            
        # Generate intervals
        intervals = []
        current = start
        while current < end:
            interval_end = min(current + delta, end)
            intervals.append((
                current.isoformat() + "Z",
                interval_end.isoformat() + "Z"
            ))
            current = interval_end
            
        return intervals
        
    def _update_indices(self, record_id: int, metric: Dict[str, Any]) -> None:
        """Update indices for a new metric record."""
        # Update metric_id index
        metric_id = metric.get("metric_id")
        if metric_id:
            if metric_id not in self.indices["metric_id"]:
                self.indices["metric_id"][metric_id] = set()
            self.indices["metric_id"][metric_id].add(record_id)
            
        # Update source index
        source = metric.get("source")
        if source:
            if source not in self.indices["source"]:
                self.indices["source"][source] = set()
            self.indices["source"][source].add(record_id)
            
        # Update tags index
        tags = metric.get("tags", [])
        for tag in tags:
            if tag not in self.indices["tags"]:
                self.indices["tags"][tag] = set()
            self.indices["tags"][tag].add(record_id)
            
    async def _find_candidate_ids(
        self, 
        metric_id: Optional[str] = None,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Set[int]:
        """Find candidate record IDs based on indices."""
        candidates = set(range(len(self.memory_store)))
        
        # Apply metric_id filter
        if metric_id and metric_id in self.indices["metric_id"]:
            candidates &= self.indices["metric_id"][metric_id]
            
        # Apply source filter
        if source and source in self.indices["source"]:
            candidates &= self.indices["source"][source]
            
        # Apply tags filter (any match)
        if tags:
            tag_candidates = set()
            for tag in tags:
                if tag in self.indices["tags"]:
                    tag_candidates |= self.indices["tags"][tag]
            if tag_candidates:
                candidates &= tag_candidates
                
        return candidates
        
    def _matches_time_filters(
        self,
        metric: Dict[str, Any],
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> bool:
        """Check if a metric matches time filters."""
        timestamp = metric.get("timestamp")
        if not timestamp:
            return False
            
        # Apply start_time filter
        if start_time and timestamp < start_time:
            return False
            
        # Apply end_time filter
        if end_time and timestamp > end_time:
            return False
            
        return True
        
    def _trim_memory_store(self) -> None:
        """Trim the memory store to the maximum size."""
        # Remove oldest records
        excess = len(self.memory_store) - self.max_memory_records
        if excess <= 0:
            return
            
        # Records to remove
        for i in range(excess):
            # Note: This is inefficient for large trims
            # For a production system, batch operations would be better
            self._remove_from_indices(i)
            
        # Shift remaining records
        self.memory_store = self.memory_store[excess:]
        
        # Rebuild indices (shift record IDs)
        self._rebuild_indices()
        
    def _rebuild_indices(self) -> None:
        """Rebuild indices after trimming memory store."""
        new_indices = {
            "metric_id": {},
            "source": {},
            "tags": {}
        }
        
        for i, metric in enumerate(self.memory_store):
            # Update metric_id index
            metric_id = metric.get("metric_id")
            if metric_id:
                if metric_id not in new_indices["metric_id"]:
                    new_indices["metric_id"][metric_id] = set()
                new_indices["metric_id"][metric_id].add(i)
                
            # Update source index
            source = metric.get("source")
            if source:
                if source not in new_indices["source"]:
                    new_indices["source"][source] = set()
                new_indices["source"][source].add(i)
                
            # Update tags index
            tags = metric.get("tags", [])
            for tag in tags:
                if tag not in new_indices["tags"]:
                    new_indices["tags"][tag] = set()
                new_indices["tags"][tag].add(i)
                
        self.indices = new_indices
        
    def _remove_from_indices(self, record_id: int) -> None:
        """Remove a record from all indices."""
        if record_id >= len(self.memory_store):
            return
            
        metric = self.memory_store[record_id]
        
        # Remove from metric_id index
        metric_id = metric.get("metric_id")
        if metric_id and metric_id in self.indices["metric_id"]:
            self.indices["metric_id"][metric_id].discard(record_id)
            
        # Remove from source index
        source = metric.get("source")
        if source and source in self.indices["source"]:
            self.indices["source"][source].discard(record_id)
            
        # Remove from tags index
        tags = metric.get("tags", [])
        for tag in tags:
            if tag in self.indices["tags"]:
                self.indices["tags"][tag].discard(record_id)
                
    def _invalidate_cache(self, metric_id: str) -> None:
        """Invalidate aggregation cache for a metric ID."""
        keys_to_remove = []
        for key in self.aggregation_cache:
            if key.startswith(f"{metric_id}:"):
                keys_to_remove.append(key)
                
        for key in keys_to_remove:
            if key in self.aggregation_cache:
                del self.aggregation_cache[key]
            if key in self.cache_expiry:
                del self.cache_expiry[key]
                
    def _cache_aggregation(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Cache an aggregation result."""
        self.aggregation_cache[cache_key] = result
        self.cache_expiry[cache_key] = datetime.utcnow() + timedelta(minutes=5)


class MetricsEngine:
    """
    Core metrics engine for collecting, storing, and analyzing metrics.
    
    Provides standardized metrics collection and storage with
    analysis capabilities for the Tekton ecosystem.
    """
    
    def __init__(self):
        """Initialize the metrics engine."""
        self.store = MetricsStore()
        self.database = None
        self.is_initialized = False
        self.polling_tasks = {}
        self.metric_definitions = {}
        self._shutdown_flag = False
        
    async def initialize(self) -> bool:
        """
        Initialize the metrics engine.
        
        Returns:
            True if initialization was successful
        """
        logger.info("Initializing Sophia Metrics Engine...")
        
        # Initialize database
        self.database = await get_database()
        
        # Load metric definitions
        await self._load_metric_definitions()
        
        self.is_initialized = True
        logger.info("Sophia Metrics Engine initialized successfully")
        return True
        
    async def start(self) -> bool:
        """
        Start the metrics engine and background tasks.
        
        Returns:
            True if successful
        """
        if not self.is_initialized:
            success = await self.initialize()
            if not success:
                logger.error("Failed to initialize Metrics Engine")
                return False
                
        logger.info("Starting Sophia Metrics Engine...")
        
        # Start polling components for metrics
        await self._start_polling_tasks()
        
        logger.info("Sophia Metrics Engine started successfully")
        return True
        
    async def stop(self) -> bool:
        """
        Stop the metrics engine and clean up resources.
        
        Returns:
            True if successful
        """
        logger.info("Stopping Sophia Metrics Engine...")
        
        # Set shutdown flag to help loops exit gracefully
        self._shutdown_flag = True
        
        # Stop polling tasks and await their cancellation
        if self.polling_tasks:
            tasks_to_cancel = list(self.polling_tasks.values())
            for task in tasks_to_cancel:
                task.cancel()
            
            # Wait for all tasks to complete cancellation
            for task in tasks_to_cancel:
                try:
                    await task
                except asyncio.CancelledError:
                    # This is expected when a task is cancelled
                    pass
                except Exception as e:
                    logger.warning(f"Error while cancelling task: {e}")
            
            self.polling_tasks = {}
            logger.info("All polling tasks cancelled")
        
        # Close persistent storage connections
        await self._close_persistent_storage()
        
        logger.info("Sophia Metrics Engine stopped successfully")
        return True
        
    async def record_metric(
        self,
        metric_id: str,
        value: Union[float, int, str],
        source: Optional[str] = None,
        timestamp: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Record a metric in the metrics engine.
        
        Args:
            metric_id: Unique identifier for the metric type
            value: Value of the metric
            source: Source of the metric (e.g., component ID)
            timestamp: ISO timestamp (defaults to current time)
            context: Additional context for the metric
            tags: Tags for categorizing the metric
            
        Returns:
            True if the metric was recorded successfully
        """
        # Convert value to float if possible
        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            numeric_value = None
            
        # Prepare metric record
        metric = {
            "metric_id": metric_id,
            "value": numeric_value if numeric_value is not None else value,
            "timestamp": timestamp or (datetime.utcnow().isoformat() + "Z")
        }
        
        # Add optional fields
        if source:
            metric["source"] = source
        if context:
            metric["context"] = context
        if tags:
            metric["tags"] = tags
            
        # Validate metric against definition
        if not await self._validate_metric(metric):
            return False
            
        # Store the metric in both memory and database
        memory_success = await self.store.store_metric(metric)
        
        # Also save to database if available
        if self.database and numeric_value is not None:
            db_success = await self.database.save_metric(
                component_name=source or "unknown",
                metric_name=metric_id,
                value=numeric_value,
                tags=dict(zip(tags or [], [True] * len(tags or []))),
                context=context,
                timestamp=metric["timestamp"]
            )
            return memory_success and db_success
        
        # Notify WebSocket clients of new metric
        if memory_success:
            try:
                from sophia.core.realtime_manager import notify_metrics_collected
                await notify_metrics_collected({
                    "metric_id": metric_id,
                    "value": numeric_value if numeric_value is not None else value,
                    "source": source,
                    "timestamp": metric["timestamp"],
                    "context": context,
                    "tags": tags
                })
            except Exception as e:
                logger.debug(f"Could not send real-time metric notification: {e}")
        
        return memory_success
        
    async def query_metrics(
        self,
        metric_id: Optional[str] = None,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        sort: str = "timestamp:desc"
    ) -> List[Dict[str, Any]]:
        """
        Query metrics from the engine.
        
        Args:
            metric_id: Filter by metric ID
            source: Filter by source
            tags: Filter by tags
            start_time: Filter by start time (ISO format)
            end_time: Filter by end time (ISO format)
            limit: Maximum number of results to return
            offset: Offset for pagination
            sort: Sorting specification (field:direction)
            
        Returns:
            List of matching metrics
        """
        return await self.store.query_metrics(
            metric_id=metric_id,
            source=source,
            tags=tags,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset,
            sort=sort
        )
        
    async def aggregate_metrics(
        self,
        metric_id: str,
        aggregation: str = "avg",
        interval: Optional[str] = None,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Aggregate metrics for analysis.
        
        Args:
            metric_id: The metric ID to aggregate
            aggregation: Aggregation function (avg, sum, min, max, count, p50, p95, p99)
            interval: Time interval for time-series aggregation (e.g., "1h", "1d")
            source: Filter by source
            tags: Filter by tags
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            Aggregation results
        """
        return await self.store.aggregate_metrics(
            metric_id=metric_id,
            aggregation=aggregation,
            interval=interval,
            source=source,
            tags=tags,
            start_time=start_time,
            end_time=end_time
        )
        
    async def _load_metric_definitions(self) -> bool:
        """
        Load metric definitions from configuration.
        
        Returns:
            True if successful
        """
        # Standard metric types based on SOPHIA_METRICS_SPECIFICATION.md
        # This would normally be loaded from a configuration file
        self.metric_definitions = {
            # Performance metrics
            "perf.response_time": {
                "description": "Time to respond to a request",
                "unit": "milliseconds",
                "type": "float",
                "aggregations": ["avg", "p50", "p95", "p99"]
            },
            "perf.processing_time": {
                "description": "Time to process a task",
                "unit": "milliseconds",
                "type": "float",
                "aggregations": ["avg", "p50", "p95", "p99"]
            },
            "perf.throughput": {
                "description": "Number of operations per unit time",
                "unit": "ops/second",
                "type": "float",
                "aggregations": ["avg", "max"]
            },
            
            # Resource metrics
            "res.cpu_usage": {
                "description": "CPU utilization",
                "unit": "percentage",
                "type": "float",
                "aggregations": ["avg", "max"]
            },
            "res.memory_usage": {
                "description": "Memory consumption",
                "unit": "megabytes",
                "type": "float",
                "aggregations": ["avg", "max"]
            },
            "res.token_usage": {
                "description": "LLM tokens consumed",
                "unit": "count",
                "type": "integer",
                "aggregations": ["sum", "avg"]
            },
            
            # Quality metrics
            "qual.accuracy": {
                "description": "Correctness of output",
                "unit": "percentage",
                "type": "float",
                "aggregations": ["avg"]
            },
            "qual.error_rate": {
                "description": "Frequency of errors",
                "unit": "percentage",
                "type": "float",
                "aggregations": ["avg"]
            },
            
            # Intelligence metrics
            "intel.reasoning": {
                "description": "Logical reasoning capability",
                "unit": "score (0-100)",
                "type": "float",
                "aggregations": ["avg"]
            },
            "intel.knowledge": {
                "description": "Knowledge representation & recall",
                "unit": "score (0-100)",
                "type": "float",
                "aggregations": ["avg"]
            },
            
            # Usage metrics
            "usage.request_count": {
                "description": "Number of requests received",
                "unit": "count",
                "type": "integer",
                "aggregations": ["sum"]
            },
            "usage.feature_usage": {
                "description": "Usage of specific features",
                "unit": "count",
                "type": "integer",
                "aggregations": ["sum"]
            },
            
            # Collaboration metrics
            "collab.info_sharing": {
                "description": "Context exchange between components",
                "unit": "score (0-5)",
                "type": "float",
                "aggregations": ["avg"]
            },
            "collab.synergy_factor": {
                "description": "Performance improvement from collaboration",
                "unit": "percentage",
                "type": "float",
                "aggregations": ["avg"]
            },
            
            # Operational metrics
            "ops.uptime": {
                "description": "System availability",
                "unit": "percentage",
                "type": "float",
                "aggregations": ["avg"]
            },
            "ops.error_count": {
                "description": "Number of errors",
                "unit": "count",
                "type": "integer",
                "aggregations": ["sum"]
            }
        }
        
        return True
        
    async def _validate_metric(self, metric: Dict[str, Any]) -> bool:
        """
        Validate a metric against its definition.
        
        Args:
            metric: The metric to validate
            
        Returns:
            True if the metric is valid
        """
        metric_id = metric.get("metric_id")
        
        # Check if the metric type is defined
        if metric_id not in self.metric_definitions:
            # Accept undefined metrics but log a warning
            logger.warning(f"Unknown metric type: {metric_id}")
            return True
            
        # Get the definition
        definition = self.metric_definitions[metric_id]
        
        # Check value type
        value = metric.get("value")
        if definition["type"] == "float":
            if not isinstance(value, (int, float)) and not isinstance(value, str):
                logger.error(f"Invalid value type for {metric_id}: expected float, got {type(value)}")
                return False
                
            if isinstance(value, str):
                try:
                    float(value)
                except ValueError:
                    logger.error(f"Invalid value for {metric_id}: could not convert to float: {value}")
                    return False
        elif definition["type"] == "integer":
            if not isinstance(value, int) and not isinstance(value, str):
                logger.error(f"Invalid value type for {metric_id}: expected integer, got {type(value)}")
                return False
                
            if isinstance(value, str):
                try:
                    int(value)
                except ValueError:
                    logger.error(f"Invalid value for {metric_id}: could not convert to integer: {value}")
                    return False
                    
        return True
    
    def get_metric_definition(self, metric_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the definition for a metric type.
        
        Args:
            metric_id: The metric ID
            
        Returns:
            Metric definition or None if not found
        """
        return self.metric_definitions.get(metric_id)
        
    def get_available_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all available metric definitions.
        
        Returns:
            Dictionary of metric definitions
        """
        return self.metric_definitions
    
    async def _start_polling_tasks(self) -> bool:
        """
        Start background tasks for polling metrics from components.
        
        Returns:
            True if successful
        """
        try:
            # Start system resource monitoring
            self.polling_tasks["system_resources"] = asyncio.create_task(
                self._poll_system_resources()
            )
            
            # Start component health monitoring
            self.polling_tasks["component_health"] = asyncio.create_task(
                self._poll_component_health()
            )
            
            # Start database maintenance task
            self.polling_tasks["database_maintenance"] = asyncio.create_task(
                self._database_maintenance_task()
            )
            
            logger.info("Started all metrics polling tasks")
            return True
            
        except Exception as e:
            logger.error(f"Error starting polling tasks: {str(e)}")
            return False
    
    async def _close_persistent_storage(self) -> bool:
        """
        Close persistent storage connections.
        
        Returns:
            True if successful
        """
        try:
            # Close database connection if open
            if self.database:
                await self.database.close()
                logger.info("Closed database connection")
            
            # Clear memory store periodically to prevent memory leaks
            if hasattr(self.store, 'memory_store') and len(self.store.memory_store) > 50000:
                # Keep only recent 10000 records
                self.store.memory_store = self.store.memory_store[-10000:]
                self.store._rebuild_indices()
                logger.info("Trimmed memory store for memory efficiency")
            
            return True
            
        except Exception as e:
            logger.error(f"Error closing persistent storage: {str(e)}")
            return False
    
    async def _poll_system_resources(self) -> None:
        """Poll system resource metrics."""
        try:
            while not self._shutdown_flag:
                # Use wait_for to make sleep interruptible
                try:
                    await asyncio.wait_for(asyncio.sleep(30), timeout=10.0)  # Poll every 30 seconds
                except asyncio.TimeoutError:
                    # Check shutdown flag every 10 seconds
                    continue
                
                if self._shutdown_flag:
                    break
                    
                try:
                    # Record basic system metrics
                    await self._collect_system_metrics()
                    
                except Exception as e:
                    logger.error(f"Error collecting system metrics: {str(e)}")
                    
        except asyncio.CancelledError:
            logger.info("System resource polling task cancelled")
        except Exception as e:
            logger.error(f"Unexpected error in system resource polling: {str(e)}")
    
    async def _poll_component_health(self) -> None:
        """Poll component health metrics."""
        try:
            while not self._shutdown_flag:
                # Use wait_for to make sleep interruptible
                try:
                    await asyncio.wait_for(asyncio.sleep(60), timeout=10.0)  # Poll every minute
                except asyncio.TimeoutError:
                    # Check shutdown flag every 10 seconds
                    continue
                
                if self._shutdown_flag:
                    break
                    
                try:
                    # Record component health metrics
                    await self._collect_component_health_metrics()
                    
                except Exception as e:
                    logger.error(f"Error collecting component health metrics: {str(e)}")
                    
        except asyncio.CancelledError:
            logger.info("Component health polling task cancelled")
        except Exception as e:
            logger.error(f"Unexpected error in component health polling: {str(e)}")
    
    async def _database_maintenance_task(self) -> None:
        """Perform periodic database maintenance."""
        try:
            while not self._shutdown_flag:
                # Use wait_for to make sleep interruptible
                try:
                    await asyncio.wait_for(asyncio.sleep(3600), timeout=10.0)  # Run every hour
                except asyncio.TimeoutError:
                    # Check shutdown flag every 10 seconds
                    continue
                
                if self._shutdown_flag:
                    break
                    
                try:
                    # Clean up old metrics (keep last 7 days)
                    if self.database:
                        cutoff_time = (datetime.utcnow() - timedelta(days=7)).isoformat() + "Z"
                        await self.database.connection.execute(
                            "DELETE FROM metrics WHERE timestamp < ?", (cutoff_time,)
                        )
                        await self.database.connection.commit()
                        logger.info("Cleaned up old metrics from database")
                    
                    # Clear old cache entries
                    current_time = datetime.utcnow()
                    expired_keys = [
                        key for key, expiry in self.store.cache_expiry.items()
                        if current_time > expiry
                    ]
                    
                    for key in expired_keys:
                        if key in self.store.aggregation_cache:
                            del self.store.aggregation_cache[key]
                        if key in self.store.cache_expiry:
                            del self.store.cache_expiry[key]
                    
                    if expired_keys:
                        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
                    
                except Exception as e:
                    logger.error(f"Error in database maintenance: {str(e)}")
                    
        except asyncio.CancelledError:
            logger.info("Database maintenance task cancelled")
        except Exception as e:
            logger.error(f"Unexpected error in database maintenance: {str(e)}")
    
    async def _collect_system_metrics(self) -> None:
        """Collect basic system metrics."""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            await self.record_metric(
                metric_id="res.cpu_usage",
                value=cpu_percent,
                source="system",
                tags=["system", "resource"]
            )
            
            # Memory usage
            memory = psutil.virtual_memory()
            await self.record_metric(
                metric_id="res.memory_usage",
                value=memory.used / (1024 * 1024),  # MB
                source="system",
                tags=["system", "resource"]
            )
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            await self.record_metric(
                metric_id="res.disk_usage",
                value=disk_usage_percent,
                source="system",
                tags=["system", "resource"]
            )
            
        except ImportError:
            # psutil not available, collect basic metrics
            await self.record_metric(
                metric_id="ops.uptime",
                value=100.0,  # Assume system is up if we're running
                source="system",
                tags=["system", "operational"]
            )
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
    
    async def _collect_component_health_metrics(self) -> None:
        """Collect component health metrics."""
        try:
            # Record that the metrics engine itself is healthy
            await self.record_metric(
                metric_id="ops.uptime",
                value=100.0,
                source="sophia_metrics_engine",
                tags=["sophia", "operational"]
            )
            
            # Record metrics collection rate
            current_time = datetime.utcnow()
            recent_metrics = await self.store.query_metrics(
                start_time=(current_time - timedelta(minutes=5)).isoformat() + "Z",
                end_time=current_time.isoformat() + "Z",
                limit=1000
            )
            
            metrics_per_minute = len(recent_metrics) / 5.0
            await self.record_metric(
                metric_id="perf.throughput",
                value=metrics_per_minute,
                source="sophia_metrics_engine",
                tags=["sophia", "performance"]
            )
            
            # Record database performance if available
            if self.database:
                start_time = time.time()
                await self.database.connection.execute("SELECT COUNT(*) FROM metrics")
                query_time = (time.time() - start_time) * 1000  # ms
                
                await self.record_metric(
                    metric_id="perf.processing_time",
                    value=query_time,
                    source="sophia_database",
                    tags=["sophia", "database", "performance"]
                )
            
        except Exception as e:
            logger.error(f"Error collecting component health metrics: {str(e)}")

# Global singleton instance
_metrics_engine = MetricsEngine()

async def get_metrics_engine() -> MetricsEngine:
    """
    Get the global metrics engine instance.
    
    Returns:
        MetricsEngine instance
    """
    if not _metrics_engine.is_initialized:
        await _metrics_engine.initialize()
    return _metrics_engine