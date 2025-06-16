"""
Unit tests for A2A multi-agent conversation support
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import uuid4

from tekton.a2a.conversation import (
    Conversation, ConversationRole, ConversationState,
    TurnTakingMode, ConversationParticipant, ConversationMessage
)
from tekton.a2a.conversation_manager import ConversationManager
from tekton.a2a.errors import ConversationNotFoundError, UnauthorizedError, InvalidRequestError


class TestConversation:
    """Test the Conversation model"""
    
    def test_conversation_creation(self):
        """Test creating a conversation"""
        conv = Conversation.create(
            topic="Project Planning",
            created_by="agent-123",
            description="Planning the next sprint",
            turn_taking_mode=TurnTakingMode.FREE_FORM
        )
        
        assert conv.topic == "Project Planning"
        assert conv.created_by == "agent-123"
        assert conv.description == "Planning the next sprint"
        assert conv.turn_taking_mode == TurnTakingMode.FREE_FORM
        assert conv.state == ConversationState.CREATED
        assert len(conv.participants) == 1  # Creator auto-joins
        assert "agent-123" in conv.participants
        assert conv.participants["agent-123"].role == ConversationRole.MODERATOR
    
    def test_add_participant(self):
        """Test adding participants to conversation"""
        conv = Conversation.create("Test", "agent-123")
        
        # Add a participant
        participant = conv.add_participant("agent-456", ConversationRole.PARTICIPANT)
        assert participant.agent_id == "agent-456"
        assert participant.role == ConversationRole.PARTICIPANT
        assert len(conv.participants) == 2
        
        # Try to add same participant again
        with pytest.raises(ValueError):
            conv.add_participant("agent-456")
    
    def test_remove_participant(self):
        """Test removing participants"""
        conv = Conversation.create("Test", "agent-123")
        conv.add_participant("agent-456")
        
        assert len(conv.participants) == 2
        conv.remove_participant("agent-456")
        assert len(conv.participants) == 1
        assert "agent-456" not in conv.participants
    
    def test_can_send_message_free_form(self):
        """Test message sending permissions in free form mode"""
        conv = Conversation.create("Test", "agent-123")
        conv.add_participant("agent-456", ConversationRole.PARTICIPANT)
        conv.add_participant("agent-789", ConversationRole.OBSERVER)
        
        # Moderator can send
        assert conv.can_send_message("agent-123") is True
        # Participant can send
        assert conv.can_send_message("agent-456") is True
        # Observer cannot send
        assert conv.can_send_message("agent-789") is False
        # Non-participant cannot send
        assert conv.can_send_message("agent-999") is False
    
    def test_can_send_message_round_robin(self):
        """Test message sending in round robin mode"""
        conv = Conversation.create(
            "Test", 
            "agent-123",
            turn_taking_mode=TurnTakingMode.ROUND_ROBIN
        )
        conv.add_participant("agent-456")
        
        # No one can send without a turn
        assert conv.can_send_message("agent-123") is False
        
        # Start turn for agent-123
        conv.start_turn("agent-123")
        assert conv.can_send_message("agent-123") is True
        assert conv.can_send_message("agent-456") is False
    
    def test_turn_management(self):
        """Test turn taking functionality"""
        conv = Conversation.create(
            "Test",
            "agent-123",
            turn_taking_mode=TurnTakingMode.ROUND_ROBIN
        )
        conv.add_participant("agent-456")
        conv.add_participant("agent-789")
        
        # Check turn queue
        assert len(conv.turn_queue) == 3
        
        # Start and end turn
        turn = conv.start_turn("agent-123")
        assert turn.agent_id == "agent-123"
        assert turn.ended_at is None
        
        conv.end_current_turn()
        assert turn.ended_at is not None
    
    def test_record_message(self):
        """Test recording messages in conversation"""
        conv = Conversation.create("Test", "agent-123")
        
        # Create and record message
        message = ConversationMessage(
            conversation_id=conv.id,
            sender_id="agent-123",
            content="Hello everyone!"
        )
        
        conv.record_message(message)
        
        assert conv.message_count == 1
        assert conv.participants["agent-123"].message_count == 1
    
    def test_conversation_lifecycle(self):
        """Test conversation state transitions"""
        conv = Conversation.create("Test", "agent-123")
        
        assert conv.state == ConversationState.CREATED
        
        conv.activate()
        assert conv.state == ConversationState.ACTIVE
        
        conv.pause()
        assert conv.state == ConversationState.PAUSED
        
        conv.resume()
        assert conv.state == ConversationState.ACTIVE
        
        conv.end()
        assert conv.state == ConversationState.ENDED
        assert conv.ended_at is not None


class TestConversationManager:
    """Test the ConversationManager"""
    
    @pytest.fixture
    def mock_channel_bridge(self):
        """Create a mock channel bridge"""
        bridge = AsyncMock()
        bridge.enhance_channel = AsyncMock()
        bridge.create_pattern_subscription = AsyncMock()
        bridge.publish_with_metadata = AsyncMock()
        return bridge
    
    @pytest.fixture
    def conversation_manager(self, mock_channel_bridge):
        """Create a conversation manager"""
        return ConversationManager(mock_channel_bridge)
    
    @pytest.mark.asyncio
    async def test_create_conversation(self, conversation_manager, mock_channel_bridge):
        """Test creating a conversation"""
        conv = await conversation_manager.create_conversation(
            topic="Test Discussion",
            created_by="agent-123",
            description="Testing conversations"
        )
        
        assert conv.topic == "Test Discussion"
        assert conv.created_by == "agent-123"
        assert conv.state == ConversationState.ACTIVE
        assert conv.id in conversation_manager.conversations
        
        # Check channel was created
        mock_channel_bridge.enhance_channel.assert_called_once()
        channel_name = mock_channel_bridge.enhance_channel.call_args[0][0]
        assert channel_name.startswith("conversations.")
    
    @pytest.mark.asyncio
    async def test_create_conversation_with_participants(self, conversation_manager):
        """Test creating conversation with initial participants"""
        conv = await conversation_manager.create_conversation(
            topic="Team Meeting",
            created_by="agent-123",
            initial_participants=[
                {"agent_id": "agent-456", "role": "participant"},
                {"agent_id": "agent-789", "role": "observer"}
            ]
        )
        
        assert len(conv.participants) == 3
        assert conv.participants["agent-456"].role == ConversationRole.PARTICIPANT
        assert conv.participants["agent-789"].role == ConversationRole.OBSERVER
    
    @pytest.mark.asyncio
    async def test_join_conversation(self, conversation_manager, mock_channel_bridge):
        """Test joining a conversation"""
        # Create conversation
        conv = await conversation_manager.create_conversation(
            topic="Open Discussion",
            created_by="agent-123"
        )
        
        # Join conversation
        participant = await conversation_manager.join_conversation(
            conversation_id=conv.id,
            agent_id="agent-456"
        )
        
        assert participant.agent_id == "agent-456"
        assert participant.role == ConversationRole.PARTICIPANT
        assert len(conv.participants) == 2
        
        # Check subscription was created
        mock_channel_bridge.create_pattern_subscription.assert_called()
    
    @pytest.mark.asyncio
    async def test_join_nonexistent_conversation(self, conversation_manager):
        """Test joining a conversation that doesn't exist"""
        with pytest.raises(ConversationNotFoundError):
            await conversation_manager.join_conversation(
                conversation_id="fake-id",
                agent_id="agent-123"
            )
    
    @pytest.mark.asyncio
    async def test_join_ended_conversation(self, conversation_manager):
        """Test joining an ended conversation"""
        conv = await conversation_manager.create_conversation(
            topic="Test",
            created_by="agent-123"
        )
        
        # End conversation
        await conversation_manager.end_conversation(conv.id, "agent-123")
        
        # Try to join
        with pytest.raises(InvalidRequestError):
            await conversation_manager.join_conversation(
                conversation_id=conv.id,
                agent_id="agent-456"
            )
    
    @pytest.mark.asyncio
    async def test_leave_conversation(self, conversation_manager, mock_channel_bridge):
        """Test leaving a conversation"""
        conv = await conversation_manager.create_conversation(
            topic="Test",
            created_by="agent-123"
        )
        
        # Add participant
        await conversation_manager.join_conversation(conv.id, "agent-456")
        assert len(conv.participants) == 2
        
        # Leave conversation
        await conversation_manager.leave_conversation(conv.id, "agent-456")
        assert len(conv.participants) == 1
        assert "agent-456" not in conv.participants
    
    @pytest.mark.asyncio
    async def test_send_message(self, conversation_manager, mock_channel_bridge):
        """Test sending a message in conversation"""
        conv = await conversation_manager.create_conversation(
            topic="Chat",
            created_by="agent-123"
        )
        
        # Send message
        message = await conversation_manager.send_message(
            conversation_id=conv.id,
            sender_id="agent-123",
            content="Hello world!"
        )
        
        assert message.sender_id == "agent-123"
        assert message.content == "Hello world!"
        assert conv.message_count == 1
        
        # Check message was published
        mock_channel_bridge.publish_with_metadata.assert_called()
    
    @pytest.mark.asyncio
    async def test_send_message_unauthorized(self, conversation_manager):
        """Test sending message when not authorized"""
        conv = await conversation_manager.create_conversation(
            topic="Test",
            created_by="agent-123"
        )
        
        # Non-participant tries to send
        with pytest.raises(UnauthorizedError):
            await conversation_manager.send_message(
                conversation_id=conv.id,
                sender_id="agent-999",
                content="Hello"
            )
    
    @pytest.mark.asyncio
    async def test_request_turn(self, conversation_manager):
        """Test requesting a turn in moderated conversation"""
        conv = await conversation_manager.create_conversation(
            topic="Moderated",
            created_by="agent-123",
            turn_taking_mode=TurnTakingMode.MODERATED
        )
        
        # Join as participant
        await conversation_manager.join_conversation(conv.id, "agent-456")
        
        # Request turn
        position = await conversation_manager.request_turn(conv.id, "agent-456")
        assert position == 1  # First in queue
        assert "agent-456" in conv.turn_queue
    
    @pytest.mark.asyncio
    async def test_grant_turn(self, conversation_manager, mock_channel_bridge):
        """Test granting turn as moderator"""
        conv = await conversation_manager.create_conversation(
            topic="Moderated",
            created_by="agent-123",
            turn_taking_mode=TurnTakingMode.MODERATED
        )
        
        await conversation_manager.join_conversation(conv.id, "agent-456")
        
        # Grant turn
        await conversation_manager.grant_turn(
            conversation_id=conv.id,
            moderator_id="agent-123",
            agent_id="agent-456"
        )
        
        assert conv.current_turn is not None
        assert conv.current_turn.agent_id == "agent-456"
    
    @pytest.mark.asyncio
    async def test_grant_turn_unauthorized(self, conversation_manager):
        """Test non-moderator trying to grant turn"""
        conv = await conversation_manager.create_conversation(
            topic="Test",
            created_by="agent-123",
            turn_taking_mode=TurnTakingMode.MODERATED
        )
        
        await conversation_manager.join_conversation(conv.id, "agent-456")
        
        # Non-moderator tries to grant turn
        with pytest.raises(UnauthorizedError):
            await conversation_manager.grant_turn(
                conversation_id=conv.id,
                moderator_id="agent-456",
                agent_id="agent-456"
            )
    
    @pytest.mark.asyncio
    async def test_end_conversation(self, conversation_manager):
        """Test ending a conversation"""
        conv = await conversation_manager.create_conversation(
            topic="Test",
            created_by="agent-123"
        )
        
        # End conversation
        await conversation_manager.end_conversation(conv.id, "agent-123")
        
        assert conv.state == ConversationState.ENDED
        assert conv.ended_at is not None
    
    @pytest.mark.asyncio
    async def test_list_conversations(self, conversation_manager):
        """Test listing conversations"""
        # Create multiple conversations
        conv1 = await conversation_manager.create_conversation(
            topic="Conv 1",
            created_by="agent-123"
        )
        
        conv2 = await conversation_manager.create_conversation(
            topic="Conv 2",
            created_by="agent-456"
        )
        
        # Join agent-123 to conv2
        await conversation_manager.join_conversation(conv2.id, "agent-123")
        
        # List all conversations
        all_convs = await conversation_manager.list_conversations()
        assert len(all_convs) == 2
        
        # List agent-123's conversations
        agent_convs = await conversation_manager.list_conversations(agent_id="agent-123")
        assert len(agent_convs) == 2
        
        # List agent-456's conversations
        agent_convs = await conversation_manager.list_conversations(agent_id="agent-456")
        assert len(agent_convs) == 1
    
    @pytest.mark.asyncio
    async def test_turn_timeout(self, conversation_manager, mock_channel_bridge):
        """Test turn timeout functionality"""
        conv = await conversation_manager.create_conversation(
            topic="Timed",
            created_by="agent-123",
            turn_taking_mode=TurnTakingMode.MODERATED,
            settings={"turn_timeout_seconds": 0.1}  # 100ms timeout
        )
        
        await conversation_manager.join_conversation(conv.id, "agent-456")
        
        # Grant turn
        await conversation_manager.grant_turn(
            conversation_id=conv.id,
            moderator_id="agent-123",
            agent_id="agent-456"
        )
        
        # Wait for timeout
        await asyncio.sleep(0.2)
        
        # Turn should be ended
        assert conv.current_turn.ended_at is not None
        
        # Check timeout event was broadcast
        calls = mock_channel_bridge.publish_with_metadata.call_args_list
        timeout_event_sent = any(
            "conversation.turn_timeout" in str(call) 
            for call in calls
        )
        assert timeout_event_sent