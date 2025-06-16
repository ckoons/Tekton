"""
Budget API Endpoints

This module defines the FastAPI endpoints for the Budget component API.
It includes endpoints for budget management, allocation, usage tracking, and reporting.
"""

import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse

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

# Import core components
from budget.core.engine import budget_engine
from budget.core.allocation import allocation_manager
from budget.core.tracking import tracking_manager
from budget.core.policy import policy_manager

# Import repositories
from budget.data.repository import (
    budget_repo, policy_repo, allocation_repo, usage_repo,
    alert_repo, pricing_repo, update_repo, source_repo
)

# Import models and dependencies
from budget.data.models import (
    BudgetTier, BudgetPeriod, BudgetPolicyType, TaskPriority,
    Budget, BudgetPolicy, BudgetAllocation, UsageRecord, Alert,
    ProviderPricing, PriceUpdateRecord, PriceSource, BudgetSummary
)
from budget.api.models import (
    # Request models
    CreateBudgetRequest, UpdateBudgetRequest, CreatePolicyRequest, UpdatePolicyRequest,
    CreateAllocationRequest, RecordUsageRequest, GetUsageSummaryRequest,
    ModelRecommendationRequest, PriceRequest,
    
    # Response models
    BudgetResponse, PolicyResponse, AllocationResponse, UsageRecordResponse,
    UsageSummaryResponse, BudgetSummaryResponse, AlertResponse, PriceResponse,
    ModelRecommendationResponse, ErrorResponse, SuccessResponse,
    
    # List response models
    BudgetListResponse, PolicyListResponse, AllocationListResponse,
    UsageRecordListResponse, AlertListResponse, ModelRecommendationListResponse,
    
    # Factory functions
    create_budget_response, create_policy_response, create_allocation_response,
    create_usage_record_response, create_alert_response, create_price_response,
    create_budget_summary_response, create_model_recommendation_response
)
from budget.api.dependencies import (
    get_authenticated_user, pagination_params,
    budget_id_param, policy_id_param, allocation_id_param, 
    record_id_param, alert_id_param
)

# Create API routers following Single Port Architecture pattern
router = APIRouter(tags=["Budget"])
budget_router = APIRouter(prefix="/budgets", tags=["Budget Management"])
policy_router = APIRouter(prefix="/policies", tags=["Budget Policies"])
allocation_router = APIRouter(prefix="/allocations", tags=["Budget Allocations"])
usage_router = APIRouter(prefix="/usage", tags=["Usage Tracking"])
report_router = APIRouter(prefix="/reports", tags=["Reporting"])
alert_router = APIRouter(prefix="/alerts", tags=["Alerts"])
price_router = APIRouter(prefix="/prices", tags=["Pricing"])

# Budget Management Endpoints

@budget_router.post("", response_model=BudgetResponse, status_code=201)
@log_function()
async def create_budget(
    request: CreateBudgetRequest,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Create a new budget.
    
    Args:
        request: The budget creation request
        user: The authenticated user
    
    Returns:
        The created budget
    """
    debug_log.info("budget_api", f"Creating budget: {request.name}")
    
    # Create the budget
    budget = budget_engine.create_budget(
        name=request.name,
        description=request.description,
        owner=request.owner,
        metadata=request.metadata
    )
    
    # Create default policies
    budget_engine.create_default_policies(budget.budget_id)
    
    # Get the updated budget
    budget = budget_repo.get_by_id(budget.budget_id)
    
    # Return the response
    return create_budget_response(budget)

@budget_router.get("", response_model=BudgetListResponse)
@log_function()
async def list_budgets(
    pagination: Dict[str, int] = Depends(pagination_params),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    owner: Optional[str] = Query(None, description="Filter by owner"),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    List budgets with optional filtering.
    
    Args:
        pagination: Pagination parameters
        is_active: Filter by active status
        owner: Filter by owner
        user: The authenticated user
    
    Returns:
        List of budgets with pagination info
    """
    debug_log.info("budget_api", "Listing budgets")
    
    # Get all budgets (in a real implementation, we would apply filtering in the repository)
    budgets = budget_repo.get_all(limit=pagination["limit"], offset=pagination["offset"])
    
    # Apply additional filtering
    if is_active is not None:
        budgets = [b for b in budgets if b.is_active == is_active]
    
    if owner:
        budgets = [b for b in budgets if b.owner == owner]
    
    # Count total (before pagination)
    total = len(budgets)
    
    # Convert to response models
    budget_responses = [create_budget_response(budget) for budget in budgets]
    
    # Return paginated response
    return BudgetListResponse(
        items=budget_responses,
        total=total,
        page=pagination["page"],
        limit=pagination["limit"]
    )

@budget_router.get("/{budget_id}", response_model=BudgetResponse)
@log_function()
async def get_budget(
    budget_id: str = Depends(budget_id_param),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Get a budget by ID.
    
    Args:
        budget_id: The budget ID
        user: The authenticated user
    
    Returns:
        The budget
    
    Raises:
        HTTPException: If the budget is not found
    """
    debug_log.info("budget_api", f"Getting budget: {budget_id}")
    
    # Get the budget
    budget = budget_repo.get_by_id(budget_id)
    if not budget:
        debug_log.warn("budget_api", f"Budget not found: {budget_id}")
        raise HTTPException(status_code=404, detail=f"Budget with ID {budget_id} not found")
    
    # Return the response
    return create_budget_response(budget)

@budget_router.put("/{budget_id}", response_model=BudgetResponse)
@log_function()
async def update_budget(
    request: UpdateBudgetRequest,
    budget_id: str = Depends(budget_id_param),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Update a budget.
    
    Args:
        request: The budget update request
        budget_id: The budget ID
        user: The authenticated user
    
    Returns:
        The updated budget
    
    Raises:
        HTTPException: If the budget is not found
    """
    debug_log.info("budget_api", f"Updating budget: {budget_id}")
    
    # Get the budget
    budget = budget_repo.get_by_id(budget_id)
    if not budget:
        debug_log.warn("budget_api", f"Budget not found: {budget_id}")
        raise HTTPException(status_code=404, detail=f"Budget with ID {budget_id} not found")
    
    # Update fields if provided
    if request.name is not None:
        budget.name = request.name
    if request.description is not None:
        budget.description = request.description
    if request.owner is not None:
        budget.owner = request.owner
    if request.is_active is not None:
        budget.is_active = request.is_active
    if request.metadata is not None:
        budget.metadata = request.metadata
    
    # Update timestamp
    budget.updated_at = datetime.now()
    
    # Save the updated budget
    updated_budget = budget_repo.update(budget)
    
    # Return the response
    return create_budget_response(updated_budget)

@budget_router.delete("/{budget_id}", response_model=SuccessResponse)
@log_function()
async def delete_budget(
    budget_id: str = Depends(budget_id_param),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Delete a budget (soft delete by setting is_active to False).
    
    Args:
        budget_id: The budget ID
        user: The authenticated user
    
    Returns:
        Success message
    
    Raises:
        HTTPException: If the budget is not found
    """
    debug_log.info("budget_api", f"Deleting budget: {budget_id}")
    
    # Get the budget
    budget = budget_repo.get_by_id(budget_id)
    if not budget:
        debug_log.warn("budget_api", f"Budget not found: {budget_id}")
        raise HTTPException(status_code=404, detail=f"Budget with ID {budget_id} not found")
    
    # Soft delete by setting is_active to False
    budget.is_active = False
    budget.updated_at = datetime.now()
    
    # Save the updated budget
    budget_repo.update(budget)
    
    # Return success message
    return SuccessResponse(message=f"Budget {budget_id} deleted successfully")

@budget_router.get("/{budget_id}/policies", response_model=PolicyListResponse)
@log_function()
async def list_budget_policies(
    budget_id: str = Depends(budget_id_param),
    pagination: Dict[str, int] = Depends(pagination_params),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    List policies for a budget.
    
    Args:
        budget_id: The budget ID
        pagination: Pagination parameters
        user: The authenticated user
    
    Returns:
        List of policies
    
    Raises:
        HTTPException: If the budget is not found
    """
    debug_log.info("budget_api", f"Listing policies for budget: {budget_id}")
    
    # Verify budget exists
    budget = budget_repo.get_by_id(budget_id)
    if not budget:
        debug_log.warn("budget_api", f"Budget not found: {budget_id}")
        raise HTTPException(status_code=404, detail=f"Budget with ID {budget_id} not found")
    
    # Get policies for the budget
    policies = policy_repo.get_by_budget_id(budget_id)
    
    # Apply pagination (in a real implementation, this would be done at the DB level)
    total = len(policies)
    policies = policies[pagination["offset"]:pagination["offset"] + pagination["limit"]]
    
    # Convert to response models
    policy_responses = [create_policy_response(policy) for policy in policies]
    
    # Return paginated response
    return PolicyListResponse(
        items=policy_responses,
        total=total,
        page=pagination["page"],
        limit=pagination["limit"]
    )

@budget_router.get("/{budget_id}/allocations", response_model=AllocationListResponse)
@log_function()
async def list_budget_allocations(
    budget_id: str = Depends(budget_id_param),
    pagination: Dict[str, int] = Depends(pagination_params),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    List allocations for a budget.
    
    Args:
        budget_id: The budget ID
        pagination: Pagination parameters
        is_active: Filter by active status
        user: The authenticated user
    
    Returns:
        List of allocations
    
    Raises:
        HTTPException: If the budget is not found
    """
    debug_log.info("budget_api", f"Listing allocations for budget: {budget_id}")
    
    # Verify budget exists
    budget = budget_repo.get_by_id(budget_id)
    if not budget:
        debug_log.warn("budget_api", f"Budget not found: {budget_id}")
        raise HTTPException(status_code=404, detail=f"Budget with ID {budget_id} not found")
    
    # Get allocations for the budget
    allocations = allocation_repo.get_active_allocations(budget_id=budget_id)
    
    # Apply additional filtering
    if is_active is not None:
        allocations = [a for a in allocations if a.is_active == is_active]
    
    # Apply pagination (in a real implementation, this would be done at the DB level)
    total = len(allocations)
    allocations = allocations[pagination["offset"]:pagination["offset"] + pagination["limit"]]
    
    # Convert to response models
    allocation_responses = [create_allocation_response(allocation) for allocation in allocations]
    
    # Return paginated response
    return AllocationListResponse(
        items=allocation_responses,
        total=total,
        page=pagination["page"],
        limit=pagination["limit"]
    )

@budget_router.get("/{budget_id}/summary", response_model=List[BudgetSummaryResponse])
@log_function()
async def get_budget_summary(
    budget_id: str = Depends(budget_id_param),
    period: str = Query("daily", description="Budget period (hourly, daily, weekly, monthly)"),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Get a summary of budget usage.
    
    Args:
        budget_id: The budget ID
        period: The budget period
        user: The authenticated user
    
    Returns:
        Budget summary
    
    Raises:
        HTTPException: If the budget is not found
    """
    debug_log.info("budget_api", f"Getting summary for budget: {budget_id}, period: {period}")
    
    # Verify budget exists
    budget = budget_repo.get_by_id(budget_id)
    if not budget:
        debug_log.warn("budget_api", f"Budget not found: {budget_id}")
        raise HTTPException(status_code=404, detail=f"Budget with ID {budget_id} not found")
    
    # Get budget summary
    try:
        # Convert string period to enum
        period_enum = BudgetPeriod(period)
        
        # Get summary
        summaries = budget_engine.get_budget_summary(
            budget_id=budget_id,
            period=period_enum
        )
        
        # Convert to response models
        summary_responses = [create_budget_summary_response(summary) for summary in summaries]
        
        return summary_responses
    except ValueError:
        debug_log.error("budget_api", f"Invalid period: {period}")
        raise HTTPException(status_code=400, detail=f"Invalid period: {period}")

# Budget Policy Endpoints

@policy_router.post("", response_model=PolicyResponse, status_code=201)
@log_function()
async def create_policy(
    request: CreatePolicyRequest,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Create a new budget policy.
    
    Args:
        request: The policy creation request
        user: The authenticated user
    
    Returns:
        The created policy
    """
    debug_log.info("budget_api", "Creating budget policy")
    
    # Validate budget ID if provided
    if request.budget_id:
        budget = budget_repo.get_by_id(request.budget_id)
        if not budget:
            debug_log.warn("budget_api", f"Budget not found: {request.budget_id}")
            raise HTTPException(
                status_code=404, 
                detail=f"Budget with ID {request.budget_id} not found"
            )
    
    try:
        # Create the policy
        policy = budget_engine.set_policy(
            budget_id=request.budget_id,
            period=request.period,
            token_limit=request.token_limit,
            cost_limit=request.cost_limit,
            tier=request.tier,
            provider=request.provider,
            component=request.component,
            task_type=request.task_type,
            policy_type=request.type,
            enabled=request.enabled
        )
        
        # Return the response
        return create_policy_response(policy)
    except ValueError as e:
        debug_log.error("budget_api", f"Error creating policy: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@policy_router.get("", response_model=PolicyListResponse)
@log_function()
async def list_policies(
    pagination: Dict[str, int] = Depends(pagination_params),
    period: Optional[str] = Query(None, description="Filter by period"),
    tier: Optional[str] = Query(None, description="Filter by tier"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    component: Optional[str] = Query(None, description="Filter by component"),
    task_type: Optional[str] = Query(None, description="Filter by task type"),
    enabled: Optional[bool] = Query(None, description="Filter by enabled status"),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    List policies with optional filtering.
    
    Args:
        pagination: Pagination parameters
        period: Filter by period
        tier: Filter by tier
        provider: Filter by provider
        component: Filter by component
        task_type: Filter by task type
        enabled: Filter by enabled status
        user: The authenticated user
    
    Returns:
        List of policies with pagination info
    """
    debug_log.info("budget_api", "Listing policies")
    
    # Get active policies with optional filtering
    # Convert string tier to enum if provided
    tier_enum = None
    if tier:
        try:
            tier_enum = BudgetTier(tier)
        except ValueError:
            debug_log.error("budget_api", f"Invalid tier: {tier}")
            raise HTTPException(status_code=400, detail=f"Invalid tier: {tier}")
    
    # Get policies
    policies = policy_repo.get_active_policies(
        tier=tier_enum,
        provider=provider,
        component=component,
        task_type=task_type
    )
    
    # Apply additional filtering
    if period:
        try:
            period_enum = BudgetPeriod(period)
            policies = [p for p in policies if p.period == period_enum]
        except ValueError:
            debug_log.error("budget_api", f"Invalid period: {period}")
            raise HTTPException(status_code=400, detail=f"Invalid period: {period}")
    
    if enabled is not None:
        policies = [p for p in policies if p.enabled == enabled]
    
    # Apply pagination (in a real implementation, this would be done at the DB level)
    total = len(policies)
    policies = policies[pagination["offset"]:pagination["offset"] + pagination["limit"]]
    
    # Convert to response models
    policy_responses = [create_policy_response(policy) for policy in policies]
    
    # Return paginated response
    return PolicyListResponse(
        items=policy_responses,
        total=total,
        page=pagination["page"],
        limit=pagination["limit"]
    )

@policy_router.get("/{policy_id}", response_model=PolicyResponse)
@log_function()
async def get_policy(
    policy_id: str = Depends(policy_id_param),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Get a policy by ID.
    
    Args:
        policy_id: The policy ID
        user: The authenticated user
    
    Returns:
        The policy
    
    Raises:
        HTTPException: If the policy is not found
    """
    debug_log.info("budget_api", f"Getting policy: {policy_id}")
    
    # Get the policy
    policy = policy_repo.get_by_id(policy_id)
    if not policy:
        debug_log.warn("budget_api", f"Policy not found: {policy_id}")
        raise HTTPException(status_code=404, detail=f"Policy with ID {policy_id} not found")
    
    # Return the response
    return create_policy_response(policy)

@policy_router.put("/{policy_id}", response_model=PolicyResponse)
@log_function()
async def update_policy(
    request: UpdatePolicyRequest,
    policy_id: str = Depends(policy_id_param),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Update a policy.
    
    Args:
        request: The policy update request
        policy_id: The policy ID
        user: The authenticated user
    
    Returns:
        The updated policy
    
    Raises:
        HTTPException: If the policy is not found
    """
    debug_log.info("budget_api", f"Updating policy: {policy_id}")
    
    # Get the policy
    policy = policy_repo.get_by_id(policy_id)
    if not policy:
        debug_log.warn("budget_api", f"Policy not found: {policy_id}")
        raise HTTPException(status_code=404, detail=f"Policy with ID {policy_id} not found")
    
    try:
        # Apply updates to the policy
        if request.type is not None:
            policy.type = BudgetPolicyType(request.type)
        if request.token_limit is not None:
            policy.token_limit = request.token_limit
        if request.cost_limit is not None:
            policy.cost_limit = request.cost_limit
        if request.warning_threshold is not None:
            policy.warning_threshold = request.warning_threshold
        if request.action_threshold is not None:
            policy.action_threshold = request.action_threshold
        if request.enabled is not None:
            policy.enabled = request.enabled
        
        # Save the updated policy
        updated_policy = policy_repo.update(policy)
        
        # Return the response
        return create_policy_response(updated_policy)
    except ValueError as e:
        debug_log.error("budget_api", f"Error updating policy: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@policy_router.delete("/{policy_id}", response_model=SuccessResponse)
@log_function()
async def delete_policy(
    policy_id: str = Depends(policy_id_param),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Disable a policy (soft delete by setting enabled to False).
    
    Args:
        policy_id: The policy ID
        user: The authenticated user
    
    Returns:
        Success message
    
    Raises:
        HTTPException: If the policy is not found
    """
    debug_log.info("budget_api", f"Disabling policy: {policy_id}")
    
    # Disable the policy
    success = budget_engine.disable_policy(policy_id)
    if not success:
        debug_log.warn("budget_api", f"Policy not found: {policy_id}")
        raise HTTPException(status_code=404, detail=f"Policy with ID {policy_id} not found")
    
    # Return success message
    return SuccessResponse(message=f"Policy {policy_id} disabled successfully")

# Budget Allocation Endpoints

@allocation_router.post("", response_model=AllocationResponse, status_code=201)
@log_function()
async def create_allocation(
    request: CreateAllocationRequest,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Create a new budget allocation.
    
    Args:
        request: The allocation creation request
        user: The authenticated user
    
    Returns:
        The created allocation
    """
    debug_log.info("budget_api", "Creating budget allocation")
    
    # Validate budget ID if provided
    if request.budget_id:
        budget = budget_repo.get_by_id(request.budget_id)
        if not budget:
            debug_log.warn("budget_api", f"Budget not found: {request.budget_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Budget with ID {request.budget_id} not found"
            )
    
    try:
        # Create the allocation
        allocation = allocation_manager.allocate_budget(
            context_id=request.context_id,
            component=request.component,
            tokens=request.tokens_allocated,
            budget_id=request.budget_id,
            tier=request.tier,
            provider=request.provider,
            model=request.model,
            task_type=request.task_type,
            priority=request.priority,
            metadata=request.metadata,
            expiration_time=request.expiration_time
        )
        
        # Return the response
        return create_allocation_response(allocation)
    except ValueError as e:
        debug_log.error("budget_api", f"Error creating allocation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@allocation_router.get("", response_model=AllocationListResponse)
@log_function()
async def list_allocations(
    pagination: Dict[str, int] = Depends(pagination_params),
    context_id: Optional[str] = Query(None, description="Filter by context ID"),
    component: Optional[str] = Query(None, description="Filter by component"),
    tier: Optional[str] = Query(None, description="Filter by tier"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    model: Optional[str] = Query(None, description="Filter by model"),
    task_type: Optional[str] = Query(None, description="Filter by task type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    List allocations with optional filtering.
    
    Args:
        pagination: Pagination parameters
        context_id: Filter by context ID
        component: Filter by component
        tier: Filter by tier
        provider: Filter by provider
        model: Filter by model
        task_type: Filter by task type
        is_active: Filter by active status
        user: The authenticated user
    
    Returns:
        List of allocations with pagination info
    """
    debug_log.info("budget_api", "Listing allocations")
    
    # Convert string tier to enum if provided
    tier_enum = None
    if tier:
        try:
            tier_enum = BudgetTier(tier)
        except ValueError:
            debug_log.error("budget_api", f"Invalid tier: {tier}")
            raise HTTPException(status_code=400, detail=f"Invalid tier: {tier}")
    
    # Get allocations with filtering
    allocations = allocation_repo.get_active_allocations(
        component=component,
        tier=tier_enum,
        provider=provider,
        model=model,
        task_type=task_type
    )
    
    # Apply additional filtering
    if context_id:
        allocations = [a for a in allocations if a.context_id == context_id]
    
    if is_active is not None:
        allocations = [a for a in allocations if a.is_active == is_active]
    
    # Apply pagination (in a real implementation, this would be done at the DB level)
    total = len(allocations)
    allocations = allocations[pagination["offset"]:pagination["offset"] + pagination["limit"]]
    
    # Convert to response models
    allocation_responses = [create_allocation_response(allocation) for allocation in allocations]
    
    # Return paginated response
    return AllocationListResponse(
        items=allocation_responses,
        total=total,
        page=pagination["page"],
        limit=pagination["limit"]
    )

@allocation_router.get("/{allocation_id}", response_model=AllocationResponse)
@log_function()
async def get_allocation(
    allocation_id: str = Depends(allocation_id_param),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Get an allocation by ID.
    
    Args:
        allocation_id: The allocation ID
        user: The authenticated user
    
    Returns:
        The allocation
    
    Raises:
        HTTPException: If the allocation is not found
    """
    debug_log.info("budget_api", f"Getting allocation: {allocation_id}")
    
    # Get the allocation
    allocation = allocation_repo.get_by_id(allocation_id)
    if not allocation:
        debug_log.warn("budget_api", f"Allocation not found: {allocation_id}")
        raise HTTPException(status_code=404, detail=f"Allocation with ID {allocation_id} not found")
    
    # Return the response
    return create_allocation_response(allocation)

@allocation_router.post("/{allocation_id}/release", response_model=SuccessResponse)
@log_function()
async def release_allocation(
    allocation_id: str = Depends(allocation_id_param),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Release an allocation (mark as inactive).
    
    Args:
        allocation_id: The allocation ID
        user: The authenticated user
    
    Returns:
        Success message
    
    Raises:
        HTTPException: If the allocation is not found
    """
    debug_log.info("budget_api", f"Releasing allocation: {allocation_id}")
    
    # Release the allocation
    success = allocation_manager.release_allocation(allocation_id)
    if not success:
        debug_log.warn("budget_api", f"Allocation not found: {allocation_id}")
        raise HTTPException(status_code=404, detail=f"Allocation with ID {allocation_id} not found")
    
    # Return success message
    return SuccessResponse(message=f"Allocation {allocation_id} released successfully")

@allocation_router.get("/context/{context_id}", response_model=AllocationResponse)
@log_function()
async def get_allocation_by_context(
    context_id: str = Path(..., description="Context ID"),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Get an active allocation by context ID.
    
    Args:
        context_id: The context ID
        user: The authenticated user
    
    Returns:
        The allocation
    
    Raises:
        HTTPException: If the allocation is not found
    """
    debug_log.info("budget_api", f"Getting allocation by context: {context_id}")
    
    # Get the allocation
    allocation = allocation_repo.get_by_context_id(context_id)
    if not allocation:
        debug_log.warn("budget_api", f"No active allocation found for context: {context_id}")
        raise HTTPException(
            status_code=404, 
            detail=f"No active allocation found for context: {context_id}"
        )
    
    # Return the response
    return create_allocation_response(allocation)

# Usage Tracking Endpoints

@usage_router.post("/record", response_model=UsageRecordResponse, status_code=201)
@log_function()
async def record_usage(
    request: RecordUsageRequest,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Record token usage.
    
    Args:
        request: The usage record request
        user: The authenticated user
    
    Returns:
        The created usage record
    """
    debug_log.info("budget_api", "Recording usage")
    
    try:
        # Record the usage
        record = tracking_manager.record_usage(
            context_id=request.context_id,
            allocation_id=request.allocation_id,
            component=request.component,
            provider=request.provider,
            model=request.model,
            task_type=request.task_type,
            input_tokens=request.input_tokens,
            output_tokens=request.output_tokens,
            operation_id=request.operation_id,
            request_id=request.request_id,
            user_id=request.user_id,
            metadata=request.metadata
        )
        
        # Return the response
        return create_usage_record_response(record)
    except ValueError as e:
        debug_log.error("budget_api", f"Error recording usage: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@usage_router.get("/records", response_model=UsageRecordListResponse)
@log_function()
async def list_usage_records(
    pagination: Dict[str, int] = Depends(pagination_params),
    context_id: Optional[str] = Query(None, description="Filter by context ID"),
    allocation_id: Optional[str] = Query(None, description="Filter by allocation ID"),
    component: Optional[str] = Query(None, description="Filter by component"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    model: Optional[str] = Query(None, description="Filter by model"),
    task_type: Optional[str] = Query(None, description="Filter by task type"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    List usage records with optional filtering.
    
    Args:
        pagination: Pagination parameters
        context_id: Filter by context ID
        allocation_id: Filter by allocation ID
        component: Filter by component
        provider: Filter by provider
        model: Filter by model
        task_type: Filter by task type
        start_date: Filter by start date
        end_date: Filter by end date
        user: The authenticated user
    
    Returns:
        List of usage records with pagination info
    """
    debug_log.info("budget_api", "Listing usage records")
    
    # Determine period from date range for repository query
    period = BudgetPeriod.DAILY  # Default
    if start_date and end_date:
        # Custom date range
        period = None
    
    # Get usage records
    records = usage_repo.get_usage_for_period(
        period=period if period else BudgetPeriod.MONTHLY,  # Use a large period for custom ranges
        provider=provider,
        component=component,
        model=model,
        task_type=task_type,
        start_time=start_date,
        end_time=end_date
    )
    
    # Apply additional filtering
    if context_id:
        records = [r for r in records if r.context_id == context_id]
    
    if allocation_id:
        records = [r for r in records if r.allocation_id == allocation_id]
    
    # Apply pagination (in a real implementation, this would be done at the DB level)
    total = len(records)
    records = records[pagination["offset"]:pagination["offset"] + pagination["limit"]]
    
    # Convert to response models
    record_responses = [create_usage_record_response(record) for record in records]
    
    # Return paginated response
    return UsageRecordListResponse(
        items=record_responses,
        total=total,
        page=pagination["page"],
        limit=pagination["limit"]
    )

@usage_router.get("/records/{record_id}", response_model=UsageRecordResponse)
@log_function()
async def get_usage_record(
    record_id: str = Depends(record_id_param),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Get a usage record by ID.
    
    Args:
        record_id: The record ID
        user: The authenticated user
    
    Returns:
        The usage record
    
    Raises:
        HTTPException: If the record is not found
    """
    debug_log.info("budget_api", f"Getting usage record: {record_id}")
    
    # Get the record
    record = usage_repo.get_by_id(record_id)
    if not record:
        debug_log.warn("budget_api", f"Usage record not found: {record_id}")
        raise HTTPException(status_code=404, detail=f"Usage record with ID {record_id} not found")
    
    # Return the response
    return create_usage_record_response(record)

@usage_router.post("/summary", response_model=UsageSummaryResponse)
@log_function()
async def get_usage_summary(
    request: GetUsageSummaryRequest,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Get usage summary.
    
    Args:
        request: The usage summary request
        user: The authenticated user
    
    Returns:
        Usage summary
    """
    debug_log.info("budget_api", f"Getting usage summary for period: {request.period}")
    
    try:
        # Convert period string to enum
        period_enum = BudgetPeriod(request.period)
        
        # Get usage summary
        summary = usage_repo.get_usage_summary(
            period=period_enum,
            budget_id=request.budget_id,
            provider=request.provider,
            component=request.component,
            model=request.model,
            task_type=request.task_type,
            start_time=request.start_time,
            end_time=request.end_time
        )
        
        # Return the summary
        return UsageSummaryResponse(**summary)
    except ValueError as e:
        debug_log.error("budget_api", f"Error getting usage summary: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# Alert Endpoints

@alert_router.get("", response_model=AlertListResponse)
@log_function()
async def list_alerts(
    pagination: Dict[str, int] = Depends(pagination_params),
    budget_id: Optional[str] = Query(None, description="Filter by budget ID"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    type: Optional[str] = Query(None, description="Filter by type"),
    acknowledged: Optional[bool] = Query(None, description="Filter by acknowledgement status"),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    List alerts with optional filtering.
    
    Args:
        pagination: Pagination parameters
        budget_id: Filter by budget ID
        severity: Filter by severity
        type: Filter by type
        acknowledged: Filter by acknowledgement status
        user: The authenticated user
    
    Returns:
        List of alerts with pagination info
    """
    debug_log.info("budget_api", "Listing alerts")
    
    # Get unacknowledged alerts by default
    if acknowledged is None:
        alerts = alert_repo.get_unacknowledged_alerts(budget_id=budget_id, severity=severity)
    else:
        # Get all alerts and filter by acknowledged status
        # (In a real implementation, this would be done at the repository level)
        alerts = alert_repo.get_all()
        alerts = [a for a in alerts if a.acknowledged == acknowledged]
        
        # Apply budget_id filter if provided
        if budget_id:
            alerts = [a for a in alerts if a.budget_id == budget_id]
        
        # Apply severity filter if provided
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
    
    # Apply type filter if provided
    if type:
        alerts = [a for a in alerts if a.type == type]
    
    # Apply pagination (in a real implementation, this would be done at the DB level)
    total = len(alerts)
    alerts = alerts[pagination["offset"]:pagination["offset"] + pagination["limit"]]
    
    # Convert to response models
    alert_responses = [create_alert_response(alert) for alert in alerts]
    
    # Return paginated response
    return AlertListResponse(
        items=alert_responses,
        total=total,
        page=pagination["page"],
        limit=pagination["limit"]
    )

@alert_router.get("/{alert_id}", response_model=AlertResponse)
@log_function()
async def get_alert(
    alert_id: str = Depends(alert_id_param),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Get an alert by ID.
    
    Args:
        alert_id: The alert ID
        user: The authenticated user
    
    Returns:
        The alert
    
    Raises:
        HTTPException: If the alert is not found
    """
    debug_log.info("budget_api", f"Getting alert: {alert_id}")
    
    # Get the alert
    alert = alert_repo.get_by_id(alert_id)
    if not alert:
        debug_log.warn("budget_api", f"Alert not found: {alert_id}")
        raise HTTPException(status_code=404, detail=f"Alert with ID {alert_id} not found")
    
    # Return the response
    return create_alert_response(alert)

@alert_router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
@log_function()
async def acknowledge_alert(
    alert_id: str = Depends(alert_id_param),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Acknowledge an alert.
    
    Args:
        alert_id: The alert ID
        user: The authenticated user
    
    Returns:
        The updated alert
    
    Raises:
        HTTPException: If the alert is not found
    """
    debug_log.info("budget_api", f"Acknowledging alert: {alert_id}")
    
    # Acknowledge the alert
    updated_alert = alert_repo.acknowledge_alert(alert_id, user_id=user["user_id"])
    if not updated_alert:
        debug_log.warn("budget_api", f"Alert not found: {alert_id}")
        raise HTTPException(status_code=404, detail=f"Alert with ID {alert_id} not found")
    
    # Return the response
    return create_alert_response(updated_alert)

@alert_router.post("/check", response_model=List[AlertResponse])
@log_function()
async def check_budget_alerts(
    budget_id: Optional[str] = Query(None, description="Budget ID to check"),
    period: Optional[str] = Query(None, description="Period to check"),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Check for budget violations and create alerts.
    
    Args:
        budget_id: The budget ID to check
        period: The period to check
        user: The authenticated user
    
    Returns:
        List of created alerts
    """
    debug_log.info("budget_api", f"Checking budget alerts for budget: {budget_id}, period: {period}")
    
    try:
        # Convert period string to enum if provided
        period_enum = None
        if period:
            period_enum = BudgetPeriod(period)
        
        # Check for violations and create alerts
        alerts = budget_engine.check_and_create_alerts(
            budget_id=budget_id,
            period=period_enum
        )
        
        # Convert to response models
        alert_responses = [create_alert_response(alert) for alert in alerts]
        
        return alert_responses
    except ValueError as e:
        debug_log.error("budget_api", f"Error checking budget alerts: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# Price Endpoints

@price_router.get("", response_model=List[PriceResponse])
@log_function()
async def list_prices(
    provider: Optional[str] = Query(None, description="Filter by provider"),
    model: Optional[str] = Query(None, description="Filter by model"),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    List current prices with optional filtering.
    
    Args:
        provider: Filter by provider
        model: Filter by model
        user: The authenticated user
    
    Returns:
        List of prices
    """
    debug_log.info("budget_api", "Listing prices")
    
    # Get all current pricing data
    # This could be optimized with a repository method
    session = pricing_repo.db_repository.db_manager.get_session()
    
    try:
        from sqlalchemy import and_, or_
        from datetime import datetime
        from budget.data.db_models import ProviderPricingDB
        
        now = datetime.now()
        
        # Build query
        query = session.query(ProviderPricingDB).filter(
            ProviderPricingDB.effective_date <= now,
            or_(
                ProviderPricingDB.end_date == None,
                ProviderPricingDB.end_date > now
            )
        )
        
        # Apply filters
        if provider:
            query = query.filter(ProviderPricingDB.provider == provider)
        
        if model:
            query = query.filter(ProviderPricingDB.model == model)
        
        # Execute query
        results = query.all()
        
        # Convert to domain models
        prices = [pricing_repo.db_repository._to_pydantic(result) for result in results]
        
        # Convert to response models
        price_responses = [create_price_response(price) for price in prices]
        
        return price_responses
    finally:
        session.close()

@price_router.post("/current", response_model=PriceResponse)
@log_function()
async def get_current_price(
    request: PriceRequest,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Get current price for a provider and model.
    
    Args:
        request: The price request
        user: The authenticated user
    
    Returns:
        Current price information
    
    Raises:
        HTTPException: If the price is not found
    """
    debug_log.info("budget_api", f"Getting current price for {request.provider}/{request.model}")
    
    # Get current pricing
    price = pricing_repo.get_current_pricing(request.provider, request.model)
    if not price:
        debug_log.warn("budget_api", f"No pricing found for {request.provider}/{request.model}")
        raise HTTPException(
            status_code=404, 
            detail=f"No pricing found for {request.provider}/{request.model}"
        )
    
    # Return the response
    return create_price_response(price)

@price_router.get("/history/{provider}/{model}", response_model=List[PriceResponse])
@log_function()
async def get_price_history(
    provider: str = Path(..., description="Provider name"),
    model: str = Path(..., description="Model name"),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Get price history for a provider and model.
    
    Args:
        provider: Provider name
        model: Model name
        user: The authenticated user
    
    Returns:
        Price history
    """
    debug_log.info("budget_api", f"Getting price history for {provider}/{model}")
    
    # Get price history
    prices = pricing_repo.get_pricing_history(provider, model)
    
    # Convert to response models
    price_responses = [create_price_response(price) for price in prices]
    
    return price_responses

@price_router.post("/recommendations", response_model=ModelRecommendationListResponse)
@log_function()
async def get_model_recommendations(
    request: ModelRecommendationRequest,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Get model recommendations based on budget constraints.
    
    Args:
        request: The recommendation request
        user: The authenticated user
    
    Returns:
        List of recommended models
    """
    debug_log.info("budget_api", f"Getting model recommendations for {request.provider}/{request.model}")
    
    # Get current pricing to calculate current cost
    current_price = pricing_repo.get_current_pricing(request.provider, request.model)
    if not current_price:
        debug_log.warn("budget_api", f"No pricing found for {request.provider}/{request.model}")
        raise HTTPException(
            status_code=404, 
            detail=f"No pricing found for {request.provider}/{request.model}"
        )
    
    # Calculate current cost for the context size
    input_tokens = int(request.context_size * 0.25)  # Assume 25% input
    output_tokens = int(request.context_size * 0.75)  # Assume 75% output
    
    current_cost = (
        input_tokens * current_price.input_cost_per_token +
        output_tokens * current_price.output_cost_per_token
    )
    
    # Get model recommendations
    recommendations = budget_engine.get_model_recommendations(
        provider=request.provider,
        model=request.model,
        task_type=request.task_type,
        context_size=request.context_size
    )
    
    # Convert to response models
    recommendation_responses = [
        create_model_recommendation_response(recommendation) 
        for recommendation in recommendations
    ]
    
    # Return the response
    return ModelRecommendationListResponse(
        items=recommendation_responses,
        current_model=request.model,
        current_provider=request.provider,
        current_cost=current_cost
    )

# Include sub-routers
router.include_router(budget_router)
router.include_router(policy_router)
router.include_router(allocation_router)
router.include_router(usage_router)
router.include_router(report_router)
router.include_router(alert_router)
router.include_router(price_router)

# Health check endpoint
@router.get("/health")
@log_function()
async def health_check():
    """Health check endpoint."""
    debug_log.info("budget_api", "Health check")
    
    return {
        "status": "healthy",
        "component": "budget",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat()
    }