"""
Budget Data Models

This module defines the core domain entities for the Budget component.
It combines token allocation tracking from Apollo with cost tracking from Rhetor,
creating a unified budget system.
"""

import uuid
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

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


class BudgetTier(str, Enum):
    """
    Token budget tiers for different model capabilities.
    
    Categorizes models based on their capabilities and typical cost/token usage:
    - LOCAL_LIGHTWEIGHT: Small, efficient models for basic tasks (e.g., CodeLlama)
    - LOCAL_MIDWEIGHT: Mid-range models with good capabilities (e.g., Local Claude Haiku)
    - REMOTE_HEAVYWEIGHT: High-capability models (e.g., Claude 3.7 Sonnet, GPT-4)
    """
    LOCAL_LIGHTWEIGHT = "local_lightweight"
    LOCAL_MIDWEIGHT = "local_midweight"
    REMOTE_HEAVYWEIGHT = "remote_heavyweight"


class BudgetPeriod(str, Enum):
    """
    Budget period types.
    
    Defines the time periods for budget allocation and enforcement:
    - HOURLY: Per-hour limits
    - DAILY: Per-day limits
    - WEEKLY: Per-week limits (starting Monday)
    - MONTHLY: Per-month limits (calendar month)
    - PER_SESSION: Limits specific to a user session
    - PER_TASK: Limits for a single task
    """
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    PER_SESSION = "per_session"
    PER_TASK = "per_task"


class BudgetPolicyType(str, Enum):
    """
    Types of budget enforcement policies.
    
    Defines how budget limits are enforced:
    - IGNORE: Track but don't enforce
    - WARN: Track and warn when exceeded
    - SOFT_LIMIT: Track and recommend actions (like downgrades)
    - HARD_LIMIT: Track and enforce limits strictly
    """
    IGNORE = "ignore"
    WARN = "warn"
    SOFT_LIMIT = "soft_limit"
    HARD_LIMIT = "hard_limit"


class TaskPriority(int, Enum):
    """
    Priority levels for tasks.
    
    Higher priority tasks may be allowed to exceed soft limits:
    - LOW: Non-critical background tasks
    - NORMAL: Standard operations
    - HIGH: Important tasks with some flexibility
    - CRITICAL: Essential tasks that must complete
    """
    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10


class PriceType(str, Enum):
    """
    Types of pricing structures.
    
    Defines how prices are calculated:
    - TOKEN_BASED: Priced per token (typical for most LLMs)
    - CHARACTER_BASED: Priced per character (some specialized models)
    - IMAGE_BASED: Priced per image or by image dimensions
    - TIME_BASED: Priced by computation time
    - FIXED: Fixed price per request
    """
    TOKEN_BASED = "token_based"
    CHARACTER_BASED = "character_based"
    IMAGE_BASED = "image_based"
    TIME_BASED = "time_based"
    FIXED = "fixed"


class ProviderPricing(BaseModel):
    """
    Provider and model-specific pricing information.
    
    Tracks the pricing details for a specific model:
    - Input/output token costs
    - Version information
    - Source of the pricing data
    - Effective dates for the pricing
    """
    pricing_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    provider: str
    model: str
    price_type: PriceType = PriceType.TOKEN_BASED
    input_cost_per_token: float = 0.0
    output_cost_per_token: float = 0.0
    input_cost_per_char: float = 0.0
    output_cost_per_char: float = 0.0
    cost_per_image: Optional[float] = None
    cost_per_second: Optional[float] = None
    fixed_cost_per_request: Optional[float] = None
    version: str = "1.0"
    source: str
    source_url: Optional[str] = None
    verified: bool = False
    effective_date: datetime = Field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    meta_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Make SQLAlchemy happy by adding _sa_instance_state attribute
    _sa_instance_state = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator('end_date')
    @classmethod
    def end_date_must_be_after_effective_date(cls, v, info):
        """Validate that end_date is after effective_date if both are provided."""
        if v and 'effective_date' in info.data and v <= info.data['effective_date']:
            raise ValueError('end_date must be after effective_date')
        return v


class BudgetPolicy(BaseModel):
    """
    Policy for token budget and cost enforcement.
    
    Defines limits and enforcement policies for a specific budget period:
    - Type of enforcement (warn, enforce, etc.)
    - Budget period (daily, weekly, etc.)
    - Token or cost limits
    - Warning thresholds
    """
    policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: BudgetPolicyType
    period: BudgetPeriod
    tier: Optional[BudgetTier] = None
    provider: Optional[str] = None
    component: Optional[str] = None
    task_type: Optional[str] = None
    token_limit: Optional[int] = None
    cost_limit: Optional[float] = None
    warning_threshold: float = 0.8
    action_threshold: float = 0.95
    start_date: datetime = Field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    enabled: bool = True
    meta_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Make SQLAlchemy happy by adding _sa_instance_state attribute
    _sa_instance_state = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode='after')
    def either_token_or_cost_limit(self) -> 'BudgetPolicy':
        """Ensure that either token_limit or cost_limit is provided."""
        if self.token_limit is None and self.cost_limit is None:
            raise ValueError('Either token_limit or cost_limit must be provided')
        return self

    @field_validator('end_date')
    @classmethod
    def end_date_must_be_after_start_date(cls, v, info):
        """Validate that end_date is after start_date if both are provided."""
        if v and 'start_date' in info.data and v <= info.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class Budget(BaseModel):
    """
    Top-level budget container.
    
    Defines a budget with its properties:
    - ID and name
    - Budget type and scope
    - Associated policies
    - Creation and modification dates
    """
    budget_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    owner: Optional[str] = None
    policies: List[str] = Field(default_factory=list)  # List of policy_ids
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    meta_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Make SQLAlchemy happy by adding _sa_instance_state attribute
    _sa_instance_state = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


class BudgetAllocation(BaseModel):
    """
    Token and cost budget allocation for a specific operation.
    
    Tracks resources allocated for a specific task:
    - Context and component identification
    - Token allocation and usage
    - Cost estimates and actual costs
    - Expiration and status tracking
    """
    allocation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    budget_id: Optional[str] = None
    context_id: str
    component: str
    tier: Optional[BudgetTier] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    task_type: str
    priority: int = Field(5, ge=1, le=10)  # 1-10 priority scale
    
    # Token allocation
    tokens_allocated: int = 0
    tokens_used: int = 0
    input_tokens_used: int = 0
    output_tokens_used: int = 0
    
    # Cost tracking
    estimated_cost: float = 0.0
    actual_cost: float = 0.0
    
    # Timestamps
    creation_time: datetime = Field(default_factory=datetime.now)
    expiration_time: Optional[datetime] = None
    last_updated: datetime = Field(default_factory=datetime.now)
    
    # Status
    is_active: bool = True
    meta_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Make SQLAlchemy happy by adding _sa_instance_state attribute
    _sa_instance_state = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    @field_validator('expiration_time', mode='before')
    @classmethod
    def set_expiration_time(cls, v, info):
        """Set default expiration time if not provided."""
        if v is None and 'creation_time' in info.data:
            # Default expiration: 24 hours after creation
            return info.data['creation_time'] + timedelta(hours=24)
        return v
    
    @property
    def remaining_tokens(self) -> int:
        """Get the number of remaining tokens in the allocation."""
        return max(0, self.tokens_allocated - self.tokens_used)
    
    @property
    def usage_percentage(self) -> float:
        """Get the percentage of allocated tokens used."""
        if self.tokens_allocated == 0:
            return 0.0
        return self.tokens_used / self.tokens_allocated
    
    @property
    def is_expired(self) -> bool:
        """Check if the allocation has expired."""
        if not self.expiration_time:
            return False
        return datetime.now() > self.expiration_time
    
    def record_usage(
        self, 
        input_tokens: int = 0, 
        output_tokens: int = 0, 
        cost: Optional[float] = None
    ) -> int:
        """
        Record token usage against this allocation.
        
        Args:
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used
            cost: Actual cost (if known)
            
        Returns:
            Number of tokens actually recorded (limited by allocation)
        """
        # Check if allocation is active
        if not self.is_active or self.is_expired:
            debug_log.warn("budget_models", 
                          f"Attempted to record usage on inactive allocation {self.allocation_id}")
            return 0
            
        # Calculate total tokens
        total_tokens = input_tokens + output_tokens
        
        # Calculate tokens to record (limited by remaining tokens)
        tokens_to_record = min(total_tokens, self.remaining_tokens)
        
        if tokens_to_record < total_tokens:
            debug_log.warn("budget_models", 
                          f"Allocation {self.allocation_id} exceeded: tried to use {total_tokens}, "
                          f"but only {tokens_to_record} were available")
        
        # Update token usage
        if tokens_to_record > 0:
            # Split recorded tokens proportionally between input and output
            if total_tokens > 0:
                input_ratio = input_tokens / total_tokens
                recorded_input = int(tokens_to_record * input_ratio)
                recorded_output = tokens_to_record - recorded_input
            else:
                recorded_input = 0
                recorded_output = 0
                
            self.input_tokens_used += recorded_input
            self.output_tokens_used += recorded_output
            self.tokens_used += tokens_to_record
            
            # Update cost if provided
            if cost is not None:
                self.actual_cost += cost
                
            # Update last updated timestamp
            self.last_updated = datetime.now()
            
            # Mark as inactive if fully used
            if self.remaining_tokens == 0:
                self.is_active = False
                debug_log.info("budget_models", 
                              f"Allocation {self.allocation_id} fully used and marked as inactive")
            
        return tokens_to_record


class UsageRecord(BaseModel):
    """
    Record of token and cost usage for a specific operation.
    
    Detailed tracking of LLM usage:
    - Request identification
    - Token consumption (input and output)
    - Costs and pricing
    - Contextual information for analysis
    """
    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    allocation_id: Optional[str] = None
    budget_id: Optional[str] = None
    context_id: str
    component: str
    provider: str
    model: str
    task_type: str
    
    # Token and cost tracking
    input_tokens: int = 0
    output_tokens: int = 0
    input_cost: float = 0.0
    output_cost: float = 0.0
    total_cost: float = 0.0
    pricing_version: Optional[str] = None
    
    # Timestamps and identification
    timestamp: datetime = Field(default_factory=datetime.now)
    operation_id: Optional[str] = None
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    
    # Additional data
    meta_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Make SQLAlchemy happy by adding _sa_instance_state attribute
    _sa_instance_state = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


class Alert(BaseModel):
    """
    Notification for budget events.
    
    Alerts for budget status changes:
    - Warnings, violations
    - Price changes
    - Policy triggers
    """
    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    budget_id: Optional[str] = None
    policy_id: Optional[str] = None
    severity: str  # info, warning, error
    type: str  # budget_exceeded, price_change, etc.
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    
    # Make SQLAlchemy happy by adding _sa_instance_state attribute
    _sa_instance_state = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


class BudgetSummary(BaseModel):
    """
    Summary of budget usage.
    
    Aggregated view of budget status:
    - Usage totals
    - Limits and thresholds
    - Period information
    """
    budget_id: Optional[str] = None
    period: BudgetPeriod
    tier: Optional[BudgetTier] = None
    provider: Optional[str] = None
    component: Optional[str] = None
    task_type: Optional[str] = None
    
    # Token tracking
    total_tokens_allocated: int = 0
    total_tokens_used: int = 0
    token_limit: Optional[int] = None
    token_usage_percentage: Optional[float] = None
    
    # Cost tracking
    total_cost: float = 0.0
    cost_limit: Optional[float] = None
    cost_usage_percentage: Optional[float] = None
    
    # Period metrics
    active_allocations: int = 0
    start_time: datetime
    end_time: datetime
    
    # Make SQLAlchemy happy by adding _sa_instance_state attribute
    _sa_instance_state = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    @property
    def remaining_tokens(self) -> Optional[int]:
        """Get the number of remaining tokens in the budget."""
        if self.token_limit is None:
            return None
        return max(0, self.token_limit - self.total_tokens_used)
    
    @property
    def remaining_cost(self) -> Optional[float]:
        """Get the remaining cost budget."""
        if self.cost_limit is None:
            return None
        return max(0.0, self.cost_limit - self.total_cost)
    
    @property
    def token_limit_exceeded(self) -> bool:
        """Check if the token budget has been exceeded."""
        if self.token_limit is None:
            return False
        return self.total_tokens_used > self.token_limit
    
    @property
    def cost_limit_exceeded(self) -> bool:
        """Check if the cost budget has been exceeded."""
        if self.cost_limit is None:
            return False
        return self.total_cost > self.cost_limit


class PriceUpdateRecord(BaseModel):
    """
    Record of a price update operation.
    
    Tracks changes to pricing data:
    - What changed and when
    - Source of the new data
    - Verification status
    """
    update_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    provider: str
    model: str
    previous_pricing_id: Optional[str] = None
    new_pricing_id: str
    source: str
    verification_status: str  # verified, unverified, conflict
    timestamp: datetime = Field(default_factory=datetime.now)
    changes: Dict[str, Any] = Field(default_factory=dict)
    meta_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Make SQLAlchemy happy by adding _sa_instance_state attribute
    _sa_instance_state = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


class PriceSource(BaseModel):
    """
    Information about a price data source.
    
    Metadata for price sources:
    - Reliability score
    - Update frequency
    - Authentication details
    """
    source_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    type: str  # api, scraper, manual
    trust_score: float = 1.0  # 0.0-1.0 scale of trustworthiness
    update_frequency: Optional[int] = None  # in minutes
    last_update: Optional[datetime] = None
    next_update: Optional[datetime] = None
    auth_required: bool = False
    auth_config: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    meta_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Make SQLAlchemy happy by adding _sa_instance_state attribute
    _sa_instance_state = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)