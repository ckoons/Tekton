"""
Tests for database migrations module.
"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path
import json
import sqlite3

from ergon.core.database.engine import get_db_session, init_db
from ergon.core.database.migrations import MigrationManager
from ergon.utils.config.settings import settings


@pytest.fixture
def temp_dir():
    """Create a temporary directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_db(temp_dir):
    """Create a temporary database."""
    # Save original database URL
    original_db_url = settings.database_url
    
    # Create temporary database path
    temp_db_path = os.path.join(temp_dir, "test.db")
    
    # Set database URL to temporary database
    settings.database_url = f"sqlite:///{temp_db_path}"
    
    # Initialize database
    init_db()
    
    yield temp_db_path
    
    # Reset database URL
    settings.database_url = original_db_url


@pytest.fixture
def migration_manager(temp_dir):
    """Create a migration manager with a temporary directory."""
    migrations_dir = os.path.join(temp_dir, "migrations")
    os.makedirs(migrations_dir, exist_ok=True)
    return MigrationManager(migrations_dir=migrations_dir)


def test_migration_manager_initialization(migration_manager):
    """Test migration manager initialization."""
    assert migration_manager is not None
    assert os.path.exists(migration_manager.alembic_ini_path)
    assert os.path.exists(os.path.join(migration_manager.migrations_dir, "versions"))


def test_migration_manager_init(migration_manager):
    """Test migration manager init method."""
    result = migration_manager.init()
    assert result is True


def test_backup_database(temp_db, migration_manager):
    """Test backing up a database."""
    # Create a table and insert data
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test_backup (id INTEGER PRIMARY KEY, value TEXT)")
    cursor.execute("INSERT INTO test_backup (value) VALUES ('test_data')")
    conn.commit()
    conn.close()
    
    # Backup the database
    backup_path = migration_manager.backup_database()
    
    # Verify backup file exists
    assert os.path.exists(backup_path)
    
    # Verify backup contains the same data
    conn = sqlite3.connect(backup_path)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM test_backup")
    row = cursor.fetchone()
    conn.close()
    
    assert row[0] == 'test_data'


def test_restore_database(temp_db, migration_manager):
    """Test restoring a database from backup."""
    # Create a table and insert data
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test_restore (id INTEGER PRIMARY KEY, value TEXT)")
    cursor.execute("INSERT INTO test_restore (value) VALUES ('original_data')")
    conn.commit()
    conn.close()
    
    # Backup the database
    backup_path = migration_manager.backup_database()
    
    # Modify the original database
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("UPDATE test_restore SET value = 'modified_data'")
    conn.commit()
    conn.close()
    
    # Restore from backup
    success = migration_manager.restore_database(backup_path)
    assert success is True
    
    # Verify data was restored
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM test_restore")
    row = cursor.fetchone()
    conn.close()
    
    assert row[0] == 'original_data'


def test_get_current_revision(migration_manager):
    """Test getting current revision."""
    revision = migration_manager.get_current_revision()
    assert revision is not None
    # Initial database should have no revisions
    assert revision == "None" or revision == "Unknown"


@pytest.mark.skip(reason="Creates actual migration files that are hard to clean up in tests")
def test_create_migration(migration_manager):
    """Test creating a migration."""
    revision = migration_manager.create_migration("test migration")
    assert revision != ""
    
    # Get migrations
    migrations = migration_manager.get_migrations()
    assert len(migrations) >= 1
    
    # Verify our migration is in the list
    assert any(m["revision"] == revision for m in migrations)
    
    # Verify migration message
    migration_data = next(m for m in migrations if m["revision"] == revision)
    assert migration_data["message"] == "test migration"