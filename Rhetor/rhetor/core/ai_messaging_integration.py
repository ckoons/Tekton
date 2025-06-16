"""
AI Messaging Integration for Rhetor with Hermes Message Bus.

This module integrates AI specialist communication with Hermes's message bus,
enabling AI-to-AI conversations across Tekton components.
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

# Standard logging - removed debug_log import
from .ai_specialist_manager import AISpecialistManager, AIMessage

logger = logging.getLogger(__name__)

class AIMessagingIntegration:
    """
    Integrates AI specialist communication with Hermes message bus.
    
    This class enables Rhetor's AI specialists to communicate with each other
    and with AI specialists in other Tekton components through Hermes.
    """
    
    def __init__(self, specialist_manager: AISpecialistManager, hermes_url: str = "http://localhost:8001", specialist_router=None):
        """
        Initialize AI messaging integration.
        
        Args:
            specialist_manager: AI specialist manager instance
            hermes_url: Hermes service URL
            specialist_router: Optional specialist router instance
        """
        self.specialist_manager = specialist_manager
        self.hermes_url = hermes_url
        self.specialist_router = specialist_router
        self.session: Optional[aiohttp.ClientSession] = None
        self.conversation_ids: Dict[str, Any] = {}  # conversation_id -> info
        self.message_handlers: Dict[str, Callable] = {}  # specialist_id -> handler
        self.hermes_client = None  # Will be initialized in initialize()
        
        logger.info("Initialized AI Messaging Integration")
        
    async def initialize(self):
        """Initialize the messaging integration."""
        # Create HTTP session for Hermes communication
        self.session = aiohttp.ClientSession()
        
        # Initialize message handlers for each specialist
        for spec_id in self.specialist_manager.specialists:
            self.message_handlers[spec_id] = self._create_message_handler(spec_id)
            
        logger.info("AI Messaging Integration initialized")
        
    async def cleanup(self):
        """Cleanup resources."""
        if self.session:
            await self.session.close()
            
    async def send_specialist_message(self, from_specialist: str, to_specialist: str, 
                                     content: str, context: Optional[Dict[str, Any]] = None):
        """
        Send a message from one specialist to another.
        
        Routes through Hermes for cross-component communication when needed.
        
        Args:
            from_specialist: Source specialist ID
            to_specialist: Target specialist ID  
            content: Message content
            context: Optional context
        """
        # Determine if specialists are in different components
        from_config = self.specialist_manager.specialists.get(from_specialist)
        to_config = self.specialist_manager.specialists.get(to_specialist)
        
        if from_config and to_config and from_config.component_id != to_config.component_id:
            # Cross-component communication through Hermes message bus
            logger.info(f"Cross-component message: {from_specialist} ({from_config.component_id}) -> {to_specialist} ({to_config.component_id})")
            
            # Publish to Hermes message bus
            await self._publish_to_hermes(
                topic=f"ai.specialist.{to_config.component_id}",
                message={
                    "from": from_specialist,
                    "to": to_specialist,
                    "content": content,
                    "context": context or {},
                    "timestamp": datetime.now().isoformat()
                }
            )
        else:
            # Internal messaging within same component
            await self.specialist_manager.send_message(
                sender_id=from_specialist,
                receiver_id=to_specialist,
                content=content,
                message_type="specialist_chat"
            )
        
    async def create_ai_conversation(self, topic: str, initial_specialists: List[str]) -> str:
        """
        Create a new AI-to-AI conversation.
        
        Args:
            topic: Conversation topic
            initial_specialists: List of specialist IDs to include
            
        Returns:
            Conversation ID
        """
        logger.info(f"Creating AI conversation: {topic}")
        
        # Generate conversation ID
        conversation_id = f"ai-conv-{int(asyncio.get_event_loop().time())}-{hash(topic) % 10000}"
        
        # Store conversation info
        self.conversation_ids[conversation_id] = {
            "topic": topic,
            "participants": initial_specialists,
            "created_at": datetime.now().isoformat(),
            "messages": []
        }
        
        logger.info(f"Created conversation {conversation_id}")
        return conversation_id
        
    async def publish_conversation_message(self, conversation_id: str, sender_id: str, 
                                         content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Publish a message in an AI conversation.
        
        Args:
            conversation_id: Conversation ID
            sender_id: Sender specialist ID
            content: Message content
            metadata: Optional metadata
        """
        if conversation_id not in self.conversation_ids:
            logger.error(f"Unknown conversation: {conversation_id}")
            return
            
        # Add to conversation history
        self.conversation_ids[conversation_id]["messages"].append({
            "sender_id": sender_id,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Added message from {sender_id} to conversation {conversation_id}")
        
    async def orchestrate_team_chat(self, topic: str, specialists: List[str], 
                                   initial_prompt: str, max_rounds: int = 5) -> List[Dict[str, Any]]:
        """
        Orchestrate a team chat between multiple AI specialists.
        
        Args:
            topic: Discussion topic
            specialists: List of specialist IDs
            initial_prompt: Initial prompt to start discussion
            max_rounds: Maximum rounds of discussion
            
        Returns:
            List of messages in the conversation
        """
        logger.info(f"Orchestrating team chat: {topic}")
        
        messages = []
        
        try:
            # Create conversation
            conversation_id = await self.create_ai_conversation(topic, specialists)
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            # Continue without conversation tracking for now
            conversation_id = f"team-chat-{int(asyncio.get_event_loop().time())}"
        
        # Rhetor orchestrator starts the conversation
        orchestrator_prompt = f"""As the AI orchestrator, I'm facilitating a discussion on: {topic}

Initial prompt: {initial_prompt}

Participating specialists: {', '.join(specialists)}

Please provide your insights on this topic."""

        messages.append({
            "sender": "rhetor-orchestrator",
            "content": orchestrator_prompt,
            "timestamp": datetime.now().isoformat()
        })
        
        # Get responses from each specialist
        for round_num in range(max_rounds):
            for specialist_id in specialists:
                if specialist_id not in self.specialist_manager.specialists:
                    continue
                    
                # Build context from previous messages
                previous_messages = [
                    {"role": "assistant" if msg["sender"] != "user" else "user", 
                     "content": f"{msg['sender']}: {msg['content']}"}
                    for msg in messages[-5:]  # Last 5 messages for context
                ]
                
                # Generate specialist response
                response = await self._generate_specialist_response(
                    specialist_id=specialist_id,
                    topic=topic,
                    prompt=f"Continue the discussion. Previous context:\n" + 
                           "\n".join([f"{msg['sender']}: {msg['content'][:100]}..." for msg in messages[-3:]]),
                    previous_messages=previous_messages
                )
                
                messages.append({
                    "sender": specialist_id,
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Store in conversation
                await self.publish_conversation_message(
                    conversation_id=conversation_id,
                    sender_id=specialist_id,
                    content=response
                )
                
            # Check if we should continue
            if round_num < max_rounds - 1:
                # Ask orchestrator if more discussion is needed
                orchestrator_check = await self._generate_orchestrator_summary(messages, topic)
                if "sufficient discussion" in orchestrator_check.lower():
                    break
                    
        logger.info(f"Team chat complete with {len(messages)} messages")
        return messages
        
    async def _generate_specialist_response(self, specialist_id: str, topic: str, 
                                          prompt: str, previous_messages: List[Dict[str, Any]]) -> str:
        """Generate a response from a specialist using actual AI."""
        config = self.specialist_manager.specialists.get(specialist_id)
        if not config:
            return f"Error: Specialist {specialist_id} not found"
            
        try:
            # Get the model for this specialist
            if not self.specialist_router:
                logger.error("Specialist router not initialized")
                return "Error: Specialist router not available"
            model = self.specialist_router.get_model_for_specialist(config.specialist_type)
            
            # Build system prompt from personality
            system_prompt = f"""You are {config.personality.get('role', specialist_id)}.
Your traits: {', '.join(config.personality.get('traits', []))}
Your communication style: {config.personality.get('communication_style', 'professional')}
Your expertise: {', '.join(config.personality.get('expertise', []))}

You are participating in a discussion about: {topic}"""

            # Use the specialist router to generate response
            response = await self.specialist_router.route_request(
                message=prompt,
                context_id=f"team_chat_{specialist_id}",
                component=config.component_id,
                system_prompt=system_prompt,
                streaming=False,
                override_config={
                    "provider": "anthropic",
                    "model": model,
                    "options": {
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                }
            )
            
            if response.get("error"):
                return f"Error generating response: {response['error']}"
                
            return response.get("message", "No response generated")
            
        except Exception as e:
            logger.error(f"Error generating AI response for {specialist_id}: {e}")
            return f"Error: {str(e)}"
            
    async def _generate_orchestrator_summary(self, messages: List[Dict[str, Any]], topic: str) -> str:
        """Generate an orchestrator summary of the discussion."""
        try:
            summary_prompt = f"""As the AI orchestrator, summarize the discussion so far on: {topic}

Messages exchanged: {len(messages)}
Participants: {', '.join(set(msg['sender'] for msg in messages))}

Has there been sufficient discussion to reach useful insights, or should the conversation continue?"""

            response = await self.specialist_router.route_request(
                message=summary_prompt,
                context_id="team_chat_orchestrator",
                component="rhetor",
                system_prompt="You are the Rhetor AI Orchestrator, responsible for managing AI team discussions.",
                streaming=False,
                override_config={
                    "provider": "anthropic", 
                    "model": "claude-3-opus-20240229",
                    "options": {
                        "temperature": 0.5,
                        "max_tokens": 200
                    }
                }
            )
            
            return response.get("message", "Unable to generate summary")
            
        except Exception as e:
            logger.error(f"Error generating orchestrator summary: {e}")
            return "Error generating summary"
            
    def _create_message_handler(self, specialist_id: str) -> Callable:
        """Create a message handler for a specialist."""
        async def handler(message: Dict[str, Any]):
            """Handle incoming messages for a specialist."""
            try:
                # Extract message details
                from_specialist = message.get("from")
                content = message.get("content")
                context = message.get("context", {})
                
                logger.info(f"Specialist {specialist_id} received message from {from_specialist}")
                
                # Process through specialist manager
                await self.specialist_manager.send_message(
                    sender_id=from_specialist,
                    receiver_id=specialist_id,
                    content=content,
                    message_type="specialist_chat"
                )
            except Exception as e:
                logger.error(f"Error handling message for {specialist_id}: {e}")
                
        return handler
        
    async def _publish_to_hermes(self, topic: str, message: Dict[str, Any]):
        """Publish a message to Hermes message bus."""
        # First try the message bus instance if available
        if self.hermes_client and hasattr(self.hermes_client, 'publish'):
            try:
                success = await self.hermes_client.publish_async(
                    topic=topic,
                    message=message,
                    headers={
                        "component_id": "rhetor",
                        "component_type": "rhetor",
                        "timestamp": datetime.now().isoformat()
                    }
                )
                if success:
                    logger.info(f"Successfully published message to topic {topic} via message bus")
                    return
            except Exception as e:
                logger.warning(f"Failed to publish via message bus client: {e}, falling back to REST API")
        
        # Fallback to REST API
        if not self.session:
            logger.error("HTTP session not initialized")
            return
            
        try:
            # Use Hermes REST API to publish message
            url = f"{self.hermes_url}/api/messages/publish"
            headers = {
                "Content-Type": "application/json",
                "X-Component-ID": "rhetor"
            }
            
            payload = {
                "topic": topic,
                "message": message,
                "headers": {
                    "component_id": "rhetor",
                    "component_type": "rhetor",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            async with self.session.post(url, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    logger.info(f"Successfully published message to topic {topic} via REST API")
                else:
                    logger.error(f"Failed to publish to Hermes: {resp.status}")
                    
        except Exception as e:
            logger.error(f"Error publishing to Hermes: {e}")
            
    async def subscribe_to_specialist_topics(self):
        """Subscribe to topics for cross-component specialist communication."""
        # Subscribe to topics for Rhetor specialists in other components
        for spec_id, config in self.specialist_manager.specialists.items():
            if config.component_id == "rhetor":
                # Subscribe to messages for this specialist
                topic = f"ai.specialist.rhetor.{spec_id}"
                # In a real implementation, this would use Hermes client subscription
                logger.info(f"Would subscribe to topic: {topic}")