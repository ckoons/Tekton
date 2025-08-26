"""CI Manager for Rhetor - Managing CI prompts, contexts, and model assignments.

This module provides centralized management for CI (Companion Intelligence) 
configuration, including prompts, contexts, and model assignments.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from rhetor.core.prompt_registry import PromptRegistry, SystemPrompt, PromptVersion
from rhetor.core.context_manager import ContextManager, WindowedContext
from rhetor.utils.engram_helper import get_engram_client

logger = logging.getLogger(__name__)


class CIManager:
    """Manages CI configurations, prompts, and contexts."""
    
    def __init__(
        self,
        prompts_file: Optional[str] = None,
        enable_memory: bool = True
    ):
        """Initialize the CI Manager.
        
        Args:
            prompts_file: Path to CI prompts configuration file
            enable_memory: Whether to enable Engram memory integration
        """
        self.prompt_registry = PromptRegistry()
        self.context_manager = ContextManager()
        self.enable_memory = enable_memory
        
        # Load CI prompts configuration
        if prompts_file:
            self.prompts_config = self._load_prompts_config(prompts_file)
        else:
            # Default path
            default_path = Path(__file__).parent.parent / "prompts" / "ci_prompts.json"
            self.prompts_config = self._load_prompts_config(str(default_path))
        
        # Initialize Engram client if memory is enabled
        self.engram = None
        if self.enable_memory:
            try:
                self.engram = get_engram_client()
                logger.info("Engram memory integration enabled")
            except Exception as e:
                logger.warning(f"Could not initialize Engram: {e}")
                logger.info("CI Manager will work without memory integration")
        
        # Register all CI prompts
        self._register_ci_prompts()
        
        # Track active CI sessions
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Context manager will be initialized when needed
    
    def _load_prompts_config(self, file_path: str) -> Dict[str, Any]:
        """Load CI prompts configuration from file.
        
        Args:
            file_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"CI prompts file not found: {file_path}")
            return {"ci_prompts": {}, "model_assignments": {}}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing CI prompts file: {e}")
            return {"ci_prompts": {}, "model_assignments": {}}
    
    def _register_ci_prompts(self) -> None:
        """Register all CI prompts from configuration."""
        for prompt_key, prompt_config in self.prompts_config.get("ci_prompts", {}).items():
            try:
                # Create system prompt
                system_prompt = SystemPrompt(
                    prompt_id=prompt_config["prompt_id"],
                    name=prompt_config["name"],
                    component=prompt_config["component"],
                    description=prompt_config.get("description"),
                    tags=prompt_config.get("tags", [])
                )
                
                # Create initial version with system prompt
                version = PromptVersion(
                    content=json.dumps(prompt_config["system_prompt"]),
                    metadata={
                        "task": prompt_config.get("task"),
                        "model": prompt_config.get("model"),
                        "context_structure": prompt_config.get("context_structure")
                    },
                    component=prompt_config["component"]
                )
                
                # Add version to prompt
                system_prompt.versions = [version]
                
                # Store prompt in registry (adjust based on actual interface)
                # For now, just store in our own dictionary
                if not hasattr(self, 'ci_prompts'):
                    self.ci_prompts = {}
                self.ci_prompts[prompt_key] = {
                    'system_prompt': system_prompt,
                    'version': version,
                    'config': prompt_config
                }
                logger.info(f"Registered CI prompt: {prompt_config['name']}")
                
            except KeyError as e:
                logger.error(f"Missing required field in prompt config: {e}")
            except Exception as e:
                logger.error(f"Error registering CI prompt: {e}")
    
    def create_ci_session(
        self,
        ci_name: str,
        task: str,
        session_id: Optional[str] = None,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new CI session with appropriate prompt and context.
        
        Args:
            ci_name: Name of the CI (e.g., 'ergon', 'numa')
            task: Task type (e.g., 'construct', 'development')
            session_id: Optional session ID (will generate if not provided)
            initial_context: Optional initial context data
            
        Returns:
            Session ID
        """
        import uuid
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Find appropriate prompt
        prompt_key = f"{ci_name}_{task}"
        prompt_config = self.prompts_config.get("ci_prompts", {}).get(prompt_key)
        
        if not prompt_config:
            logger.warning(f"No prompt found for {ci_name} doing {task}, using defaults")
            prompt_config = self._get_default_prompt_config(ci_name, task)
        
        # Create context for this session
        # For now, create a simple context structure without async
        context = WindowedContext(
            context_id=session_id,
            max_tokens=4000
        )
        
        # Set metadata
        context.metadata = {
            "component": ci_name,
            "task": task,
            "model": prompt_config.get("model"),
            "created_at": datetime.now().isoformat()
        }
        
        # Store in context manager's contexts
        if not hasattr(self.context_manager, 'contexts'):
            self.context_manager.contexts = {}
        self.context_manager.contexts[session_id] = context
        
        # Initialize context with structure
        if initial_context:
            context.metadata.update(initial_context)
        else:
            # Use context structure from prompt config
            context_structure = prompt_config.get("context_structure", {})
            context.metadata.update(context_structure)
        
        # Load relevant memories if Engram is available
        if self.engram and self.enable_memory:
            self._load_relevant_memories(ci_name, task, context)
        
        # Store session information
        self.active_sessions[session_id] = {
            "ci_name": ci_name,
            "task": task,
            "prompt_config": prompt_config,
            "context_id": context.context_id,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        logger.info(f"Created CI session {session_id} for {ci_name} doing {task}")
        return session_id
    
    def get_ci_prompt(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """Get the full prompt for a CI session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Complete prompt with system prompt and context
        """
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"No active session found: {session_id}")
        
        # Get context from stored contexts
        context = self.context_manager.contexts.get(session["context_id"]) if hasattr(self.context_manager, 'contexts') else None
        
        # Build complete prompt
        prompt = {
            "system_prompt": session["prompt_config"].get("system_prompt", {}),
            "context": context.metadata if context else {},
            "model": session["prompt_config"].get("model"),
            "task": session["task"]
        }
        
        # Add conversation history if exists
        if context and context.messages:
            prompt["conversation_history"] = context.messages
        
        return prompt
    
    def update_ci_context(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> None:
        """Update the context for a CI session.
        
        Args:
            session_id: Session ID
            updates: Dictionary of updates to apply
        """
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"No active session found: {session_id}")
        
        # Get context from stored contexts
        context = self.context_manager.contexts.get(session["context_id"]) if hasattr(self.context_manager, 'contexts') else None
        if context:
            # Update metadata
            context.metadata.update(updates)
            
            # Store update in memory if enabled
            if self.engram and self.enable_memory:
                self._store_context_update(session["ci_name"], session["task"], updates)
        
        logger.debug(f"Updated context for session {session_id}")
    
    def add_message_to_session(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a message to a CI session's conversation history.
        
        Args:
            session_id: Session ID
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            metadata: Optional message metadata
        """
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"No active session found: {session_id}")
        
        # Get context from stored contexts
        context = self.context_manager.contexts.get(session["context_id"]) if hasattr(self.context_manager, 'contexts') else None
        if context:
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            if metadata:
                message["metadata"] = metadata
            
            context.add_message(message)
            
            # Store in memory if it's an important exchange
            if self.engram and self.enable_memory and role == "assistant":
                self._store_conversation_memory(
                    session["ci_name"],
                    session["task"],
                    content
                )
    
    def get_model_for_ci(self, ci_name: str) -> str:
        """Get the assigned model for a CI.
        
        Args:
            ci_name: Name of the CI
            
        Returns:
            Model identifier
        """
        model_config = self.prompts_config.get("model_assignments", {}).get(ci_name, {})
        return model_config.get("model", "claude-3-5-sonnet")  # Default
    
    def _load_relevant_memories(
        self,
        ci_name: str,
        task: str,
        context: WindowedContext
    ) -> None:
        """Load relevant memories from Engram for the CI session.
        
        Args:
            ci_name: Name of the CI
            task: Task type
            context: Context to update with memories
        """
        try:
            # Query for relevant memories
            query = f"{ci_name} {task} patterns solutions"
            memories = self.engram.search_memories(
                query=query,
                limit=5,
                filter_metadata={"ci": ci_name, "task": task}
            )
            
            if memories:
                context.metadata["loaded_memories"] = [
                    {
                        "id": mem.get("id"),
                        "content": mem.get("content"),
                        "relevance": mem.get("score")
                    }
                    for mem in memories
                ]
                logger.info(f"Loaded {len(memories)} relevant memories for {ci_name}")
        except Exception as e:
            logger.error(f"Error loading memories: {e}")
    
    def _store_context_update(
        self,
        ci_name: str,
        task: str,
        updates: Dict[str, Any]
    ) -> None:
        """Store context updates in Engram.
        
        Args:
            ci_name: Name of the CI
            task: Task type
            updates: Updates to store
        """
        try:
            self.engram.store_memory(
                content=json.dumps(updates),
                metadata={
                    "ci": ci_name,
                    "task": task,
                    "type": "context_update",
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error storing context update: {e}")
    
    def _store_conversation_memory(
        self,
        ci_name: str,
        task: str,
        content: str
    ) -> None:
        """Store important conversation content in memory.
        
        Args:
            ci_name: Name of the CI
            task: Task type
            content: Content to store
        """
        # Only store if content seems important (has decisions, learnings, etc.)
        important_keywords = ["decided", "learned", "pattern", "solution", "error", "success"]
        if any(keyword in content.lower() for keyword in important_keywords):
            try:
                self.engram.store_memory(
                    content=content,
                    metadata={
                        "ci": ci_name,
                        "task": task,
                        "type": "conversation",
                        "timestamp": datetime.now().isoformat()
                    }
                )
                logger.debug(f"Stored conversation memory for {ci_name}")
            except Exception as e:
                logger.error(f"Error storing conversation memory: {e}")
    
    def _get_default_prompt_config(self, ci_name: str, task: str) -> Dict[str, Any]:
        """Get a default prompt configuration.
        
        Args:
            ci_name: Name of the CI
            task: Task type
            
        Returns:
            Default prompt configuration
        """
        return {
            "prompt_id": f"{ci_name}-{task}-default",
            "name": f"{ci_name.title()} {task.title()}",
            "component": ci_name,
            "task": task,
            "model": self.get_model_for_ci(ci_name),
            "system_prompt": {
                "role": f"You are {ci_name} performing {task}",
                "instructions": "Help the user with their request"
            },
            "context_structure": {}
        }
    
    def end_session(self, session_id: str) -> None:
        """End a CI session and clean up resources.
        
        Args:
            session_id: Session ID to end
        """
        session = self.active_sessions.get(session_id)
        if session:
            session["status"] = "ended"
            session["ended_at"] = datetime.now().isoformat()
            
            # Store final session summary in memory if enabled
            if self.engram and self.enable_memory:
                # Get context from stored contexts
                context = self.context_manager.contexts.get(session["context_id"]) if hasattr(self.context_manager, 'contexts') else None
                if context:
                    self._store_session_summary(
                        session["ci_name"],
                        session["task"],
                        context
                    )
            
            logger.info(f"Ended CI session {session_id}")
    
    def _store_session_summary(
        self,
        ci_name: str,
        task: str,
        context: WindowedContext
    ) -> None:
        """Store a summary of the session in memory.
        
        Args:
            ci_name: Name of the CI
            task: Task type
            context: Session context
        """
        try:
            summary = {
                "ci": ci_name,
                "task": task,
                "duration": context.updated_at,
                "message_count": len(context.messages),
                "key_decisions": context.metadata.get("design_decisions", []),
                "outcome": context.metadata.get("outcome", "completed")
            }
            
            self.engram.store_memory(
                content=json.dumps(summary),
                metadata={
                    "ci": ci_name,
                    "task": task,
                    "type": "session_summary",
                    "timestamp": datetime.now().isoformat()
                }
            )
            logger.info(f"Stored session summary for {ci_name}")
        except Exception as e:
            logger.error(f"Error storing session summary: {e}")