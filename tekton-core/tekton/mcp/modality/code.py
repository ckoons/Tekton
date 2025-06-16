"""
Code Processor - Processor for code content.

This module provides a processor for code content in the MCP protocol.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Union

from tekton.mcp.message import MCPContentItem
from tekton.mcp.modality.base import ModalityProcessor

logger = logging.getLogger(__name__)

class CodeProcessor(ModalityProcessor):
    """
    Processor for code content.
    
    This class provides methods for processing and validating
    code content in the MCP protocol.
    """
    
    def __init__(self):
        """Initialize the code processor."""
        super().__init__()
        logger.info("Code processor initialized")
    
    async def process(
        self,
        content_item: MCPContentItem,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a code content item.
        
        Args:
            content_item: Code content item to process
            context: Processing context
            
        Returns:
            Processing result
        """
        # Validate content item
        if not await self.validate(content_item):
            return {
                "error": "Invalid code content item",
                "processed": False
            }
            
        # Extract code data
        code_data = content_item.data
        
        # Determine code language
        language = content_item.metadata.get("language")
        if not language:
            language = self._detect_language(code_data, content_item.format)
            
        # Process the code
        # For now, just do basic analysis; this would normally involve
        # more sophisticated parsing and analysis
        
        # Count lines and characters
        line_count = len(code_data.splitlines())
        char_count = len(code_data)
        
        # Analyze code structure (simplified)
        structure_analysis = self._analyze_structure(code_data, language)
        
        # Create processed result
        processed_result = {
            "original_code": code_data,
            "language": language,
            "metrics": {
                "line_count": line_count,
                "char_count": char_count,
                "function_count": len(structure_analysis.get("functions", [])),
                "class_count": len(structure_analysis.get("classes", []))
            },
            "analysis": {
                "structure": structure_analysis,
                "complexity": self._analyze_complexity(code_data, language),
                "imports": self._extract_imports(code_data, language)
            },
            "processed": True
        }
        
        return processed_result
    
    async def validate(self, content_item: MCPContentItem) -> bool:
        """
        Validate a code content item.
        
        Args:
            content_item: Content item to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check content type
        if content_item.type != "code":
            logger.warning(f"Invalid content type for code processor: {content_item.type}")
            return False
            
        # Check data format
        if not isinstance(content_item.data, str):
            logger.warning("Invalid data format for code processor: data must be a string")
            return False
            
        # Check content format (MIME type)
        valid_formats = self.get_supported_formats()
        if content_item.format not in valid_formats:
            logger.warning(f"Unsupported format for code processor: {content_item.format}")
            # Still return True as we can process most code formats regardless
            
        return True
    
    def get_supported_formats(self) -> List[str]:
        """
        Get the formats supported by this processor.
        
        Returns:
            List of supported format strings
        """
        return [
            "text/plain",
            "text/x-python",
            "text/javascript",
            "text/x-java",
            "text/x-c",
            "text/x-c++",
            "text/x-csharp",
            "text/x-ruby",
            "text/x-go",
            "text/x-rust",
            "application/json"
        ]
    
    def _detect_language(self, code: str, format_hint: str) -> str:
        """
        Detect the programming language of code.
        
        Args:
            code: Code to analyze
            format_hint: Format hint from content item
            
        Returns:
            Detected language
        """
        # Check format hint first
        format_to_language = {
            "text/x-python": "python",
            "text/javascript": "javascript",
            "text/x-java": "java",
            "text/x-c": "c",
            "text/x-c++": "cpp",
            "text/x-csharp": "csharp",
            "text/x-ruby": "ruby",
            "text/x-go": "go",
            "text/x-rust": "rust",
            "application/json": "json"
        }
        
        if format_hint in format_to_language:
            return format_to_language[format_hint]
            
        # Check for language indicators in the code
        # These are very simplistic rules that would be much more sophisticated in reality
        if re.search(r"def\s+\w+\s*\(.*\):", code):
            return "python"
        elif re.search(r"function\s+\w+\s*\(.*\)", code) or re.search(r"const\s+\w+\s*=", code):
            return "javascript"
        elif re.search(r"public\s+class\s+\w+", code):
            return "java"
        elif re.search(r"#include", code):
            return "cpp"
        elif re.search(r"using\s+System;", code):
            return "csharp"
        elif re.search(r"fn\s+\w+\s*\(", code):
            return "rust"
        elif re.search(r"package\s+main", code):
            return "go"
        elif re.search(r"require\s+[\"']", code):
            return "ruby"
        elif re.search(r"^\s*\{", code) and re.search(r"\}\s*$", code):
            return "json"
        else:
            return "unknown"
    
    def _analyze_structure(self, code: str, language: str) -> Dict[str, Any]:
        """
        Analyze the structure of code.
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            Structure analysis result
        """
        # In a real implementation, this would use language-specific parsers
        # For now, just use some basic regex patterns for common constructs
        
        result = {
            "functions": [],
            "classes": [],
            "imports": []
        }
        
        # Extract function and class definitions
        if language == "python":
            # Find Python functions
            for match in re.finditer(r"def\s+(\w+)\s*\((.*?)\):", code):
                result["functions"].append({
                    "name": match.group(1),
                    "params": match.group(2),
                    "line": code[:match.start()].count("\n") + 1
                })
                
            # Find Python classes
            for match in re.finditer(r"class\s+(\w+)(?:\((.*?)\))?:", code):
                result["classes"].append({
                    "name": match.group(1),
                    "inherits": match.group(2) or "",
                    "line": code[:match.start()].count("\n") + 1
                })
                
        elif language == "javascript":
            # Find JavaScript functions
            for match in re.finditer(r"function\s+(\w+)\s*\((.*?)\)", code):
                result["functions"].append({
                    "name": match.group(1),
                    "params": match.group(2),
                    "line": code[:match.start()].count("\n") + 1
                })
                
            # Find JavaScript arrow functions and const functions
            for match in re.finditer(r"(const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\((.*?)\)\s*=>", code):
                result["functions"].append({
                    "name": match.group(2),
                    "params": match.group(3),
                    "type": "arrow",
                    "line": code[:match.start()].count("\n") + 1
                })
                
            # Find JavaScript classes
            for match in re.finditer(r"class\s+(\w+)(?:\s+extends\s+(\w+))?", code):
                result["classes"].append({
                    "name": match.group(1),
                    "inherits": match.group(2) or "",
                    "line": code[:match.start()].count("\n") + 1
                })
        
        return result
    
    def _analyze_complexity(self, code: str, language: str) -> Dict[str, Any]:
        """
        Analyze the complexity of code.
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            Complexity analysis result
        """
        # In a real implementation, this would use more sophisticated metrics
        # For now, just use some basic counting
        
        # Count control structures
        control_count = 0
        
        if language == "python":
            # Count Python control structures
            control_count += len(re.findall(r"\bif\b|\belif\b|\belse\b|\bfor\b|\bwhile\b|\btry\b|\bexcept\b", code))
        elif language == "javascript":
            # Count JavaScript control structures
            control_count += len(re.findall(r"\bif\b|\belse\b|\bfor\b|\bwhile\b|\bswitch\b|\btry\b|\bcatch\b", code))
        
        # Calculate nesting level (simplified)
        lines = code.splitlines()
        max_indentation = 0
        for line in lines:
            if line.strip():  # Skip empty lines
                indentation = len(line) - len(line.lstrip())
                max_indentation = max(max_indentation, indentation)
        
        # Estimate nesting level based on indentation
        estimated_nesting = max_indentation // 2 if language == "python" else max_indentation // 4
        
        return {
            "control_structures": control_count,
            "max_nesting": estimated_nesting,
            "estimation": "simplified"
        }
    
    def _extract_imports(self, code: str, language: str) -> List[str]:
        """
        Extract imports from code.
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            List of extracted imports
        """
        imports = []
        
        if language == "python":
            # Find Python imports
            for match in re.finditer(r"(?:import|from)\s+([\w\.]+)", code):
                imports.append(match.group(1))
        elif language == "javascript":
            # Find JavaScript imports
            for match in re.finditer(r"(?:import|require)\s+[\"']([\w\.\/\-]+)[\"']", code):
                imports.append(match.group(1))
        
        return imports