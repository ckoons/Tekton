"""
API endpoints package for Sophia.

This package contains the API endpoint modules for Sophia's RESTful API.
"""

from fastapi import APIRouter

from sophia.api.endpoints.metrics import router as metrics_router
from sophia.api.endpoints.experiments import router as experiments_router
from sophia.api.endpoints.recommendations import router as recommendations_router
from sophia.api.endpoints.intelligence import router as intelligence_router
from sophia.api.endpoints.components import router as components_router
from sophia.api.endpoints.research import router as research_router

# Create a master router that includes all endpoint routers
api_router = APIRouter()

# Include all endpoint routers with their prefixes
api_router.include_router(metrics_router, prefix="/metrics", tags=["Metrics"])
api_router.include_router(experiments_router, prefix="/experiments", tags=["Experiments"])
api_router.include_router(recommendations_router, prefix="/recommendations", tags=["Recommendations"])
api_router.include_router(intelligence_router, prefix="/intelligence", tags=["Intelligence"])
api_router.include_router(components_router, prefix="/components", tags=["Components"])
api_router.include_router(research_router, prefix="/research", tags=["Research"])