"""
Sprint File Management Endpoints

Provides REST API endpoints for managing sprint files:
- DAILY_LOG.md
- HANDOFF.md  
- Sprint_Plan.md
"""

import os
from typing import Dict
from fastapi import APIRouter, HTTPException
from datetime import datetime
from shared.utils.logging_setup import setup_component_logging

logger = setup_component_logging("tekton_core.api.sprint_files")

# Create router with the /api/v1/sprints prefix
router = APIRouter()

# Sprint file endpoints (daily-log, handoff, sprint-plan)

@router.get("/{sprint_name}/daily-log")
async def get_sprint_daily_log(sprint_name: str):
    """Get sprint daily log content"""
    
    try:
        # Get sprint directory path
        tekton_root = os.environ.get("TEKTON_ROOT", os.getcwd())
        sprint_dir = os.path.join(tekton_root, "MetaData", "DevelopmentSprints", sprint_name)
        daily_log_path = os.path.join(sprint_dir, "DAILY_LOG.md")
        
        if not os.path.exists(daily_log_path):
            raise HTTPException(status_code=404, detail=f"Daily log not found for sprint {sprint_name}")
        
        with open(daily_log_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "success": True,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get daily log: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{sprint_name}/daily-log")
async def update_sprint_daily_log(sprint_name: str, request: Dict[str, str]):
    """Update sprint daily log content"""
    
    try:
        content = request.get("content", "")
        
        # Get sprint directory path
        tekton_root = os.environ.get("TEKTON_ROOT", os.getcwd())
        sprint_dir = os.path.join(tekton_root, "MetaData", "DevelopmentSprints", sprint_name)
        daily_log_path = os.path.join(sprint_dir, "DAILY_LOG.md")
        
        if not os.path.exists(sprint_dir):
            raise HTTPException(status_code=404, detail=f"Sprint directory not found for {sprint_name}")
        
        with open(daily_log_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "message": f"Daily log updated for {sprint_name}",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update daily log: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{sprint_name}/handoff")
async def get_sprint_handoff(sprint_name: str):
    """Get sprint handoff content"""
    
    try:
        # Get sprint directory path
        tekton_root = os.environ.get("TEKTON_ROOT", os.getcwd())
        sprint_dir = os.path.join(tekton_root, "MetaData", "DevelopmentSprints", sprint_name)
        handoff_path = os.path.join(sprint_dir, "HANDOFF.md")
        
        if not os.path.exists(handoff_path):
            raise HTTPException(status_code=404, detail=f"Handoff not found for sprint {sprint_name}")
        
        with open(handoff_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "success": True,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get handoff: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{sprint_name}/handoff")
async def update_sprint_handoff(sprint_name: str, request: Dict[str, str]):
    """Update sprint handoff content"""
    
    try:
        content = request.get("content", "")
        
        # Get sprint directory path
        tekton_root = os.environ.get("TEKTON_ROOT", os.getcwd())
        sprint_dir = os.path.join(tekton_root, "MetaData", "DevelopmentSprints", sprint_name)
        handoff_path = os.path.join(sprint_dir, "HANDOFF.md")
        
        if not os.path.exists(sprint_dir):
            raise HTTPException(status_code=404, detail=f"Sprint directory not found for {sprint_name}")
        
        with open(handoff_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "message": f"Handoff updated for {sprint_name}",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update handoff: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{sprint_name}/sprint-plan")
async def get_sprint_plan(sprint_name: str):
    """Get sprint plan content"""
    
    try:
        # Get sprint directory path
        tekton_root = os.environ.get("TEKTON_ROOT", os.getcwd())
        sprint_dir = os.path.join(tekton_root, "MetaData", "DevelopmentSprints", sprint_name)
        sprint_plan_path = os.path.join(sprint_dir, "SPRINT_PLAN.md")
        
        if not os.path.exists(sprint_plan_path):
            # Return a default Sprint Plan if file doesn't exist
            default_content = f"""# Sprint Plan: {sprint_name}

Automated: No
Autonomy Level: Co-Developer

## Overview
Sprint plan for {sprint_name}

## Tasks
- [ ] Task 1: Description
- [ ] Task 2: Description

## Notes
Created: {datetime.now().isoformat()}
"""
            return {
                "success": True,
                "content": default_content,
                "timestamp": datetime.now().isoformat()
            }
        
        with open(sprint_plan_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "success": True,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get sprint plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{sprint_name}/sprint-plan")
async def update_sprint_plan(sprint_name: str, request: Dict[str, str]):
    """Update sprint plan content"""
    
    try:
        content = request.get("content", "")
        
        # Get sprint directory path
        tekton_root = os.environ.get("TEKTON_ROOT", os.getcwd())
        sprint_dir = os.path.join(tekton_root, "MetaData", "DevelopmentSprints", sprint_name)
        sprint_plan_path = os.path.join(sprint_dir, "SPRINT_PLAN.md")
        
        # Create directory if it doesn't exist
        os.makedirs(sprint_dir, exist_ok=True)
        
        with open(sprint_plan_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "message": f"Sprint plan updated for {sprint_name}",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to update sprint plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))