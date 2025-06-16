"""
Tests for the terminal session module
"""

import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import time
import uuid

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from terma.core.terminal import TerminalSession

class TestTerminalSession(unittest.TestCase):
    """Test the TerminalSession class"""
    
    @patch('ptyprocess.PtyProcess.spawn')
    def test_init(self, mock_spawn):
        """Test initializing a terminal session"""
        # Arrange
        session_id = str(uuid.uuid4())
        shell_command = "/bin/bash"
        
        # Act
        session = TerminalSession(session_id, shell_command)
        
        # Assert
        self.assertEqual(session.session_id, session_id)
        self.assertEqual(session.shell_command, shell_command)
        self.assertFalse(session.active)
        self.assertIsNone(session.pty)
        
    @patch('ptyprocess.PtyProcess.spawn')
    def test_start(self, mock_spawn):
        """Test starting a terminal session"""
        # Arrange
        session_id = str(uuid.uuid4())
        shell_command = "/bin/bash"
        mock_pty = MagicMock()
        mock_spawn.return_value = mock_pty
        
        # Act
        session = TerminalSession(session_id, shell_command)
        result = session.start()
        
        # Assert
        self.assertTrue(result)
        self.assertTrue(session.active)
        self.assertIsNotNone(session.pty)
        mock_spawn.assert_called_once_with([shell_command])
        
    @patch('ptyprocess.PtyProcess.spawn')
    def test_start_with_complex_command(self, mock_spawn):
        """Test starting a terminal session with a complex command"""
        # Arrange
        session_id = str(uuid.uuid4())
        shell_command = "/bin/bash -c 'echo hello'"
        mock_pty = MagicMock()
        mock_spawn.return_value = mock_pty
        
        # Act
        session = TerminalSession(session_id, shell_command)
        result = session.start()
        
        # Assert
        self.assertTrue(result)
        self.assertTrue(session.active)
        self.assertIsNotNone(session.pty)
        mock_spawn.assert_called_once_with(["/bin/bash", "-c", "echo hello"])
        
    @patch('ptyprocess.PtyProcess.spawn')
    def test_start_failure(self, mock_spawn):
        """Test starting a terminal session with failure"""
        # Arrange
        session_id = str(uuid.uuid4())
        shell_command = "/bin/bash"
        mock_spawn.side_effect = Exception("Failed to spawn")
        
        # Act
        session = TerminalSession(session_id, shell_command)
        result = session.start()
        
        # Assert
        self.assertFalse(result)
        self.assertFalse(session.active)
        self.assertIsNone(session.pty)
        
    @patch('ptyprocess.PtyProcess.spawn')
    def test_stop(self, mock_spawn):
        """Test stopping a terminal session"""
        # Arrange
        session_id = str(uuid.uuid4())
        shell_command = "/bin/bash"
        mock_pty = MagicMock()
        mock_pty.isalive.return_value = True
        mock_spawn.return_value = mock_pty
        
        # Act
        session = TerminalSession(session_id, shell_command)
        session.start()
        result = session.stop()
        
        # Assert
        self.assertTrue(result)
        self.assertFalse(session.active)
        mock_pty.terminate.assert_called_once_with(force=True)
        
    @patch('ptyprocess.PtyProcess.spawn')
    def test_write(self, mock_spawn):
        """Test writing to a terminal session"""
        # Arrange
        session_id = str(uuid.uuid4())
        shell_command = "/bin/bash"
        mock_pty = MagicMock()
        mock_spawn.return_value = mock_pty
        
        # Act
        session = TerminalSession(session_id, shell_command)
        session.start()
        result = session.write("echo hello\\n")
        
        # Assert
        self.assertTrue(result)
        mock_pty.write.assert_called_once_with("echo hello\\n")
        
    @patch('ptyprocess.PtyProcess.spawn')
    def test_read(self, mock_spawn):
        """Test reading from a terminal session"""
        # Arrange
        session_id = str(uuid.uuid4())
        shell_command = "/bin/bash"
        mock_pty = MagicMock()
        mock_pty.read.return_value = "hello\\n"
        mock_spawn.return_value = mock_pty
        
        # Act
        session = TerminalSession(session_id, shell_command)
        session.start()
        result = session.read()
        
        # Assert
        self.assertEqual(result, "hello\\n")
        mock_pty.read.assert_called_once_with(1024)
        
    @patch('ptyprocess.PtyProcess.spawn')
    def test_resize(self, mock_spawn):
        """Test resizing a terminal session"""
        # Arrange
        session_id = str(uuid.uuid4())
        shell_command = "/bin/bash"
        mock_pty = MagicMock()
        mock_spawn.return_value = mock_pty
        
        # Act
        session = TerminalSession(session_id, shell_command)
        session.start()
        result = session.resize(24, 80)
        
        # Assert
        self.assertTrue(result)
        mock_pty.setwinsize.assert_called_once_with(24, 80)
        
    @patch('ptyprocess.PtyProcess.spawn')
    def test_get_info(self, mock_spawn):
        """Test getting session information"""
        # Arrange
        session_id = str(uuid.uuid4())
        shell_command = "/bin/bash"
        mock_pty = MagicMock()
        mock_spawn.return_value = mock_pty
        
        # Act
        session = TerminalSession(session_id, shell_command)
        session.start()
        info = session.get_info()
        
        # Assert
        self.assertEqual(info["id"], session_id)
        self.assertTrue(info["active"])
        self.assertEqual(info["shell_command"], shell_command)
        
if __name__ == '__main__':
    unittest.main()