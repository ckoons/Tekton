#!/usr/bin/env python3
"""
Tests for the enhanced tekton-llm-client features.

This module tests the new features:
1. Prompt templates
2. Response handlers
3. Configuration utilities
"""

import os
import sys
import json
import unittest
import tempfile
from unittest import mock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tekton_llm_client.prompt_templates import PromptTemplateRegistry, PromptTemplate, load_template
from tekton_llm_client.response_handlers import (
    JSONParser, parse_json, extract_json,
    StreamHandler, StructuredOutputParser, OutputFormat
)
from tekton_llm_client.config import (
    get_env, get_env_bool, get_env_int, get_env_float, set_env,
    LLMSettings, ClientSettings, load_settings, save_settings
)


class TestPromptTemplates(unittest.TestCase):
    """Tests for the prompt templates functionality."""
    
    def test_prompt_template(self):
        """Test basic prompt template functionality."""
        # Create a template
        template = PromptTemplate(
            name="test",
            template="Hello, {{ name }}!",
            description="Test template"
        )
        
        # Render the template
        rendered = template.render(name="World")
        self.assertEqual(rendered, "Hello, World!")
        
        # Test with additional variables
        rendered = template.render(name="User", extra="ignored")
        self.assertEqual(rendered, "Hello, User!")
    
    def test_registry(self):
        """Test template registry functionality."""
        # Create registry
        registry = PromptTemplateRegistry()
        
        # Check default templates
        self.assertIn("general_system", registry.templates)
        
        # Register a new template
        registry.register({
            "name": "custom",
            "template": "Custom template for {{ purpose }}",
            "description": "Custom template"
        })
        
        # Get and render template
        template = registry.get("custom")
        self.assertIsNotNone(template)
        self.assertEqual(template.name, "custom")
        
        # Render directly from registry
        rendered = registry.render("custom", purpose="testing")
        self.assertEqual(rendered, "Custom template for testing")
        
        # List templates
        templates = registry.list_templates()
        self.assertTrue(any(t["name"] == "custom" for t in templates))
        
        # Remove template
        self.assertTrue(registry.remove("custom"))
        self.assertIsNone(registry.get("custom"))
    
    def test_template_loading(self):
        """Test template loading from files."""
        # Create a temporary template file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write(json.dumps({
                "name": "temp_template",
                "template": "This is a {{ type }} template",
                "description": "Template for testing"
            }))
            template_path = f.name
        
        try:
            # Load the template
            template = load_template(template_path)
            self.assertEqual(template.name, "temp_template")
            self.assertEqual(template.render(type="test"), "This is a test template")
            
            # Test loading with a different name
            template2 = load_template(template_path, name="renamed")
            self.assertEqual(template2.name, "renamed")
            
        finally:
            # Clean up
            os.unlink(template_path)


class TestResponseHandlers(unittest.TestCase):
    """Tests for the response handlers functionality."""
    
    def test_json_parser(self):
        """Test JSON parser functionality."""
        # Test basic JSON parsing
        json_str = '{"name": "Test", "values": [1, 2, 3]}'
        result = parse_json(json_str)
        self.assertEqual(result["name"], "Test")
        self.assertEqual(result["values"], [1, 2, 3])
        
        # Test extracting JSON from text
        text = """This is a response with JSON:
        ```json
        {"result": "success", "count": 42}
        ```
        Hope that helps!"""
        
        json_str = extract_json(text)
        self.assertIn('"result": "success"', json_str)
        
        result = parse_json(text)
        self.assertEqual(result["result"], "success")
        self.assertEqual(result["count"], 42)
        
        # Test invalid JSON
        with self.assertRaises(Exception):
            parse_json("This is not JSON")
    
    def test_structured_output_parser(self):
        """Test structured output parser functionality."""
        # Test list parsing
        list_text = """Here are some items:
        1. First item
        2. Second item
        3. Third item
        """
        
        parser = StructuredOutputParser(format=OutputFormat.LIST)
        result = parser.parse(list_text)
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], "First item")
        self.assertEqual(result[1], "Second item")
        
        # Test key-value parsing
        kv_text = """
        Name: John Doe
        Age: 42
        Occupation: Software Engineer
        """
        
        parser = StructuredOutputParser(format=OutputFormat.KEY_VALUE)
        result = parser.parse(kv_text)
        
        self.assertEqual(result["Name"], "John Doe")
        self.assertEqual(result["Age"], "42")
        self.assertEqual(result["Occupation"], "Software Engineer")
        
        # Test markdown parsing
        md_text = """# Main Title
        
        This is some content.
        
        ## Section 1
        
        Section 1 content.
        
        ## Section 2
        
        Section 2 content.
        
        ```python
        def hello():
            print("Hello, world!")
        ```
        """
        
        parser = StructuredOutputParser(format=OutputFormat.MARKDOWN)
        result = parser.parse(md_text)
        
        self.assertIn("sections", result)
        self.assertIn("Main Title", result["sections"])
        self.assertIn("code_blocks", result)


class TestConfigUtils(unittest.TestCase):
    """Tests for the configuration utilities."""
    
    def setUp(self):
        """Set up the test environment."""
        # Clear any existing environment variables
        for key in list(os.environ.keys()):
            if key.startswith("TEKTON_LLM_"):
                del os.environ[key]
    
    def test_env_utils(self):
        """Test environment variable utilities."""
        # Test setting and getting
        set_env("TEST_VAR", "value")
        self.assertEqual(get_env("TEST_VAR"), "value")
        
        # Test boolean
        set_env("TEST_BOOL", "true")
        self.assertTrue(get_env_bool("TEST_BOOL"))
        
        set_env("TEST_BOOL", "false")
        self.assertFalse(get_env_bool("TEST_BOOL"))
        
        # Test integer
        set_env("TEST_INT", "42")
        self.assertEqual(get_env_int("TEST_INT"), 42)
        
        # Test float
        set_env("TEST_FLOAT", "3.14")
        self.assertEqual(get_env_float("TEST_FLOAT"), 3.14)
        
        # Test default values
        self.assertEqual(get_env("NONEXISTENT", default="default"), "default")
        self.assertEqual(get_env_int("NONEXISTENT", default=10), 10)
    
    def test_settings(self):
        """Test settings functionality."""
        # Create settings
        settings = ClientSettings(
            component_id="test-component",
            llm=LLMSettings(
                provider="test-provider",
                model="test-model"
            )
        )
        
        # Test properties
        self.assertEqual(settings.component_id, "test-component")
        self.assertEqual(settings.llm.provider, "test-provider")
        self.assertEqual(settings.llm.model, "test-model")
        
        # Test saving and loading
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            settings_path = f.name
        
        try:
            # Save settings
            save_settings(settings, settings_path)
            
            # Load settings
            loaded = load_settings("test-component", file_path=settings_path)
            
            # Verify loaded settings
            self.assertEqual(loaded.component_id, "test-component")
            self.assertEqual(loaded.llm.provider, "test-provider")
            self.assertEqual(loaded.llm.model, "test-model")
            
            # Test environment override
            set_env("PROVIDER", "env-provider")
            
            # Load with env variables
            loaded_with_env = load_settings("test-component", file_path=settings_path, load_from_env=True)
            
            # Verify env override
            self.assertEqual(loaded_with_env.llm.provider, "env-provider")
            self.assertEqual(loaded_with_env.llm.model, "test-model")  # Not overridden
            
        finally:
            # Clean up
            os.unlink(settings_path)


if __name__ == "__main__":
    unittest.main()