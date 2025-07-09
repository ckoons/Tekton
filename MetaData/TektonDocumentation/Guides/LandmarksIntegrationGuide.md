# Landmarks Integration Guide

## Overview

Landmarks are a code annotation system in Tekton that helps AI assistants understand and navigate codebases more effectively. They serve as semantic markers that highlight important architectural decisions, integration points, and key functionality within the code.

## What are Landmarks?

Landmarks are decorators or comments that mark significant points in code, creating a knowledge graph that AI systems can use to:
- Understand architectural decisions and their rationale
- Navigate complex codebases efficiently
- Identify integration points between components
- Track state management and data flow
- Locate critical functionality quickly

## Types of Landmarks

### 1. Architecture Decision
Marks significant architectural choices and design patterns.

```python
@architecture_decision(
    title="Plugin System Architecture",
    description="Implements a dynamic plugin loader for extensibility",
    rationale="Allows third-party extensions without modifying core code"
)
class PluginManager:
    pass
```

### 2. Integration Point
Identifies where components connect or communicate.

```python
@integration_point(
    title="Hermes Message Handler",
    systems=["hermes", "engram"],
    description="Handles incoming messages from Hermes message bus"
)
def handle_hermes_message(message):
    pass
```

### 3. State Checkpoint
Marks important state management locations.

```python
@state_checkpoint(
    title="User Session State",
    state_type="persistent",
    description="Manages user session data across requests"
)
class SessionManager:
    pass
```

### 4. Performance Critical
Highlights performance-sensitive code sections.

```python
@performance_critical(
    title="Vector Search",
    metrics=["latency", "throughput"],
    description="Core vector similarity search - must complete in <100ms"
)
def search_vectors(query_vector):
    pass
```

### 5. Security Boundary
Marks security-critical code.

```python
@security_boundary(
    title="API Authentication",
    type="authentication",
    description="Validates API tokens and manages access control"
)
def authenticate_request(token):
    pass
```

## Implementation Patterns

### For Python Components

#### Using Decorators (Preferred)

```python
from shared.landmarks import (
    architecture_decision,
    integration_point,
    state_checkpoint,
    performance_critical,
    security_boundary
)

@architecture_decision(
    title="Event-Driven Architecture",
    description="Uses async event handling for scalability",
    rationale="Supports high-concurrency scenarios without blocking"
)
class EventHandler:
    
    @integration_point(
        title="Webhook Processor",
        systems=["external_api", "event_queue"],
        description="Processes incoming webhooks and queues events"
    )
    async def process_webhook(self, payload):
        # Implementation
        pass
```

#### Using Comments (Fallback)

When decorators aren't available or cause issues:

```python
# Landmark: Event-Driven Architecture - Uses async event handling for scalability
class EventHandler:
    
    # Landmark: Webhook Processor - Processes incoming webhooks and queues events
    async def process_webhook(self, payload):
        pass
```

### For JavaScript/TypeScript Components

Use JSDoc-style comments:

```javascript
/**
 * @landmark architecture_decision
 * @title React Component Architecture
 * @description Uses functional components with hooks
 * @rationale Simpler state management and better performance
 */
const AppComponent = () => {
    
    /**
     * @landmark integration_point
     * @title API Data Fetcher
     * @systems ["backend_api", "cache_layer"]
     * @description Fetches and caches API data
     */
    const fetchData = async () => {
        // Implementation
    };
};
```

## Adding Landmarks to Existing Components

### Step 1: Identify Key Areas

Look for:
- Main entry points and initialization code
- Component boundaries and interfaces
- State management locations
- API endpoints and handlers
- Critical algorithms or business logic
- Security checks and validations

### Step 2: Choose Appropriate Landmark Types

Match the code's purpose to landmark types:
- Architectural patterns → `@architecture_decision`
- Component connections → `@integration_point`
- State management → `@state_checkpoint`
- Performance hotspots → `@performance_critical`
- Security code → `@security_boundary`

### Step 3: Add Descriptive Information

Include:
- **Title**: Brief, descriptive name
- **Description**: What this code does
- **Rationale**: Why it's implemented this way (for architecture decisions)
- **Systems**: Connected components (for integration points)
- **Metrics**: What to measure (for performance critical)

### Step 4: Maintain Consistency

- Use consistent naming conventions
- Keep descriptions concise but informative
- Update landmarks when code changes significantly
- Remove landmarks when code is deleted

## Best Practices

### DO:
- ✅ Use natural, descriptive names
- ✅ Focus on "why" not just "what"
- ✅ Mark genuine architectural decisions
- ✅ Keep landmark density reasonable (not every function needs one)
- ✅ Update landmarks when refactoring

### DON'T:
- ❌ Over-annotate trivial code
- ❌ Use generic descriptions
- ❌ Leave outdated landmarks in place
- ❌ Mark temporary or experimental code
- ❌ Use landmarks as TODO comments

## Examples by Component Type

### API Endpoint

```python
@integration_point(
    title="User Registration Endpoint",
    systems=["database", "email_service", "auth_service"],
    description="Handles new user registration with email verification"
)
@security_boundary(
    title="Registration Input Validation",
    type="input_validation",
    description="Validates and sanitizes user registration data"
)
async def register_user(request):
    # Implementation
```

### Database Model

```python
@architecture_decision(
    title="Soft Delete Pattern",
    description="Uses deleted_at timestamp instead of hard deletes",
    rationale="Maintains data history and supports recovery"
)
@state_checkpoint(
    title="User Account State",
    state_type="persistent",
    description="Core user account data and status"
)
class User(Base):
    __tablename__ = "users"
    # Model definition
```

### Service Class

```python
@architecture_decision(
    title="Repository Pattern Implementation",
    description="Abstracts database operations behind repository interface",
    rationale="Allows swapping data stores without changing business logic"
)
class UserRepository:
    
    @performance_critical(
        title="Bulk User Query",
        metrics=["query_time", "memory_usage"],
        description="Retrieves large user sets - optimized with pagination"
    )
    def find_users(self, filters, limit=100):
        # Implementation
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure `shared.landmarks` is in your Python path
   - Fall back to comment-based landmarks if needed

2. **Parameter Conflicts**
   - Check decorator parameter names match implementation
   - Use `title` not `name` for most landmarks
   - `state_checkpoint` requires `state_type` parameter

3. **Performance Impact**
   - Landmarks have negligible runtime overhead
   - They're primarily metadata for development

### Validation

Run landmark validation:
```bash
python scripts/validate_landmarks.py [component_path]
```

This checks for:
- Correct decorator syntax
- Required parameters
- Consistent naming
- Orphaned landmarks

## Integration with AI Systems

Landmarks are automatically:
- Indexed by Athena for knowledge graph construction
- Used by AI specialists for code navigation
- Included in AI context for better understanding
- Searchable through specialized queries

AI assistants can:
- Find code by landmark type or title
- Understand component relationships
- Navigate to specific functionality
- Comprehend architectural decisions

## Future Enhancements

Planned improvements:
- Visual landmark browser in Hephaestus UI
- Automatic landmark suggestions
- Cross-component landmark linking
- Landmark-based code generation
- Integration with IDE extensions

## Related Documentation

- [Landmarks README](/shared/landmarks/README.md)
- [Athena Integration Guide](/MetaData/ComponentDocumentation/Athena/INTEGRATION_GUIDE.md)
- [AI Specialists Guide](/MetaData/TektonDocumentation/Guides/AISpecialistsGuide.md)