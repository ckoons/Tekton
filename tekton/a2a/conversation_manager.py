"""
Conversation management for multi-agent interactions

This module provides the ConversationManager that handles conversation
lifecycle, message routing, and integration with the channel system.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Set, Any, Callable
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from .conversation import (
    Conversation, ConversationMessage, ConversationRole,
    ConversationState, TurnTakingMode, ConversationParticipant
)
from .streaming.channels import ChannelBridge
from .streaming.events import ChannelEvent, EventType
from .errors import InvalidRequestError, UnauthorizedError, ConversationNotFoundError


logger = logging.getLogger(__name__)


class ConversationManager:
    """Manages multi-agent conversations"""
    
    def __init__(self, channel_bridge: ChannelBridge):
        """
        Initialize the conversation manager.
        
        Args:
            channel_bridge: Bridge to the channel system for message distribution
        """
        self.channel_bridge = channel_bridge
        self.conversations: Dict[str, Conversation] = {}
        self.agent_conversations: Dict[str, Set[str]] = {}  # agent_id -> set of conv_ids
        self._lock = asyncio.Lock()
        self._turn_timers: Dict[str, asyncio.Task] = {}  # conv_id -> timer task
        
    async def create_conversation(
        self,
        topic: str,
        created_by: str,
        description: Optional[str] = None,
        turn_taking_mode: TurnTakingMode = TurnTakingMode.FREE_FORM,
        settings: Optional[Dict[str, Any]] = None,
        initial_participants: Optional[List[Dict[str, str]]] = None
    ) -> Conversation:
        """
        Create a new conversation.
        
        Args:
            topic: The topic/title of the conversation
            created_by: Agent ID creating the conversation
            description: Optional description
            turn_taking_mode: How turns are managed
            settings: Conversation settings
            initial_participants: List of {agent_id, role} dicts
            
        Returns:
            Created conversation
        """
        async with self._lock:
            # Create the conversation
            conversation = Conversation.create(
                topic=topic,
                created_by=created_by,
                description=description,
                turn_taking_mode=turn_taking_mode,
                settings=settings
            )
            
            # Store conversation
            self.conversations[conversation.id] = conversation
            
            # Track creator's conversations
            if created_by not in self.agent_conversations:
                self.agent_conversations[created_by] = set()
            self.agent_conversations[created_by].add(conversation.id)
            
            # Create underlying channel
            await self.channel_bridge.enhance_channel(
                conversation.channel_name,
                created_by,
                description=f"Conversation: {topic}"
            )
            
            # Add initial participants if provided
            if initial_participants:
                for participant_info in initial_participants:
                    agent_id = participant_info["agent_id"]
                    role = ConversationRole(participant_info.get("role", "participant"))
                    
                    if agent_id != created_by:  # Creator already added
                        await self._add_participant_internal(
                            conversation,
                            agent_id,
                            role
                        )
            
            # Activate conversation
            conversation.activate()
            
            # Broadcast conversation created event
            await self._broadcast_event(
                conversation,
                "conversation.created",
                {
                    "conversation": conversation.to_summary(),
                    "created_by": created_by
                }
            )
            
            logger.info(f"Created conversation {conversation.id}: {topic}")
            return conversation
    
    async def join_conversation(
        self,
        conversation_id: str,
        agent_id: str,
        role: Optional[ConversationRole] = None
    ) -> ConversationParticipant:
        """
        Join an existing conversation.
        
        Args:
            conversation_id: ID of the conversation to join
            agent_id: Agent wanting to join
            role: Requested role (may be overridden by settings)
            
        Returns:
            Participant info
            
        Raises:
            ConversationNotFoundError: If conversation doesn't exist
            InvalidRequestError: If can't join (full, ended, etc.)
        """
        async with self._lock:
            conversation = self.conversations.get(conversation_id)
            if not conversation:
                raise ConversationNotFoundError(conversation_id)
                
            # Check if conversation is joinable
            if conversation.state == "ended":
                raise InvalidRequestError("Cannot join ended conversation")
                
            if not conversation.settings.get("allow_late_join", True):
                if conversation.state != "created":
                    raise InvalidRequestError("Late joining is not allowed")
            
            # Default role
            if role is None:
                role = ConversationRole.PARTICIPANT
                
            # Add participant
            participant = await self._add_participant_internal(
                conversation,
                agent_id,
                role
            )
            
            # Subscribe agent to conversation channel
            await self.channel_bridge.create_pattern_subscription(
                agent_id,
                conversation.channel_name
            )
            
            # Broadcast join event
            await self._broadcast_event(
                conversation,
                "conversation.participant_joined",
                {
                    "agent_id": agent_id,
                    "role": role.value,
                    "participant_count": len(conversation.participants)
                }
            )
            
            logger.info(f"Agent {agent_id} joined conversation {conversation_id}")
            return participant
    
    async def leave_conversation(
        self,
        conversation_id: str,
        agent_id: str
    ) -> None:
        """
        Leave a conversation.
        
        Args:
            conversation_id: ID of the conversation
            agent_id: Agent leaving
        """
        async with self._lock:
            conversation = self.conversations.get(conversation_id)
            if not conversation:
                return
                
            if agent_id not in conversation.participants:
                return
                
            # Remove participant
            conversation.remove_participant(agent_id)
            
            # Update tracking
            if agent_id in self.agent_conversations:
                self.agent_conversations[agent_id].discard(conversation_id)
                
            # Handle empty conversation
            if (not conversation.participants and 
                conversation.settings.get("auto_end_on_empty", False)):
                await self._end_conversation_internal(conversation)
            else:
                # Broadcast leave event
                await self._broadcast_event(
                    conversation,
                    "conversation.participant_left",
                    {
                        "agent_id": agent_id,
                        "participant_count": len(conversation.participants)
                    }
                )
                
            logger.info(f"Agent {agent_id} left conversation {conversation_id}")
    
    async def send_message(
        self,
        conversation_id: str,
        sender_id: str,
        content: Any,
        in_reply_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationMessage:
        """
        Send a message in a conversation.
        
        Args:
            conversation_id: Target conversation
            sender_id: Sending agent
            content: Message content
            in_reply_to: Optional message ID being replied to
            metadata: Optional metadata
            
        Returns:
            Created message
            
        Raises:
            ConversationNotFoundError: If conversation doesn't exist
            UnauthorizedError: If agent can't send messages
        """
        async with self._lock:
            conversation = self.conversations.get(conversation_id)
            if not conversation:
                raise ConversationNotFoundError(conversation_id)
                
            # Check permissions
            if not conversation.can_send_message(sender_id):
                raise UnauthorizedError(
                    f"Agent {sender_id} cannot send messages in this conversation"
                )
                
            # Create message
            message = ConversationMessage(
                conversation_id=conversation_id,
                sender_id=sender_id,
                content=content,
                timestamp=datetime.now(timezone.utc),
                in_reply_to=in_reply_to,
                metadata=metadata or {}
            )
            
            # Record in conversation
            conversation.record_message(message)
            
            # Publish to channel
            await self.channel_bridge.publish_with_metadata(
                conversation.channel_name,
                sender_id,
                {
                    "type": "conversation.message",
                    "message": {
                        "id": message.id,
                        "sender_id": message.sender_id,
                        "content": message.content,
                        "timestamp": message.timestamp.isoformat(),
                        "in_reply_to": message.in_reply_to,
                        "metadata": message.metadata
                    },
                    "conversation_id": conversation_id
                },
                metadata={"conversation_id": conversation_id}
            )
            
            # Handle turn management
            await self._handle_turn_management(conversation, sender_id)
            
            return message
    
    async def request_turn(
        self,
        conversation_id: str,
        agent_id: str
    ) -> Optional[int]:
        """
        Request a turn to speak in a moderated conversation.
        
        Returns:
            Position in queue, or None if can speak immediately
        """
        async with self._lock:
            conversation = self.conversations.get(conversation_id)
            if not conversation:
                raise ConversationNotFoundError(conversation_id)
                
            if agent_id not in conversation.participants:
                raise UnauthorizedError(f"Agent {agent_id} not in conversation")
                
            participant = conversation.participants[agent_id]
            if participant.role == ConversationRole.OBSERVER:
                raise UnauthorizedError("Observers cannot request turns")
                
            # Free-form conversations don't need turn requests
            if conversation.turn_taking_mode == "free_form":
                return None
                
            # Already have the turn
            if (conversation.current_turn and 
                conversation.current_turn.agent_id == agent_id):
                return None
                
            # Add to queue if not already there
            if agent_id not in conversation.turn_queue:
                conversation.turn_queue.append(agent_id)
                
            position = conversation.turn_queue.index(agent_id) + 1
            
            # Broadcast turn request
            await self._broadcast_event(
                conversation,
                "conversation.turn_requested",
                {
                    "agent_id": agent_id,
                    "position": position,
                    "queue_length": len(conversation.turn_queue)
                }
            )
            
            return position
    
    async def grant_turn(
        self,
        conversation_id: str,
        moderator_id: str,
        agent_id: str
    ) -> None:
        """
        Grant speaking turn to an agent (moderator only).
        """
        async with self._lock:
            conversation = self.conversations.get(conversation_id)
            if not conversation:
                raise ConversationNotFoundError(conversation_id)
                
            # Verify moderator
            if moderator_id not in conversation.participants:
                raise UnauthorizedError("Not in conversation")
                
            moderator = conversation.participants[moderator_id]
            if moderator.role != ConversationRole.MODERATOR:
                raise UnauthorizedError("Only moderators can grant turns")
                
            # Start turn for agent
            conversation.start_turn(agent_id)
            
            # Remove from queue
            if agent_id in conversation.turn_queue:
                conversation.turn_queue.remove(agent_id)
                
            # Set up turn timer if configured
            timeout = conversation.settings.get("turn_timeout_seconds")
            if timeout:
                await self._start_turn_timer(conversation_id, agent_id, timeout)
                
            # Broadcast turn granted
            await self._broadcast_event(
                conversation,
                "conversation.turn_granted",
                {
                    "agent_id": agent_id,
                    "granted_by": moderator_id,
                    "timeout_seconds": timeout
                }
            )
    
    async def end_conversation(
        self,
        conversation_id: str,
        agent_id: str
    ) -> None:
        """
        End a conversation (moderator only).
        """
        async with self._lock:
            conversation = self.conversations.get(conversation_id)
            if not conversation:
                raise ConversationNotFoundError(conversation_id)
                
            # Verify permissions
            if agent_id not in conversation.participants:
                raise UnauthorizedError("Not in conversation")
                
            participant = conversation.participants[agent_id]
            if participant.role != ConversationRole.MODERATOR:
                # Check if it's the creator
                if agent_id != conversation.created_by:
                    raise UnauthorizedError("Only moderators can end conversations")
                    
            await self._end_conversation_internal(conversation)
    
    async def get_conversation(
        self,
        conversation_id: str,
        agent_id: Optional[str] = None
    ) -> Optional[Conversation]:
        """Get conversation details."""
        conversation = self.conversations.get(conversation_id)
        
        # If agent specified, check if they have access
        if conversation and agent_id:
            if agent_id not in conversation.participants:
                return None
                
        return conversation
    
    async def list_conversations(
        self,
        agent_id: Optional[str] = None,
        state: Optional[ConversationState] = None
    ) -> List[Dict[str, Any]]:
        """List conversations, optionally filtered."""
        conversations = []
        
        for conv in self.conversations.values():
            # Filter by state
            if state and conv.state != state:
                continue
                
            # Filter by agent participation
            if agent_id and agent_id not in conv.participants:
                continue
                
            conversations.append(conv.to_summary())
            
        # Sort by last activity
        conversations.sort(
            key=lambda c: c["last_activity"],
            reverse=True
        )
        
        return conversations
    
    # Internal helper methods
    
    async def _add_participant_internal(
        self,
        conversation: Conversation,
        agent_id: str,
        role: ConversationRole
    ) -> ConversationParticipant:
        """Internal method to add participant."""
        participant = conversation.add_participant(agent_id, role)
        
        # Track agent's conversations
        if agent_id not in self.agent_conversations:
            self.agent_conversations[agent_id] = set()
        self.agent_conversations[agent_id].add(conversation.id)
        
        return participant
    
    async def _end_conversation_internal(self, conversation: Conversation) -> None:
        """Internal method to end conversation."""
        conversation.end()
        
        # Cancel any turn timers
        if conversation.id in self._turn_timers:
            self._turn_timers[conversation.id].cancel()
            del self._turn_timers[conversation.id]
            
        # Broadcast end event
        await self._broadcast_event(
            conversation,
            "conversation.ended",
            {
                "ended_at": conversation.ended_at.isoformat(),
                "message_count": conversation.message_count
            }
        )
        
        logger.info(f"Ended conversation {conversation.id}")
    
    async def _broadcast_event(
        self,
        conversation: Conversation,
        event_type: str,
        data: Dict[str, Any]
    ) -> None:
        """Broadcast an event to conversation participants."""
        # Publish to conversation channel
        await self.channel_bridge.publish_with_metadata(
            conversation.channel_name,
            "system",
            {
                "type": event_type,
                "conversation_id": conversation.id,
                "data": data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            metadata={"system_event": True}
        )
    
    async def _handle_turn_management(
        self,
        conversation: Conversation,
        sender_id: str
    ) -> None:
        """Handle turn management after a message."""
        if conversation.turn_taking_mode == "round_robin":
            # Automatically advance to next speaker
            next_speaker = conversation.get_next_speaker()
            if next_speaker and next_speaker != sender_id:
                conversation.start_turn(next_speaker)
                
                # Set timer if configured
                timeout = conversation.settings.get("turn_timeout_seconds")
                if timeout:
                    await self._start_turn_timer(
                        conversation.id,
                        next_speaker,
                        timeout
                    )
                    
                await self._broadcast_event(
                    conversation,
                    "conversation.turn_advanced",
                    {
                        "previous_speaker": sender_id,
                        "next_speaker": next_speaker,
                        "timeout_seconds": timeout
                    }
                )
    
    async def _start_turn_timer(
        self,
        conversation_id: str,
        agent_id: str,
        timeout_seconds: float
    ) -> None:
        """Start a timer for turn timeout."""
        # Cancel existing timer
        if conversation_id in self._turn_timers:
            self._turn_timers[conversation_id].cancel()
            
        async def timeout_handler():
            await asyncio.sleep(timeout_seconds)
            async with self._lock:
                conversation = self.conversations.get(conversation_id)
                if (conversation and 
                    conversation.current_turn and
                    conversation.current_turn.agent_id == agent_id):
                    
                    # End turn
                    conversation.end_current_turn()
                    
                    # Advance to next if round-robin
                    if conversation.turn_taking_mode == "round_robin":
                        await self._handle_turn_management(conversation, agent_id)
                    
                    # Broadcast timeout
                    await self._broadcast_event(
                        conversation,
                        "conversation.turn_timeout",
                        {"agent_id": agent_id}
                    )
                    
        # Create and store timer task
        timer_task = asyncio.create_task(timeout_handler())
        self._turn_timers[conversation_id] = timer_task