"""
Data models for Athena.
"""

from typing import Dict, Any, List, Optional, Set
from pydantic import Field, ConfigDict
from tekton.models import TektonBaseModel

from athena.core.entity import Entity


class EntityModel(TektonBaseModel):
    """Pydantic model wrapper for Entity class"""
    
    entity: Entity = Field(...)
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )