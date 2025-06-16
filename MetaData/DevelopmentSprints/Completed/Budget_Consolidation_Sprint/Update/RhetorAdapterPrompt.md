# Implementing the Rhetor Adapter for Budget Component

## Task Overview

You need to implement the Rhetor adapter for the Budget component, which will allow Rhetor's cost-focused budget management system to seamlessly integrate with the new unified Budget component. This adapter is crucial for providing a migration path for existing Rhetor users while bringing the benefits of the new Budget system.

## Context

Rhetor has its own budget management system that focuses on cost tracking rather than token allocation (which Apollo emphasizes). The new Budget component combines both approaches, but we need to ensure that Rhetor can continue operating with minimal changes by providing an adapter layer.

The existing Apollo adapter (`/Budget/budget/adapters/apollo.py`) provides a pattern to follow, but the Rhetor adapter needs to account for the differences in Rhetor's cost-focused approach.

## Implementation Requirements

The Rhetor adapter must:

1. Map Rhetor's cost-focused budget concepts to Budget's unified model
2. Provide API compatibility for existing Rhetor calls
3. Include migration utilities for existing Rhetor budget data
4. Implement comprehensive error handling and logging
5. Add debugging instrumentation following Tekton standards
6. Include unit tests with adequate coverage

## Implementation Steps

1. **Analyze Rhetor's Budget Implementation**
   - Review `/Rhetor/rhetor/core/budget_manager.py` to understand Rhetor's budget system
   - Identify key concepts, methods, and data structures
   - Note any Rhetor-specific terminology or conventions

2. **Design the Adapter Interface**
   - Create a class structure similar to `ApolloAdapter`
   - Define methods that map to Rhetor's budget operations
   - Plan how to translate between Rhetor and Budget concepts

3. **Implement Core Adapter Functionality**
   - Create the basic adapter class with constructor and initialization
   - Implement methods for budget creation, tracking, and reporting
   - Add cost calculation and limit enforcement logic

4. **Create Migration Utilities**
   - Implement methods to export data from Rhetor's format
   - Create import methods for the Budget component
   - Ensure data integrity during migration

5. **Implement Error Handling and Logging**
   - Add comprehensive error handling for all operations
   - Include debug instrumentation following Tekton standards
   - Log important operations and state changes

6. **Add Unit Tests**
   - Create unit tests for all adapter methods
   - Add tests for error conditions and edge cases
   - Ensure adequate test coverage (>80%)

## File Structure

```
/Budget/
  /budget/
    /adapters/
      rhetor.py               # Main adapter implementation
      /migration/
        rhetor_migration.py   # Migration utilities
  /tests/
    /unit/
      /adapters/
        test_rhetor.py        # Unit tests for Rhetor adapter
```

## Implementation Details

### 1. RhetorAdapter Class

Create a `RhetorAdapter` class similar to `ApolloAdapter` with these methods:

- `__init__`: Initialize the adapter with configuration
- `_get_or_create_rhetor_budget`: Get or create a budget for Rhetor
- `allocate_budget`: Allocate budget for a request
- `record_cost`: Record cost for a usage
- `get_budget_status`: Get budget status
- `check_budget`: Check if a budget has available funds
- `reset_budget`: Reset a budget for a new period
- `migrate_from_rhetor`: Migrate data from Rhetor format

### 2. Budget Mapping

Map these Rhetor concepts to Budget concepts:

| Rhetor Concept | Budget Concept |
|----------------|---------------|
| Cost Limit | Budget with cost_limit |
| Provider Rate | ProviderPricing |
| Usage Record | UsageRecord |
| Cost Category | Component/task_type |
| Budget Reset | BudgetPeriod |

### 3. Migration Strategy

The migration utility should:

1. Extract budget configurations from Rhetor
2. Create equivalent budgets in the Budget component
3. Transfer historical usage data
4. Provide verification of migrated data

### 4. Error Handling

Implement error handling for:
- Missing or invalid budgets
- API communication errors
- Data format incompatibilities
- Migration failures

## Code Template

Here's a template for the Rhetor adapter implementation:

```python
"""
Rhetor Integration Adapter

This module provides an adapter for integrating with Rhetor's budget system,
allowing a seamless transition to the consolidated Budget component.
"""

import os
import json
import logging
import asyncio
import uuid
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import requests

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

# Import domain models and repositories
from budget.data.models import (
    BudgetTier, BudgetPeriod, BudgetPolicyType, TaskPriority,
    Budget, BudgetPolicy, BudgetAllocation, UsageRecord, Alert
)
from budget.data.repository import (
    budget_repo, policy_repo, allocation_repo, usage_repo, alert_repo
)

# Import core components
from budget.core.engine import budget_engine
from budget.core.allocation import allocation_manager

class RhetorAdapter:
    """
    Adapter for integrating with Rhetor's budget system.
    
    This adapter provides compatibility with Rhetor's cost-focused budget API,
    translating Rhetor's calls to the new Budget component's domain model.
    """
    
    def __init__(self, api_base_url: Optional[str] = None):
        """
        Initialize the Rhetor adapter.
        
        Args:
            api_base_url: Base URL for Rhetor API (for migration purposes)
        """
        self.api_base_url = api_base_url or os.environ.get("RHETOR_API_URL", "http://localhost:8003")
        
        # Mapping of Rhetor concepts to Budget concepts
        # ... implement mappings here ...
        
        # Create or get the Rhetor budget
        self.rhetor_budget_id = self._get_or_create_rhetor_budget()
    
    @log_function()
    def _get_or_create_rhetor_budget(self) -> str:
        """
        Get or create a budget for Rhetor.
        
        Returns:
            Budget ID
        """
        debug_log.info("rhetor_adapter", "Getting or creating Rhetor budget")
        
        # ... implementation ...
        
        return budget_id
    
    @log_function()
    def allocate_budget(
        self,
        request_id: str,
        cost_estimate: float,
        provider: str,
        model: str,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Allocate budget for a Rhetor request.
        
        Args:
            request_id: Request identifier
            cost_estimate: Estimated cost for the request
            provider: Provider name
            model: Model name
            category: Request category (optional)
            
        Returns:
            Allocation details
        """
        debug_log.info("rhetor_adapter", f"Allocating ${cost_estimate} for request {request_id}")
        
        # ... implementation ...
        
        return allocation_response
    
    @log_function()
    def record_cost(
        self,
        request_id: str,
        actual_cost: float,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Record the actual cost for a request.
        
        Args:
            request_id: Request identifier
            actual_cost: Actual cost for the request
            input_tokens: Number of input tokens (optional)
            output_tokens: Number of output tokens (optional)
            
        Returns:
            Recording result
        """
        debug_log.info("rhetor_adapter", f"Recording cost ${actual_cost} for request {request_id}")
        
        # ... implementation ...
        
        return record_response
    
    @log_function()
    def get_budget_status(
        self,
        period: str = "daily",
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get budget status for Rhetor.
        
        Args:
            period: Budget period (hourly, daily, weekly, monthly)
            category: Filter by category (optional)
            
        Returns:
            Budget status
        """
        debug_log.info("rhetor_adapter", f"Getting budget status for period {period}")
        
        # ... implementation ...
        
        return budget_status
    
    @log_function()
    def check_budget(
        self,
        cost_estimate: float,
        provider: str,
        model: str,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check if a budget has available funds.
        
        Args:
            cost_estimate: Estimated cost
            provider: Provider name
            model: Model name
            category: Request category (optional)
            
        Returns:
            Budget check result
        """
        debug_log.info("rhetor_adapter", 
                     f"Checking budget for ${cost_estimate} ({provider}/{model})")
        
        # ... implementation ...
        
        return check_result
    
    @log_function()
    def reset_budget(
        self,
        period: str = "daily"
    ) -> Dict[str, Any]:
        """
        Reset a budget for a new period.
        
        Args:
            period: Budget period to reset
            
        Returns:
            Reset result
        """
        debug_log.info("rhetor_adapter", f"Resetting budget for period {period}")
        
        # ... implementation ...
        
        return reset_result
    
    @log_function()
    async def migrate_from_rhetor(self) -> Dict[str, Any]:
        """
        Migrate data from Rhetor's budget system.
        
        Returns:
            Migration results
        """
        debug_log.info("rhetor_adapter", "Starting migration from Rhetor")
        
        # ... implementation ...
        
        return migration_results

# Create global instance
rhetor_adapter = RhetorAdapter()
```

## Testing Approach

Create unit tests that:

1. Mock Rhetor's API responses
2. Test each method of the adapter
3. Verify correct mapping between Rhetor and Budget concepts
4. Test error handling and edge cases
5. Verify data migration functionality

## Integration with Rhetor

After implementing the adapter, Rhetor should be updated to use it. The changes to Rhetor should be minimal, ideally just updating import statements and configuration to point to the new Budget component.

## References

- [Apollo Adapter Implementation](/Budget/budget/adapters/apollo.py)
- [Rhetor Budget Manager](/Rhetor/rhetor/core/budget_manager.py)
- [Budget Data Models](/Budget/budget/data/models.py)
- [Budget Engine Core](/Budget/budget/core/engine.py)
- [Tekton Debug Instrumentation Guidelines](/MetaData/TektonDocumentation/DeveloperGuides/Debugging/DebuggingInstrumentation.md)

## Deliverables

1. Complete implementation of the Rhetor adapter
2. Migration utilities for existing Rhetor data
3. Unit tests with >80% coverage
4. Documentation explaining the adapter usage
5. Updates to the Budget component's integration guide