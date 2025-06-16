"""
Tests for the Tekton configuration utility.
"""

import os
import json
import tempfile
import unittest
from unittest import mock

from tekton.utils.tekton_config import (
    Config,
    ConfigSource,
    get_component_config,
    get_component_port_config
)


class TestConfig(unittest.TestCase):
    """Test Config class."""

    def setUp(self):
        """Set up tests."""
        # Create test config with defaults
        self.config = Config(
            defaults={
                "app": {
                    "name": "test-app",
                    "port": 8000,
                    "log_level": "INFO"
                },
                "database": {
                    "url": "postgresql://localhost:5432/test",
                    "pool_size": 10
                }
            }
        )

    def test_get_simple_values(self):
        """Test getting simple values."""
        self.assertEqual(self.config.get("app.name"), "test-app")
        self.assertEqual(self.config.get("app.port"), 8000)
        self.assertEqual(self.config.get("app.log_level"), "INFO")
        self.assertEqual(self.config.get("database.url"), "postgresql://localhost:5432/test")
        self.assertEqual(self.config.get("database.pool_size"), 10)

    def test_get_with_default(self):
        """Test getting value with default."""
        self.assertEqual(self.config.get("app.debug", False), False)
        self.assertEqual(self.config.get("app.timeout", 30), 30)

    def test_get_with_type(self):
        """Test getting value with type conversion."""
        self.assertEqual(self.config.get("app.port", type=int), 8000)
        self.assertEqual(self.config.get("app.port", type=str), "8000")
        self.assertEqual(self.config.get("app.log_level", type=str), "INFO")
        self.assertEqual(self.config.get("database.pool_size", type=int), 10)

    def test_get_nested_dict(self):
        """Test getting nested dict."""
        app_config = self.config.get("app")
        self.assertEqual(app_config, {
            "name": "test-app",
            "port": 8000,
            "log_level": "INFO"
        })

    def test_set_value(self):
        """Test setting value."""
        self.config.set("app.port", 8001)
        self.assertEqual(self.config.get("app.port"), 8001)

        self.config.set("app.debug", True)
        self.assertEqual(self.config.get("app.debug"), True)

        self.config.set("new.key", "value")
        self.assertEqual(self.config.get("new.key"), "value")

    def test_set_nested_dict(self):
        """Test setting nested dict."""
        self.config.set("app", {
            "name": "new-app",
            "port": 8002,
            "log_level": "DEBUG"
        })
        
        self.assertEqual(self.config.get("app.name"), "new-app")
        self.assertEqual(self.config.get("app.port"), 8002)
        self.assertEqual(self.config.get("app.log_level"), "DEBUG")

    def test_get_enum(self):
        """Test getting enum value."""
        # Valid enum value
        self.assertEqual(
            self.config.get_enum("app.log_level", ["DEBUG", "INFO", "WARNING", "ERROR"]),
            "INFO"
        )
        
        # Invalid enum value
        with self.assertRaises(ValueError):
            self.config.set("app.log_level", "INVALID")
            self.config.get_enum("app.log_level", ["DEBUG", "INFO", "WARNING", "ERROR"])

    def test_load_from_dict(self):
        """Test loading from dict."""
        self.config.load_from_dict({
            "app": {
                "name": "dict-app",
                "port": 8003
            }
        })
        
        self.assertEqual(self.config.get("app.name"), "dict-app")
        self.assertEqual(self.config.get("app.port"), 8003)
        self.assertEqual(self.config.get("app.log_level"), "INFO")  # Unchanged

    def test_load_from_env(self):
        """Test loading from environment variables."""
        with mock.patch.dict(os.environ, {
            "TEST_APP_NAME": "env-app",
            "TEST_APP_PORT": "8004",
            "TEST_DATABASE_URL": "postgresql://localhost:5432/env"
        }):
            self.config.load_from_env(prefix="TEST")
        
        self.assertEqual(self.config.get("app.name"), "env-app")
        self.assertEqual(self.config.get("app.port"), 8004)
        self.assertEqual(self.config.get("database.url"), "postgresql://localhost:5432/env")
        self.assertEqual(self.config.get("app.log_level"), "INFO")  # Unchanged

    def test_load_from_file_json(self):
        """Test loading from JSON file."""
        config_data = {
            "app": {
                "name": "json-app",
                "port": 8005
            }
        }
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as temp:
            json.dump(config_data, temp)
            temp.flush()
            
            self.config.load_from_file(temp.name)
        
        self.assertEqual(self.config.get("app.name"), "json-app")
        self.assertEqual(self.config.get("app.port"), 8005)
        self.assertEqual(self.config.get("app.log_level"), "INFO")  # Unchanged

    def test_to_dict(self):
        """Test converting config to dict."""
        config_dict = self.config.to_dict()
        
        self.assertEqual(config_dict, {
            "app": {
                "name": "test-app",
                "port": 8000,
                "log_level": "INFO"
            },
            "database": {
                "url": "postgresql://localhost:5432/test",
                "pool_size": 10
            }
        })

    def test_merge_configs(self):
        """Test merging configs."""
        config1 = Config(defaults={"a": 1, "b": {"c": 2}})
        config2 = Config(defaults={"b": {"d": 3}, "e": 4})
        
        merged = Config.merge(config1, config2)
        
        self.assertEqual(merged.get("a"), 1)
        self.assertEqual(merged.get("b.c"), 2)
        self.assertEqual(merged.get("b.d"), 3)
        self.assertEqual(merged.get("e"), 4)


class TestComponentConfig(unittest.TestCase):
    """Test component config functions."""
    
    def test_get_component_config(self):
        """Test getting component config."""
        with mock.patch.dict(os.environ, {
            "TEST_PORT": "8001",
            "TEST_HOST": "example.com"
        }):
            config = get_component_config("test")
        
        self.assertEqual(config.get("port"), 8001)
        self.assertEqual(config.get("host"), "example.com")
    
    def test_get_component_port_config(self):
        """Test getting component port config."""
        with mock.patch.dict(os.environ, {
            "TEST_PORT": "8001"
        }):
            port = get_component_port_config("test")
        
        self.assertEqual(port, 8001)
        
        # Test with default port
        with mock.patch.dict(os.environ, {}):
            port = get_component_port_config("test", default=9000)
        
        self.assertEqual(port, 9000)


if __name__ == "__main__":
    unittest.main()