# Sprint: Ergon Docker Integration with Container CIs

## Overview
Implement comprehensive Docker support in Ergon with intelligent Container CIs that provide self-aware, self-managing containerized environments for Tekton projects and solutions.

## Goals
1. **Docker Management**: Full Docker lifecycle management through Ergon UI
2. **Container CIs**: Create intelligent CI for each container that understands and manages its contents
3. **TektonCore Integration**: Add Docker image generation to project cards
4. **Container Registry**: Extend Ergon's registry to include Docker solutions

## Phase 1: TektonCore Docker Button [0% Complete]

### Tasks
- [ ] Add "Create Docker Image" button to project cards in tekton-component.html
- [ ] Create `/tekton-core/tekton/api/docker.py` endpoint for Dockerfile generation
- [ ] Implement Dockerfile generation using project CI analysis
- [ ] Add docker_config field to Project model
- [ ] Create handoff API to pass Docker projects to Ergon
- [ ] Store Dockerfile in project repository
- [ ] Add modal to show generated Dockerfile with "Send to Ergon" option

### Success Criteria
- [ ] Button appears on all project cards
- [ ] Dockerfile generates based on project type
- [ ] Dockerfile saves to project directory
- [ ] Ergon receives Docker project registration
- [ ] Project CI provides intelligent analysis

### Blocked On
- [ ] Nothing currently blocking

## Phase 2: Ergon Docker Menu & Registry [0% Complete]

### Tasks
- [ ] Add "Docker" top-level menu item in Ergon UI
- [ ] Create Docker submenu structure (Images, Containers, Networks, Volumes)
- [ ] Extend Ergon Solution model for Docker configurations
- [ ] Create `/Ergon/ergon/docker/` module structure
- [ ] Implement Docker SDK integration
- [ ] Create Docker solution registry schema
- [ ] Add Docker build management endpoints
- [ ] Implement image tagging system (latest, version, sprint-based)

### Success Criteria
- [ ] Docker menu fully navigable
- [ ] Registry stores Docker solutions
- [ ] Build process works via UI
- [ ] Images properly tagged
- [ ] Docker SDK integrated

### Blocked On
- [ ] Waiting for Phase 1 completion

## Phase 3: Container CI Implementation [0% Complete]

### Tasks
- [ ] Create `/shared/container_ci/container_ci.py` base class
- [ ] Implement container process discovery
- [ ] Add service detection (web servers, databases, workers)
- [ ] Create health monitoring system
- [ ] Implement CI socket communication
- [ ] Auto-register Container CI with aish
- [ ] Add container optimization capabilities
- [ ] Implement multi-service coordination logic
- [ ] Create debugging assistance features

### Success Criteria
- [ ] Container CI launches with each container
- [ ] CI correctly identifies all services
- [ ] Health monitoring works
- [ ] Can communicate via aish
- [ ] Provides intelligent responses

### Blocked On
- [ ] Waiting for Phase 2 completion

## Phase 4: TektonCore GitHub Reorganization [0% Complete]

### Tasks
- [ ] Move Analyzer from Ergon to TektonCore
- [ ] Combine Analyzer with Create New Project
- [ ] Create unified GitHub management interface
- [ ] Add modal dialog for project creation
- [ ] Pre-fill project data from analysis
- [ ] Remove GitHub components from Ergon
- [ ] Update navigation and menus
- [ ] Test GitHub workflow end-to-end

### Success Criteria
- [ ] Analyzer works in TektonCore
- [ ] Modal shows pre-filled data
- [ ] GitHub operations consolidated
- [ ] No GitHub UI in Ergon
- [ ] Workflow is intuitive

### Blocked On
- [ ] Casey's design approval needed

## Phase 5: Container Management UI [0% Complete]

### Tasks
- [ ] Create container list view in Ergon
- [ ] Add container launch dialog with configuration
- [ ] Implement port mapping interface
- [ ] Add environment variable management
- [ ] Create volume mount configuration
- [ ] Add container logs viewer
- [ ] Implement start/stop/restart controls
- [ ] Add resource limit configuration
- [ ] Create container status indicators

### Success Criteria
- [ ] All containers visible in UI
- [ ] Can launch with full configuration
- [ ] Logs stream in real-time
- [ ] Status updates live
- [ ] Controls work reliably

### Blocked On
- [ ] Waiting for Phase 3 completion

## Phase 6: Hermes Monitoring Integration [0% Complete]

### Tasks
- [ ] Create `/Hermes/hermes/docker/monitor.py` module
- [ ] Implement container registration with Hermes
- [ ] Add health check monitoring
- [ ] Create metrics collection system
- [ ] Add container event listeners
- [ ] Implement alert system for container issues
- [ ] Store container metrics in database
- [ ] Add cleanup for stopped containers

### Success Criteria
- [ ] Hermes tracks all containers
- [ ] Health checks run periodically
- [ ] Metrics stored and accessible
- [ ] Alerts work for issues
- [ ] Automatic cleanup works

### Blocked On
- [ ] Waiting for Phase 5 completion

## Phase 7: Status & aish Integration [0% Complete]

### Tasks
- [ ] Enhance `tekton status` to show containers
- [ ] Add Docker section to status output
- [ ] Create aish container-ci communication protocol
- [ ] Add container debugging commands
- [ ] Implement container optimization commands
- [ ] Add log analysis capabilities
- [ ] Create container CI directory listing
- [ ] Test all aish interactions

### Success Criteria
- [ ] Status shows all containers
- [ ] Can talk to any container CI
- [ ] Debugging commands work
- [ ] Log analysis provides insights
- [ ] CI directory is accurate

### Blocked On
- [ ] Waiting for Phase 6 completion

## Technical Decisions

### Container CI Architecture
```python
class ContainerCI:
    """Intelligent consciousness for a Docker container"""
    
    def __init__(self, container_id, project_name):
        self.container_id = container_id
        self.name = f"{project_name}-container-ci"
        self.socket_path = f"/tmp/ci_{container_id}.sock"
        
    async def analyze_contents(self):
        """Understand what's running inside"""
        # Process detection
        # Service identification
        # Resource analysis
        
    async def optimize(self):
        """Self-optimization capabilities"""
        # Memory management
        # Cache clearing
        # Service restart
```

### Docker Menu Structure
```
Ergon
└── Docker
    ├── Images
    │   ├── Build
    │   ├── Push
    │   └── Manage
    ├── Containers
    │   ├── Running
    │   ├── Launch
    │   └── Logs
    ├── Networks
    └── Volumes
```

### Registry Schema Extension
```python
docker_config = {
    "dockerfile_path": str,
    "base_image": str,
    "exposed_ports": [int],
    "environment": dict,
    "build_args": dict,
    "container_ci": {
        "enabled": bool,
        "socket": str,
        "capabilities": [str]
    }
}
```

## Out of Scope
- Kubernetes orchestration
- Docker Swarm management
- Complex networking (overlay, macvlan)
- Docker Compose full support (future sprint)
- Production deployment automation (future sprint)

## Files to Update
```
# TektonCore
/tekton-core/tekton/api/docker.py (new)
/tekton-core/tekton/core/project_manager.py
/Hephaestus/ui/components/tekton/tekton-component.html

# Ergon
/Ergon/ergon/docker/ (new directory)
/Ergon/ergon/docker/manager.py (new)
/Ergon/ergon/docker/registry.py (new)
/Ergon/ergon/models/solution.py
/Hephaestus/ui/components/ergon/ergon-component.html

# Container CI
/shared/container_ci/ (new directory)
/shared/container_ci/container_ci.py (new)
/shared/container_ci/health_monitor.py (new)
/shared/container_ci/optimizer.py (new)

# Hermes
/Hermes/hermes/docker/ (new directory)
/Hermes/hermes/docker/monitor.py (new)

# Scripts
/scripts/tekton-status
/shared/aish/src/registry/ci_registry.py
```

## Container CI Capabilities
- Process tree analysis
- Service health monitoring
- Resource optimization
- Log aggregation
- Performance profiling
- Security scanning
- Debugging assistance
- Multi-service coordination

## Success Metrics
- [ ] All Docker operations available through UI
- [ ] Container CIs provide meaningful assistance
- [ ] Integration seamless with existing workflow
- [ ] No manual Docker commands needed
- [ ] Containers self-manage effectively