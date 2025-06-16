#!/usr/bin/env python3
"""
Pattern Matching Utilities
This module provides utilities for detecting and extracting patterns in text.
"""

import re
from typing import Dict, Any, List, Tuple, Callable, Optional

def detect_all_operations(model_output: str, handlers: Dict[str, Any]) -> Tuple[str, Dict[str, List[Dict[str, Any]]]]:
    """
    Detect all types of operations in model output.
    
    Args:
        model_output: The output text from the model
        handlers: Dictionary of handlers for different operation types
        
    Returns:
        tuple: (cleaned_output, grouped_operations)
    """
    from ..memory.operations import detect_memory_operations
    from ..communication.messenger import detect_communication_operations
    from ..communication.dialog import detect_dialog_operations
    
    # Get memory handler if provided
    memory_handler = handlers.get("memory")
    messenger = handlers.get("messenger")
    dialog_manager = handlers.get("dialog")
    
    # Initialize with original output
    cleaned_output = model_output
    all_operations = {}
    
    # Detect memory operations
    memory_cleaned, memory_ops = detect_memory_operations(cleaned_output, memory_handler)
    cleaned_output = memory_cleaned
    all_operations["memory"] = memory_ops
    
    # Detect communication operations
    comm_cleaned, comm_ops = detect_communication_operations(cleaned_output, messenger)
    cleaned_output = comm_cleaned
    all_operations["communication"] = comm_ops
    
    # Detect dialog operations
    dialog_cleaned, dialog_ops = detect_dialog_operations(cleaned_output, dialog_manager)
    cleaned_output = dialog_cleaned
    all_operations["dialog"] = dialog_ops
    
    return cleaned_output, all_operations

def format_operations_report(operations: Dict[str, List[Dict[str, Any]]]) -> str:
    """
    Format all operations into a combined report.
    
    Args:
        operations: Dictionary of operation types and their results
        
    Returns:
        String with formatted report
    """
    from ..memory.operations import format_memory_operations_report
    from ..communication.messenger import format_communication_operations_report
    
    report = ""
    
    # Add memory operations report
    memory_ops = operations.get("memory", [])
    if memory_ops:
        report += format_memory_operations_report(memory_ops)
    
    # Add communication operations report
    comm_ops = operations.get("communication", [])
    if comm_ops:
        report += format_communication_operations_report(comm_ops)
    
    # Add dialog operations report
    dialog_ops = operations.get("dialog", [])
    if dialog_ops:
        for op in dialog_ops:
            result = op.get("result", {})
            message = result.get("message", "Dialog mode activated")
            report += f"\n[Dialog] {message}\n"
    
    return report