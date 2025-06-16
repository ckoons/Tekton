"""
Database engine and session management for Ergon.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from typing import Generator, Any
import os

from ergon.utils.config.settings import settings

# Import Base from base module
from ergon.core.database.base import Base

# Create engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
ScopedSession = scoped_session(SessionLocal)


def get_db() -> Generator:
    """Get database session."""
    db = ScopedSession()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session():
    """Context manager for database session."""
    session = ScopedSession()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    """Initialize the database, creating all tables."""
    # Create database directory if it doesn't exist (for SQLite)
    if settings.database_url.startswith("sqlite"):
        db_path = settings.database_url.replace("sqlite:///", "")
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    
    # Make sure all models are registered
    # Import all models to ensure they're registered with Base
    from ergon.core.database.models import Agent, AgentTool, AgentFile, AgentExecution, AgentMessage, DocumentationPage
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
