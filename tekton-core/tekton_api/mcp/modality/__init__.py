"""
Modality Processors - Specialized processors for different content types.

This package provides specialized processors for different content modalities,
such as text, code, images, and structured data.
"""

from tekton.mcp.modality.base import ModalityProcessor
from tekton.mcp.modality.text import TextProcessor
from tekton.mcp.modality.code import CodeProcessor
from tekton.mcp.modality.image import ImageProcessor
from tekton.mcp.modality.structured import StructuredDataProcessor

__all__ = [
    "ModalityProcessor",
    "TextProcessor",
    "CodeProcessor",
    "ImageProcessor",
    "StructuredDataProcessor"
]