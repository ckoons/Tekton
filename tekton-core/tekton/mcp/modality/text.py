"""
Text Processor - Processor for text content.

This module provides a processor for text content in the MCP protocol.
"""

import logging
from typing import Dict, List, Any, Optional, Union

from tekton.mcp.message import MCPContentItem
from tekton.mcp.modality.base import ModalityProcessor

logger = logging.getLogger(__name__)

class TextProcessor(ModalityProcessor):
    """
    Processor for text content.
    
    This class provides methods for processing and validating
    text content in the MCP protocol.
    """
    
    def __init__(self):
        """Initialize the text processor."""
        super().__init__()
        logger.info("Text processor initialized")
    
    async def process(
        self,
        content_item: MCPContentItem,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a text content item.
        
        Args:
            content_item: Text content item to process
            context: Processing context
            
        Returns:
            Processing result
        """
        # Validate content item
        if not await self.validate(content_item):
            return {
                "error": "Invalid text content item",
                "processed": False
            }
            
        # Extract text data
        text_data = content_item.data
        
        # Process the text
        # For now, just do basic processing; this would normally involve
        # more sophisticated NLP processing
        
        # Count characters, words, and lines
        char_count = len(text_data)
        word_count = len(text_data.split())
        line_count = len(text_data.splitlines())
        
        # Calculate readability metrics (simplified)
        avg_word_length = char_count / word_count if word_count > 0 else 0
        
        # Extract any important entities (simplified)
        # In a real implementation, this would use NER or other techniques
        important_terms = self._extract_important_terms(text_data)
        
        # Create processed result
        processed_result = {
            "original_text": text_data,
            "metrics": {
                "char_count": char_count,
                "word_count": word_count,
                "line_count": line_count,
                "avg_word_length": avg_word_length
            },
            "analysis": {
                "important_terms": important_terms,
                "sentiment": self._analyze_sentiment(text_data),
                "type": self._determine_text_type(text_data)
            },
            "processed": True
        }
        
        return processed_result
    
    async def validate(self, content_item: MCPContentItem) -> bool:
        """
        Validate a text content item.
        
        Args:
            content_item: Content item to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check content type
        if content_item.type != "text":
            logger.warning(f"Invalid content type for text processor: {content_item.type}")
            return False
            
        # Check data format
        if not isinstance(content_item.data, str):
            logger.warning("Invalid data format for text processor: data must be a string")
            return False
            
        # Check content format (MIME type)
        valid_formats = self.get_supported_formats()
        if content_item.format not in valid_formats:
            logger.warning(f"Unsupported format for text processor: {content_item.format}")
            # Still return True as we can process most text formats regardless
            
        return True
    
    def get_supported_formats(self) -> List[str]:
        """
        Get the formats supported by this processor.
        
        Returns:
            List of supported format strings
        """
        return [
            "text/plain",
            "text/html",
            "text/markdown",
            "text/csv",
            "application/json"
        ]
    
    def _extract_important_terms(self, text: str) -> List[str]:
        """
        Extract important terms from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of important terms
        """
        # In a real implementation, this would use more sophisticated NLP
        # For now, just extract long words as a simple approximation
        words = text.split()
        return [word for word in words if len(word) > 8][:10]  # Top 10 long words
    
    def _analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis result
        """
        # In a real implementation, this would use a sentiment analysis model
        # For now, just use a very simplistic keyword approach
        positive_words = ["good", "great", "excellent", "amazing", "happy", "positive"]
        negative_words = ["bad", "poor", "terrible", "awful", "sad", "negative"]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _determine_text_type(self, text: str) -> str:
        """
        Determine the type of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Text type determination
        """
        # In a real implementation, this would use more sophisticated classification
        # For now, just use some basic heuristics
        
        # Check for question
        if "?" in text:
            return "question"
            
        # Check for code-like content
        code_indicators = ["function", "class", "def ", "import ", "var ", "const ", "let "]
        if any(indicator in text for indicator in code_indicators):
            return "code"
            
        # Check for list-like content
        list_indicators = ["\n- ", "\n* ", "\n1. ", "\n1) "]
        if any(indicator in text for indicator in list_indicators):
            return "list"
            
        # Default
        return "general"