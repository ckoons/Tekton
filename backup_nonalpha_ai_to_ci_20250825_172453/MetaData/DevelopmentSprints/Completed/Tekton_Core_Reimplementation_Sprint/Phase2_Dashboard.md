# Phase 2: Dashboard & Functionality

## Overview

Build the visual dashboard that makes project management intuitive, implement core project operations, and integrate merge coordination for PR management.

## Timeline: Weeks 2-3

### Week 2, Day 1-2: Dashboard UI Foundation

**Create Dashboard Structure**
```
tekton-core/
└── ui/
    ├── index.html          # Main dashboard
    ├── css/
    │   └── dashboard.css   # Styling (bubbles, layout)
    ├── js/
    │   ├── dashboard.js    # Main dashboard logic
    │   ├── projects.js     # Project bubble management
    │   ├── chat.js         # Chat integration
    │   └── github.js       # GitHub operations
    └── components/
        ├── project-bubble.html
        ├── chat-panel.html
        └── merge-dialog.html
```

**Dashboard Layout**
```
┌─────────────────────────────────────────────────┐
│  Dashboard | Project Chat | Team Chat           │
├─────────────────────────────────────────────────┤
│                                                 │
│     ○ Tekton          ○ Python SDK             │
│                                                 │
│     ○ JS Client       ○ New GitHub Project     │
│                                                 │
│  ┌─────────────────────────────────────┐       │
│  │ Selected: Tekton                     │       │
│  │ [Status] [Tasks] [PRs] [Edit] [Clone]│       │
│  │ [Pull/Fetch]                         │       │
│  └─────────────────────────────────────┘       │
└─────────────────────────────────────────────────┘
```

### Week 2, Day 3-4: Project Bubbles

**Bubble Visualization**
```javascript
class ProjectBubble {
    constructor(project) {
        this.project = project;
        this.element = this.createElement();
        this.selected = false;
    }
    
    createElement() {
        const bubble = document.createElement('div');
        bubble.className = 'project-bubble';
        bubble.innerHTML = `
            <div class="bubble-icon">${this.getIcon()}</div>
            <div class="bubble-name">${this.project.name}</div>
            <div class="bubble-ai">${this.project.companion_ai}</div>
        `;
        bubble.onclick = () => this.select();
        return bubble;
    }
    
    select() {
        // Show project controls
        dashboard.showProjectControls(this.project);
    }
}
```

**Special Bubbles**
1. **New GitHub Project** - Shows form on click
2. **Regular Projects** - Shows control buttons

### Week 2, Day 5: Project Controls

**Status Button**
```javascript
async function showProjectStatus(projectId) {
    const status = await api.getProjectStatus(projectId);
    
    // Display:
    // - Current branch
    // - Active workers (AI terminals)
    // - Open tasks
    // - Recent commits
    // - Health indicators
    
    const dialog = new StatusDialog(status);
    dialog.show();
}
```

**Tasks Button**
```javascript
async function showProjectTasks(projectId) {
    const tasks = await api.getProjectTasks(projectId);
    
    // Display GitHub issues
    // Show assignment status
    // Allow task creation
    // Quick assign to AI
}
```

**Edit Button**
```javascript
function showProjectEdit(project) {
    const form = new EditForm({
        name: project.name,
        repo: project.repo,
        upstream: project.upstream,
        workingDir: project.workingDir,
        companionAI: project.companionAI
    });
    
    form.onSave = async (data) => {
        await api.updateProject(project.id, data);
        dashboard.refresh();
    };
    
    form.onDelete = async () => {
        if (confirm("Really delete project?")) {
            await api.deleteProject(project.id);
            dashboard.refresh();
        }
    };
}
```

### Week 2, Day 6-7: Clone Functionality

**Clone Existing Project**
```javascript
async function cloneProject(sourceProject) {
    const dialog = new CloneDialog(sourceProject);
    
    dialog.onConfirm = async (newData) => {
        // 1. Clone repository locally
        await api.cloneRepository(sourceProject.repo, newData.workingDir);
        
        // 2. Create fork on GitHub
        await api.createGitHubFork(sourceProject.repo, newData.repoName);
        
        // 3. Register new project
        const newProject = await api.createProject({
            name: newData.name,
            repo: newData.repoUrl,
            upstream: sourceProject.repo,
            workingDir: newData.workingDir,
            companionAI: newData.companionAI
        });
        
        // 4. Add new bubble
        dashboard.addProject(newProject);
    };
}
```

**New GitHub Project**
```javascript
function showNewGitHubProject() {
    const form = new GitHubProjectForm();
    
    form.onSubmit = async (githubUrl) => {
        // 1. Parse GitHub URL
        const repoInfo = parseGitHubUrl(githubUrl);
        
        // 2. Clone to local
        const workingDir = generateWorkingDir(repoInfo.name);
        await api.cloneRepository(githubUrl, workingDir);
        
        // 3. Create our fork
        const forkUrl = await api.createGitHubFork(githubUrl);
        
        // 4. Create project
        const project = await api.createProject({
            name: repoInfo.name,
            repo: forkUrl,
            upstream: githubUrl,
            workingDir: workingDir,
            companionAI: "numa"  // Default
        });
        
        dashboard.addProject(project);
    };
}
```

### Week 3, Day 1-3: Merge Coordination Integration

**PR Management Interface**
```javascript
async function showProjectPRs(projectId) {
    const prs = await api.getProjectPRs(projectId);
    
    const dialog = new PRDialog(prs);
    dialog.onPRClick = (pr) => showMergeCoordination(pr);
}
```

**Merge Coordination Dialog**
```javascript
class MergeCoordinationDialog {
    constructor(pr) {
        this.pr = pr;
        this.createDialog();
    }
    
    createDialog() {
        this.element = createElement(`
            <div class="merge-dialog">
                <h2>PR #${this.pr.number}: ${this.pr.title}</h2>
                
                <div class="pr-details">
                    <div>Author: ${this.pr.author}</div>
                    <div>Branch: ${this.pr.branch}</div>
                    <div>Changes: +${this.pr.additions} -${this.pr.deletions}</div>
                </div>
                
                <div class="pr-diff">
                    ${this.renderDiff()}
                </div>
                
                <div class="pr-tests">
                    ${this.renderTestStatus()}
                </div>
                
                <div class="merge-actions">
                    <button onclick="this.approve()">✓ Approve & Merge</button>
                    <button onclick="this.reject()">✗ Reject & Task</button>
                    <button onclick="this.resolve()">↻ Resolve Conflicts</button>
                    <button onclick="this.deletePR()">🗑 Delete PR</button>
                </div>
            </div>
        `);
    }
    
    async approve() {
        // 1. Approve PR on GitHub
        await api.approvePR(this.pr.id);
        
        // 2. Merge to main
        await api.mergePR(this.pr.id, {
            method: "squash",
            message: `Merge PR #${this.pr.number}: ${this.pr.title}`
        });
        
        // 3. Delete branch
        await api.deleteBranch(this.pr.branch);
        
        // 4. Notify team
        await api.sendTeamChat(`Merged PR #${this.pr.number}`);
        
        this.close();
    }
    
    async reject() {
        // 1. Create task for fixes
        const task = await api.createTask({
            title: `Fix issues in PR #${this.pr.number}`,
            description: this.getRejectionReason(),
            assignee: this.pr.author
        });
        
        // 2. Comment on PR
        await api.commentOnPR(this.pr.id, 
            `Needs work. Created task #${task.number}`);
        
        // 3. Update PR status
        await api.updatePRStatus(this.pr.id, "changes_requested");
        
        this.close();
    }
    
    async resolve() {
        // 1. Show conflict resolution UI
        const conflicts = await api.getConflicts(this.pr.id);
        const resolver = new ConflictResolver(conflicts);
        
        resolver.onResolved = async (resolution) => {
            await api.resolveConflicts(this.pr.id, resolution);
            this.refresh();
        };
    }
    
    async deletePR() {
        if (confirm("Really delete this PR?")) {
            await api.closePR(this.pr.id);
            await api.deleteBranch(this.pr.branch);
            this.close();
        }
    }
}
```

### Week 3, Day 4-5: Pull/Fetch Implementation

**Upstream Synchronization**
```javascript
async function pullFromUpstream(projectId) {
    const project = await api.getProject(projectId);
    
    if (!project.upstream) {
        alert("No upstream configured");
        return;
    }
    
    const dialog = new PullDialog(project);
    
    dialog.onPull = async (options) => {
        // 1. Fetch from upstream
        const changes = await api.fetchUpstream(project.id);
        
        // 2. Show changes
        if (changes.length > 0) {
            const merge = confirm(`${changes.length} commits available. Merge?`);
            
            if (merge) {
                // 3. Merge upstream changes
                await api.mergeUpstream(project.id, {
                    strategy: options.strategy || "merge"
                });
                
                // 4. Run tests
                await api.runTests(project.id);
                
                // 5. Notify team
                await api.sendProjectChat(project.id, 
                    `Pulled ${changes.length} commits from upstream`);
            }
        } else {
            alert("Already up to date");
        }
    };
}
```

### Week 3, Day 6-7: Testing & Polish

**Integration Testing**
1. Create multiple projects
2. Test chat integration
3. Test clone operations
4. Test merge coordination
5. Test upstream pulls

**UI Polish**
- Smooth animations
- Loading states
- Error handling
- Responsive design

## Backend Extensions

### Project Storage Enhancement
```python
class Project:
    id: str
    name: str
    repo: str
    upstream: Optional[str]
    working_dir: str
    companion_ai: str
    created_at: datetime
    last_activity: datetime
    status: ProjectStatus
    open_prs: List[int]
    active_tasks: List[int]
    team_members: List[str]
```

### New API Endpoints
```python
# Project operations
POST /api/v1/projects/{id}/clone
POST /api/v1/projects/{id}/pull
GET /api/v1/projects/{id}/status
GET /api/v1/projects/{id}/tasks
GET /api/v1/projects/{id}/prs

# GitHub operations
POST /api/v1/github/clone
POST /api/v1/github/fork
GET /api/v1/github/prs/{pr_id}
POST /api/v1/github/prs/{pr_id}/merge
POST /api/v1/github/prs/{pr_id}/comment

# Merge coordination
GET /api/v1/merge/conflicts/{pr_id}
POST /api/v1/merge/resolve/{pr_id}
```

## Project Registry Storage

**Location**: `~/.tekton/projects/registry.json`

**Enhanced Format**:
```json
{
  "projects": [
    {
      "id": "tekton-main",
      "name": "Tekton",
      "repo": "https://github.com/casey/Tekton",
      "upstream": null,
      "working_dir": "/Users/casey/projects/github/Tekton",
      "companion_ai": "numa",
      "created_at": "2025-01-05T10:00:00Z",
      "last_activity": "2025-01-05T14:30:00Z",
      "status": {
        "health": "good",
        "current_branch": "main",
        "uncommitted_changes": false
      },
      "open_prs": [145, 146],
      "active_tasks": [234, 235, 236],
      "team_members": ["alice", "bob", "charlie"]
    }
  ]
}
```

## Success Criteria

### Must Have
- [ ] Visual dashboard with project bubbles
- [ ] All project control buttons working
- [ ] Clone functionality for existing projects
- [ ] New GitHub project creation
- [ ] Merge coordination dialog with 4 actions
- [ ] Pull/Fetch from upstream

### Should Have
- [ ] Real-time status updates
- [ ] Smooth UI transitions
- [ ] Error recovery
- [ ] Project search/filter

### Nice to Have
- [ ] Project templates
- [ ] Bulk operations
- [ ] Project archiving
- [ ] Activity timeline

---
*"Making project management visual and intuitive"*