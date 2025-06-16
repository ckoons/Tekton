"""
Tests for shared error classes.
"""
import pytest
from shared.utils.errors import (
    TektonError,
    StartupError,
    ShutdownError,
    ConfigurationError,
    RegistrationError,
    DependencyError,
    ComponentError
)


def test_base_error():
    """Test base TektonError."""
    error = TektonError("Test error", "test_component", "TEST001")
    assert str(error) == "[test_component] Test error"
    assert error.component == "test_component"
    assert error.error_code == "TEST001"
    assert error.details is None


def test_base_error_with_details():
    """Test base error with additional details."""
    details = {"port": 8000, "reason": "bind failed"}
    error = TektonError("Port error", "test_component", "PORT001", details)
    assert error.details == details
    assert error.component == "test_component"


def test_startup_error():
    """Test StartupError."""
    error = StartupError("Failed to initialize", "athena")
    assert str(error) == "[athena] Failed to initialize"
    assert error.component == "athena"
    assert isinstance(error, TektonError)


def test_shutdown_error():
    """Test ShutdownError."""
    error = ShutdownError("Cleanup failed", "budget", "SHUTDOWN001")
    assert str(error) == "[budget] Cleanup failed"
    assert error.error_code == "SHUTDOWN001"


def test_configuration_error():
    """Test ConfigurationError."""
    error = ConfigurationError("Invalid port", "hermes", details={"port": -1})
    assert error.component == "hermes"
    assert error.details["port"] == -1


def test_registration_error():
    """Test RegistrationError."""
    error = RegistrationError("Hermes unavailable", "sophia")
    assert "sophia" in str(error)
    assert "Hermes unavailable" in str(error)


def test_dependency_error():
    """Test DependencyError."""
    deps = ["hermes", "engram"]
    error = DependencyError("Required services not available", "metis", dependencies=deps)
    assert error.dependencies == deps
    assert error.component == "metis"


def test_component_error():
    """Test generic ComponentError."""
    error = ComponentError("Internal error", "telos", "INTERNAL001")
    assert error.error_code == "INTERNAL001"


def test_error_inheritance():
    """Test that all errors inherit from base TektonError."""
    errors = [
        StartupError("test", "comp"),
        ShutdownError("test", "comp"),
        ConfigurationError("test", "comp"),
        RegistrationError("test", "comp"),
        DependencyError("test", "comp"),
        ComponentError("test", "comp")
    ]
    
    for error in errors:
        assert isinstance(error, TektonError)
        assert isinstance(error, Exception)


def test_error_serialization():
    """Test error can be serialized for logging/API responses."""
    error = StartupError("Port in use", "ergon", "PORT_IN_USE", {"port": 8002})
    
    error_dict = error.to_dict()
    assert error_dict["component"] == "ergon"
    assert error_dict["message"] == "Port in use"
    assert error_dict["error_code"] == "PORT_IN_USE"
    assert error_dict["details"]["port"] == 8002
    assert error_dict["error_type"] == "StartupError"


def test_error_comparison():
    """Test error comparison for deduplication."""
    error1 = ConfigurationError("Bad config", "apollo", "CONFIG001")
    error2 = ConfigurationError("Bad config", "apollo", "CONFIG001")
    error3 = ConfigurationError("Bad config", "apollo", "CONFIG002")
    
    assert error1.is_same_error(error2)
    assert not error1.is_same_error(error3)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])