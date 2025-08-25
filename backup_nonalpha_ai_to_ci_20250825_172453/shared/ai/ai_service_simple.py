#!/usr/bin/env python3
"""
Simple CI Service - Just message->ai->response
No connection management, that's another layer's job
"""

import json
import time
import uuid
from typing import Dict, Optional, Any
from dataclasses import dataclass

from landmarks import (
    architecture_decision,
    performance_boundary,
    state_checkpoint,
    integration_point
)

@dataclass
class Message:
    id: str
    request: str
    response: Optional[str] = None
    error: Optional[str] = None

@architecture_decision(
    title="One Queue, One Socket, One CI Architecture",
    rationale="Simplify CI communication by eliminating connection pooling and complex routing",
    alternatives_considered=["Connection pooling", "Multiple socket per AI", "Event-driven architecture"],
    impacts=["simplicity", "reliability", "maintainability"],
    decided_by="Casey"
)
@state_checkpoint(
    title="AI Message Queue Management",
    state_type="runtime",
    persistence=False,
    consistency_requirements="UUID-based message tracking ensures no message loss",
    recovery_strategy="Queue per CI allows independent recovery"
)
class CIService:
    """One queue per AI, one socket per CI - just send/receive messages"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.queues: Dict[str, Dict[str, Message]] = {}  # ai_id -> {msg_id -> Message}
        self.sockets: Dict[str, Any] = {}  # ai_id -> socket (reader, writer)
        
    def register_ai(self, ai_id: str, reader, writer):
        """Register an CI with its socket"""
        self.sockets[ai_id] = (reader, writer)
        if ai_id not in self.queues:
            self.queues[ai_id] = {}
            
    def send_request(self, ai_id: str, request: str) -> str:
        """Queue a request, return ID immediately"""
        if ai_id not in self.queues:
            raise ValueError(f"AI {ai_id} not registered")
            
        msg_id = str(uuid.uuid4())
        self.queues[ai_id][msg_id] = Message(id=msg_id, request=request)
        
        if self.debug:
            print(f"Queued {msg_id} for {ai_id}")
            
        return msg_id
        
    @performance_boundary(
        title="Message Processing Pipeline",
        sla="<1s per batch of messages",
        optimization_notes="Async processing with direct socket communication",
        metrics={"batch_processing": "all_queued_messages"}
    )
    async def process_messages(self):
        """Process all queued messages through their sockets"""
        for ai_id, queue in self.queues.items():
            if ai_id not in self.sockets:
                continue
                
            reader, writer = self.sockets[ai_id]
            
            for msg_id, msg in list(queue.items()):
                if msg.response is None and msg.error is None:
                    try:
                        # Send message
                        request = {"type": "chat", "content": msg.request}
                        data = json.dumps(request).encode('utf-8') + b'\n'
                        writer.write(data)
                        await writer.drain()
                        
                        # Get response
                        response_data = await reader.readline()
                        if response_data:
                            response = json.loads(response_data.decode('utf-8').strip())
                            msg.response = response.get('response', response.get('content', str(response)))
                        else:
                            msg.error = "No response"
                    except Exception as e:
                        msg.error = str(e)
                        
    def process_messages_sync(self):
        """Sync wrapper for process_messages"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Can't use run_until_complete in running loop
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.process_messages())
                    future.result()
            else:
                loop.run_until_complete(self.process_messages())
        except RuntimeError:
            # No event loop
            asyncio.run(self.process_messages())
                        
    def get_response(self, ai_id: str, msg_id: str) -> Optional[Dict[str, Any]]:
        """Check if response is ready"""
        if ai_id not in self.queues or msg_id not in self.queues[ai_id]:
            return None
            
        msg = self.queues[ai_id][msg_id]
        if msg.response is not None:
            return {"success": True, "response": msg.response}
        elif msg.error is not None:
            return {"success": False, "error": msg.error}
        else:
            return None  # Still processing

    async def process_one_message(self, ai_id: str, msg_id: str):
        """Process a single message"""
        if ai_id not in self.queues or msg_id not in self.queues[ai_id]:
            return
            
        if ai_id not in self.sockets:
            return
            
        msg = self.queues[ai_id][msg_id]
        if msg.response is not None or msg.error is not None:
            return  # Already processed
            
        reader, writer = self.sockets[ai_id]
        
        try:
            # Send message
            request = {"type": "chat", "content": msg.request}
            data = json.dumps(request).encode('utf-8') + b'\n'
            writer.write(data)
            await writer.drain()
            
            # Get response
            response_data = await reader.readline()
            if response_data:
                response = json.loads(response_data.decode('utf-8').strip())
                msg.response = response.get('response', response.get('content', str(response)))
            else:
                msg.error = "No response"
        except Exception as e:
            msg.error = str(e)

    def send_message_sync(self, ai_id: str, message: str) -> str:
        """Synchronous send and receive - one call"""
        # For now, just raise error if sockets are registered
        # Real implementation would need separate sync sockets
        if ai_id in self.sockets:
            raise RuntimeError("send_message_sync cannot use async sockets. Use async methods or create sync sockets.")
        
        # If no socket registered, we can simulate for testing
        msg_id = self.send_request(ai_id, message)
        
        # Simulate processing
        msg = self.queues[ai_id][msg_id]
        msg.response = f"Mock response to: {message}"
        
        # Get response
        result = self.get_response(ai_id, msg_id)
        if result and result['success']:
            return result['response']
        else:
            raise Exception("No response received")

    def send_message_async(self, ai_id: str, message: str) -> str:
        """Async send - just queue and return msg_id"""
        return self.send_request(ai_id, message)

    def send_to_all(self, message: str, ai_ids: list) -> Dict[str, str]:
        """Send message to multiple CIs, return dict of msg_ids"""
        msg_ids = {}
        for ai_id in ai_ids:
            try:
                msg_ids[ai_id] = self.send_request(ai_id, message)
            except Exception as e:
                if self.debug:
                    print(f"Failed to queue for {ai_id}: {e}")
        return msg_ids

    async def collect_responses(self, msg_ids: Dict[str, str], timeout: float = None):
        """Collect responses as they arrive
        
        Args:
            msg_ids: Dictionary of CI IDs to message IDs
            timeout: Optional timeout in seconds (None = no timeout for Claude)
        """
        start_time = time.time()
        remaining = set(msg_ids.keys())
        
        while remaining and (timeout is None or (time.time() - start_time) < timeout):
            for ai_id in list(remaining):
                msg_id = msg_ids[ai_id]
                response = self.get_response(ai_id, msg_id)
                
                if response is not None:
                    remaining.remove(ai_id)
                    yield ai_id, response
            
            if remaining:
                await asyncio.sleep(0.1)  # Small delay before checking again

# Global instance
_service = None

def get_service(debug: bool = False) -> CIService:
    global _service
    if _service is None:
        _service = CIService(debug=debug)
    return _service