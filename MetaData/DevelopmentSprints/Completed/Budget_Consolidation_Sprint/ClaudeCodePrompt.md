# Budget Consolidation Sprint - Claude Code Implementation Guide

## Context

You are assisting with the Budget Consolidation Sprint for the Tekton project. This sprint focuses on consolidating the fragmented budget management implementations from multiple components (Apollo and Rhetor) into a unified, comprehensive Budget component with automated price monitoring capabilities.

Tekton is an intelligent orchestration system that coordinates multiple AI models and resources to efficiently solve complex software engineering problems. The current budget implementations are scattered and inconsistent, with Apollo focusing on token allocation and Rhetor focusing on cost tracking. Our goal is to consolidate these into a single system that provides the best of both approaches along with automated price updates.

## Your Role

As the AI assistant for this sprint, your role is to implement the plans following the architectural decisions and implementation plan documents. You should:

1. Follow the implementation plan exactly, progressing through phases in order
2. Implement the unified Budget component with all required features
3. Create the price monitoring system with multiple source adapters
4. Develop the integration adapters for Apollo and Rhetor
5. Create a basic dashboard UI for budget visualization
6. Ensure all code is properly documented and tested
7. Add appropriate debug instrumentation to all components

## Key Principles to Follow

### 1. Clean, Modular Architecture

- Implement a clear layered architecture
- Maintain separation of concerns between layers
- Use well-defined interfaces between components
- Create small, focused classes with single responsibilities
- Follow domain-driven design principles

### 2. Robust Price Monitoring

- Implement multiple price source adapters
- Create a verification system to cross-check prices
- Handle source failures gracefully
- Maintain price history with versioning
- Provide clear logging of price update operations

### 3. Comprehensive Budget Tracking

- Combine token allocation and cost tracking
- Support different budget periods and policies
- Implement detailed usage recording
- Support both token and cost-based enforcement
- Provide rich reporting capabilities

### 4. Integration-Friendly Design

- Create clean, well-documented APIs
- Provide client libraries for easy integration
- Implement compatibility adapters for existing components
- Use consistent naming and patterns
- Document integration patterns clearly

## Implementation Approach

### Phase 1: Core Budget Engine

1. **Budget Component Setup**
   - Create the basic directory structure
   - Set up package configuration
   - Implement debug instrumentation
   - Create the core module structure

2. **Core Data Model Implementation**
   - Implement the domain entities (Budget, Allocation, Usage Record, etc.)
   - Define relationships between entities
   - Implement validation and business rules
   - Create data transfer objects for API communication

3. **Storage Layer Implementation**
   - Create repository interfaces
   - Implement SQLite storage for development
   - Create migration scripts for schema creation
   - Implement the repository pattern

4. **Budget Engine Core Implementation**
   - Create the budget manager
   - Implement allocation logic
   - Implement token tracking
   - Implement cost calculation
   - Create budget enforcement policies

5. **Basic API Implementation**
   - Define API interfaces
   - Implement budget operation endpoints
   - Create allocation endpoints
   - Implement usage reporting endpoints
   - Add basic authentication

### Phase 2: Price Monitoring and Integration

1. **Price Source Adapter Framework**
   - Create adapter interfaces
   - Implement the adapter base class
   - Build the source registry
   - Implement configuration system

2. **Primary Price Source Implementation**
   - Implement LiteLLM adapter
   - Set up price data mapping
   - Add error handling
   - Implement rate limiting

3. **Secondary Price Source Implementation**
   - Create scrapers for LLMPrices.com and Pretrained.ai
   - Implement the generic scraper base class
   - Create parsers for different formats
   - Add error handling and retries

4. **Price Verification System**
   - Implement the verification service
   - Create conflict resolution logic
   - Implement trust scoring
   - Build the approval workflow

5. **Apollo Integration Adapter**
   - Create the Apollo client library
   - Implement mapping for Apollo's concepts
   - Build migration utilities
   - Create the compatibility layer

6. **Rhetor Integration Adapter**
   - Create the Rhetor client library
   - Implement mapping for Rhetor's concepts
   - Build migration utilities
   - Create the compatibility layer

### Phase 3: Reporting and Visualization

1. **Reporting Service Implementation**
   - Create the reporting service
   - Implement query builders
   - Add aggregation functions
   - Create export formats

2. **Dashboard API Implementation**
   - Create dashboard data endpoints
   - Implement filtering options
   - Add time-based queries
   - Create aggregation endpoints

3. **Basic Dashboard UI Implementation**
   - Create the budget overview component
   - Implement usage charts
   - Build the cost tracking component
   - Create the provider breakdown component

4. **Alert System Implementation**
   - Implement the alert service
   - Create notification channels
   - Define alert policies
   - Add user preferences

5. **Final Documentation and Testing**
   - Complete API documentation
   - Create user guides
   - Write integration guides
   - Ensure full test coverage

## Specific Guidelines

### Working with Budget Core

- Implement a clean domain model based on DDD principles
- Use clear, meaningful names for all classes and methods
- Implement proper validation for all operations
- Add comprehensive error handling
- Use value objects for immutable concepts
- Implement entity equality based on identity
- Follow the repository pattern for data access
- Add debug instrumentation to all key methods

### Working with Price Monitoring

- Implement a flexible adapter pattern for price sources
- Create a robust verification system
- Implement fallback mechanisms for source failures
- Add caching with appropriate TTL values
- Use a weighted trust model for different sources
- Add rate limiting for external API calls
- Implement comprehensive logging
- Store full history of price changes

### Working with Reporting

- Design for efficiency with large datasets
- Implement proper aggregation functions
- Create flexible filtering options
- Add sorting and pagination
- Support different output formats
- Optimize queries for performance
- Add caching for frequent report requests
- Include visualization-friendly data structures

### Working with Integration

- Create clean, intuitive API interfaces
- Implement comprehensive client libraries
- Add backward compatibility layers
- Create migration utilities for existing data
- Document integration patterns clearly
- Add examples for common use cases
- Implement proper error handling and reporting
- Add debug instrumentation for troubleshooting

## Key Files to Create

### Budget Core
- `/Budget/budget/core/engine.py`
- `/Budget/budget/core/allocation.py`
- `/Budget/budget/core/tracking.py`
- `/Budget/budget/core/policy.py`
- `/Budget/budget/data/models.py`
- `/Budget/budget/data/repository.py`
- `/Budget/budget/api/endpoints.py`

### Price Monitoring
- `/Budget/budget/service/price_monitor.py`
- `/Budget/budget/adapters/price_sources/litellm.py`
- `/Budget/budget/adapters/price_sources/llmprices.py`
- `/Budget/budget/adapters/price_sources/pretrained.py`

### Integration
- `/Budget/budget/adapters/apollo.py`
- `/Budget/budget/adapters/rhetor.py`
- `/Budget/client/budget_client.py`

### Reporting and UI
- `/Budget/budget/service/reporting.py`
- `/Budget/budget/service/alerts.py`
- `/Budget/ui/components/budget-dashboard.html`
- `/Budget/ui/scripts/budget-dashboard.js`

### Documentation
- `/Budget/README.md`
- `/MetaData/ComponentDocumentation/Budget/API_REFERENCE.md`
- `/MetaData/ComponentDocumentation/Budget/INTEGRATION_GUIDE.md`
- `/MetaData/ComponentDocumentation/Budget/USER_GUIDE.md`

## Reference Files

These existing files should be used as references for the implementation:

- `/Apollo/apollo/core/token_budget.py`
- `/Apollo/apollo/models/budget.py`
- `/Rhetor/rhetor/core/budget_manager.py`

## Getting Started

1. Verify you're on the correct branch:
   ```bash
   git branch
   # Should show something like sprint/Budget_Consolidation_MMYY
   ```

2. Create the basic Budget component structure:
   ```bash
   mkdir -p Budget/budget/{api,core,data,service,adapters,utils}
   mkdir -p Budget/budget/adapters/price_sources
   mkdir -p Budget/client
   mkdir -p Budget/ui/{components,scripts,styles}
   mkdir -p Budget/tests/{unit,integration,end_to_end}
   ```

3. Start implementing the core data models:
   ```bash
   touch Budget/budget/data/models.py
   ```

4. Begin implementing the budget engine:
   ```bash
   touch Budget/budget/core/engine.py
   ```

5. Proceed through the implementation plan phases in order

## Important Notes

1. **Follow Clean Architecture**: Ensure clear separation between layers
2. **Add Debug Instrumentation**: Add appropriate debug logging to all components
3. **Implement Error Handling**: Ensure robust error handling throughout
4. **Write Tests**: Create comprehensive tests for all functionality
5. **Document As You Go**: Add clear documentation to all code
6. **Follow Implementation Plan**: Proceed through phases in the specified order
7. **Use Reference Implementations**: Learn from Apollo and Rhetor's existing code
8. **Consider Performance**: Optimize for both speed and resource usage

## Documentation

Refer to these documents for detailed guidance:

- [Sprint Plan](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Budget_Consolidation_Sprint/SprintPlan.md)
- [Architectural Decisions](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Budget_Consolidation_Sprint/ArchitecturalDecisions.md)
- [Implementation Plan](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Budget_Consolidation_Sprint/ImplementationPlan.md)
- [Debug Instrumentation Guide](/MetaData/TektonDocumentation/DeveloperGuides/Debugging/DebuggingInstrumentation.md)

## Budget Component Overview

The Budget component is Tekton's centralized system for managing LLM token allocations and cost tracking. It provides these key capabilities:

1. **Budget Management**: Creation and management of budgets with limits and policies
2. **Allocation System**: Allocating tokens to contexts, components, and operations
3. **Usage Tracking**: Recording and analyzing token usage and costs
4. **Price Monitoring**: Automatically tracking provider pricing changes
5. **Reporting**: Generating reports on usage and costs
6. **Alerting**: Notifying users of budget events and issues

The component should be designed as a standalone service with a clean API that other components can use. It should combine the strengths of Apollo's sophisticated allocation system and Rhetor's practical cost tracking, while adding new capabilities for automated price updates.