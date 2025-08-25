# tekton-core Rewrite Specification

## Component Overview

tekton-core transforms from a simple component into the **Multi-CI Engineering Platform Manager** - the conductor of the CI orchestra.

## Architecture

### Core Responsibilities

```python
class TektonCore:
    """
    Central orchestrator for multi-project, multi-CI development.
    
    Responsibilities:
    1. Project Registry - Track all projects under management
    2. GitHub Integration - Issues, PRs, branches, webhooks
    3. CI Orchestration - Assignment, coordination, monitoring
    4. Progress Tracking - Daily reports, dashboards, metrics
    5. Workflow Automation - GitHub Flow implementation
    """
```

### Directory Structure

```
tekton-core/
├── api/
│   ├── projects.py         # Project management endpoints
│   ├── github.py          # GitHub integration endpoints
│   ├── assignments.py     # CI work assignment endpoints
│   ├── workflows.py       # Workflow automation endpoints
│   └── dashboard.py       # Status and metrics endpoints
├── core/
│   ├── orchestrator.py    # Main orchestration logic
│   ├── project_registry.py # Project tracking
│   ├── ai_matcher.py      # CI capability matching
│   └── scheduler.py       # Work scheduling
├── github/
│   ├── client.py          # GitHub API wrapper
│   ├── webhooks.py        # Webhook handlers
│   ├── issues.py          # Issue management
│   └── pull_requests.py   # PR automation
├── storage/
│   ├── models.py          # Data models
│   ├── database.py        # SQLite/PostgreSQL
│   └── cache.py           # Redis caching
├── integrations/
│   ├── terma.py           # Terminal communication
│   ├── rhetor.py          # CI messaging
│   └── hermes.py          # Service discovery
└── utils/
    ├── metrics.py         # Performance tracking
    └── reports.py         # Report generation
```

## API Specification

### Project Management

```python
# GET /api/v1/projects
# List all managed projects
{
    "projects": [
        {
            "id": "tekton-main",
            "name": "Tekton",
            "repo": "github.com/user/Tekton",
            "directory": "/Users/casey/projects/Tekton",
            "shepherd": "numa",
            "status": "active",
            "health": 90
        },
        {
            "id": "python-sdk",
            "name": "Tekton Python SDK",
            "repo": "github.com/user/tekton-python-sdk",
            "directory": "/Users/casey/projects/external/tekton-python-sdk",
            "shepherd": "numa",
            "status": "active",
            "health": 85
        }
    ]
}

# POST /api/v1/projects
# Register new project
{
    "name": "Project Name",
    "repo_url": "https://github.com/org/repo",
    "shepherd": "numa",
    "team": ["apollo", "athena", "synthesis"]
}
```

### CI Assignment

```python
# GET /api/v1/assignments/active
# Current CI assignments
{
    "assignments": [
        {
            "terminal": "alice",
            "ai": "apollo",
            "project": "tekton-main",
            "issue": 123,
            "branch": "feature/apollo-123-add-caching",
            "status": "in_progress",
            "started": "2025-01-04T10:00:00Z",
            "confidence": "high"
        }
    ]
}

# POST /api/v1/assignments/create
# Assign issue to AI
{
    "issue_id": 123,
    "project_id": "tekton-main",
    "auto_assign": true  # or specify CI name
}
```

### GitHub Integration

```python
# GET /api/v1/github/issues/{project_id}
# List project issues
{
    "issues": [
        {
            "id": 123,
            "title": "Add caching layer",
            "labels": ["enhancement", "performance"],
            "complexity": "medium",
            "suggested_ai": ["apollo", "synthesis"],
            "status": "open"
        }
    ]
}

# POST /api/v1/github/branch
# Create feature branch
{
    "project_id": "tekton-main",
    "issue_id": 123,
    "terminal": "alice"
}
# Returns: {"branch": "feature/alice-123-add-caching"}
```

### Workflow Automation

```python
# POST /api/v1/workflows/start
# Start GitHub Flow for issue
{
    "issue_id": 123,
    "project_id": "tekton-main"
}

# GET /api/v1/workflows/status/{workflow_id}
# Check workflow progress
{
    "workflow_id": "wf-123",
    "steps": [
        {"name": "assign", "status": "complete"},
        {"name": "branch", "status": "complete"},
        {"name": "develop", "status": "in_progress"},
        {"name": "test", "status": "pending"},
        {"name": "pr", "status": "pending"}
    ]
}
```

## Database Schema

```sql
-- Projects table
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    repo_url TEXT NOT NULL,
    directory TEXT NOT NULL,
    shepherd TEXT,
    status TEXT DEFAULT 'active',
    health INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CI assignments
CREATE TABLE assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT REFERENCES projects(id),
    issue_id INTEGER,
    terminal_name TEXT,
    ai_name TEXT,
    branch_name TEXT,
    status TEXT,
    confidence TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Daily reports
CREATE TABLE daily_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_name TEXT,
    project_id TEXT,
    report_date DATE,
    progress TEXT,
    blockers TEXT,
    confidence TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workflow tracking
CREATE TABLE workflows (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    issue_id INTEGER,
    current_step TEXT,
    status TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

## Integration Points

### With Terma (Terminal Management)

```python
class TermaIntegration:
    def get_active_terminals(self):
        """Query Terma for active CI terminals"""
        
    def send_assignment(self, terminal, assignment):
        """Notify terminal of new assignment via terma message"""
        
    def request_status(self, terminal):
        """Request progress update from terminal"""
```

### With Rhetor (CI Communication)

```python
class RhetorIntegration:
    def analyze_issue(self, issue_text):
        """Use Rhetor to understand issue requirements"""
        
    def match_ai_capabilities(self, requirements):
        """Find best CI for task"""
        
    def coordinate_team(self, team_members, task):
        """Orchestrate multi-CI collaboration"""
```

### With Hermes (Service Discovery)

```python
class HermesIntegration:
    def register_service(self):
        """Register tekton-core with Hermes"""
        
    def discover_components(self):
        """Find available Tekton components"""
        
    def health_check_all(self):
        """Check health of all components"""
```

## Workflow Implementation

### GitHub Flow Automation

```python
class GitHubFlowWorkflow:
    """
    Implements standard GitHub Flow:
    1. Create branch from issue
    2. Development in branch
    3. Tests must pass
    4. Create PR
    5. Review and merge
    """
    
    async def execute(self, issue_id, project_id):
        # Step 1: Analyze issue
        issue = await self.analyze_issue(issue_id)
        
        # Step 2: Assign to AI(s)
        assignments = await self.assign_to_ai(issue)
        
        # Step 3: Create branches
        branches = await self.create_branches(assignments)
        
        # Step 4: Monitor development
        await self.monitor_progress(assignments)
        
        # Step 5: Run tests
        test_results = await self.run_tests(branches)
        
        # Step 6: Create PR if tests pass
        if test_results.passed:
            pr = await self.create_pr(branches)
            await self.assign_reviewers(pr)
```

### Daily Report Collection

```python
class DailyReportCollector:
    """
    Collects reports from all CIs at configured time
    """
    
    async def collect_reports(self):
        terminals = await self.terma.get_active_terminals()
        
        for terminal in terminals:
            # Request report via terma
            await self.terma.send_message(
                terminal,
                "Please provide your daily report"
            )
            
            # Store in database
            report = await self.wait_for_report(terminal)
            await self.store_report(report)
        
        # Generate summary for Casey
        summary = await self.generate_summary()
        await self.send_to_casey(summary)
```

## Configuration

```yaml
# tekton-core configuration
github:
  token: ${GITHUB_TOKEN}
  webhook_secret: ${WEBHOOK_SECRET}
  
projects:
  default_directory: /Users/casey/projects/external
  
ai_matching:
  complexity_threshold: 
    simple: 1  # Single AI
    medium: 3  # Small team
    complex: 5 # Large team
    
reporting:
  daily_report_time: "18:00"  # 6 PM
  reminder_time: "17:30"      # 5:30 PM
  
health_targets:
  week_1: 60
  week_2: 75
  week_3: 85
  week_4: 90
```

## Error Handling

### Graceful Degradation
- If GitHub API fails, queue operations
- If CI unavailable, reassign to available AI
- If tests fail, block PR but notify human

### Recovery Strategies
- Automatic retry with exponential backoff
- Human escalation for critical failures
- State persistence for crash recovery

## Performance Targets

- API response time: < 200ms
- Issue assignment: < 5 seconds
- Daily report collection: < 2 minutes
- Dashboard refresh: Real-time via WebSocket

---
*"tekton-core: Where human vision meets CI velocity"*