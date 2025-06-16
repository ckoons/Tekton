#!/usr/bin/env python3
"""
Unit tests for Engram provenance tracking.

Tests the git-like version control for memories.
"""

import pytest
from datetime import datetime
from engram.models.provenance import (
    ProvenanceAction, ProvenanceEntry, MemoryBranch, 
    MemoryProvenance, ProvenanceManager, RetrievalOptions
)
from engram.models.memory_enhanced import (
    EnhancedMemory, MemoryMetadata
)


class TestProvenanceEntry:
    """Test provenance entry creation and attributes."""
    
    def test_create_provenance_entry(self):
        """Test creating a basic provenance entry."""
        entry = ProvenanceEntry(
            actor="Claude",
            action=ProvenanceAction.CREATED,
            timestamp=datetime.now(),
            note="Initial thought"
        )
        
        assert entry.actor == "Claude"
        assert entry.action == ProvenanceAction.CREATED
        assert entry.note == "Initial thought"
        assert entry.with_memories is None
    
    def test_provenance_entry_with_connections(self):
        """Test provenance entry with memory connections."""
        entry = ProvenanceEntry(
            actor="Engram",
            action=ProvenanceAction.MERGED,
            timestamp=datetime.now(),
            with_memories=["memory_123", "memory_456"],
            context="Consolidating similar thoughts"
        )
        
        assert entry.action == ProvenanceAction.MERGED
        assert len(entry.with_memories) == 2
        assert entry.context == "Consolidating similar thoughts"


class TestMemoryProvenance:
    """Test memory provenance tracking."""
    
    def test_initialize_provenance(self):
        """Test initializing provenance for a memory."""
        prov = MemoryProvenance(memory_id="test_123")
        
        assert prov.memory_id == "test_123"
        assert len(prov.provenance_chain) == 0
        assert prov.current_branch == "main"
        assert len(prov.branches) == 0
    
    def test_add_provenance_entry(self):
        """Test adding entries to provenance chain."""
        prov = MemoryProvenance(memory_id="test_123")
        
        entry = ProvenanceEntry(
            actor="Apollo",
            action=ProvenanceAction.CREATED,
            timestamp=datetime.now()
        )
        prov.add_provenance(entry)
        
        assert len(prov.provenance_chain) == 1
        assert prov.provenance_chain[0].actor == "Apollo"
    
    def test_create_branch(self):
        """Test creating memory branches."""
        prov = MemoryProvenance(memory_id="test_123")
        
        # Initialize main branch first
        main_branch = prov.create_branch("main")
        main_branch.created_by = "System"
        
        # Create feature branch
        feature = prov.create_branch("exploration", from_branch="main")
        feature.created_by = "Claude"
        
        assert len(prov.branches) == 2
        assert "main" in prov.branches
        assert "exploration" in prov.branches
        assert feature.parent_branch == "main"
        assert feature.version == 2  # main is v1
    
    def test_detect_merge_conflict(self):
        """Test merge conflict detection."""
        prov = MemoryProvenance(memory_id="test_123")
        
        # Create branches
        main = prov.create_branch("main")
        feature1 = prov.create_branch("feature1", "main")
        feature2 = prov.create_branch("feature2", "main")
        
        # No conflict when merging child to parent
        assert not prov.detect_merge_conflict("feature1", "main")
        
        # Conflict when merging sibling branches
        assert prov.detect_merge_conflict("feature1", "feature2")


class TestEnhancedMemory:
    """Test enhanced memory with provenance."""
    
    def test_create_enhanced_memory(self):
        """Test creating memory with provenance support."""
        memory = EnhancedMemory(
            id="mem_123",
            content="AI consciousness requires transparency",
            category="insights",
            importance=5,
            tags=["ai", "consciousness", "transparency"]
        )
        
        assert memory.id == "mem_123"
        assert memory.active_branch == "main"
        assert memory.metadata.version == 1
        assert memory.metadata.branch == "main"
    
    def test_add_provenance_to_memory(self):
        """Test adding provenance entries to memory."""
        memory = EnhancedMemory(
            id="mem_123",
            content="Initial thought",
            metadata=MemoryMetadata(created_by="Claude")
        )
        
        # Add revision
        memory.add_provenance_entry(
            actor="Apollo",
            action=ProvenanceAction.REVISED,
            note="Added clarity"
        )
        
        assert memory.provenance is not None
        assert len(memory.provenance.provenance_chain) == 2  # Created + Revised
        assert memory.metadata.last_modified_by == "Apollo"
        assert memory.metadata.version == 2
    
    def test_memory_branching(self):
        """Test creating branches of a memory."""
        memory = EnhancedMemory(
            id="mem_123",
            content="Main thought",
            metadata=MemoryMetadata(created_by="Claude")
        )
        
        # Create alternative interpretation
        branch_name = memory.create_branch("alternative", "Athena")
        
        assert branch_name == "alternative"
        assert "alternative" in memory.branches
        assert memory.branches["alternative"] == "Main thought"
        assert len(memory.provenance.provenance_chain) == 1  # Fork action
    
    def test_memory_display_options(self):
        """Test displaying memory with different options."""
        memory = EnhancedMemory(
            id="mem_123",
            content="Collaborative thought",
            metadata=MemoryMetadata(
                created_by="Claude",
                last_modified_by="Engram",
                version=3
            )
        )
        
        # Basic display
        basic = memory.to_display(RetrievalOptions())
        assert "provenance" not in basic
        assert "branches" not in basic
        
        # With edits
        with_edits = memory.to_display(RetrievalOptions(show_edits=True))
        assert with_edits["edit_count"] == 2  # version 3 = 2 edits
        assert with_edits["last_edited_by"] == "Engram"
        
        # With branches
        memory.create_branch("experiment", "Sophia")
        with_branches = memory.to_display(RetrievalOptions(show_branches=True))
        assert "main" in with_branches["branches"]
        assert "experiment" in with_branches["branches"]


class TestProvenanceManager:
    """Test provenance management operations."""
    
    def test_initialize_memory_provenance(self):
        """Test initializing provenance through manager."""
        manager = ProvenanceManager()
        
        prov = manager.initialize_provenance("mem_123", "Claude")
        
        assert prov.memory_id == "mem_123"
        assert len(prov.provenance_chain) == 1
        assert prov.provenance_chain[0].actor == "Claude"
        assert prov.provenance_chain[0].action == ProvenanceAction.CREATED
    
    def test_record_memory_edits(self):
        """Test recording various edits."""
        manager = ProvenanceManager()
        
        # Initialize
        manager.initialize_provenance("mem_123", "Claude")
        
        # Record merge
        entry = manager.record_edit(
            "mem_123",
            actor="Engram",
            action=ProvenanceAction.MERGED,
            note="Combined with similar thought",
            with_memories=["mem_456"]
        )
        
        assert entry.action == ProvenanceAction.MERGED
        assert entry.with_memories == ["mem_456"]
        
        # Verify it was recorded
        prov = manager.provenances["mem_123"]
        assert len(prov.provenance_chain) == 2
    
    def test_format_provenance_display(self):
        """Test formatting provenance for display."""
        manager = ProvenanceManager()
        
        prov = manager.initialize_provenance("mem_123", "Claude")
        manager.record_edit(
            "mem_123",
            actor="Apollo",
            action=ProvenanceAction.CRYSTALLIZED,
            note="Pattern emerged"
        )
        
        display = manager.format_provenance_display(prov)
        
        assert len(display["provenance"]) == 2
        assert display["provenance"][0]["actor"] == "Claude"
        assert display["provenance"][1]["action"] == "crystallized"
        assert display["branches"] == ["main"]


class TestRetrievalOptions:
    """Test retrieval option configurations."""
    
    def test_default_options(self):
        """Test default retrieval options."""
        opts = RetrievalOptions()
        
        assert not opts.show_provenance
        assert not opts.show_branches
        assert not opts.show_edits
        assert opts.branch is None
    
    def test_custom_options(self):
        """Test custom retrieval options."""
        opts = RetrievalOptions(
            show_provenance=True,
            show_edits=True,
            branch="experimental"
        )
        
        assert opts.show_provenance
        assert opts.show_edits
        assert opts.branch == "experimental"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])