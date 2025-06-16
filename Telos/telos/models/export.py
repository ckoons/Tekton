"""
Export data models for Telos requirements management.

This module provides Pydantic models for data export and import.
"""

from typing import Dict, List, Optional, Any
from pydantic import Field
from tekton.models.base import TektonBaseModel

class ExportOptions(TektonBaseModel):
    """Model for export options."""
    format: str = "json"  # json, markdown, pdf, etc.
    sections: Optional[List[str]] = None
    include_metadata: Optional[bool] = True
    include_history: Optional[bool] = False
    include_traces: Optional[bool] = True

class ExportResult(TektonBaseModel):
    """Model for export result."""
    format: str
    content: Any
    filename: Optional[str] = None

class ImportOptions(TektonBaseModel):
    """Model for import options."""
    format: str = "json"
    merge_strategy: Optional[str] = "replace"  # replace, merge, or skip
    ignore_conflicts: Optional[bool] = False

class ImportResult(TektonBaseModel):
    """Model for import result."""
    project_id: str
    name: str
    imported_requirements: int
    conflicts: Optional[int] = 0
    warnings: Optional[List[str]] = Field(default_factory=list)

class ExportModel(TektonBaseModel):
    """Model for export data."""
    options: ExportOptions
    result: ExportResult