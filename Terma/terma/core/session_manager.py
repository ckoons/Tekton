"""Terminal session management system"""

import asyncio
import time
import uuid
import logging
import os
import signal
from typing import Dict, List, Optional, Any, Set, Callable
from concurrent.futures import ThreadPoolExecutor

from .terminal import TerminalSession
from ..utils.logging import setup_logging

logger = setup_logging()

class SessionManager:
    """Manages multiple terminal sessions"""
    
    def __init__(self, cleanup_interval: int = 3600, idle_timeout: int = 86400):
        """Initialize the session manager
        
        Args:
            cleanup_interval: Interval in seconds to check for idle sessions
            idle_timeout: Time in seconds after which an idle session is closed
        """
        self.sessions: Dict[str, TerminalSession] = {}
        self.locks: Dict[str, asyncio.Lock] = {}
        self.cleanup_interval = cleanup_interval
        self.idle_timeout = idle_timeout
        self._executor = ThreadPoolExecutor(max_workers=10)
        self._cleanup_task = None
        self._running = False
        
    def start(self):
        """Start the session manager"""
        if not self._running:
            self._running = True
            self._start_cleanup_task()
            logger.info("Session manager started")
    
    def stop(self):
        """Stop the session manager and close all sessions"""
        if self._running:
            self._running = False
            
            # Cancel cleanup task if running
            if self._cleanup_task and not self._cleanup_task.done():
                self._cleanup_task.cancel()
            
            # Close all sessions
            for session_id in list(self.sessions.keys()):
                self.close_session(session_id)
            
            # Shutdown the executor
            self._executor.shutdown(wait=False)
            
            logger.info("Session manager stopped")
    
    def _start_cleanup_task(self):
        """Start the cleanup task"""
        if asyncio.get_event_loop().is_running():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        else:
            logger.warning("Event loop not running, cleanup task not started")
    
    async def _cleanup_loop(self):
        """Periodically check for and close idle sessions"""
        try:
            while self._running:
                await self._cleanup_idle_sessions()
                await asyncio.sleep(self.cleanup_interval)
        except asyncio.CancelledError:
            logger.info("Cleanup task cancelled")
        except Exception as e:
            logger.error(f"Cleanup task error: {e}")
    
    async def _cleanup_idle_sessions(self):
        """Close idle sessions"""
        now = time.time()
        closed_count = 0
        
        for session_id, session in list(self.sessions.items()):
            # Check if the session is idle
            if now - session.last_activity > self.idle_timeout:
                logger.info(f"Closing idle session {session_id} (idle for {now - session.last_activity:.1f}s)")
                if self.close_session(session_id):
                    closed_count += 1
        
        if closed_count > 0:
            logger.info(f"Closed {closed_count} idle sessions")
    
    async def create_session_async(self, session_id: Optional[str] = None, 
                                  shell_command: Optional[str] = None) -> Optional[str]:
        """Create a new terminal session asynchronously
        
        Args:
            session_id: Optional identifier for the session
            shell_command: Shell command to run (defaults to user's default shell)
            
        Returns:
            str: The ID of the created session, or None if creation failed
        """
        # Generate a session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
            
        # Check if the session already exists
        if session_id in self.sessions:
            logger.warning(f"Session {session_id} already exists")
            return session_id
            
        # Create a lock for this session
        self.locks[session_id] = asyncio.Lock()
        
        # Create and start the session
        async with self.locks[session_id]:
            # Create the session
            session = TerminalSession(session_id, shell_command)
            
            # Start the session in a separate thread to avoid blocking
            success = await asyncio.get_event_loop().run_in_executor(
                self._executor,
                session.start
            )
            
            if success:
                # Store the session
                self.sessions[session_id] = session
                logger.info(f"Created session {session_id}")
                return session_id
            else:
                # Failed to start the session
                logger.error(f"Failed to create session {session_id}")
                if session_id in self.locks:
                    del self.locks[session_id]
                return None
        
    def create_session(self, session_id: Optional[str] = None, 
                      shell_command: Optional[str] = None) -> Optional[str]:
        """Create a new terminal session
        
        Args:
            session_id: Optional identifier for the session
            shell_command: Shell command to run (defaults to user's default shell)
            
        Returns:
            str: The ID of the created session, or None if creation failed
        """
        # Generate a session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
            
        # Check if the session already exists
        if session_id in self.sessions:
            logger.warning(f"Session {session_id} already exists")
            return session_id
            
        # Create the session
        session = TerminalSession(session_id, shell_command)
        
        # Start the session
        if session.start():
            # Store the session
            self.sessions[session_id] = session
            self.locks[session_id] = asyncio.Lock()
            logger.info(f"Created session {session_id}")
            return session_id
        else:
            # Failed to start the session
            logger.error(f"Failed to create session {session_id}")
            return None
        
    def get_session(self, session_id: str) -> Optional[TerminalSession]:
        """Get a terminal session by ID
        
        Args:
            session_id: The ID of the session to retrieve
            
        Returns:
            The terminal session object, or None if not found
        """
        return self.sessions.get(session_id)
        
    def close_session(self, session_id: str) -> bool:
        """Close a terminal session
        
        Args:
            session_id: The ID of the session to close
            
        Returns:
            bool: True if successful, False otherwise
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found")
            return False
            
        # Stop the session
        success = session.stop()
        
        # Remove from sessions dict
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        # Remove lock
        if session_id in self.locks:
            del self.locks[session_id]
            
        if success:
            logger.info(f"Closed session {session_id}")
        else:
            logger.error(f"Failed to close session {session_id}")
            
        return success
        
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active terminal sessions
        
        Returns:
            A list of session information dictionaries
        """
        return [session.get_info() for session in self.sessions.values()]
    
    def write_to_session(self, session_id: str, data: str) -> bool:
        """Write data to a terminal session
        
        Args:
            session_id: The ID of the session to write to
            data: The data to write
            
        Returns:
            bool: True if successful, False otherwise
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found")
            return False
            
        return session.write(data)
    
    def read_from_session(self, session_id: str, size: int = 1024) -> Optional[str]:
        """Read data from a terminal session
        
        Args:
            session_id: The ID of the session to read from
            size: Maximum number of bytes to read
            
        Returns:
            str: The data read, or None if an error occurred
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found")
            return None
            
        return session.read(size)
    
    def resize_session(self, session_id: str, rows: int, cols: int) -> bool:
        """Resize a terminal session
        
        Args:
            session_id: The ID of the session to resize
            rows: Number of rows
            cols: Number of columns
            
        Returns:
            bool: True if successful, False otherwise
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found")
            return False
            
        return session.resize(rows, cols)
    
    def register_output_callback(self, session_id: str, callback: Callable[[str], None]) -> bool:
        """Register a callback for terminal output
        
        Args:
            session_id: The ID of the session
            callback: Function to call with the output string
            
        Returns:
            bool: True if successful, False otherwise
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found")
            return False
            
        session.register_output_callback(callback)
        return True
    
    def unregister_output_callback(self, session_id: str, callback: Callable[[str], None]) -> bool:
        """Unregister a terminal output callback
        
        Args:
            session_id: The ID of the session
            callback: Function to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found")
            return False
            
        session.unregister_output_callback(callback)
        return True