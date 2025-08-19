"""
Analyzer API endpoints for TektonCore.

Provides repository analysis functionality through REST API endpoints.
Moved from Ergon to TektonCore as part of Phase 0 of the Ergon Container Management Sprint.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from ..analyzer.analyzer import RepositoryAnalyzer, AnalysisType

logger = logging.getLogger(__name__)

# Create router for analyzer endpoints
router = APIRouter(prefix="/api/v1/analyzer", tags=["analyzer"])

# Global analyzer instance (will be properly initialized in startup)
analyzer_instance: Optional[RepositoryAnalyzer] = None


class AnalyzeRequest(BaseModel):
    """Request model for repository analysis."""
    repo_url: Optional[str] = Field(None, description="GitHub repository URL")
    local_path: Optional[str] = Field(None, description="Local repository path")
    analysis_type: str = Field("basic", description="Type of analysis: basic, architecture, tekton, companion, full")


class AnalysisStatus(BaseModel):
    """Response model for analysis status."""
    status: str
    message: str
    timestamp: datetime
    analysis_types: list[str]


@router.get("/status", response_model=AnalysisStatus)
async def get_analyzer_status():
    """
    Get the current status of the analyzer service.
    
    Returns:
        Current analyzer status and available analysis types
    """
    global analyzer_instance
    
    try:
        status = "ready" if analyzer_instance else "initializing"
        analysis_types = []
        
        if analyzer_instance:
            analysis_types = analyzer_instance.get_supported_analysis_types()
        
        return AnalysisStatus(
            status=status,
            message="Analyzer service is operational" if analyzer_instance else "Analyzer service is starting up",
            timestamp=datetime.utcnow(),
            analysis_types=analysis_types
        )
        
    except Exception as e:
        logger.error(f"Error getting analyzer status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get analyzer status: {str(e)}")


@router.get("/analysis-types")
async def get_analysis_types():
    """
    Get available analysis types and their descriptions.
    
    Returns:
        Dictionary of analysis types with descriptions
    """
    global analyzer_instance
    
    if not analyzer_instance:
        raise HTTPException(status_code=503, detail="Analyzer service not ready")
    
    try:
        types_info = {}
        for analysis_type in AnalysisType:
            types_info[analysis_type.value] = analyzer_instance.get_analysis_description(analysis_type)
        
        return {
            "analysis_types": types_info,
            "default": "basic"
        }
        
    except Exception as e:
        logger.error(f"Error getting analysis types: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get analysis types: {str(e)}")


@router.post("/analyze")
async def analyze_repository(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Analyze a GitHub repository or local path.
    
    Args:
        request: Analysis request containing repository information
        background_tasks: FastAPI background tasks
        
    Returns:
        Analysis results dictionary
    """
    global analyzer_instance
    
    if not analyzer_instance:
        raise HTTPException(status_code=503, detail="Analyzer service not ready")
    
    # Validate request
    if not request.repo_url and not request.local_path:
        raise HTTPException(status_code=400, detail="Either repo_url or local_path must be provided")
    
    if request.repo_url and request.local_path:
        raise HTTPException(status_code=400, detail="Provide either repo_url or local_path, not both")
    
    # Validate analysis type
    try:
        analysis_type = AnalysisType(request.analysis_type.lower())
    except ValueError:
        valid_types = [t.value for t in AnalysisType]
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid analysis type '{request.analysis_type}'. Valid types: {valid_types}"
        )
    
    try:
        logger.info(f"Starting {analysis_type.value} analysis for: {request.repo_url or request.local_path}")
        
        # Perform analysis
        result = await analyzer_instance.analyze(
            repo_url=request.repo_url,
            local_path=request.local_path,
            analysis_type=analysis_type
        )
        
        # Add metadata
        result["request"] = {
            "repo_url": request.repo_url,
            "local_path": request.local_path,
            "analysis_type": request.analysis_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Completed {analysis_type.value} analysis")
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing repository: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


def initialize_analyzer(github_token: Optional[str] = None) -> None:
    """
    Initialize the global analyzer instance.
    
    Args:
        github_token: Optional GitHub token for enhanced API access
    """
    global analyzer_instance
    
    try:
        analyzer_instance = RepositoryAnalyzer(github_token)
        logger.info("Analyzer service initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize analyzer: {str(e)}")
        analyzer_instance = None


def get_analyzer_router() -> APIRouter:
    """
    Get the analyzer router for including in the main app.
    
    Returns:
        Configured analyzer router
    """
    return router