"""
Test for Tekton Environment Management
"""
import os
import sys
import tempfile
import pytest
from pathlib import Path

# Add Tekton root to path
tekton_root = os.environ.get('TEKTON_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, tekton_root)

from shared.env import TektonEnvironLock, TektonEnviron, TektonEnvironUpdate, _frozen_env, _is_loaded


class TestTektonEnviron:
    """Test TektonEnviron functionality"""
    
    def setup_method(self):
        """Reset state before each test"""
        # Reset module-level state
        global _frozen_env, _is_loaded
        _frozen_env.clear()
        _is_loaded = False
        
        # Save original environment
        self.original_env = dict(os.environ)
        
    def teardown_method(self):
        """Restore original environment after each test"""
        os.environ.clear()
        os.environ.update(self.original_env)
        
    def test_is_loaded_before_load(self):
        """Test is_loaded returns False before TektonEnvironLock.load()"""
        assert TektonEnviron.is_loaded() is False
        
    def test_is_loaded_after_load(self):
        """Test is_loaded returns True after TektonEnvironLock.load()"""
        # Create temp env files
        with tempfile.TemporaryDirectory() as tmpdir:
            # Set TEKTON_ROOT to temp dir
            os.environ['TEKTON_ROOT'] = tmpdir
            
            # Create a .env.tekton file
            env_file = Path(tmpdir) / '.env.tekton'
            env_file.write_text('TEST_VAR=test_value\n')
            
            # Load environment
            TektonEnvironLock.load()
            
            # Check is_loaded
            assert TektonEnviron.is_loaded() is True
            
    def test_get_before_load(self):
        """Test TektonEnviron.get returns from os.environ before load"""
        os.environ['TEST_KEY'] = 'test_value'
        assert TektonEnviron.get('TEST_KEY') == 'test_value'
        
    def test_get_after_load(self):
        """Test TektonEnviron.get returns from frozen env after load"""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ['TEKTON_ROOT'] = tmpdir
            os.environ['ORIGINAL_KEY'] = 'original_value'
            
            # Create env file with override
            env_file = Path(tmpdir) / '.env.tekton'
            env_file.write_text('ORIGINAL_KEY=overridden_value\n')
            
            # Load environment
            TektonEnvironLock.load()
            
            # Change os.environ after load
            os.environ['ORIGINAL_KEY'] = 'changed_after_load'
            
            # Should still get the frozen value
            assert TektonEnviron.get('ORIGINAL_KEY') == 'overridden_value'
            
    def test_all_returns_copy(self):
        """Test TektonEnviron.all() returns a copy, not the original"""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ['TEKTON_ROOT'] = tmpdir
            TektonEnvironLock.load()
            
            env1 = TektonEnviron.all()
            env2 = TektonEnviron.all()
            
            # Should be equal but not the same object
            assert env1 == env2
            assert env1 is not env2
            
            # Modifying the copy shouldn't affect the frozen env
            env1['NEW_KEY'] = 'new_value'
            assert 'NEW_KEY' not in TektonEnviron.all()
            
    def test_set_is_noop(self):
        """Test TektonEnviron.set doesn't actually set anything"""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ['TEKTON_ROOT'] = tmpdir
            TektonEnvironLock.load()
            
            # Try to set a value
            TektonEnviron.set('NEW_KEY', 'new_value')
            
            # Should not be in frozen env
            assert TektonEnviron.get('NEW_KEY') is None
            assert 'NEW_KEY' not in TektonEnviron.all()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])