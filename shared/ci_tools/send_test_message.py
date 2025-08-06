#!/usr/bin/env python3
"""
Send a test message to a running wrapper
"""

import sys
import socket
import json

def send_message(ci_name, from_name, content):
    """Send a message to a CI wrapper"""
    socket_path = f"/tmp/ci_{ci_name}.sock"
    
    message = {
        'from': from_name,
        'content': content,
        'type': 'message'
    }
    
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(socket_path)
        sock.send(json.dumps(message).encode('utf-8'))
        sock.close()
        print(f"Sent to {ci_name}: {content}")
        return True
    except Exception as e:
        print(f"Failed to send: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: send_test_message.py <ci_name> <from> <message>")
        sys.exit(1)
    
    ci_name = sys.argv[1]
    from_name = sys.argv[2]
    message = ' '.join(sys.argv[3:])
    
    send_message(ci_name, from_name, message)