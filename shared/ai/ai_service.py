#!/usr/bin/env python3
"""
AI Service - One Queue, One Socket, One AI
"""

import asyncio
import json
import time
import uuid
from typing import Dict, Optional, Any, List
from dataclasses import dataclass


@dataclass
class Message:
    id: str
    request: str
    response: Optional[str] = None
    error: Optional[str] = None
    timestamp: float = 0.0


@dataclass  
class Connection:
    ai_id: str
    host: str
    port: int
    reader: Optional[asyncio.StreamReader] = None
    writer: Optional[asyncio.StreamWriter] = None
    connected: bool = False


class AIService:
    """One queue per AI, one socket per AI"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.queues: Dict[str, Dict[str, Message]] = {}  # ai_id -> {msg_id -> Message}
        self.connections: Dict[str, Connection] = {}  # ai_id -> Connection
        self._loop = None  # Store the event loop
        
    def register_ai(self, ai_id: str, host: str, port: int):
        """Register an AI"""
        if ai_id not in self.connections:
            self.connections[ai_id] = Connection(ai_id, host, port)
        if ai_id not in self.queues:
            self.queues[ai_id] = {}
            
    def send_request(self, ai_id: str, request: str) -> str:
        """Queue a request, return ID"""
        if ai_id not in self.queues:
            raise ValueError(f"AI {ai_id} not registered")
            
        msg_id = str(uuid.uuid4())
        self.queues[ai_id][msg_id] = Message(
            id=msg_id,
            request=request,
            timestamp=time.time()
        )
        
        if self.debug:
            print(f"Queued {msg_id} for {ai_id}")
            
        return msg_id
        
    async def process_message(self, ai_id: str, msg_id: str):
        """Process a specific message"""
        if ai_id not in self.queues or msg_id not in self.queues[ai_id]:
            return
            
        msg = self.queues[ai_id][msg_id]
        conn = self.connections[ai_id]
        
        # Connect if needed
        if not conn.connected:
            await self._connect(conn)
            
        # Send message
        if conn.connected:
            await self._send_message(conn, msg)
            
    async def process_all_messages(self):
        """Process all pending messages"""
        # Find all pending messages
        tasks = []
        for ai_id, queue in self.queues.items():
            for msg in queue.values():
                if msg.response is None and msg.error is None:
                    tasks.append(self.process_message(ai_id, msg.id))
                    
        # Process in batches of 5 to avoid overwhelming the system
        if tasks:
            batch_size = 5
            for i in range(0, len(tasks), batch_size):
                batch = tasks[i:i + batch_size]
                await asyncio.gather(*batch, return_exceptions=True)
        
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
            return None
            
    async def _connect(self, conn: Connection):
        """Connect to AI"""
        try:
            # Close existing connection if any (might be from different loop)
            if conn.writer:
                try:
                    conn.writer.close()
                    await conn.writer.wait_closed()
                except:
                    pass
                conn.reader = None
                conn.writer = None
            
            conn.reader, conn.writer = await asyncio.open_connection(conn.host, conn.port)
            conn.connected = True
            if self.debug:
                print(f"Connected to {conn.ai_id} at {conn.host}:{conn.port}")
        except Exception as e:
            if self.debug:
                print(f"Failed to connect to {conn.ai_id} at {conn.host}:{conn.port}: {e}")
            conn.connected = False
                
    async def _send_message(self, conn: Connection, msg: Message):
        """Send message and wait for response"""
        try:
            # Send JSON format - same as working socket client
            request = {
                "type": "chat",
                "content": msg.request
            }
            data = json.dumps(request).encode('utf-8') + b'\n'
            
            if self.debug:
                print(f"Sending to {conn.ai_id}: {data}")
                
            conn.writer.write(data)
            await conn.writer.drain()
            
            if self.debug:
                print(f"Message sent to {conn.ai_id}, waiting for response...")
            
            # Read response with timeout
            response_data = await asyncio.wait_for(conn.reader.readline(), timeout=60.0)
            if self.debug:
                print(f"Raw response from {conn.ai_id}: {response_data[:200] if response_data else 'None'}")
            if response_data:
                # Parse JSON response
                response = json.loads(response_data.decode('utf-8').strip())
                # Extract the actual response content
                msg.response = response.get('response', response.get('content', str(response)))
                if self.debug:
                    print(f"Got response from {conn.ai_id}: {msg.response[:50]}...")
            else:
                msg.error = "No response"
                
        except asyncio.TimeoutError:
            msg.error = "Timeout"
            if self.debug:
                print(f"Timeout waiting for {conn.ai_id}")
        except Exception as e:
            msg.error = str(e)
            conn.connected = False
            if self.debug:
                print(f"Error reading from {conn.ai_id}: {e}")
            
    # Team chat helpers
    
    def broadcast(self, request: str, ai_ids: List[str]) -> Dict[str, str]:
        """Send to multiple AIs"""
        return {ai_id: self.send_request(ai_id, request) for ai_id in ai_ids}
    
    async def send_message(self, ai_id: str, message: str, host: str = None, port: int = None, timeout: float = 30.0) -> str:
        """Simple async method to send message and get response"""
        # Register AI if needed
        if ai_id not in self.connections:
            if not host or not port:
                raise ValueError(f"AI {ai_id} not registered and no host/port provided")
            self.register_ai(ai_id, host, port)
        
        # Queue the message
        msg_id = self.send_request(ai_id, message)
        
        # Process it
        await self.process_message(ai_id, msg_id)
        
        # Get response
        response = self.get_response(ai_id, msg_id)
        
        if response:
            if response['success']:
                return response['response']
            else:
                raise Exception(f"AI error: {response['error']}")
        else:
            raise TimeoutError(f"No response from {ai_id}")
    
    def send_message_sync(self, ai_id: str, message: str, host: str = None, port: int = None, timeout: float = 30.0) -> str:
        """Simple sync method to send message and get response"""
        import asyncio
        
        # Check if we're in an event loop
        try:
            loop = asyncio.get_running_loop()
            # Already in a loop, use thread pool to run in new loop
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    self.send_message(ai_id, message, host, port, timeout)
                )
                return future.result()
        except RuntimeError:
            # No loop running
            if self._loop is None:
                # Create and store a loop for this service instance
                self._loop = asyncio.new_event_loop()
            
            # Run in our persistent loop
            asyncio.set_event_loop(self._loop)
            try:
                return self._loop.run_until_complete(
                    self.send_message(ai_id, message, host, port, timeout)
                )
            finally:
                # Don't close the loop - we'll reuse it
                asyncio.set_event_loop(None)
        
    async def collect_responses(self, msg_ids: Dict[str, str], timeout: float = 35.0):
        """Yield responses as they arrive"""
        start = time.time()
        remaining = set(msg_ids.keys())
        
        while remaining and time.time() - start < timeout:
            for ai_id in list(remaining):
                msg_id = msg_ids[ai_id]
                response = self.get_response(ai_id, msg_id)
                
                if response:
                    remaining.remove(ai_id)
                    yield ai_id, response
                    
            await asyncio.sleep(0.1)


# Global instance
_service = None

def get_service(debug: bool = False) -> AIService:
    global _service
    if _service is None:
        _service = AIService(debug=debug)
    return _service