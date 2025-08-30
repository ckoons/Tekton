# Landmarks and Semantic Tags: Standard of Practice

## Executive Summary

Landmarks and Semantic Tags are our two complementary systems for mapping the Tekton codebase and UI, creating a navigable knowledge graph that both humans and Companion Intelligences (CIs) can understand. Like street signs and building markers in a city, these systems ensure everyone knows where they are, why things exist, and how to find what they need. This document is our standard of practice - follow it at the end of every sprint to maintain consistency and clarity across the entire Tekton platform.

## Quick Decision Guide

**What are you marking?**
- **UI/HTML Element** → Use Semantic Tags (`data-tekton-*`)
- **Code/Architecture** → Use Landmarks (`@architecture_decision`, etc.)
- **Both feed our knowledge graph** → Athena indexes them for semantic search

## Landmarks (Code Layer)

### The Core Landmark Types

#### 1. @architecture_decision
**Purpose**: Document WHY architectural choices were made
```python
@architecture_decision(
    title="MCP Server Architecture",
    description="Single source of truth for CI routing through standard protocol",
    rationale="Consolidates all CI message routing, eliminating duplicate HTTP endpoints",
    alternatives_considered=["Direct HTTP endpoints", "WebSocket-only", "gRPC"],
    impacts=["ui_integration", "distributed_tekton", "ai_communication"],
    decided_by="Casey",
    decision_date="2025-01-18"
)
class MCPServer:
    pass
```

#### 2. @api_contract
**Purpose**: Document API endpoints and their contracts
```python
@api_contract(
    title="Team Chat Broadcast",
    description="Broadcasts messages to all CI specialists",
    endpoint="/api/mcp/v2/tools/team-chat",
    method="POST",
    request_schema={"message": "string"},
    response_schema={"responses": [{"specialist_id": "string", "content": "string"}]},
    performance_requirements="<2s for all CI responses"
)
async def team_chat(request: Request):
    pass
```

#### 3. @performance_boundary
**Purpose**: Mark performance-critical sections with SLAs
```python
@performance_boundary(
    title="Cache Invalidation Check",
    description="Validates cache entries against file modification times",
    sla="<1ms validation time",
    optimization_notes="mtime comparison avoids expensive re-introspection",
    measured_impact="Enables <5ms cached responses while ensuring freshness"
)
def _is_cache_valid(self, key: str):
    pass
```

#### 4. @integration_point
**Purpose**: Mark where components connect
```python
@integration_point(
    title="CI Shell Message Integration",
    description="Routes messages through AIShell to appropriate CI specialist",
    target_component="AIShell",
    protocol="internal_api",
    data_flow="MCP request → AIShell.send_to_ai → CI specialist → response",
    integration_date="2025-01-18"
)
async def send_message(request: Request):
    pass
```

#### 5. @danger_zone
**Purpose**: Mark complex or risky code sections
```python
@danger_zone(
    title="Concurrent State Modification",
    description="Multiple threads may access shared registry",
    risk_level="high",
    risks=["race conditions", "data corruption"],
    mitigation="Thread-safe queue and locks",
    review_required=True
)
def update_registry(self):
    pass
```

#### 6. @state_checkpoint
**Purpose**: Mark important state management points
```python
@state_checkpoint(
    title="Introspection Cache",
    description="Two-tier cache (memory + disk) for introspection results",
    state_type="cache",
    persistence=True,
    consistency_requirements="File modification time aware",
    recovery_strategy="Reload from disk on restart"
)
class IntrospectionCache:
    pass
```

### Advanced Landmark Patterns (New)

#### Apollo Memory Landmarks (Added 2025-08-29)

##### @memory_landmark
**Purpose**: Mark significant memories as navigable landmarks
```python
@memory_landmark(
    title="Redux State Decision",
    type="decision",
    description="Chose Redux for predictable state management",
    summary="Redux over MobX for state",
    ci_source="ergon-ci",
    tags=["redux", "architecture", "state"],
    priority=8,
    impacts=["frontend", "performance", "debugging"],
    namespace="apollo"
)
def store_redux_decision():
    pass
```

##### @decision_landmark
**Purpose**: Mark important decisions that affect project direction
```python
@decision_landmark(
    title="Migration to TypeScript",
    summary="Migrating codebase to TypeScript",
    rationale="Type safety and better IDE support",
    decided_by="team_consensus",
    impacts=["all_components", "build_process"],
    alternatives_considered=["Flow", "JSDoc", "PropTypes"],
    namespace="apollo"
)
```

##### @insight_landmark
**Purpose**: Mark discovered insights and learnings
```python
@insight_landmark(
    title="Render Performance Bottleneck",
    summary="Unnecessary re-renders causing delays",
    discovery="Profiling showed 200ms delays",
    resolution="Applied React.memo and useMemo",
    impact="10x performance improvement",
    namespace="apollo"
)
```

##### @error_landmark
**Purpose**: Mark significant errors and their resolutions
```python
@error_landmark(
    title="Import Order Bug",
    summary="Shared imports before path setup",
    symptoms=["ModuleNotFoundError", "CI launch failures"],
    root_cause="sys.path not configured before imports",
    resolution="Reordered imports in launcher",
    prevented_by="Import order validation",
    namespace="apollo"
)
```

### Advanced Landmark Patterns (New)

#### 7. @ci_orchestrated
**Purpose**: Mark components designed for CI orchestration
```python
@ci_orchestrated(
    title="Construct Solution Builder",
    description="Interactive solution composition guided by CI",
    orchestrator="ergon-ai",
    workflow=["discover", "analyze", "build", "test", "publish"],
    ci_capabilities=["component_selection", "code_generation", "validation"]
)
class ConstructSystem:
    pass
```

#### 8. @message_buffer
**Purpose**: Document message buffering for async communication
```python
@message_buffer(
    title="Single-Prompt Model Buffer",
    description="Buffers messages for Claude/GPT models that process single prompts",
    buffer_type="file_based",
    location="/tmp/ci_buffers",
    clearing_policy="on_read",
    max_size="1MB"
)
def buffer_message(ci_name: str, message: str):
    pass
```

#### 9. @fuzzy_match
**Purpose**: Mark intelligent name resolution logic
```python
@fuzzy_match(
    title="CI Name Resolution",
    description="Matches CI names with fuzzy logic for flexible routing",
    algorithm="prefix_match_with_suffix_handling",
    examples=["ergon->ergon", "ergon-ci->ergon", "ergon->ergon-ci"],
    priority="exact > prefix > suffix_variant"
)
def get_forward_state(self, ci_name: str):
    pass
```

#### 10. @ci_collaboration
**Purpose**: Document multi-CI coordination points
```python
@ci_collaboration(
    title="Greek Chorus Coordination",
    description="Multiple specialist CIs working together on complex tasks",
    participants=["athena-ai", "rhetor-ai", "hermes-ai"],
    coordination_method="message_passing",
    synchronization="async_buffered"
)
async def coordinate_specialists(task: dict):
    pass
```

### Landmark Implementation Pattern

Always include fallback for environments without landmarks:
```python
# Import landmarks with fallback
try:
    from landmarks import (
        architecture_decision,
        api_contract,
        integration_point,
        performance_boundary,
        ci_orchestrated,
        message_buffer,
        fuzzy_match,
        ci_collaboration
    )
except ImportError:
    # Define no-op decorators when landmarks not available
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    # ... repeat for other decorators
```

## Semantic Tags (UI Layer)

### The Core Tag Categories

#### 1. Structure Tags
**Purpose**: Define UI hierarchy and organization
```html
<div class="component-container"
     data-tekton-area="rhetor"
     data-tekton-component="rhetor-main"
     data-tekton-type="workspace"
     data-tekton-zone="content">
```

#### 2. Navigation Tags
**Purpose**: Enable UI element discovery and routing
```html
<button data-tekton-nav-item="aish"
        data-tekton-nav-target="aish-terminal"
        data-tekton-nav-action="switch-component">
    CI Shell
</button>
```

#### 3. Interactive Elements
**Purpose**: Mark actionable UI elements
```html
<button data-tekton-action="send-message"
        data-tekton-trigger="click"
        data-tekton-target="team-chat">
    Send to All
</button>
```

#### 4. CI Integration Tags
**Purpose**: Connect UI elements to CI capabilities
```html
<div data-tekton-chat="numa-assistant"
     data-tekton-ai="numa"
     data-tekton-ai-ready="true">
    <div data-tekton-chat-messages="true"></div>
    <input data-tekton-chat-input="true">
</div>
```

#### 5. State Management Tags
**Purpose**: Track runtime state and visibility
```html
<div data-tekton-state="active"
     data-tekton-status="connected"
     data-tekton-visibility="visible">
```

### Advanced Semantic Tags (New)

#### 6. Solution Building Tags
**Purpose**: Mark UI elements involved in solution composition
```html
<div data-tekton-construct="solution-builder"
     data-tekton-construct-phase="discovery"
     data-tekton-construct-ci="ergon-ai">
    <div data-tekton-construct-questions="true"></div>
    <div data-tekton-construct-workspace="active"></div>
</div>
```

#### 7. CI Coordination Tags
**Purpose**: Show multi-CI collaboration in UI
```html
<div data-tekton-ci-ensemble="greek-chorus"
     data-tekton-ci-participants="athena,rhetor,hermes"
     data-tekton-ci-coordination="active">
    <div data-tekton-ci-messages="buffered"></div>
</div>
```

#### 8. Registry Integration Tags
**Purpose**: Connect UI to component registry
```html
<div data-tekton-registry="component-browser"
     data-tekton-registry-action="search"
     data-tekton-registry-filter="data-processing">
    <div data-tekton-registry-results="true"></div>
</div>
```

### Semantic Tag Conventions

1. **Always prefix with `data-tekton-`**
2. **Use descriptive, specific values**
3. **Layer tags for rich context**
4. **Update state tags dynamically**
5. **Think about CI navigation paths**
6. **Consider CI collaboration patterns**

## End of Sprint Checklist

Before completing any sprint, verify:

### Code Landmarks
- [ ] Added `@architecture_decision` for major design choices?
- [ ] Marked all API endpoints with `@api_contract`?
- [ ] Tagged performance-critical code with `@performance_boundary`?
- [ ] Identified component connections with `@integration_point`?
- [ ] Flagged risky code sections with `@danger_zone`?
- [ ] Marked state management with `@state_checkpoint`?
- [ ] Tagged CI-driven components with `@ci_orchestrated`?
- [ ] Documented message buffering with `@message_buffer`?
- [ ] Marked fuzzy matching logic with `@fuzzy_match`?
- [ ] Identified CI collaboration points with `@ci_collaboration`?

### UI Semantic Tags
- [ ] Tagged all new components with structure tags?
- [ ] Added navigation tags for new UI elements?
- [ ] Marked interactive elements appropriately?
- [ ] Connected CI features with integration tags?
- [ ] Implemented dynamic state management tags?
- [ ] Added solution building tags for Construct UI?
- [ ] Marked CI coordination displays?
- [ ] Connected Registry browsing elements?

### Quality Check
- [ ] Can a CI navigate your code using landmarks?
- [ ] Can a CI understand your UI using semantic tags?
- [ ] Do your landmarks explain WHY, not just WHAT?
- [ ] Are your semantic tags specific and descriptive?
- [ ] Have you documented CI collaboration patterns?

## New Pattern Examples

### Ergon Construct Sprint
```python
# CI orchestration for solution building
@ci_orchestrated(
    title="Construct Solution Composer",
    description="CI-guided interactive solution building",
    orchestrator="ergon-ai",
    workflow=["requirements", "components", "configuration", "deployment"],
    ci_capabilities=["analysis", "suggestion", "validation", "generation"]
)
class ConstructGuidedDialog:
    """Interactive dialog for solution composition"""
    
    @message_buffer(
        title="CI Message Queue",
        description="Buffers messages from collaborating CIs",
        buffer_type="memory",
        clearing_policy="on_build"
    )
    def queue_ci_message(self, sender: str, message: str):
        pass
    
    @ci_collaboration(
        title="Component Discovery",
        participants=["athena-ai", "ergon-ai"],
        coordination_method="query_response"
    )
    async def discover_components(self, requirements: dict):
        pass
```

### CI Message Buffering Implementation
```python
# Message buffering for single-prompt models
@message_buffer(
    title="Claude Message Buffer",
    description="File-based buffer for Claude/GPT forwarded CIs",
    buffer_type="file",
    location="/tmp/ci_buffers",
    format="{ci_name}.buffer"
)
def buffer_for_claude(ci_name: str, message: str):
    """Buffer message for next Claude prompt"""
    buffer_file = BUFFER_DIR / f"{ci_name}.buffer"
    with open(buffer_file, 'a') as f:
        f.write(f"{message}\n")
```

### Fuzzy Name Resolution
```python
# Intelligent CI name matching
@fuzzy_match(
    title="CI Name Resolution",
    description="Flexible matching for CI routing",
    algorithm="prefix_with_suffix_awareness",
    examples={
        "ergon": "matches ergon or ergon-ci based on availability",
        "ergon-ci": "matches ergon if ergon-ci not found",
        "ergon-ai": "exact match only"
    }
)
def resolve_ci_name(search_name: str, available_names: list) -> str:
    """Find best matching CI name"""
    # Exact match first
    if search_name in available_names:
        return search_name
    # Fuzzy matching logic...
```

### Greek Chorus Coordination
```python
# Multi-CI collaboration
@ci_collaboration(
    title="Greek Chorus Analysis",
    description="Specialist CIs analyze problem from multiple angles",
    participants=["athena-ai", "rhetor-ai", "apollo-ai", "hermes-ai"],
    coordination_method="parallel_analysis",
    aggregation="ergon-ai"
)
async def analyze_codebase(query: str) -> dict:
    """Coordinate specialists for comprehensive analysis"""
    responses = await gather_specialist_insights(query)
    return synthesize_responses(responses)
```

### Construct UI Semantic Tags
```html
<!-- Solution builder with full CI integration -->
<div class="construct-container"
     data-tekton-component="construct"
     data-tekton-construct="solution-builder"
     data-tekton-construct-mode="guided"
     data-tekton-ci="ergon-ai"
     data-tekton-ci-state="engaged">
    
    <!-- Question flow -->
    <div data-tekton-construct-questions="true"
         data-tekton-construct-phase="requirements"
         data-tekton-question-current="purpose">
        <div data-tekton-question-id="purpose"></div>
    </div>
    
    <!-- CI collaboration display -->
    <div data-tekton-ci-ensemble="active"
         data-tekton-ci-messages="3"
         data-tekton-ci-buffer="populated">
        <div data-tekton-ci-participant="athena-ai"></div>
        <div data-tekton-ci-participant="rhetor-ai"></div>
    </div>
    
    <!-- Build actions -->
    <button data-tekton-action="build"
            data-tekton-construct-action="compose"
            data-tekton-ci-trigger="true">
        Build Solution
    </button>
</div>
```

## CI-First Architecture Principles

### Design for CI Orchestration
When building new features, consider:
1. **Can a CI drive this process?** Design for CI orchestration
2. **How do CIs collaborate?** Plan message passing and coordination
3. **What context does the CI need?** Provide rich landmarks
4. **How does the UI show CI activity?** Use semantic tags

### Message Flow Patterns
```python
# Document async message flows
@integration_point(
    title="CI Message Router",
    description="Routes messages between CIs based on forwarding rules",
    data_flow="sender_ci → router → buffer/direct → recipient_ci",
    buffering="single_prompt_models",
    direct="streaming_models"
)
```

### Solution Composition Pattern
The Construct system exemplifies CI-first design:
- CI guides the user through questions
- CI analyzes responses and suggests components
- CI generates configuration and glue code
- CI coordinates testing and deployment

## Common Patterns

### Python Module with Landmarks
```python
#!/usr/bin/env python3
"""Module description"""

# Imports
import os
import sys

# Landmark imports with fallback
try:
    from landmarks import (
        architecture_decision, 
        api_contract,
        ci_orchestrated,
        message_buffer
    )
except ImportError:
    def architecture_decision(**kwargs):
        def decorator(func): return func
        return decorator
    def api_contract(**kwargs):
        def decorator(func): return func
        return decorator
    def ci_orchestrated(**kwargs):
        def decorator(func): return func
        return decorator
    def message_buffer(**kwargs):
        def decorator(func): return func
        return decorator

# Your code with landmarks
@architecture_decision(
    title="Your Decision",
    rationale="Why this approach"
)
class YourClass:
    pass
```

### HTML Component with Semantic Tags
```html
<div class="component-root"
     data-tekton-component="component-name"
     data-tekton-type="component-type"
     data-tekton-area="functional-area"
     data-tekton-ci="associated-ci">
    
    <!-- Navigation -->
    <nav data-tekton-nav="component-nav">
        <button data-tekton-nav-item="item1"
                data-tekton-nav-target="target1">
            Item 1
        </button>
    </nav>
    
    <!-- Content -->
    <div data-tekton-zone="content"
         data-tekton-state="active"
         data-tekton-ci-ready="true">
        <!-- Component content -->
    </div>
    
    <!-- CI Integration -->
    <div data-tekton-ci-interface="true"
         data-tekton-ci-model="claude"
         data-tekton-ci-buffer="enabled">
        <!-- CI interaction area -->
    </div>
</div>
```

## Why This Matters

1. **Knowledge Graph**: Every landmark and tag feeds Athena's semantic understanding
2. **CI Navigation**: CIs can find and understand code without guessing
3. **Human Understanding**: New developers/CIs immediately grasp system structure
4. **Consistency**: Following these standards ensures predictable, maintainable code
5. **Context Preservation**: Saves ~40% context by eliminating exploration/errors
6. **CI Collaboration**: Enables multi-CI coordination and ensemble intelligence

## Summary

This document is our standard of practice. At the end of every sprint, use the checklist to ensure you've properly marked your code with landmarks and your UI with semantic tags. These aren't optional decorations - they're essential infrastructure that makes Tekton navigable and understandable for everyone who works with it.

Remember Casey's wisdom: "Map First, Build Second" - but also "Update the Map When You Build!"

The new CI-first patterns reflect our evolution toward Companion Intelligence:
- Design for CI orchestration from the start
- Document message flows and buffering strategies
- Mark collaboration points clearly
- Think about how CIs will work together

---

*Last Updated: 2025-08-24*
*Standard Version: 2.0*
*Changes: Added CI-first patterns, message buffering, fuzzy matching, and collaboration landmarks*