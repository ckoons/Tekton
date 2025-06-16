"""
Rhetor API - Now using enhanced version with real provider support
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rhetor.api")

# Import the enhanced app
try:
    # Try relative import first
    from .app_enhanced import app
    logger.info("Successfully imported enhanced Rhetor app")
except ImportError:
    try:
        # Try absolute import
        from rhetor.api.app_enhanced import app
        logger.info("Successfully imported enhanced Rhetor app (absolute)")
    except ImportError as e:
        logger.error(f"Failed to import enhanced app: {e}, falling back to basic version")
    # Fallback to basic app if enhanced fails
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    
    app = FastAPI(
        title="Rhetor LLM Management API (Fallback)",
        description="Basic Rhetor API",
        version="0.1.0"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        return {
            "name": "Rhetor LLM Management API (Fallback)",
            "version": "0.1.0",
            "status": "operational",
            "mode": "fallback"
        }
    
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "version": "0.1.0",
            "mode": "fallback"
        }

if __name__ == "__main__":
    import uvicorn
    
    # Add Tekton root to path for shared imports
    tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    if tekton_root not in sys.path:
        sys.path.append(tekton_root)
    
    from shared.utils.env_config import get_component_config
    
    config = get_component_config()
    port = config.rhetor.port if hasattr(config, 'rhetor') else int(os.environ.get("RHETOR_PORT"))
    logger.info(f"Starting Rhetor on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)