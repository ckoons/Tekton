"""
Memory System Optimizer
Analyzes metrics and automatically optimizes memory operations.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import statistics

from .metrics import (
    MemoryMetrics,
    MetricType,
    HealthScore,
    get_memory_metrics
)
from .middleware import MemoryConfig, MemoryTier, InjectionStyle

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """Memory optimization strategies."""
    CACHE_TUNING = "cache_tuning"
    TIER_REBALANCING = "tier_rebalancing"
    CONSOLIDATION_SCHEDULING = "consolidation_scheduling"
    RELEVANCE_ADJUSTMENT = "relevance_adjustment"
    INJECTION_OPTIMIZATION = "injection_optimization"
    COLLECTIVE_ROUTING = "collective_routing"


class MemoryOptimizer:
    """
    Automatically optimizes memory system based on metrics.
    
    Features:
    - Dynamic cache sizing
    - Tier rebalancing
    - Consolidation scheduling
    - Relevance threshold tuning
    - Injection style selection
    - Collective memory routing
    """
    
    def __init__(self, ci_name: str):
        self.ci_name = ci_name
        self.metrics = get_memory_metrics()
        self.optimization_history: List[Dict] = []
        self.current_config = MemoryConfig(namespace=ci_name)
        
        # Optimization parameters
        self.cache_size_min = 50
        self.cache_size_max = 500
        self.tier_size_limits = {
            MemoryTier.RECENT: (20, 100),
            MemoryTier.SESSION: (100, 1000),
            MemoryTier.DOMAIN: (500, 5000),
            MemoryTier.ASSOCIATIONS: (1000, 10000),
            MemoryTier.COLLECTIVE: (100, 1000)
        }
        
        # Performance targets
        self.target_latency_ms = 50
        self.target_cache_hit_rate = 0.7
        self.target_precision = 0.8
        self.target_recall = 0.6
        
    async def optimize(self) -> Dict[str, Any]:
        """
        Perform comprehensive optimization.
        
        Returns optimization report.
        """
        logger.info(f"Starting memory optimization for {self.ci_name}")
        
        # Get current metrics
        health = self.metrics.get_health_score()
        
        # Determine needed optimizations
        strategies = self._select_strategies(health)
        
        # Apply optimizations
        results = {}
        for strategy in strategies:
            result = await self._apply_strategy(strategy)
            results[strategy.value] = result
        
        # Record optimization
        self.optimization_history.append({
            'timestamp': datetime.now().isoformat(),
            'health_before': health.overall_score,
            'strategies_applied': [s.value for s in strategies],
            'results': results
        })
        
        # Get new health score
        new_health = self.metrics.get_health_score()
        
        return {
            'optimization_complete': True,
            'health_before': health.overall_score,
            'health_after': new_health.overall_score,
            'improvement': new_health.overall_score - health.overall_score,
            'strategies_applied': [s.value for s in strategies],
            'results': results,
            'recommendations': self._generate_recommendations(new_health)
        }
    
    def _select_strategies(self, health: HealthScore) -> List[OptimizationStrategy]:
        """Select optimization strategies based on health metrics."""
        strategies = []
        
        # Check cache performance
        if health.factors.get('cache_hit_rate', 1.0) < self.target_cache_hit_rate:
            strategies.append(OptimizationStrategy.CACHE_TUNING)
        
        # Check retrieval performance  
        if health.factors.get('retrieval_precision', 1.0) < self.target_precision:
            strategies.append(OptimizationStrategy.RELEVANCE_ADJUSTMENT)
        
        # Check latency
        avg_latency = self._get_average_latency()
        if avg_latency > self.target_latency_ms:
            strategies.append(OptimizationStrategy.TIER_REBALANCING)
            strategies.append(OptimizationStrategy.INJECTION_OPTIMIZATION)
        
        # Check memory usage patterns
        if self._needs_consolidation():
            strategies.append(OptimizationStrategy.CONSOLIDATION_SCHEDULING)
        
        # Check collective memory usage
        if self._has_collective_issues():
            strategies.append(OptimizationStrategy.COLLECTIVE_ROUTING)
        
        return strategies
    
    async def _apply_strategy(
        self, 
        strategy: OptimizationStrategy
    ) -> Dict[str, Any]:
        """Apply specific optimization strategy."""
        
        if strategy == OptimizationStrategy.CACHE_TUNING:
            return await self._optimize_cache()
        
        elif strategy == OptimizationStrategy.TIER_REBALANCING:
            return await self._rebalance_tiers()
        
        elif strategy == OptimizationStrategy.CONSOLIDATION_SCHEDULING:
            return await self._optimize_consolidation()
        
        elif strategy == OptimizationStrategy.RELEVANCE_ADJUSTMENT:
            return await self._tune_relevance()
        
        elif strategy == OptimizationStrategy.INJECTION_OPTIMIZATION:
            return await self._optimize_injection()
        
        elif strategy == OptimizationStrategy.COLLECTIVE_ROUTING:
            return await self._optimize_collective()
        
        return {'status': 'not_implemented'}
    
    async def _optimize_cache(self) -> Dict[str, Any]:
        """Optimize cache size and eviction policy."""
        # Get cache metrics
        hit_rate = self._get_cache_hit_rate()
        current_size = self._get_cache_size()
        
        # Calculate optimal size
        if hit_rate < self.target_cache_hit_rate:
            # Increase cache size
            new_size = min(
                int(current_size * 1.5),
                self.cache_size_max
            )
        else:
            # Potentially decrease if hit rate is very high
            if hit_rate > 0.9:
                new_size = max(
                    int(current_size * 0.9),
                    self.cache_size_min
                )
            else:
                new_size = current_size
        
        # Apply new size
        self.current_config.cache_size = new_size
        
        return {
            'cache_size_before': current_size,
            'cache_size_after': new_size,
            'hit_rate': hit_rate,
            'target_hit_rate': self.target_cache_hit_rate
        }
    
    async def _rebalance_tiers(self) -> Dict[str, Any]:
        """Rebalance memory tier sizes based on usage."""
        tier_usage = self._get_tier_usage()
        adjustments = {}
        
        for tier, usage in tier_usage.items():
            min_size, max_size = self.tier_size_limits.get(
                tier, 
                (100, 1000)
            )
            
            # Calculate optimal size based on usage
            if usage['hit_rate'] > 0.8:
                # High usage, increase size
                new_size = min(
                    int(usage['current_size'] * 1.2),
                    max_size
                )
            elif usage['hit_rate'] < 0.3:
                # Low usage, decrease size
                new_size = max(
                    int(usage['current_size'] * 0.8),
                    min_size
                )
            else:
                new_size = usage['current_size']
            
            adjustments[tier.value] = {
                'before': usage['current_size'],
                'after': new_size,
                'hit_rate': usage['hit_rate']
            }
        
        return {
            'tier_adjustments': adjustments,
            'total_memory_before': sum(
                u['current_size'] for u in tier_usage.values()
            ),
            'total_memory_after': sum(
                a['after'] for a in adjustments.values()
            )
        }
    
    async def _optimize_consolidation(self) -> Dict[str, Any]:
        """Optimize memory consolidation scheduling."""
        # Analyze memory growth patterns
        growth_rate = self._calculate_memory_growth_rate()
        
        # Determine consolidation frequency
        if growth_rate > 100:  # High growth
            consolidation_interval = timedelta(minutes=15)
        elif growth_rate > 50:
            consolidation_interval = timedelta(minutes=30)
        else:
            consolidation_interval = timedelta(hours=1)
        
        # Schedule consolidation
        next_consolidation = datetime.now() + consolidation_interval
        
        return {
            'growth_rate_per_hour': growth_rate,
            'consolidation_interval': str(consolidation_interval),
            'next_consolidation': next_consolidation.isoformat(),
            'strategy': 'aggressive' if growth_rate > 100 else 'balanced'
        }
    
    async def _tune_relevance(self) -> Dict[str, Any]:
        """Tune relevance thresholds for better precision."""
        current_precision = self._get_retrieval_precision()
        current_threshold = self.current_config.relevance_threshold
        
        # Adjust threshold
        if current_precision < self.target_precision:
            # Increase threshold for higher precision
            new_threshold = min(current_threshold + 0.05, 0.95)
        elif current_precision > 0.95:
            # Can afford to decrease for better recall
            new_threshold = max(current_threshold - 0.02, 0.5)
        else:
            new_threshold = current_threshold
        
        self.current_config.relevance_threshold = new_threshold
        
        return {
            'threshold_before': current_threshold,
            'threshold_after': new_threshold,
            'precision': current_precision,
            'target_precision': self.target_precision
        }
    
    async def _optimize_injection(self) -> Dict[str, Any]:
        """Optimize memory injection style based on usage patterns."""
        # Analyze CI usage patterns
        patterns = self._analyze_usage_patterns()
        
        # Select optimal injection style
        if patterns['conversational_ratio'] > 0.6:
            optimal_style = InjectionStyle.NATURAL
        elif patterns['analytical_ratio'] > 0.5:
            optimal_style = InjectionStyle.STRUCTURED
        elif patterns['technical_ratio'] > 0.4:
            optimal_style = InjectionStyle.TECHNICAL
        else:
            optimal_style = InjectionStyle.MINIMAL
        
        previous_style = self.current_config.injection_style
        self.current_config.injection_style = optimal_style
        
        return {
            'style_before': previous_style.value,
            'style_after': optimal_style.value,
            'usage_patterns': patterns,
            'reason': self._explain_style_choice(patterns, optimal_style)
        }
    
    async def _optimize_collective(self) -> Dict[str, Any]:
        """Optimize collective memory routing and sharing."""
        # Analyze sharing patterns
        sharing_stats = self._get_sharing_statistics()
        
        optimizations = []
        
        # Optimize channel subscriptions
        if sharing_stats['unused_channels']:
            for channel in sharing_stats['unused_channels']:
                # Unsubscribe from unused channels
                optimizations.append({
                    'action': 'unsubscribe',
                    'channel': channel
                })
        
        # Optimize sharing frequency
        if sharing_stats['oversharing_rate'] > 0.3:
            optimizations.append({
                'action': 'reduce_sharing',
                'current_rate': sharing_stats['share_rate'],
                'target_rate': sharing_stats['share_rate'] * 0.7
            })
        
        # Optimize memory types shared
        if sharing_stats['irrelevant_shares'] > 0.2:
            optimizations.append({
                'action': 'filter_sharing',
                'filter_threshold': 0.8
            })
        
        return {
            'optimizations_applied': optimizations,
            'channels_optimized': len(sharing_stats['unused_channels']),
            'efficiency_improvement': self._calculate_collective_efficiency(
                sharing_stats,
                optimizations
            )
        }
    
    def _get_average_latency(self) -> float:
        """Get average operation latency."""
        storage_metrics = self.metrics.aggregate_metrics(
            MetricType.STORAGE_LATENCY,
            timedelta(hours=1)
        )
        retrieval_metrics = self.metrics.aggregate_metrics(
            MetricType.RETRIEVAL_LATENCY,
            timedelta(hours=1)
        )
        
        latencies = []
        if storage_metrics:
            latencies.append(storage_metrics.mean)
        if retrieval_metrics:
            latencies.append(retrieval_metrics.mean)
        
        return statistics.mean(latencies) if latencies else 0
    
    def _get_cache_hit_rate(self) -> float:
        """Get current cache hit rate."""
        hits = self.metrics.aggregate_metrics(
            MetricType.CACHE_HIT,
            timedelta(hours=1)
        )
        
        if not hits:
            return 0
        
        return hits.mean
    
    def _get_cache_size(self) -> int:
        """Get current cache size."""
        return self.current_config.cache_size or 100
    
    def _get_tier_usage(self) -> Dict[MemoryTier, Dict]:
        """Get usage statistics per memory tier."""
        # This would integrate with actual memory backend
        # Placeholder implementation
        return {
            MemoryTier.RECENT: {
                'current_size': 50,
                'hit_rate': 0.85,
                'growth_rate': 10
            },
            MemoryTier.SESSION: {
                'current_size': 200,
                'hit_rate': 0.65,
                'growth_rate': 20
            },
            MemoryTier.DOMAIN: {
                'current_size': 1000,
                'hit_rate': 0.45,
                'growth_rate': 5
            }
        }
    
    def _needs_consolidation(self) -> bool:
        """Check if memory needs consolidation."""
        growth_rate = self._calculate_memory_growth_rate()
        return growth_rate > 50
    
    def _has_collective_issues(self) -> bool:
        """Check if collective memory has issues."""
        sharing_stats = self._get_sharing_statistics()
        return (
            sharing_stats['oversharing_rate'] > 0.3 or
            len(sharing_stats['unused_channels']) > 2
        )
    
    def _calculate_memory_growth_rate(self) -> float:
        """Calculate memory growth rate per hour."""
        storage_metrics = self.metrics.aggregate_metrics(
            MetricType.STORAGE_COUNT,
            timedelta(hours=1)
        )
        
        if not storage_metrics:
            return 0
        
        return storage_metrics.count
    
    def _get_retrieval_precision(self) -> float:
        """Get current retrieval precision."""
        precision_metrics = self.metrics.aggregate_metrics(
            MetricType.RETRIEVAL_PRECISION,
            timedelta(hours=1)
        )
        
        if not precision_metrics:
            return 1.0
        
        return precision_metrics.mean
    
    def _analyze_usage_patterns(self) -> Dict[str, float]:
        """Analyze CI usage patterns."""
        # This would analyze actual usage
        # Placeholder implementation
        return {
            'conversational_ratio': 0.4,
            'analytical_ratio': 0.3,
            'technical_ratio': 0.2,
            'creative_ratio': 0.1
        }
    
    def _explain_style_choice(
        self,
        patterns: Dict[str, float],
        style: InjectionStyle
    ) -> str:
        """Explain why a style was chosen."""
        if style == InjectionStyle.NATURAL:
            return f"Natural style chosen due to high conversational usage ({patterns['conversational_ratio']:.0%})"
        elif style == InjectionStyle.STRUCTURED:
            return f"Structured style chosen due to analytical focus ({patterns['analytical_ratio']:.0%})"
        elif style == InjectionStyle.TECHNICAL:
            return f"Technical style chosen due to technical tasks ({patterns['technical_ratio']:.0%})"
        else:
            return "Minimal style chosen for efficiency"
    
    def _get_sharing_statistics(self) -> Dict[str, Any]:
        """Get collective memory sharing statistics."""
        # Placeholder implementation
        return {
            'share_rate': 10,  # shares per hour
            'oversharing_rate': 0.2,
            'irrelevant_shares': 0.1,
            'unused_channels': ['old_channel_1', 'old_channel_2']
        }
    
    def _calculate_collective_efficiency(
        self,
        stats: Dict,
        optimizations: List[Dict]
    ) -> float:
        """Calculate efficiency improvement from optimizations."""
        base_efficiency = 1.0 - stats['oversharing_rate'] - stats['irrelevant_shares']
        
        # Estimate improvement
        improvement = 0
        for opt in optimizations:
            if opt['action'] == 'unsubscribe':
                improvement += 0.05
            elif opt['action'] == 'reduce_sharing':
                improvement += 0.1
            elif opt['action'] == 'filter_sharing':
                improvement += 0.15
        
        return min(improvement, 0.3)
    
    def _generate_recommendations(self, health: HealthScore) -> List[str]:
        """Generate ongoing recommendations."""
        recommendations = []
        
        if health.overall_score < 70:
            recommendations.append("Consider increasing cache size for better performance")
        
        if health.factors.get('retrieval_precision', 1) < 0.7:
            recommendations.append("Review relevance algorithms for better precision")
        
        if self._get_average_latency() > 100:
            recommendations.append("Consider upgrading storage backend for lower latency")
        
        if not recommendations:
            recommendations.append("System performing well, maintain current configuration")
        
        return recommendations


class AutoOptimizer:
    """
    Automatic continuous optimizer that runs in background.
    """
    
    def __init__(self, ci_name: str, interval: timedelta = timedelta(minutes=30)):
        self.ci_name = ci_name
        self.interval = interval
        self.optimizer = MemoryOptimizer(ci_name)
        self.running = False
        self.task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start automatic optimization."""
        if self.running:
            return
        
        self.running = True
        self.task = asyncio.create_task(self._optimization_loop())
        logger.info(f"Started auto-optimization for {self.ci_name}")
    
    async def stop(self):
        """Stop automatic optimization."""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info(f"Stopped auto-optimization for {self.ci_name}")
    
    async def _optimization_loop(self):
        """Continuous optimization loop."""
        while self.running:
            try:
                # Run optimization
                result = await self.optimizer.optimize()
                
                # Log results
                if result['improvement'] > 0:
                    logger.info(
                        f"Optimization improved health by {result['improvement']:.1f}% "
                        f"for {self.ci_name}"
                    )
                
                # Wait for next cycle
                await asyncio.sleep(self.interval.total_seconds())
                
            except Exception as e:
                logger.error(f"Optimization error for {self.ci_name}: {e}")
                await asyncio.sleep(60)  # Wait before retry


# Singleton auto-optimizers per CI
_auto_optimizers: Dict[str, AutoOptimizer] = {}


async def start_auto_optimization(
    ci_name: str,
    interval: timedelta = timedelta(minutes=30)
) -> AutoOptimizer:
    """
    Start automatic optimization for a CI.
    
    Args:
        ci_name: Name of CI to optimize
        interval: Optimization interval
    
    Returns:
        AutoOptimizer instance
    """
    if ci_name not in _auto_optimizers:
        _auto_optimizers[ci_name] = AutoOptimizer(ci_name, interval)
    
    optimizer = _auto_optimizers[ci_name]
    await optimizer.start()
    
    return optimizer


async def stop_auto_optimization(ci_name: str):
    """Stop automatic optimization for a CI."""
    if ci_name in _auto_optimizers:
        await _auto_optimizers[ci_name].stop()
        del _auto_optimizers[ci_name]


async def optimize_once(ci_name: str) -> Dict[str, Any]:
    """
    Run one-time optimization for a CI.
    
    Returns optimization report.
    """
    optimizer = MemoryOptimizer(ci_name)
    return await optimizer.optimize()