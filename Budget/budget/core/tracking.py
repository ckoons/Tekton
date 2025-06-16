"""
Budget Tracking System

This module provides functionality for tracking token and cost usage
across different time periods, components, and providers.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple

# Try to import debug_utils from shared if available
try:
    from shared.debug.debug_utils import debug_log, log_function
except ImportError:
    # Create a simple fallback if shared module is not available
    class DebugLog:
        def __getattr__(self, name):
            def dummy_log(*args, **kwargs):
                pass
            return dummy_log
    debug_log = DebugLog()
    
    def log_function(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# Import models and constants
from budget.data.models import (
    BudgetTier, BudgetPeriod, BudgetPolicyType, TaskPriority,
    UsageRecord
)

# Import repositories
from budget.data.repository import (
    budget_repo, policy_repo, allocation_repo, usage_repo,
    alert_repo, pricing_repo
)


class UsageTracker:
    """
    Tracks token and cost usage across different dimensions.
    
    This class provides functionality for tracking, analyzing,
    and reporting on token and cost usage.
    """
    
    def __init__(self):
        """Initialize the usage tracker."""
        # Usage counters for in-memory tracking
        self.period_counters = {}
        
    @log_function()
    def update_usage_counter(
        self,
        period: BudgetPeriod,
        budget_id: Optional[str] = None,
        tier: Optional[BudgetTier] = None,
        provider: Optional[str] = None,
        component: Optional[str] = None,
        task_type: Optional[str] = None,
        tokens: int = 0,
        cost: float = 0.0
    ):
        """
        Update the in-memory usage counter for a specific period and criteria.
        
        Args:
            period: Budget period
            budget_id: Budget ID (optional)
            tier: Budget tier (optional)
            provider: Provider name (optional)
            component: Component name (optional)
            task_type: Task type (optional)
            tokens: Number of tokens to add
            cost: Cost to add
        """
        if tokens <= 0 and cost <= 0.0:
            return
            
        # Create counter key
        key = f"{period.value}"
        if budget_id:
            key += f":budget={budget_id}"
        if tier:
            key += f":tier={tier.value}"
        if provider:
            key += f":provider={provider}"
        if component:
            key += f":component={component}"
        if task_type:
            key += f":task={task_type}"
            
        # Get or create counter for this key
        if key not in self.period_counters:
            self.period_counters[key] = {}
            
        # Get period key
        period_key = self._get_period_key(period)
        
        # Update counter
        if period_key not in self.period_counters[key]:
            self.period_counters[key][period_key] = {
                "tokens": 0,
                "cost": 0.0
            }
            
        self.period_counters[key][period_key]["tokens"] += tokens
        self.period_counters[key][period_key]["cost"] += cost
        
        debug_log.debug("budget_tracking", 
                      f"Updated usage counter for {key}/{period_key}: "
                      f"+{tokens} tokens, +${cost:.6f}")
        
    @log_function()
    def _get_period_key(self, period: BudgetPeriod, now: Optional[datetime] = None) -> str:
        """
        Get the key for a budget period.
        
        Args:
            period: Budget period
            now: Current datetime (default: now)
            
        Returns:
            String key for the period
        """
        if now is None:
            now = datetime.now()
            
        if period == BudgetPeriod.HOURLY:
            return now.strftime("%Y-%m-%d-%H")
        elif period == BudgetPeriod.DAILY:
            return now.strftime("%Y-%m-%d")
        elif period == BudgetPeriod.WEEKLY:
            # ISO week format (year, week number)
            return f"{now.isocalendar()[0]}-W{now.isocalendar()[1]}"
        elif period == BudgetPeriod.MONTHLY:
            return now.strftime("%Y-%m")
        else:
            # For PER_SESSION and PER_TASK, use timestamp
            return str(int(now.timestamp()))
        
    @log_function()
    def _get_period_start_end(
        self, 
        period: BudgetPeriod,
        now: Optional[datetime] = None
    ) -> Tuple[datetime, datetime]:
        """
        Get the start and end datetimes for a budget period.
        
        Args:
            period: Budget period
            now: Current datetime (default: now)
            
        Returns:
            Tuple of (start_datetime, end_datetime)
        """
        if now is None:
            now = datetime.now()
            
        if period == BudgetPeriod.HOURLY:
            start = datetime(now.year, now.month, now.day, now.hour, 0, 0)
            end = start + timedelta(hours=1)
        elif period == BudgetPeriod.DAILY:
            start = datetime(now.year, now.month, now.day, 0, 0, 0)
            end = start + timedelta(days=1)
        elif period == BudgetPeriod.WEEKLY:
            # Start of the ISO week (Monday)
            start = datetime.fromisocalendar(now.isocalendar()[0], now.isocalendar()[1], 1)
            end = start + timedelta(days=7)
        elif period == BudgetPeriod.MONTHLY:
            start = datetime(now.year, now.month, 1, 0, 0, 0)
            # Handle different month lengths
            if now.month == 12:
                end = datetime(now.year + 1, 1, 1, 0, 0, 0)
            else:
                end = datetime(now.year, now.month + 1, 1, 0, 0, 0)
        else:
            # For PER_SESSION and PER_TASK, use the current time
            start = now
            end = now + timedelta(days=1)  # Default expiration
            
        return (start, end)
        
    @log_function()
    def get_usage_from_memory(
        self,
        period: BudgetPeriod,
        budget_id: Optional[str] = None,
        tier: Optional[BudgetTier] = None,
        provider: Optional[str] = None,
        component: Optional[str] = None,
        task_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get usage data from in-memory counters.
        
        Args:
            period: Budget period
            budget_id: Budget ID (optional)
            tier: Budget tier (optional)
            provider: Provider name (optional)
            component: Component name (optional)
            task_type: Task type (optional)
            
        Returns:
            Dictionary with usage data
        """
        # Create counter key
        key = f"{period.value}"
        if budget_id:
            key += f":budget={budget_id}"
        if tier:
            key += f":tier={tier.value}"
        if provider:
            key += f":provider={provider}"
        if component:
            key += f":component={component}"
        if task_type:
            key += f":task={task_type}"
            
        # Check if counter exists
        if key not in self.period_counters:
            return {
                "tokens": 0,
                "cost": 0.0
            }
            
        # Get period key
        period_key = self._get_period_key(period)
        
        # Get usage for this period
        if period_key not in self.period_counters[key]:
            return {
                "tokens": 0,
                "cost": 0.0
            }
            
        return self.period_counters[key][period_key].copy()
        
    @log_function()
    def get_usage_history(
        self,
        period: BudgetPeriod,
        days: int = 30,
        budget_id: Optional[str] = None,
        provider: Optional[str] = None,
        component: Optional[str] = None,
        model: Optional[str] = None,
        task_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get historical usage data for a period.
        
        Args:
            period: Budget period
            days: Number of days to include in history
            budget_id: Budget ID (optional)
            provider: Provider name (optional)
            component: Component name (optional)
            model: Model name (optional)
            task_type: Task type (optional)
            
        Returns:
            List of usage records by period
        """
        debug_log.info("budget_tracking", 
                     f"Getting usage history for {period.value} over {days} days")
        
        # Calculate start and end dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get usage records from repository
        records = usage_repo.get_usage_for_period(
            period=BudgetPeriod.DAILY,  # Always get daily data for granularity
            budget_id=budget_id,
            provider=provider,
            component=component,
            model=model,
            task_type=task_type,
            start_time=start_date,
            end_time=end_date
        )
        
        # Group records by period
        history = []
        
        if period == BudgetPeriod.DAILY:
            # Group by day
            days_data = {}
            
            for record in records:
                day_key = record.timestamp.strftime("%Y-%m-%d")
                
                if day_key not in days_data:
                    days_data[day_key] = {
                        "period": day_key,
                        "date": record.timestamp.replace(hour=0, minute=0, second=0, microsecond=0),
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "total_tokens": 0,
                        "total_cost": 0.0,
                        "count": 0
                    }
                    
                days_data[day_key]["input_tokens"] += record.input_tokens
                days_data[day_key]["output_tokens"] += record.output_tokens
                days_data[day_key]["total_tokens"] += record.input_tokens + record.output_tokens
                days_data[day_key]["total_cost"] += record.total_cost
                days_data[day_key]["count"] += 1
                
            # Convert to list and sort by date
            history = list(days_data.values())
            history.sort(key=lambda x: x["date"])
            
        elif period == BudgetPeriod.WEEKLY:
            # Group by week
            weeks_data = {}
            
            for record in records:
                week_key = f"{record.timestamp.isocalendar()[0]}-W{record.timestamp.isocalendar()[1]}"
                week_start = datetime.fromisocalendar(
                    record.timestamp.isocalendar()[0], 
                    record.timestamp.isocalendar()[1], 
                    1
                )
                
                if week_key not in weeks_data:
                    weeks_data[week_key] = {
                        "period": week_key,
                        "date": week_start,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "total_tokens": 0,
                        "total_cost": 0.0,
                        "count": 0
                    }
                    
                weeks_data[week_key]["input_tokens"] += record.input_tokens
                weeks_data[week_key]["output_tokens"] += record.output_tokens
                weeks_data[week_key]["total_tokens"] += record.input_tokens + record.output_tokens
                weeks_data[week_key]["total_cost"] += record.total_cost
                weeks_data[week_key]["count"] += 1
                
            # Convert to list and sort by date
            history = list(weeks_data.values())
            history.sort(key=lambda x: x["date"])
            
        elif period == BudgetPeriod.MONTHLY:
            # Group by month
            months_data = {}
            
            for record in records:
                month_key = record.timestamp.strftime("%Y-%m")
                month_start = datetime(record.timestamp.year, record.timestamp.month, 1)
                
                if month_key not in months_data:
                    months_data[month_key] = {
                        "period": month_key,
                        "date": month_start,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "total_tokens": 0,
                        "total_cost": 0.0,
                        "count": 0
                    }
                    
                months_data[month_key]["input_tokens"] += record.input_tokens
                months_data[month_key]["output_tokens"] += record.output_tokens
                months_data[month_key]["total_tokens"] += record.input_tokens + record.output_tokens
                months_data[month_key]["total_cost"] += record.total_cost
                months_data[month_key]["count"] += 1
                
            # Convert to list and sort by date
            history = list(months_data.values())
            history.sort(key=lambda x: x["date"])
            
        else:
            # For other periods, group by day as fallback
            return self.get_usage_history(
                period=BudgetPeriod.DAILY,
                days=days,
                budget_id=budget_id,
                provider=provider,
                component=component,
                model=model,
                task_type=task_type
            )
            
        debug_log.info("budget_tracking", 
                     f"Generated usage history with {len(history)} periods")
        
        return history
        
    @log_function()
    def analyze_usage_patterns(
        self,
        period: BudgetPeriod = BudgetPeriod.DAILY,
        days: int = 30,
        budget_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze usage patterns to identify trends and optimization opportunities.
        
        Args:
            period: Budget period
            days: Number of days to include in analysis
            budget_id: Budget ID (optional)
            
        Returns:
            Dictionary with usage pattern analysis
        """
        debug_log.info("budget_tracking", 
                     f"Analyzing usage patterns for {period.value} over {days} days")
        
        # Get usage history
        history = self.get_usage_history(
            period=period,
            days=days,
            budget_id=budget_id
        )
        
        if not history:
            debug_log.warn("budget_tracking", "No usage data for pattern analysis")
            return {
                "trends": [],
                "patterns": [],
                "anomalies": [],
                "recommendations": []
            }
            
        # Calculate trend (simple linear trend)
        tokens_trend = []
        cost_trend = []
        
        for entry in history:
            tokens_trend.append(entry["total_tokens"])
            cost_trend.append(entry["total_cost"])
            
        # Calculate trend direction
        tokens_trend_direction = "stable"
        if len(tokens_trend) >= 3:
            first_half = sum(tokens_trend[:len(tokens_trend)//2]) / (len(tokens_trend)//2)
            second_half = sum(tokens_trend[len(tokens_trend)//2:]) / (len(tokens_trend) - len(tokens_trend)//2)
            
            if second_half > first_half * 1.1:
                tokens_trend_direction = "increasing"
            elif second_half < first_half * 0.9:
                tokens_trend_direction = "decreasing"
                
        cost_trend_direction = "stable"
        if len(cost_trend) >= 3:
            first_half = sum(cost_trend[:len(cost_trend)//2]) / (len(cost_trend)//2)
            second_half = sum(cost_trend[len(cost_trend)//2:]) / (len(cost_trend) - len(cost_trend)//2)
            
            if second_half > first_half * 1.1:
                cost_trend_direction = "increasing"
            elif second_half < first_half * 0.9:
                cost_trend_direction = "decreasing"
                
        # Calculate averages
        avg_tokens = sum(tokens_trend) / len(tokens_trend) if tokens_trend else 0
        avg_cost = sum(cost_trend) / len(cost_trend) if cost_trend else 0
        
        # Detect anomalies (simple threshold-based)
        anomalies = []
        
        for i, entry in enumerate(history):
            # Check for token anomalies
            if entry["total_tokens"] > avg_tokens * 1.5:
                anomalies.append({
                    "type": "token_spike",
                    "period": entry["period"],
                    "value": entry["total_tokens"],
                    "average": avg_tokens,
                    "deviation": entry["total_tokens"] / avg_tokens if avg_tokens > 0 else 0
                })
                
            # Check for cost anomalies
            if entry["total_cost"] > avg_cost * 1.5:
                anomalies.append({
                    "type": "cost_spike",
                    "period": entry["period"],
                    "value": entry["total_cost"],
                    "average": avg_cost,
                    "deviation": entry["total_cost"] / avg_cost if avg_cost > 0 else 0
                })
                
        # Generate recommendations
        recommendations = []
        
        if tokens_trend_direction == "increasing":
            recommendations.append({
                "type": "token_usage",
                "description": "Token usage is trending upward",
                "recommendation": "Review recent changes in usage patterns and consider optimization strategies"
            })
            
        if cost_trend_direction == "increasing":
            recommendations.append({
                "type": "cost_control",
                "description": "Cost is trending upward",
                "recommendation": "Consider implementing stricter budget controls or switching to more cost-effective models"
            })
            
        if anomalies:
            recommendations.append({
                "type": "anomaly_investigation",
                "description": f"Detected {len(anomalies)} usage anomalies",
                "recommendation": "Investigate periods with unusually high usage to identify potential optimization opportunities"
            })
            
        # Compile analysis
        analysis = {
            "trends": [
                {
                    "type": "tokens",
                    "direction": tokens_trend_direction,
                    "average": avg_tokens,
                    "values": tokens_trend
                },
                {
                    "type": "cost",
                    "direction": cost_trend_direction,
                    "average": avg_cost,
                    "values": cost_trend
                }
            ],
            "patterns": [
                {
                    "type": "weekly_pattern",
                    "description": "Not enough data for weekly pattern analysis"
                }
            ],
            "anomalies": anomalies,
            "recommendations": recommendations
        }
        
        debug_log.info("budget_tracking", 
                     f"Completed usage pattern analysis with {len(recommendations)} recommendations")
        
        return analysis
        
    @log_function()
    def process_usage_record(
        self,
        record: UsageRecord
    ):
        """
        Process a usage record for tracking and analysis.
        
        Args:
            record: Usage record to process
        """
        debug_log.debug("budget_tracking", 
                      f"Processing usage record {record.record_id}")
        
        # Update in-memory counters for all periods
        for period in [BudgetPeriod.HOURLY, BudgetPeriod.DAILY, 
                      BudgetPeriod.WEEKLY, BudgetPeriod.MONTHLY]:
                      
            # Update global counter
            self.update_usage_counter(
                period=period,
                tokens=record.input_tokens + record.output_tokens,
                cost=record.total_cost
            )
            
            # Update budget-specific counter if applicable
            if record.budget_id:
                self.update_usage_counter(
                    period=period,
                    budget_id=record.budget_id,
                    tokens=record.input_tokens + record.output_tokens,
                    cost=record.total_cost
                )
                
            # Update provider counter
            self.update_usage_counter(
                period=period,
                provider=record.provider,
                tokens=record.input_tokens + record.output_tokens,
                cost=record.total_cost
            )
            
            # Update model counter
            self.update_usage_counter(
                period=period,
                provider=record.provider,
                model=record.model,
                tokens=record.input_tokens + record.output_tokens,
                cost=record.total_cost
            )
            
            # Update component counter
            self.update_usage_counter(
                period=period,
                component=record.component,
                tokens=record.input_tokens + record.output_tokens,
                cost=record.total_cost
            )
            
            # Update task type counter
            self.update_usage_counter(
                period=period,
                task_type=record.task_type,
                tokens=record.input_tokens + record.output_tokens,
                cost=record.total_cost
            )


# Create singleton instance
usage_tracker = UsageTracker()

# Legacy alias for backward compatibility
tracking_manager = usage_tracker