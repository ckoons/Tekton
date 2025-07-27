"""
Enhanced Rhetor API - Intelligent LLM Orchestrator with Context Management
"""
import os
import sys
import json
import logging
import aiohttp
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add Tekton root to path if not already present
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rhetor.api.enhanced")

# Import shared utils with correct path
try:
    from shared.utils.graceful_shutdown import GracefulShutdown, add_fastapi_shutdown
    from shared.utils.health_check import create_health_response
    from shared.utils.hermes_registration import HermesRegistration, heartbeat_loop
    from shared.workflow.endpoint_template import create_workflow_endpoint
except ImportError as e:
    logger.warning(f"Could not import shared utils: {e}")
    GracefulShutdown = None
    create_health_response = None
    HermesRegistration = None
    create_workflow_endpoint = None

# Create FastAPI app
app = FastAPI(
    title="Rhetor LLM Orchestrator",
    description="Intelligent LLM management with context-aware routing and Apollo integration",
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

# Include standardized workflow endpoint
if create_workflow_endpoint:
    workflow_router = create_workflow_endpoint("rhetor")
    app.include_router(workflow_router)

# Provider configurations
PROVIDERS = {
    "ollama": {
        "id": "ollama",
        "name": "Ollama Local LLMs",
        "type": "local",
        "base_url": "http://localhost:11434",
        "available": False,
        "models": [],
        "default_model": "llama3.3",
        "capabilities": ["fast", "private", "code"]
    },
    "anthropic": {
        "id": "anthropic",
        "name": "Anthropic Claude",
        "type": "remote",
        "base_url": "https://api.anthropic.com/v1",
        "available": False,
        "models": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
        "default_model": "claude-3-5-sonnet-20241022",
        "capabilities": ["reasoning", "coding", "analysis"]
    },
    "openai": {
        "id": "openai",
        "name": "OpenAI",
        "type": "remote", 
        "base_url": "https://api.openai.com/v1",
        "available": False,
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
        "default_model": "gpt-4o",
        "capabilities": ["general", "coding", "vision"]
    },
    "groq": {
        "id": "groq",
        "name": "Groq",
        "type": "remote",
        "base_url": "https://api.groq.com/openai/v1",
        "available": False,
        "models": ["llama3-70b-8192", "mixtral-8x7b-32768"],
        "default_model": "llama3-70b-8192",
        "capabilities": ["fast", "coding", "general"]
    },
    "google": {
        "id": "google",
        "name": "Google Gemini",
        "type": "remote",
        "base_url": "https://generativelanguage.googleapis.com/v1",
        "available": False,
        "models": ["gemini-1.5-pro", "gemini-1.5-flash"],
        "default_model": "gemini-1.5-pro",
        "capabilities": ["multimodal", "reasoning", "long-context"]
    },
    "openrouter": {
        "id": "openrouter",
        "name": "OpenRouter",
        "type": "aggregator",
        "base_url": "https://openrouter.ai/api/v1",
        "available": False,
        "models": [],  # Will be populated dynamically
        "default_model": "anthropic/claude-3.5-sonnet",
        "capabilities": ["fallback", "cost-optimization", "model-variety"]
    }
}

# Context Management Models
class RoleContext(BaseModel):
    component_name: str
    primary_responsibility: str
    goals: List[str]
    capabilities: List[str]
    interaction_patterns: Dict[str, str]
    success_metrics: List[str]

class ProjectContext(BaseModel):
    project_name: str
    current_sprint: str
    my_deliverables: List[str]
    dependencies: Dict[str, List[str]]
    handoff_protocols: Dict[str, str]
    improvement_channels: List[str]

class TaskContext(BaseModel):
    current_task_id: str
    specific_instructions: str
    acceptance_criteria: List[str]
    constraints: List[str]
    deadline: Optional[str] = None

class DataContext(BaseModel):
    memory_indices: Dict[str, str]
    codebase_access: List[str]
    documentation_refs: List[str]
    conversation_memory_id: str
    shared_memory_ids: Dict[str, str]

class TektonContext(BaseModel):
    role: RoleContext
    project: ProjectContext
    task: TaskContext
    data: DataContext

class CompletionRequest(BaseModel):
    message: str
    context_id: str
    system_prompt: Optional[str] = None
    provider_id: Optional[str] = None
    model_id: Optional[str] = None
    component_name: Optional[str] = None  # For context injection
    task_type: Optional[str] = None  # For intelligent routing
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)

# Global state
session: Optional[aiohttp.ClientSession] = None
component_contexts: Dict[str, TektonContext] = {}
performance_metrics: Dict[str, Dict[str, Any]] = {}
shutdown_handler: Optional[GracefulShutdown] = None
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

async def save_contexts():
    """Save component contexts before shutdown"""
    if component_contexts:
        try:
            contexts_file = "/tmp/rhetor_contexts.json"
            with open(contexts_file, 'w') as f:
                # Convert contexts to dict format
                contexts_dict = {k: v.dict() for k, v in component_contexts.items()}
                json.dump(contexts_dict, f, indent=2)
            logger.info(f"Saved {len(component_contexts)} contexts to {contexts_file}")
        except Exception as e:
            logger.error(f"Failed to save contexts: {e}")

@app.on_event("startup")
async def startup_event():
    """Initialize providers on startup"""
    global shutdown_handler, is_registered_with_hermes, hermes_registration, heartbeat_task
    logger.info("Starting Rhetor Enhanced API")
    
    # Initialize graceful shutdown if available
    if GracefulShutdown:
        shutdown_handler = GracefulShutdown("rhetor", 8003)
        shutdown_handler.add_handler(cleanup_session)
        shutdown_handler.add_handler(save_contexts)
        add_fastapi_shutdown(app, shutdown_handler)
        logger.info("Graceful shutdown configured")
    
    await initialize_providers()
    
    # Register with Hermes if available
    if HermesRegistration:
        hermes_registration = HermesRegistration()
        is_registered_with_hermes = await hermes_registration.register_component(
            component_name="rhetor",
            port=8003,
            version="0.2.0",
            capabilities=[
                "llm_orchestration",
                "multi_provider_support",
                "intelligent_routing",
                "context_management",
                "apollo_integration"
            ],
            metadata={
                "providers": list(PROVIDERS.keys()),
                "enhanced": True
            }
        )
        
        # Start heartbeat task if registered
        if is_registered_with_hermes:
            heartbeat_task = asyncio.create_task(
                heartbeat_loop(hermes_registration, "rhetor", interval=30)
            )
            logger.info("Started Hermes heartbeat task")
    
    logger.info("Rhetor Enhanced API started successfully")

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
        await hermes_registration.deregister("rhetor")
    
    if shutdown_handler and not shutdown_handler.is_shutting_down:
        await shutdown_handler.shutdown()
    else:
        # Fallback cleanup if no shutdown handler
        await cleanup_session()

async def initialize_providers():
    """Check availability of all providers"""
    sess = await get_session()
    
    # Check Ollama
    try:
        async with sess.get(f"{PROVIDERS['ollama']['base_url']}/api/tags", timeout=2) as resp:
            if resp.status == 200:
                data = await resp.json()
                models = [m["name"] for m in data.get("models", [])]
                PROVIDERS["ollama"]["available"] = True
                PROVIDERS["ollama"]["models"] = models
                logger.info(f"Ollama available with {len(models)} models")
    except Exception as e:
        logger.warning(f"Ollama not available: {e}")
    
    # Check API key availability for other providers
    if os.environ.get("ANTHROPIC_API_KEY"):
        PROVIDERS["anthropic"]["available"] = True
        logger.info("Anthropic API key found")
    
    if os.environ.get("OPENAI_API_KEY"):
        PROVIDERS["openai"]["available"] = True
        logger.info("OpenAI API key found")
        
    if os.environ.get("GROQ_API_KEY"):
        PROVIDERS["groq"]["available"] = True
        logger.info("Groq API key found")
        
    if os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY"):
        PROVIDERS["google"]["available"] = True
        logger.info("Google API key found")
        
    if os.environ.get("OPEN_ROUTER_API_KEY"):
        PROVIDERS["openrouter"]["available"] = True
        logger.info("OpenRouter API key found")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Rhetor LLM Orchestrator",
        "version": "0.2.0",
        "status": "operational",
        "capabilities": [
            "multi-provider support",
            "intelligent routing",
            "context management",
            "apollo integration"
        ]
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    available_providers = {k: v["available"] for k, v in PROVIDERS.items()}
    
    # Use standardized health response if available
    if create_health_response:
        return create_health_response(
            component_name="rhetor",
            port=8003,
            version="0.2.0",
            status="healthy",
            registered=is_registered_with_hermes,
            details={
                "providers": available_providers,
                "active_contexts": len(component_contexts),
                "performance_metrics": len(performance_metrics)
            }
        )
    else:
        # Fallback to manual format
        return {
            "status": "healthy",
            "version": "0.2.0",
            "timestamp": datetime.now().isoformat(),
            "component": "rhetor",
            "port": 8003,
            "registered_with_hermes": is_registered_with_hermes,
            "details": {
                "providers": available_providers,
                "active_contexts": len(component_contexts),
                "performance_metrics": len(performance_metrics)
            }
        }

@app.get("/providers")
async def get_providers():
    """Get available LLM providers with real status"""
    return {"providers": PROVIDERS}

@app.get("/providers/{provider_id}")
async def get_provider(provider_id: str):
    """Get specific provider info"""
    if provider_id not in PROVIDERS:
        raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found")
    return PROVIDERS[provider_id]

@app.get("/models")
async def get_models():
    """Get all available models across providers"""
    models = []
    for provider_id, provider in PROVIDERS.items():
        if provider["available"]:
            for model in provider["models"]:
                models.append({
                    "id": f"{provider_id}/{model}",
                    "provider": provider_id,
                    "model": model,
                    "available": True,
                    "capabilities": provider["capabilities"]
                })
    return {"models": models}

def select_provider_for_task(task_type: Optional[str], component_name: Optional[str]) -> tuple[str, str]:
    """Intelligently select provider and model based on task type"""
    # Default fallback
    default_provider = "ollama" if PROVIDERS["ollama"]["available"] else "anthropic"
    
    # Task-based routing
    if task_type:
        if task_type in ["code", "debug", "refactor"]:
            if PROVIDERS["ollama"]["available"] and "deepseek-coder-v2" in PROVIDERS["ollama"]["models"]:
                return "ollama", "deepseek-coder-v2"
            elif PROVIDERS["anthropic"]["available"]:
                return "anthropic", "claude-3-5-sonnet-20241022"
        elif task_type in ["reasoning", "analysis", "planning"]:
            if PROVIDERS["anthropic"]["available"]:
                return "anthropic", "claude-3-5-sonnet-20241022"
        elif task_type in ["fast", "simple", "extraction"]:
            if PROVIDERS["groq"]["available"]:
                return "groq", "llama3-70b-8192"
            elif PROVIDERS["ollama"]["available"]:
                return "ollama", PROVIDERS["ollama"]["default_model"]
    
    # Component-based routing
    if component_name:
        if component_name in ["Sophia", "Prometheus"]:  # Complex reasoning
            if PROVIDERS["anthropic"]["available"]:
                return "anthropic", "claude-3-5-sonnet-20241022"
        elif component_name in ["Metis", "Apollo"]:  # Fast responses
            if PROVIDERS["groq"]["available"]:
                return "groq", "llama3-70b-8192"
    
    # Return best available
    for provider_id in ["anthropic", "openai", "groq", "ollama", "google", "openrouter"]:
        if PROVIDERS[provider_id]["available"]:
            return provider_id, PROVIDERS[provider_id]["default_model"]
    
    raise HTTPException(status_code=503, detail="No providers available")

async def complete_with_ollama(message: str, model: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
    """Complete using Ollama"""
    sess = await get_session()
    payload = {
        "model": model,
        "prompt": message,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 2048
        }
    }
    
    if system_prompt:
        payload["system"] = system_prompt
        
    try:
        async with sess.post(
            f"{PROVIDERS['ollama']['base_url']}/api/generate",
            json=payload,
            timeout=30
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return {
                    "content": data.get("response", ""),
                    "model": model,
                    "provider": "ollama",
                    "usage": {
                        "prompt_tokens": data.get("prompt_eval_count", 0),
                        "completion_tokens": data.get("eval_count", 0)
                    }
                }
            else:
                raise Exception(f"Ollama returned status {resp.status}")
    except Exception as e:
        logger.error(f"Ollama completion error: {e}")
        raise

async def complete_with_anthropic(message: str, model: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
    """Complete using Anthropic"""
    sess = await get_session()
    
    messages = [{"role": "user", "content": message}]
    
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 2048
    }
    
    if system_prompt:
        payload["system"] = system_prompt
        
    headers = {
        "x-api-key": os.environ.get("ANTHROPIC_API_KEY"),
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    try:
        async with sess.post(
            f"{PROVIDERS['anthropic']['base_url']}/messages",
            json=payload,
            headers=headers,
            timeout=30
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return {
                    "content": data["content"][0]["text"],
                    "model": model,
                    "provider": "anthropic",
                    "usage": data.get("usage", {})
                }
            else:
                error_text = await resp.text()
                raise Exception(f"Anthropic returned status {resp.status}: {error_text}")
    except Exception as e:
        logger.error(f"Anthropic completion error: {e}")
        raise

async def complete_with_openai_compatible(
    provider_id: str, 
    message: str, 
    model: str, 
    system_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """Complete using OpenAI-compatible API (OpenAI, Groq, OpenRouter)"""
    sess = await get_session()
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": message})
    
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 2048,
        "temperature": 0.7
    }
    
    # Set appropriate headers based on provider
    headers = {"Content-Type": "application/json"}
    
    if provider_id == "openai":
        headers["Authorization"] = f"Bearer {os.environ.get('OPENAI_API_KEY')}"
    elif provider_id == "groq":
        headers["Authorization"] = f"Bearer {os.environ.get('GROQ_API_KEY')}"
    elif provider_id == "openrouter":
        headers["Authorization"] = f"Bearer {os.environ.get('OPEN_ROUTER_API_KEY')}"
        headers["HTTP-Referer"] = "https://tekton.ai"  # OpenRouter requires this
    
    try:
        url = f"{PROVIDERS[provider_id]['base_url']}/chat/completions"
        async with sess.post(url, json=payload, headers=headers, timeout=30) as resp:
            if resp.status == 200:
                data = await resp.json()
                return {
                    "content": data["choices"][0]["message"]["content"],
                    "model": model,
                    "provider": provider_id,
                    "usage": data.get("usage", {})
                }
            else:
                error_text = await resp.text()
                raise Exception(f"{provider_id} returned status {resp.status}: {error_text}")
    except Exception as e:
        logger.error(f"{provider_id} completion error: {e}")
        raise

async def complete_with_google(message: str, model: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
    """Complete using Google Gemini"""
    sess = await get_session()
    
    # Gemini uses a different API structure
    contents = []
    if system_prompt:
        contents.append({"role": "user", "parts": [{"text": system_prompt}]})
        contents.append({"role": "model", "parts": [{"text": "I understand."}]})
    contents.append({"role": "user", "parts": [{"text": message}]})
    
    payload = {"contents": contents}
    
    api_key = os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY")
    url = f"{PROVIDERS['google']['base_url']}/models/{model}:generateContent?key={api_key}"
    
    try:
        async with sess.post(url, json=payload, timeout=30) as resp:
            if resp.status == 200:
                data = await resp.json()
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                return {
                    "content": content,
                    "model": model,
                    "provider": "google",
                    "usage": {}  # Google doesn't provide token counts in the same way
                }
            else:
                error_text = await resp.text()
                raise Exception(f"Google returned status {resp.status}: {error_text}")
    except Exception as e:
        logger.error(f"Google completion error: {e}")
        raise

@app.post("/complete")
async def complete(request: CompletionRequest):
    """Complete a message with intelligent provider selection"""
    start_time = datetime.now()
    
    # Select provider and model
    if request.provider_id and request.model_id:
        provider_id = request.provider_id
        model_id = request.model_id
    else:
        provider_id, model_id = select_provider_for_task(request.task_type, request.component_name)
    
    # Inject context if component specified
    system_prompt = request.system_prompt
    if request.component_name and request.component_name in component_contexts:
        context = component_contexts[request.component_name]
        context_prompt = generate_context_prompt(request.component_name, context)
        system_prompt = f"{context_prompt}\n\n{system_prompt}" if system_prompt else context_prompt
    
    try:
        # Route to appropriate provider
        if provider_id == "ollama":
            result = await complete_with_ollama(request.message, model_id, system_prompt)
        elif provider_id == "anthropic":
            result = await complete_with_anthropic(request.message, model_id, system_prompt)
        elif provider_id in ["openai", "groq", "openrouter"]:
            result = await complete_with_openai_compatible(provider_id, request.message, model_id, system_prompt)
        elif provider_id == "google":
            result = await complete_with_google(request.message, model_id, system_prompt)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider_id}")
        
        # Track performance metrics
        elapsed = (datetime.now() - start_time).total_seconds()
        track_performance(provider_id, model_id, elapsed, True)
        
        # Add metadata
        result["context_id"] = request.context_id
        result["elapsed_seconds"] = elapsed
        result["timestamp"] = datetime.now().isoformat()
        
        return result
        
    except Exception as e:
        # Track failure
        elapsed = (datetime.now() - start_time).total_seconds()
        track_performance(provider_id, model_id, elapsed, False)
        
        # Try fallback if available
        if "openrouter" in request.options.get("fallback_providers", []) and PROVIDERS["openrouter"]["available"]:
            try:
                logger.info(f"Attempting OpenRouter fallback after {provider_id} failure")
                result = await complete_with_openai_compatible(
                    "openrouter", 
                    request.message, 
                    "anthropic/claude-3.5-sonnet", 
                    system_prompt
                )
                result["fallback"] = True
                result["original_error"] = str(e)
                return result
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")
        
        raise HTTPException(status_code=500, detail=str(e))

def generate_context_prompt(component_name: str, context: TektonContext) -> str:
    """Generate system prompt from Tekton context"""
    return f"""You are {context.role.component_name}, a component in the Tekton AI orchestration system.

Your Role:
- Primary Responsibility: {context.role.primary_responsibility}
- Goals: {', '.join(context.role.goals)}
- Capabilities: {', '.join(context.role.capabilities)}

Current Project: {context.project.project_name}
Sprint: {context.project.current_sprint}
Your Deliverables: {', '.join(context.project.my_deliverables)}

Current Task: {context.task.current_task_id}
Instructions: {context.task.specific_instructions}
Acceptance Criteria: {', '.join(context.task.acceptance_criteria)}

You have access to:
- Memory indices: {', '.join(context.data.memory_indices.keys())}
- Conversation memory: {context.data.conversation_memory_id}

Remember to coordinate with other Tekton components as needed."""

def track_performance(provider_id: str, model_id: str, elapsed: float, success: bool):
    """Track provider/model performance metrics"""
    key = f"{provider_id}/{model_id}"
    if key not in performance_metrics:
        performance_metrics[key] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_time": 0.0,
            "average_time": 0.0
        }
    
    metrics = performance_metrics[key]
    metrics["total_requests"] += 1
    if success:
        metrics["successful_requests"] += 1
    else:
        metrics["failed_requests"] += 1
    metrics["total_time"] += elapsed
    metrics["average_time"] = metrics["total_time"] / metrics["total_requests"]

# Context Management Endpoints
@app.post("/contexts/{component_name}")
async def create_context(component_name: str, context: TektonContext):
    """Create or update context for a component"""
    component_contexts[component_name] = context
    return {"status": "created", "component": component_name}

@app.get("/contexts/{component_name}")
async def get_context(component_name: str):
    """Get context for a component"""
    if component_name not in component_contexts:
        raise HTTPException(status_code=404, detail=f"No context found for {component_name}")
    return component_contexts[component_name]

@app.delete("/contexts/{component_name}")
async def delete_context(component_name: str):
    """Delete context for a component"""
    if component_name in component_contexts:
        del component_contexts[component_name]
    return {"status": "deleted", "component": component_name}

@app.get("/contexts")
async def list_contexts():
    """List all component contexts"""
    return {
        "contexts": list(component_contexts.keys()),
        "count": len(component_contexts)
    }

# Performance Monitoring
@app.get("/metrics")
async def get_metrics():
    """Get performance metrics for all providers/models"""
    return {
        "metrics": performance_metrics,
        "timestamp": datetime.now().isoformat()
    }

# Apollo Integration Stub
@app.post("/apollo/guidelines")
async def receive_apollo_guidelines(guidelines: Dict[str, Any] = Body(...)):
    """Receive guidelines from Apollo for model selection and behavior"""
    # TODO: Implement Apollo guideline processing
    logger.info(f"Received Apollo guidelines: {guidelines}")
    return {"status": "received", "guidelines": guidelines}

if __name__ == "__main__":
    import uvicorn
    
    # Add Tekton root to path for shared imports
    tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    if tekton_root not in sys.path:
        sys.path.append(tekton_root)
    
    from shared.utils.env_config import get_component_config
    
    config = get_component_config()
    port = config.rhetor.port if hasattr(config, 'rhetor') else int(os.environ.get("RHETOR_PORT"))
    logger.info(f"Starting enhanced Rhetor on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)