"""
TektonCore Integration Module for Ergon Registry.

Monitors TektonCore for completed projects and automatically imports them
into the Ergon Registry with full metadata extraction.
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import httpx
import sys

# Add parent directory for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from shared.env import TektonEnviron

# Import landmarks with fallback for environments without landmarks
try:
    from landmarks import (
        architecture_decision,
        integration_point,
        performance_boundary,
        danger_zone
    )
except ImportError:
    # Define no-op decorators when landmarks not available
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def danger_zone(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

# Setup logging
logger = logging.getLogger(__name__)

# TektonCore API endpoint (using environment-aware configuration)
TEKTON_CORE_PORT = int(TektonEnviron.get('TEKTON_CORE_PORT', '8110'))
TEKTON_CORE_URL = f"http://localhost:{TEKTON_CORE_PORT}"


@architecture_decision(
    title="TektonCore Monitoring Architecture",
    description="Background service that monitors TektonCore for completed projects",
    rationale="Automatic import ensures Registry stays current without manual intervention",
    alternatives_considered=["Webhook-based notifications", "Manual import only", "Batch scheduled imports"],
    impacts=["registry_population", "resource_usage", "data_consistency"],
    decided_by="Casey",
    decision_date="2025-08-22"
)
class TektonCoreMonitor:
    """Monitor TektonCore for completed projects and import to Registry."""
    
    def __init__(self, registry_url: str = None, check_interval: int = 60):
        """
        Initialize the TektonCore monitor.
        
        Args:
            registry_url: URL of the Ergon Registry API
            check_interval: Seconds between completion checks
        """
        self.registry_url = registry_url or f"http://localhost:{TektonEnviron.get('ERGON_PORT', '8102')}/api/ergon/registry"
        self.check_interval = check_interval
        self.processed_projects = set()  # Track what we've already imported
        self._running = False
        
    async def start(self):
        """Start monitoring TektonCore for completed projects."""
        self._running = True
        logger.info("Started TektonCore monitoring")
        
        while self._running:
            try:
                await self.check_for_completed_projects()
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            await asyncio.sleep(self.check_interval)
    
    def stop(self):
        """Stop monitoring."""
        self._running = False
        logger.info("Stopped TektonCore monitoring")
    
    @danger_zone(
        title="Duplicate Import Prevention",
        description="Tracks processed projects to prevent duplicate Registry entries",
        risk_level="medium",
        risks=["duplicate_entries", "missed_projects", "memory_growth"],
        mitigation="In-memory set tracking with project IDs, consider persistent storage for production",
        review_required=True
    )
    async def check_for_completed_projects(self):
        """Check TektonCore for newly completed projects."""
        try:
            completed = await monitor_completed_projects()
            
            for project in completed:
                project_id = project.get('id')
                
                # Skip if we've already processed this project
                if project_id in self.processed_projects:
                    continue
                
                # Extract metadata and create Registry entry
                metadata = await extract_sprint_metadata(project)
                if metadata:
                    entry = prepare_registry_entry(project, metadata)
                    
                    # Submit to Registry
                    if await self.submit_to_registry(entry):
                        self.processed_projects.add(project_id)
                        logger.info(f"Imported project {project_id} to Registry")
                    
        except Exception as e:
            logger.error(f"Error checking completed projects: {e}")
    
    async def submit_to_registry(self, entry: Dict[str, Any]) -> bool:
        """
        Submit an entry to the Registry.
        
        Args:
            entry: Registry entry to submit
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.registry_url}/store",
                    json=entry
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to submit to Registry: {e}")
            return False


@integration_point(
    title="TektonCore Project Query",
    description="Queries TektonCore API for completed projects",
    target_component="TektonCore",
    protocol="REST API",
    data_flow="Ergon → TektonCore /api/projects → filter status=Complete → return list",
    integration_date="2025-08-22"
)
async def monitor_completed_projects() -> List[Dict[str, Any]]:
    """
    Query TektonCore for completed projects.
    
    Returns:
        List of completed project dictionaries
    """
    try:
        async with httpx.AsyncClient() as client:
            # Query TektonCore projects endpoint
            response = await client.get(
                f"{TEKTON_CORE_URL}/api/projects",
                params={"status": "Complete"}
            )
            
            if response.status_code == 200:
                data = response.json()
                # Return list of completed projects
                projects = data.get('projects', [])
                return [p for p in projects if p.get('status') == 'Complete']
            else:
                logger.warning(f"Failed to query TektonCore: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"Error querying TektonCore: {e}")
        return []


@performance_boundary(
    title="Sprint Metadata Extraction",
    description="Extracts metadata from sprint documents (proposal.json, SPRINT_PLAN.md)",
    sla="<500ms per sprint directory",
    optimization_notes="File I/O intensive - consider caching for repeated access",
    measured_impact="Processes typical sprint in ~100ms"
)
async def extract_sprint_metadata(project: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract metadata from development sprint documents.
    
    Args:
        project: TektonCore project dictionary
        
    Returns:
        Extracted metadata dictionary or None if extraction fails
    """
    metadata = {
        'project_id': project.get('id'),
        'project_name': project.get('name'),
        'completion_date': project.get('completion_date'),
        'sprints': []
    }
    
    # Get sprint directory from project
    sprint_dir = project.get('sprint_directory')
    if not sprint_dir:
        # Try to construct from project info
        project_name = project.get('name', '')
        if project_name:
            # Look in MetaData/DevelopmentSprints/
            base_path = Path(TektonEnviron.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Coder-A'))
            sprint_dir = base_path / 'MetaData' / 'DevelopmentSprints' / f"{project_name}_Sprint"
    
    if sprint_dir and Path(sprint_dir).exists():
        # Extract from proposal.json
        proposal_path = Path(sprint_dir) / 'proposal.json'
        if proposal_path.exists():
            try:
                with open(proposal_path, 'r') as f:
                    proposal = json.load(f)
                    metadata['title'] = proposal.get('title', '').strip()
                    metadata['description'] = proposal.get('description', '').strip()
                    metadata['status'] = proposal.get('status', 'unknown')
            except Exception as e:
                logger.error(f"Failed to read proposal.json: {e}")
        
        # Extract from SPRINT_PLAN.md
        sprint_plan_path = Path(sprint_dir) / 'SPRINT_PLAN.md'
        if sprint_plan_path.exists():
            try:
                with open(sprint_plan_path, 'r') as f:
                    content = f.read()
                    # Extract key sections
                    metadata['has_sprint_plan'] = True
                    
                    # Look for Goals section
                    if '## Goals' in content:
                        goals_section = content.split('## Goals')[1].split('##')[0]
                        goals = [line.strip('- ').strip() for line in goals_section.split('\n') 
                                if line.strip().startswith('-')]
                        metadata['goals'] = goals[:5]  # First 5 goals
                    
                    # Look for Success Criteria
                    if '## Success Criteria' in content or '### Success Criteria' in content:
                        metadata['has_success_criteria'] = True
                    
                    # Check for completion status
                    if '[100% Complete]' in content or '✅' in content:
                        metadata['has_completed_tasks'] = True
                        
            except Exception as e:
                logger.error(f"Failed to read SPRINT_PLAN.md: {e}")
        
        # Look for solution files
        metadata['solution_files'] = []
        for pattern in ['*.py', '*.js', '*.ts', '*.go', '*.rs']:
            files = list(Path(sprint_dir).glob(pattern))
            metadata['solution_files'].extend([str(f.relative_to(sprint_dir)) for f in files])
    
    return metadata if metadata.get('title') or metadata.get('project_name') else None


@integration_point(
    title="Registry Entry Preparation",
    description="Transforms TektonCore project data into Registry-compatible format",
    target_component="Ergon Registry",
    protocol="internal_api",
    data_flow="TektonCore data → type detection → tag generation → Registry entry",
    integration_date="2025-08-22"
)
def prepare_registry_entry(project: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare a Registry entry from project and metadata.
    
    Args:
        project: TektonCore project dictionary
        metadata: Extracted metadata
        
    Returns:
        Registry-compatible entry dictionary
    """
    # Determine solution type based on metadata
    solution_type = "solution"  # Default
    if metadata.get('solution_files'):
        if any(f.endswith('.Dockerfile') for f in metadata['solution_files']):
            solution_type = "container"
        elif any(f.endswith('.yaml') or f.endswith('.yml') for f in metadata['solution_files']):
            solution_type = "config"
        elif any(f.endswith('.sh') or f.endswith('.bash') for f in metadata['solution_files']):
            solution_type = "tool"
    
    # Build Registry entry
    entry = {
        'type': solution_type,
        'name': metadata.get('title') or metadata.get('project_name') or 'Unnamed Solution',
        'version': '1.0.0',  # Default version, could extract from project
        'description': metadata.get('description', ''),
        'meets_standards': False,  # Will be checked after import
        'lineage': [],  # No parent for auto-imported solutions
        'source': {
            'project_id': project.get('id'),
            'sprint_id': f"{project.get('name')}_Sprint",
            'location': str(project.get('sprint_directory', ''))
        },
        'content': {
            'goals': metadata.get('goals', []),
            'files': metadata.get('solution_files', []),
            'has_sprint_plan': metadata.get('has_sprint_plan', False),
            'has_success_criteria': metadata.get('has_success_criteria', False),
            'has_completed_tasks': metadata.get('has_completed_tasks', False),
            'completion_date': metadata.get('completion_date'),
            'metadata': metadata  # Store full metadata for reference
        },
        'tags': []
    }
    
    # Auto-generate tags
    tags = []
    if solution_type:
        tags.append(solution_type)
    if project.get('name'):
        tags.append(project['name'].lower().replace('_', '-'))
    if metadata.get('has_completed_tasks'):
        tags.append('completed')
    if metadata.get('status') == 'sprint':
        tags.append('sprint')
    
    entry['tags'] = tags
    
    return entry


async def import_completed_project(project_id: str) -> Optional[str]:
    """
    Import a specific completed project to the Registry.
    
    Args:
        project_id: ID of the TektonCore project to import
        
    Returns:
        Registry entry ID if successful, None otherwise
    """
    try:
        # Get project details from TektonCore
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{TEKTON_CORE_URL}/api/projects/{project_id}")
            
            if response.status_code != 200:
                logger.error(f"Failed to get project {project_id}")
                return None
            
            project = response.json()
            
            # Extract metadata
            metadata = await extract_sprint_metadata(project)
            if not metadata:
                logger.warning(f"No metadata extracted for project {project_id}")
                return None
            
            # Prepare Registry entry
            entry = prepare_registry_entry(project, metadata)
            
            # Submit to Registry
            registry_url = f"http://localhost:{TektonEnviron.get('ERGON_PORT', '8102')}/api/ergon/registry"
            response = await client.post(f"{registry_url}/store", json=entry)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('id')
            else:
                logger.error(f"Failed to store in Registry: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Error importing project {project_id}: {e}")
        return None


# Convenience function for manual testing
async def test_import():
    """Test importing completed projects from TektonCore."""
    logger.info("Testing TektonCore import...")
    
    # Get completed projects
    projects = await monitor_completed_projects()
    logger.info(f"Found {len(projects)} completed projects")
    
    for project in projects[:1]:  # Test with first project only
        logger.info(f"Testing with project: {project.get('name')}")
        
        # Extract metadata
        metadata = await extract_sprint_metadata(project)
        if metadata:
            logger.info(f"Extracted metadata: {json.dumps(metadata, indent=2)}")
            
            # Prepare entry
            entry = prepare_registry_entry(project, metadata)
            logger.info(f"Prepared entry: {json.dumps(entry, indent=2)}")
        else:
            logger.warning("No metadata extracted")


if __name__ == "__main__":
    # Test the import functionality
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_import())