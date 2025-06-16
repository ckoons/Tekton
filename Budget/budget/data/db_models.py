"""
Database Models for Budget Component

This module defines the SQLAlchemy ORM models for the Budget component.
These models provide persistence for the core domain entities.
"""

import os
import sys
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Type, Union

from sqlalchemy import (
    create_engine, Column, String, Integer, Float, Boolean,
    DateTime, ForeignKey, Text, Enum, JSON, func, text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

# Try to import debug_utils from shared if available
try:
    from shared.debug.debug_utils import debug_log, log_function
except ImportError:
    # Create a simple fallback if shared module is not available
    class DebugLog:
        def __getattr__(self, name):
            def dummy_log(*args, **kwargs):
                pass
            return dummy_log
    debug_log = DebugLog()
    
    def log_function(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# Import models for type annotations
from budget.data.models import (
    BudgetTier, BudgetPeriod, BudgetPolicyType, TaskPriority,
    PriceType, Budget, BudgetPolicy, BudgetAllocation,
    UsageRecord, Alert, ProviderPricing, PriceUpdateRecord,
    PriceSource, BudgetSummary
)

# Import constants for default values
from budget.core.constants import (
    DEFAULT_TOKEN_LIMITS, DEFAULT_COST_LIMITS, 
    DEFAULT_ALLOCATIONS, INITIAL_PRICING_DATA,
    DEFAULT_PRICE_SOURCES
)

# Create base class for all models
Base = declarative_base()

class BudgetDBModel(Base):
    """Base class for Budget entity tables."""
    __abstract__ = True
    __tablename__ = None
    # We should not use 'metadata' as a column name since it's reserved by SQLAlchemy


class BudgetDB(BudgetDBModel):
    """Budget database model."""
    __tablename__ = "budget"
    
    budget_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    owner = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=True)
    meta_data = Column(Text, default="{}")  # JSON stored as text
    
    # Relationships
    policies = relationship("BudgetPolicyDB", back_populates="budget")
    allocations = relationship("BudgetAllocationDB", back_populates="budget")


class BudgetPolicyDB(BudgetDBModel):
    """Budget policy database model."""
    __tablename__ = "budget_policy"
    
    policy_id = Column(String, primary_key=True)
    budget_id = Column(String, ForeignKey("budget.budget_id"), nullable=True)
    type = Column(String, nullable=False)
    period = Column(String, nullable=False)
    tier = Column(String, nullable=True)
    provider = Column(String, nullable=True)
    component = Column(String, nullable=True)
    task_type = Column(String, nullable=True)
    token_limit = Column(Integer, nullable=True)
    cost_limit = Column(Float, nullable=True)
    warning_threshold = Column(Float, default=0.8)
    action_threshold = Column(Float, default=0.95)
    start_date = Column(DateTime, default=datetime.now)
    end_date = Column(DateTime, nullable=True)
    enabled = Column(Boolean, default=True)
    meta_data = Column(Text, default="{}")  # JSON stored as text
    
    # Relationships
    budget = relationship("BudgetDB", back_populates="policies")


class BudgetAllocationDB(BudgetDBModel):
    """Budget allocation database model."""
    __tablename__ = "budget_allocation"
    
    allocation_id = Column(String, primary_key=True)
    budget_id = Column(String, ForeignKey("budget.budget_id"), nullable=True)
    context_id = Column(String, nullable=False)
    component = Column(String, nullable=False)
    tier = Column(String, nullable=True)
    provider = Column(String, nullable=True)
    model = Column(String, nullable=True)
    task_type = Column(String, nullable=False)
    priority = Column(Integer, default=5)
    
    # Token allocation
    tokens_allocated = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    input_tokens_used = Column(Integer, default=0)
    output_tokens_used = Column(Integer, default=0)
    
    # Cost tracking
    estimated_cost = Column(Float, default=0.0)
    actual_cost = Column(Float, default=0.0)
    
    # Timestamps
    creation_time = Column(DateTime, default=datetime.now)
    expiration_time = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Status
    is_active = Column(Boolean, default=True)
    meta_data = Column(Text, default="{}")  # JSON stored as text
    
    # Relationships
    budget = relationship("BudgetDB", back_populates="allocations")
    usage_records = relationship("UsageRecordDB", back_populates="allocation")


class UsageRecordDB(BudgetDBModel):
    """Usage record database model."""
    __tablename__ = "usage_record"
    
    record_id = Column(String, primary_key=True)
    allocation_id = Column(String, ForeignKey("budget_allocation.allocation_id"), nullable=True)
    budget_id = Column(String, ForeignKey("budget.budget_id"), nullable=True)
    context_id = Column(String, nullable=False)
    component = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    model = Column(String, nullable=False)
    task_type = Column(String, nullable=False)
    
    # Token and cost tracking
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    input_cost = Column(Float, default=0.0)
    output_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    pricing_version = Column(String, nullable=True)
    
    # Timestamps and identification
    timestamp = Column(DateTime, default=datetime.now)
    operation_id = Column(String, nullable=True)
    request_id = Column(String, nullable=True)
    user_id = Column(String, nullable=True)
    
    # Additional data
    meta_data = Column(Text, default="{}")  # JSON stored as text
    
    # Relationships
    allocation = relationship("BudgetAllocationDB", back_populates="usage_records")


class AlertDB(BudgetDBModel):
    """Alert database model."""
    __tablename__ = "alert"
    
    alert_id = Column(String, primary_key=True)
    budget_id = Column(String, ForeignKey("budget.budget_id"), nullable=True)
    policy_id = Column(String, ForeignKey("budget_policy.policy_id"), nullable=True)
    severity = Column(String, nullable=False)
    type = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    details = Column(Text, default="{}")  # JSON stored as text
    timestamp = Column(DateTime, default=datetime.now)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)


class ProviderPricingDB(BudgetDBModel):
    """Provider pricing database model."""
    __tablename__ = "provider_pricing"
    
    pricing_id = Column(String, primary_key=True)
    provider = Column(String, nullable=False)
    model = Column(String, nullable=False)
    price_type = Column(String, default=PriceType.TOKEN_BASED)
    input_cost_per_token = Column(Float, default=0.0)
    output_cost_per_token = Column(Float, default=0.0)
    input_cost_per_char = Column(Float, default=0.0)
    output_cost_per_char = Column(Float, default=0.0)
    cost_per_image = Column(Float, nullable=True)
    cost_per_second = Column(Float, nullable=True)
    fixed_cost_per_request = Column(Float, nullable=True)
    version = Column(String, default="1.0")
    source = Column(String, nullable=False)
    source_url = Column(String, nullable=True)
    verified = Column(Boolean, default=False)
    effective_date = Column(DateTime, default=datetime.now)
    end_date = Column(DateTime, nullable=True)
    meta_data = Column(Text, default="{}")  # JSON stored as text
    
    # Relationships
    price_updates = relationship("PriceUpdateRecordDB", 
                                foreign_keys="[PriceUpdateRecordDB.new_pricing_id]",
                                back_populates="new_pricing")


class PriceUpdateRecordDB(BudgetDBModel):
    """Price update record database model."""
    __tablename__ = "price_update_record"
    
    update_id = Column(String, primary_key=True)
    provider = Column(String, nullable=False)
    model = Column(String, nullable=False)
    previous_pricing_id = Column(String, ForeignKey("provider_pricing.pricing_id"), nullable=True)
    new_pricing_id = Column(String, ForeignKey("provider_pricing.pricing_id"), nullable=False)
    source = Column(String, nullable=False)
    verification_status = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    changes = Column(Text, default="{}")  # JSON stored as text
    meta_data = Column(Text, default="{}")  # JSON stored as text
    
    # Relationships
    new_pricing = relationship("ProviderPricingDB", 
                             foreign_keys=[new_pricing_id],
                             back_populates="price_updates")
    previous_pricing = relationship("ProviderPricingDB", 
                                  foreign_keys=[previous_pricing_id])


class PriceSourceDB(BudgetDBModel):
    """Price source database model."""
    __tablename__ = "price_source"
    
    source_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String, nullable=True)
    type = Column(String, nullable=False)
    trust_score = Column(Float, default=1.0)
    update_frequency = Column(Integer, nullable=True)  # in minutes
    last_update = Column(DateTime, nullable=True)
    next_update = Column(DateTime, nullable=True)
    auth_required = Column(Boolean, default=False)
    auth_config = Column(Text, default="{}")  # JSON stored as text
    is_active = Column(Boolean, default=True)
    meta_data = Column(Text, default="{}")  # JSON stored as text


class DatabaseManager:
    """
    Database manager for Budget component.
    
    Handles database connection, session management, and ORM operations.
    """
    
    def __init__(self, connection_string=None):
        """Initialize the database manager."""
        if connection_string:
            self.connection_string = connection_string
        else:
            # Store in Budget component directory
            import os
            from pathlib import Path
            budget_dir = Path(__file__).parent.parent.parent.absolute()
            db_path = os.path.join(budget_dir, "budget.db")
            self.connection_string = f"sqlite:///{db_path}"

        self.engine = None
        self.session_factory = None
        self.Session = None
        self.initialized = False
        
    @log_function()
    def initialize(self):
        """Initialize the database connection and create tables if needed."""
        if self.initialized:
            return
        
        debug_log.info("budget_db", f"Initializing database with {self.connection_string}")
        
        # Create engine
        self.engine = create_engine(self.connection_string, echo=False)
        
        # Create session factory
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        
        # Create tables
        Base.metadata.create_all(self.engine)
        
        self.initialized = True
        debug_log.info("budget_db", "Database initialized")
        
        # Load initial data if needed
        self._load_initial_data()
        
    @log_function()
    def _load_initial_data(self):
        """Load initial data into the database if tables are empty."""
        session = self.Session()
        try:
            # Check if we need to load initial price sources
            price_source_count = session.query(PriceSourceDB).count()
            if price_source_count == 0:
                debug_log.info("budget_db", "Loading initial price sources")
                self._load_price_sources(session)
            
            # Check if we need to load initial pricing data
            pricing_count = session.query(ProviderPricingDB).count()
            if pricing_count == 0:
                debug_log.info("budget_db", "Loading initial pricing data")
                self._load_initial_pricing(session)
                
            # Commit changes
            session.commit()
            debug_log.info("budget_db", "Initial data loaded")
            
        except Exception as e:
            session.rollback()
            debug_log.error("budget_db", f"Error loading initial data: {str(e)}")
        finally:
            session.close()

    @log_function()
    def _load_price_sources(self, session):
        """Load initial price sources."""
        for source_data in DEFAULT_PRICE_SOURCES:
            source = PriceSourceDB(
                source_id=str(uuid.uuid4()),
                name=source_data["name"],
                description=source_data.get("description"),
                url=source_data.get("url"),
                type=source_data["type"],
                trust_score=source_data.get("trust_score", 1.0),
                update_frequency=source_data.get("update_frequency"),
                is_active=source_data.get("is_active", True)
            )
            session.add(source)
            
    @log_function()
    def _load_initial_pricing(self, session):
        """Load initial pricing data."""
        # Get the litellm source for attribution
        source = session.query(PriceSourceDB).filter_by(name="LiteLLM").first()
        source_id = source.source_id if source else str(uuid.uuid4())
        
        # Load initial pricing data
        for provider, models in INITIAL_PRICING_DATA.items():
            for model, pricing in models.items():
                model_pricing = ProviderPricingDB(
                    pricing_id=str(uuid.uuid4()),
                    provider=provider,
                    model=model,
                    price_type=PriceType.TOKEN_BASED,
                    input_cost_per_token=pricing.get("input_cost_per_token", 0.0),
                    output_cost_per_token=pricing.get("output_cost_per_token", 0.0),
                    version="1.0",
                    source=source_id,
                    verified=True,
                    effective_date=datetime.now()
                )
                session.add(model_pricing)

    def get_session(self):
        """Get a database session."""
        if not self.initialized:
            self.initialize()
        return self.Session()
        
    def close(self):
        """Close the database connection."""
        if self.Session:
            self.Session.remove()
            
    def __del__(self):
        """Clean up when the object is deleted."""
        self.close()


# Create singleton instance
db_manager = DatabaseManager()


class DatabaseRepository:
    """
    Base repository for database operations.
    
    Provides common CRUD operations for database models.
    """
    
    def __init__(self, model_class: Type[BudgetDBModel], pydantic_class=None):
        """Initialize the repository with model classes."""
        self.model_class = model_class
        self.pydantic_class = pydantic_class
        
    def _to_pydantic(self, db_model):
        """Convert a database model to a Pydantic model."""
        if not self.pydantic_class:
            return db_model
            
        # Convert JSON strings to dictionaries
        data = {c.name: getattr(db_model, c.name) for c in db_model.__table__.columns}
        for field in ["meta_data", "details", "changes", "auth_config"]:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                except (json.JSONDecodeError, TypeError):
                    data[field] = {}
                    
        return self.pydantic_class(**data)
        
    def _to_db_model(self, pydantic_model):
        """Convert a Pydantic model to a database model."""
        data = pydantic_model.dict()
        
        # Convert dictionaries to JSON strings
        for field in ["meta_data", "details", "changes", "auth_config"]:
            if field in data and isinstance(data[field], dict):
                data[field] = json.dumps(data[field])
                
        return self.model_class(**data)
        
    @log_function()
    def get_by_id(self, id_value, session=None):
        """Get a record by its primary key."""
        should_close = False
        if not session:
            session = db_manager.get_session()
            should_close = True
            
        try:
            # Get model by primary key
            result = session.query(self.model_class).get(id_value)
            
            if result:
                return self._to_pydantic(result)
            return None
            
        finally:
            if should_close:
                session.close()
                
    @log_function()
    def get_all(self, limit=None, offset=None, session=None):
        """Get all records, optionally with pagination."""
        should_close = False
        if not session:
            session = db_manager.get_session()
            should_close = True
            
        try:
            # Build query
            query = session.query(self.model_class)
            
            # Apply pagination
            if offset is not None:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)
                
            # Execute query
            results = query.all()
            
            # Convert to Pydantic models
            return [self._to_pydantic(result) for result in results]
            
        finally:
            if should_close:
                session.close()
                
    @log_function()
    def create(self, model, session=None):
        """Create a new record."""
        should_close = False
        if not session:
            session = db_manager.get_session()
            should_close = True
            
        try:
            # Convert to database model if needed
            if not isinstance(model, self.model_class):
                db_model = self._to_db_model(model)
            else:
                db_model = model
                
            # Add to session
            session.add(db_model)
            session.commit()
            
            # Return as Pydantic model
            return self._to_pydantic(db_model)
            
        except Exception as e:
            session.rollback()
            debug_log.error("budget_db", f"Error creating record: {str(e)}")
            raise
            
        finally:
            if should_close:
                session.close()
                
    @log_function()
    def update(self, model, session=None):
        """Update an existing record."""
        should_close = False
        if not session:
            session = db_manager.get_session()
            should_close = True
            
        try:
            # Get primary key field name
            pk_field = self.model_class.__table__.primary_key.columns.values()[0].name
            
            # Get primary key value
            if isinstance(model, self.model_class):
                pk_value = getattr(model, pk_field)
            else:
                pk_value = getattr(model, pk_field)
                
            # Check if record exists
            existing = session.query(self.model_class).get(pk_value)
            if not existing:
                debug_log.warn("budget_db", f"Record with ID {pk_value} not found for update")
                return None
                
            # Convert to database model if needed
            if not isinstance(model, self.model_class):
                data = model.dict(exclude={pk_field})
                
                # Convert dictionaries to JSON strings
                for field in ["meta_data", "details", "changes", "auth_config"]:
                    if field in data and isinstance(data[field], dict):
                        data[field] = json.dumps(data[field])
                        
                # Update fields
                for key, value in data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
            else:
                # Copy fields from model to existing
                for column in self.model_class.__table__.columns:
                    if column.name != pk_field:
                        setattr(existing, column.name, getattr(model, column.name))
                        
            # Commit changes
            session.commit()
            
            # Return updated model
            return self._to_pydantic(existing)
            
        except Exception as e:
            session.rollback()
            debug_log.error("budget_db", f"Error updating record: {str(e)}")
            raise
            
        finally:
            if should_close:
                session.close()
                
    @log_function()
    def delete(self, id_value, session=None):
        """Delete a record by its primary key."""
        should_close = False
        if not session:
            session = db_manager.get_session()
            should_close = True
            
        try:
            # Get record
            record = session.query(self.model_class).get(id_value)
            if not record:
                debug_log.warn("budget_db", f"Record with ID {id_value} not found for deletion")
                return False
                
            # Delete record
            session.delete(record)
            session.commit()
            
            return True
            
        except Exception as e:
            session.rollback()
            debug_log.error("budget_db", f"Error deleting record: {str(e)}")
            raise
            
        finally:
            if should_close:
                session.close()
                
    @log_function()
    def upsert(self, model, session=None):
        """Create or update a record."""
        should_close = False
        if not session:
            session = db_manager.get_session()
            should_close = True
            
        try:
            # Get primary key field name
            pk_field = self.model_class.__table__.primary_key.columns.values()[0].name
            
            # Get primary key value
            if isinstance(model, self.model_class):
                pk_value = getattr(model, pk_field)
            else:
                pk_value = getattr(model, pk_field)
                
            # Check if record exists
            existing = session.query(self.model_class).get(pk_value)
            if existing:
                return self.update(model, session=session)
            else:
                return self.create(model, session=session)
                
        finally:
            if should_close:
                session.close()


# Create repository classes for each model
budget_repository = DatabaseRepository(BudgetDB, Budget)
policy_repository = DatabaseRepository(BudgetPolicyDB, BudgetPolicy)
allocation_repository = DatabaseRepository(BudgetAllocationDB, BudgetAllocation)
usage_repository = DatabaseRepository(UsageRecordDB, UsageRecord)
alert_repository = DatabaseRepository(AlertDB, Alert)
pricing_repository = DatabaseRepository(ProviderPricingDB, ProviderPricing)
update_repository = DatabaseRepository(PriceUpdateRecordDB, PriceUpdateRecord)
source_repository = DatabaseRepository(PriceSourceDB, PriceSource)