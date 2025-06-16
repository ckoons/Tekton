"""
Streaming response handling for agent runner.
"""

import logging
import asyncio
from typing import Dict, Any, List, AsyncGenerator, Optional

from ergon.core.database.engine import get_db_session
from ergon.core.database.models import AgentMessage

# Configure logger
logger = logging.getLogger(__name__)

async def stream_response(
    llm_client: Any,
    messages: List[Dict[str, str]],
    execution_id: Optional[int] = None
) -> AsyncGenerator[str, None]:
    """
    Stream a response from the LLM.
    
    Args:
        llm_client: LLM client
        messages: Messages to send to the LLM
        execution_id: Optional execution ID for database recording
        
    Yields:
        Chunks of the response
    """
    try:
        # Record in database if execution_id provided
        if execution_id:
            full_response = ""
            async for chunk in llm_client.acomplete_stream(messages):
                full_response += chunk
                yield chunk
            
            # Record the complete response
            try:
                with get_db_session() as db:
                    message = AgentMessage(
                        execution_id=execution_id,
                        role="assistant",
                        content=full_response
                    )
                    db.add(message)
                    db.commit()
            except Exception as e:
                logger.error(f"Error recording streamed response: {str(e)}")
        else:
            # Just stream the response without recording
            async for chunk in llm_client.acomplete_stream(messages):
                yield chunk
    except Exception as e:
        logger.error(f"Error streaming response: {str(e)}")
        yield f"Error streaming response: {str(e)}"