# Handoff Document - Ergon DevOps Sprint

## Current Status
**Sprint Phase**: Planning Complete
**Ready to Start**: Phase 1 - TektonCore Docker Button
**Stop Point**: After Phase 3 completion

## Sprint Overview
This sprint implements Docker support in three immediate phases, with two future phases defined but not implemented. The focus is on Container CIs (novel) and JSON manifests (foundational) without overbuilding.

## Phase 1: Docker Button Implementation

### Immediate Tasks
1. Add Docker button to project cards in `tekton-component.html`
2. Create `/tekton-core/tekton/api/docker.py` endpoint
3. Implement Dockerfile generation using project CI

### Implementation Guide

#### 1. UI Button Addition
```javascript
// In tekton-component.html project card section
<button onclick="generateDockerImage('${project.id}')" 
        class="tekton__project-action-btn"
        title="Generate Dockerfile for project">
    🐳 Docker
</button>

async function generateDockerImage(projectId) {
    // Show loading
    const button = event.target;
    button.disabled = true;
    button.textContent = "Generating...";
    
    try {
        const response = await fetch(
            tektonUrl('tekton-core', `/api/projects/${projectId}/docker/generate`),
            { method: 'POST' }
        );
        
        const result = await response.json();
        
        // Show Dockerfile in modal
        showDockerfileModal(result);
    } finally {
        button.disabled = false;
        button.textContent = "🐳 Docker";
    }
}

function showDockerfileModal(result) {
    const modal = TektonModal.show({
        title: "Generated Dockerfile",
        content: `<pre>${result.dockerfile}</pre>`,
        buttons: [
            { text: "Save to Project", action: () => saveDockerfile(result) },
            { text: "Send to Ergon", action: () => sendToErgon(result) },
            { text: "Close" }
        ]
    });
}
```

#### 2. API Endpoint
```python
# /tekton-core/tekton/api/docker.py
from fastapi import APIRouter, HTTPException
from ..core.project_manager import project_manager

router = APIRouter(prefix="/api/projects/{project_id}/docker")

@router.post("/generate")
async def generate_dockerfile(project_id: str):
    """Generate Dockerfile using project's CI analysis"""
    
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    
    # Use project CI to analyze
    analysis_prompt = """
    Analyze this project and provide:
    1. Primary language and framework
    2. Required dependencies
    3. Build commands
    4. Runtime commands
    5. Required ports
    6. Environment variables
    """
    
    ci_response = await project.companion_intelligence.send(analysis_prompt)
    
    # Generate Dockerfile based on analysis
    dockerfile = generate_dockerfile_from_analysis(ci_response)
    
    # Save to project
    save_path = f"{project.local_directory}/Dockerfile"
    with open(save_path, 'w') as f:
        f.write(dockerfile)
    
    return {
        "dockerfile": dockerfile,
        "project_id": project_id,
        "project_name": project.name,
        "saved_to": save_path
    }
```

## Phase 2: Container CI Implementation

### Core Container CI Class
```python
# /shared/container_ci/container_ci.py
import asyncio
import docker
import socket
import json
from typing import Dict, List

class ContainerCI:
    """Intelligent consciousness for a Docker container"""
    
    def __init__(self, container_id: str, name: str):
        self.container_id = container_id
        self.name = name
        self.docker_client = docker.from_env()
        self.container = self.docker_client.containers.get(container_id)
        self.socket_path = f"/tmp/ci_{container_id[:12]}.sock"
        self.services = {}
        
    async def initialize(self):
        """Start the Container CI"""
        await self.discover_services()
        await self.register_with_aish()
        await self.start_socket_listener()
        
    async def discover_services(self):
        """Understand what's running in the container"""
        # Execute ps command in container
        result = self.container.exec_run("ps aux")
        processes = result.output.decode('utf-8')
        
        # Detect common services
        if 'nginx' in processes:
            self.services['web_server'] = 'nginx'
        if 'python' in processes and 'uvicorn' in processes:
            self.services['api'] = 'fastapi'
        if 'node' in processes:
            self.services['app'] = 'nodejs'
        if 'postgres' in processes:
            self.services['database'] = 'postgresql'
        if 'redis-server' in processes:
            self.services['cache'] = 'redis'
            
        return self.services
    
    async def handle_message(self, message: str) -> str:
        """Respond to queries about the container"""
        
        if "status" in message.lower():
            return self.get_status()
        elif "optimize" in message.lower():
            return await self.optimize()
        elif "services" in message.lower():
            return f"Running services: {', '.join(self.services.values())}"
        elif "health" in message.lower():
            return self.check_health()
        else:
            return f"Container {self.name} is running. Ask about status, services, or health."
    
    def get_status(self) -> str:
        """Get container status"""
        stats = self.container.stats(stream=False)
        memory_usage = stats['memory_stats']['usage'] / (1024*1024)  # MB
        
        return f"""Container Status:
        - ID: {self.container_id[:12]}
        - Status: {self.container.status}
        - Services: {', '.join(self.services.values())}
        - Memory: {memory_usage:.1f}MB
        - Uptime: {self.get_uptime()}"""
    
    async def optimize(self) -> str:
        """Optimize container resources"""
        optimizations = []
        
        # Clear caches if Redis present
        if 'redis' in self.services.values():
            self.container.exec_run("redis-cli FLUSHDB")
            optimizations.append("Cleared Redis cache")
        
        # Restart workers if present
        if 'worker' in str(self.services):
            self.container.exec_run("supervisorctl restart all")
            optimizations.append("Restarted workers")
        
        return f"Optimizations performed: {', '.join(optimizations)}" if optimizations else "No optimizations needed"
```

### Registration with aish
```python
async def register_with_aish(self):
    """Register this Container CI with aish"""
    from shared.aish.src.registry.ci_registry import get_registry
    
    registry = get_registry()
    registry.register_wrapped_ci({
        'name': self.name,
        'type': 'container',
        'socket': self.socket_path,
        'container_id': self.container_id,
        'capabilities': ['status', 'optimize', 'debug', 'monitor'],
        'pid': os.getpid()
    })
```

## Phase 3: JSON Manifest System

### Manifest Structure
```json
{
  "manifest_version": "1.0",
  "project": {
    "name": "example-api",
    "repository": "github.com/company/api"
  },
  "applications": {
    "api-service": {
      "type": "fastapi",
      "language": "python",
      "entrypoint": "main.py",
      "dependencies": "requirements.txt",
      "build_commands": ["pip install -r requirements.txt"],
      "run_command": "uvicorn main:app --host 0.0.0.0"
    }
  },
  "containers": {
    "api-container": {
      "base_image": "python:3.11-slim",
      "applications": ["api-service"],
      "ports": [8000],
      "ci_name": "api-ci",
      "ci_capabilities": ["monitor", "optimize", "debug"]
    }
  },
  "packaging": {
    "build_order": ["api-container"],
    "registry": "docker.io/company",
    "tagging": "git-sha"
  }
}
```

### Deterministic Packager
```python
# /Ergon/ergon/packager/deterministic_packager.py
import json
import hashlib
from typing import Dict

class DeterministicPackager:
    """Ensures same manifest always produces same container"""
    
    def __init__(self, manifest_path: str):
        with open(manifest_path) as f:
            self.manifest = json.load(f)
        self.build_hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Deterministic hash of build specification"""
        # Sort keys for consistent ordering
        canonical = json.dumps(self.manifest, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()
    
    def package_application(self, app_name: str) -> Dict:
        """Package application with deterministic identity"""
        app = self.manifest['applications'][app_name]
        
        return {
            'name': app_name,
            'hash': self.build_hash,
            'full_id': f"{app_name}:{self.build_hash[:12]}",
            'manifest': app
        }
    
    def build_container(self, container_name: str):
        """Build container deterministically"""
        container = self.manifest['containers'][container_name]
        
        # Generate Dockerfile
        dockerfile = self.generate_dockerfile(container)
        
        # Build with consistent tags
        image_tag = f"{container_name}:{self.build_hash[:12]}"
        
        # Build image
        import docker
        client = docker.from_env()
        image = client.images.build(
            path=".",
            dockerfile=dockerfile,
            tag=image_tag,
            rm=True,  # Remove intermediate containers
            forcerm=True  # Always remove
        )
        
        return image_tag
```

## Testing Instructions

### Phase 1 Test
1. Click Docker button on any project
2. Verify Dockerfile generates correctly
3. Check that file saves to project
4. Test "Send to Ergon" option

### Phase 2 Test
```bash
# Start a container
docker run -d --name test-app your-image

# Launch Container CI
python /shared/container_ci/launcher.py --container test-app --name test-app-ci

# Test communication
aish test-app-ci "What's your status?"
```

### Phase 3 Test
1. Generate manifest for a project
2. Run packager with same manifest twice
3. Verify identical hash produced
4. Check Ergon registry has entry

## Definition of Done - Phase 1-3

- [ ] Docker button generates appropriate Dockerfiles
- [ ] Container CIs launch and communicate
- [ ] JSON manifests produce deterministic builds
- [ ] All three phases integrate cleanly
- [ ] Documentation updated
- [ ] Casey approves before moving to Phase 4

## Important Notes

### The Casey Method
- JSON cookbooks (proven since 2007)
- Bottom-up deployment
- Deterministic execution
- Simple > Complex

### Stop Point After Phase 3
- Evaluate what we've built
- Rest and think
- Decide if Phase 4-5 needed
- Don't overbuild

### Future Phases (4-5) Overview
**Phase 4**: Sites, Stages, Lifecycle (2025)
**Phase 5**: Federated Tekton Stacks (2026)

These are defined but NOT to be implemented now. The foundation from Phases 1-3 enables them when needed.

## Next Session Should
1. Start with Phase 1 Docker button
2. Test with multiple project types
3. Move to Phase 2 only when Phase 1 complete
4. Keep it simple - don't add extra features