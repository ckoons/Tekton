"""
Budget API Models

This module defines the Pydantic models used for API requests and responses.
These models provide validation, serialization, and OpenAPI schema generation.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from uuid import UUID, uuid4
from pydantic import Field, field_validator, model_validator
from tekton.models import TektonBaseModel

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

# Import domain models
from budget.data.models import (
    BudgetTier, BudgetPeriod, BudgetPolicyType, TaskPriority,
    PriceType
)

# Request Models

class CreateBudgetRequest(TektonBaseModel):
    """Request model for creating a budget."""
    name: str = Field(..., description="Budget name")
    description: Optional[str] = Field(None, description="Budget description")
    owner: Optional[str] = Field(None, description="Budget owner")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Production Budget",
                "description": "Production environment budget for Q2 2025",
                "owner": "engineering-team",
                "metadata": {
                    "department": "engineering",
                    "project": "tekton-core"
                }
            }
        }
    }


class UpdateBudgetRequest(TektonBaseModel):
    """Request model for updating a budget."""
    name: Optional[str] = Field(None, description="Budget name")
    description: Optional[str] = Field(None, description="Budget description")
    owner: Optional[str] = Field(None, description="Budget owner")
    is_active: Optional[bool] = Field(None, description="Active status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Production Budget (Updated)",
                "description": "Updated production environment budget for Q2 2025",
                "is_active": True
            }
        }
    }


class CreatePolicyRequest(TektonBaseModel):
    """Request model for creating a budget policy."""
    budget_id: Optional[str] = Field(None, description="Budget ID (optional)")
    type: str = Field(..., description="Policy type (ignore, warn, soft_limit, hard_limit)")
    period: str = Field(..., description="Budget period (hourly, daily, weekly, monthly, per_session, per_task)")
    tier: Optional[str] = Field(None, description="Budget tier (local_lightweight, local_midweight, remote_heavyweight)")
    provider: Optional[str] = Field(None, description="Provider name")
    component: Optional[str] = Field(None, description="Component name")
    task_type: Optional[str] = Field(None, description="Task type")
    token_limit: Optional[int] = Field(None, description="Token limit")
    cost_limit: Optional[float] = Field(None, description="Cost limit")
    warning_threshold: Optional[float] = Field(0.8, description="Warning threshold (0.0-1.0)")
    action_threshold: Optional[float] = Field(0.95, description="Action threshold (0.0-1.0)")
    enabled: Optional[bool] = Field(True, description="Whether policy is enabled")
    
    @model_validator(mode='after')
    def validate_limits(self) -> 'BudgetRequest':
        """Validate that either token_limit or cost_limit is provided."""
        if self.token_limit is None and self.cost_limit is None:
            raise ValueError('Either token_limit or cost_limit must be provided')
        return self
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "budget_id": "budget-123e4567-e89b-12d3-a456-426614174000",
                "type": "warn",
                "period": "daily",
                "tier": "remote_heavyweight",
                "token_limit": 100000,
                "warning_threshold": 0.8,
                "action_threshold": 0.95,
                "enabled": True
            }
        }
    }

class UpdatePolicyRequest(TektonBaseModel):
    """Request model for updating a budget policy."""
    type: Optional[str] = Field(None, description="Policy type (ignore, warn, soft_limit, hard_limit)")
    token_limit: Optional[int] = Field(None, description="Token limit")
    cost_limit: Optional[float] = Field(None, description="Cost limit")
    warning_threshold: Optional[float] = Field(None, description="Warning threshold (0.0-1.0)")
    action_threshold: Optional[float] = Field(None, description="Action threshold (0.0-1.0)")
    enabled: Optional[bool] = Field(None, description="Whether policy is enabled")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "hard_limit",
                "token_limit": 150000,
                "warning_threshold": 0.7,
                "enabled": True
            }
        }
    }


class CreateAllocationRequest(TektonBaseModel):
    """Request model for creating a budget allocation."""
    budget_id: Optional[str] = Field(None, description="Budget ID (optional)")
    context_id: str = Field(..., description="Context ID")
    component: str = Field(..., description="Component name")
    tier: Optional[str] = Field(None, description="Budget tier (local_lightweight, local_midweight, remote_heavyweight)")
    provider: Optional[str] = Field(None, description="Provider name")
    model: Optional[str] = Field(None, description="Model name")
    task_type: str = Field(..., description="Task type")
    priority: Optional[int] = Field(5, description="Priority (1-10)")
    tokens_allocated: int = Field(..., description="Number of tokens to allocate")
    expected_tokens_used: Optional[int] = Field(None, description="Expected token usage")
    expiration_time: Optional[datetime] = Field(None, description="Expiration time")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "budget_id": "budget-123e4567-e89b-12d3-a456-426614174000",
                "context_id": "session-123",
                "component": "athena",
                "tier": "remote_heavyweight",
                "provider": "anthropic",
                "model": "claude-3-opus-20240229",
                "task_type": "text_generation",
                "priority": 5,
                "tokens_allocated": 10000,
                "metadata": {
                    "user_id": "user-456",
                    "session_type": "interactive"
                }
            }
        }
    }


class RecordUsageRequest(TektonBaseModel):
    """Request model for recording usage."""
    context_id: Optional[str] = Field(None, description="Context ID")
    allocation_id: Optional[str] = Field(None, description="Allocation ID")
    component: str = Field(..., description="Component name")
    provider: str = Field(..., description="Provider name")
    model: str = Field(..., description="Model name")
    task_type: str = Field(..., description="Task type")
    input_tokens: int = Field(..., description="Number of input tokens")
    output_tokens: int = Field(..., description="Number of output tokens")
    operation_id: Optional[str] = Field(None, description="Operation ID")
    request_id: Optional[str] = Field(None, description="Request ID")
    user_id: Optional[str] = Field(None, description="User ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @model_validator(mode='after')
    def validate_allocation_reference(self) -> 'BudgetAllocationRequest':
        """Validate that either context_id or allocation_id is provided."""
        if self.context_id is None and self.allocation_id is None:
            raise ValueError('Either context_id or allocation_id must be provided')
        return self
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "context_id": "session-123",
                "component": "athena",
                "provider": "anthropic",
                "model": "claude-3-opus-20240229",
                "task_type": "text_generation",
                "input_tokens": 150,
                "output_tokens": 420,
                "request_id": "req-abc123",
                "metadata": {
                    "prompt_type": "question_answering"
                }
            }
        }
    }


class GetUsageSummaryRequest(TektonBaseModel):
    """Request model for getting usage summary."""
    period: str = Field(..., description="Budget period (hourly, daily, weekly, monthly)")
    budget_id: Optional[str] = Field(None, description="Budget ID")
    provider: Optional[str] = Field(None, description="Provider name")
    component: Optional[str] = Field(None, description="Component name")
    model: Optional[str] = Field(None, description="Model name")
    task_type: Optional[str] = Field(None, description="Task type")
    start_time: Optional[datetime] = Field(None, description="Custom start time")
    end_time: Optional[datetime] = Field(None, description="Custom end time")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "period": "daily",
                "component": "athena",
                "provider": "anthropic"
            }
        }
    }



class ModelRecommendationRequest(TektonBaseModel):
    """Request model for getting model recommendations."""
    provider: str = Field(..., description="Current provider")
    model: str = Field(..., description="Current model")
    task_type: Optional[str] = Field("default", description="Task type")
    context_size: Optional[int] = Field(4000, description="Estimated context size in tokens")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "provider": "anthropic",
                "model": "claude-3-opus-20240229",
                "task_type": "text_generation",
                "context_size": 5000
            }
        }
    }



class PriceRequest(TektonBaseModel):
    """Request model for getting current price."""
    provider: str = Field(..., description="Provider name")
    model: str = Field(..., description="Model name")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "provider": "anthropic",
                "model": "claude-3-opus-20240229"
            }
        }
    }


# Response Models

class BudgetResponse(TektonBaseModel):
    """Response model for budget."""
    budget_id: str = Field(..., description="Budget ID")
    name: str = Field(..., description="Budget name")
    description: Optional[str] = Field(None, description="Budget description")
    owner: Optional[str] = Field(None, description="Budget owner")
    policies: List[str] = Field([], description="List of policy IDs")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_active: bool = Field(True, description="Active status")
    metadata: Dict[str, Any] = Field({}, description="Additional metadata")

class PolicyResponse(TektonBaseModel):
    """Response model for budget policy."""
    policy_id: str = Field(..., description="Policy ID")
    budget_id: Optional[str] = Field(None, description="Budget ID")
    type: str = Field(..., description="Policy type")
    period: str = Field(..., description="Budget period")
    tier: Optional[str] = Field(None, description="Budget tier")
    provider: Optional[str] = Field(None, description="Provider name")
    component: Optional[str] = Field(None, description="Component name")
    task_type: Optional[str] = Field(None, description="Task type")
    token_limit: Optional[int] = Field(None, description="Token limit")
    cost_limit: Optional[float] = Field(None, description="Cost limit")
    warning_threshold: float = Field(..., description="Warning threshold")
    action_threshold: float = Field(..., description="Action threshold")
    start_date: datetime = Field(..., description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")
    enabled: bool = Field(..., description="Whether policy is enabled")
    metadata: Dict[str, Any] = Field({}, description="Additional metadata")

class AllocationResponse(TektonBaseModel):
    """Response model for budget allocation."""
    allocation_id: str = Field(..., description="Allocation ID")
    budget_id: Optional[str] = Field(None, description="Budget ID")
    context_id: str = Field(..., description="Context ID")
    component: str = Field(..., description="Component name")
    tier: Optional[str] = Field(None, description="Budget tier")
    provider: Optional[str] = Field(None, description="Provider name")
    model: Optional[str] = Field(None, description="Model name")
    task_type: str = Field(..., description="Task type")
    priority: int = Field(..., description="Priority")
    tokens_allocated: int = Field(..., description="Number of tokens allocated")
    tokens_used: int = Field(..., description="Number of tokens used")
    input_tokens_used: int = Field(..., description="Number of input tokens used")
    output_tokens_used: int = Field(..., description="Number of output tokens used")
    estimated_cost: float = Field(..., description="Estimated cost")
    actual_cost: float = Field(..., description="Actual cost")
    creation_time: datetime = Field(..., description="Creation timestamp")
    expiration_time: Optional[datetime] = Field(None, description="Expiration timestamp")
    last_updated: datetime = Field(..., description="Last update timestamp")
    is_active: bool = Field(..., description="Active status")
    metadata: Dict[str, Any] = Field({}, description="Additional metadata")
    remaining_tokens: int = Field(..., description="Number of remaining tokens")
    usage_percentage: float = Field(..., description="Percentage of allocation used")

class UsageRecordResponse(TektonBaseModel):
    """Response model for usage record."""
    record_id: str = Field(..., description="Record ID")
    allocation_id: Optional[str] = Field(None, description="Allocation ID")
    budget_id: Optional[str] = Field(None, description="Budget ID")
    context_id: str = Field(..., description="Context ID")
    component: str = Field(..., description="Component name")
    provider: str = Field(..., description="Provider name")
    model: str = Field(..., description="Model name")
    task_type: str = Field(..., description="Task type")
    input_tokens: int = Field(..., description="Number of input tokens")
    output_tokens: int = Field(..., description="Number of output tokens")
    input_cost: float = Field(..., description="Input cost")
    output_cost: float = Field(..., description="Output cost")
    total_cost: float = Field(..., description="Total cost")
    pricing_version: Optional[str] = Field(None, description="Pricing version")
    timestamp: datetime = Field(..., description="Timestamp")
    operation_id: Optional[str] = Field(None, description="Operation ID")
    request_id: Optional[str] = Field(None, description="Request ID")
    user_id: Optional[str] = Field(None, description="User ID")
    metadata: Dict[str, Any] = Field({}, description="Additional metadata")

class UsageSummaryResponse(TektonBaseModel):
    """Response model for usage summary."""
    period: str = Field(..., description="Budget period")
    total_input_tokens: int = Field(..., description="Total input tokens")
    total_output_tokens: int = Field(..., description="Total output tokens")
    total_tokens: int = Field(..., description="Total tokens")
    total_cost: float = Field(..., description="Total cost")
    count: int = Field(..., description="Number of records")
    start_time: Optional[str] = Field(None, description="Start time")
    end_time: Optional[str] = Field(None, description="End time")
    groups: Dict[str, Dict[str, Dict[str, Any]]] = Field(..., description="Grouped summary data")

class BudgetSummaryResponse(TektonBaseModel):
    """Response model for budget summary."""
    budget_id: Optional[str] = Field(None, description="Budget ID")
    period: str = Field(..., description="Budget period")
    tier: Optional[str] = Field(None, description="Budget tier")
    provider: Optional[str] = Field(None, description="Provider name")
    component: Optional[str] = Field(None, description="Component name")
    task_type: Optional[str] = Field(None, description="Task type")
    total_tokens_allocated: int = Field(..., description="Total tokens allocated")
    total_tokens_used: int = Field(..., description="Total tokens used")
    token_limit: Optional[int] = Field(None, description="Token limit")
    token_usage_percentage: Optional[float] = Field(None, description="Token usage percentage")
    total_cost: float = Field(..., description="Total cost")
    cost_limit: Optional[float] = Field(None, description="Cost limit")
    cost_usage_percentage: Optional[float] = Field(None, description="Cost usage percentage")
    active_allocations: int = Field(..., description="Number of active allocations")
    start_time: datetime = Field(..., description="Start time")
    end_time: datetime = Field(..., description="End time")
    remaining_tokens: Optional[int] = Field(None, description="Remaining tokens")
    remaining_cost: Optional[float] = Field(None, description="Remaining cost")
    token_limit_exceeded: bool = Field(..., description="Whether token limit is exceeded")
    cost_limit_exceeded: bool = Field(..., description="Whether cost limit is exceeded")

class AlertResponse(TektonBaseModel):
    """Response model for alert."""
    alert_id: str = Field(..., description="Alert ID")
    budget_id: Optional[str] = Field(None, description="Budget ID")
    policy_id: Optional[str] = Field(None, description="Policy ID")
    severity: str = Field(..., description="Alert severity")
    type: str = Field(..., description="Alert type")
    message: str = Field(..., description="Alert message")
    details: Dict[str, Any] = Field({}, description="Alert details")
    timestamp: datetime = Field(..., description="Timestamp")
    acknowledged: bool = Field(..., description="Acknowledgement status")
    acknowledged_by: Optional[str] = Field(None, description="User who acknowledged")
    acknowledged_at: Optional[datetime] = Field(None, description="Acknowledgement timestamp")

class PriceResponse(TektonBaseModel):
    """Response model for price information."""
    pricing_id: str = Field(..., description="Pricing ID")
    provider: str = Field(..., description="Provider name")
    model: str = Field(..., description="Model name")
    price_type: str = Field(..., description="Price type")
    input_cost_per_token: float = Field(..., description="Input cost per token")
    output_cost_per_token: float = Field(..., description="Output cost per token")
    input_cost_per_char: float = Field(..., description="Input cost per character")
    output_cost_per_char: float = Field(..., description="Output cost per character")
    cost_per_image: Optional[float] = Field(None, description="Cost per image")
    cost_per_second: Optional[float] = Field(None, description="Cost per second")
    fixed_cost_per_request: Optional[float] = Field(None, description="Fixed cost per request")
    version: str = Field(..., description="Version")
    source: str = Field(..., description="Source")
    source_url: Optional[str] = Field(None, description="Source URL")
    verified: bool = Field(..., description="Verification status")
    effective_date: datetime = Field(..., description="Effective date")
    end_date: Optional[datetime] = Field(None, description="End date")
    metadata: Dict[str, Any] = Field({}, description="Additional metadata")

class ModelRecommendationResponse(TektonBaseModel):
    """Response model for model recommendation."""
    provider: str = Field(..., description="Provider name")
    model: str = Field(..., description="Model name")
    estimated_cost: float = Field(..., description="Estimated cost")
    savings: float = Field(..., description="Cost savings")
    savings_percent: float = Field(..., description="Cost savings percentage")
    input_cost_per_token: float = Field(..., description="Input cost per token")
    output_cost_per_token: float = Field(..., description="Output cost per token")

class ErrorResponse(TektonBaseModel):
    """Response model for errors."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    code: Optional[str] = Field(None, description="Error code")

class SuccessResponse(TektonBaseModel):
    """Response model for success messages."""
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")

# List Response Models

class BudgetListResponse(TektonBaseModel):
    """Response model for budget list."""
    items: List[BudgetResponse] = Field(..., description="List of budgets")
    total: int = Field(..., description="Total number of budgets")
    page: int = Field(1, description="Current page")
    limit: int = Field(20, description="Items per page")

class PolicyListResponse(TektonBaseModel):
    """Response model for policy list."""
    items: List[PolicyResponse] = Field(..., description="List of policies")
    total: int = Field(..., description="Total number of policies")
    page: int = Field(1, description="Current page")
    limit: int = Field(20, description="Items per page")

class AllocationListResponse(TektonBaseModel):
    """Response model for allocation list."""
    items: List[AllocationResponse] = Field(..., description="List of allocations")
    total: int = Field(..., description="Total number of allocations")
    page: int = Field(1, description="Current page")
    limit: int = Field(20, description="Items per page")

class UsageRecordListResponse(TektonBaseModel):
    """Response model for usage record list."""
    items: List[UsageRecordResponse] = Field(..., description="List of usage records")
    total: int = Field(..., description="Total number of records")
    page: int = Field(1, description="Current page")
    limit: int = Field(20, description="Items per page")

class AlertListResponse(TektonBaseModel):
    """Response model for alert list."""
    items: List[AlertResponse] = Field(..., description="List of alerts")
    total: int = Field(..., description="Total number of alerts")
    page: int = Field(1, description="Current page")
    limit: int = Field(20, description="Items per page")

class ModelRecommendationListResponse(TektonBaseModel):
    """Response model for model recommendation list."""
    items: List[ModelRecommendationResponse] = Field(..., description="List of recommendations")
    current_model: str = Field(..., description="Current model")
    current_provider: str = Field(..., description="Current provider")
    current_cost: float = Field(..., description="Current cost")

# Factory Functions for Response Models

def create_budget_response(budget):
    """Convert a Budget model to a BudgetResponse."""
    return BudgetResponse(
        budget_id=budget.budget_id,
        name=budget.name,
        description=budget.description,
        owner=budget.owner,
        policies=budget.policies,
        created_at=budget.created_at,
        updated_at=budget.updated_at,
        is_active=budget.is_active,
        metadata=budget.metadata,
    )

def create_policy_response(policy):
    """Convert a BudgetPolicy model to a PolicyResponse."""
    return PolicyResponse(
        policy_id=policy.policy_id,
        budget_id=policy.budget_id,
        type=policy.type.value,
        period=policy.period.value,
        tier=policy.tier.value if policy.tier else None,
        provider=policy.provider,
        component=policy.component,
        task_type=policy.task_type,
        token_limit=policy.token_limit,
        cost_limit=policy.cost_limit,
        warning_threshold=policy.warning_threshold,
        action_threshold=policy.action_threshold,
        start_date=policy.start_date,
        end_date=policy.end_date,
        enabled=policy.enabled,
        metadata=policy.metadata,
    )

def create_allocation_response(allocation):
    """Convert a BudgetAllocation model to an AllocationResponse."""
    return AllocationResponse(
        allocation_id=allocation.allocation_id,
        budget_id=allocation.budget_id,
        context_id=allocation.context_id,
        component=allocation.component,
        tier=allocation.tier.value if allocation.tier else None,
        provider=allocation.provider,
        model=allocation.model,
        task_type=allocation.task_type,
        priority=allocation.priority,
        tokens_allocated=allocation.tokens_allocated,
        tokens_used=allocation.tokens_used,
        input_tokens_used=allocation.input_tokens_used,
        output_tokens_used=allocation.output_tokens_used,
        estimated_cost=allocation.estimated_cost,
        actual_cost=allocation.actual_cost,
        creation_time=allocation.creation_time,
        expiration_time=allocation.expiration_time,
        last_updated=allocation.last_updated,
        is_active=allocation.is_active,
        metadata=allocation.metadata,
        remaining_tokens=allocation.remaining_tokens,
        usage_percentage=allocation.usage_percentage,
    )

def create_usage_record_response(record):
    """Convert a UsageRecord model to a UsageRecordResponse."""
    return UsageRecordResponse(
        record_id=record.record_id,
        allocation_id=record.allocation_id,
        budget_id=record.budget_id,
        context_id=record.context_id,
        component=record.component,
        provider=record.provider,
        model=record.model,
        task_type=record.task_type,
        input_tokens=record.input_tokens,
        output_tokens=record.output_tokens,
        input_cost=record.input_cost,
        output_cost=record.output_cost,
        total_cost=record.total_cost,
        pricing_version=record.pricing_version,
        timestamp=record.timestamp,
        operation_id=record.operation_id,
        request_id=record.request_id,
        user_id=record.user_id,
        metadata=record.metadata,
    )

def create_alert_response(alert):
    """Convert an Alert model to an AlertResponse."""
    return AlertResponse(
        alert_id=alert.alert_id,
        budget_id=alert.budget_id,
        policy_id=alert.policy_id,
        severity=alert.severity,
        type=alert.type,
        message=alert.message,
        details=alert.details,
        timestamp=alert.timestamp,
        acknowledged=alert.acknowledged,
        acknowledged_by=alert.acknowledged_by,
        acknowledged_at=alert.acknowledged_at,
    )

def create_price_response(price):
    """Convert a ProviderPricing model to a PriceResponse."""
    return PriceResponse(
        pricing_id=price.pricing_id,
        provider=price.provider,
        model=price.model,
        price_type=price.price_type.value,
        input_cost_per_token=price.input_cost_per_token,
        output_cost_per_token=price.output_cost_per_token,
        input_cost_per_char=price.input_cost_per_char,
        output_cost_per_char=price.output_cost_per_char,
        cost_per_image=price.cost_per_image,
        cost_per_second=price.cost_per_second,
        fixed_cost_per_request=price.fixed_cost_per_request,
        version=price.version,
        source=price.source,
        source_url=price.source_url,
        verified=price.verified,
        effective_date=price.effective_date,
        end_date=price.end_date,
        metadata=price.metadata,
    )

def create_budget_summary_response(summary):
    """Convert a BudgetSummary model to a BudgetSummaryResponse."""
    return BudgetSummaryResponse(
        budget_id=summary.budget_id,
        period=summary.period.value,
        tier=summary.tier.value if summary.tier else None,
        provider=summary.provider,
        component=summary.component,
        task_type=summary.task_type,
        total_tokens_allocated=summary.total_tokens_allocated,
        total_tokens_used=summary.total_tokens_used,
        token_limit=summary.token_limit,
        token_usage_percentage=summary.token_usage_percentage,
        total_cost=summary.total_cost,
        cost_limit=summary.cost_limit,
        cost_usage_percentage=summary.cost_usage_percentage,
        active_allocations=summary.active_allocations,
        start_time=summary.start_time,
        end_time=summary.end_time,
        remaining_tokens=summary.remaining_tokens,
        remaining_cost=summary.remaining_cost,
        token_limit_exceeded=summary.token_limit_exceeded,
        cost_limit_exceeded=summary.cost_limit_exceeded,
    )

def create_model_recommendation_response(recommendation):
    """Convert a model recommendation to a ModelRecommendationResponse."""
    return ModelRecommendationResponse(
        provider=recommendation["provider"],
        model=recommendation["model"],
        estimated_cost=recommendation["estimated_cost"],
        savings=recommendation["savings"],
        savings_percent=recommendation["savings_percent"],
        input_cost_per_token=recommendation["input_cost_per_token"],
        output_cost_per_token=recommendation["output_cost_per_token"],
    )