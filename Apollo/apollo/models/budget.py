"""
Budget models for Apollo.

This module defines the data models used for token budget management.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from pydantic import Field, field_validator
from tekton.models import TektonBaseModel
import uuid


class BudgetTier(str, Enum):
    """Token budget tiers for different model capabilities."""
    LOCAL_LIGHTWEIGHT = "local_lightweight"  # e.g., CodeLlama, Deepseek Coder
    LOCAL_MIDWEIGHT = "local_midweight"      # e.g., Local Claude Haiku, Qwen
    REMOTE_HEAVYWEIGHT = "remote_heavyweight"  # e.g., Claude 3.7 Sonnet, GPT-4


class BudgetPeriod(str, Enum):
    """Budget period types."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    PER_SESSION = "per_session"
    PER_TASK = "per_task"


class BudgetPolicyType(str, Enum):
    """Types of budget enforcement policies."""
    IGNORE = "ignore"       # Track but don't enforce
    WARN = "warn"           # Track and warn when exceeded
    SOFT_LIMIT = "soft_limit"  # Track and recommend actions
    HARD_LIMIT = "hard_limit"  # Track and enforce limits strictly


class TaskPriority(int, Enum):
    """Priority levels for tasks."""
    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10


class BudgetPolicy(TektonBaseModel):
    """Policy for token budget enforcement."""
    policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: BudgetPolicyType
    period: BudgetPeriod
    tier: BudgetTier
    component: Optional[str] = None  # Specific component or None for all
    task_type: Optional[str] = None  # Specific task type or None for all
    limit: int  # Token limit for the period
    warning_threshold: float = 0.8  # Warning percentage (0.0-1.0)
    action_threshold: float = 0.95  # Action percentage (0.0-1.0)
    start_date: datetime = Field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    enabled: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BudgetAllocation(TektonBaseModel):
    """Token budget allocation for a specific LLM operation."""
    allocation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    context_id: str
    component: str
    tier: BudgetTier
    provider: Optional[str] = None
    model: Optional[str] = None
    task_type: str
    priority: int = Field(5, ge=1, le=10)  # 1-10 priority scale
    tokens_allocated: int
    tokens_used: int = 0
    creation_time: datetime = Field(default_factory=datetime.now)
    expiration_time: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
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
    
    def record_usage(self, tokens: int) -> int:
        """
        Record token usage against this allocation.
        
        Args:
            tokens: Number of tokens used
            
        Returns:
            Number of tokens actually recorded (limited by allocation)
        """
        # Check if allocation is active
        if not self.is_active or self.is_expired:
            return 0
            
        # Calculate tokens to record (limited by remaining tokens)
        tokens_to_record = min(tokens, self.remaining_tokens)
        
        # Update token usage
        self.tokens_used += tokens_to_record
        
        # Mark as inactive if fully used
        if self.remaining_tokens == 0:
            self.is_active = False
            
        return tokens_to_record


class BudgetUsageRecord(TektonBaseModel):
    """Record of token usage for a specific operation."""
    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    allocation_id: str
    context_id: str
    component: str
    provider: str
    model: str
    task_type: str
    tokens_used: int
    usage_type: str  # input, output, total
    timestamp: datetime = Field(default_factory=datetime.now)
    operation_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BudgetSummary(TektonBaseModel):
    """Summary of budget usage for a component or task type."""
    period: BudgetPeriod
    tier: BudgetTier
    component: Optional[str] = None
    task_type: Optional[str] = None
    total_allocated: int
    total_used: int
    limit: int
    usage_percentage: float
    active_allocations: int
    start_time: datetime
    end_time: datetime
    
    @property
    def remaining(self) -> int:
        """Get the number of remaining tokens in the budget."""
        return max(0, self.limit - self.total_used)
    
    @property
    def is_exceeded(self) -> bool:
        """Check if the budget has been exceeded."""
        return self.total_used > self.limit