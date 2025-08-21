"""
Token Budget Manager for Apollo.

This module is responsible for allocating and managing token budgets for LLM
operations, tracking usage, and enforcing policies to prevent token exhaustion.
"""

import os
from shared.env import TektonEnviron
import json
import logging
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
import uuid
import heapq

from apollo.models.budget import (
    BudgetTier,
    BudgetPeriod,
    BudgetPolicyType,
    TaskPriority,
    BudgetPolicy,
    BudgetAllocation,
    BudgetUsageRecord,
    BudgetSummary
)

# Try to import landmarks
try:
    from landmarks import state_checkpoint, performance_boundary, architecture_decision
except ImportError:
    # Define no-op decorators if landmarks not available
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

# Configure logging
logger = logging.getLogger(__name__)


@architecture_decision(
    title="Token budget management system",
    rationale="Prevent runaway costs and ensure fair resource allocation across components",
    alternatives_considered=["No limits", "Static quotas", "Pay-per-use"],
    impacts=["cost_control", "performance", "user_experience"],
    decided_by="team"
)
@state_checkpoint(
    title="Token usage tracking",
    state_type="runtime",
    persistence=True,
    consistency_requirements="Atomic updates for usage tracking",
    recovery_strategy="Reload from persistent storage, reset periods if corrupted"
)
class TokenBudgetManager:
    """
    Manages token budgets for LLM operations across components.
    
    This class is responsible for allocating token budgets based on task
    requirements and priorities, tracking token usage, and enforcing budget
    policies to prevent token exhaustion.
    """
    
    # Default token budget limits per tier
    DEFAULT_LIMITS = {
        BudgetTier.LOCAL_LIGHTWEIGHT: {
            BudgetPeriod.HOURLY: 1000000,  # 1M tokens/hour
            BudgetPeriod.DAILY: 10000000,  # 10M tokens/day
            BudgetPeriod.PER_SESSION: 8000  # 8K tokens/session
        },
        BudgetTier.LOCAL_MIDWEIGHT: {
            BudgetPeriod.HOURLY: 500000,  # 500K tokens/hour
            BudgetPeriod.DAILY: 5000000,  # 5M tokens/day
            BudgetPeriod.PER_SESSION: 16000  # 16K tokens/session
        },
        BudgetTier.REMOTE_HEAVYWEIGHT: {
            BudgetPeriod.HOURLY: 100000,  # 100K tokens/hour
            BudgetPeriod.DAILY: 1000000,  # 1M tokens/day
            BudgetPeriod.PER_SESSION: 32000  # 32K tokens/session
        }
    }
    
    # Default token allocation per task type and priority
    DEFAULT_ALLOCATIONS = {
        "default": {
            TaskPriority.LOW: 1000,
            TaskPriority.NORMAL: 2000,
            TaskPriority.HIGH: 4000,
            TaskPriority.CRITICAL: 8000
        },
        "chat": {
            TaskPriority.LOW: 2000,
            TaskPriority.NORMAL: 4000,
            TaskPriority.HIGH: 8000,
            TaskPriority.CRITICAL: 16000
        },
        "coding": {
            TaskPriority.LOW: 4000,
            TaskPriority.NORMAL: 8000,
            TaskPriority.HIGH: 16000,
            TaskPriority.CRITICAL: 32000
        },
        "analysis": {
            TaskPriority.LOW: 4000,
            TaskPriority.NORMAL: 8000,
            TaskPriority.HIGH: 16000,
            TaskPriority.CRITICAL: 32000
        }
    }
    
    def __init__(
        self,
        data_dir: Optional[str] = None,
        policy_file: Optional[str] = None,
        cleanup_interval: float = 3600.0  # 1 hour
    ):
        """
        Initialize the Token Budget Manager.
        
        Args:
            data_dir: Directory for storing budget data
            policy_file: Path to budget policy configuration file
            cleanup_interval: Interval for cleaning up expired allocations (seconds)
        """
        # Set up data directory
        if data_dir:
            self.data_dir = data_dir
        else:
            # Use $TEKTON_DATA_DIR/apollo/budget_data by default
            default_data_dir = os.path.join(
                TektonEnviron.get('TEKTON_DATA_DIR', 
                              os.path.join(TektonEnviron.get('TEKTON_ROOT', os.path.expanduser('~')), '.tekton', 'data')),
                'apollo', 'budget_data'
            )
            self.data_dir = default_data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Set up policy file
        self.policy_file = policy_file or os.path.join(self.data_dir, "budget_policies.json")
        
        # Set cleanup interval
        self.cleanup_interval = cleanup_interval
        
        # Active budget allocations (context_id -> allocation)
        self.allocations: Dict[str, BudgetAllocation] = {}
        
        # Budget policies (policy_id -> policy)
        self.policies: Dict[str, BudgetPolicy] = {}
        
        # Usage records for tracking and analysis
        self.usage_records: List[BudgetUsageRecord] = []
        
        # Usage counters per period
        self.usage_counters: Dict[str, Dict[datetime, int]] = {}
        
        # Priority queue for pending allocations
        self.pending_allocations = []
        
        # Component tiers
        self.component_tiers: Dict[str, BudgetTier] = {}
        
        # Model tiers
        self.model_tiers: Dict[str, BudgetTier] = {
            # Local lightweight models
            "codellama": BudgetTier.LOCAL_LIGHTWEIGHT,
            "deepseek-coder": BudgetTier.LOCAL_LIGHTWEIGHT,
            "starcoder": BudgetTier.LOCAL_LIGHTWEIGHT,
            
            # Local midweight models
            "claude-haiku": BudgetTier.LOCAL_MIDWEIGHT,
            "claude-3-haiku": BudgetTier.LOCAL_MIDWEIGHT,
            "llama-3": BudgetTier.LOCAL_MIDWEIGHT,
            "mistral": BudgetTier.LOCAL_MIDWEIGHT,
            "qwen": BudgetTier.LOCAL_MIDWEIGHT,
            
            # Remote heavyweight models
            "gpt-4": BudgetTier.REMOTE_HEAVYWEIGHT,
            "claude-3-opus": BudgetTier.REMOTE_HEAVYWEIGHT,
            "claude-3-sonnet": BudgetTier.REMOTE_HEAVYWEIGHT,
            "claude-3.5-sonnet": BudgetTier.REMOTE_HEAVYWEIGHT,
            "claude-3.7-sonnet": BudgetTier.REMOTE_HEAVYWEIGHT
        }
        
        # Provider default tiers
        self.provider_tiers: Dict[str, BudgetTier] = {
            "openai": BudgetTier.REMOTE_HEAVYWEIGHT,
            "anthropic": BudgetTier.REMOTE_HEAVYWEIGHT,
            "ollama": BudgetTier.LOCAL_MIDWEIGHT,
            "local": BudgetTier.LOCAL_LIGHTWEIGHT
        }
        
        # Callbacks for budget events
        self.callbacks: Dict[str, List[Callable]] = {
            "on_allocation_created": [],
            "on_allocation_updated": [],
            "on_allocation_expired": [],
            "on_budget_exceeded": [],
            "on_policy_updated": []
        }
        
        # For cleanup task
        self.cleanup_task = None
        self.is_running = False
        
        # Load policies from file
        self._load_policies()
    
    async def start(self):
        """Start the budget management process."""
        if self.is_running:
            logger.warning("Budget management is already running")
            return
        
        self.is_running = True
        
        # Start the cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("Token budget management started")
    
    async def stop(self):
        """Stop the budget management process."""
        if not self.is_running:
            logger.warning("Budget management is not running")
            return
        
        self.is_running = False
        
        # Cancel the cleanup task
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
            
        # Save policies to file
        self._save_policies()
        
        # Save usage records
        self._save_usage_records()
        
        logger.info("Token budget management stopped")
    
    async def _cleanup_loop(self):
        """Periodic task to clean up expired allocations."""
        try:
            while self.is_running:
                self._cleanup_expired_allocations()
                await asyncio.sleep(self.cleanup_interval)
        except asyncio.CancelledError:
            logger.info("Cleanup loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in cleanup loop: {e}")
            self.is_running = False
            raise
    
    def _cleanup_expired_allocations(self):
        """Clean up expired allocations."""
        now = datetime.now()
        expired_ids = []
        
        for allocation_id, allocation in self.allocations.items():
            if allocation.expiration_time and now > allocation.expiration_time:
                expired_ids.append(allocation_id)
                allocation.is_active = False
                
                # Trigger callback
                self._trigger_callback("on_allocation_expired", allocation)
                
        # Remove expired allocations
        for allocation_id in expired_ids:
            logger.info(f"Allocation {allocation_id} expired and removed")
            if allocation_id in self.allocations:
                del self.allocations[allocation_id]
    
    def _determine_tier(
        self, 
        component: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None
    ) -> BudgetTier:
        """
        Determine the appropriate budget tier based on component, provider, and model.
        
        Args:
            component: Component ID
            provider: Provider ID
            model: Model ID
            
        Returns:
            BudgetTier
        """
        # Check if model has a specific tier
        if model and model.lower() in self.model_tiers:
            return self.model_tiers[model.lower()]
            
        # Check if component has a specific tier
        if component and component in self.component_tiers:
            return self.component_tiers[component]
            
        # Check if provider has a default tier
        if provider and provider.lower() in self.provider_tiers:
            return self.provider_tiers[provider.lower()]
            
        # Default to remote heavyweight (most conservative)
        return BudgetTier.REMOTE_HEAVYWEIGHT
    
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
    
    def _get_applicable_policies(
        self,
        tier: BudgetTier,
        component: Optional[str] = None,
        task_type: Optional[str] = None
    ) -> List[BudgetPolicy]:
        """
        Get all policies that apply to a given tier, component, and task type.
        
        Args:
            tier: Budget tier
            component: Component ID (optional)
            task_type: Task type (optional)
            
        Returns:
            List of applicable BudgetPolicy objects
        """
        applicable_policies = []
        
        for policy in self.policies.values():
            # Skip disabled policies
            if not policy.enabled:
                continue
                
            # Skip policies for other tiers
            if policy.tier != tier:
                continue
                
            # Check if policy applies to this component
            if policy.component and component and policy.component != component:
                continue
                
            # Check if policy applies to this task type
            if policy.task_type and task_type and policy.task_type != task_type:
                continue
                
            # Check if policy is still valid (not expired)
            if policy.end_date and datetime.now() > policy.end_date:
                continue
                
            # This policy applies
            applicable_policies.append(policy)
            
        return applicable_policies
    
    def _update_usage_counter(
        self,
        tier: BudgetTier,
        period: BudgetPeriod,
        component: Optional[str] = None,
        task_type: Optional[str] = None,
        tokens: int = 0
    ):
        """
        Update the usage counter for a specific period.
        
        Args:
            tier: Budget tier
            period: Budget period
            component: Component ID (optional)
            task_type: Task type (optional)
            tokens: Number of tokens to add
        """
        if tokens <= 0:
            return
            
        # Create counter key
        key = f"{tier}:{period}"
        if component:
            key += f":{component}"
        if task_type:
            key += f":{task_type}"
            
        # Get or create counter for this key
        if key not in self.usage_counters:
            self.usage_counters[key] = {}
            
        # Get period key
        period_key = self._get_period_key(period)
        
        # Update counter
        if period_key not in self.usage_counters[key]:
            self.usage_counters[key][period_key] = 0
            
        self.usage_counters[key][period_key] += tokens
    
    def _get_usage_for_period(
        self,
        tier: BudgetTier,
        period: BudgetPeriod,
        component: Optional[str] = None,
        task_type: Optional[str] = None
    ) -> int:
        """
        Get the total token usage for a specific period.
        
        Args:
            tier: Budget tier
            period: Budget period
            component: Component ID (optional)
            task_type: Task type (optional)
            
        Returns:
            Total token usage for the period
        """
        # Create counter key
        key = f"{tier}:{period}"
        if component:
            key += f":{component}"
        if task_type:
            key += f":{task_type}"
            
        # Check if counter exists
        if key not in self.usage_counters:
            return 0
            
        # Get period key
        period_key = self._get_period_key(period)
        
        # Get usage for this period
        return self.usage_counters[key].get(period_key, 0)
    
    def _check_budget_exceeded(
        self,
        tier: BudgetTier,
        component: Optional[str] = None,
        task_type: Optional[str] = None
    ) -> List[BudgetPolicy]:
        """
        Check if any budget policies have been exceeded.
        
        Args:
            tier: Budget tier
            component: Component ID (optional)
            task_type: Task type (optional)
            
        Returns:
            List of exceeded BudgetPolicy objects
        """
        exceeded_policies = []
        
        # Get applicable policies
        policies = self._get_applicable_policies(tier, component, task_type)
        
        for policy in policies:
            # Get current usage for this period
            usage = self._get_usage_for_period(
                tier=tier,
                period=policy.period,
                component=component if policy.component else None,
                task_type=task_type if policy.task_type else None
            )
            
            # Check if limit is exceeded
            if usage > policy.limit:
                exceeded_policies.append(policy)
                
                # Trigger callback for exceeded budget
                self._trigger_callback("on_budget_exceeded", policy, usage)
                
        return exceeded_policies
    
    def _trigger_callback(self, event_type: str, *args, **kwargs):
        """
        Trigger registered callbacks for an event.
        
        Args:
            event_type: Type of event
            *args: Arguments to pass to callbacks
            **kwargs: Keyword arguments to pass to callbacks
        """
        if event_type not in self.callbacks:
            return
            
        for callback in self.callbacks[event_type]:
            try:
                # Support both synchronous and asynchronous callbacks
                if asyncio.iscoroutinefunction(callback):
                    # Schedule asynchronous callback
                    asyncio.create_task(callback(*args, **kwargs))
                else:
                    # Call synchronous callback directly
                    callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {event_type} callback: {e}")
    
    def _load_policies(self):
        """Load budget policies from file."""
        try:
            if not os.path.exists(self.policy_file):
                # Create default policies
                logger.info("Creating default budget policies")
                self._create_default_policies()
                self._save_policies()
                return
                
            with open(self.policy_file, "r") as f:
                policies_data = json.load(f)
                
            for policy_data in policies_data:
                # Convert datetimes from strings
                if "start_date" in policy_data:
                    policy_data["start_date"] = datetime.fromisoformat(policy_data["start_date"])
                if "end_date" in policy_data and policy_data["end_date"]:
                    policy_data["end_date"] = datetime.fromisoformat(policy_data["end_date"])
                    
                policy = BudgetPolicy(**policy_data)
                self.policies[policy.policy_id] = policy
                
            logger.info(f"Loaded {len(self.policies)} budget policies")
            
        except Exception as e:
            logger.error(f"Error loading budget policies: {e}")
            # Create default policies
            self._create_default_policies()
    
    def _save_policies(self):
        """Save budget policies to file."""
        try:
            policies_data = []
            
            for policy in self.policies.values():
                policy_dict = policy.model_dump()
                
                # Convert datetimes to strings
                policy_dict["start_date"] = policy_dict["start_date"].isoformat()
                if policy_dict["end_date"]:
                    policy_dict["end_date"] = policy_dict["end_date"].isoformat()
                    
                policies_data.append(policy_dict)
                
            with open(self.policy_file, "w") as f:
                json.dump(policies_data, f, indent=2)
                
            logger.info(f"Saved {len(self.policies)} budget policies")
            
        except Exception as e:
            logger.error(f"Error saving budget policies: {e}")
    
    def _create_default_policies(self):
        """Create default budget policies for each tier and period."""
        self.policies = {}
        
        # Create policies for each tier and period
        for tier, limits in self.DEFAULT_LIMITS.items():
            for period, limit in limits.items():
                policy = BudgetPolicy(
                    type=BudgetPolicyType.WARN,
                    period=period,
                    tier=tier,
                    limit=limit,
                    warning_threshold=0.8,
                    action_threshold=0.95,
                    start_date=datetime.now(),
                    enabled=True
                )
                self.policies[policy.policy_id] = policy
    
    def _save_usage_records(self):
        """Save recent usage records to file."""
        try:
            # Only save the most recent records (last 1000)
            recent_records = self.usage_records[-1000:] if len(self.usage_records) > 1000 else self.usage_records
            
            records_data = []
            for record in recent_records:
                record_dict = record.model_dump()
                record_dict["timestamp"] = record_dict["timestamp"].isoformat()
                records_data.append(record_dict)
                
            # Create filename with timestamp
            filename = os.path.join(self.data_dir, f"usage_records_{int(time.time())}.json")
            
            with open(filename, "w") as f:
                json.dump(records_data, f, indent=2)
                
            logger.info(f"Saved {len(recent_records)} usage records to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving usage records: {e}")
    
    async def allocate_budget(
        self,
        context_id: str,
        component: str,
        task_type: str = "default",
        provider: Optional[str] = None,
        model: Optional[str] = None,
        priority: int = 5,
        token_count: Optional[int] = None,
        expiration: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[BudgetAllocation]:
        """
        Allocate a token budget for an LLM operation.
        
        Args:
            context_id: Context identifier
            component: Component ID
            task_type: Task type
            provider: Provider ID (optional)
            model: Model ID (optional)
            priority: Task priority (1-10)
            token_count: Requested token count (optional)
            expiration: Expiration time (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            BudgetAllocation or None if allocation failed
        """
        # Determine tier based on component, provider, and model
        tier = self._determine_tier(component, provider, model)
        
        # Determine token count if not specified
        if token_count is None:
            # Use default allocation for task type and priority
            if task_type in self.DEFAULT_ALLOCATIONS:
                if priority in self.DEFAULT_ALLOCATIONS[task_type]:
                    token_count = self.DEFAULT_ALLOCATIONS[task_type][priority]
                else:
                    token_count = self.DEFAULT_ALLOCATIONS[task_type][TaskPriority.NORMAL]
            else:
                token_count = self.DEFAULT_ALLOCATIONS["default"][TaskPriority.NORMAL]
        
        # Check if there are any hard-limit policies that would be exceeded
        exceeded_policies = self._check_budget_exceeded(tier, component, task_type)
        hard_limit_exceeded = any(p.type == BudgetPolicyType.HARD_LIMIT for p in exceeded_policies)
        
        if hard_limit_exceeded and priority < TaskPriority.CRITICAL:
            logger.warning(f"Budget hard limit exceeded for {tier} (context: {context_id})")
            return None
            
        # Create allocation
        allocation = BudgetAllocation(
            context_id=context_id,
            component=component,
            tier=tier,
            provider=provider,
            model=model,
            task_type=task_type,
            priority=priority,
            tokens_allocated=token_count,
            tokens_used=0,
            creation_time=datetime.now(),
            expiration_time=expiration,
            is_active=True,
            metadata=metadata or {}
        )
        
        # Add to active allocations
        self.allocations[context_id] = allocation
        
        # Trigger callback
        self._trigger_callback("on_allocation_created", allocation)
        
        return allocation
    
    def record_usage(
        self,
        context_id: str,
        tokens: int,
        usage_type: str = "total",
        operation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Record token usage against an allocation.
        
        Args:
            context_id: Context identifier
            tokens: Number of tokens used
            usage_type: Type of usage (input, output, total)
            operation_id: Operation identifier (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            Number of tokens actually recorded (limited by allocation)
        """
        if context_id not in self.allocations:
            logger.warning(f"No active allocation for context {context_id}")
            return 0
            
        if tokens <= 0:
            return 0
            
        # Get allocation
        allocation = self.allocations[context_id]
        
        # Check if allocation is active
        if not allocation.is_active or allocation.is_expired:
            logger.warning(f"Allocation for context {context_id} is inactive or expired")
            return 0
            
        # Record usage against allocation
        tokens_recorded = allocation.record_usage(tokens)
        
        # Update usage counters
        if tokens_recorded > 0:
            # Update counters for all periods
            for period in BudgetPeriod:
                if period in [BudgetPeriod.PER_SESSION, BudgetPeriod.PER_TASK]:
                    continue  # Skip per-session and per-task periods
                    
                self._update_usage_counter(
                    tier=allocation.tier,
                    period=period,
                    component=allocation.component,
                    task_type=allocation.task_type,
                    tokens=tokens_recorded
                )
            
            # Create usage record
            record = BudgetUsageRecord(
                allocation_id=allocation.allocation_id,
                context_id=context_id,
                component=allocation.component,
                provider=allocation.provider or "unknown",
                model=allocation.model or "unknown",
                task_type=allocation.task_type,
                tokens_used=tokens_recorded,
                usage_type=usage_type,
                operation_id=operation_id,
                metadata=metadata or {}
            )
            
            # Add to usage records
            self.usage_records.append(record)
            
            # Check if any budgets have been exceeded
            self._check_budget_exceeded(
                tier=allocation.tier,
                component=allocation.component,
                task_type=allocation.task_type
            )
            
            # Trigger callback
            self._trigger_callback("on_allocation_updated", allocation)
            
        return tokens_recorded
    
    def get_allocation(self, context_id: str) -> Optional[BudgetAllocation]:
        """
        Get the budget allocation for a context.
        
        Args:
            context_id: Context identifier
            
        Returns:
            BudgetAllocation or None if not found
        """
        return self.allocations.get(context_id)
    
    def update_allocation(
        self,
        context_id: str,
        additional_tokens: Optional[int] = None,
        extend_expiration: Optional[timedelta] = None,
        is_active: Optional[bool] = None
    ) -> Optional[BudgetAllocation]:
        """
        Update a budget allocation.
        
        Args:
            context_id: Context identifier
            additional_tokens: Additional tokens to allocate (optional)
            extend_expiration: Extension to expiration time (optional)
            is_active: New active status (optional)
            
        Returns:
            Updated BudgetAllocation or None if not found
        """
        if context_id not in self.allocations:
            logger.warning(f"No active allocation for context {context_id}")
            return None
            
        # Get allocation
        allocation = self.allocations[context_id]
        
        # Update allocation
        if additional_tokens is not None and additional_tokens > 0:
            allocation.tokens_allocated += additional_tokens
            
        if extend_expiration is not None and allocation.expiration_time:
            allocation.expiration_time += extend_expiration
            
        if is_active is not None:
            allocation.is_active = is_active
            
        # Trigger callback
        self._trigger_callback("on_allocation_updated", allocation)
        
        return allocation
    
    def get_budget_summary(
        self,
        tier: Optional[BudgetTier] = None,
        period: BudgetPeriod = BudgetPeriod.DAILY,
        component: Optional[str] = None,
        task_type: Optional[str] = None
    ) -> List[BudgetSummary]:
        """
        Get a summary of budget usage.
        
        Args:
            tier: Budget tier (optional, if None, summarize all tiers)
            period: Budget period
            component: Component ID (optional)
            task_type: Task type (optional)
            
        Returns:
            List of BudgetSummary objects
        """
        summaries = []
        
        # Determine tiers to summarize
        tiers = [tier] if tier else list(BudgetTier)
        
        for current_tier in tiers:
            # Get applicable policies
            policies = self._get_applicable_policies(current_tier, component, task_type)
            
            if not policies:
                continue
                
            # Get the most specific policy for this period
            policy = None
            for p in policies:
                if p.period == period:
                    # More specific policy (has component or task_type) overrides less specific
                    if not policy or (p.component or p.task_type):
                        policy = p
                        
            if not policy:
                continue
                
            # Get current usage
            usage = self._get_usage_for_period(
                tier=current_tier,
                period=period,
                component=component,
                task_type=task_type
            )
            
            # Get active allocations
            active_count = sum(
                1 for a in self.allocations.values()
                if a.tier == current_tier 
                and (not component or a.component == component)
                and (not task_type or a.task_type == task_type)
                and a.is_active and not a.is_expired
            )
            
            # Get period start and end
            start, end = self._get_period_start_end(period)
            
            # Create summary
            summary = BudgetSummary(
                period=period,
                tier=current_tier,
                component=component,
                task_type=task_type,
                total_allocated=sum(
                    a.tokens_allocated for a in self.allocations.values()
                    if a.tier == current_tier 
                    and (not component or a.component == component)
                    and (not task_type or a.task_type == task_type)
                ),
                total_used=usage,
                limit=policy.limit,
                usage_percentage=usage / policy.limit if policy.limit > 0 else 0.0,
                active_allocations=active_count,
                start_time=start,
                end_time=end
            )
            
            summaries.append(summary)
            
        return summaries
    
    def register_callback(self, event_type: str, callback: Callable):
        """
        Register a callback for a specific event type.
        
        Args:
            event_type: Type of event to register for
            callback: Callback function
        """
        if event_type not in self.callbacks:
            logger.warning(f"Unknown event type: {event_type}")
            return
            
        self.callbacks[event_type].append(callback)
        logger.debug(f"Registered callback for {event_type}")
    
    def add_policy(self, policy: BudgetPolicy) -> str:
        """
        Add or update a budget policy.
        
        Args:
            policy: Budget policy to add
            
        Returns:
            Policy ID
        """
        # Store policy
        self.policies[policy.policy_id] = policy
        
        # Trigger callback
        self._trigger_callback("on_policy_updated", policy)
        
        # Save policies to file
        self._save_policies()
        
        return policy.policy_id
    
    def get_policy(self, policy_id: str) -> Optional[BudgetPolicy]:
        """
        Get a budget policy by ID.
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            BudgetPolicy or None if not found
        """
        return self.policies.get(policy_id)
    
    def update_policy(
        self,
        policy_id: str,
        **kwargs
    ) -> Optional[BudgetPolicy]:
        """
        Update a budget policy.
        
        Args:
            policy_id: Policy identifier
            **kwargs: Fields to update
            
        Returns:
            Updated BudgetPolicy or None if not found
        """
        if policy_id not in self.policies:
            logger.warning(f"No policy with ID {policy_id}")
            return None
            
        # Get policy
        policy = self.policies[policy_id]
        
        # Update fields
        for field, value in kwargs.items():
            if hasattr(policy, field):
                setattr(policy, field, value)
                
        # Trigger callback
        self._trigger_callback("on_policy_updated", policy)
        
        # Save policies to file
        self._save_policies()
        
        return policy
    
    def delete_policy(self, policy_id: str) -> bool:
        """
        Delete a budget policy.
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            True if policy was deleted
        """
        if policy_id not in self.policies:
            logger.warning(f"No policy with ID {policy_id}")
            return False
            
        # Delete policy
        del self.policies[policy_id]
        
        # Save policies to file
        self._save_policies()
        
        return True
    
    def get_model_tier(self, model: str) -> BudgetTier:
        """
        Get the budget tier for a model.
        
        Args:
            model: Model identifier
            
        Returns:
            BudgetTier
        """
        return self.model_tiers.get(model.lower(), BudgetTier.REMOTE_HEAVYWEIGHT)
    
    def set_model_tier(self, model: str, tier: BudgetTier):
        """
        Set the budget tier for a model.
        
        Args:
            model: Model identifier
            tier: Budget tier
        """
        self.model_tiers[model.lower()] = tier
        
    def get_component_tier(self, component: str) -> Optional[BudgetTier]:
        """
        Get the budget tier for a component.
        
        Args:
            component: Component identifier
            
        Returns:
            BudgetTier or None if not set
        """
        return self.component_tiers.get(component)
    
    def set_component_tier(self, component: str, tier: BudgetTier):
        """
        Set the budget tier for a component.
        
        Args:
            component: Component identifier
            tier: Budget tier
        """
        self.component_tiers[component] = tier
        
    def get_provider_tier(self, provider: str) -> BudgetTier:
        """
        Get the default budget tier for a provider.
        
        Args:
            provider: Provider identifier
            
        Returns:
            BudgetTier
        """
        return self.provider_tiers.get(provider.lower(), BudgetTier.REMOTE_HEAVYWEIGHT)
    
    def set_provider_tier(self, provider: str, tier: BudgetTier):
        """
        Set the default budget tier for a provider.
        
        Args:
            provider: Provider identifier
            tier: Budget tier
        """
        self.provider_tiers[provider.lower()] = tier