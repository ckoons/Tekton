"""
Webhook models for Harmonia.

This module defines the data models for webhook functionality,
including webhook definitions, triggers, and event handling.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from uuid import UUID, uuid4

from pydantic import Field, validator, HttpUrl
from tekton.models import TektonBaseModel


class WebhookTriggerType(str, Enum):
    """Types of webhook triggers."""
    
    HTTP_POST = "http_post"
    HTTP_GET = "http_get"
    SCHEDULED = "scheduled"
    EVENT_TRIGGERED = "event_triggered"
    COMPONENT_CALLBACK = "component_callback"
    MANUAL = "manual"


class WebhookAuthType(str, Enum):
    """Types of webhook authentication."""
    
    NONE = "none"
    BASIC = "basic"
    BEARER = "bearer"
    API_KEY = "api_key"
    HMAC = "hmac"
    CUSTOM = "custom"


class WebhookDefinition(TektonBaseModel):
    """Definition of a webhook."""
    
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the webhook")
    name: str = Field(..., description="Name of the webhook")
    description: Optional[str] = Field(None, description="Description of the webhook")
    endpoint: str = Field(..., description="Endpoint path for the webhook")
    trigger_type: WebhookTriggerType = Field(WebhookTriggerType.HTTP_POST, description="Type of trigger")
    workflow_id: UUID = Field(..., description="ID of the workflow to trigger")
    input_mapping: Dict[str, str] = Field(default_factory=dict, description="Mapping from webhook payload to workflow input")
    enabled: bool = Field(True, description="Whether the webhook is enabled")
    auth_type: WebhookAuthType = Field(WebhookAuthType.NONE, description="Authentication type")
    auth_config: Dict[str, Any] = Field(default_factory=dict, description="Authentication configuration")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator("endpoint")
    def validate_endpoint(cls, v):
        """Validate webhook endpoint."""
        if not v.startswith("/"):
            return f"/{v}"
        return v


class WebhookEvent(TektonBaseModel):
    """Event representing a webhook invocation."""
    
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the event")
    webhook_id: UUID = Field(..., description="ID of the webhook")
    timestamp: datetime = Field(default_factory=datetime.now, description="Time when the event occurred")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Payload received in the webhook")
    headers: Dict[str, str] = Field(default_factory=dict, description="Headers received with the webhook")
    source_ip: Optional[str] = Field(None, description="IP address of the source")
    execution_id: Optional[UUID] = Field(None, description="ID of the workflow execution triggered")
    status: str = Field("pending", description="Status of the webhook processing")
    response: Optional[Dict[str, Any]] = Field(None, description="Response sent back to the caller")
    error: Optional[str] = Field(None, description="Error message if processing failed")


class WebhookSubscription(TektonBaseModel):
    """Subscription for receiving webhooks from external systems."""
    
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the subscription")
    name: str = Field(..., description="Name of the subscription")
    description: Optional[str] = Field(None, description="Description of the subscription")
    external_url: HttpUrl = Field(..., description="URL of the external system's webhook endpoint")
    payload_template: Dict[str, Any] = Field(default_factory=dict, description="Template for the payload to send")
    headers: Dict[str, str] = Field(default_factory=dict, description="Headers to include in the request")
    auth_type: WebhookAuthType = Field(WebhookAuthType.NONE, description="Authentication type")
    auth_config: Dict[str, Any] = Field(default_factory=dict, description="Authentication configuration")
    retry_config: Dict[str, Any] = Field(default_factory=dict, description="Retry configuration")
    enabled: bool = Field(True, description="Whether the subscription is enabled")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class WebhookDelivery(TektonBaseModel):
    """Record of a webhook delivery attempt."""
    
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the delivery")
    subscription_id: UUID = Field(..., description="ID of the subscription")
    timestamp: datetime = Field(default_factory=datetime.now, description="Time when the delivery was attempted")
    payload: Dict[str, Any] = Field(..., description="Payload that was sent")
    headers: Dict[str, str] = Field(default_factory=dict, description="Headers that were sent")
    status_code: Optional[int] = Field(None, description="HTTP status code received")
    response: Optional[Dict[str, Any]] = Field(None, description="Response received")
    success: bool = Field(False, description="Whether the delivery was successful")
    retry_count: int = Field(0, description="Number of retry attempts made")
    error: Optional[str] = Field(None, description="Error message if delivery failed")
    duration_ms: Optional[int] = Field(None, description="Duration of the delivery in milliseconds")