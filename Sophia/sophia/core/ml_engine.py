"""
Sophia Machine Learning Engine

Core machine learning capabilities for the Tekton ecosystem.
"""

import os
import logging
import asyncio
import importlib
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path

logger = logging.getLogger("sophia.ml_engine")

class ModelRegistry:
    """
    Registry for managing ML models in Sophia.
    """
    
    def __init__(self):
        self.models = {}
        self.active_models = {}
        self.default_models = {
            "embedding": None,
            "classification": None,
            "generation": None,
            "vision": None
        }
    
    async def register_model(self, 
                            model_id: str, 
                            model_type: str, 
                            provider: str,
                            capabilities: List[str],
                            metadata: Dict[str, Any] = None) -> bool:
        """
        Register a model with the registry.
        
        Args:
            model_id: Unique identifier for the model
            model_type: Type of model (embedding, classification, etc.)
            provider: The provider of the model (local, huggingface, etc.)
            capabilities: List of capabilities the model provides
            metadata: Additional model information
            
        Returns:
            True if registration was successful
        """
        if model_id in self.models:
            logger.warning(f"Model {model_id} is already registered. Updating registration.")
            
        self.models[model_id] = {
            "model_type": model_type,
            "provider": provider,
            "capabilities": capabilities,
            "metadata": metadata or {},
            "status": "registered"
        }
        
        # If this is the first model of its type, set it as default
        if model_type in self.default_models and self.default_models[model_type] is None:
            self.default_models[model_type] = model_id
            logger.info(f"Setting {model_id} as default model for {model_type}")
            
        logger.info(f"Registered model {model_id} of type {model_type} from {provider}")
        return True
    
    async def load_model(self, model_id: str) -> bool:
        """
        Load a registered model into memory.
        
        Args:
            model_id: ID of the model to load
            
        Returns:
            True if the model was loaded successfully
        """
        if model_id not in self.models:
            logger.error(f"Cannot load model {model_id}: not registered")
            return False
            
        model_info = self.models[model_id]
        logger.info(f"Loading model {model_id} ({model_info['model_type']})...")
        
        try:
            # This would normally load the actual model
            # For now, we just update the status
            model_info["status"] = "loaded"
            self.active_models[model_id] = {"instance": None}
            logger.info(f"Model {model_id} loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading model {model_id}: {e}")
            return False
    
    async def unload_model(self, model_id: str) -> bool:
        """
        Unload a model from memory.
        
        Args:
            model_id: ID of the model to unload
            
        Returns:
            True if the model was unloaded successfully
        """
        if model_id not in self.active_models:
            logger.warning(f"Model {model_id} is not currently loaded")
            return True
            
        try:
            # This would normally unload the actual model
            # For now, we just update the status
            self.models[model_id]["status"] = "registered"
            del self.active_models[model_id]
            logger.info(f"Model {model_id} unloaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error unloading model {model_id}: {e}")
            return False
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a registered model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            Model information dictionary or None if not found
        """
        return self.models.get(model_id)
        
    def get_default_model(self, model_type: str) -> Optional[str]:
        """
        Get the default model ID for a specific type.
        
        Args:
            model_type: Type of model to get
            
        Returns:
            Model ID or None if no default is set
        """
        return self.default_models.get(model_type)
        
    def set_default_model(self, model_type: str, model_id: str) -> bool:
        """
        Set the default model for a specific type.
        
        Args:
            model_type: Type of model
            model_id: ID of the model to set as default
            
        Returns:
            True if successful
        """
        if model_type not in self.default_models:
            logger.error(f"Unknown model type: {model_type}")
            return False
            
        if model_id not in self.models:
            logger.error(f"Unknown model ID: {model_id}")
            return False
            
        self.default_models[model_type] = model_id
        logger.info(f"Set {model_id} as default model for {model_type}")
        return True
        
    def get_models_by_type(self, model_type: str) -> List[str]:
        """
        Get all model IDs of a specific type.
        
        Args:
            model_type: Type of models to get
            
        Returns:
            List of model IDs
        """
        return [
            model_id for model_id, info in self.models.items()
            if info["model_type"] == model_type
        ]

class MLEngine:
    """
    Core machine learning engine for Sophia.
    
    Manages ML model registration, loading, and execution.
    """
    
    def __init__(self):
        self.registry = ModelRegistry()
        self.is_initialized = False
        
    async def initialize(self) -> bool:
        """
        Initialize the ML engine.
        
        Returns:
            True if successful
        """
        logger.info("Initializing Sophia ML Engine...")
        
        # Register built-in models
        await self._register_builtin_models()
        
        self.is_initialized = True
        logger.info("Sophia ML Engine initialized successfully")
        return True
        
    async def _register_builtin_models(self) -> None:
        """Register built-in ML models."""
        # Example built-in model registrations
        await self.registry.register_model(
            model_id="sophia-embedding-small",
            model_type="embedding",
            provider="local",
            capabilities=["text_embedding"],
            metadata={
                "dimensions": 384,
                "version": "1.0.0",
                "description": "Small text embedding model"
            }
        )
        
        await self.registry.register_model(
            model_id="sophia-classification-base",
            model_type="classification",
            provider="local",
            capabilities=["text_classification", "intent_detection"],
            metadata={
                "classes": ["intent", "entity", "sentiment"],
                "version": "1.0.0",
                "description": "Base text classification model"
            }
        )
        
    async def start(self) -> bool:
        """
        Start the ML engine and load default models.
        
        Returns:
            True if successful
        """
        if not self.is_initialized:
            success = await self.initialize()
            if not success:
                logger.error("Failed to initialize ML Engine")
                return False
                
        logger.info("Starting Sophia ML Engine...")
        
        # Load default models
        for model_type, model_id in self.registry.default_models.items():
            if model_id is not None:
                await self.registry.load_model(model_id)
        
        logger.info("Sophia ML Engine started successfully")
        return True
        
    async def stop(self) -> bool:
        """
        Stop the ML engine and unload all models.
        
        Returns:
            True if successful
        """
        logger.info("Stopping Sophia ML Engine...")
        
        # Unload all active models
        active_models = list(self.registry.active_models.keys())
        for model_id in active_models:
            await self.registry.unload_model(model_id)
            
        logger.info("Sophia ML Engine stopped successfully")
        return True
        
    async def embed_text(self, text: str, model_id: Optional[str] = None) -> List[float]:
        """
        Generate embeddings for a text string.
        
        Args:
            text: The text to embed
            model_id: ID of the embedding model to use (optional)
            
        Returns:
            List of embedding values
        """
        # Use default embedding model if none specified
        if model_id is None:
            model_id = self.registry.get_default_model("embedding")
            if model_id is None:
                raise ValueError("No embedding model available")
                
        # Check if model is loaded
        if model_id not in self.registry.active_models:
            await self.registry.load_model(model_id)
            
        # This would normally use the actual model to generate embeddings
        # For now, return a dummy embedding
        logger.info(f"Generated embeddings for text using model {model_id}")
        return [0.1] * 10  # Dummy embedding
        
    async def classify_text(self, 
                          text: str, 
                          categories: List[str],
                          model_id: Optional[str] = None) -> Dict[str, float]:
        """
        Classify text into provided categories.
        
        Args:
            text: The text to classify
            categories: List of categories to classify into
            model_id: ID of the classification model to use (optional)
            
        Returns:
            Dictionary mapping categories to confidence scores
        """
        # Use default classification model if none specified
        if model_id is None:
            model_id = self.registry.get_default_model("classification")
            if model_id is None:
                raise ValueError("No classification model available")
                
        # Check if model is loaded
        if model_id not in self.registry.active_models:
            await self.registry.load_model(model_id)
            
        # This would normally use the actual model for classification
        # For now, return dummy classifications
        logger.info(f"Classified text into {len(categories)} categories using model {model_id}")
        return {category: 1.0 / len(categories) for category in categories}
        
    async def get_model_status(self) -> Dict[str, Any]:
        """
        Get the status of all models.
        
        Returns:
            Dictionary with model status information
        """
        return {
            "registered_models": len(self.registry.models),
            "active_models": len(self.registry.active_models),
            "default_models": self.registry.default_models,
            "models": self.registry.models
        }

# Global singleton instance
_engine = MLEngine()

async def get_ml_engine() -> MLEngine:
    """
    Get the global ML engine instance.
    
    Returns:
        MLEngine instance
    """
    if not _engine.is_initialized:
        await _engine.initialize()
    return _engine