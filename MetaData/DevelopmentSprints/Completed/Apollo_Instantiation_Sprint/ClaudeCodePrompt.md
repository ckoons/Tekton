# Apollo Instantiation Sprint - Claude Code Prompt

## Context

You are implementing the Apollo component for the Tekton project. Apollo is the executive coordinator and predictive planning system responsible for managing operational health, token flow, and behavioral reliability of all LLM components in Tekton.

The Apollo component needs to be created from scratch, following the Single Port Architecture pattern and integrating with existing Tekton components, particularly Rhetor (for LLM communication), Engram (for memory management), and Synthesis (for execution coordination).

This sprint focuses on implementing the backend components of Apollo, establishing its core functionality, API interfaces, CLI tools, and integration points. The UI components will be addressed in a future sprint.

## Project Structure and Standards

The Apollo component should follow the established Tekton component structure:

1. **Directory Structure:**
   - `apollo/` - Main Python package
   - `apollo/core/` - Core modules (context monitoring, token budgeting, etc.)
   - `apollo/api/` - FastAPI implementation with Single Port Architecture
   - `apollo/cli/` - Command-line interface tools
   - `apollo/models/` - Data models and schemas
   - `apollo/utils/` - Utility functions and helpers
   - `apollo/integrations/` - Integration with other Tekton components
   - `tests/` - Unit and integration tests

2. **Code Standards:**
   - Follow PEP 8 guidelines
   - Use type hints for all function signatures
   - Include docstrings for all functions and classes
   - Use f-strings for string formatting
   - Follow Tekton error handling patterns
   - Implement proper logging with appropriate levels

3. **API Standards:**
   - Follow Single Port Architecture pattern
   - Implement REST API with FastAPI
   - Provide WebSocket interface for real-time monitoring
   - Include MCP-compatible endpoints for component discovery
   - Document all endpoints thoroughly

## Key Requirements

1. **Context Monitoring:**
   - Collect context usage metrics from Rhetor
   - Track token consumption rates and patterns
   - Monitor for signs of hallucination or degradation
   - Maintain historical data for trend analysis

2. **Token Budgeting:**
   - Allocate token budgets for different LLM operations
   - Adjust budgets based on task complexity and priority
   - Enforce budget constraints to prevent exhaustion
   - Support different budget strategies per model tier

3. **Predictive Planning:**
   - Apply rules to predict potential issues
   - Forecast token exhaustion and context degradation
   - Identify optimal intervention points
   - Generate action recommendations

4. **Protocol Enforcement:**
   - Define standardized protocols for component interactions
   - Enforce protocol compliance across components
   - Manage protocol versions and transitions
   - Coordinate protocol implementation

5. **Bidirectional Messaging:**
   - Create a flexible messaging interface for components
   - Process incoming requests from any component
   - Generate and send directive messages to components
   - Ensure components can examine and respond to directives
   - Route messages to appropriate Apollo modules
   - Provide consistent response handling

6. **CLI Tools:**
   - Provide commands for system status monitoring
   - Implement control commands for configuration
   - Create visualization tools for forecasting
   - Support debugging and diagnostics

7. **Component Integration:**
   - Interface with Rhetor for LLM communication
   - Coordinate with Engram for memory operations
   - Integrate with Harmonia for workflow orchestration
   - Connect with Synthesis for task execution
   - Enable any component to interface with Apollo as needed
   - Connect with other components via Hermes/MCP

## Implementation Approach

Your implementation should follow these principles:

1. **Modular Structure:**
   - Implement a modular observer-controller architecture
   - Create loosely coupled modules with clear responsibilities
   - Define clean interfaces between modules
   - Enable independent testing and extension

2. **Progressive Implementation:**
   - Start with core functionality before adding complexity
   - Implement monitoring foundations first
   - Add predictive capabilities incrementally
   - Build integration points after core is solid

3. **Testing Focus:**
   - Write comprehensive unit tests for all modules
   - Create integration tests for component interactions
   - Implement system tests for end-to-end workflows
   - Use test-driven development where appropriate

4. **Documentation:**
   - Document all public interfaces thoroughly
   - Create clear usage examples
   - Provide integration guidelines
   - Follow Tekton documentation standards

## Sprint Workflow

1. Meticulously follow the Implementation Plan to develop each module
2. Implement comprehensive testing alongside code development
3. Document all functionality as it's implemented
4. Commit code at stable points with descriptive commit messages
5. Regularly check the Implementation Plan to ensure all requirements are met
6. Ask questions if any aspects of the design or implementation are unclear

## Specific Guidelines

1. **Before making changes:**
   - Thoroughly review the Apollo specification and sprint documentation
   - Understand the existing component patterns from Athena, Engram, etc.
   - Identify clear module boundaries

2. **When implementing:**
   - Follow the modular observer-controller architecture
   - Create a clear data flow between modules
   - Implement strict error handling and logging
   - Avoid tight coupling between components

3. **For API endpoints:**
   - Follow the Single Port Architecture pattern
   - Implement standardized error responses
   - Include proper validation for all inputs
   - Document all endpoints with examples

4. **For CLI tools:**
   - Create a consistent command structure
   - Implement helpful error messages
   - Provide clear usage examples
   - Support both basic and advanced use cases

5. **For component integration:**
   - Use protocol-based integration
   - Implement clean separation of concerns
   - Handle error cases gracefully
   - Provide fallback behavior where appropriate

## Key Interfaces and Components

1. **Context Observer Module:**
   - Interface with Rhetor for context metrics
   - Track token usage and content patterns
   - Identify potential issues in context
   - Maintain historical metrics

2. **Token Budget Manager:**
   - Allocate and track token budgets
   - Enforce budget constraints
   - Adjust budgets dynamically
   - Support different model tiers

3. **Predictive Engine:**
   - Apply rule-based prediction
   - Generate forecasts for potential issues
   - Evaluate intervention options
   - Recommend optimal actions

4. **Action Planner:**
   - Map conditions to appropriate actions
   - Construct action sequences
   - Coordinate with other components
   - Handle action prioritization

5. **Protocol Enforcer:**
   - Define component interaction protocols
   - Validate protocol compliance
   - Manage protocol versions
   - Coordinate protocol transitions

6. **Message Handler:**
   - Process on-demand requests from components
   - Generate and send directive messages to components
   - Route messages to appropriate modules
   - Format and return responses
   - Track message delivery and acknowledgments
   - Maintain messaging context and state

7. **API Layer:**
   - Implement REST endpoints
   - Create WebSocket interface
   - Support MCP integration
   - Handle authentication and authorization
   - Provide component-to-Apollo messaging endpoints

8. **CLI Framework:**
   - Parse and validate commands
   - Implement status and control commands
   - Create visualization tools
   - Provide comprehensive help
   - Support component message simulation for testing

## Resources and References

- [Apollo Specification](/MetaData/DevelopmentSprints/Clean_Slate_Sprint/apollo_specification.md)
- [Sprint Plan](/MetaData/DevelopmentSprints/Apollo_Instantiation_Sprint/SprintPlan.md)
- [Architectural Decisions](/MetaData/DevelopmentSprints/Apollo_Instantiation_Sprint/ArchitecturalDecisions.md)
- [Implementation Plan](/MetaData/DevelopmentSprints/Apollo_Instantiation_Sprint/ImplementationPlan.md)
- Existing Components (Athena, Engram, Prometheus) as reference implementations
- [Single Port Architecture Documentation](/MetaData/TektonDocumentation/Architecture/SinglePortArchitecture.md)

## Expected Deliverables

1. Complete Apollo backend implementation
2. API and CLI interfaces
3. Integration with Rhetor, Engram, and Synthesis
4. Comprehensive tests
5. Thorough documentation
6. Demonstration of core functionality

Please proceed methodically, following the Implementation Plan and asking for clarification when needed. Remember to maintain clean, well-documented, and thoroughly tested code throughout the implementation.

## Final Guidance

This Apollo component is a critical part of Tekton's architecture, serving as the executive function for the entire system. Take care to build it with reliability, maintainability, and extensibility in mind. Follow the established patterns from other Tekton components while introducing the unique architecture needed for Apollo's specific responsibilities.

When in doubt, refer to the Architectural Decisions document for guidance on the key design choices and their rationales. Follow the Implementation Plan for the detailed tasks and their sequencing. Quality and reliability should be prioritized over rapid implementation.