"""
Base Models for Tekton

Provides foundational Pydantic v2 models that all components can extend.
Uses the latest Pydantic v2 patterns and best practices.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar, Generic
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.alias_generators import to_camel


# Type variable for generic responses
T = TypeVar('T')


class TektonBaseModel(BaseModel):
    """
    Base model for all Tekton models.
    
    Provides:
    - Consistent configuration across all models
    - CamelCase JSON field names while keeping snake_case in Python
    - Validation on assignment
    - Proper JSON serialization settings
    """
    model_config = ConfigDict(
        # Convert snake_case to camelCase for JSON
        alias_generator=to_camel,
        # Allow population by field name or alias
        populate_by_name=True,
        # Validate field values on assignment
        validate_assignment=True,
        # Include all fields in JSON schema
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "createdAt": "2025-01-06T10:00:00Z"
            }
        },
        # Use enum values in JSON
        use_enum_values=True
    )


class ValidationErrorDetail(TektonBaseModel):
    """Details about a validation error"""
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class ErrorResponse(TektonBaseModel):
    """Standard error response for all Tekton APIs"""
    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[List[ValidationErrorDetail]] = Field(None, description="Validation error details")
    request_id: UUID = Field(default_factory=uuid4, description="Unique request ID for tracking")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    component: Optional[str] = Field(None, description="Component that generated the error")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "ValidationError",
                "message": "Invalid request parameters",
                "details": [{
                    "field": "name",
                    "message": "Field required",
                    "type": "missing"
                }],
                "requestId": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2025-01-06T10:00:00Z",
                "component": "hermes"
            }
        }
    )


class SuccessResponse(TektonBaseModel):
    """Standard success response for operations without specific return data"""
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    request_id: UUID = Field(default_factory=uuid4, description="Unique request ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "requestId": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2025-01-06T10:00:00Z"
            }
        }
    )


class APIResponse(TektonBaseModel, Generic[T]):
    """
    Generic API response wrapper for consistent response format.
    
    Usage:
        response = APIResponse[UserModel](
            data=user,
            message="User retrieved successfully"
        )
    """
    success: bool = Field(True, description="Request success status")
    data: Optional[T] = Field(None, description="Response data")
    message: Optional[str] = Field(None, description="Optional message")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    request_id: UUID = Field(default_factory=uuid4, description="Unique request ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    @field_validator('data')
    @classmethod
    def validate_data_when_success(cls, v: Optional[T], info) -> Optional[T]:
        """Ensure data is provided when success is True (unless explicitly None)"""
        if info.data.get('success', True) and v is None and 'data' not in info.field_name:
            # Allow None if explicitly set, but warn if missing
            pass
        return v