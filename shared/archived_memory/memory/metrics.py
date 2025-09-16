"""
Memory Metrics System for Tekton CIs
Measures and optimizes memory effectiveness, performance, and quality.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, Counter
import statistics
import json

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of memory metrics."""
    # Storage metrics
    STORAGE_COUNT = "storage_count"
    STORAGE_SIZE = "storage_size"
    STORAGE_LATENCY = "storage_latency"
    
    # Retrieval metrics
    RETRIEVAL_COUNT = "retrieval_count"
    RETRIEVAL_LATENCY = "retrieval_latency"
    RETRIEVAL_PRECISION = "retrieval_precision"
    RETRIEVAL_RECALL = "retrieval_recall"
    
    # Quality metrics
    RELEVANCE_SCORE = "relevance_score"
    CONTEXT_IMPROVEMENT = "context_improvement"
    DECISION_INFLUENCE = "decision_influence"
    
    # Performance metrics
    CACHE_HIT_RATE = "cache_hit_rate"
    MEMORY_THROUGHPUT = "memory_throughput"
    ERROR_RATE = "error_rate"
    
    # Learning metrics
    CONSOLIDATION_RATE = "consolidation_rate"
    FORGETTING_CURVE = "forgetting_curve"
    LEARNING_VELOCITY = "learning_velocity"
    
    # Collective metrics
    SHARING_FREQUENCY = "sharing_frequency"
    COLLABORATION_SCORE = "collaboration_score"
    KNOWLEDGE_DIFFUSION = "knowledge_diffusion"


@dataclass
class MetricValue:
    """A single metric measurement."""
    metric_type: MetricType
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    ci_name: Optional[str] = None
    namespace: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricAggregation:
    """Aggregated metric statistics."""
    metric_type: MetricType
    count: int
    mean: float
    median: float
    std_dev: float
    min_value: float
    max_value: float
    percentile_95: float
    trend: str  # "increasing", "decreasing", "stable"
    period_start: datetime
    period_end: datetime


@dataclass
class MemoryHealthScore:
    """Overall memory system health score."""
    overall_score: float  # 0-100
    storage_health: float
    retrieval_health: float
    quality_health: float
    performance_health: float
    learning_health: float
    recommendations: List[str] = field(default_factory=list)


class MemoryMetrics:
    """
    Memory metrics collection and analysis system.
    
    Tracks memory system performance, quality, and effectiveness.
    """
    
    def __init__(self):
        self.metrics: Dict[MetricType, List[MetricValue]] = defaultdict(list)
        self.ci_metrics: Dict[str, Dict[MetricType, List[MetricValue]]] = defaultdict(lambda: defaultdict(list))
        self.aggregations: Dict[MetricType, MetricAggregation] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.optimization_history: List[Dict[str, Any]] = []
        
    # Storage Metrics
    
    async def record_storage(
        self,
        ci_name: str,
        size: int,
        latency_ms: float,
        success: bool = True
    ):
        """Record memory storage metrics."""
        # Record count
        self.record_metric(
            MetricType.STORAGE_COUNT,
            1.0,
            ci_name=ci_name,
            metadata={'success': success}
        )
        
        # Record size
        self.record_metric(
            MetricType.STORAGE_SIZE,
            float(size),
            ci_name=ci_name
        )
        
        # Record latency
        self.record_metric(
            MetricType.STORAGE_LATENCY,
            latency_ms,
            ci_name=ci_name
        )
        
        # Check for performance issues
        if latency_ms > 100:
            await self._create_alert(
                'high_storage_latency',
                f"Storage latency {latency_ms}ms exceeds 100ms for {ci_name}"
            )
    
    # Retrieval Metrics
    
    async def record_retrieval(
        self,
        ci_name: str,
        query: str,
        results_count: int,
        relevant_count: int,
        total_possible: int,
        latency_ms: float
    ):
        """Record memory retrieval metrics."""
        # Record count
        self.record_metric(
            MetricType.RETRIEVAL_COUNT,
            1.0,
            ci_name=ci_name
        )
        
        # Record latency
        self.record_metric(
            MetricType.RETRIEVAL_LATENCY,
            latency_ms,
            ci_name=ci_name
        )
        
        # Calculate precision (relevant results / total results)
        if results_count > 0:
            precision = relevant_count / results_count
            self.record_metric(
                MetricType.RETRIEVAL_PRECISION,
                precision,
                ci_name=ci_name,
                metadata={'query': query}
            )
        
        # Calculate recall (relevant results / total possible relevant)
        if total_possible > 0:
            recall = relevant_count / total_possible
            self.record_metric(
                MetricType.RETRIEVAL_RECALL,
                recall,
                ci_name=ci_name,
                metadata={'query': query}
            )
    
    # Quality Metrics
    
    async def record_relevance(
        self,
        ci_name: str,
        memory_id: str,
        relevance_score: float
    ):
        """Record memory relevance score."""
        self.record_metric(
            MetricType.RELEVANCE_SCORE,
            relevance_score,
            ci_name=ci_name,
            metadata={'memory_id': memory_id}
        )
    
    async def record_context_improvement(
        self,
        ci_name: str,
        before_score: float,
        after_score: float
    ):
        """Record context improvement from memory injection."""
        improvement = (after_score - before_score) / before_score if before_score > 0 else 0
        
        self.record_metric(
            MetricType.CONTEXT_IMPROVEMENT,
            improvement,
            ci_name=ci_name,
            metadata={
                'before': before_score,
                'after': after_score
            }
        )
    
    async def record_decision_influence(
        self,
        ci_name: str,
        decision_id: str,
        memory_influence: float
    ):
        """Record how much memory influenced a decision."""
        self.record_metric(
            MetricType.DECISION_INFLUENCE,
            memory_influence,
            ci_name=ci_name,
            metadata={'decision_id': decision_id}
        )
    
    # Performance Metrics
    
    async def record_cache_hit(
        self,
        ci_name: str,
        cache_hit: bool
    ):
        """Record cache hit/miss."""
        self.record_metric(
            MetricType.CACHE_HIT_RATE,
            1.0 if cache_hit else 0.0,
            ci_name=ci_name
        )
    
    async def record_throughput(
        self,
        ci_name: str,
        operations_per_second: float
    ):
        """Record memory operation throughput."""
        self.record_metric(
            MetricType.MEMORY_THROUGHPUT,
            operations_per_second,
            ci_name=ci_name
        )
    
    async def record_error(
        self,
        ci_name: str,
        error_type: str,
        error_message: str
    ):
        """Record memory system error."""
        self.record_metric(
            MetricType.ERROR_RATE,
            1.0,
            ci_name=ci_name,
            metadata={
                'error_type': error_type,
                'error_message': error_message
            }
        )
        
        await self._create_alert(
            'memory_error',
            f"Memory error for {ci_name}: {error_type}"
        )
    
    # Learning Metrics
    
    async def record_consolidation(
        self,
        ci_name: str,
        memories_consolidated: int,
        time_taken_ms: float
    ):
        """Record memory consolidation event."""
        self.record_metric(
            MetricType.CONSOLIDATION_RATE,
            float(memories_consolidated),
            ci_name=ci_name,
            metadata={'time_taken': time_taken_ms}
        )
    
    async def record_forgetting(
        self,
        ci_name: str,
        memory_age_hours: float,
        recall_probability: float
    ):
        """Record forgetting curve data point."""
        self.record_metric(
            MetricType.FORGETTING_CURVE,
            recall_probability,
            ci_name=ci_name,
            metadata={'age_hours': memory_age_hours}
        )
    
    async def record_learning(
        self,
        ci_name: str,
        new_knowledge_items: int,
        integration_time_ms: float
    ):
        """Record learning velocity."""
        velocity = new_knowledge_items / (integration_time_ms / 1000) if integration_time_ms > 0 else 0
        
        self.record_metric(
            MetricType.LEARNING_VELOCITY,
            velocity,
            ci_name=ci_name,
            metadata={
                'items': new_knowledge_items,
                'time': integration_time_ms
            }
        )
    
    # Collective Metrics
    
    async def record_sharing(
        self,
        from_ci: str,
        to_ci: str,
        memory_type: str
    ):
        """Record memory sharing event."""
        self.record_metric(
            MetricType.SHARING_FREQUENCY,
            1.0,
            ci_name=from_ci,
            metadata={
                'recipient': to_ci,
                'type': memory_type
            }
        )
    
    async def record_collaboration(
        self,
        ci_names: List[str],
        collaboration_score: float
    ):
        """Record collaboration effectiveness."""
        for ci_name in ci_names:
            self.record_metric(
                MetricType.COLLABORATION_SCORE,
                collaboration_score,
                ci_name=ci_name,
                metadata={'participants': ci_names}
            )
    
    async def record_knowledge_diffusion(
        self,
        source_ci: str,
        spread_count: int,
        time_to_spread_hours: float
    ):
        """Record how knowledge spreads through the CI network."""
        diffusion_rate = spread_count / time_to_spread_hours if time_to_spread_hours > 0 else 0
        
        self.record_metric(
            MetricType.KNOWLEDGE_DIFFUSION,
            diffusion_rate,
            ci_name=source_ci,
            metadata={
                'spread_count': spread_count,
                'time_hours': time_to_spread_hours
            }
        )
    
    # Core metric recording
    
    def record_metric(
        self,
        metric_type: MetricType,
        value: float,
        ci_name: Optional[str] = None,
        namespace: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a metric value."""
        metric = MetricValue(
            metric_type=metric_type,
            value=value,
            ci_name=ci_name,
            namespace=namespace,
            metadata=metadata or {}
        )
        
        # Add to global metrics
        self.metrics[metric_type].append(metric)
        
        # Add to CI-specific metrics
        if ci_name:
            self.ci_metrics[ci_name][metric_type].append(metric)
        
        # Trim old metrics (keep last 10000)
        if len(self.metrics[metric_type]) > 10000:
            self.metrics[metric_type] = self.metrics[metric_type][-10000:]
    
    # Aggregation and Analysis
    
    def aggregate_metrics(
        self,
        metric_type: MetricType,
        period: timedelta = timedelta(hours=1),
        ci_name: Optional[str] = None
    ) -> Optional[MetricAggregation]:
        """Aggregate metrics over a time period."""
        now = datetime.now()
        period_start = now - period
        
        # Get relevant metrics
        if ci_name and ci_name in self.ci_metrics:
            metrics = self.ci_metrics[ci_name][metric_type]
        else:
            metrics = self.metrics[metric_type]
        
        # Filter by time period
        period_metrics = [
            m for m in metrics
            if m.timestamp >= period_start
        ]
        
        if not period_metrics:
            return None
        
        values = [m.value for m in period_metrics]
        
        # Calculate statistics
        aggregation = MetricAggregation(
            metric_type=metric_type,
            count=len(values),
            mean=statistics.mean(values),
            median=statistics.median(values),
            std_dev=statistics.stdev(values) if len(values) > 1 else 0,
            min_value=min(values),
            max_value=max(values),
            percentile_95=sorted(values)[int(len(values) * 0.95)] if values else 0,
            trend=self._calculate_trend(period_metrics),
            period_start=period_start,
            period_end=now
        )
        
        self.aggregations[metric_type] = aggregation
        
        return aggregation
    
    def get_health_score(self) -> MemoryHealthScore:
        """Calculate overall memory health score."""
        # Aggregate recent metrics
        period = timedelta(hours=1)
        
        # Storage health
        storage_latency = self.aggregate_metrics(MetricType.STORAGE_LATENCY, period)
        storage_health = 100 - min((storage_latency.mean if storage_latency else 0) / 2, 100)
        
        # Retrieval health
        retrieval_precision = self.aggregate_metrics(MetricType.RETRIEVAL_PRECISION, period)
        retrieval_recall = self.aggregate_metrics(MetricType.RETRIEVAL_RECALL, period)
        retrieval_health = 50 * (retrieval_precision.mean if retrieval_precision else 0.5) + \
                          50 * (retrieval_recall.mean if retrieval_recall else 0.5)
        
        # Quality health
        relevance = self.aggregate_metrics(MetricType.RELEVANCE_SCORE, period)
        quality_health = 100 * (relevance.mean if relevance else 0.7)
        
        # Performance health
        cache_hits = self.aggregate_metrics(MetricType.CACHE_HIT_RATE, period)
        error_rate = self.aggregate_metrics(MetricType.ERROR_RATE, period)
        performance_health = 50 * (cache_hits.mean if cache_hits else 0.5) + \
                           50 * (1 - min((error_rate.count if error_rate else 0) / 100, 1))
        
        # Learning health
        learning_velocity = self.aggregate_metrics(MetricType.LEARNING_VELOCITY, period)
        learning_health = min(100 * (learning_velocity.mean if learning_velocity else 0.5), 100)
        
        # Overall score
        overall_score = statistics.mean([
            storage_health,
            retrieval_health,
            quality_health,
            performance_health,
            learning_health
        ])
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            storage_health,
            retrieval_health,
            quality_health,
            performance_health,
            learning_health
        )
        
        return MemoryHealthScore(
            overall_score=overall_score,
            storage_health=storage_health,
            retrieval_health=retrieval_health,
            quality_health=quality_health,
            performance_health=performance_health,
            learning_health=learning_health,
            recommendations=recommendations
        )
    
    def get_ci_performance(self, ci_name: str) -> Dict[str, Any]:
        """Get performance metrics for a specific CI."""
        if ci_name not in self.ci_metrics:
            return {}
        
        period = timedelta(hours=1)
        ci_perf = {}
        
        for metric_type in MetricType:
            aggregation = self.aggregate_metrics(metric_type, period, ci_name)
            if aggregation:
                ci_perf[metric_type.value] = {
                    'mean': aggregation.mean,
                    'median': aggregation.median,
                    'count': aggregation.count,
                    'trend': aggregation.trend
                }
        
        return ci_perf
    
    def get_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """Generate optimization suggestions based on metrics."""
        suggestions = []
        
        # Check storage latency
        storage_latency = self.aggregate_metrics(MetricType.STORAGE_LATENCY)
        if storage_latency and storage_latency.mean > 100:
            suggestions.append({
                'type': 'performance',
                'priority': 'high',
                'suggestion': 'Enable write batching to reduce storage latency',
                'impact': 'Could reduce latency by 50%'
            })
        
        # Check cache hit rate
        cache_hits = self.aggregate_metrics(MetricType.CACHE_HIT_RATE)
        if cache_hits and cache_hits.mean < 0.7:
            suggestions.append({
                'type': 'performance',
                'priority': 'medium',
                'suggestion': 'Increase cache size or adjust TTL',
                'impact': 'Could improve hit rate to >80%'
            })
        
        # Check retrieval precision
        precision = self.aggregate_metrics(MetricType.RETRIEVAL_PRECISION)
        if precision and precision.mean < 0.6:
            suggestions.append({
                'type': 'quality',
                'priority': 'high',
                'suggestion': 'Tune relevance scoring algorithm',
                'impact': 'Could improve precision by 20-30%'
            })
        
        # Check error rate
        errors = self.aggregate_metrics(MetricType.ERROR_RATE)
        if errors and errors.count > 10:
            suggestions.append({
                'type': 'reliability',
                'priority': 'critical',
                'suggestion': 'Investigate and fix memory system errors',
                'impact': 'Improve system stability'
            })
        
        return suggestions
    
    # Helper methods
    
    def _calculate_trend(self, metrics: List[MetricValue]) -> str:
        """Calculate trend from metrics."""
        if len(metrics) < 2:
            return "stable"
        
        # Get first half and second half means
        mid = len(metrics) // 2
        first_half = statistics.mean([m.value for m in metrics[:mid]])
        second_half = statistics.mean([m.value for m in metrics[mid:]])
        
        if second_half > first_half * 1.1:
            return "increasing"
        elif second_half < first_half * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    def _generate_recommendations(
        self,
        storage_health: float,
        retrieval_health: float,
        quality_health: float,
        performance_health: float,
        learning_health: float
    ) -> List[str]:
        """Generate health recommendations."""
        recommendations = []
        
        if storage_health < 70:
            recommendations.append("Optimize storage: Consider batching or async writes")
        
        if retrieval_health < 70:
            recommendations.append("Improve retrieval: Tune relevance scoring and indexing")
        
        if quality_health < 70:
            recommendations.append("Enhance quality: Implement better context filtering")
        
        if performance_health < 70:
            recommendations.append("Boost performance: Increase cache size and optimize queries")
        
        if learning_health < 70:
            recommendations.append("Accelerate learning: Increase consolidation frequency")
        
        return recommendations
    
    async def _create_alert(self, alert_type: str, message: str):
        """Create an alert."""
        alert = {
            'type': alert_type,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'resolved': False
        }
        
        self.alerts.append(alert)
        
        # Keep only recent alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        logger.warning(f"Alert: {alert_type} - {message}")
    
    # Export and reporting
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        if format == "json":
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'health_score': self.get_health_score().__dict__,
                'aggregations': {
                    k.value: {
                        'mean': v.mean,
                        'median': v.median,
                        'count': v.count,
                        'trend': v.trend
                    }
                    for k, v in self.aggregations.items()
                },
                'alerts': self.alerts[-10:],  # Last 10 alerts
                'suggestions': self.get_optimization_suggestions()
            }
            
            return json.dumps(export_data, default=str, indent=2)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Global metrics instance
_memory_metrics: Optional[MemoryMetrics] = None


def get_memory_metrics() -> MemoryMetrics:
    """Get the global memory metrics instance."""
    global _memory_metrics
    if _memory_metrics is None:
        _memory_metrics = MemoryMetrics()
    return _memory_metrics


# Metric recording decorators

def track_memory_operation(operation_type: str):
    """Decorator to track memory operation metrics."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            metrics = get_memory_metrics()
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Record success
                latency = (time.time() - start_time) * 1000
                
                if operation_type == "storage":
                    await metrics.record_storage(
                        ci_name=kwargs.get('ci_name', 'unknown'),
                        size=len(str(result)),
                        latency_ms=latency,
                        success=True
                    )
                elif operation_type == "retrieval":
                    await metrics.record_retrieval(
                        ci_name=kwargs.get('ci_name', 'unknown'),
                        query=kwargs.get('query', ''),
                        results_count=len(result) if isinstance(result, list) else 1,
                        relevant_count=len(result) if isinstance(result, list) else 1,
                        total_possible=100,  # Placeholder
                        latency_ms=latency
                    )
                
                return result
                
            except Exception as e:
                # Record error
                await metrics.record_error(
                    ci_name=kwargs.get('ci_name', 'unknown'),
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
                raise
        
        return wrapper
    return decorator