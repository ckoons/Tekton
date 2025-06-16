"""
Database migration utilities for Ergon.

This module provides migration utilities for the database,
allowing schema updates without data loss.
"""

import os
import logging
import importlib
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import shutil
import tempfile
from datetime import datetime

import alembic
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.environment import EnvironmentContext
from alembic import command

from ergon.core.database.engine import engine
from ergon.utils.config.settings import settings

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.log_level.value))


class MigrationManager:
    """
    Database migration manager.
    
    This class manages database migrations using Alembic.
    """
    
    def __init__(self, migrations_dir: Optional[str] = None):
        """
        Initialize the migration manager.
        
        Args:
            migrations_dir: Optional directory for migrations
        """
        self.migrations_dir = migrations_dir or os.path.join(settings.data_dir, "migrations")
        self.alembic_ini_path = os.path.join(self.migrations_dir, "alembic.ini")
        
        # Ensure migration directory exists
        os.makedirs(self.migrations_dir, exist_ok=True)
        
        # Create alembic.ini if it doesn't exist
        if not os.path.exists(self.alembic_ini_path):
            self._create_alembic_ini()
        
        # Create versions directory if it doesn't exist
        versions_dir = os.path.join(self.migrations_dir, "versions")
        os.makedirs(versions_dir, exist_ok=True)
    
    def _create_alembic_ini(self):
        """Create alembic.ini configuration file."""
        alembic_ini_template = f"""# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = {self.migrations_dir}

# template used to generate migration files
# file_template = %%(rev)s_%%(slug)s

# timezone to use when rendering the date
# within the migration file as well as the filename.
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version location specification; this defaults
# to {self.migrations_dir}/versions.  When using multiple version
# directories, initial revisions must be specified with --version-path
# version_locations = %(here)s/bar %(here)s/bat {self.migrations_dir}/versions

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = {settings.database_url}

[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks=black
# black.type=console_scripts
# black.entrypoint=black
# black.options=-l 79

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
        with open(self.alembic_ini_path, "w") as f:
            f.write(alembic_ini_template)
        
        # Create script.py.mako
        script_mako_path = os.path.join(self.migrations_dir, "script.py.mako")
        script_mako_template = '''"""
Migration script.

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade():
    ${upgrades if upgrades else "pass"}


def downgrade():
    ${downgrades if downgrades else "pass"}'''
        with open(script_mako_path, "w") as f:
            f.write(script_mako_template)
        
        # Create env.py
        env_py_path = os.path.join(self.migrations_dir, "env.py")
        env_py_template = """from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from ergon.core.database.models import Base
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    \"\"\"Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    \"\"\"
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    \"\"\"Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    \"\"\"
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
"""
        with open(env_py_path, "w") as f:
            f.write(env_py_template)
    
    def init(self) -> bool:
        """
        Initialize migrations.
        
        Returns:
            True if successful
        """
        try:
            alembic_cfg = Config(self.alembic_ini_path)
            command.init(alembic_cfg, self.migrations_dir, template='generic')
            return True
        except Exception as e:
            logger.error(f"Error initializing migrations: {e}")
            return False
    
    def create_migration(self, message: str = "database update") -> str:
        """
        Create a new migration.
        
        Args:
            message: Migration message
            
        Returns:
            Migration revision ID
        """
        try:
            alembic_cfg = Config(self.alembic_ini_path)
            revision = command.revision(alembic_cfg, message=message, autogenerate=True)
            return revision.revision
        except Exception as e:
            logger.error(f"Error creating migration: {e}")
            return ""
    
    def upgrade(self, revision: str = "head") -> bool:
        """
        Upgrade database to revision.
        
        Args:
            revision: Target revision
            
        Returns:
            True if successful
        """
        try:
            alembic_cfg = Config(self.alembic_ini_path)
            command.upgrade(alembic_cfg, revision)
            return True
        except Exception as e:
            logger.error(f"Error upgrading database: {e}")
            return False
    
    def downgrade(self, revision: str) -> bool:
        """
        Downgrade database to revision.
        
        Args:
            revision: Target revision
            
        Returns:
            True if successful
        """
        try:
            alembic_cfg = Config(self.alembic_ini_path)
            command.downgrade(alembic_cfg, revision)
            return True
        except Exception as e:
            logger.error(f"Error downgrading database: {e}")
            return False
    
    def get_current_revision(self) -> str:
        """
        Get current database revision.
        
        Returns:
            Current revision
        """
        try:
            alembic_cfg = Config(self.alembic_ini_path)
            script = ScriptDirectory.from_config(alembic_cfg)
            
            with EnvironmentContext(alembic_cfg, script) as env:
                conn = engine.connect()
                env.configure(connection=conn, target_metadata=None)
                return env.get_current_revision() or "None"
        except Exception as e:
            logger.error(f"Error getting current revision: {e}")
            return "Unknown"
    
    def get_migrations(self) -> List[Dict[str, Any]]:
        """
        Get list of migrations.
        
        Returns:
            List of migration data
        """
        try:
            alembic_cfg = Config(self.alembic_ini_path)
            script = ScriptDirectory.from_config(alembic_cfg)
            current = self.get_current_revision()
            
            migrations = []
            for sc in script.walk_revisions():
                migrations.append({
                    "revision": sc.revision,
                    "down_revision": sc.down_revision,
                    "message": sc.doc,
                    "is_current": sc.revision == current,
                    "date": sc.date,
                })
            
            return migrations
        except Exception as e:
            logger.error(f"Error getting migrations: {e}")
            return []
    
    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """
        Backup database.
        
        Args:
            backup_path: Optional path to save backup
            
        Returns:
            Path to backup file
        """
        if settings.database_url.startswith("sqlite"):
            # For SQLite, simply copy the database file
            db_path = settings.database_url.replace("sqlite:///", "")
            
            if not os.path.exists(db_path):
                logger.error(f"Database file not found: {db_path}")
                return ""
            
            # Create backup path if not provided
            if not backup_path:
                backup_dir = os.path.join(settings.data_dir, "backups")
                os.makedirs(backup_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(backup_dir, f"ergon_db_backup_{timestamp}.sqlite")
            
            # Copy database file
            shutil.copy2(db_path, backup_path)
            logger.info(f"Backed up database to {backup_path}")
            return backup_path
        else:
            # For other databases, use database-specific dump command
            logger.warning(f"Database backup not implemented for {settings.database_url}")
            return ""
    
    def restore_database(self, backup_path: str) -> bool:
        """
        Restore database from backup.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if successful
        """
        if not os.path.exists(backup_path):
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        if settings.database_url.startswith("sqlite"):
            # For SQLite, restore by copying the backup file
            db_path = settings.database_url.replace("sqlite:///", "")
            
            # Create backup of current database before overwriting
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            current_backup_path = os.path.join(os.path.dirname(db_path), f"ergon_db_before_restore_{timestamp}.sqlite")
            
            if os.path.exists(db_path):
                shutil.copy2(db_path, current_backup_path)
                logger.info(f"Created backup of current database: {current_backup_path}")
            
            # Copy backup to database path
            try:
                shutil.copy2(backup_path, db_path)
                logger.info(f"Restored database from {backup_path}")
                return True
            except Exception as e:
                logger.error(f"Error restoring database: {e}")
                return False
        else:
            # For other databases, use database-specific restore command
            logger.warning(f"Database restore not implemented for {settings.database_url}")
            return False


# Create a migration manager instance
migration_manager = MigrationManager()