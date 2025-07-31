# Landmarks and Semantic Tags: Standard of Practice

## Executive Summary

Landmarks and Semantic Tags are our two complementary systems for mapping the Tekton codebase and UI, creating a navigable knowledge graph that both humans and Companion Intelligences (CIs) can understand. Like street signs and building markers in a city, these systems ensure everyone knows where they are, why things exist, and how to find what they need. This document is our standard of practice - follow it at the end of every sprint to maintain consistency and clarity across the entire Tekton platform.

## Quick Decision Guide

**What are you marking?**
- **UI/HTML Element** → Use Semantic Tags (`data-tekton-*`)
- **Code/Architecture** → Use Landmarks (`@architecture_decision`, etc.)
- **Both feed our knowledge graph** → Athena indexes them for semantic search

## Landmarks (Code Layer)

### The 6 Landmark Types

#### 1. @architecture_decision
**Purpose**: Document WHY architectural choices were made
```python
@architecture_decision(
    title="MCP Server Architecture",
    description="Single source of truth for AI routing through standard protocol",
    rationale="Consolidates all AI message routing, eliminating duplicate HTTP endpoints",
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
    description="Broadcasts messages to all AI specialists",
    endpoint="/api/mcp/v2/tools/team-chat",
    method="POST",
    request_schema={"message": "string"},
    response_schema={"responses": [{"specialist_id": "string", "content": "string"}]},
    performance_requirements="<2s for all AI responses"
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
    title="AI Shell Message Integration",
    description="Routes messages through AIShell to appropriate AI specialist",
    target_component="AIShell",
    protocol="internal_api",
    data_flow="MCP request → AIShell.send_to_ai → AI specialist → response",
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

### Landmark Implementation Pattern

Always include fallback for environments without landmarks:
```python
# Import landmarks with fallback
try:
    from landmarks import (
        architecture_decision,
        api_contract,
        integration_point,
        performance_boundary
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

### The 5 Tag Categories

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
    AI Shell
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

#### 4. AI Integration Tags
**Purpose**: Connect UI elements to AI capabilities
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

### Semantic Tag Conventions

1. **Always prefix with `data-tekton-`**
2. **Use descriptive, specific values**
3. **Layer tags for rich context**
4. **Update state tags dynamically**
5. **Think about AI navigation paths**

## End of Sprint Checklist

Before completing any sprint, verify:

### Code Landmarks
- [ ] Added `@architecture_decision` for major design choices?
- [ ] Marked all API endpoints with `@api_contract`?
- [ ] Tagged performance-critical code with `@performance_boundary`?
- [ ] Identified component connections with `@integration_point`?
- [ ] Flagged risky code sections with `@danger_zone`?
- [ ] Marked state management with `@state_checkpoint`?

### UI Semantic Tags
- [ ] Tagged all new components with structure tags?
- [ ] Added navigation tags for new UI elements?
- [ ] Marked interactive elements appropriately?
- [ ] Connected AI features with integration tags?
- [ ] Implemented dynamic state management tags?

### Quality Check
- [ ] Can a CI navigate your code using landmarks?
- [ ] Can a CI understand your UI using semantic tags?
- [ ] Do your landmarks explain WHY, not just WHAT?
- [ ] Are your semantic tags specific and descriptive?

## Real Sprint Examples

### MCP Distributed Tekton Sprint
```python
# Architecture decision at module level
@architecture_decision(
    title="MCP Server Architecture",
    rationale="Consolidates all AI message routing through standard protocol"
)
class _MCPServerArchitecture:
    pass

# API contract for team chat
@api_contract(
    title="Team Chat Broadcast",
    endpoint="/api/mcp/v2/tools/team-chat"
)
async def team_chat(request: Request):
    pass
```

### TektonCore Automated Merge Sprint
```python
# Architecture decision for merge strategy
@architecture_decision(
    title="Dry-Run Merge Strategy",
    description="Use git merge --no-commit to detect conflicts without corruption",
    rationale="Allows safe conflict detection while keeping repository clean",
    alternatives_considered=["Temporary branches", "Merge simulation"],
    decided_by="Casey",
    decision_date="2025-01-31"
)
async def dry_run_merge(self, branch_name: str):
    pass

# Danger zone for concurrent operations
@danger_zone(
    title="Concurrent Merge Operations",
    description="Multiple merge operations can corrupt repository state",
    risk_level="high",
    risks=["repository corruption", "lost commits", "branch conflicts"],
    mitigation="Queue-based processing, atomic operations, merge locks"
)
async def merge_branch(self, branch_name: str):
    pass

# API contract for merge endpoints
@api_contract(
    title="Dry-Run Merge API",
    endpoint="/sprints/merge/dry-run",
    method="POST",
    request_schema={"merge_id": "str", "merge_name": "str"},
    response_schema={"can_merge": "bool", "conflicts": "List[Dict]"}
)
async def dry_run_merge(request: DryRunMergeRequest):
    pass
```

### Claude Code IDE Sprint
```python
# Performance boundary for caching
@performance_boundary(
    title="Cache Invalidation Check",
    sla="<1ms validation time",
    measured_impact="Saves ~40% context by preventing error spirals"
)
def _is_cache_valid(self):
    pass

# Architecture decision for eliminating guesswork
@architecture_decision(
    title="Claude Code IDE Introspection Engine",
    rationale="CIs waste ~40% context on AttributeErrors from guessing"
)
class TektonInspector:
    pass
```

### UI Component Example
```html
<!-- Properly tagged chat interface -->
<div class="chat-container"
     data-tekton-component="team-chat"
     data-tekton-type="chat-interface"
     data-tekton-ai="multi-specialist"
     data-tekton-state="ready">
    
    <div data-tekton-chat-messages="true"
         data-tekton-zone="message-area">
    </div>
    
    <input data-tekton-chat-input="true"
           data-tekton-action="compose-message">
    
    <button data-tekton-action="send"
            data-tekton-trigger="team-broadcast">
        Send to Team
    </button>
</div>
```

### Penia/Budget Component Sprint
```python
# Architecture decision for budget tracking
@architecture_decision(
    title="Real-time Budget Tracking Architecture",
    description="Live budget monitoring with WebSocket updates",
    rationale="Provides immediate cost visibility to prevent overruns",
    alternatives_considered=["Polling-based updates", "Batch processing"],
    impacts=["cost_management", "user_experience", "system_performance"],
    decided_by="Casey",
    decision_date="2025-07-31"
)
class BudgetEngine:
    pass

# API contract for budget API
@api_contract(
    title="Budget Summary API",
    endpoint="/api/v1/budgets/{budget_id}/summary",
    method="GET",
    request_schema={"period": "str"},
    response_schema={"daily": "dict", "weekly": "dict", "monthly": "dict"},
    performance_requirements="<100ms response time"
)
async def get_budget_summary(budget_id: str, period: str):
    pass

# Performance boundary for usage tracking
@performance_boundary(
    title="Usage Record Processing",
    description="Process incoming usage records in real-time",
    sla="<50ms per record",
    optimization_notes="Batch database writes for efficiency",
    measured_impact="Handles 1000+ records/second"
)
async def record_usage(self, usage_data: dict):
    pass
```

### Penia UI Semantic Tags
```html
<!-- Budget component with full semantic tagging -->
<div class="budget" 
     data-tekton-area="budget" 
     data-tekton-component="budget" 
     data-tekton-type="component-workspace" 
     data-tekton-ai="budget-assistant" 
     data-tekton-ai-ready="false">
    
    <!-- Menu navigation -->
    <div class="budget__menu-bar" 
         data-tekton-zone="menu" 
         data-tekton-nav="component-menu">
        <div class="budget__tab" 
             data-tab="dashboard" 
             data-tekton-menu-item="Dashboard"
             data-tekton-menu-component="budget"
             data-tekton-menu-active="true"
             data-tekton-menu-panel="dashboard-panel"
             data-tekton-nav-target="dashboard-panel">
            <span class="budget__tab-label">Dashboard</span>
        </div>
    </div>
    
    <!-- Actions with proper tagging -->
    <button class="budget__button budget__button--success" 
            id="clear-alerts" 
            onclick="budget_clearAlerts(); return false;" 
            data-tekton-action="clear-alerts" 
            data-tekton-action-type="success">
        Clear All
    </button>
    
    <!-- Filter controls -->
    <div class="budget__filter-group">
        <label class="budget__filter-label">Beginning:</label>
        <input type="date" 
               class="budget__input" 
               id="start-date"
               data-tekton-filter="start-date"
               data-tekton-filter-type="date">
    </div>
</div>
```

### TektonCore Merge UI Example
```html
<!-- Sprint merge card with full tagging -->
<div class="tekton__merge-card"
     data-tekton-element="merge-card"
     data-tekton-merge-id="${merge.id}"
     data-tekton-status="${merge.status}"
     data-tekton-priority="${merge.priority}">
    
    <div class="tekton__merge-header"
         data-tekton-zone="header">
        <h3 data-tekton-element="merge-name">${merge.name}</h3>
        <span data-tekton-element="status-badge"
              data-tekton-status="ready-for-merge">Ready</span>
    </div>
    
    <div class="tekton__merge-actions"
         data-tekton-zone="actions">
        <button data-tekton-action="execute-merge"
                data-tekton-merge-target="${merge.id}"
                data-tekton-trigger="dry-run"
                data-tekton-workflow="merge-check">
            Execute
        </button>
    </div>
</div>

<!-- Conflict resolution modal -->
<div class="tekton__modal-overlay"
     data-tekton-modal="merge-conflict"
     data-tekton-modal-type="decision"
     data-tekton-conflict-type="content"
     data-tekton-ai-ready="true">
    
    <div class="tekton__modal-actions"
         data-tekton-zone="resolution-actions">
        <button data-tekton-action="fix-conflict"
                data-tekton-ai="conflict-resolver"
                data-tekton-confidence="high">Fix</button>
        <button data-tekton-action="consult-coder"
                data-tekton-target="original-coder"
                data-tekton-workflow="human-review">Consult</button>
        <button data-tekton-action="redo-sprint"
                data-tekton-priority="1"
                data-tekton-workflow="sprint-recreation">Redo</button>
    </div>
</div>
```

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
    from landmarks import architecture_decision, api_contract
except ImportError:
    def architecture_decision(**kwargs):
        def decorator(func): return func
        return decorator
    def api_contract(**kwargs):
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
     data-tekton-area="functional-area">
    
    <!-- Navigation -->
    <nav data-tekton-nav="component-nav">
        <button data-tekton-nav-item="item1"
                data-tekton-nav-target="target1">
            Item 1
        </button>
    </nav>
    
    <!-- Content -->
    <div data-tekton-zone="content"
         data-tekton-state="active">
        <!-- Component content -->
    </div>
</div>
```

## Why This Matters

1. **Knowledge Graph**: Every landmark and tag feeds Athena's semantic understanding
2. **CI Navigation**: CIs can find and understand code without guessing
3. **Human Understanding**: New developers/CIs immediately grasp system structure
4. **Consistency**: Following these standards ensures predictable, maintainable code
5. **Context Preservation**: Saves ~40% context by eliminating exploration/errors

## Summary

This document is our standard of practice. At the end of every sprint, use the checklist to ensure you've properly marked your code with landmarks and your UI with semantic tags. These aren't optional decorations - they're essential infrastructure that makes Tekton navigable and understandable for everyone who works with it.

Remember Casey's wisdom: "Map First, Build Second" - but also "Update the Map When You Build!"

---

*Last Updated: 2025-07-31*
*Standard Version: 1.2*
*Changes: Added Penia/Budget component examples for both landmarks and semantic tags*