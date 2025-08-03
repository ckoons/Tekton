"""
Socket bridge for CI tool communication.
Provides bidirectional socket-based communication with CI tool processes.
"""

import json
import logging
import socket
import threading
import time
import queue
from typing import Dict, Any, Optional, Callable

try:
    from landmarks import (
        architecture_decision, 
        integration_point, 
        performance_boundary,
        danger_zone,
        state_checkpoint
    )
except ImportError:
    def architecture_decision(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def danger_zone(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func):
            return func
        return decorator


@architecture_decision(
    title="Socket Bridge Architecture",
    description="Bidirectional bridge between CI tools and Tekton's socket interface",
    rationale="Maintains 'CIs are sockets' philosophy while allowing stdio-based tools",
    alternatives_considered=["Direct socket integration in tools", "HTTP REST APIs", "Named pipes"],
    impacts=["tool_communication", "message_routing", "client_compatibility"],
    decided_by="Casey",
    decision_date="2025-08-02"
)
@integration_point(
    title="Socket Bridge Integration",
    description="Bridges socket communication with CI tool processes",
    target_component="CI Tool Process",
    protocol="TCP Socket",
    data_flow="client → socket → bridge → adapter → tool",
    integration_date="2025-08-02"
)
class SocketBridge:
    """
    Manages socket-based communication with CI tools.
    
    Provides a clean interface for sending/receiving messages
    while handling the complexities of socket communication.
    """
    
    def __init__(self, tool_name: str, port: int):
        """
        Initialize socket bridge.
        
        Args:
            tool_name: Name of the CI tool
            port: Port number for socket communication
        """
        self.tool_name = tool_name
        self.port = port
        self.socket = None
        self.running = False
        self.logger = logging.getLogger(f"socket_bridge.{tool_name}")
        
        # Message queues
        self.outgoing_queue = queue.Queue()
        self.incoming_queue = queue.Queue()
        
        # Callbacks
        self.message_handler = None
        self.error_handler = None
        
        # Connection state
        self.connected = False
        self.connection_thread = None
        self.adapter = None
    
    def connect_adapter(self, adapter):
        """
        Connect the bridge to a CI tool adapter.
        
        Args:
            adapter: BaseCIToolAdapter instance
        """
        self.adapter = adapter
    
    @performance_boundary(
        title="Socket Start",
        description="Start socket bridge with minimal latency",
        sla="<100ms startup time",
        measured_impact="Negligible impact on tool launch"
    )
    def start(self) -> bool:
        """
        Start the socket bridge server.
        
        Returns:
            True if started successfully
        """
        if self.running:
            return True
        
        try:
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind to port
            self.socket.bind(('localhost', self.port))
            self.socket.listen(1)
            self.socket.settimeout(1.0)  # Non-blocking with timeout
            
            self.running = True
            
            # Start connection handler thread
            self.connection_thread = threading.Thread(
                target=self._handle_connections,
                daemon=True
            )
            self.connection_thread.start()
            
            self.logger.info(f"Socket bridge started on port {self.port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start socket bridge: {e}")
            return False
    
    def stop(self):
        """Stop the socket bridge."""
        self.running = False
        
        if self.connection_thread:
            self.connection_thread.join(timeout=2)
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        self.logger.info("Socket bridge stopped")
    
    def send_message(self, message: Dict[str, Any]) -> bool:
        """
        Send a message through the socket.
        
        Args:
            message: Message to send
            
        Returns:
            True if queued successfully
        """
        if not self.running:
            return False
        
        try:
            # Add timestamp if not present
            if 'timestamp' not in message:
                message['timestamp'] = time.time()
            
            # Queue message
            self.outgoing_queue.put(message)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to queue message: {e}")
            return False
    
    def get_message(self, timeout: float = 0.1) -> Optional[Dict[str, Any]]:
        """
        Get a received message.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Message or None if none available
        """
        try:
            return self.incoming_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def set_message_handler(self, handler: Callable[[Dict[str, Any]], None]):
        """Set callback for incoming messages."""
        self.message_handler = handler
    
    def set_error_handler(self, handler: Callable[[str], None]):
        """Set callback for errors."""
        self.error_handler = handler
    
    def _handle_connections(self):
        """Handle incoming socket connections."""
        while self.running:
            try:
                # Accept connection
                try:
                    client_socket, address = self.socket.accept()
                    self.logger.info(f"Client connected from {address}")
                    
                    # Handle this client
                    self._handle_client(client_socket)
                    
                except socket.timeout:
                    continue  # Normal timeout, keep listening
                    
            except Exception as e:
                if self.running:
                    self.logger.error(f"Connection handler error: {e}")
                    if self.error_handler:
                        self.error_handler(str(e))
    
    @danger_zone(
        title="Concurrent Client Handler",
        description="Manages client socket lifecycle with multiple threads",
        risk_level="medium",
        risks=["socket leaks", "thread synchronization", "message ordering"],
        mitigation="Proper cleanup, thread-safe queues, connection state tracking",
        review_required=False
    )
    def _handle_client(self, client_socket: socket.socket):
        """Handle a connected client."""
        self.connected = True
        client_socket.settimeout(0.1)
        
        # Start sender thread
        sender_thread = threading.Thread(
            target=self._send_loop,
            args=(client_socket,),
            daemon=True
        )
        sender_thread.start()
        
        # Receive loop
        buffer = ""
        while self.running and self.connected:
            try:
                # Receive data
                data = client_socket.recv(4096)
                if not data:
                    break  # Client disconnected
                
                # Add to buffer
                buffer += data.decode()
                
                # Process complete messages (newline delimited)
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        self._process_message(line.strip())
                        
            except socket.timeout:
                continue  # Normal timeout
                
            except Exception as e:
                self.logger.error(f"Receive error: {e}")
                break
        
        # Cleanup
        self.connected = False
        try:
            client_socket.close()
        except:
            pass
        
        self.logger.info("Client disconnected")
    
    def _send_loop(self, client_socket: socket.socket):
        """Send queued messages to client."""
        while self.running and self.connected:
            try:
                # Get message from queue
                message = self.outgoing_queue.get(timeout=0.1)
                
                # Send to client
                data = json.dumps(message) + '\n'
                client_socket.sendall(data.encode())
                
                self.logger.debug(f"Sent: {message.get('type', 'unknown')}")
                
            except queue.Empty:
                continue  # Normal timeout
                
            except Exception as e:
                self.logger.error(f"Send error: {e}")
                self.connected = False
                break
    
    def _process_message(self, data: str):
        """Process a received message."""
        try:
            # Parse JSON
            message = json.loads(data)
            
            # Add metadata
            message['_received_at'] = time.time()
            message['_source'] = self.tool_name
            
            # Queue for retrieval
            self.incoming_queue.put(message)
            
            # Call handler if set
            if self.message_handler:
                self.message_handler(message)
            
            self.logger.debug(f"Received: {message.get('type', 'unknown')}")
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON received: {e}")
            
            # If connected to adapter, try to parse as raw output
            if self.adapter:
                try:
                    translated = self.adapter.translate_from_tool(data)
                    self.incoming_queue.put(translated)
                    
                    if self.message_handler:
                        self.message_handler(translated)
                        
                except Exception as e2:
                    self.logger.error(f"Failed to translate raw output: {e2}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get bridge status."""
        return {
            'running': self.running,
            'connected': self.connected,
            'port': self.port,
            'outgoing_queue_size': self.outgoing_queue.qsize(),
            'incoming_queue_size': self.incoming_queue.qsize()
        }