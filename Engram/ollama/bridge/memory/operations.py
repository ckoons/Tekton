#!/usr/bin/env python3
"""
Memory Operations
This module provides functions for detecting and processing memory operations in model outputs.
"""

import re
from typing import List, Dict, Any, Tuple

from .handler import MemoryHandler

def detect_memory_operations(model_output: str, memory_handler=None) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Detect and execute memory operations in model output.
    
    Args:
        model_output: The output text from the model
        memory_handler: Optional memory handler to use (creates one if not provided)
        
    Returns:
        tuple: (cleaned_output, operation_results)
    """
    if memory_handler is None:
        memory_handler = MemoryHandler()
        
    operation_results = []
    cleaned_output = model_output
    
    # Define patterns for memory operations
    memory_patterns = [
        (r"(?:REMEMBER:|(?:\*\*)?REMEMBER(?:\*\*)?:?)\s*(.+?)(?=\n|$)", "store", MemoryHandler.store_memory),
        (r"(?:SEARCH:|(?:\*\*)?SEARCH(?:\*\*)?:?)\s*(.+?)(?=\n|$)", "search", MemoryHandler.search_memories),
        (r"(?:RETRIEVE:|(?:\*\*)?RETRIEVE(?:\*\*)?:?)\s*(\d+)(?=\n|$)", "retrieve", lambda n: MemoryHandler.get_recent_memories(int(n))),
        (r"(?:CONTEXT:|(?:\*\*)?CONTEXT(?:\*\*)?:?)\s*(.+?)(?=\n|$)", "context", MemoryHandler.get_context_memories),
        (r"(?:SEMANTIC:|(?:\*\*)?SEMANTIC(?:\*\*)?:?)\s*(.+?)(?=\n|$)", "semantic", MemoryHandler.get_semantic_memories),
        (r"(?:FORGET:|(?:\*\*)?FORGET(?:\*\*)?:?)\s*(.+?)(?=\n|$)", "forget", lambda info: MemoryHandler.store_memory(f"FORGET/IGNORE: {info}")),
        (r"(?:LIST:|(?:\*\*)?LIST(?:\*\*)?:?)\s*(\d+)(?=\n|$)", "list", lambda n: MemoryHandler.get_recent_memories(int(n))),
        (r"(?:SUMMARIZE:|(?:\*\*)?SUMMARIZE(?:\*\*)?:?)\s*(.+?)(?=\n|$)", "summarize", MemoryHandler.search_memories),
    ]
    
    # Check for patterns and execute corresponding functions
    for pattern, op_type, func in memory_patterns:
        try:
            # Standard pattern handling for memory operations
            matches = re.findall(pattern, model_output)
            for match in matches:
                try:
                    result = func(match)
                    operation_results.append({
                        "type": op_type,
                        "input": match,
                        "result": result
                    })
                    # Remove the operation from the output
                    cleaned_output = re.sub(pattern, "", cleaned_output, count=1)
                except Exception as e:
                    print(f"Error executing memory operation: {e}")
        except Exception as e:
            print(f"Error processing pattern {pattern}: {e}")
    
    # Clean up extra newlines caused by removal
    cleaned_output = re.sub(r'\n{3,}', '\n\n', cleaned_output)
    return cleaned_output.strip(), operation_results


def format_memory_operations_report(operations: List[Dict[str, Any]]) -> str:
    """
    Format memory operations into a readable report.
    
    Args:
        operations: List of memory operations and their results
        
    Returns:
        String with formatted report
    """
    if not operations:
        return ""
        
    report = "\n[Memory system: Detected memory operations]\n"
    
    for op in operations:
        op_type = op.get("type", "")
        op_input = op.get("input", "")
        
        if op_type == "store":
            report += f"[Memory system: Remembered '{op_input}']\n"
        elif op_type == "forget":
            report += f"[Memory system: Marked to forget '{op_input}']\n"
        elif op_type in ["search", "retrieve", "context", "semantic", "list", "summarize"]:
            report += f"[Memory system: {op_type.capitalize()} results for '{op_input}']\n"
            results = op.get("result", [])
            for i, result in enumerate(results[:3]):
                content = result.get("content", "")
                if content:
                    report += f"  {i+1}. {content[:80]}...\n"
    
    return report