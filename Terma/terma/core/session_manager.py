"""Stub SessionManager for backwards compatibility with HermesIntegration"""

class SessionManager:
    """Stub class - native terminals are managed differently now"""
    
    def __init__(self):
        pass
    
    def create_session(self, *args, **kwargs):
        """Stub method"""
        return {"session_id": "stub", "status": "Native terminals don't use sessions"}
    
    def get_session(self, session_id):
        """Stub method"""
        return None
    
    def list_sessions(self):
        """Stub method"""
        return []
    
    def remove_session(self, session_id):
        """Stub method"""
        pass