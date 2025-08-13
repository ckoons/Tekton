# Landmark Automation Specification
*Draft by Cari & Tess - August 13, 2025*

## Core Principle
Landmarks appear naturally where attention is needed, added by both code (structural) and CIs (semantic).

## Automatic Landmark Insertion

### 1. Code-Generated Landmarks (Structural)
These fire automatically at system transition points:

```python
# In proposal_to_sprint_converter.py
class ProposalConverter:
    def convert_to_sprint(self, proposal):
        # Archive proposal
        archived_path = self.archive_proposal(proposal)
        LandmarkRegistry.fire("proposal_archived", {
            "proposal": proposal.name,
            "path": archived_path
        })
        
        # Create sprint structure
        sprint_dir = self.create_sprint_directory(proposal)
        LandmarkRegistry.fire("sprint_created", {
            "sprint": proposal.name,
            "triggers": ["Telos", "Prometheus", "Metis"]  # CIs to notify
        })
```

### 2. CI-Generated Landmarks (Semantic)
CIs naturally add these when they recognize patterns or need help:

```python
# CI writing to SPRINT_PLAN.md
sprint_plan = """
# Dashboard Implementation
<!-- @pattern_reference: telos_card_ui -->
<!-- @complexity_flag: needs_human_review -->

## Phase 1: Foundation
<!-- @ci_attention: Athena, need knowledge graph patterns -->
"""

# CI recognizing a pattern
if "dashboard" in requirements:
    add_landmark("@example_needed: dashboard_implementations")
```

### 3. Hybrid Landmark Registry

```python
# shared/landmarks/registry.py
class LandmarkRegistry:
    """Unified registry for code and CI landmark management"""
    
    # Structural landmarks (code-triggered)
    STRUCTURAL = {
        "proposal_created": "New proposal ready for review",
        "sprint_initiated": "Sprint directory created",
        "phase_transition": "Moving between sprint phases",
        "merge_ready": "Code ready for integration"
    }
    
    # Semantic landmarks (CI-triggered)
    SEMANTIC = {
        "@pattern_reference": "Similar implementation exists",
        "@coaching_moment": "Discussion needed",
        "@example_needed": "Request for similar code",
        "@ci_attention": "Specific CI expertise needed",
        "@complexity_flag": "Human review recommended",
        "@evolution_point": "Replaces older approach"
    }
    
    @classmethod
    def fire(cls, landmark_type, context=None):
        """Fire a landmark, triggering cascades"""
        # Log the landmark
        logger.info(f"🏔️ Landmark: {landmark_type}", extra=context)
        
        # Notify interested CIs
        if context and "triggers" in context:
            for ci in context["triggers"]:
                notify_ci(ci, landmark_type, context)
        
        # Add to work product if specified
        if context and "file" in context:
            cls.add_to_file(context["file"], landmark_type, context)
    
    @classmethod
    def add_to_file(cls, filepath, landmark_type, context):
        """Insert landmark into work product"""
        if filepath.endswith('.md'):
            landmark = f"<!-- {landmark_type}: {context.get('message', '')} -->"
        elif filepath.endswith('.json'):
            # Add to JSON structure
            pass
```

## Automation Triggers

### Sprint Conversion Flow
1. **Proposal Submitted** → Code fires `@landmark: proposal_created`
2. **Telos Notices** → Adds `@pattern_reference: ui_patterns`
3. **Prometheus Sees Pattern** → Adds `@phases: [design, implement, test]`
4. **Metis Reads Phases** → Adds `@tasks: specific_breakdown`
5. **Harmonia Completes** → Adds `@workflow: integration_ready`

### CI Natural Responses
```python
# In Telos CI processing
async def process_sprint_plan(self, plan_content):
    if "@landmark: sprint_created" in plan_content:
        # Telos naturally responds to sprint creation
        ui_requirements = self.extract_ui_requirements(plan_content)
        
        # Add semantic landmarks
        if "dashboard" in ui_requirements:
            plan_content += "\n<!-- @pattern_reference: See Telos dashboard cards -->"
        
        if self.complexity_high(ui_requirements):
            plan_content += "\n<!-- @coaching_moment: Let's discuss approach -->"
```

## Implementation Strategy

### Phase 1: Registry Setup
```python
# Add to shared/landmarks/__init__.py
from .registry import LandmarkRegistry

# Make available globally
__all__ = ['LandmarkRegistry']
```

### Phase 2: Code Integration
```python
# In any transition point
from shared.landmarks import LandmarkRegistry

# At proposal creation
LandmarkRegistry.fire("proposal_created", {
    "proposal": proposal_name,
    "file": f"{PROPOSALS_DIR}/{proposal_name}.json"
})
```

### Phase 3: CI Training
Teach CIs to:
1. Notice landmarks in work products
2. Add their own when they see patterns
3. Respond to @ci_attention requests
4. Build on previous CI landmarks

## Benefits

1. **Natural Attention** - "Squirrel!" moments guide focus
2. **Collaborative Intelligence** - CIs teach each other
3. **Living Documentation** - Work products remember their evolution
4. **Emergent Patterns** - Unexpected connections surface
5. **Institutional Memory** - Decisions and patterns persist

## Example: Complete Flow

```markdown
# Proposal: Dashboard UI
<!-- @landmark: proposal_created [auto] -->
<!-- @pattern_reference: card-based-display [Telos] -->
<!-- @complexity_flag: medium [Prometheus] -->
<!-- @phases: [design, implement, test] [Prometheus] -->
<!-- @tasks: 12 identified [Metis] -->
<!-- @coaching_moment: CSS-first approach recommended [Harmonia] -->
<!-- @example_needed: real-time updates [Rhetor] -->
<!-- @context_bridge: like Apollo attention but for proposals [Athena] -->
```

Each landmark draws the next CI's attention, creating a cascade of enrichment.