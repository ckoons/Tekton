"""
Tests for environment configuration loader.
"""
import pytest
import os
from unittest.mock import patch, MagicMock

from shared.utils.env_config import (
    ComponentConfig,
    TektonConfig,
    HermesConfig,
    EngramConfig,
    RhetorConfig,
    AthenaConfig,
    ApolloConfig,
    BudgetConfig,
    get_component_config,
    get_tekton_config
)


def test_hermes_config_defaults():
    """Test HermesConfig with default values."""
    config = HermesConfig()
    assert config.port == 8001
    assert config.discovery_enabled == True
    assert config.registration_timeout == 30
    assert config.health_check_interval == 60


def test_hermes_config_with_env():
    """Test HermesConfig loads from environment."""
    with patch.dict(os.environ, {
        'HERMES_PORT': '9001',
        'TEKTON_HERMES_DISCOVERY': 'false',
        'HERMES_REGISTRATION_TIMEOUT': '45'
    }):
        config = HermesConfig.from_env()
        assert config.port == 9001
        assert config.discovery_enabled == False
        assert config.registration_timeout == 45


def test_engram_config():
    """Test EngramConfig with memory settings."""
    with patch.dict(os.environ, {
        'ENGRAM_PORT': '8000',
        'ENGRAM_MEMORY_LIMIT': '1000',
        'ENGRAM_CACHE_ENABLED': 'true'
    }):
        config = EngramConfig.from_env()
        assert config.port == 8000
        assert config.memory_limit == 1000
        assert config.cache_enabled == True


def test_rhetor_config():
    """Test RhetorConfig with LLM settings."""
    with patch.dict(os.environ, {
        'RHETOR_PORT': '8003',
        'TEKTON_DEFAULT_PROVIDER': 'openai',
        'RHETOR_TIMEOUT': '120'
    }):
        config = RhetorConfig.from_env()
        assert config.port == 8003
        assert config.default_model == 'gpt-4'
        assert config.default_provider == 'openai'
        assert config.request_timeout == 120


def test_apollo_config():
    """Test ApolloConfig with prediction settings."""
    with patch.dict(os.environ, {
        'APOLLO_PORT': '8012',
        'TEKTON_APOLLO_PREDICTIONS': 'false',
        'APOLLO_CONFIDENCE_THRESHOLD': '0.85'
    }):
        config = ApolloConfig.from_env()
        assert config.port == 8012
        assert config.predictions_enabled == False
        assert config.confidence_threshold == 0.85


def test_budget_config():
    """Test BudgetConfig with cost tracking settings."""
    with patch.dict(os.environ, {
        'BUDGET_PORT': '8013',
        'TEKTON_BUDGET_TRACKING': 'true',
        'BUDGET_WARNING_THRESHOLD': '100.50',
        'BUDGET_LIMIT': '500'
    }):
        config = BudgetConfig.from_env()
        assert config.port == 8013
        assert config.tracking_enabled == True
        assert config.warning_threshold == 100.50
        assert config.limit == 500.0


def test_tekton_config_global_settings():
    """Test TektonConfig with global settings."""
    with patch.dict(os.environ, {
        'TEKTON_DEBUG': 'true',
        'TEKTON_LOG_LEVEL': 'DEBUG',
        'TEKTON_AUTO_LAUNCH': 'false',
        'TEKTON_COMPONENT_TIMEOUT': '45',
        'SHOW_GREEK_NAMES': 'true',
        'TEKTON_THEME_MODE': 'dark'
    }):
        config = TektonConfig.from_env()
        assert config.debug == True
        assert config.log_level == 'DEBUG'
        assert config.auto_launch == False
        assert config.component_timeout == 45
        assert config.show_greek_names == True
        assert config.theme_mode == 'dark'


def test_component_config_loads_all():
    """Test ComponentConfig loads all component configs."""
    with patch('shared.utils.env_config.get_env_manager') as mock_env_manager:
        mock_manager = MagicMock()
        mock_env_manager.return_value = mock_manager
        
        config = ComponentConfig()
        
        # Verify env manager was used
        mock_manager.load_environment.assert_called_once()
        
        # Check all component configs exist
        assert hasattr(config, 'hermes')
        assert hasattr(config, 'engram')
        assert hasattr(config, 'rhetor')
        assert hasattr(config, 'athena')
        assert hasattr(config, 'apollo')
        assert hasattr(config, 'budget')
        assert hasattr(config, 'tekton')
        
        # Verify they are the right types
        assert isinstance(config.hermes, HermesConfig)
        assert isinstance(config.engram, EngramConfig)
        assert isinstance(config.tekton, TektonConfig)


def test_component_config_with_env_overrides():
    """Test ComponentConfig with environment overrides."""
    with patch.dict(os.environ, {
        'HERMES_PORT': '9999',
        'ENGRAM_PORT': '9998',
        'RHETOR_PORT': '9997'
    }):
        with patch('shared.utils.env_config.get_env_manager') as mock_env_manager:
            mock_manager = MagicMock()
            mock_manager.load_environment = MagicMock()
            mock_env_manager.return_value = mock_manager
            
            config = ComponentConfig()
            
            assert config.hermes.port == 9999
            assert config.engram.port == 9998
            assert config.rhetor.port == 9997


def test_get_component_config_singleton():
    """Test get_component_config returns singleton."""
    config1 = get_component_config()
    config2 = get_component_config()
    
    assert config1 is config2  # Same instance


def test_get_component_port():
    """Test getting port for specific component."""
    with patch.dict(os.environ, {'ATHENA_PORT': '8005'}):
        config = ComponentConfig()
        assert config.get_port('athena') == 8005
        assert config.get_port('ATHENA') == 8005  # Case insensitive
        assert config.get_port('unknown') is None


def test_validation_errors():
    """Test Pydantic validation for invalid values."""
    with patch.dict(os.environ, {
        'HERMES_PORT': 'not-a-number',
        'APOLLO_CONFIDENCE_THRESHOLD': 'invalid'
    }):
        # Should use defaults for invalid values
        config = HermesConfig.from_env()
        assert config.port == 8001  # Falls back to default
        
        config = ApolloConfig.from_env()
        assert config.confidence_threshold == 0.75  # Falls back to default


def test_config_to_dict():
    """Test converting config to dictionary."""
    config = HermesConfig(port=9001, discovery_enabled=False)
    config_dict = config.model_dump()
    
    assert config_dict['port'] == 9001
    assert config_dict['discovery_enabled'] == False
    assert 'registration_timeout' in config_dict


def test_component_config_refresh():
    """Test refreshing configuration from environment."""
    with patch('shared.utils.env_config.get_env_manager') as mock_env_manager:
        mock_manager = MagicMock()
        mock_manager.load_environment = MagicMock()
        mock_env_manager.return_value = mock_manager
        
        with patch.dict(os.environ, {'HERMES_PORT': '8001'}):
            config = ComponentConfig()
            assert config.hermes.port == 8001
        
        # Change environment
        with patch.dict(os.environ, {'HERMES_PORT': '9001'}):
            config.refresh()
            assert config.hermes.port == 9001


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
