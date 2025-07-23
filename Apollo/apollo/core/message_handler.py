"""
Message Handler Module for Apollo.

This module is responsible for handling bi-directional communication between
Apollo and other Tekton components. It integrates with Hermes for message
distribution and provides a pub/sub mechanism for component communication.
"""

import os
import json
import logging
import asyncio
import time
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Set, Callable
import uuid
import re

from apollo.models.message import (
    TektonMessage,
    MessageType,
    MessagePriority,
    ContextMessage,
    ActionMessage,
    BudgetMessage,
    ProtocolMessage,
    PredictionMessage,
    CommandMessage,
    QueryMessage,
    MessageBatch,
    MessageSubscription,
    MessageDeliveryStatus,
    MessageDeliveryRecord
)
# Try to import landmarks
try:
    from landmarks import integration_point, state_checkpoint, performance_boundary
except ImportError:
    # Define no-op decorators if landmarks not available
    def integration_point(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

from apollo.core.protocol_enforcer import ProtocolEnforcer
# from tekton.utils.port_config import get_hermes_url
def get_hermes_url() -> str:
    return "http://localhost:8001"

# Configure logging
logger = logging.getLogger(__name__)


class MessageFilter:
    """Filter for message subscriptions."""
    
    def __init__(self, filter_expression: str):
        """
        Initialize the message filter.
        
        Args:
            filter_expression: Filter expression to parse
        """
        self.filter_expression = filter_expression
        self.parsed_expression = self._parse_expression(filter_expression)
    
    def _parse_expression(self, expression: str) -> Dict[str, Any]:
        """
        Parse a filter expression into a structured format.
        
        The expression format is a simple key-value format with optional
        operators for comparison. For example:
        
        - "context_id=123" - Exact match
        - "priority>5" - Greater than
        - "source=~athena.*" - Regex match
        
        Args:
            expression: Filter expression to parse
            
        Returns:
            Parsed expression as a dict
        """
        parsed = {}
        
        # Skip if empty
        if not expression:
            return parsed
            
        # Split by AND
        conditions = expression.split(" AND ")
        
        for condition in conditions:
            # Check for various operators
            if "=~" in condition:
                key, value = condition.split("=~", 1)
                parsed[key.strip()] = {"op": "regex", "value": value.strip()}
            elif "!=" in condition:
                key, value = condition.split("!=", 1)
                parsed[key.strip()] = {"op": "not_equal", "value": value.strip()}
            elif ">=" in condition:
                key, value = condition.split(">=", 1)
                parsed[key.strip()] = {"op": "gte", "value": value.strip()}
            elif "<=" in condition:
                key, value = condition.split("<=", 1)
                parsed[key.strip()] = {"op": "lte", "value": value.strip()}
            elif ">" in condition:
                key, value = condition.split(">", 1)
                parsed[key.strip()] = {"op": "gt", "value": value.strip()}
            elif "<" in condition:
                key, value = condition.split("<", 1)
                parsed[key.strip()] = {"op": "lt", "value": value.strip()}
            elif "=" in condition:
                key, value = condition.split("=", 1)
                parsed[key.strip()] = {"op": "equal", "value": value.strip()}
            else:
                # Invalid condition
                logger.warning(f"Invalid filter condition: {condition}")
        
        return parsed
    
    def matches(self, message: TektonMessage) -> bool:
        """
        Check if a message matches this filter.
        
        Args:
            message: Message to check
            
        Returns:
            True if the message matches, False otherwise
        """
        # If no filter, always match
        if not self.parsed_expression:
            return True
            
        # Check each condition
        for key, condition in self.parsed_expression.items():
            # Get value from message
            if key == "payload" or key.startswith("payload."):
                # Handle payload fields
                if key == "payload":
                    value = message.payload
                else:
                    # Extract nested payload field
                    field = key[8:]  # Remove "payload."
                    value = message.payload.get(field)
            elif key == "metadata" or key.startswith("metadata."):
                # Handle metadata fields
                if key == "metadata":
                    value = message.metadata
                else:
                    # Extract nested metadata field
                    field = key[9:]  # Remove "metadata."
                    value = message.metadata.get(field)
            else:
                # Handle message attributes
                value = getattr(message, key, None)
            
            # Skip if field not found
            if value is None:
                return False
                
            # Check condition
            op = condition["op"]
            expected = condition["value"]
            
            # Convert expected value type if needed
            if isinstance(value, int) and not isinstance(expected, int):
                try:
                    expected = int(expected)
                except ValueError:
                    pass
            elif isinstance(value, float) and not isinstance(expected, float):
                try:
                    expected = float(expected)
                except ValueError:
                    pass
            elif isinstance(value, bool) and not isinstance(expected, bool):
                expected = expected.lower() == "true"
            
            # Perform comparison
            if op == "equal":
                if value != expected:
                    return False
            elif op == "not_equal":
                if value == expected:
                    return False
            elif op == "gt":
                if not value > expected:
                    return False
            elif op == "gte":
                if not value >= expected:
                    return False
            elif op == "lt":
                if not value < expected:
                    return False
            elif op == "lte":
                if not value <= expected:
                    return False
            elif op == "regex":
                try:
                    if not re.search(expected, str(value)):
                        return False
                except re.error:
                    logger.error(f"Invalid regex pattern: {expected}")
                    return False
        
        # All conditions matched
        return True


@integration_point(
    title="Apollo-Hermes Message Bus Client",
    target_component="Hermes Message Bus",
    protocol="HTTP/JSON REST API",
    data_flow="Apollo → Hermes (messages, subscriptions) → Other components",
    critical_notes="Central integration point for all Apollo messaging"
)
class HermesClient:
    """Client for interacting with Hermes message bus."""
    
    def __init__(self, base_url: Optional[str] = None, timeout: float = 10.0):
        """
        Initialize the Hermes client.
        
        Args:
            base_url: Base URL for Hermes API, defaults to config
            timeout: Timeout for HTTP requests in seconds
        """
        self.base_url = base_url or get_hermes_url()
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def send_message(self, message: TektonMessage) -> bool:
        """
        Send a message to Hermes.
        
        Args:
            message: Message to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            url = f"{self.base_url}/api/messages"
            response = await self.client.post(
                url, 
                json=message.model_dump(),
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.debug(f"Message {message.message_id} sent to Hermes")
                return True
            else:
                logger.error(f"Failed to send message to Hermes: {response.status_code} {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message to Hermes: {e}")
            return False
    
    async def send_batch(self, batch: MessageBatch) -> bool:
        """
        Send a batch of messages to Hermes.
        
        Args:
            batch: Batch of messages to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            url = f"{self.base_url}/api/messages/batch"
            response = await self.client.post(
                url, 
                json=batch.model_dump(),
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.debug(f"Batch {batch.batch_id} with {len(batch.messages)} messages sent to Hermes")
                return True
            else:
                logger.error(f"Failed to send batch to Hermes: {response.status_code} {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending batch to Hermes: {e}")
            return False
    
    async def subscribe(self, subscription: MessageSubscription) -> Optional[str]:
        """
        Create a subscription in Hermes.
        
        Args:
            subscription: Subscription to create
            
        Returns:
            Subscription ID if created successfully, None otherwise
        """
        try:
            url = f"{self.base_url}/api/subscriptions"
            response = await self.client.post(
                url, 
                json=subscription.model_dump(),
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                subscription_id = result.get("subscription_id")
                logger.info(f"Created subscription {subscription_id} in Hermes")
                return subscription_id
            else:
                logger.error(f"Failed to create subscription in Hermes: {response.status_code} {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating subscription in Hermes: {e}")
            return None
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """
        Delete a subscription from Hermes.
        
        Args:
            subscription_id: ID of subscription to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            url = f"{self.base_url}/api/subscriptions/{subscription_id}"
            response = await self.client.delete(url)
            
            if response.status_code == 200:
                logger.info(f"Deleted subscription {subscription_id} from Hermes")
                return True
            else:
                logger.error(f"Failed to delete subscription from Hermes: {response.status_code} {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting subscription from Hermes: {e}")
            return False
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


@state_checkpoint(
    title="Apollo Message Handler State",
    state_type="operational",
    persistence=True,
    consistency_requirements="Message queues, subscriptions, and delivery records must be consistent",
    recovery_strategy="Reload from disk, requeue failed messages"
)
@performance_boundary(
    title="Message Processing Performance",
    sla="<100ms message processing, batch send every 1s",
    metrics={"batch_size": "10 messages", "queue_limit": "1000 messages"},
    optimization_notes="Async processing, message batching, retry logic"
)
class MessageHandler:
    """
    Message handler for Apollo that manages communication with other components.
    
    This class provides messaging functionality for Apollo, including sending
    and receiving messages, managing subscriptions, and integrating with Hermes.
    """
    
    def __init__(
        self,
        component_name: str = "apollo",
        hermes_client: Optional[HermesClient] = None,
        protocol_enforcer: Optional[ProtocolEnforcer] = None,
        message_queue_limit: int = 1000,
        retry_interval: float = 5.0,
        max_retry_count: int = 3,
        delivery_history_limit: int = 10000,
        data_dir: Optional[str] = None
    ):
        """
        Initialize the Message Handler.
        
        Args:
            component_name: Name of this component
            hermes_client: Client for Hermes, created if not provided
            protocol_enforcer: Protocol enforcer for validating messages
            message_queue_limit: Maximum messages in queue
            retry_interval: Interval for retrying failed deliveries in seconds
            max_retry_count: Maximum retry attempts for failed deliveries
            delivery_history_limit: Maximum delivery records to keep
            data_dir: Directory for storing message data
        """
        self.component_name = component_name
        self.hermes_client = hermes_client or HermesClient()
        self.protocol_enforcer = protocol_enforcer
        self.message_queue_limit = message_queue_limit
        self.retry_interval = retry_interval
        self.max_retry_count = max_retry_count
        self.delivery_history_limit = delivery_history_limit
        
        # Set up data directory
        if data_dir:
            self.data_dir = data_dir
        else:
            # Use $TEKTON_DATA_DIR/apollo/message_data by default
            default_data_dir = os.path.join(
                os.environ.get('TEKTON_DATA_DIR', 
                              os.path.join(os.environ.get('TEKTON_ROOT', os.path.expanduser('~')), '.tekton', 'data')),
                'apollo', 'message_data'
            )
            self.data_dir = default_data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize message queues
        self.outbound_queue: asyncio.Queue = asyncio.Queue(maxsize=message_queue_limit)
        self.inbound_queue: asyncio.Queue = asyncio.Queue(maxsize=message_queue_limit)
        
        # Delivery tracking
        self.delivery_records: Dict[str, MessageDeliveryRecord] = {}
        
        # Local subscriptions
        self.local_subscriptions: Dict[str, Dict[str, Any]] = {}
        
        # Remote subscriptions
        self.remote_subscriptions: Dict[str, MessageSubscription] = {}
        
        # For task management
        self.is_running = False
        self.processing_tasks: List[asyncio.Task] = []
        
        # For callbacks
        self.message_callbacks: Dict[MessageType, List[Callable]] = {}
        
        # Message batching
        self.batch_size = 10
        self.batch_interval = 1.0  # seconds
        self.current_batch: List[TektonMessage] = []
        self.batch_lock = asyncio.Lock()
    
    async def start(self):
        """Start the message handler."""
        if self.is_running:
            logger.warning("Message handler is already running")
            return
            
        self.is_running = True
        
        # Start outbound message processor
        self.processing_tasks.append(
            asyncio.create_task(self._process_outbound_messages())
        )
        
        # Start inbound message processor
        self.processing_tasks.append(
            asyncio.create_task(self._process_inbound_messages())
        )
        
        # Start message batch processor
        self.processing_tasks.append(
            asyncio.create_task(self._process_batched_messages())
        )
        
        # Start failed delivery retry processor
        self.processing_tasks.append(
            asyncio.create_task(self._retry_failed_deliveries())
        )
        
        logger.info("Message handler started")
    
    async def stop(self):
        """Stop the message handler."""
        if not self.is_running:
            logger.warning("Message handler is not running")
            return
            
        self.is_running = False
        
        # Cancel processing tasks
        for task in self.processing_tasks:
            task.cancel()
            
        # Wait for tasks to complete
        for task in self.processing_tasks:
            try:
                await task
            except asyncio.CancelledError:
                pass
                
        # Close Hermes client
        await self.hermes_client.close()
        
        # Save delivery records
        await self._save_delivery_records()
        
        logger.info("Message handler stopped")
    
    async def _process_outbound_messages(self):
        """Process outbound messages from the queue."""
        try:
            while self.is_running:
                # Get message from queue
                message = await self.outbound_queue.get()
                
                # Add to current batch
                async with self.batch_lock:
                    self.current_batch.append(message)
                    
                    # If batch is full, flush it immediately
                    if len(self.current_batch) >= self.batch_size:
                        await self._flush_batch()
                        
                # Mark task as done
                self.outbound_queue.task_done()
                
        except asyncio.CancelledError:
            logger.info("Outbound message processor cancelled")
            raise
        except Exception as e:
            logger.error(f"Error processing outbound messages: {e}")
            raise
    
    async def _process_batched_messages(self):
        """Process batched messages on an interval."""
        try:
            while self.is_running:
                # Sleep for batch interval
                await asyncio.sleep(self.batch_interval)
                
                # Flush current batch if not empty
                async with self.batch_lock:
                    if self.current_batch:
                        await self._flush_batch()
                        
        except asyncio.CancelledError:
            logger.info("Batch processor cancelled")
            
            # Flush any remaining messages
            async with self.batch_lock:
                if self.current_batch:
                    await self._flush_batch()
                    
            raise
        except Exception as e:
            logger.error(f"Error processing batched messages: {e}")
            raise
    
    async def _flush_batch(self):
        """Flush the current batch of messages to Hermes."""
        # Skip if empty
        if not self.current_batch:
            return
            
        # Create batch
        batch = MessageBatch(
            source=self.component_name,
            messages=self.current_batch.copy()
        )
        
        # Clear current batch
        self.current_batch = []
        
        # Send batch to Hermes
        success = await self.hermes_client.send_batch(batch)
        
        if not success:
            logger.error(f"Failed to send batch {batch.batch_id}, requeuing messages")
            
            # Requeue messages
            for message in batch.messages:
                try:
                    await self.outbound_queue.put(message)
                except asyncio.QueueFull:
                    logger.error(f"Outbound queue full, dropping message {message.message_id}")
    
    async def _process_inbound_messages(self):
        """Process inbound messages from the queue."""
        try:
            while self.is_running:
                # Get message from queue
                message = await self.inbound_queue.get()
                
                # Validate message if protocol enforcer is available
                if self.protocol_enforcer:
                    context = {
                        "component": self.component_name,
                        "message_type": str(message.type)
                    }
                    
                    # Handle message according to protocols
                    result = await self.protocol_enforcer.handle_message(
                        message.model_dump(), context
                    )
                    
                    # Skip if message was blocked
                    if not result:
                        logger.warning(f"Message {message.message_id} blocked by protocol enforcer")
                        self.inbound_queue.task_done()
                        continue
                
                # Process message
                await self._handle_inbound_message(message)
                
                # Mark task as done
                self.inbound_queue.task_done()
                
        except asyncio.CancelledError:
            logger.info("Inbound message processor cancelled")
            raise
        except Exception as e:
            logger.error(f"Error processing inbound messages: {e}")
            raise
    
    async def _retry_failed_deliveries(self):
        """Retry failed message deliveries."""
        try:
            while self.is_running:
                # Sleep for retry interval
                await asyncio.sleep(self.retry_interval)
                
                # Find failed deliveries to retry
                now = datetime.now()
                retry_records = []
                
                for message_id, record in self.delivery_records.items():
                    if (record.status == MessageDeliveryStatus.FAILED and 
                        record.attempt_count < self.max_retry_count):
                        retry_records.append(record)
                
                # Retry each failed delivery
                for record in retry_records:
                    # TODO: Implement retry logic based on subscription type
                    
                    # Update record
                    record.attempt_count += 1
                    record.last_attempt = now
                    
                    # If max retries reached, mark as expired
                    if record.attempt_count >= self.max_retry_count:
                        record.status = MessageDeliveryStatus.EXPIRED
                        logger.warning(f"Message {record.message_id} delivery expired after {record.attempt_count} attempts")
                
                # Clean up old records
                if len(self.delivery_records) > self.delivery_history_limit:
                    # Sort by timestamp (oldest first)
                    sorted_records = sorted(
                        self.delivery_records.items(),
                        key=lambda item: item[1].last_attempt or datetime.min
                    )
                    
                    # Remove oldest records
                    excess = len(self.delivery_records) - self.delivery_history_limit
                    for i in range(excess):
                        if i < len(sorted_records):
                            del self.delivery_records[sorted_records[i][0]]
                
        except asyncio.CancelledError:
            logger.info("Retry processor cancelled")
            raise
        except Exception as e:
            logger.error(f"Error retrying failed deliveries: {e}")
            raise
    
    async def _handle_inbound_message(self, message: TektonMessage):
        """
        Handle an inbound message.
        
        Args:
            message: Message to handle
        """
        # Check for matching subscriptions
        matched_subscriptions = []
        
        for sub_id, subscription in self.local_subscriptions.items():
            # Check message type
            if message.type in subscription["message_types"]:
                # Check filter
                if subscription["filter"] is None or subscription["filter"].matches(message):
                    matched_subscriptions.append(subscription)
        
        # If no matching subscriptions, log and return
        if not matched_subscriptions:
            logger.debug(f"No matching subscriptions for message {message.message_id}")
            return
            
        # Process message for each subscription
        for subscription in matched_subscriptions:
            try:
                # Get callback
                callback = subscription["callback"]
                
                # Call callback
                if asyncio.iscoroutinefunction(callback):
                    await callback(message)
                else:
                    callback(message)
                    
                # Update delivery record
                self._record_delivery(
                    message.message_id,
                    subscription["id"],
                    MessageDeliveryStatus.DELIVERED
                )
                
            except Exception as e:
                logger.error(f"Error processing message for subscription {subscription['id']}: {e}")
                
                # Update delivery record
                self._record_delivery(
                    message.message_id,
                    subscription["id"],
                    MessageDeliveryStatus.FAILED,
                    str(e)
                )
    
    def _record_delivery(
        self,
        message_id: str,
        subscription_id: str,
        status: MessageDeliveryStatus,
        error_message: Optional[str] = None
    ):
        """
        Record a message delivery attempt.
        
        Args:
            message_id: ID of message delivered
            subscription_id: ID of subscription receiving the message
            status: Delivery status
            error_message: Optional error message if delivery failed
        """
        # Create record key
        record_key = f"{message_id}:{subscription_id}"
        
        # Update existing record if found
        if record_key in self.delivery_records:
            record = self.delivery_records[record_key]
            record.status = status
            record.attempt_count += 1
            record.last_attempt = datetime.now()
            
            if status == MessageDeliveryStatus.DELIVERED:
                record.delivered_at = datetime.now()
                
            if error_message:
                record.error_message = error_message
                
        # Otherwise create new record
        else:
            record = MessageDeliveryRecord(
                message_id=message_id,
                subscription_id=subscription_id,
                status=status,
                attempt_count=1,
                last_attempt=datetime.now(),
                delivered_at=datetime.now() if status == MessageDeliveryStatus.DELIVERED else None,
                error_message=error_message
            )
            
            self.delivery_records[record_key] = record
    
    async def _save_delivery_records(self):
        """Save delivery records to disk."""
        try:
            # Create filename
            filename = os.path.join(self.data_dir, f"delivery_records_{int(time.time())}.json")
            
            # Convert to dict
            records_data = {
                key: record.model_dump()
                for key, record in self.delivery_records.items()
            }
            
            # Save to file
            with open(filename, "w") as f:
                json.dump(records_data, f, indent=2, default=str)
                
            logger.info(f"Saved {len(records_data)} delivery records to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving delivery records: {e}")
    
    @integration_point(
        title="Apollo Outbound Message Flow",
        target_component="All Tekton Components via Hermes",
        protocol="Async message queue → batch send → Hermes HTTP API",
        data_flow="Apollo → Queue → Batch → Hermes → Target components"
    )
    async def send_message(self, message: TektonMessage) -> bool:
        """
        Send a message to other components via Hermes.
        
        Args:
            message: Message to send
            
        Returns:
            True if queued successfully, False otherwise
        """
        try:
            # Ensure source is set
            if not message.source:
                message.source = self.component_name
                
            # Ensure timestamp is set
            if not message.timestamp:
                message.timestamp = datetime.now()
                
            # Add to outbound queue
            try:
                await self.outbound_queue.put(message)
                logger.debug(f"Queued message {message.message_id} for sending")
                return True
            except asyncio.QueueFull:
                logger.error(f"Outbound queue full, dropping message {message.message_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    async def receive_message(self, message: TektonMessage) -> bool:
        """
        Receive a message from another component.
        
        This method is called by the API when a message is received.
        
        Args:
            message: Message received
            
        Returns:
            True if queued successfully, False otherwise
        """
        try:
            # Add to inbound queue
            try:
                await self.inbound_queue.put(message)
                logger.debug(f"Queued message {message.message_id} for processing")
                return True
            except asyncio.QueueFull:
                logger.error(f"Inbound queue full, dropping message {message.message_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            return False
    
    async def subscribe_local(
        self,
        message_types: List[MessageType],
        callback: Callable,
        filter_expression: Optional[str] = None
    ) -> str:
        """
        Subscribe to messages locally.
        
        Args:
            message_types: Types of messages to subscribe to
            callback: Callback function to call when message received
            filter_expression: Optional filter expression
            
        Returns:
            Subscription ID
        """
        # Create subscription ID
        subscription_id = str(uuid.uuid4())
        
        # Parse filter if provided
        filter_obj = None
        if filter_expression:
            filter_obj = MessageFilter(filter_expression)
            
        # Add to local subscriptions
        self.local_subscriptions[subscription_id] = {
            "id": subscription_id,
            "message_types": message_types,
            "filter": filter_obj,
            "callback": callback
        }
        
        logger.info(f"Created local subscription {subscription_id} for {len(message_types)} message types")
        
        return subscription_id
    
    async def unsubscribe_local(self, subscription_id: str) -> bool:
        """
        Unsubscribe from local messages.
        
        Args:
            subscription_id: ID of subscription to remove
            
        Returns:
            True if unsubscribed successfully, False otherwise
        """
        # Check if subscription exists
        if subscription_id not in self.local_subscriptions:
            logger.warning(f"Local subscription {subscription_id} not found")
            return False
            
        # Remove subscription
        del self.local_subscriptions[subscription_id]
        
        logger.info(f"Removed local subscription {subscription_id}")
        
        return True
    
    @integration_point(
        title="Apollo Event Subscription",
        target_component="Hermes Message Bus",
        protocol="HTTP subscription registration",
        data_flow="Apollo → Hermes (subscription) ← Other components (events)",
        critical_notes="Enables Apollo to receive async events from any component"
    )
    async def subscribe_remote(
        self,
        message_types: List[MessageType],
        callback_url: Optional[str] = None,
        filter_expression: Optional[str] = None
    ) -> Optional[str]:
        """
        Subscribe to messages from Hermes.
        
        Args:
            message_types: Types of messages to subscribe to
            callback_url: URL to call when message received
            filter_expression: Optional filter expression
            
        Returns:
            Subscription ID if created successfully, None otherwise
        """
        # Create subscription
        subscription = MessageSubscription(
            component=self.component_name,
            message_types=message_types,
            filter_expression=filter_expression,
            callback_url=callback_url
        )
        
        # Send to Hermes
        subscription_id = await self.hermes_client.subscribe(subscription)
        
        if subscription_id:
            # Store subscription
            self.remote_subscriptions[subscription_id] = subscription
            
            # If callback URL is not provided, messages will be sent to the API
            if not callback_url:
                # Register local handler for messages from Hermes
                await self.subscribe_local(
                    message_types=message_types,
                    callback=self._handle_remote_message,
                    filter_expression=filter_expression
                )
        
        return subscription_id
    
    async def unsubscribe_remote(self, subscription_id: str) -> bool:
        """
        Unsubscribe from remote messages.
        
        Args:
            subscription_id: ID of subscription to remove
            
        Returns:
            True if unsubscribed successfully, False otherwise
        """
        # Check if subscription exists
        if subscription_id not in self.remote_subscriptions:
            logger.warning(f"Remote subscription {subscription_id} not found")
            return False
            
        # Send to Hermes
        success = await self.hermes_client.unsubscribe(subscription_id)
        
        if success:
            # Remove subscription
            del self.remote_subscriptions[subscription_id]
            
            # Note: We don't remove the local subscription here as it may be
            # used by other remote subscriptions
        
        return success
    
    async def _handle_remote_message(self, message: TektonMessage):
        """
        Handle a message received from Hermes.
        
        Args:
            message: Message received
        """
        # Process message
        await self.receive_message(message)
    
    async def create_context_message(
        self,
        message_type: MessageType,
        context_id: str,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ContextMessage:
        """
        Create and send a context-related message.
        
        Args:
            message_type: Type of message to create
            context_id: Context identifier
            payload: Message payload
            priority: Message priority
            metadata: Optional message metadata
            
        Returns:
            Created message
        """
        # Create message
        message = ContextMessage(
            type=message_type,
            source=self.component_name,
            context_id=context_id,
            payload=payload,
            priority=priority,
            metadata=metadata or {}
        )
        
        # Send message
        await self.send_message(message)
        
        return message
    
    async def create_action_message(
        self,
        message_type: MessageType,
        context_id: str,
        action_id: str,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ActionMessage:
        """
        Create and send an action-related message.
        
        Args:
            message_type: Type of message to create
            context_id: Context identifier
            action_id: Action identifier
            payload: Message payload
            priority: Message priority
            metadata: Optional message metadata
            
        Returns:
            Created message
        """
        # Create message
        message = ActionMessage(
            type=message_type,
            source=self.component_name,
            context_id=context_id,
            payload={
                "action_id": action_id,
                **payload
            },
            priority=priority,
            metadata=metadata or {}
        )
        
        # Send message
        await self.send_message(message)
        
        return message
    
    async def create_budget_message(
        self,
        message_type: MessageType,
        context_id: Optional[str],
        component_id: str,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> BudgetMessage:
        """
        Create and send a budget-related message.
        
        Args:
            message_type: Type of message to create
            context_id: Optional context identifier
            component_id: Component identifier
            payload: Message payload
            priority: Message priority
            metadata: Optional message metadata
            
        Returns:
            Created message
        """
        # Create message
        message = BudgetMessage(
            type=message_type,
            source=self.component_name,
            context_id=context_id,
            payload={
                "component_id": component_id,
                **payload
            },
            priority=priority,
            metadata=metadata or {}
        )
        
        # Send message
        await self.send_message(message)
        
        return message
    
    async def create_command_message(
        self,
        component: str,
        command: str,
        parameters: Dict[str, Any],
        context_id: Optional[str] = None,
        priority: MessagePriority = MessagePriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CommandMessage:
        """
        Create and send a command message.
        
        Args:
            component: Component to send command to
            command: Command name
            parameters: Command parameters
            context_id: Optional context identifier
            priority: Message priority
            metadata: Optional message metadata
            
        Returns:
            Created message
        """
        # Create message
        message = CommandMessage(
            type=MessageType.COMMAND_EXECUTE,
            source=self.component_name,
            context_id=context_id,
            payload={
                "component": component,
                "command": command,
                "parameters": parameters
            },
            priority=priority,
            metadata=metadata or {}
        )
        
        # Send message
        await self.send_message(message)
        
        return message
    
    async def create_query_message(
        self,
        component: str,
        query: str,
        parameters: Dict[str, Any],
        context_id: Optional[str] = None,
        priority: MessagePriority = MessagePriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> QueryMessage:
        """
        Create and send a query message.
        
        Args:
            component: Component to query
            query: Query name
            parameters: Query parameters
            context_id: Optional context identifier
            priority: Message priority
            metadata: Optional message metadata
            
        Returns:
            Created message
        """
        # Create message
        message = QueryMessage(
            type=MessageType.QUERY_REQUEST,
            source=self.component_name,
            context_id=context_id,
            payload={
                "component": component,
                "query": query,
                "parameters": parameters
            },
            priority=priority,
            metadata=metadata or {}
        )
        
        # Send message
        await self.send_message(message)
        
        return message
    
    def register_message_callback(self, message_type: MessageType, callback: Callable):
        """
        Register a callback for a specific message type.
        
        This is a convenience method for registering callbacks for specific
        message types, rather than creating a full subscription.
        
        Args:
            message_type: Type of message to register for
            callback: Callback function to call when message received
        """
        # Initialize list if needed
        if message_type not in self.message_callbacks:
            self.message_callbacks[message_type] = []
            
        # Add callback
        self.message_callbacks[message_type].append(callback)
        
        # Create subscription if needed
        if self.is_running:
            asyncio.create_task(
                self.subscribe_local(
                    message_types=[message_type],
                    callback=self._handle_callback_message
                )
            )
    
    async def _handle_callback_message(self, message: TektonMessage):
        """
        Handle a message for registered callbacks.
        
        Args:
            message: Message received
        """
        # Check for callbacks
        if message.type in self.message_callbacks:
            # Call each callback
            for callback in self.message_callbacks[message.type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(message)
                    else:
                        callback(message)
                except Exception as e:
                    logger.error(f"Error in message callback: {e}")
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the message queues.
        
        Returns:
            Dictionary with queue statistics
        """
        return {
            "outbound_queue_size": self.outbound_queue.qsize(),
            "outbound_queue_max_size": self.message_queue_limit,
            "inbound_queue_size": self.inbound_queue.qsize(),
            "inbound_queue_max_size": self.message_queue_limit,
            "current_batch_size": len(self.current_batch),
            "batch_size_limit": self.batch_size,
            "delivery_records_count": len(self.delivery_records),
            "local_subscriptions_count": len(self.local_subscriptions),
            "remote_subscriptions_count": len(self.remote_subscriptions)
        }
    
    def get_delivery_stats(self) -> Dict[str, int]:
        """
        Get statistics about message delivery.
        
        Returns:
            Dictionary with delivery statistics
        """
        stats = {status.value: 0 for status in MessageDeliveryStatus}
        
        for record in self.delivery_records.values():
            stats[record.status.value] += 1
            
        return stats