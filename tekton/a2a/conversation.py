"""
Multi-agent conversation support for A2A Protocol v0.2.1

This module provides structured conversations between multiple agents,
building on top of the channel-based pub/sub system.
"""

from typing import Dict, List, Optional, Set, Any, Literal
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from tekton.models import TektonBaseModel


class ConversationRole(str, Enum):
    """Roles that agents can have in a conversation"""
    MODERATOR = "moderator"      # Can manage conversation settings
    PARTICIPANT = "participant"  # Can send messages
    OBSERVER = "observer"        # Can only receive messages
    

class ConversationState(str, Enum):
    """States of a conversation lifecycle"""
    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
    

class TurnTakingMode(str, Enum):
    """Turn-taking strategies for conversations"""
    FREE_FORM = "free_form"          # Anyone can speak at any time
    ROUND_ROBIN = "round_robin"      # Participants take turns in order
    MODERATED = "moderated"          # Moderator controls who can speak
    CONSENSUS = "consensus"          # Group must agree on next speaker


@dataclass
class ConversationParticipant:
    """Represents an agent participating in a conversation"""
    agent_id: str
    role: ConversationRole
    joined_at: datetime
    last_active: datetime
    message_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    

@dataclass
class ConversationMessage:
    """A message within a conversation"""
    conversation_id: str
    sender_id: str
    content: Any  # Can be text, structured data, etc.
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    in_reply_to: Optional[str] = None  # For threaded conversations
    metadata: Dict[str, Any] = field(default_factory=dict)
    

@dataclass
class ConversationTurn:
    """Represents a turn in a moderated conversation"""
    agent_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    messages: List[str] = field(default_factory=list)  # Message IDs
    

class Conversation(TektonBaseModel):
    """Represents a multi-agent conversation"""
    
    id: str
    topic: str
    description: Optional[str] = None
    created_by: str
    created_at: datetime
    state: ConversationState = ConversationState.CREATED
    
    # Participants
    participants: Dict[str, ConversationParticipant] = {}
    max_participants: Optional[int] = None
    
    # Turn-taking
    turn_taking_mode: TurnTakingMode = TurnTakingMode.FREE_FORM
    current_turn: Optional[ConversationTurn] = None
    turn_queue: List[str] = []  # Agent IDs waiting for their turn
    
    # Settings
    settings: Dict[str, Any] = {
        "allow_late_join": True,
        "record_history": True,
        "auto_end_on_empty": False,
        "max_message_length": 4096,
        "turn_timeout_seconds": None,  # For moderated/round-robin modes
    }
    
    # State tracking
    message_count: int = 0
    last_activity: datetime
    ended_at: Optional[datetime] = None
    
    # Channel integration
    channel_name: str  # Underlying channel for message distribution
    
    @classmethod
    def create(
        cls,
        topic: str,
        created_by: str,
        description: Optional[str] = None,
        turn_taking_mode: TurnTakingMode = TurnTakingMode.FREE_FORM,
        settings: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> 'Conversation':
        """Create a new conversation"""
        conv_id = f"conv-{uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)
        
        # Create underlying channel for this conversation
        channel_name = f"conversations.{conv_id}"
        
        conversation = cls(
            id=conv_id,
            topic=topic,
            description=description,
            created_by=created_by,
            created_at=now,
            state=ConversationState.CREATED,
            turn_taking_mode=turn_taking_mode,
            last_activity=now,
            channel_name=channel_name,
            **kwargs
        )
        
        if settings:
            conversation.settings.update(settings)
            
        # Creator automatically joins as moderator
        conversation.add_participant(
            created_by,
            ConversationRole.MODERATOR
        )
        
        return conversation
    
    def add_participant(
        self,
        agent_id: str,
        role: ConversationRole = ConversationRole.PARTICIPANT
    ) -> ConversationParticipant:
        """Add a participant to the conversation"""
        if agent_id in self.participants:
            raise ValueError(f"Agent {agent_id} is already in the conversation")
            
        if (self.max_participants and 
            len(self.participants) >= self.max_participants):
            raise ValueError("Conversation is full")
            
        participant = ConversationParticipant(
            agent_id=agent_id,
            role=role,
            joined_at=datetime.now(timezone.utc),
            last_active=datetime.now(timezone.utc)
        )
        
        self.participants[agent_id] = participant
        
        # If conversation uses turn-based mode, add to queue
        if self.turn_taking_mode == "round_robin":
            # In round robin, everyone including moderator takes turns
            self.turn_queue.append(agent_id)
        elif self.turn_taking_mode == "moderated" and role == ConversationRole.PARTICIPANT:
            # In moderated mode, only participants need turns
            self.turn_queue.append(agent_id)
            
        return participant
    
    def remove_participant(self, agent_id: str) -> None:
        """Remove a participant from the conversation"""
        if agent_id not in self.participants:
            return
            
        del self.participants[agent_id]
        
        # Remove from turn queue if present
        if agent_id in self.turn_queue:
            self.turn_queue.remove(agent_id)
            
        # Handle current turn if it's this agent's turn
        if self.current_turn and self.current_turn.agent_id == agent_id:
            self.end_current_turn()
    
    def can_send_message(self, agent_id: str) -> bool:
        """Check if an agent can send a message"""
        if agent_id not in self.participants:
            return False
            
        participant = self.participants[agent_id]
        
        # Observers can't send messages
        if participant.role == ConversationRole.OBSERVER:
            return False
            
        # Check turn-taking rules
        if self.turn_taking_mode == "free_form":
            return True
        elif self.turn_taking_mode in ["round_robin", "moderated"]:
            return bool(self.current_turn and self.current_turn.agent_id == agent_id)
        elif self.turn_taking_mode == "consensus":
            # TODO: Implement consensus checking
            return True
            
        return False
    
    def start_turn(self, agent_id: str) -> ConversationTurn:
        """Start a new turn for an agent"""
        if self.current_turn and self.current_turn.ended_at is None:
            self.end_current_turn()
            
        self.current_turn = ConversationTurn(
            agent_id=agent_id,
            started_at=datetime.now(timezone.utc)
        )
        
        return self.current_turn
    
    def end_current_turn(self) -> None:
        """End the current turn"""
        if self.current_turn:
            self.current_turn.ended_at = datetime.now(timezone.utc)
            
    def get_next_speaker(self) -> Optional[str]:
        """Get the next agent who should speak"""
        if self.turn_taking_mode == "round_robin":
            if self.turn_queue:
                # Move current speaker to end of queue
                if self.current_turn:
                    current = self.current_turn.agent_id
                    if current in self.turn_queue:
                        self.turn_queue.remove(current)
                        self.turn_queue.append(current)
                        
                return self.turn_queue[0] if self.turn_queue else None
                
        return None
    
    def record_message(self, message: ConversationMessage) -> None:
        """Record a message in the conversation"""
        self.message_count += 1
        self.last_activity = datetime.now(timezone.utc)
        
        # Update participant stats
        if message.sender_id in self.participants:
            participant = self.participants[message.sender_id]
            participant.message_count += 1
            participant.last_active = datetime.now(timezone.utc)
            
        # Track message in current turn
        if self.current_turn and self.current_turn.agent_id == message.sender_id:
            self.current_turn.messages.append(message.id)
    
    def activate(self) -> None:
        """Activate the conversation"""
        if self.state == ConversationState.CREATED:
            self.state = ConversationState.ACTIVE
            
    def pause(self) -> None:
        """Pause the conversation"""
        if self.state == ConversationState.ACTIVE:
            self.state = ConversationState.PAUSED
            
    def resume(self) -> None:
        """Resume a paused conversation"""
        if self.state == ConversationState.PAUSED:
            self.state = ConversationState.ACTIVE
            
    def end(self) -> None:
        """End the conversation"""
        self.state = ConversationState.ENDED
        self.ended_at = datetime.now(timezone.utc)
        if self.current_turn:
            self.end_current_turn()
            
    def to_summary(self) -> Dict[str, Any]:
        """Get a summary of the conversation"""
        return {
            "id": self.id,
            "topic": self.topic,
            "description": self.description,
            "state": self.state,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "participant_count": len(self.participants),
            "message_count": self.message_count,
            "turn_taking_mode": self.turn_taking_mode,
            "last_activity": self.last_activity.isoformat(),
            "channel_name": self.channel_name
        }