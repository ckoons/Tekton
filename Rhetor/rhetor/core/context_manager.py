"""Enhanced context manager for CI interactions.

This module provides a sophisticated context manager for tracking conversations across
components, with support for Engram integration, context windowing, and search capabilities.
"""

import os
from shared.env import TektonEnviron
import logging
import json
import asyncio
import re
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from datetime import datetime
from pathlib import Path
import uuid
import tiktoken

from rhetor.utils.engram_helper import EngramClient, get_engram_client

logger = logging.getLogger(__name__)

class TokenCounter:
    """Utility for counting tokens in text."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """Initialize the token counter.
        
        Args:
            model_name: Name of the model to count tokens for
        """
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # Fall back to cl100k_base for Claude and other models
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in text.
        
        Args:
            text: The text to count tokens for
            
        Returns:
            Token count
        """
        if not text:
            return 0
        
        return len(self.encoding.encode(text))
    
    def count_message_tokens(self, message: Dict[str, Any]) -> int:
        """Count tokens in a message.
        
        Args:
            message: Message dictionary with role and content
            
        Returns:
            Token count
        """
        # Count tokens in the content
        content_tokens = self.count_tokens(message.get("content", ""))
        
        # Add tokens for role and metadata (role + 2 tokens as per OpenAI documentation)
        return content_tokens + 4  # Approximation for all models


class WindowedContext:
    """A windowed view of a conversation context with dynamic token management."""
    
    def __init__(
        self,
        context_id: str,
        max_tokens: int = 4000,
        max_messages: Optional[int] = None,
        token_counter: Optional[TokenCounter] = None,
        summary_method: str = "heuristic"
    ):
        """Initialize a windowed context.
        
        Args:
            context_id: Unique identifier for this context
            max_tokens: Maximum number of tokens to include in the window
            max_messages: Optional maximum number of messages regardless of tokens
            token_counter: Optional token counter instance
            summary_method: Method for generating summaries ("llm" or "heuristic")
        """
        self.context_id = context_id
        self.max_tokens = max_tokens
        self.max_messages = max_messages
        self.token_counter = token_counter or TokenCounter()
        self.summary_method = summary_method
        
        self.messages: List[Dict[str, Any]] = []
        self.archived_messages: List[Dict[str, Any]] = []
        self.summaries: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.total_token_count = 0
    
    def add_message(self, message: Dict[str, Any]) -> None:
        """Add a message to the context, managing window as needed.
        
        Args:
            message: Message to add
        """
        # Calculate tokens for this message
        tokens = self.token_counter.count_message_tokens(message)
        
        # If this single message is larger than the window, truncate it
        if tokens > self.max_tokens:
            # Truncate content to fit within window
            content = message["content"]
            while tokens > self.max_tokens:
                content = content[:int(len(content) * 0.8)]  # Cut 20% each time
                message["content"] = content
                message["metadata"] = message.get("metadata", {}) or {}
                message["metadata"]["truncated"] = True
                tokens = self.token_counter.count_message_tokens(message)
        
        # Add message to history
        self.messages.append(message)
        self.total_token_count += tokens
        
        # Update timestamp
        self.updated_at = datetime.now().isoformat()
        
        # Check if we need to trim the window
        self._manage_window()
    
    def _manage_window(self) -> None:
        """Manage the context window based on token limits and message count."""
        # Handle max messages limit if specified
        if self.max_messages and len(self.messages) > self.max_messages:
            # Move oldest messages to archived
            overflow = len(self.messages) - self.max_messages
            self._archive_messages(overflow)
        
        # Handle token count limit
        while self.total_token_count > self.max_tokens and len(self.messages) > 1:
            # Always keep at least one message
            self._archive_messages(1)
    
    def _archive_messages(self, count: int) -> None:
        """Archive the oldest messages from the active window.
        
        Args:
            count: Number of messages to archive
        """
        if count <= 0 or not self.messages:
            return
        
        # Limit count to available messages (keep at least 1)
        count = min(count, len(self.messages) - 1) if len(self.messages) > 1 else 0
        if count == 0:
            return
        
        # Get messages to archive
        to_archive = self.messages[:count]
        
        # Generate summary if needed
        if to_archive:
            summary = self._summarize_messages(to_archive)
            if summary:
                self.summaries.append(summary)
        
        # Move messages to archived
        self.archived_messages.extend(to_archive)
        
        # Update active messages
        self.messages = self.messages[count:]
        
        # Recalculate token count for remaining messages
        self._recalculate_token_count()
    
    def _recalculate_token_count(self) -> None:
        """Recalculate the total token count for current messages."""
        self.total_token_count = sum(
            self.token_counter.count_message_tokens(msg)
            for msg in self.messages
        )
    
    def _summarize_messages(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a summary of archived messages.
        
        Args:
            messages: List of messages to summarize
            
        Returns:
            Summary dictionary
        """
        if not messages:
            return None
        
        if self.summary_method == "llm":
            # This would call an LLM to generate a proper summary
            # Implemented in ContextManager to avoid circular dependencies
            return {
                "type": "summary_placeholder",
                "message_count": len(messages),
                "time_range": f"{messages[0]['timestamp']} to {messages[-1]['timestamp']}",
                "summary": "Messages archived (LLM summary pending)",
                "summary_method": "llm_pending"
            }
        else:
            # Create a heuristic summary
            user_msgs = [m for m in messages if m["role"] == "user"]
            system_msgs = [m for m in messages if m["role"] == "system"]
            assistant_msgs = [m for m in messages if m["role"] == "assistant"]
            
            # Extract potential topics from user messages
            topics = set()
            for msg in user_msgs:
                # Simple keyword extraction - split on spaces and keep 3+ character words
                content = msg.get("content", "")
                words = re.findall(r'\b\w{3,}\b', content.lower())
                # Take the most frequent non-common words
                stop_words = {"the", "and", "for", "this", "that", "with", "from"}
                topics.update([w for w in words if w not in stop_words][:5])
            
            return {
                "id": str(uuid.uuid4()),
                "type": "summary",
                "timestamp": datetime.now().isoformat(),
                "message_count": len(messages),
                "user_message_count": len(user_msgs),
                "assistant_message_count": len(assistant_msgs),
                "system_message_count": len(system_msgs),
                "time_range": f"{messages[0]['timestamp']} to {messages[-1]['timestamp']}",
                "topics": list(topics)[:5],  # Top 5 potential topics
                "summary": f"Archived {len(messages)} messages ({len(user_msgs)} from user, {len(assistant_msgs)} from assistant)",
                "summary_method": "heuristic"
            }
    
    def get_formatted_messages(
        self,
        provider: str = "anthropic",
        include_summaries: bool = True
    ) -> List[Dict[str, str]]:
        """Get provider-formatted messages for the current window.
        
        Args:
            provider: Provider name (anthropic, openai, ollama)
            include_summaries: Whether to include summaries of archived messages
            
        Returns:
            List of formatted messages for the provider
        """
        formatted = []
        
        # Add summaries if requested
        if include_summaries and self.summaries:
            # Combine summaries into a single system message
            summary_texts = []
            for summary in self.summaries:
                text = f"Previous conversation: {summary['summary']}"
                if "topics" in summary and summary["topics"]:
                    text += f" Topics: {', '.join(summary['topics'])}"
                summary_texts.append(text)
            
            # Add as a system message
            formatted.append({
                "role": "system", 
                "content": "Context summaries:\n" + "\n".join(summary_texts)
            })
        
        # Add current messages
        for msg in self.messages:
            role = msg["role"]
            # Standardize roles for providers
            if provider in ["anthropic", "openai"] and role not in ["user", "assistant", "system"]:
                role = "user"  # Default non-standard roles to user
            formatted.append({"role": role, "content": msg["content"]})
        
        return formatted
    
    def to_dict(self, include_archived: bool = False) -> Dict[str, Any]:
        """Convert to a dictionary for serialization.
        
        Args:
            include_archived: Whether to include archived messages
            
        Returns:
            Dictionary representation
        """
        result = {
            "context_id": self.context_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": self.messages,
            "summaries": self.summaries,
            "metadata": self.metadata,
            "total_token_count": self.total_token_count,
            "max_tokens": self.max_tokens
        }
        
        if include_archived:
            result["archived_messages"] = self.archived_messages
        
        return result
    
    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        token_counter: Optional[TokenCounter] = None
    ) -> 'WindowedContext':
        """Create from a dictionary.
        
        Args:
            data: Dictionary representation
            token_counter: Optional token counter to use
            
        Returns:
            WindowedContext instance
        """
        context = cls(
            context_id=data["context_id"],
            max_tokens=data.get("max_tokens", 4000),
            token_counter=token_counter
        )
        
        context.created_at = data.get("created_at", context.created_at)
        context.updated_at = data.get("updated_at", context.updated_at)
        context.messages = data.get("messages", [])
        context.archived_messages = data.get("archived_messages", [])
        context.summaries = data.get("summaries", [])
        context.metadata = data.get("metadata", {})
        
        # Recalculate token count
        context._recalculate_token_count()
        
        return context


class ContextManager:
    """Enhanced manager for CI contexts across components with advanced features."""
    
    def __init__(
        self,
        engram_client: Optional[EngramClient] = None,
        llm_client = None,
        token_counter: Optional[TokenCounter] = None,
        default_max_tokens: int = 4000,
        default_max_messages: int = 20
    ):
        """Initialize the context manager.
        
        Args:
            engram_client: Optional Engram client for persistent storage
            llm_client: Optional LLM client for summarization
            token_counter: Optional token counter for token tracking
            default_max_tokens: Default maximum tokens per context
            default_max_messages: Default maximum messages per context
        """
        self.contexts: Dict[str, WindowedContext] = {}
        self.engram_client = engram_client
        self.llm_client = llm_client
        self.token_counter = token_counter or TokenCounter()
        self.default_max_tokens = default_max_tokens
        self.default_max_messages = default_max_messages
        
        # Directory for local persistence
        default_context_dir = os.path.join(
            TektonEnviron.get('TEKTON_DATA_DIR', 
                          os.path.join(TektonEnviron.get('TEKTON_ROOT', os.path.expanduser('~')), '.tekton', 'data')),
            'rhetor', 'contexts'
        )
        self.persistence_dir = TektonEnviron.get("RHETOR_CONTEXT_DIR", default_context_dir)
        os.makedirs(self.persistence_dir, exist_ok=True)
        
        # Track loading stats to avoid excessive logging
        self._last_load_log_time = 0
        self._total_loads = 0
        self._contexts_loaded = False
    
    async def initialize(self) -> None:
        """Initialize the context manager with clients and load contexts."""
        # Set up Engram client if not provided
        if not self.engram_client:
            try:
                self.engram_client = await get_engram_client()
            except Exception as e:
                logger.warning(f"Failed to initialize Engram client: {e}")
                self.engram_client = None
        
        # Load contexts
        await self.load_all_contexts()
    
    async def get_or_create_context(
        self,
        context_id: str,
        max_tokens: Optional[int] = None,
        max_messages: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> WindowedContext:
        """Get or create a context by ID.
        
        Args:
            context_id: Context identifier
            max_tokens: Maximum tokens for this context
            max_messages: Maximum messages for this context
            metadata: Optional metadata for new contexts
            
        Returns:
            WindowedContext object
        """
        if context_id in self.contexts:
            # Update metadata if provided
            if metadata:
                self.contexts[context_id].metadata.update(metadata)
            
            return self.contexts[context_id]
        
        # Try to load from Engram if available
        context_data = None
        if self.engram_client:
            try:
                context_data = await self.engram_client.get_memory(
                    namespace="rhetor_contexts",
                    key=context_id
                )
                if context_data:
                    context = WindowedContext.from_dict(
                        context_data,
                        token_counter=self.token_counter
                    )
                    self.contexts[context_id] = context
                    logger.info(f"Loaded context {context_id} from Engram")
                    
                    # Update metadata if provided
                    if metadata:
                        context.metadata.update(metadata)
                    
                    return context
            except Exception as e:
                logger.warning(f"Error loading context from Engram: {e}")
        
        # Try to load from local file
        if not context_data:
            try:
                file_path = os.path.join(self.persistence_dir, f"{context_id}.json")
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        context_data = json.load(f)
                    
                    context = WindowedContext.from_dict(
                        context_data,
                        token_counter=self.token_counter
                    )
                    self.contexts[context_id] = context
                    logger.info(f"Loaded context {context_id} from local file")
                    
                    # Update metadata if provided
                    if metadata:
                        context.metadata.update(metadata)
                    
                    return context
            except Exception as e:
                logger.warning(f"Error loading context from file: {e}")
        
        # Create new context if not found
        context = WindowedContext(
            context_id=context_id,
            max_tokens=max_tokens or self.default_max_tokens,
            max_messages=max_messages or self.default_max_messages,
            token_counter=self.token_counter
        )
        
        # Set metadata
        component = context_id.split(":")[0] if ":" in context_id else "unknown"
        context.metadata = {
            "component": component,
            **(metadata or {})
        }
        
        # Store in memory
        self.contexts[context_id] = context
        logger.info(f"Created new context {context_id}")
        
        return context
    
    async def add_to_context(
        self, 
        context_id: str, 
        role: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> WindowedContext:
        """Add a message to the context.
        
        Args:
            context_id: Context identifier
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Additional metadata for the message
            
        Returns:
            Updated WindowedContext
        """
        # Get or create the context
        context = await self.get_or_create_context(context_id)
        
        # Create the message
        message = {
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Add to context
        context.add_message(message)
        
        # Persist to storage
        await self._persist_context(context_id)
        
        # NEW: Monitor stress for CI contexts
        if role == 'assistant' and (
            context_id.endswith('-ci') or 
            context_id in ['apollo', 'athena', 'rhetor', 'numa', 'synthesis', 'metis', 
                          'harmonia', 'noesis', 'engram', 'penia', 'hermes', 'ergon', 
                          'sophia', 'telos', 'prometheus']
        ):
            try:
                from .stress_monitor import get_stress_monitor
                monitor = get_stress_monitor()
                
                # Analyze stress
                analysis = await monitor.analyze_context_stress(
                    context_id,
                    context,
                    output={'content': content, 'role': role}
                )
                
                # Whisper to Apollo if needed
                if monitor.should_whisper(analysis):
                    await monitor.whisper_to_apollo(analysis)
                    logger.debug(f"Stress monitor whispered about {context_id}: "
                               f"stress={analysis['stress']:.2f}")
            except Exception as e:
                # Don't fail the context update if monitoring fails
                logger.warning(f"Stress monitoring failed: {e}")
        
        return context
    
    async def get_context_history(
        self, 
        context_id: str, 
        include_archived: bool = False,
        include_summaries: bool = True,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get the message history for a context.
        
        Args:
            context_id: Context identifier
            include_archived: Whether to include archived messages
            include_summaries: Whether to include summaries
            limit: Maximum number of messages to return
            
        Returns:
            List of message dictionaries
        """
        context = await self.get_or_create_context(context_id)
        
        result = []
        
        # Add summaries if requested
        if include_summaries and context.summaries:
            for summary in context.summaries:
                # Convert summary to message format
                result.append({
                    "id": summary.get("id", str(uuid.uuid4())),
                    "role": "system",
                    "content": summary.get("summary", "Previous conversation archived"),
                    "timestamp": summary.get("timestamp", datetime.now().isoformat()),
                    "metadata": {
                        "type": "summary",
                        "message_count": summary.get("message_count", 0),
                        "user_message_count": summary.get("user_message_count", 0),
                        "assistant_message_count": summary.get("assistant_message_count", 0),
                        "time_range": summary.get("time_range", ""),
                        "topics": summary.get("topics", [])
                    }
                })
        
        # Add archived messages if requested
        if include_archived:
            result.extend(context.archived_messages)
        
        # Add active messages
        result.extend(context.messages)
        
        # Apply limit if specified
        if limit and limit > 0 and len(result) > limit:
            result = result[-limit:]
        
        return result
    
    async def get_formatted_history(
        self, 
        context_id: str, 
        provider: str = "anthropic",
        include_summaries: bool = True
    ) -> List[Dict[str, str]]:
        """Get provider-formatted conversation history.
        
        Args:
            context_id: Context identifier
            provider: Provider format to use (anthropic, openai, ollama)
            include_summaries: Whether to include summaries
            
        Returns:
            Formatted messages for the provider
        """
        context = await self.get_or_create_context(context_id)
        return context.get_formatted_messages(provider, include_summaries)
    
    async def generate_summary_with_llm(
        self,
        context_id: str,
        messages: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Generate a summary of messages using an LLM.
        
        Args:
            context_id: Context identifier
            messages: Messages to summarize
            
        Returns:
            Summary dictionary or None if failed
        """
        if not self.llm_client or not messages:
            return None
        
        try:
            # Extract basic metadata
            message_count = len(messages)
            user_messages = [m for m in messages if m["role"] == "user"]
            assistant_messages = [m for m in messages if m["role"] == "assistant"]
            
            # Create the prompt for summarization
            prompt = (
                "Summarize the following conversation messages in a concise paragraph "
                "focusing on key points and topics discussed. Extract 3-5 main topics.\n\n"
            )
            
            # Add messages to the prompt
            for msg in messages:
                prompt += f"[{msg['role']}]: {msg['content'][:500]}...\n\n"
            
            # Get summary from LLM
            result = await self.llm_client.complete(
                message=prompt,
                context_id=f"summary_{context_id}",
                system_prompt="You are a summarization assistant. Create concise, accurate summaries.",
                provider_id="anthropic",  # Use default provider
                model_id=None,  # Use default model
                streaming=False,
                options={"temperature": 0.3, "max_tokens": 300}
            )
            
            if result and "message" in result:
                summary_text = result["message"]
                
                # Extract topics using simple regex
                topic_match = re.search(r"Topics:?\s*(.*?)(?:\n|$)", summary_text, re.IGNORECASE)
                topics = []
                if topic_match:
                    topics_text = topic_match.group(1)
                    # Split on commas or bullet points
                    topics = [t.strip().strip('•-*') for t in re.split(r'[,•\n]', topics_text)]
                    topics = [t for t in topics if t]  # Remove empty
                
                # Create summary object
                return {
                    "id": str(uuid.uuid4()),
                    "type": "summary",
                    "timestamp": datetime.now().isoformat(),
                    "message_count": message_count,
                    "user_message_count": len(user_messages),
                    "assistant_message_count": len(assistant_messages),
                    "time_range": f"{messages[0]['timestamp']} to {messages[-1]['timestamp']}",
                    "summary": summary_text,
                    "topics": topics,
                    "summary_method": "llm"
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error generating summary with LLM: {e}")
            return None
    
    async def search_context(
        self,
        context_id: str,
        query: str,
        search_archived: bool = True,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for messages in a context.
        
        Args:
            context_id: Context identifier
            query: Search query string
            search_archived: Whether to include archived messages
            limit: Maximum number of results
            
        Returns:
            List of matching messages with scores
        """
        context = await self.get_or_create_context(context_id)
        
        # Get messages to search
        messages = list(context.messages)
        if search_archived:
            messages = context.archived_messages + messages
        
        # Simple regex-based search
        results = []
        for msg in messages:
            content = msg.get("content", "").lower()
            query_lower = query.lower()
            
            # Check if query is in content
            if query_lower in content:
                # Simple scoring based on occurrence count and position
                count = content.count(query_lower)
                position = content.find(query_lower) / len(content) if content else 1.0
                
                # Higher score for earlier occurrences and multiple occurrences
                score = (1.0 - position * 0.5) + (count * 0.1)
                
                results.append({
                    "message": msg,
                    "score": min(score, 1.0)  # Cap at 1.0
                })
        
        # Sort by score (descending) and limit results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    async def get_context_summary(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of the context without full message history.
        
        Args:
            context_id: Context identifier
            
        Returns:
            Context summary dictionary
        """
        try:
            context = await self.get_or_create_context(context_id)
            
            # Collect the most recent summary
            latest_summary = None
            if context.summaries:
                latest_summary = context.summaries[-1].get("summary", "")
            
            # Return summary metadata
            return {
                "id": context_id,
                "created_at": context.created_at,
                "updated_at": context.updated_at,
                "active_message_count": len(context.messages),
                "archived_message_count": len(context.archived_messages),
                "total_messages": len(context.messages) + len(context.archived_messages),
                "summary_count": len(context.summaries),
                "latest_summary": latest_summary,
                "token_count": context.total_token_count,
                "metadata": context.metadata
            }
        except Exception as e:
            logger.error(f"Error getting context summary: {e}")
            return None
    
    async def _persist_context(self, context_id: str) -> bool:
        """Persist a context to storage.
        
        Args:
            context_id: Context identifier
            
        Returns:
            Success status
        """
        if context_id not in self.contexts:
            return False
        
        context = self.contexts[context_id]
        context_data = context.to_dict(include_archived=True)
        success = True
        
        # Persist to Engram if available
        if self.engram_client:
            try:
                await self.engram_client.store_memory(
                    namespace="rhetor_contexts",
                    key=context_id,
                    data=context_data
                )
            except Exception as e:
                logger.warning(f"Error storing context to Engram: {e}")
                success = False
        
        # Persist to local file
        try:
            file_path = os.path.join(self.persistence_dir, f"{context_id}.json")
            with open(file_path, 'w') as f:
                json.dump(context_data, f, indent=2)
            logger.debug(f"Persisted context {context_id} to local file")
        except Exception as e:
            logger.warning(f"Error storing context to file: {e}")
            success = False
        
        return success
    
    async def load_all_contexts(self) -> int:
        """Load all persisted contexts.
        
        Returns:
            Number of contexts loaded
        """
        count = 0
        
        # Load from local files
        try:
            for filename in os.listdir(self.persistence_dir):
                if filename.endswith('.json'):
                    context_id = filename[:-5]  # Remove .json
                    file_path = os.path.join(self.persistence_dir, filename)
                    
                    try:
                        with open(file_path, 'r') as f:
                            context_data = json.load(f)
                            
                            # Create context from data
                            context = WindowedContext.from_dict(
                                context_data,
                                token_counter=self.token_counter
                            )
                            
                            self.contexts[context_id] = context
                            count += 1
                    except Exception as e:
                        logger.warning(f"Error loading context from {file_path}: {e}")
        except Exception as e:
            logger.warning(f"Error loading contexts from directory: {e}")
        
        # Update load tracking
        self._total_loads += 1
        self._contexts_loaded = True
        
        # Only log at INFO level once per hour or on first load
        current_time = datetime.now().timestamp()
        if self._total_loads == 1 or (current_time - self._last_load_log_time) >= 3600:
            logger.info(f"Loaded {count} contexts from local files (total loads: {self._total_loads})")
            self._last_load_log_time = current_time
        else:
            # Use debug level for routine loads
            logger.debug(f"Loaded {count} contexts from local files")
        
        return count
    
    async def delete_context(self, context_id: str) -> bool:
        """Delete a context.
        
        Args:
            context_id: Context identifier
            
        Returns:
            Success status
        """
        success = True
        
        # Remove from memory
        if context_id in self.contexts:
            del self.contexts[context_id]
        
        # Remove from Engram if available
        if self.engram_client:
            try:
                await self.engram_client.delete_memory(
                    namespace="rhetor_contexts",
                    key=context_id
                )
            except Exception as e:
                logger.warning(f"Error deleting context from Engram: {e}")
                success = False
        
        # Remove local file
        try:
            file_path = os.path.join(self.persistence_dir, f"{context_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted context file for {context_id}")
        except Exception as e:
            logger.warning(f"Error deleting context file: {e}")
            success = False
        
        return success
    
    async def list_contexts(self, component: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all available contexts with summary info.
        
        Args:
            component: Optional component filter
            
        Returns:
            List of context summary dictionaries
        """
        # Load contexts if not already loaded
        if not self.contexts:
            await self.load_all_contexts()
        
        # Prepare summary list
        summaries = []
        for context_id, context in self.contexts.items():
            # Apply component filter if specified
            if component:
                ctx_component = context.metadata.get("component", "").lower()
                if ctx_component != component.lower() and not context_id.lower().startswith(f"{component.lower()}:"):
                    continue
            
            # Get summary
            summary = await self.get_context_summary(context_id)
            if summary:
                summaries.append(summary)
        
        # Sort by updated_at (newest first)
        summaries.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        
        return summaries
    
    async def search_all_contexts(
        self,
        query: str,
        component: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search across all contexts.
        
        Args:
            query: Search query
            component: Optional component filter
            limit: Maximum number of results per context
            
        Returns:
            List of matching messages with context info
        """
        # Load contexts if not already loaded
        if not self.contexts:
            await self.load_all_contexts()
        
        all_results = []
        
        # Search each context
        for context_id, context in self.contexts.items():
            # Apply component filter if specified
            if component:
                ctx_component = context.metadata.get("component", "").lower()
                if ctx_component != component.lower() and not context_id.lower().startswith(f"{component.lower()}:"):
                    continue
            
            # Search this context
            results = await self.search_context(context_id, query, search_archived=True, limit=limit)
            
            # Add context info to results
            for result in results:
                result["context_id"] = context_id
                result["context_metadata"] = context.metadata
            
            all_results.extend(results)
        
        # Sort by score (descending)
        all_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top results
        return all_results[:limit]
    
    async def merge_contexts(
        self,
        target_id: str,
        source_ids: List[str],
        max_messages: Optional[int] = None
    ) -> Optional[WindowedContext]:
        """Merge multiple contexts into a target context.
        
        Args:
            target_id: Target context ID (will be created if doesn't exist)
            source_ids: List of source context IDs to merge
            max_messages: Optional maximum number of messages to keep
            
        Returns:
            Merged context or None if failed
        """
        # Check if all source contexts exist
        for source_id in source_ids:
            if source_id not in self.contexts:
                logger.warning(f"Source context {source_id} not found for merging")
                return None
        
        # Create or get target context
        target = await self.get_or_create_context(
            context_id=target_id,
            max_messages=max_messages or self.default_max_messages
        )
        
        # Combine metadata from all sources
        combined_metadata = {}
        for source_id in source_ids:
            source = self.contexts[source_id]
            combined_metadata.update(source.metadata)
        
        # Update target metadata (keeping original component)
        component = target.metadata.get("component")
        target.metadata.update(combined_metadata)
        if component:
            target.metadata["component"] = component
        
        # Add a special merged context marker
        target.metadata["merged_from"] = source_ids
        target.metadata["merged_at"] = datetime.now().isoformat()
        
        # Combine messages from all sources, sorted by timestamp
        all_messages = []
        for source_id in source_ids:
            source = self.contexts[source_id]
            all_messages.extend(source.archived_messages)
            all_messages.extend(source.messages)
        
        # Sort messages by timestamp
        all_messages.sort(key=lambda x: x.get("timestamp", ""))
        
        # Clear existing messages
        target.messages = []
        target.archived_messages = []
        target.summaries = []
        target._recalculate_token_count()
        
        # Add messages to target (will automatically manage windowing)
        for message in all_messages:
            target.add_message(message)
        
        # Persist the merged context
        await self._persist_context(target_id)
        
        return target
    
    async def set_llm_client(self, llm_client) -> None:
        """Set the LLM client for summarization.
        
        Args:
            llm_client: LLM client instance
        """
        self.llm_client = llm_client