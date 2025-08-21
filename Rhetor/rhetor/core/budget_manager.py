"""
Budget management system for tracking and controlling LLM API costs.

This module provides a budget manager that tracks token usage and costs across
different LLM providers, enforces budget limits, and provides reporting capabilities.
"""

import os
from shared.env import TektonEnviron
import json
import logging
import sqlite3
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union

try:
    from litellm import token_counter
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    logging.warning("litellm not installed. Token counting will be less accurate.")

logger = logging.getLogger(__name__)

class BudgetPolicy(str, Enum):
    """Budget enforcement policies"""
    IGNORE = "ignore"  # Track but don't take action
    WARN = "warn"      # Show warnings when approaching limits
    ENFORCE = "enforce"  # Prevent usage when limits exceeded

class BudgetPeriod(str, Enum):
    """Budget period types"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class BudgetManager:
    """Manages LLM usage budgets and tracks costs"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the budget manager.

        Args:
            db_path: Path to the SQLite database file. Defaults to Rhetor component directory
        """
        if db_path:
            self.db_path = db_path
        else:
            # Store in Rhetor component directory
            rhetor_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            self.db_path = os.path.join(rhetor_dir, "rhetor.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Model pricing for various providers in USD
        self.pricing = {
            "anthropic": {
                "claude-3-opus-20240229": {
                    "input_cost_per_token": 0.000015,
                    "output_cost_per_token": 0.000075,
                },
                "claude-3-sonnet-20240229": {
                    "input_cost_per_token": 0.000003,
                    "output_cost_per_token": 0.000015,
                },
                "claude-3-haiku-20240307": {
                    "input_cost_per_token": 0.00000025,
                    "output_cost_per_token": 0.00000125,
                },
                "claude-3-5-sonnet-20240620": {
                    "input_cost_per_token": 0.000003,
                    "output_cost_per_token": 0.000013,
                }
            },
            "openai": {
                "gpt-4": {
                    "input_cost_per_token": 0.00003,
                    "output_cost_per_token": 0.00006,
                },
                "gpt-4-turbo": {
                    "input_cost_per_token": 0.00001,
                    "output_cost_per_token": 0.00003,
                },
                "gpt-4o": {
                    "input_cost_per_token": 0.00001,
                    "output_cost_per_token": 0.00003,
                },
                "gpt-3.5-turbo": {
                    "input_cost_per_token": 0.0000005,
                    "output_cost_per_token": 0.0000015,
                }
            },
            "ollama": {  # Local models are free
                "llama3": {
                    "input_cost_per_token": 0.0,
                    "output_cost_per_token": 0.0,
                }
            },
            "simulated": {  # Simulated provider is free
                "simulated-standard": {
                    "input_cost_per_token": 0.0,
                    "output_cost_per_token": 0.0,
                }
            }
        }
        
        # Load environment variables for policy configuration
        self.default_policy = TektonEnviron.get("RHETOR_BUDGET_POLICY", BudgetPolicy.WARN)
        
        # Initialize the database
        self._init_db()
        
        # Try to load the default budget limit if not already set
        default_daily_limit = float(TektonEnviron.get("RHETOR_BUDGET_DAILY_LIMIT", "0"))
        if default_daily_limit > 0:
            self._set_budget_if_not_exists(BudgetPeriod.DAILY, default_daily_limit)
            
        default_weekly_limit = float(TektonEnviron.get("RHETOR_BUDGET_WEEKLY_LIMIT", "0"))
        if default_weekly_limit > 0:
            self._set_budget_if_not_exists(BudgetPeriod.WEEKLY, default_weekly_limit)
            
        default_monthly_limit = float(TektonEnviron.get("RHETOR_BUDGET_MONTHLY_LIMIT", "0"))
        if default_monthly_limit > 0:
            self._set_budget_if_not_exists(BudgetPeriod.MONTHLY, default_monthly_limit)
    
    def _init_db(self):
        """Initialize the database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create usage tracking table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            provider TEXT,
            model TEXT,
            component TEXT,
            task_type TEXT,
            input_tokens INTEGER,
            output_tokens INTEGER,
            cost REAL,
            metadata TEXT
        )
        ''')
        
        # Create budget settings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS budget_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            period TEXT,  -- daily, weekly, monthly
            provider TEXT,  -- specific provider or 'all'
            limit_amount REAL,
            enforcement TEXT,  -- ignore, warn, enforce
            start_date TEXT,
            active INTEGER
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _set_budget_if_not_exists(self, period: BudgetPeriod, limit_amount: float):
        """
        Set budget if it doesn't already exist.
        
        Args:
            period: Budget period (daily, weekly, monthly)
            limit_amount: Budget limit amount
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if budget exists
        cursor.execute(
            "SELECT COUNT(*) FROM budget_settings WHERE period = ? AND provider = ? AND active = 1",
            (period.value, "all")
        )
        count = cursor.fetchone()[0]
        
        # If no budget exists, create one
        if count == 0:
            cursor.execute(
                """
                INSERT INTO budget_settings 
                (period, provider, limit_amount, enforcement, start_date, active)
                VALUES (?, ?, ?, ?, ?, 1)
                """,
                (
                    period.value,
                    "all",
                    limit_amount,
                    self.default_policy,
                    datetime.now().isoformat()
                )
            )
            
            conn.commit()
            logger.info(f"Set default {period.value} budget to ${limit_amount}")
        
        conn.close()
    
    def count_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """
        Count tokens in text using appropriate tokenizer.
        
        Args:
            text: Text to count tokens in
            model: Model to use for token counting
            
        Returns:
            Number of tokens
        """
        if not text:
            return 0
            
        if LITELLM_AVAILABLE:
            # Use litellm for accurate token counting
            return token_counter(model=model, text=text)
        else:
            # Fallback approximation method (words / 0.75)
            return len(text.split()) + int(len(text) / 4)
    
    def calculate_cost(
        self, 
        provider: str, 
        model: str, 
        input_text: str, 
        output_text: str
    ) -> Dict[str, Any]:
        """
        Calculate the cost of a request using appropriate token counter.
        
        Args:
            provider: Provider name (anthropic, openai, etc.)
            model: Model name
            input_text: Input text
            output_text: Output text
            
        Returns:
            Dictionary with token counts and costs
        """
        # Count tokens
        input_tokens = self.count_tokens(input_text, model)
        output_tokens = self.count_tokens(output_text, model)
        
        # Get costs per token
        model_pricing = self.pricing.get(provider, {}).get(model, {})
        input_cost_per_token = model_pricing.get("input_cost_per_token", 0)
        output_cost_per_token = model_pricing.get("output_cost_per_token", 0)
        
        # Calculate total cost
        input_cost = input_tokens * input_cost_per_token
        output_cost = output_tokens * output_cost_per_token
        total_cost = input_cost + output_cost
        
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost
        }
    
    def estimate_cost(
        self, 
        provider: str, 
        model: str, 
        input_text: str, 
        estimated_output_length: int = 500
    ) -> Dict[str, Any]:
        """
        Estimate the cost of a request before making it.
        
        Args:
            provider: Provider name
            model: Model name
            input_text: Input text
            estimated_output_length: Estimated output length in characters
            
        Returns:
            Dictionary with estimated token counts and costs
        """
        # For estimation, we create a dummy output text with the estimated length
        estimated_output = "a" * estimated_output_length
        return self.calculate_cost(provider, model, input_text, estimated_output)
    
    def record_usage(
        self,
        provider: str,
        model: str,
        component: str,
        task_type: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Record usage data in the database.
        
        Args:
            provider: Provider name
            model: Model name
            component: Component name that made the request
            task_type: Type of task (code, chat, etc.)
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cost: Total cost in USD
            metadata: Additional metadata
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO usage 
            (timestamp, provider, model, component, task_type, input_tokens, output_tokens, cost, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(),
                provider,
                model,
                component,
                task_type,
                input_tokens,
                output_tokens,
                cost,
                json.dumps(metadata or {})
            )
        )
        
        conn.commit()
        conn.close()
    
    def get_usage(
        self, 
        period: Union[BudgetPeriod, str] = BudgetPeriod.DAILY,
        provider: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get usage data for a specific period.
        
        Args:
            period: Budget period (daily, weekly, monthly) or "custom"
            provider: Optional provider name to filter by
            start_date: Custom start date (required if period is "custom")
            end_date: Custom end date (defaults to now if period is "custom")
            
        Returns:
            List of usage records
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Calculate date range based on period
        now = datetime.now()
        
        if isinstance(period, str) and period != "custom":
            period = BudgetPeriod(period)
        
        if period == BudgetPeriod.DAILY:
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == BudgetPeriod.WEEKLY:
            # Start of week (Monday)
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == BudgetPeriod.MONTHLY:
            # Start of month
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "custom" and start_date is None:
            # Custom period requires start_date
            raise ValueError("Custom period requires start_date parameter")
        
        end_date = end_date or now
        
        # Build query
        query = "SELECT * FROM usage WHERE timestamp >= ? AND timestamp <= ?"
        params = [start_date.isoformat(), end_date.isoformat()]
        
        if provider:
            query += " AND provider = ?"
            params.append(provider)
        
        # Execute query
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert to list of dicts
        result = []
        for row in rows:
            record = dict(row)
            # Parse JSON metadata
            if record["metadata"]:
                record["metadata"] = json.loads(record["metadata"])
            result.append(record)
        
        conn.close()
        
        return result
    
    def get_current_usage_total(
        self, 
        period: Union[BudgetPeriod, str] = BudgetPeriod.DAILY,
        provider: Optional[str] = None
    ) -> float:
        """
        Get the total cost of usage for the current period.
        
        Args:
            period: Budget period (daily, weekly, monthly)
            provider: Optional provider name to filter by
            
        Returns:
            Total cost for the period
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate date range based on period
        now = datetime.now()
        
        if isinstance(period, str):
            period = BudgetPeriod(period)
            
        if period == BudgetPeriod.DAILY:
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == BudgetPeriod.WEEKLY:
            # Start of week (Monday)
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == BudgetPeriod.MONTHLY:
            # Start of month
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Build query
        query = "SELECT SUM(cost) FROM usage WHERE timestamp >= ?"
        params = [start_date.isoformat()]
        
        if provider:
            query += " AND provider = ?"
            params.append(provider)
        
        # Execute query
        cursor.execute(query, params)
        total = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return float(total)
    
    def get_budget_limit(self, period: Union[BudgetPeriod, str], provider: str = "all") -> float:
        """
        Get the budget limit for a period.
        
        Args:
            period: Budget period (daily, weekly, monthly)
            provider: Provider name or "all" for global limit
            
        Returns:
            Budget limit amount (0 if no limit set)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if isinstance(period, str):
            period = BudgetPeriod(period)
        
        cursor.execute(
            "SELECT limit_amount FROM budget_settings WHERE period = ? AND provider = ? AND active = 1",
            (period.value, provider)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        return float(row[0]) if row else 0.0
    
    def set_budget_limit(
        self, 
        period: Union[BudgetPeriod, str], 
        limit_amount: float,
        provider: str = "all",
        enforcement: Optional[Union[BudgetPolicy, str]] = None
    ) -> bool:
        """
        Set the budget limit for a period.
        
        Args:
            period: Budget period (daily, weekly, monthly)
            limit_amount: Budget limit amount
            provider: Provider name or "all" for global limit
            enforcement: Budget enforcement policy (ignore, warn, enforce)
            
        Returns:
            True if successful
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if isinstance(period, str):
            period = BudgetPeriod(period)
            
        if isinstance(enforcement, str):
            enforcement = BudgetPolicy(enforcement)
            
        enforcement = enforcement or self.default_policy
        
        # Deactivate any existing budget for this period/provider
        cursor.execute(
            "UPDATE budget_settings SET active = 0 WHERE period = ? AND provider = ? AND active = 1",
            (period.value, provider)
        )
        
        # Create new budget setting
        cursor.execute(
            """
            INSERT INTO budget_settings 
            (period, provider, limit_amount, enforcement, start_date, active)
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (
                period.value,
                provider,
                limit_amount,
                enforcement.value,
                datetime.now().isoformat()
            )
        )
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_enforcement_policy(self, period: Union[BudgetPeriod, str], provider: str = "all") -> str:
        """
        Get the budget enforcement policy for a period.
        
        Args:
            period: Budget period (daily, weekly, monthly)
            provider: Provider name or "all" for global policy
            
        Returns:
            Budget enforcement policy (ignore, warn, enforce)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if isinstance(period, str):
            period = BudgetPeriod(period)
        
        cursor.execute(
            "SELECT enforcement FROM budget_settings WHERE period = ? AND provider = ? AND active = 1",
            (period.value, provider)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else self.default_policy
    
    def set_enforcement_policy(
        self, 
        period: Union[BudgetPeriod, str], 
        policy: Union[BudgetPolicy, str],
        provider: str = "all"
    ) -> bool:
        """
        Set the budget enforcement policy for a period.
        
        Args:
            period: Budget period (daily, weekly, monthly)
            policy: Budget enforcement policy (ignore, warn, enforce)
            provider: Provider name or "all" for global policy
            
        Returns:
            True if successful
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if isinstance(period, str):
            period = BudgetPeriod(period)
            
        if isinstance(policy, str):
            policy = BudgetPolicy(policy)
        
        cursor.execute(
            "UPDATE budget_settings SET enforcement = ? WHERE period = ? AND provider = ? AND active = 1",
            (policy.value, period.value, provider)
        )
        
        if cursor.rowcount == 0:
            # No existing budget, create one with default limit (0)
            cursor.execute(
                """
                INSERT INTO budget_settings 
                (period, provider, limit_amount, enforcement, start_date, active)
                VALUES (?, ?, 0, ?, ?, 1)
                """,
                (
                    period.value,
                    provider,
                    policy.value,
                    datetime.now().isoformat()
                )
            )
        
        conn.commit()
        conn.close()
        
        return True
    
    def check_budget(
        self, 
        provider: str, 
        model: str, 
        input_text: str,
        component: str = "unknown",
        task_type: str = "default"
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request is within budget limits.
        
        Args:
            provider: Provider name
            model: Model name
            input_text: Input text
            component: Component making the request
            task_type: Type of task
            
        Returns:
            Tuple of (True if allowed, info dict with details)
        """
        # Estimate cost
        cost_estimate = self.estimate_cost(provider, model, input_text)
        estimated_cost = cost_estimate["total_cost"]
        
        # If cost is 0, always allow
        if estimated_cost == 0:
            return True, {
                "allowed": True,
                "reason": "Free model",
                "cost_estimate": cost_estimate
            }
        
        # Check daily budget first
        daily_usage = self.get_current_usage_total(BudgetPeriod.DAILY, provider)
        daily_limit = self.get_budget_limit(BudgetPeriod.DAILY, provider)
        daily_policy = self.get_enforcement_policy(BudgetPeriod.DAILY, provider)
        
        daily_exceeded = False
        if daily_limit > 0 and daily_usage + estimated_cost > daily_limit:
            daily_exceeded = True
            if daily_policy == BudgetPolicy.ENFORCE.value:
                return False, {
                    "allowed": False,
                    "reason": "Daily budget limit exceeded",
                    "limit": daily_limit,
                    "usage": daily_usage,
                    "estimated_cost": estimated_cost,
                    "policy": daily_policy,
                    "cost_estimate": cost_estimate
                }
        
        # Check weekly budget
        weekly_usage = self.get_current_usage_total(BudgetPeriod.WEEKLY, provider)
        weekly_limit = self.get_budget_limit(BudgetPeriod.WEEKLY, provider)
        weekly_policy = self.get_enforcement_policy(BudgetPeriod.WEEKLY, provider)
        
        weekly_exceeded = False
        if weekly_limit > 0 and weekly_usage + estimated_cost > weekly_limit:
            weekly_exceeded = True
            if weekly_policy == BudgetPolicy.ENFORCE.value:
                return False, {
                    "allowed": False,
                    "reason": "Weekly budget limit exceeded",
                    "limit": weekly_limit,
                    "usage": weekly_usage,
                    "estimated_cost": estimated_cost,
                    "policy": weekly_policy,
                    "cost_estimate": cost_estimate
                }
        
        # Check monthly budget
        monthly_usage = self.get_current_usage_total(BudgetPeriod.MONTHLY, provider)
        monthly_limit = self.get_budget_limit(BudgetPeriod.MONTHLY, provider)
        monthly_policy = self.get_enforcement_policy(BudgetPeriod.MONTHLY, provider)
        
        monthly_exceeded = False
        if monthly_limit > 0 and monthly_usage + estimated_cost > monthly_limit:
            monthly_exceeded = True
            if monthly_policy == BudgetPolicy.ENFORCE.value:
                return False, {
                    "allowed": False,
                    "reason": "Monthly budget limit exceeded",
                    "limit": monthly_limit,
                    "usage": monthly_usage,
                    "estimated_cost": estimated_cost,
                    "policy": monthly_policy,
                    "cost_estimate": cost_estimate
                }
        
        # If we get here, the request is allowed, but we might need to warn
        warnings = []
        
        if daily_exceeded and daily_policy == BudgetPolicy.WARN.value:
            warnings.append(f"Daily budget limit of ${daily_limit:.2f} will be exceeded (current: ${daily_usage:.2f})")
            
        if weekly_exceeded and weekly_policy == BudgetPolicy.WARN.value:
            warnings.append(f"Weekly budget limit of ${weekly_limit:.2f} will be exceeded (current: ${weekly_usage:.2f})")
            
        if monthly_exceeded and monthly_policy == BudgetPolicy.WARN.value:
            warnings.append(f"Monthly budget limit of ${monthly_limit:.2f} will be exceeded (current: ${monthly_usage:.2f})")
        
        return True, {
            "allowed": True,
            "warnings": warnings,
            "daily_usage": daily_usage,
            "weekly_usage": weekly_usage,
            "monthly_usage": monthly_usage,
            "daily_limit": daily_limit,
            "weekly_limit": weekly_limit,
            "monthly_limit": monthly_limit,
            "estimated_cost": estimated_cost,
            "cost_estimate": cost_estimate
        }
    
    def record_completion(
        self,
        provider: str,
        model: str,
        input_text: str,
        output_text: str,
        component: str = "unknown",
        task_type: str = "default",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record a completed LLM request.
        
        Args:
            provider: Provider name
            model: Model name
            input_text: Input text
            output_text: Output text
            component: Component that made the request
            task_type: Type of task
            metadata: Additional metadata
            
        Returns:
            Dictionary with usage data
        """
        # Calculate cost
        cost_data = self.calculate_cost(provider, model, input_text, output_text)
        
        # Record in database
        self.record_usage(
            provider=provider,
            model=model,
            component=component,
            task_type=task_type,
            input_tokens=cost_data["input_tokens"],
            output_tokens=cost_data["output_tokens"],
            cost=cost_data["total_cost"],
            metadata=metadata
        )
        
        return {
            "provider": provider,
            "model": model,
            "component": component,
            "task_type": task_type,
            "timestamp": datetime.now().isoformat(),
            "input_tokens": cost_data["input_tokens"],
            "output_tokens": cost_data["output_tokens"],
            "input_cost": cost_data["input_cost"],
            "output_cost": cost_data["output_cost"],
            "total_cost": cost_data["total_cost"]
        }
    
    def get_usage_summary(
        self, 
        period: Union[BudgetPeriod, str] = BudgetPeriod.DAILY,
        group_by: str = "provider"
    ) -> Dict[str, Any]:
        """
        Get a summary of usage for a period, grouped by provider, model, or component.
        
        Args:
            period: Budget period (daily, weekly, monthly)
            group_by: Field to group by (provider, model, component, task_type)
            
        Returns:
            Dictionary with usage summary
        """
        usage = self.get_usage(period)
        
        if not usage:
            return {
                "period": period.value if isinstance(period, BudgetPeriod) else period,
                "total_cost": 0.0,
                "total_tokens": 0,
                "groups": {}
            }
        
        # Group by specified field
        groups = {}
        for record in usage:
            key = record[group_by]
            
            if key not in groups:
                groups[key] = {
                    "cost": 0.0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "count": 0
                }
            
            groups[key]["cost"] += record["cost"]
            groups[key]["input_tokens"] += record["input_tokens"]
            groups[key]["output_tokens"] += record["output_tokens"]
            groups[key]["count"] += 1
        
        # Calculate totals
        total_cost = sum(record["cost"] for record in usage)
        total_input_tokens = sum(record["input_tokens"] for record in usage)
        total_output_tokens = sum(record["output_tokens"] for record in usage)
        
        return {
            "period": period.value if isinstance(period, BudgetPeriod) else period,
            "total_cost": total_cost,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,
            "count": len(usage),
            "groups": groups
        }
    
    def get_budget_settings(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all active budget settings.
        
        Returns:
            Dictionary with budget settings by period
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM budget_settings WHERE active = 1")
        rows = cursor.fetchall()
        
        result = {
            "daily": [],
            "weekly": [],
            "monthly": []
        }
        
        for row in rows:
            period = row["period"]
            if period not in result:
                result[period] = []
                
            result[period].append({
                "id": row["id"],
                "provider": row["provider"],
                "limit_amount": row["limit_amount"],
                "enforcement": row["enforcement"],
                "start_date": row["start_date"]
            })
        
        conn.close()
        
        return result
    
    def get_model_tiers(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get models categorized by pricing tier.
        
        Returns:
            Dictionary with models by tier
        """
        tiers = {
            "free": [],
            "low": [],
            "medium": [],
            "high": []
        }
        
        for provider, models in self.pricing.items():
            for model, pricing in models.items():
                cost_per_1k = (pricing["input_cost_per_token"] + pricing["output_cost_per_token"]) * 1000
                
                if cost_per_1k == 0:
                    tier = "free"
                elif cost_per_1k < 0.01:
                    tier = "low"
                elif cost_per_1k < 0.05:
                    tier = "medium"
                else:
                    tier = "high"
                
                tiers[tier].append({
                    "provider": provider,
                    "model": model,
                    "cost_per_1k_tokens": cost_per_1k
                })
        
        return tiers
    
    def find_cheaper_alternative(
        self, 
        provider: str, 
        model: str, 
        task_type: str = "default"
    ) -> Optional[Tuple[str, str]]:
        """
        Find a cheaper alternative model for a given provider/model.
        
        Args:
            provider: Current provider
            model: Current model
            task_type: Task type for consideration
            
        Returns:
            Tuple of (provider, model) or None if no cheaper alternative
        """
        # Get the cost of the current model
        current_cost = 0
        current_model_info = self.pricing.get(provider, {}).get(model, {})
        if current_model_info:
            current_cost = current_model_info["input_cost_per_token"] + current_model_info["output_cost_per_token"]
        
        # If already free, no cheaper alternative
        if current_cost == 0:
            return None
        
        # Model selection preferences by task type
        task_preferences = {
            "code": ["anthropic", "openai", "ollama"],  # Code tasks prefer Claude, then GPT
            "planning": ["anthropic", "openai", "ollama"],  # Planning tasks work well on most
            "reasoning": ["anthropic", "openai", "ollama"],  # Reasoning tasks work well on most
            "chat": ["openai", "anthropic", "ollama"],  # Chat can work well on many models
            "default": ["anthropic", "openai", "ollama"]  # Default ordering
        }
        
        # Use task preferences or default
        preferred_order = task_preferences.get(task_type, task_preferences["default"])
        
        # Find all models cheaper than current model
        cheaper_alternatives = []
        for alt_provider, models in self.pricing.items():
            for alt_model, pricing in models.items():
                alt_cost = pricing["input_cost_per_token"] + pricing["output_cost_per_token"]
                
                if alt_cost < current_cost:
                    cheaper_alternatives.append({
                        "provider": alt_provider,
                        "model": alt_model,
                        "cost": alt_cost
                    })
        
        if not cheaper_alternatives:
            return None
        
        # Sort by preference and then by cost
        def sort_key(alt):
            provider_pref = preferred_order.index(alt["provider"]) if alt["provider"] in preferred_order else 99
            return (provider_pref, alt["cost"])
            
        cheaper_alternatives.sort(key=sort_key)
        
        # Return the best alternative
        best = cheaper_alternatives[0]
        return best["provider"], best["model"]
    
    def route_with_budget_awareness(
        self,
        input_text: str,
        task_type: str,
        default_provider: str,
        default_model: str,
        component: str = "unknown"
    ) -> Tuple[str, str, List[str]]:
        """
        Route a request with budget awareness.
        
        Args:
            input_text: Input text for cost estimation
            task_type: Type of task (code, chat, etc.)
            default_provider: Default provider
            default_model: Default model
            component: Component making the request
            
        Returns:
            Tuple of (provider, model, warnings)
        """
        # Check if the default model is within budget
        allowed, info = self.check_budget(
            provider=default_provider,
            model=default_model,
            input_text=input_text,
            component=component,
            task_type=task_type
        )
        
        # If allowed, use the default model but return any warnings
        if allowed:
            warnings = info.get("warnings", [])
            return default_provider, default_model, warnings
        
        # If not allowed, find a cheaper alternative
        alternative = self.find_cheaper_alternative(
            provider=default_provider,
            model=default_model,
            task_type=task_type
        )
        
        if alternative:
            alt_provider, alt_model = alternative
            
            # Check if the alternative is within budget
            alt_allowed, alt_info = self.check_budget(
                provider=alt_provider,
                model=alt_model,
                input_text=input_text,
                component=component,
                task_type=task_type
            )
            
            if alt_allowed:
                warnings = alt_info.get("warnings", [])
                downgrade_warning = f"Budget limit exceeded. Downgraded from {default_provider}/{default_model} to {alt_provider}/{alt_model}"
                warnings.append(downgrade_warning)
                return alt_provider, alt_model, warnings
        
        # If no affordable alternative, use a free model
        free_models = self.get_model_tiers()["free"]
        if free_models:
            # Prefer Ollama for free models, then simulated
            for provider_pref in ["ollama", "simulated"]:
                for model_info in free_models:
                    if model_info["provider"] == provider_pref:
                        downgrade_warning = f"Budget limit exceeded. Using free model {provider_pref}/{model_info['model']}"
                        return provider_pref, model_info["model"], [downgrade_warning]
            
            # If no preferred free model, use the first available
            model_info = free_models[0]
            downgrade_warning = f"Budget limit exceeded. Using free model {model_info['provider']}/{model_info['model']}"
            return model_info["provider"], model_info["model"], [downgrade_warning]
        
        # If no free models, use the cheapest model regardless of budget
        # This is a last resort when budget enforcement is enabled but we need to provide a response
        cheapest = None
        min_cost = float('inf')
        
        for provider, models in self.pricing.items():
            for model, pricing in models.items():
                cost = pricing["input_cost_per_token"] + pricing["output_cost_per_token"]
                if cost < min_cost:
                    min_cost = cost
                    cheapest = (provider, model)
        
        if cheapest:
            downgrade_warning = f"Budget limit exceeded. Using cheapest model {cheapest[0]}/{cheapest[1]}"
            return cheapest[0], cheapest[1], [downgrade_warning]
        
        # If somehow we have no models at all, use the default as a fallback
        emergency_warning = "Budget limit exceeded but no alternatives available. Using default model."
        return default_provider, default_model, [emergency_warning]