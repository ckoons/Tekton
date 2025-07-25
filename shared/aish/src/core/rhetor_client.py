"""
Simple Rhetor client for sending messages to Greek Chorus AIs.
Replaces the old MessageHandler and shell.send_to_ai methods.
"""

import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any


def send_to_rhetor(ai_name: str, message: str, rhetor_endpoint: str = None) -> Optional[str]:
    """
    Send a message to a Greek Chorus AI via Rhetor.
    
    Args:
        ai_name: Name of the AI (e.g., 'numa', 'apollo')
        message: Message to send
        rhetor_endpoint: Optional Rhetor endpoint override
        
    Returns:
        str: Response from the AI, or None if failed
    """
    if not rhetor_endpoint:
        # Get default Rhetor endpoint
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
        from shared.urls import tekton_url
        rhetor_endpoint = tekton_url('rhetor', '')
    
    # Build the request
    url = f"{rhetor_endpoint}/rhetor/socket"
    data = {
        "ai_name": ai_name,
        "message": message
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read())
            
        # Extract response
        if isinstance(result, dict):
            # Handle different response formats
            if 'response' in result:
                return result['response']
            elif 'message' in result:
                return result['message']
            elif 'content' in result:
                return result['content']
            else:
                # Return the whole dict as JSON if we don't recognize the format
                return json.dumps(result, indent=2)
        elif isinstance(result, str):
            return result
        else:
            return str(result)
            
    except urllib.error.HTTPError as e:
        error_msg = f"HTTP {e.code}"
        try:
            error_data = json.loads(e.read())
            if 'detail' in error_data:
                error_msg += f": {error_data['detail']}"
        except:
            pass
        print(f"Error calling Rhetor for {ai_name}: {error_msg}")
        return None
    except Exception as e:
        print(f"Error sending to {ai_name}: {e}")
        return None


def broadcast_to_rhetor(message: str, rhetor_endpoint: str = None) -> Dict[str, str]:
    """
    Broadcast a message to all Greek Chorus AIs via Rhetor.
    
    Args:
        message: Message to broadcast
        rhetor_endpoint: Optional Rhetor endpoint override
        
    Returns:
        Dict[str, str]: Responses from each AI
    """
    if not rhetor_endpoint:
        # Get default Rhetor endpoint
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
        from shared.urls import tekton_url
        rhetor_endpoint = tekton_url('rhetor', '')
    
    # Build the request for team-chat
    url = f"{rhetor_endpoint}/rhetor/team-chat"
    data = {"message": message}
    
    responses = {}
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read())
            
        # Extract responses from each AI
        if isinstance(result, dict):
            if 'responses' in result:
                # New format: {"responses": [{"specialist_id": "numa", "content": "..."}]}
                for resp in result['responses']:
                    ai_name = resp.get('specialist_id', 'unknown')
                    content = resp.get('content', '')
                    responses[ai_name] = content
            else:
                # Old format or direct responses
                responses = result
        elif isinstance(result, list):
            # List of responses
            for i, resp in enumerate(result):
                if isinstance(resp, dict) and 'specialist_id' in resp:
                    responses[resp['specialist_id']] = resp.get('content', '')
                else:
                    responses[f'ai_{i}'] = str(resp)
        
        return responses
            
    except Exception as e:
        print(f"Error broadcasting to team: {e}")
        return responses