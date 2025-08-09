# Handoff Document - Ergon Docker Sprint

## Current Status
**Sprint Phase**: Planning Complete
**Ready to Start**: Phase 1 - TektonCore Docker Button

## Container CI Concept Summary
Each Docker container gets an intelligent CI that acts as its "consciousness" - understanding what's running inside, optimizing resources, and providing debugging assistance. This is a paradigm shift from application-level CIs to container-level intelligence.

## Next Session Should Start With

### Phase 1: TektonCore Docker Button

#### 1. Add Button to Project Cards
```javascript
// In tekton-component.html, add to project card actions
<button onclick="generateDockerImage('${project.id}')" 
        class="tekton__project-action-btn"
        title="Generate Docker image">
    🐳 Docker
</button>

async function generateDockerImage(projectId) {
    const project = projects.find(p => p.id === projectId);
    
    // Ask project's CI to analyze and generate Dockerfile
    const response = await fetch(tektonUrl('tekton-core', `/api/projects/${projectId}/docker/generate`), {
        method: 'POST'
    });
    
    const result = await response.json();
    
    // Show Dockerfile in modal with option to send to Ergon
    showDockerfileModal(result.dockerfile, projectId);
}
```

#### 2. Create Docker API Endpoint
```python
# /tekton-core/tekton/api/docker.py
from fastapi import APIRouter, HTTPException
from ..core.project_manager import project_manager

router = APIRouter(prefix="/api/projects/{project_id}/docker")

@router.post("/generate")
async def generate_dockerfile(project_id: str):
    """Generate Dockerfile using project's CI"""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    
    # Use project's CI to analyze codebase
    ci_analysis = await analyze_project_for_docker(project)
    
    # Generate appropriate Dockerfile
    dockerfile = generate_dockerfile_from_analysis(ci_analysis)
    
    # Save to project
    save_dockerfile(project, dockerfile)
    
    # Register with Ergon
    await register_with_ergon(project, dockerfile)
    
    return {
        "dockerfile": dockerfile,
        "analysis": ci_analysis,
        "ergon_registered": True
    }
```

#### 3. Dockerfile Generation Logic
```python
async def analyze_project_for_docker(project):
    """Use project CI to understand the project"""
    
    # Ask CI to analyze
    prompt = """Analyze this project and tell me:
    1. Primary language/framework
    2. Dependencies/requirements files
    3. Build commands
    4. Run commands
    5. Required ports
    6. Environment variables needed
    """
    
    analysis = await project.ci.send(prompt)
    return parse_ci_analysis(analysis)

def generate_dockerfile_from_analysis(analysis):
    """Generate optimized Dockerfile"""
    
    if analysis['framework'] == 'fastapi':
        return generate_fastapi_dockerfile(analysis)
    elif analysis['framework'] == 'django':
        return generate_django_dockerfile(analysis)
    elif analysis['framework'] == 'node':
        return generate_node_dockerfile(analysis)
    # etc...
```

### Phase 2 Preparation: Ergon Docker Structure

#### Docker Module Structure
```
/Ergon/ergon/docker/
├── __init__.py
├── manager.py       # Docker operations manager
├── registry.py      # Docker solution registry
├── builder.py       # Image building logic
├── runner.py        # Container running logic
└── container_ci.py  # Container CI creation
```

#### Ergon UI Docker Menu
```html
<!-- In ergon-component.html -->
<div class="ergon__menu-item" onclick="showDockerMenu()">
    <span class="icon">🐳</span> Docker
</div>

<div id="docker-submenu" class="ergon__submenu">
    <div onclick="showDockerImages()">Images</div>
    <div onclick="showDockerContainers()">Containers</div>
    <div onclick="showDockerNetworks()">Networks</div>
    <div onclick="showDockerVolumes()">Volumes</div>
</div>
```

## Container CI Implementation Guide

### Core Container CI Class
```python
# /shared/container_ci/container_ci.py
import asyncio
import docker
import psutil
from typing import Dict, List, Any

class ContainerCI:
    """Intelligent consciousness for a Docker container"""
    
    def __init__(self, container_id: str, project_name: str):
        self.container_id = container_id
        self.name = f"{project_name}-container-ci"
        self.docker_client = docker.from_env()
        self.container = self.docker_client.containers.get(container_id)
        self.socket_path = f"/tmp/ci_{container_id}.sock"
        self.services = {}
        self.health_status = {}
        
    async def initialize(self):
        """Start monitoring and register with aish"""
        await self.discover_services()
        await self.register_with_aish()
        await self.start_health_monitoring()
        
    async def discover_services(self):
        """Understand what's running in the container"""
        # Get process list
        processes = self.container.exec_run("ps aux").output.decode()
        
        # Detect common services
        if "python.*fastapi" in processes:
            self.services['web'] = {
                'type': 'fastapi',
                'port': self.find_port('uvicorn'),
                'status': 'running'
            }
        
        if "redis-server" in processes:
            self.services['cache'] = {
                'type': 'redis',
                'port': 6379,
                'status': 'running'
            }
        
        if "postgres" in processes:
            self.services['database'] = {
                'type': 'postgresql',
                'port': 5432,
                'status': 'running'
            }
        
        return self.services
    
    async def handle_query(self, query: str) -> str:
        """Respond to user queries about the container"""
        
        if "status" in query.lower():
            return self.get_status_report()
        
        if "optimize" in query.lower():
            return await self.optimize_container()
        
        if "debug" in query.lower():
            return await self.debug_issues()
        
        if "logs" in query.lower():
            return self.get_relevant_logs()
        
        # Use AI for complex queries
        return await self.ai_analysis(query)
```

### Container CI Registration
```python
# When Ergon launches a container
async def launch_container(solution_id: str, config: dict):
    """Launch container with Container CI"""
    
    # Start container
    container = docker_client.containers.run(
        image=config['image'],
        detach=True,
        ports=config['ports'],
        environment=config['environment'],
        volumes=config['volumes']
    )
    
    # Create Container CI
    container_ci = ContainerCI(
        container_id=container.id,
        project_name=config['project_name']
    )
    await container_ci.initialize()
    
    # Register with aish for communication
    from shared.aish.src.registry.ci_registry import get_registry
    registry = get_registry()
    registry.register_wrapped_ci({
        'name': container_ci.name,
        'type': 'container',
        'socket': container_ci.socket_path,
        'container_id': container.id,
        'capabilities': ['monitoring', 'optimization', 'debugging'],
        'pid': container.attrs['State']['Pid']
    })
    
    return container_ci
```

## Testing Strategy

### Phase 1 Tests
1. Generate Dockerfile for Python project
2. Generate Dockerfile for Node project
3. Verify Dockerfile saves to project
4. Verify Ergon registration

### Phase 2 Tests
1. Build image through UI
2. List images in registry
3. Tag management works
4. Multi-stage builds work

### Phase 3 Tests
1. Container CI launches with container
2. Service detection accurate
3. aish communication works
4. Health monitoring functions

## Key Design Decisions

### Why Container CIs?
- **Encapsulation**: Intelligence travels with container
- **Self-Management**: Containers can optimize themselves
- **Debugging**: Immediate, context-aware help
- **Scalability**: CIs manage replicas automatically

### Technology Choices
- **Docker SDK for Python**: Direct Docker API access
- **Unix sockets**: For CI communication
- **FastAPI**: For Docker API endpoints
- **asyncio**: For concurrent operations

## Common Pitfalls to Avoid
1. Don't hardcode Docker socket path (/var/run/docker.sock)
2. Handle Docker daemon not running gracefully
3. Clean up containers and CIs on shutdown
4. Don't assume specific ports are available
5. Handle multi-platform images (AMD64/ARM64)

## Definition of Done
- [ ] Docker button generates appropriate Dockerfiles
- [ ] Container CIs provide intelligent assistance
- [ ] Ergon manages full Docker lifecycle
- [ ] Status command shows all containers
- [ ] aish can communicate with any Container CI
- [ ] Documentation updated
- [ ] Tests pass
- [ ] Casey approves implementation