"""
Budget Repository

This module provides a repository pattern implementation for budget data access.
It abstracts the underlying storage mechanisms and provides a consistent interface
for data operations.
"""

import os
import sys
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Type, TypeVar, Generic

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

# Import models for type annotations
from budget.data.models import (
    BudgetTier, BudgetPeriod, BudgetPolicyType, TaskPriority,
    PriceType, Budget, BudgetPolicy, BudgetAllocation,
    UsageRecord, Alert, ProviderPricing, PriceUpdateRecord,
    PriceSource, BudgetSummary
)

# Import database models and repositories
from budget.data.db_models import (
    db_manager, budget_repository, policy_repository, 
    allocation_repository, usage_repository, alert_repository,
    pricing_repository, update_repository, source_repository
)

# Generic type for models
T = TypeVar('T')

class Repository(Generic[T]):
    """
    Generic repository interface.
    
    Provides a consistent interface for data access operations.
    """
    
    def __init__(self, db_repository):
        """Initialize with a database repository."""
        self.db_repository = db_repository
        
    @log_function()
    def get_by_id(self, id_value: str) -> Optional[T]:
        """
        Get a model by its ID.
        
        Args:
            id_value: The ID of the model to retrieve
            
        Returns:
            The model if found, None otherwise
        """
        debug_log.debug("budget_repository", f"Getting model by ID: {id_value}")
        return self.db_repository.get_by_id(id_value)
        
    @log_function()
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        """
        Get all models, optionally with pagination.
        
        Args:
            limit: Maximum number of models to retrieve
            offset: Number of models to skip
            
        Returns:
            List of models
        """
        debug_log.debug("budget_repository", f"Getting all models (limit={limit}, offset={offset})")
        return self.db_repository.get_all(limit=limit, offset=offset)
        
    @log_function()
    def create(self, model: T) -> T:
        """
        Create a new model.
        
        Args:
            model: The model to create
            
        Returns:
            The created model
        """
        debug_log.debug("budget_repository", f"Creating model: {model}")
        return self.db_repository.create(model)
        
    @log_function()
    def update(self, model: T) -> Optional[T]:
        """
        Update an existing model.
        
        Args:
            model: The model to update
            
        Returns:
            The updated model if successful, None otherwise
        """
        debug_log.debug("budget_repository", f"Updating model: {model}")
        return self.db_repository.update(model)
        
    @log_function()
    def delete(self, id_value: str) -> bool:
        """
        Delete a model by its ID.
        
        Args:
            id_value: The ID of the model to delete
            
        Returns:
            True if the model was deleted, False otherwise
        """
        debug_log.debug("budget_repository", f"Deleting model with ID: {id_value}")
        return self.db_repository.delete(id_value)
        
    @log_function()
    def upsert(self, model: T) -> T:
        """
        Create or update a model.
        
        Args:
            model: The model to create or update
            
        Returns:
            The created or updated model
        """
        debug_log.debug("budget_repository", f"Upserting model: {model}")
        return self.db_repository.upsert(model)


class BudgetRepository(Repository[Budget]):
    """Repository for Budget models."""
    
    def __init__(self):
        """Initialize the repository."""
        super().__init__(budget_repository)
        
    @log_function()
    def get_by_name(self, name: str) -> Optional[Budget]:
        """
        Get a budget by its name.
        
        Args:
            name: The name of the budget to retrieve
            
        Returns:
            The budget if found, None otherwise
        """
        debug_log.debug("budget_repository", f"Getting budget by name: {name}")
        
        session = db_manager.get_session()
        try:
            # Query for budget with matching name
            from budget.data.db_models import BudgetDB
            result = session.query(BudgetDB).filter(BudgetDB.name == name).first()
            
            if result:
                return self.db_repository._to_pydantic(result)
            return None
            
        finally:
            session.close()
            
    @log_function()
    def get_active_budgets(self) -> List[Budget]:
        """
        Get all active budgets.
        
        Returns:
            List of active budgets
        """
        debug_log.debug("budget_repository", "Getting active budgets")
        
        session = db_manager.get_session()
        try:
            # Query for active budgets
            from budget.data.db_models import BudgetDB
            results = session.query(BudgetDB).filter(BudgetDB.is_active == True).all()
            
            return [self.db_repository._to_pydantic(result) for result in results]
            
        finally:
            session.close()


class BudgetPolicyRepository(Repository[BudgetPolicy]):
    """Repository for BudgetPolicy models."""
    
    def __init__(self):
        """Initialize the repository."""
        super().__init__(policy_repository)
        
    @log_function()
    def get_by_budget_id(self, budget_id: str) -> List[BudgetPolicy]:
        """
        Get all policies for a budget.
        
        Args:
            budget_id: The ID of the budget
            
        Returns:
            List of budget policies
        """
        debug_log.debug("budget_repository", f"Getting policies for budget: {budget_id}")
        
        session = db_manager.get_session()
        try:
            # Query for policies with matching budget_id
            from budget.data.db_models import BudgetPolicyDB
            results = session.query(BudgetPolicyDB).filter(
                BudgetPolicyDB.budget_id == budget_id
            ).all()
            
            return [self.db_repository._to_pydantic(result) for result in results]
            
        finally:
            session.close()
            
    @log_function()
    def get_active_policies(
        self,
        tier: Optional[BudgetTier] = None,
        provider: Optional[str] = None,
        component: Optional[str] = None,
        task_type: Optional[str] = None
    ) -> List[BudgetPolicy]:
        """
        Get active policies matching the specified criteria.
        
        Args:
            tier: Filter by budget tier
            provider: Filter by provider
            component: Filter by component
            task_type: Filter by task type
            
        Returns:
            List of matching active policies
        """
        debug_log.debug("budget_repository", "Getting active policies with filters")
        
        session = db_manager.get_session()
        try:
            # Query for active policies with matching criteria
            from budget.data.db_models import BudgetPolicyDB
            query = session.query(BudgetPolicyDB).filter(
                BudgetPolicyDB.enabled == True
            )
            
            # Apply filters
            if tier:
                query = query.filter(BudgetPolicyDB.tier == tier)
            if provider:
                query = query.filter(BudgetPolicyDB.provider == provider)
            if component:
                query = query.filter(BudgetPolicyDB.component == component)
            if task_type:
                query = query.filter(BudgetPolicyDB.task_type == task_type)
                
            # Filter by date
            now = datetime.now()
            query = query.filter(BudgetPolicyDB.start_date <= now)
            query = query.filter(
                (BudgetPolicyDB.end_date == None) | (BudgetPolicyDB.end_date > now)
            )
            
            results = query.all()
            
            return [self.db_repository._to_pydantic(result) for result in results]
            
        finally:
            session.close()


class BudgetAllocationRepository(Repository[BudgetAllocation]):
    """Repository for BudgetAllocation models."""
    
    def __init__(self):
        """Initialize the repository."""
        super().__init__(allocation_repository)
        
    @log_function()
    def get_by_context_id(self, context_id: str) -> Optional[BudgetAllocation]:
        """
        Get an allocation by its context ID.
        
        Args:
            context_id: The context ID to retrieve allocation for
            
        Returns:
            The allocation if found, None otherwise
        """
        debug_log.debug("budget_repository", f"Getting allocation by context ID: {context_id}")
        
        session = db_manager.get_session()
        try:
            # Query for allocation with matching context_id
            from budget.data.db_models import BudgetAllocationDB
            result = session.query(BudgetAllocationDB).filter(
                BudgetAllocationDB.context_id == context_id,
                BudgetAllocationDB.is_active == True
            ).first()
            
            if result:
                return self.db_repository._to_pydantic(result)
            return None
            
        finally:
            session.close()
            
    @log_function()
    def get_active_allocations(
        self,
        budget_id: Optional[str] = None,
        component: Optional[str] = None,
        tier: Optional[BudgetTier] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        task_type: Optional[str] = None
    ) -> List[BudgetAllocation]:
        """
        Get active allocations matching the specified criteria.
        
        Args:
            budget_id: Filter by budget ID
            component: Filter by component
            tier: Filter by budget tier
            provider: Filter by provider
            model: Filter by model
            task_type: Filter by task type
            
        Returns:
            List of matching active allocations
        """
        debug_log.debug("budget_repository", "Getting active allocations with filters")
        
        session = db_manager.get_session()
        try:
            # Query for active allocations with matching criteria
            from budget.data.db_models import BudgetAllocationDB
            query = session.query(BudgetAllocationDB).filter(
                BudgetAllocationDB.is_active == True
            )
            
            # Apply filters
            if budget_id:
                query = query.filter(BudgetAllocationDB.budget_id == budget_id)
            if component:
                query = query.filter(BudgetAllocationDB.component == component)
            if tier:
                query = query.filter(BudgetAllocationDB.tier == tier)
            if provider:
                query = query.filter(BudgetAllocationDB.provider == provider)
            if model:
                query = query.filter(BudgetAllocationDB.model == model)
            if task_type:
                query = query.filter(BudgetAllocationDB.task_type == task_type)
                
            # Filter by expiration time
            now = datetime.now()
            query = query.filter(
                (BudgetAllocationDB.expiration_time == None) | 
                (BudgetAllocationDB.expiration_time > now)
            )
            
            results = query.all()
            
            return [self.db_repository._to_pydantic(result) for result in results]
            
        finally:
            session.close()
            
    @log_function()
    def update_usage(
        self,
        allocation_id: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost: Optional[float] = None
    ) -> Optional[BudgetAllocation]:
        """
        Update usage for an allocation.
        
        Args:
            allocation_id: The ID of the allocation to update
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used
            cost: Actual cost if known
            
        Returns:
            Updated allocation if successful, None otherwise
        """
        debug_log.debug("budget_repository", 
                      f"Updating usage for allocation {allocation_id}: "
                      f"input={input_tokens}, output={output_tokens}, cost={cost}")
        
        session = db_manager.get_session()
        try:
            # Get allocation
            from budget.data.db_models import BudgetAllocationDB
            allocation_db = session.query(BudgetAllocationDB).get(allocation_id)
            
            if not allocation_db:
                debug_log.warn("budget_repository", 
                              f"Allocation {allocation_id} not found for usage update")
                return None
                
            # Convert to Pydantic model
            allocation = self.db_repository._to_pydantic(allocation_db)
            
            # Record usage
            tokens_recorded = allocation.record_usage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost
            )
            
            if tokens_recorded > 0:
                # Update database model
                allocation_db.tokens_used = allocation.tokens_used
                allocation_db.input_tokens_used = allocation.input_tokens_used
                allocation_db.output_tokens_used = allocation.output_tokens_used
                allocation_db.actual_cost = allocation.actual_cost
                allocation_db.last_updated = allocation.last_updated
                allocation_db.is_active = allocation.is_active
                
                # Commit changes
                session.commit()
                
                return allocation
            
            return allocation
            
        except Exception as e:
            session.rollback()
            debug_log.error("budget_repository", 
                           f"Error updating usage for allocation {allocation_id}: {str(e)}")
            raise
            
        finally:
            session.close()


class UsageRecordRepository(Repository[UsageRecord]):
    """Repository for UsageRecord models."""
    
    def __init__(self):
        """Initialize the repository."""
        super().__init__(usage_repository)
        
    @log_function()
    def get_usage_for_period(
        self,
        period: BudgetPeriod,
        budget_id: Optional[str] = None,
        provider: Optional[str] = None,
        component: Optional[str] = None,
        model: Optional[str] = None,
        task_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[UsageRecord]:
        """
        Get usage records for a specific period.
        
        Args:
            period: Budget period
            budget_id: Filter by budget ID
            provider: Filter by provider
            component: Filter by component
            model: Filter by model
            task_type: Filter by task type
            start_time: Custom start time (overrides period)
            end_time: Custom end time (overrides period)
            
        Returns:
            List of matching usage records
        """
        debug_log.debug("budget_repository", f"Getting usage for period: {period}")
        
        # Calculate time range based on period if not provided
        if not start_time:
            now = datetime.now()
            if period == BudgetPeriod.HOURLY:
                start_time = now.replace(minute=0, second=0, microsecond=0)
            elif period == BudgetPeriod.DAILY:
                start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == BudgetPeriod.WEEKLY:
                # Start of week (Monday)
                start_time = now - timedelta(days=now.weekday())
                start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == BudgetPeriod.MONTHLY:
                # Start of month
                start_time = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                
        end_time = end_time or datetime.now()
        
        session = db_manager.get_session()
        try:
            # Query for usage records in the time range
            from budget.data.db_models import UsageRecordDB
            query = session.query(UsageRecordDB).filter(
                UsageRecordDB.timestamp >= start_time,
                UsageRecordDB.timestamp <= end_time
            )
            
            # Apply filters
            if budget_id:
                query = query.filter(UsageRecordDB.budget_id == budget_id)
            if provider:
                query = query.filter(UsageRecordDB.provider == provider)
            if component:
                query = query.filter(UsageRecordDB.component == component)
            if model:
                query = query.filter(UsageRecordDB.model == model)
            if task_type:
                query = query.filter(UsageRecordDB.task_type == task_type)
                
            results = query.all()
            
            return [self.db_repository._to_pydantic(result) for result in results]
            
        finally:
            session.close()
            
    @log_function()
    def get_usage_summary(
        self,
        period: BudgetPeriod,
        budget_id: Optional[str] = None,
        provider: Optional[str] = None,
        component: Optional[str] = None,
        model: Optional[str] = None,
        task_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get a summary of usage for a period.
        
        Args:
            period: Budget period
            budget_id: Filter by budget ID
            provider: Filter by provider
            component: Filter by component
            model: Filter by model
            task_type: Filter by task type
            start_time: Custom start time (overrides period)
            end_time: Custom end time (overrides period)
            
        Returns:
            Dictionary with usage summary
        """
        debug_log.debug("budget_repository", f"Getting usage summary for period: {period}")
        
        # Get usage records
        records = self.get_usage_for_period(
            period=period,
            budget_id=budget_id,
            provider=provider,
            component=component,
            model=model,
            task_type=task_type,
            start_time=start_time,
            end_time=end_time
        )
        
        if not records:
            return {
                "period": period.value,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "count": 0,
                "start_time": start_time.isoformat() if start_time else None,
                "end_time": end_time.isoformat() if end_time else None
            }
            
        # Calculate totals
        total_input_tokens = sum(record.input_tokens for record in records)
        total_output_tokens = sum(record.output_tokens for record in records)
        total_cost = sum(record.total_cost for record in records)
        
        # Group by provider, model, component, or task_type
        groups = {}
        for group_by in ["provider", "model", "component", "task_type"]:
            groups[group_by] = {}
            
            for record in records:
                key = getattr(record, group_by)
                if key not in groups[group_by]:
                    groups[group_by][key] = {
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "total_tokens": 0,
                        "cost": 0.0,
                        "count": 0
                    }
                    
                groups[group_by][key]["input_tokens"] += record.input_tokens
                groups[group_by][key]["output_tokens"] += record.output_tokens
                groups[group_by][key]["total_tokens"] += record.input_tokens + record.output_tokens
                groups[group_by][key]["cost"] += record.total_cost
                groups[group_by][key]["count"] += 1
                
        return {
            "period": period.value,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,
            "total_cost": total_cost,
            "count": len(records),
            "start_time": start_time.isoformat() if start_time else None,
            "end_time": end_time.isoformat() if end_time else None,
            "groups": groups
        }


class AlertRepository(Repository[Alert]):
    """Repository for Alert models."""
    
    def __init__(self):
        """Initialize the repository."""
        super().__init__(alert_repository)
        
    @log_function()
    def get_unacknowledged_alerts(
        self,
        budget_id: Optional[str] = None,
        severity: Optional[str] = None
    ) -> List[Alert]:
        """
        Get unacknowledged alerts.
        
        Args:
            budget_id: Filter by budget ID
            severity: Filter by severity
            
        Returns:
            List of unacknowledged alerts
        """
        debug_log.debug("budget_repository", "Getting unacknowledged alerts")
        
        session = db_manager.get_session()
        try:
            # Query for unacknowledged alerts
            from budget.data.db_models import AlertDB
            query = session.query(AlertDB).filter(AlertDB.acknowledged == False)
            
            # Apply filters
            if budget_id:
                query = query.filter(AlertDB.budget_id == budget_id)
            if severity:
                query = query.filter(AlertDB.severity == severity)
                
            # Order by timestamp (newest first)
            query = query.order_by(AlertDB.timestamp.desc())
            
            results = query.all()
            
            return [self.db_repository._to_pydantic(result) for result in results]
            
        finally:
            session.close()
            
    @log_function()
    def acknowledge_alert(
        self,
        alert_id: str,
        user_id: Optional[str] = None
    ) -> Optional[Alert]:
        """
        Acknowledge an alert.
        
        Args:
            alert_id: The ID of the alert to acknowledge
            user_id: The ID of the user acknowledging the alert
            
        Returns:
            Updated alert if successful, None otherwise
        """
        debug_log.debug("budget_repository", f"Acknowledging alert: {alert_id}")
        
        session = db_manager.get_session()
        try:
            # Get alert
            from budget.data.db_models import AlertDB
            alert = session.query(AlertDB).get(alert_id)
            
            if not alert:
                debug_log.warn("budget_repository", f"Alert {alert_id} not found for acknowledgement")
                return None
                
            # Update alert
            alert.acknowledged = True
            alert.acknowledged_by = user_id
            alert.acknowledged_at = datetime.now()
            
            # Commit changes
            session.commit()
            
            return self.db_repository._to_pydantic(alert)
            
        except Exception as e:
            session.rollback()
            debug_log.error("budget_repository", 
                          f"Error acknowledging alert {alert_id}: {str(e)}")
            raise
            
        finally:
            session.close()


class ProviderPricingRepository(Repository[ProviderPricing]):
    """Repository for ProviderPricing models."""
    
    def __init__(self):
        """Initialize the repository."""
        super().__init__(pricing_repository)
        
    @log_function()
    def get_current_pricing(
        self,
        provider: str,
        model: str
    ) -> Optional[ProviderPricing]:
        """
        Get current pricing for a provider and model.
        
        Args:
            provider: Provider name
            model: Model name
            
        Returns:
            Current pricing if found, None otherwise
        """
        debug_log.debug("budget_repository", 
                      f"Getting current pricing for {provider}/{model}")
        
        session = db_manager.get_session()
        try:
            # Query for current pricing (no end_date or end_date in future)
            from budget.data.db_models import ProviderPricingDB
            now = datetime.now()
            
            result = session.query(ProviderPricingDB).filter(
                ProviderPricingDB.provider == provider,
                ProviderPricingDB.model == model,
                ProviderPricingDB.effective_date <= now,
                ((ProviderPricingDB.end_date == None) | (ProviderPricingDB.end_date > now))
            ).order_by(ProviderPricingDB.effective_date.desc()).first()
            
            if result:
                return self.db_repository._to_pydantic(result)
            return None
            
        finally:
            session.close()
            
    @log_function()
    def get_pricing_history(
        self,
        provider: str,
        model: str
    ) -> List[ProviderPricing]:
        """
        Get pricing history for a provider and model.
        
        Args:
            provider: Provider name
            model: Model name
            
        Returns:
            List of pricing entries sorted by effective date
        """
        debug_log.debug("budget_repository", 
                      f"Getting pricing history for {provider}/{model}")
        
        session = db_manager.get_session()
        try:
            # Query for pricing history
            from budget.data.db_models import ProviderPricingDB
            
            results = session.query(ProviderPricingDB).filter(
                ProviderPricingDB.provider == provider,
                ProviderPricingDB.model == model
            ).order_by(ProviderPricingDB.effective_date.desc()).all()
            
            return [self.db_repository._to_pydantic(result) for result in results]
            
        finally:
            session.close()


class PriceUpdateRecordRepository(Repository[PriceUpdateRecord]):
    """Repository for PriceUpdateRecord models."""
    
    def __init__(self):
        """Initialize the repository."""
        super().__init__(update_repository)


class PriceSourceRepository(Repository[PriceSource]):
    """Repository for PriceSource models."""
    
    def __init__(self):
        """Initialize the repository."""
        super().__init__(source_repository)
        
    @log_function()
    def get_active_sources(self) -> List[PriceSource]:
        """
        Get all active price sources.
        
        Returns:
            List of active price sources
        """
        debug_log.debug("budget_repository", "Getting active price sources")
        
        session = db_manager.get_session()
        try:
            # Query for active price sources
            from budget.data.db_models import PriceSourceDB
            results = session.query(PriceSourceDB).filter(
                PriceSourceDB.is_active == True
            ).order_by(PriceSourceDB.trust_score.desc()).all()
            
            return [self.db_repository._to_pydantic(result) for result in results]
            
        finally:
            session.close()
            
    @log_function()
    def get_sources_for_update(self) -> List[PriceSource]:
        """
        Get price sources that are due for update.
        
        Returns:
            List of price sources due for update
        """
        debug_log.debug("budget_repository", "Getting price sources due for update")
        
        session = db_manager.get_session()
        try:
            # Query for active price sources due for update
            from budget.data.db_models import PriceSourceDB
            now = datetime.now()
            
            results = session.query(PriceSourceDB).filter(
                PriceSourceDB.is_active == True,
                (
                    (PriceSourceDB.next_update == None) |
                    (PriceSourceDB.next_update <= now)
                )
            ).order_by(PriceSourceDB.trust_score.desc()).all()
            
            return [self.db_repository._to_pydantic(result) for result in results]
            
        finally:
            session.close()
            
    @log_function()
    def update_source_timestamp(
        self,
        source_id: str,
        success: bool
    ) -> Optional[PriceSource]:
        """
        Update the last_update and next_update timestamps for a price source.
        
        Args:
            source_id: The ID of the price source
            success: Whether the update was successful
            
        Returns:
            Updated price source if successful, None otherwise
        """
        debug_log.debug("budget_repository", 
                      f"Updating timestamps for price source {source_id}")
        
        session = db_manager.get_session()
        try:
            # Get price source
            from budget.data.db_models import PriceSourceDB
            source = session.query(PriceSourceDB).get(source_id)
            
            if not source:
                debug_log.warn("budget_repository", 
                              f"Price source {source_id} not found for update")
                return None
                
            # Update timestamps
            now = datetime.now()
            source.last_update = now
            
            # Calculate next update time based on update_frequency
            if source.update_frequency:
                source.next_update = now + timedelta(minutes=source.update_frequency)
            else:
                source.next_update = now + timedelta(days=1)  # Default: daily updates
                
            # Commit changes
            session.commit()
            
            return self.db_repository._to_pydantic(source)
            
        except Exception as e:
            session.rollback()
            debug_log.error("budget_repository", 
                          f"Error updating price source {source_id}: {str(e)}")
            raise
            
        finally:
            session.close()


# Create repository instances
budget_repo = BudgetRepository()
policy_repo = BudgetPolicyRepository()
allocation_repo = BudgetAllocationRepository()
usage_repo = UsageRecordRepository()
alert_repo = AlertRepository()
pricing_repo = ProviderPricingRepository()
update_repo = PriceUpdateRecordRepository()
source_repo = PriceSourceRepository()