"""
Example showing integration between A2A and MCP in Ergon.

This example demonstrates how to use the A2A and MCP clients together
to create a multimodal agent communication flow.
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add Ergon to path
import sys
ergon_dir = str(Path(__file__).parent.parent)
if ergon_dir not in sys.path:
    sys.path.append(ergon_dir)

from ergon.core.a2a_client import A2AClient
from ergon.core.mcp_client import MCPClient
from ergon.utils.mcp_adapter import (
    prepare_text_content,
    prepare_code_content,
    prepare_structured_content,
    extract_text_from_mcp_result
)

class MultimodalAgent:
    """
    An example agent that uses both A2A and MCP protocols.
    
    This agent can communicate with other agents using A2A
    and process multimodal content using MCP.
    """
    
    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        capabilities: Optional[List[str]] = None
    ):
        """Initialize the multimodal agent."""
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.capabilities = capabilities or ["text_processing", "code_analysis"]
        
        # Initialize clients
        self.a2a_client = A2AClient(
            agent_id=agent_id,
            agent_name=agent_name,
            capabilities={"processing": self.capabilities},
            hermes_url=os.environ.get("HERMES_URL")
        )
        
        self.mcp_client = MCPClient(
            client_id=agent_id,
            client_name=agent_name,
            hermes_url=os.environ.get("HERMES_URL")
        )
        
        # Track conversations
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
        self.contexts: Dict[str, str] = {}
        
        logger.info(f"Multimodal agent initialized: {self.agent_id}")
    
    async def initialize(self) -> bool:
        """Initialize the agent."""
        # Initialize A2A client
        a2a_initialized = await self.a2a_client.initialize()
        if not a2a_initialized:
            logger.error("Failed to initialize A2A client")
            return False
        
        # Initialize MCP client
        mcp_initialized = await self.mcp_client.initialize()
        if not mcp_initialized:
            logger.error("Failed to initialize MCP client")
            return False
        
        # Register with A2A service
        registered = await self.a2a_client.register()
        if not registered:
            logger.error("Failed to register with A2A service")
            return False
        
        logger.info(f"Agent {self.agent_name} initialized and registered")
        return True
    
    async def close(self) -> None:
        """Close the agent."""
        await self.a2a_client.close()
        await self.mcp_client.close()
        logger.info(f"Agent {self.agent_name} closed")
    
    async def handle_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle an incoming A2A message.
        
        This method processes the message content using MCP and
        generates a response.
        
        Args:
            message: A2A message
            
        Returns:
            Response message or None if no response is needed
        """
        sender = message.get("sender", {}).get("agent_id", "unknown")
        conversation_id = message.get("conversation_id")
        content = message.get("content", {})
        message_type = message.get("message_type", "request")
        
        logger.info(f"Received message from {sender} in conversation {conversation_id}")
        
        # Store message in conversation history
        if conversation_id:
            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = []
            
            self.conversations[conversation_id].append(message)
        
        # Process message content based on type
        response_content = None
        
        if "text" in content:
            # Process text content
            result = await self.mcp_client.process_content(
                content=content["text"],
                content_type="text",
                context=self._get_context(conversation_id)
            )
            
            response_text = extract_text_from_mcp_result(result)
            if response_text:
                response_content = {"text": response_text}
        
        elif "code" in content:
            # Process code content
            result = await self.mcp_client.process_content(
                content=content["code"],
                content_type="code",
                processing_options={"language": content.get("language", "python")},
                context=self._get_context(conversation_id)
            )
            
            response_text = extract_text_from_mcp_result(result)
            if response_text:
                response_content = {
                    "text": response_text,
                    "code": response_text if "code_response" in content else None
                }
        
        elif "image" in content:
            # Process image content (base64-encoded)
            result = await self.mcp_client.process_content(
                content=content["image"],
                content_type="image",
                context=self._get_context(conversation_id)
            )
            
            response_text = extract_text_from_mcp_result(result)
            if response_text:
                response_content = {"text": response_text}
        
        elif "structured" in content:
            # Process structured content
            result = await self.mcp_client.process_content(
                content=content["structured"],
                content_type="structured",
                context=self._get_context(conversation_id)
            )
            
            response_text = extract_text_from_mcp_result(result)
            if response_text:
                response_content = {"text": response_text}
        
        # If this is a request, send a response
        if message_type == "request" and response_content:
            await self._send_response(
                sender=sender,
                conversation_id=conversation_id,
                content=response_content,
                reply_to=message.get("message_id")
            )
            return response_content
        
        return None
    
    async def start_conversation(
        self,
        recipients: List[Dict[str, Any]],
        content: Dict[str, Any],
        intent: Optional[str] = None
    ) -> Optional[str]:
        """
        Start a new conversation with other agents.
        
        Args:
            recipients: List of recipient agents
            content: Message content
            intent: Optional conversation intent
            
        Returns:
            Conversation ID if successful
        """
        # Process content with MCP before sending
        processed_content = content
        
        if "text" in content:
            # Pre-process text if needed
            result = await self.mcp_client.process_content(
                content=content["text"],
                content_type="text",
                processing_options={"action": "prepare"}
            )
            
            text = extract_text_from_mcp_result(result)
            if text:
                processed_content["text"] = text
        
        # Create a context for this conversation
        context_id = await self.mcp_client.create_context(
            context_type="conversation",
            content={"initial_message": processed_content}
        )
        
        # Send the message
        conversation_id = await self.a2a_client.send_message(
            recipients=recipients,
            content=processed_content,
            intent=intent
        )
        
        if conversation_id and context_id:
            # Store context ID for later use
            self.contexts[conversation_id] = context_id
            logger.info(f"Started conversation {conversation_id} with context {context_id}")
        
        return conversation_id
    
    async def discover_agents(self, capabilities: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Discover agents with specific capabilities.
        
        Args:
            capabilities: List of required capabilities
            
        Returns:
            List of discovered agents
        """
        return await self.a2a_client.discover_agents(capabilities)
    
    async def create_task(
        self,
        name: str,
        description: str,
        required_capabilities: List[str],
        parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create a task for other agents.
        
        Args:
            name: Task name
            description: Task description
            required_capabilities: List of required capabilities
            parameters: Task parameters
            
        Returns:
            Task ID if successful
        """
        # Process the task description with MCP
        result = await self.mcp_client.process_content(
            content=description,
            content_type="text",
            processing_options={"action": "enhance_task"}
        )
        
        enhanced_description = extract_text_from_mcp_result(result)
        
        # Create the task
        task_id = await self.a2a_client.create_task(
            name=name,
            description=enhanced_description or description,
            required_capabilities=required_capabilities,
            parameters=parameters
        )
        
        if task_id:
            logger.info(f"Created task {task_id}")
        
        return task_id
    
    def _get_context(self, conversation_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """Get context for a conversation."""
        if not conversation_id or conversation_id not in self.contexts:
            return None
        
        return {"context_id": self.contexts[conversation_id]}
    
    async def _send_response(
        self,
        sender: str,
        conversation_id: Optional[str],
        content: Dict[str, Any],
        reply_to: Optional[str] = None
    ) -> Optional[str]:
        """Send a response message."""
        # Create recipient specification
        recipient = {"agent_id": sender}
        
        # Send the message
        message_id = await self.a2a_client.send_message(
            recipients=[recipient],
            content=content,
            message_type="response",
            conversation_id=conversation_id,
            reply_to=reply_to
        )
        
        if message_id and conversation_id:
            # Update conversation history
            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = []
            
            self.conversations[conversation_id].append({
                "message_id": message_id,
                "sender": {"agent_id": self.agent_id},
                "content": content,
                "message_type": "response",
                "conversation_id": conversation_id,
                "reply_to": reply_to
            })
            
            # Update context if available
            if conversation_id in self.contexts:
                await self.mcp_client.enhance_context(
                    context_id=self.contexts[conversation_id],
                    content={"message": content, "type": "response"}
                )
        
        return message_id

async def run_agent_example():
    """Run an example with two multimodal agents."""
    # Create first agent
    agent1 = MultimodalAgent(
        agent_id="agent1",
        agent_name="Code Assistant",
        capabilities=["code_analysis", "code_generation"]
    )
    
    # Create second agent
    agent2 = MultimodalAgent(
        agent_id="agent2",
        agent_name="Text Processor",
        capabilities=["text_processing", "summarization"]
    )
    
    try:
        # Initialize both agents
        await agent1.initialize()
        await agent2.initialize()
        
        # Wait for registration to propagate
        await asyncio.sleep(1)
        
        # Agent1 discovers agent2
        discovered = await agent1.discover_agents(["text_processing"])
        logger.info(f"Discovered agents: {discovered}")
        
        if discovered:
            # Agent1 starts a conversation with agent2
            conversation_id = await agent1.start_conversation(
                recipients=[discovered[0]],
                content={
                    "text": "Can you analyze this code snippet?",
                    "code": "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)"
                },
                intent="code_analysis"
            )
            
            if conversation_id:
                logger.info(f"Started conversation: {conversation_id}")
                
                # Simulate message handling
                # In a real application, you would set up webhooks or polling
                await asyncio.sleep(2)
                
                # Create a task
                task_id = await agent1.create_task(
                    name="Optimize Code",
                    description="Optimize the factorial function to use iteration instead of recursion",
                    required_capabilities=["code_generation"],
                    parameters={
                        "language": "python",
                        "optimization_level": "high"
                    }
                )
                
                if task_id:
                    logger.info(f"Created task: {task_id}")
        
    finally:
        # Close both agents
        await agent1.close()
        await agent2.close()

async def main():
    """Run the integration example."""
    try:
        await run_agent_example()
    except Exception as e:
        logger.error(f"Error in example: {e}")

if __name__ == "__main__":
    asyncio.run(main())