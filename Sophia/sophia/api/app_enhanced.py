"""
Enhanced Sophia API - Intelligence Measurement with Real Component Health Mapping
"""
import os
import sys
import json
import logging
import aiohttp
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Field
from tekton.models.base import TektonBaseModel

# Add Tekton root to path if not already present
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sophia.api.enhanced")

# Import shared utils with correct path
try:
    from shared.utils.graceful_shutdown import GracefulShutdown, add_fastapi_shutdown
    from shared.utils.health_check import create_health_response
    from shared.utils.hermes_registration import HermesRegistration, heartbeat_loop
    from shared.utils.env_config import get_component_config
except ImportError as e:
    logger.warning(f"Could not import shared utils: {e}")
    GracefulShutdown = None
    create_health_response = None
    HermesRegistration = None
    get_component_config = None

# Create FastAPI app
app = FastAPI(
    title="Sophia Machine Learning & Intelligence API",
    description="AI intelligence measurement and self-improvement system",
    version="0.2.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_component_ports():
    """Get component ports from configuration"""
    import os
    config = get_component_config()
    
    # Map of component names to config attributes
    components = {
        "engram": "engram",
        "hermes": "hermes",
        "ergon": "ergon",
        "rhetor": "rhetor",
        "athena": "athena",
        "prometheus": "prometheus",
        "harmonia": "harmonia",
        "telos": "telos",
        "synthesis": "synthesis",
        "metis": "metis",
        "apollo": "apollo",
        "budget": "budget",
        "sophia": "sophia",
        "hephaestus": "hephaestus"
    }
    
    ports = {}
    for name, config_attr in components.items():
        if hasattr(config, config_attr):
            component_config = getattr(config, config_attr)
            if hasattr(component_config, 'port'):
                ports[name] = component_config.port
            else:
                # Fallback to environment variable
                env_var = f"{name.upper()}_PORT"
                ports[name] = int(os.environ.get(env_var))
        else:
            # Fallback to environment variable
            env_var = f"{name.upper()}_PORT"
            ports[name] = int(os.environ.get(env_var))
    
    return ports

# Component port mapping
COMPONENT_PORTS = get_component_ports()

# Intelligence dimensions and their weights
INTELLIGENCE_DIMENSIONS = {
    "language_processing": {
        "name": "Language Processing",
        "weight": 0.15,
        "components": ["rhetor", "telos", "hermes"]
    },
    "reasoning": {
        "name": "Reasoning",
        "weight": 0.20,
        "components": ["prometheus", "metis", "athena"]
    },
    "knowledge": {
        "name": "Knowledge Management",
        "weight": 0.15,
        "components": ["athena", "engram"]
    },
    "learning": {
        "name": "Learning & Adaptation",
        "weight": 0.10,
        "components": ["sophia", "engram"]
    },
    "planning": {
        "name": "Planning & Organization",
        "weight": 0.15,
        "components": ["prometheus", "metis", "harmonia"]
    },
    "execution": {
        "name": "Task Execution",
        "weight": 0.10,
        "components": ["synthesis", "ergon", "harmonia"]
    },
    "collaboration": {
        "name": "Inter-component Collaboration",
        "weight": 0.15,
        "components": ["hermes", "apollo", "budget"]
    }
}

# Component specializations for IQ calculation
COMPONENT_SPECIALIZATIONS = {
    "engram": {"primary": "knowledge", "secondary": ["learning"]},
    "hermes": {"primary": "collaboration", "secondary": ["language_processing"]},
    "ergon": {"primary": "execution", "secondary": ["planning"]},
    "rhetor": {"primary": "language_processing", "secondary": ["reasoning"]},
    "athena": {"primary": "knowledge", "secondary": ["reasoning"]},
    "prometheus": {"primary": "planning", "secondary": ["reasoning"]},
    "harmonia": {"primary": "execution", "secondary": ["planning"]},
    "telos": {"primary": "language_processing", "secondary": ["reasoning"]},
    "synthesis": {"primary": "execution", "secondary": []},
    "metis": {"primary": "planning", "secondary": ["reasoning"]},
    "apollo": {"primary": "collaboration", "secondary": ["learning"]},
    "budget": {"primary": "collaboration", "secondary": []},
    "sophia": {"primary": "learning", "secondary": ["reasoning"]},
    "hephaestus": {"primary": "collaboration", "secondary": []}
}

# Global state
session: Optional[aiohttp.ClientSession] = None
component_health_cache: Dict[str, Dict[str, Any]] = {}
last_health_check: Optional[datetime] = None
shutdown_handler: Optional[GracefulShutdown] = None
background_task = None
is_registered_with_hermes: bool = False
hermes_registration: Optional[HermesRegistration] = None
heartbeat_task = None

async def get_session() -> aiohttp.ClientSession:
    """Get or create aiohttp session"""
    global session
    if session is None or session.closed:
        session = aiohttp.ClientSession()
    return session

# Cleanup functions for graceful shutdown
async def cleanup_session():
    """Close aiohttp session"""
    global session
    if session and not session.closed:
        await session.close()
        logger.info("Closed aiohttp session")

async def save_health_data():
    """Save component health data before shutdown"""
    if component_health_cache:
        try:
            health_file = "/tmp/sophia_health_cache.json"
            with open(health_file, 'w') as f:
                json.dump({
                    "health_cache": component_health_cache,
                    "last_check": last_health_check.isoformat() if last_health_check else None,
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2)
            logger.info(f"Saved health data for {len(component_health_cache)} components")
        except Exception as e:
            logger.error(f"Failed to save health data: {e}")

async def cancel_background_task():
    """Cancel background health update task"""
    global background_task
    if background_task and not background_task.done():
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            logger.info("Background health update task cancelled")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global heartbeat_task
    
    # Cancel heartbeat task
    if heartbeat_task:
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass
    
    # Deregister from Hermes
    if hermes_registration and is_registered_with_hermes:
        await hermes_registration.deregister("sophia")
    
    if shutdown_handler and not shutdown_handler.is_shutting_down:
        await shutdown_handler.shutdown()
    else:
        # Fallback cleanup
        await cancel_background_task()
        await cleanup_session()

async def check_component_health(component: str, port: int) -> Dict[str, Any]:
    """Check health of a specific component"""
    sess = await get_session()
    
    try:
        url = f"http://localhost:{port}/health"
        async with sess.get(url, timeout=2) as resp:
            if resp.status == 200:
                data = await resp.json()
                return {
                    "component": component,
                    "port": port,
                    "status": "healthy",
                    "data": data,
                    "response_time": 0.1  # Would need actual timing
                }
            else:
                return {
                    "component": component,
                    "port": port,
                    "status": "unhealthy",
                    "error": f"HTTP {resp.status}"
                }
    except asyncio.TimeoutError:
        return {
            "component": component,
            "port": port,
            "status": "timeout",
            "error": "Health check timed out"
        }
    except Exception as e:
        return {
            "component": component,
            "port": port,
            "status": "error",
            "error": str(e)
        }

async def update_component_health():
    """Update health status for all components"""
    global component_health_cache, last_health_check
    
    # Check all components in parallel
    tasks = []
    for component, port in COMPONENT_PORTS.items():
        task = check_component_health(component, port)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    
    # Update cache
    component_health_cache = {r["component"]: r for r in results}
    last_health_check = datetime.now()
    
    logger.info(f"Updated health for {len(results)} components")

def calculate_component_iq(component: str, health_data: Dict[str, Any]) -> float:
    """Calculate IQ score for a single component based on health"""
    base_iq = 100.0
    
    # Health status impacts
    if health_data["status"] == "healthy":
        health_bonus = 20.0
    elif health_data["status"] == "unhealthy":
        health_bonus = -30.0
    elif health_data["status"] == "timeout":
        health_bonus = -40.0
    else:  # error
        health_bonus = -50.0
    
    # Response time impacts (if available)
    response_time = health_data.get("response_time", 1.0)
    if response_time < 0.1:
        speed_bonus = 10.0
    elif response_time < 0.5:
        speed_bonus = 5.0
    elif response_time < 1.0:
        speed_bonus = 0.0
    else:
        speed_bonus = -10.0
    
    # Specialization bonus
    spec = COMPONENT_SPECIALIZATIONS.get(component, {})
    if spec.get("primary"):
        specialization_bonus = 10.0
    else:
        specialization_bonus = 0.0
    
    # Calculate final IQ
    component_iq = base_iq + health_bonus + speed_bonus + specialization_bonus
    
    # Ensure reasonable bounds
    component_iq = max(50, min(150, component_iq))
    
    return component_iq

def calculate_dimension_score(dimension: str, dimension_info: Dict[str, Any]) -> float:
    """Calculate score for a specific intelligence dimension"""
    relevant_components = dimension_info["components"]
    
    scores = []
    weights = []
    
    for component in relevant_components:
        if component in component_health_cache:
            health_data = component_health_cache[component]
            component_iq = calculate_component_iq(component, health_data)
            
            # Weight by specialization
            spec = COMPONENT_SPECIALIZATIONS.get(component, {})
            if spec.get("primary") == dimension:
                weight = 2.0  # Primary specialization
            elif dimension in spec.get("secondary", []):
                weight = 1.5  # Secondary specialization
            else:
                weight = 1.0  # Contributing component
            
            scores.append(component_iq)
            weights.append(weight)
    
    # Calculate weighted average
    if scores:
        weighted_sum = sum(s * w for s, w in zip(scores, weights))
        total_weight = sum(weights)
        dimension_score = weighted_sum / total_weight
    else:
        dimension_score = 100.0  # Default if no data
    
    return dimension_score

def calculate_system_iq() -> Dict[str, Any]:
    """Calculate overall system IQ from component health"""
    dimension_scores = {}
    
    # Calculate score for each dimension
    for dimension, info in INTELLIGENCE_DIMENSIONS.items():
        dimension_scores[dimension] = calculate_dimension_score(dimension, info)
    
    # Calculate weighted overall IQ
    total_iq = 0.0
    for dimension, info in INTELLIGENCE_DIMENSIONS.items():
        score = dimension_scores[dimension]
        weight = info["weight"]
        total_iq += score * weight
    
    # Learning rate based on system health
    healthy_count = sum(1 for h in component_health_cache.values() if h["status"] == "healthy")
    total_count = len(component_health_cache)
    learning_rate = healthy_count / total_count if total_count > 0 else 0.5
    
    # Adaptation score based on response times
    avg_response_time = sum(h.get("response_time", 1.0) for h in component_health_cache.values()) / max(len(component_health_cache), 1)
    adaptation_score = 1.0 - min(avg_response_time, 1.0)
    
    return {
        "system_iq": round(total_iq, 1),
        "learning_rate": round(learning_rate, 2),
        "adaptation_score": round(adaptation_score, 2),
        "dimension_scores": {k: round(v, 1) for k, v in dimension_scores.items()},
        "healthy_components": healthy_count,
        "total_components": total_count
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Sophia Machine Learning & Intelligence API",
        "version": "0.2.0",
        "status": "operational",
        "capabilities": [
            "real-time intelligence measurement",
            "component health monitoring",
            "ml analysis",
            "research management"
        ]
    }

def _get_sophia_port() -> int:
    """Get Sophia port from configuration."""
    config = get_component_config()
    try:
        return config.sophia.port
    except (AttributeError, TypeError):
        return int(os.environ.get("SOPHIA_PORT"))

@app.get("/health")
async def health():
    """Health check endpoint"""
    # Use standardized health response if available
    if create_health_response:
        return create_health_response(
            component_name="sophia",
            port=_get_sophia_port(),
            version="0.2.0",
            status="healthy",
            registered=is_registered_with_hermes,
            details={
                "services": {
                    "ml_engine": "operational",
                    "research_framework": "operational",
                    "intelligence_measurement": "operational"
                },
                "last_health_check": last_health_check.isoformat() if last_health_check else None,
                "components_monitored": len(component_health_cache)
            }
        )
    else:
        # Fallback to manual format
        return {
            "status": "healthy",
            "version": "0.2.0",
            "timestamp": datetime.now().isoformat(),
            "component": "sophia",
            "port": _get_sophia_port(),
            "registered_with_hermes": is_registered_with_hermes,
            "details": {
                "services": {
                    "ml_engine": "operational",
                    "research_framework": "operational",
                    "intelligence_measurement": "operational"
                },
                "last_health_check": last_health_check.isoformat() if last_health_check else None,
                "components_monitored": len(component_health_cache)
            }
        }

@app.get("/api/mcp/v1/sophia-status")
async def sophia_status():
    """Get Sophia status for MCP"""
    return {
        "status": "active",
        "capabilities": {
            "ml_analysis": True,
            "research_management": True,
            "intelligence_measurement": True
        },
        "active_experiments": 0,
        "research_projects": 0,
        "components_monitored": len(component_health_cache)
    }

@app.get("/api/intelligence/metrics")
async def get_intelligence_metrics():
    """Get real-time system intelligence metrics"""
    # Update health if stale (> 30 seconds)
    if not last_health_check or (datetime.now() - last_health_check).seconds > 30:
        await update_component_health()
    
    # Calculate system IQ
    system_metrics = calculate_system_iq()
    
    # Get component IQs
    component_iqs = {}
    for component, health_data in component_health_cache.items():
        iq = calculate_component_iq(component, health_data)
        spec = COMPONENT_SPECIALIZATIONS.get(component, {})
        component_iqs[component] = {
            "iq": round(iq, 1),
            "specialization": spec.get("primary", "general"),
            "status": health_data["status"]
        }
    
    return {
        "system_iq": system_metrics["system_iq"],
        "learning_rate": system_metrics["learning_rate"],
        "adaptation_score": system_metrics["adaptation_score"],
        "dimension_scores": system_metrics["dimension_scores"],
        "components": component_iqs,
        "health_summary": {
            "healthy": system_metrics["healthy_components"],
            "total": system_metrics["total_components"],
            "percentage": round(system_metrics["healthy_components"] / max(system_metrics["total_components"], 1) * 100, 1)
        },
        "timestamp": datetime.now().isoformat(),
        "measurement_interval": "30s"
    }

@app.post("/api/intelligence/refresh")
async def refresh_intelligence_metrics():
    """Force refresh of component health and intelligence metrics"""
    await update_component_health()
    return {
        "status": "refreshed",
        "components_checked": len(component_health_cache),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/intelligence/components/{component_name}")
async def get_component_intelligence(component_name: str):
    """Get detailed intelligence metrics for a specific component"""
    if component_name not in COMPONENT_PORTS:
        raise HTTPException(status_code=404, detail=f"Component {component_name} not found")
    
    # Update health if needed
    if not last_health_check or (datetime.now() - last_health_check).seconds > 30:
        await update_component_health()
    
    health_data = component_health_cache.get(component_name)
    if not health_data:
        raise HTTPException(status_code=404, detail=f"No health data for {component_name}")
    
    # Calculate component IQ
    iq = calculate_component_iq(component_name, health_data)
    spec = COMPONENT_SPECIALIZATIONS.get(component_name, {})
    
    # Calculate dimension contributions
    dimension_contributions = {}
    for dimension, info in INTELLIGENCE_DIMENSIONS.items():
        if component_name in info["components"]:
            if spec.get("primary") == dimension:
                contribution = "primary"
            elif dimension in spec.get("secondary", []):
                contribution = "secondary"
            else:
                contribution = "supporting"
            dimension_contributions[dimension] = contribution
    
    return {
        "component": component_name,
        "iq": round(iq, 1),
        "status": health_data["status"],
        "port": health_data["port"],
        "specialization": {
            "primary": spec.get("primary", "general"),
            "secondary": spec.get("secondary", [])
        },
        "dimension_contributions": dimension_contributions,
        "health_details": health_data,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/intelligence/dimensions")
async def get_intelligence_dimensions():
    """Get information about all intelligence dimensions"""
    dimensions = {}
    
    for dimension, info in INTELLIGENCE_DIMENSIONS.items():
        dimensions[dimension] = {
            "name": info["name"],
            "weight": info["weight"],
            "contributing_components": info["components"],
            "description": f"Measures {info['name'].lower()} capabilities across the system"
        }
    
    return {
        "dimensions": dimensions,
        "total_weight": sum(d["weight"] for d in INTELLIGENCE_DIMENSIONS.values())
    }

@app.get("/api/intelligence/recommendations")
async def get_improvement_recommendations():
    """Get recommendations for improving system intelligence"""
    # Update health if needed
    if not last_health_check or (datetime.now() - last_health_check).seconds > 30:
        await update_component_health()
    
    recommendations = []
    
    # Check for unhealthy components
    unhealthy = [c for c, h in component_health_cache.items() if h["status"] != "healthy"]
    if unhealthy:
        recommendations.append({
            "priority": "high",
            "category": "health",
            "issue": f"{len(unhealthy)} components are unhealthy",
            "components": unhealthy,
            "action": "Investigate and fix component health issues",
            "impact": "Could improve system IQ by 10-30 points"
        })
    
    # Check for slow components
    slow_components = [c for c, h in component_health_cache.items() 
                      if h.get("response_time", 0) > 0.5]
    if slow_components:
        recommendations.append({
            "priority": "medium",
            "category": "performance",
            "issue": f"{len(slow_components)} components have slow response times",
            "components": slow_components,
            "action": "Optimize component performance",
            "impact": "Could improve adaptation score by 0.1-0.2"
        })
    
    # Check dimension balance
    system_metrics = calculate_system_iq()
    dimension_scores = system_metrics["dimension_scores"]
    
    # Find weak dimensions
    weak_dimensions = [(d, s) for d, s in dimension_scores.items() if s < 90]
    if weak_dimensions:
        for dimension, score in weak_dimensions:
            recommendations.append({
                "priority": "medium",
                "category": "capability",
                "issue": f"{INTELLIGENCE_DIMENSIONS[dimension]['name']} score is low ({score})",
                "dimension": dimension,
                "action": f"Improve components: {', '.join(INTELLIGENCE_DIMENSIONS[dimension]['components'])}",
                "impact": f"Could improve {dimension} score by {100-score} points"
            })
    
    return {
        "recommendations": recommendations,
        "current_system_iq": system_metrics["system_iq"],
        "potential_improvement": sum(20 for r in recommendations if r["priority"] == "high") +
                               sum(10 for r in recommendations if r["priority"] == "medium"),
        "timestamp": datetime.now().isoformat()
    }

@app.on_event("startup") 
async def startup_event():
    """Initialize on startup"""
    global background_task, shutdown_handler, is_registered_with_hermes, hermes_registration, heartbeat_task
    logger.info("Starting Sophia Enhanced API")
    
    # Initialize graceful shutdown if available
    if GracefulShutdown:
        config = get_component_config() if get_component_config else None
        port = config.sophia.port if config and hasattr(config, 'sophia') else int(os.environ.get("SOPHIA_PORT"))
        shutdown_handler = GracefulShutdown("sophia", port)
        shutdown_handler.add_handler(cancel_background_task)
        shutdown_handler.add_handler(save_health_data)
        shutdown_handler.add_handler(cleanup_session)
        add_fastapi_shutdown(app, shutdown_handler)
        logger.info("Graceful shutdown configured")
    
    await update_component_health()
    # Start background task
    background_task = asyncio.create_task(periodic_health_update())
    
    # Register with Hermes if available
    if HermesRegistration:
        hermes_registration = HermesRegistration()
        config = get_component_config() if get_component_config else None
        port = config.sophia.port if config and hasattr(config, 'sophia') else int(os.environ.get("SOPHIA_PORT"))
        is_registered_with_hermes = await hermes_registration.register_component(
            component_name="sophia",
            port=port,
            version="0.2.0",
            capabilities=[
                "intelligence_measurement",
                "component_health_monitoring",
                "ml_analysis",
                "research_management"
            ],
            metadata={
                "enhanced": True,
                "intelligence_dimensions": 7
            }
        )
        
        # Start heartbeat task if registered
        if is_registered_with_hermes:
            heartbeat_task = asyncio.create_task(
                heartbeat_loop(hermes_registration, "sophia", interval=30)
            )
            logger.info("Started Hermes heartbeat task")
    
    logger.info("Sophia Enhanced API started successfully")

async def periodic_health_update():
    """Periodically update component health"""
    while True:
        await asyncio.sleep(30)  # Update every 30 seconds
        try:
            await update_component_health()
        except Exception as e:
            logger.error(f"Error in periodic health update: {e}")

if __name__ == "__main__":
    import uvicorn
    config = get_component_config() if get_component_config else None
    port = config.sophia.port if config and hasattr(config, 'sophia') else int(os.environ.get("SOPHIA_PORT"))
    logger.info(f"Starting enhanced Sophia on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)