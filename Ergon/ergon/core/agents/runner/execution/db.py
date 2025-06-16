"""
Database interactions for agent runner.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple

from ergon.core.database.engine import get_db_session
from ergon.core.database.models import AgentExecution, AgentMessage

# Configure logger
logger = logging.getLogger(__name__)

def record_execution_error(
    execution_id: Optional[int],
    error_msg: str
) -> None:
    """
    Record execution error in database.
    
    Args:
        execution_id: Execution ID (if None, no record is made)
        error_msg: Error message to record
    """
    if not execution_id:
        return
    
    try:
        with get_db_session() as db:
            execution = db.query(AgentExecution).filter(AgentExecution.id == execution_id).first()
            if execution:
                execution.success = False
                execution.error = error_msg
                execution.completed_at = datetime.now()
                db.commit()
                
                # Add error message to the conversation
                message = AgentMessage(
                    execution_id=execution_id,
                    role="system",
                    content=error_msg
                )
                db.add(message)
                db.commit()
    except Exception as e:
        logger.error(f"Error recording execution error: {str(e)}")


def record_execution_success(
    execution_id: Optional[int]
) -> None:
    """
    Record execution success in database.
    
    Args:
        execution_id: Execution ID (if None, no record is made)
    """
    if not execution_id:
        return
    
    try:
        with get_db_session() as db:
            execution = db.query(AgentExecution).filter(AgentExecution.id == execution_id).first()
            if execution:
                execution.success = True
                execution.completed_at = datetime.now()
                db.commit()
    except Exception as e:
        logger.error(f"Error recording execution success: {str(e)}")


def record_assistant_message(
    execution_id: Optional[int],
    content: str
) -> None:
    """
    Record assistant message in database.
    
    Args:
        execution_id: Execution ID (if None, no record is made)
        content: Message content
    """
    if not execution_id:
        return
    
    try:
        with get_db_session() as db:
            message = AgentMessage(
                execution_id=execution_id,
                role="assistant",
                content=content
            )
            db.add(message)
            db.commit()
    except Exception as e:
        logger.error(f"Error recording assistant message: {str(e)}")


def record_tool_call(
    execution_id: Optional[int],
    tool_name: str,
    tool_arguments: Dict[str, Any]
) -> None:
    """
    Record tool call in database.
    
    Args:
        execution_id: Execution ID (if None, no record is made)
        tool_name: Name of the tool called
        tool_arguments: Arguments passed to the tool
    """
    if not execution_id:
        return
    
    try:
        with get_db_session() as db:
            message = AgentMessage(
                execution_id=execution_id,
                role="tool",
                content="",
                tool_name=tool_name,
                tool_input=json.dumps(tool_arguments)
            )
            db.add(message)
            db.commit()
    except Exception as e:
        logger.error(f"Error recording tool call: {str(e)}")


def record_tool_result(
    execution_id: Optional[int],
    tool_name: str,
    tool_result: Any
) -> None:
    """
    Record tool result in database.
    
    Args:
        execution_id: Execution ID (if None, no record is made)
        tool_name: Name of the tool
        tool_result: Result returned by the tool
    """
    if not execution_id:
        return
    
    try:
        with get_db_session() as db:
            message = db.query(AgentMessage).filter(
                AgentMessage.execution_id == execution_id,
                AgentMessage.tool_name == tool_name
            ).order_by(AgentMessage.id.desc()).first()
            
            if message:
                # Make sure tool_output is stored as a string
                if isinstance(tool_result, (dict, list)):
                    message.tool_output = json.dumps(tool_result)
                else:
                    message.tool_output = str(tool_result)
                db.commit()
    except Exception as e:
        logger.error(f"Error recording tool result: {str(e)}")