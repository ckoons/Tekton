"""Unified configuration system for Ergon."""

from typing import Optional, Dict, Any, List
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from enum import Enum


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file
    """
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"
    
    # GitHub API settings
    github_api_token: Optional[str] = None
    github_username: Optional[str] = None
    
    # Mail provider settings
    outlook_client_id: Optional[str] = None
    
    # Browser settings
    browser_headless: bool = True
    
    # Model settings
    default_model: str = "gpt-4o-mini"
    use_local_models: bool = False
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Tekton shared settings
    tekton_home: Path = Field(default_factory=lambda: Path(
        os.environ.get('TEKTON_DATA_DIR', 
                      os.path.join(os.environ.get('TEKTON_ROOT', Path.home()), '.tekton', 'data'))
    ))
    
    # Database settings
    database_url: str = Field(default_factory=lambda: f"sqlite:///{Path(__file__).parent.parent.parent.parent.absolute()}/ergon.db")
    vector_db_path: str = Field(default_factory=lambda: str(Path(
        os.environ.get('TEKTON_DATA_DIR', 
                      os.path.join(os.environ.get('TEKTON_ROOT', Path.home()), '.tekton', 'data'))
    ) / "vector_store"))
    data_dir: str = Field(default_factory=lambda: str(Path(
        os.environ.get('TEKTON_DATA_DIR', 
                      os.path.join(os.environ.get('TEKTON_ROOT', Path.home()), '.tekton', 'data'))
    )))
    
    # Authentication settings
    require_authentication: bool = True  # Default to requiring authentication
    
    # Application settings
    log_level: LogLevel = LogLevel.INFO
    debug: bool = False
    
    # Internal settings
    app_root: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent.absolute())
    
    # Config path for persistent settings
    config_path: Path = Field(default_factory=lambda: Path.home() / ".ergon")
    
    # Config for environment variables
    model_config = SettingsConfigDict(
        # Priority order: .env.owner, .env.local, .env
        env_file=[".env.owner", ".env.local", ".env"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @field_validator('database_url')
    def validate_db_url(cls, v):
        """Make database URL absolute if it's a SQLite database"""
        if v.startswith('sqlite:///') and not v.startswith('sqlite:////'):
            # It's a relative path SQLite database
            return f"sqlite:////{os.path.abspath(v.replace('sqlite:///', ''))}" 
        return v
    
    @field_validator('vector_db_path', 'data_dir')
    def validate_paths(cls, v):
        """Make paths absolute if they're relative"""
        if not os.path.isabs(v):
            return os.path.abspath(v)
        return v
        
    @field_validator('config_path', 'tekton_home')
    def validate_config_paths(cls, v):
        """Ensure config paths exist"""
        if not os.path.exists(v):
            os.makedirs(v, exist_ok=True)
        return v
    
    def __init__(self, **data):
        super().__init__(**data)
        # Set environment variable for Tekton vector store path
        os.environ["TEKTON_VECTOR_DB_PATH"] = str(self.vector_db_path)
    
    @property
    def has_openai(self) -> bool:
        """Check if OpenAI API key is configured"""
        return bool(self.openai_api_key)
    
    @property
    def has_anthropic(self) -> bool:
        """Check if Anthropic API key is configured"""
        return bool(self.anthropic_api_key)
    
    @property
    def has_ollama(self) -> bool:
        """Check if Ollama base URL is configured"""
        import requests
        try:
            response = requests.get(f"{self.ollama_base_url}/api/version", timeout=2)
            return response.status_code == 200
        except:
            return False
            
    @property
    def has_github(self) -> bool:
        """Check if GitHub API token is configured"""
        return bool(self.github_api_token)
    
    @property
    def available_models(self) -> List[str]:
        """Get list of available models based on configured API keys"""
        models = []
        if self.has_openai:
            models.extend(["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o"])
        if self.has_anthropic:
            models.extend([
                "claude-3-sonnet-20240229", 
                "claude-3-opus-20240229",
                "claude-3-haiku-20240307",
                "claude-3-5-sonnet-20240620",
                "claude-3-7-sonnet-20250219"
            ])
        if self.has_ollama:
            try:
                import requests
                response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    for model in response.json().get("models", []):
                        models.append(f"ollama/{model['name']}")
            except:
                pass
        return models


# Create global settings instance
settings = Settings()
