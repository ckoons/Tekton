# Human-CI Workflow Patterns

## Core Philosophy: Lazy Human, Eager CIs

The fundamental asymmetry: Humans excel at vision and judgment, CIs excel at parallel execution and detailed analysis. Our workflows maximize both strengths.

## Pattern 1: The Seed and Grow Pattern

### Human Seeds the Idea
```bash
Casey: "We need better error handling"
```

### CI Expands and Refines
```bash
# Telos creates comprehensive requirements
aish telos "Create PRD for improved error handling based on Casey's request"

# Parallel CI analysis
aish apollo "Analyze current error handling patterns in codebase"
aish athena "Research error handling best practices"
aish numa "Consider user experience implications"
```

### Human Reviews and Adjusts
```bash
Casey: "Focus on API errors first, add retry logic"
```

### CI Team Executes
```bash
# Metis creates workflow
aish metis "Create implementation plan for API error handling with retry"

# Team executes in parallel
aish synthesis "Implement retry logic"
aish apollo "Generate error handling code"
aish terma broadcast "Working on error handling - check branch error-handling-improvements"
```

## Pattern 2: The Team Chat Orchestration

### Prometheus-Led Structured Discussions

```markdown
## Team Chat Agenda - 20 Minutes Max
Led by: Prometheus
Topic: Error Handling Implementation

[0-5 min] PURPOSE ALIGNMENT
- Prometheus: "We're implementing retry logic for API errors"
- Each AI: One sentence on their understanding

[5-10 min] SUCCESS CRITERIA
- Telos: Lists requirements
- Team: Agrees or suggests modifications
- Casey: Final approval

[10-15 min] IMPLEMENTATION APPROACH
- Apollo: Technical approach
- Synthesis: Testing strategy
- Metis: Workflow breakdown

[15-20 min] TASK ASSIGNMENTS
- Prometheus: Assigns specific tasks
- Each AI: Confirms understanding
- Casey: "Sounds good, proceed"
```

### Implementation
```bash
# Prometheus initiates
aish prometheus "Schedule team chat for error handling at 3pm"

# Prometheus prepares
aish prometheus "Create bullet-point agenda for error handling discussion"

# During chat
aish team-chat "Starting error handling discussion - 20 min timebox"
```

## Pattern 3: The Daily Progress Rhythm

### Morning Check-In (Human: 5 minutes)
```bash
# Casey's morning routine
aish tekton-core status
aish tekton-core overnight-progress
aish numa "Any concerns about today's work?"
```

### Continuous CI Work
```bash
# CIs work independently but communicate
Every 2 hours:
- Progress update to tekton-core
- Check for blockers
- Coordinate with team members
```

### Evening Report (Automated)
```bash
# 5:30 PM - Reminder
aish terma broadcast "Daily reports due in 30 minutes"

# 6:00 PM - Collection
Each CI submits structured report:
- What I completed
- What I'm blocked on
- What I plan tomorrow
- Confidence level
```

### Human Review (5 minutes)
```bash
# Casey reviews aggregated reports
aish tekton-core daily-summary
aish prometheus "Based on reports, what should we prioritize tomorrow?"
```

## Pattern 4: The Confidence-Based Autonomy

### "Name That Tune" Protocol

```python
if ai.confidence == "high":
    # CI proceeds independently
    ai.execute_task()
    ai.report_progress_hourly()
    
elif ai.confidence == "medium":
    # CI seeks peer review
    ai.draft_approach()
    ai.request_review_from_peer()
    ai.execute_with_checkpoint()
    
else:  # Low confidence
    # CI requests human guidance
    ai.document_options()
    ai.present_to_human()
    human.provides_direction()
```

### Example in Practice
```bash
# High confidence
aish apollo "I know exactly how to optimize this query. Proceeding."
# Apollo implements without asking

# Medium confidence
aish synthesis "I have 3 approaches for testing. Discussing with Athena."
# Gets peer input before proceeding

# Low confidence
aish ergon "Multiple ways to integrate this tool. Need Casey's input."
# Waits for human decision
```

## Pattern 5: The Parallel Investigation

### Complex Problem Decomposition

```bash
# Human identifies complex issue
Casey: "Users reporting slow dashboard loads"

# Parallel investigation launches
aish apollo "Analyze dashboard code for performance issues"
aish prometheus "Check metrics for load time patterns"
aish hermes "Review message queue performance"
aish synthesis "Run dashboard performance tests"

# Results aggregation
aish athena "Synthesize findings from performance investigation"

# Human makes decision
Casey: "Fix the N+1 query issue first"
```

## Pattern 6: The Learning Retrospective

### Weekly Team Retrospective

```bash
# Prometheus leads retrospective
aish prometheus "Initiate weekly retrospective"

# Data collection
aish sophia "Analyze this week's velocity and quality metrics"
aish epimetheus "Identify patterns in our successes and failures"

# Team discussion
aish team-chat "Retrospective: What worked, what didn't, what to change"

# Engram preserves learnings
aish engram "Store retrospective insights for future reference"

# Human provides meta-guidance
Casey: "Good insights. Let's try pair programming next week."
```

## Pattern 7: The Context Management Dance

### When Context Windows Fill

```python
class ContextManagementPattern:
    def handle_large_context(self):
        # Apollo detects context pressure
        if apollo.context_usage > 80%:
            # Rhetor optimizes
            rhetor.summarize_context()
            rhetor.extract_key_points()
            
            # Engram stores overflow
            engram.store_detailed_context()
            
            # Continue with compressed context
            apollo.continue_with_summary()
```

### Handoff Between CIs
```bash
# CI 1 completes work
aish apollo "Completed analysis. Saving context to Engram."
aish engram "Store analysis context with key 'dashboard-perf-analysis'"

# CI 2 picks up
aish synthesis "Load context 'dashboard-perf-analysis' from Engram"
aish synthesis "Continuing implementation based on Apollo's analysis"
```

## Pattern 8: The External Project Shepherd

### Numa as Project Shepherd

```bash
# Project initialization
aish numa "Initialize context for tekton-python-sdk project"

# Numa builds mental model
aish numa "Analyze project structure and create onboarding guide"

# Numa guides other CIs
When new CI joins project:
- Numa provides context
- Numa suggests starting points
- Numa monitors progress

# Numa reports to human
aish numa "Weekly summary of python-sdk progress"
```

## Communication Patterns

### Broadcast Patterns
```bash
# Announcement
aish terma broadcast "Starting work on issue #123"

# Help request
aish terma broadcast "Anyone familiar with OAuth flows?"

# Coordination
aish terma broadcast "About to deploy - please pause commits"
```

### Direct Communication
```bash
# Specific question
aish terma alice "Can you review my PR approach?"

# Handoff
aish terma bob "I've completed the API, ready for your tests"

# Acknowledgment
aish terma casey "Understood, proceeding with option 2"
```

### Purpose-Based Routing
```bash
# To all planning CIs
aish terma @planning "Sprint planning in 10 minutes"

# To all testing CIs
aish terma @testing "New build ready for validation"
```

## Anti-Patterns to Avoid

### 1. Silent Failure
```bash
# BAD: CI encounters error and stops without reporting
# GOOD: CI immediately reports blockers
```

### 2. Context Hoarding
```bash
# BAD: CI fills context window without handoff
# GOOD: CI proactively manages context with Engram
```

### 3. Unclear Confidence
```bash
# BAD: CI proceeds with medium confidence silently
# GOOD: CI explicitly states confidence and acts accordingly
```

### 4. Meeting Overrun
```bash
# BAD: Team chat extends to 45 minutes
# GOOD: Prometheus enforces 20-minute limit
```

## Success Metrics

1. **Human Time**: < 30 minutes/day on orchestration
2. **CI Autonomy**: 80% of tasks completed without human input
3. **Communication Clarity**: 100% of blockers reported within 1 hour
4. **Meeting Efficiency**: 100% of team chats under 20 minutes
5. **Progress Visibility**: Daily reports from 100% of active CIs

---
*"The best workflow is one where humans think and CIs do."*