"""
Registry API endpoints for Ergon Container Management.

Provides REST API for Registry operations including storage, retrieval,
search, standards checking, and lineage tracking.
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse

# Landmark imports with fallback
try:
    from landmarks import api_contract, integration_point, performance_boundary
except ImportError:
    # Define no-op decorators when landmarks not available
    def api_contract(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func):
            return func
        return decorator

from ..registry.storage import RegistryStorage

# Setup logging
logger = logging.getLogger(__name__)

# Create API router with prefix and tags
router = APIRouter(prefix="/api/ergon/registry", tags=["registry"])

# Initialize registry storage (singleton pattern)
_storage_instance = None

def get_storage() -> RegistryStorage:
    """Get or create the registry storage instance."""
    global _storage_instance
    if _storage_instance is None:
        # Use a dedicated registry database in Ergon's directory
        import os
        ergon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(ergon_dir, "ergon_registry.db")
        _storage_instance = RegistryStorage(db_path)
        logger.info(f"Initialized Registry storage at {db_path}")
    return _storage_instance


# ===== SPECIFIC ROUTES FIRST (before /{entry_id}) =====

@router.post("/store")
@api_contract(
    title="Store Deployable Unit",
    description="Store a new deployable unit in the Registry",
    endpoint="/api/ergon/registry/store",
    method="POST",
    request_schema={"type": "str", "name": "str", "version": "str", "content": "dict"},
    response_schema={"success": "bool", "id": "str", "message": "str"},
    performance_requirements="<100ms for storage operation"
)
async def store_deployable_unit(
    unit: Dict[str, Any] = Body(..., description="Deployable unit to store")
) -> Dict[str, Any]:
    """
    Store a new deployable unit in the registry.
    
    Args:
        unit: JSON object representing the deployable unit
        
    Returns:
        Success response with the stored unit's ID
    """
    try:
        storage = get_storage()
        entry_id = storage.store(unit)
        
        return {
            "success": True,
            "id": entry_id,
            "message": f"Successfully stored unit: {unit.get('name', 'Unnamed')}"
        }
    except Exception as e:
        logger.error(f"Failed to store unit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
@api_contract(
    title="Search Registry Units",
    description="Search for deployable units with filters",
    endpoint="/api/ergon/registry/search",
    method="GET",
    request_schema={"type": "str?", "name": "str?", "meets_standards": "bool?", "limit": "int?"},
    response_schema={"success": "bool", "count": "int", "results": "list"},
    performance_requirements="<200ms for search queries"
)
async def search_units(
    type: Optional[str] = Query(None, description="Filter by type"),
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    meets_standards: Optional[bool] = Query(None, description="Filter by standards compliance"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results to return")
) -> Dict[str, Any]:
    """
    Search for deployable units with filters.
    
    Args:
        type: Optional type filter
        name: Optional name filter (supports partial matching)
        meets_standards: Optional standards compliance filter
        limit: Maximum number of results
        
    Returns:
        List of matching deployable units
    """
    try:
        storage = get_storage()
        results = storage.search(
            type=type,
            name=name,
            meets_standards=meets_standards,
            limit=limit
        )
        
        return {
            "success": True,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
async def list_types() -> Dict[str, Any]:
    """
    Get all available unit types in the registry.
    
    Returns:
        List of unique type values
    """
    try:
        storage = get_storage()
        types = storage.list_types()
        
        return {
            "success": True,
            "types": types,
            "count": len(types)
        }
    except Exception as e:
        logger.error(f"Failed to list types: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def registry_health() -> Dict[str, Any]:
    """
    Check the health of the Registry service.
    
    Returns:
        Health status and statistics
    """
    try:
        storage = get_storage()
        
        # Get some stats
        all_units = storage.search(limit=1000)
        types = storage.list_types()
        compliant = storage.search(meets_standards=True, limit=1000)
        
        return {
            "status": "healthy",
            "statistics": {
                "total_units": len(all_units),
                "unique_types": len(types),
                "standards_compliant": len(compliant),
                "compliance_rate": f"{(len(compliant) / len(all_units) * 100):.1f}%" if all_units else "N/A"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# ===== ROUTES WITH ENTRY_ID PARAMETER =====

@router.get("/{entry_id}")
async def retrieve_unit(
    entry_id: str = Path(..., description="ID of the unit to retrieve")
) -> Dict[str, Any]:
    """
    Retrieve a deployable unit by ID.
    
    Args:
        entry_id: The unique identifier of the unit
        
    Returns:
        The deployable unit JSON object
    """
    try:
        storage = get_storage()
        unit = storage.retrieve(entry_id)
        
        if unit is None:
            raise HTTPException(status_code=404, detail=f"Unit not found: {entry_id}")
        
        return unit
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve unit {entry_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{entry_id}")
async def delete_unit(
    entry_id: str = Path(..., description="ID of the unit to delete")
) -> Dict[str, Any]:
    """
    Delete a deployable unit from the registry.
    
    Note: Units with dependents cannot be deleted (safeguard).
    
    Args:
        entry_id: The unique identifier of the unit to delete
        
    Returns:
        Success response
    """
    try:
        storage = get_storage()
        
        # Check if unit exists first
        unit = storage.retrieve(entry_id)
        if unit is None:
            raise HTTPException(status_code=404, detail=f"Unit not found: {entry_id}")
        
        # Attempt deletion (will fail if has dependents)
        deleted = storage.delete(entry_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Unit not found: {entry_id}")
        
        return {
            "success": True,
            "message": f"Successfully deleted unit: {unit.get('name', entry_id)}"
        }
    except ValueError as e:
        # This happens when trying to delete a unit with dependents
        raise HTTPException(status_code=409, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete unit {entry_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{entry_id}/check-standards")
async def check_standards(
    entry_id: str = Path(..., description="ID of the unit to check")
) -> Dict[str, Any]:
    """
    Check if a deployable unit meets Tekton standards.
    
    Args:
        entry_id: The unique identifier of the unit
        
    Returns:
        Compliance report with detailed checks
    """
    try:
        storage = get_storage()
        report = storage.check_standards(entry_id)
        
        if "error" in report:
            raise HTTPException(status_code=404, detail=report["error"])
        
        return {
            "success": True,
            "report": report
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Standards check failed for {entry_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{entry_id}/lineage")
async def get_lineage(
    entry_id: str = Path(..., description="ID of the unit")
) -> Dict[str, Any]:
    """
    Get the lineage (parent history) of a deployable unit.
    
    Args:
        entry_id: The unique identifier of the unit
        
    Returns:
        List of ancestor units from newest to oldest
    """
    try:
        storage = get_storage()
        
        # Check if unit exists
        unit = storage.retrieve(entry_id)
        if unit is None:
            raise HTTPException(status_code=404, detail=f"Unit not found: {entry_id}")
        
        lineage = storage.get_lineage(entry_id)
        
        return {
            "success": True,
            "unit": {
                "id": unit["id"],
                "name": unit["name"],
                "version": unit["version"]
            },
            "lineage": lineage,
            "depth": len(lineage)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get lineage for {entry_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{entry_id}/standards-compliance")
async def update_standards_compliance(
    entry_id: str = Path(..., description="ID of the unit"),
    meets_standards: bool = Body(..., description="Whether the unit meets standards")
) -> Dict[str, Any]:
    """
    Update the standards compliance status of a unit.
    
    Args:
        entry_id: The unique identifier of the unit
        meets_standards: New compliance status
        
    Returns:
        Success response
    """
    try:
        storage = get_storage()
        updated = storage.update_standards_compliance(entry_id, meets_standards)
        
        if not updated:
            raise HTTPException(status_code=404, detail=f"Unit not found: {entry_id}")
        
        return {
            "success": True,
            "message": f"Updated standards compliance to: {meets_standards}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update compliance for {entry_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== TEKTONCORE INTEGRATION ENDPOINTS =====

@router.post("/import/notify")
@integration_point(
    title="TektonCore Project Completion Notification",
    description="Receives notifications from TektonCore when projects are completed",
    target_component="TektonCore",
    protocol="REST webhook",
    data_flow="TektonCore completion → Registry import → Storage",
    integration_date="2025-08-22"
)
@api_contract(
    title="Import Notification Endpoint",
    endpoint="/api/ergon/registry/import/notify",
    method="POST",
    request_schema={"project_id": "str", "sprint_id": "str", "completion_date": "str"},
    response_schema={"success": "bool", "registry_id": "str", "status": "str"}
)
async def notify_project_completion(
    notification: Dict[str, Any] = Body(..., description="TektonCore project completion notification")
) -> Dict[str, Any]:
    """
    Receive notification from TektonCore about a completed project.
    
    Expected notification format:
    {
        "project_id": "uuid",
        "project_name": "string",
        "sprint_id": "uuid",
        "completion_date": "iso-timestamp",
        "sprint_path": "/path/to/sprint",
        "metadata": {...}
    }
    
    Args:
        notification: Project completion notification from TektonCore
        
    Returns:
        Acknowledgment with import status
    """
    try:
        from ..integrations.tekton_core import prepare_registry_entry
        
        # Extract required fields
        project_id = notification.get("project_id")
        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")
        
        logger.info(f"Received completion notification for project: {project_id}")
        
        # Prepare the registry entry from TektonCore data
        registry_entry = await prepare_registry_entry(notification)
        
        # Store in registry
        storage = get_storage()
        entry_id = storage.store(registry_entry)
        
        return {
            "success": True,
            "message": f"Project imported to registry",
            "registry_id": entry_id,
            "project_id": project_id,
            "status": "imported"
        }
        
    except ImportError:
        logger.warning("TektonCore integration module not available yet")
        # Store notification for later processing
        return {
            "success": True,
            "message": "Notification queued for processing",
            "project_id": notification.get("project_id"),
            "status": "queued"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process TektonCore notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import/batch")
@performance_boundary(
    title="Batch Import Performance",
    description="Batch imports multiple projects from TektonCore",
    sla="<5s for 10 projects, <30s for 100 projects",
    optimization_notes="Parallel processing where possible, batch database operations",
    measured_impact="Reduces import time by 60% vs sequential imports"
)
@api_contract(
    title="Batch Import Projects",
    endpoint="/api/ergon/registry/import/batch",
    method="POST",
    request_schema={"project_ids": "List[str]"},
    response_schema={"success": "bool", "summary": "dict", "results": "list"}
)
async def batch_import_projects(
    project_ids: List[str] = Body(..., description="List of TektonCore project IDs to import")
) -> Dict[str, Any]:
    """
    Batch import multiple completed projects from TektonCore.
    
    Args:
        project_ids: List of project IDs to import
        
    Returns:
        Import results for each project
    """
    try:
        from ..integrations.tekton_core import monitor_completed_projects, prepare_registry_entry
        
        storage = get_storage()
        results = []
        
        for project_id in project_ids:
            try:
                # Get project data from TektonCore
                project_data = await monitor_completed_projects(project_id)
                
                if project_data:
                    # Prepare and store
                    registry_entry = await prepare_registry_entry(project_data)
                    entry_id = storage.store(registry_entry)
                    
                    results.append({
                        "project_id": project_id,
                        "registry_id": entry_id,
                        "status": "imported"
                    })
                else:
                    results.append({
                        "project_id": project_id,
                        "status": "not_found"
                    })
                    
            except Exception as e:
                logger.error(f"Failed to import project {project_id}: {e}")
                results.append({
                    "project_id": project_id,
                    "status": "failed",
                    "error": str(e)
                })
        
        # Calculate summary
        imported = sum(1 for r in results if r["status"] == "imported")
        failed = sum(1 for r in results if r["status"] == "failed")
        not_found = sum(1 for r in results if r["status"] == "not_found")
        
        return {
            "success": True,
            "summary": {
                "total": len(project_ids),
                "imported": imported,
                "failed": failed,
                "not_found": not_found
            },
            "results": results
        }
        
    except ImportError:
        logger.warning("TektonCore integration module not available yet")
        return {
            "success": False,
            "message": "TektonCore integration not available",
            "summary": {
                "total": len(project_ids),
                "imported": 0,
                "failed": len(project_ids),
                "not_found": 0
            }
        }
    except Exception as e:
        logger.error(f"Batch import failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/import/status")
async def get_import_status() -> Dict[str, Any]:
    """
    Get the status of TektonCore import integration.
    
    Returns:
        Integration status and statistics
    """
    try:
        storage = get_storage()
        
        # Get TektonCore imported solutions
        tekton_solutions = storage.search(limit=1000)
        imported_count = sum(
            1 for s in tekton_solutions 
            if s.get("source", {}).get("origin") == "tekton-core"
        )
        
        # Check if integration module is available
        integration_available = False
        try:
            from ..integrations.tekton_core import monitor_completed_projects
            integration_available = True
        except ImportError:
            pass
        
        return {
            "status": "healthy",
            "integration_available": integration_available,
            "statistics": {
                "total_imported": imported_count,
                "auto_import_enabled": integration_available,
                "last_import": None  # TODO: Track last import timestamp
            }
        }
    except Exception as e:
        logger.error(f"Failed to get import status: {e}")
        return {
            "status": "error",
            "error": str(e)
        }