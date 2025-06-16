"""
Memory database models for Ergon's memory system.

This module defines the SQLAlchemy models for storing memory metadata,
while the actual vector embeddings are stored in hardware-optimized
vector databases managed by Tekton.
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from ergon.core.database.base import Base

class MemoryCollection(Base):
    """Collection of memories for organizational purposes."""
    __tablename__ = "memory_collections"
    
    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    memories = relationship("Memory", back_populates="collection")

class Memory(Base):
    """Individual memory entry."""
    __tablename__ = "memories"
    
    id = Column(String(255), primary_key=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    collection_id = Column(String(255), ForeignKey("memory_collections.id"), nullable=True)
    content = Column(Text, nullable=False)
    category = Column(String(50), index=True)
    importance = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)
    memory_metadata = Column(JSON, nullable=True)
    
    # Relationships
    agent = relationship("Agent", back_populates="memories")
    collection = relationship("MemoryCollection", back_populates="memories")