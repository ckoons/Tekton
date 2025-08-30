# Apollo Cognitive Guidance System

## Overview

The Apollo Preparation System acts as a **cognitive coach** for Companion Intelligences (CIs), guiding them through proper memory workflow and context preparation. It transforms raw memories into structured Context Briefs with embedded cognitive guidance that helps CIs maintain optimal memory patterns naturally.

## How It Works

### 1. Context Brief Preparation

Apollo prepares **token-aware Context Briefs** that include:
- **Task Context**: What the CI is currently working on
- **Relevant Memories**: Curated from short, medium, and long-term storage
- **Next Steps**: Clear guidance on what comes next
- **Cognitive Instructions**: How to use the brief effectively
- **Inner Voice Prompts**: Subtle, naturalistic reminders

### 2. Memory Rhythm

The system implements a naturalistic memory workflow:

```
Short-term Memory:  Every turn (immediate context)
Medium-term Memory: Every N turns (consolidation)  
Long-term Memory:   Phase completion (permanent storage)
Latent Space:       Task completion (deep integration)
```

The **Memory Rhythm Indicator** provides visual feedback:
- 🟢 **Active**: Memory updates needed frequently
- 🟡 **Monitoring**: Watching for phase transitions
- 🔴 **Update Needed**: Time to consolidate memories
- ⚪ **Idle**: No active memory workflow

### 3. Inner Voice System

Instead of explicit commands, Apollo provides gentle prompts that feel natural:

**Traditional Approach:**
```
WARNING: Update your short-term memory now!
COMMAND: Save current context to memory store
```

**Apollo's Inner Voice:**
```
"Remember to capture that insight about the Redux pattern"
"This error solution might be useful later"
"Consider documenting this architectural decision"
```

### 4. CI Registry Integration

Apollo dynamically loads available CIs from the registry:
- **Specialist CIs**: Ergon, Rhetor, Noesis, Athena, Hermes, Sophia, Apollo
- **Terminal CIs**: Direct interfaces for each specialist
- **Project CIs**: Task-specific companion intelligences

### 5. Task Association

Each Context Brief can be associated with:
- Active tasks from Ergon
- Project phases
- Debugging sessions
- Code reviews
- Architecture decisions

## User Interface Components

### Cognitive Guidance Builder
Located in the Preparation tab, this section includes:

1. **CI Selection**
   - Source CI (who's requesting)
   - Target CI (who will receive the brief)

2. **Task Context**
   - Current task description
   - Next steps planning

3. **Memory Workflow Rules**
   - Checkboxes for each memory tier
   - Visual rhythm indicator

4. **Inner Voice Prompts**
   - Add custom prompts
   - Use templates for common scenarios

### Context Brief Display
Shows the generated brief with:
- Memory items grouped by type
- Token count awareness
- Cognitive instructions
- Save/Load functionality

### Templates
Pre-configured workflows for common scenarios:
- **Task Start**: Initial context gathering
- **Debugging**: Error tracking and solutions
- **Code Review**: Standards and patterns
- **Phase Completion**: Long-term consolidation

## How to Test

### 1. Open Test Interface
```bash
open test_apollo_preparation_ui.html
```

### 2. Manual Testing in Hephaestus

1. Navigate to Apollo component
2. Click "Preparation" tab
3. Select Source and Target CIs
4. Enter task context
5. Choose memory workflow rules
6. Add inner voice prompts
7. Click "Generate Brief"

### 3. Check Memory Rhythm

Watch the floating indicator (bottom-right):
- Should pulse when updates are needed
- Changes color based on workflow state
- Provides hover tooltips with guidance

### 4. Test Brief Persistence

1. Generate a brief
2. Click "Save Brief" and name it
3. Reload the page
4. Select from "Saved Briefs" dropdown
5. Click "Load Brief" to restore

## API Endpoints

### Generate Context Brief
```
POST /api/preparation/generate
{
  "source_ci": "ergon-ci",
  "target_ci": "rhetor-ci",
  "task_context": "Implementing new feature",
  "memory_workflow": {
    "shortTerm": true,
    "mediumTerm": false
  },
  "inner_voice_prompts": ["Remember patterns"]
}
```

### Save/Load Briefs
```
POST /api/preparation/save
GET /api/preparation/saved
GET /api/preparation/saved/{brief_id}
DELETE /api/preparation/saved/{brief_id}
```

### CI Registry
```
GET /api/ci-registry
```

## Memory Workflow Patterns

### Short-term (Every Turn)
- Immediate context from current interaction
- Working memory for active problem-solving
- Quick insights and observations

### Medium-term (Every N Turns)
- Consolidated patterns and solutions
- Verified approaches that worked
- Connections between related issues

### Long-term (Phase Completion)
- Architectural decisions
- Project-wide patterns
- Team knowledge and conventions

### Latent Space (Task End)
- Deep insights for future tasks
- Abstract patterns and principles
- Cross-project learnings

## Visual Design

The system uses **Apollo Gold (#FF9500)** throughout:
- Solid gold buttons with black text
- Gold borders on input fields
- Gold accents for active states
- Subtle gold glow for rhythm indicator

## Integration Points

### With Rhetor (Orchestration)
- Rhetor requests Context Briefs via MCP
- Apollo prepares token-aware packages
- Includes relevant memories and guidance

### With Ergon (Task Management)
- Links briefs to active tasks
- Tracks memory updates per task
- Provides task-specific templates

### With Athena (Knowledge Graph)
- Exports memories as landmarks
- Maintains Apollo namespace
- Enables graph traversal of memories

## Benefits

1. **Natural Workflow**: Memories update organically, not through forced commands
2. **Token Efficiency**: Curated briefs stay within context limits
3. **Cognitive Coaching**: Gentle guidance improves CI performance
4. **Pattern Recognition**: Learns from past interactions
5. **Task Continuity**: Maintains context across sessions

## Example Workflow

1. **Ergon CI** starts a new debugging task
2. **Apollo** receives task context via MCP
3. Prepares Context Brief with:
   - Recent error patterns (short-term)
   - Similar past issues (medium-term)
   - Debugging best practices (long-term)
4. Adds inner voice prompts:
   - "Check if this relates to yesterday's API changes"
   - "Remember to update the test suite"
5. **Rhetor CI** receives brief and orchestrates debugging
6. Memory rhythm indicator reminds to capture solution
7. Solution gets stored as new memory landmark

## Future Enhancements

1. **Machine Learning Integration**
   - Learn optimal memory patterns per CI
   - Predict which memories are most relevant
   - Adaptive rhythm based on task complexity

2. **Multi-CI Coordination**
   - Share context across CI teams
   - Synchronize memory updates
   - Collaborative knowledge building

3. **Advanced Templates**
   - Industry-specific workflows
   - Custom rhythm patterns
   - Role-based guidance

## Conclusion

The Apollo Cognitive Guidance System transforms memory management from a manual chore into a natural, guided workflow. By acting as a cognitive coach rather than a command system, it helps CIs maintain optimal memory patterns while focusing on their primary tasks.

The combination of Context Briefs, Memory Rhythm, and Inner Voice creates a seamless experience where memory updates happen naturally at the right moments, improving both individual CI performance and collective system intelligence.