#!/usr/bin/env python3
"""
Integration tests for cognitive interface with provenance.

Tests the ez interface extensions for git-like memory tracking.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from engram.cognitive.ez_provenance import (
    wonder, share, wh, wb, fork, merge, x, c
)


class TestCognitiveProvenance:
    """Test cognitive interface with provenance features."""
    
    @pytest.mark.asyncio
    async def test_wonder_with_edits(self):
        """Test wondering about memories with edit visibility."""
        # Mock the base wonder function
        with patch('engram.cognitive.ez_provenance._wonder') as mock_wonder:
            mock_wonder.return_value = [{
                'memory': {
                    'id': 'mem_123',
                    'content': 'Test thought',
                    'metadata': {
                        'last_modified_by': 'Engram',
                        'version': 3
                    }
                }
            }]
            
            results = await wonder("test topic", show_edits=True)
            
            assert len(results) == 1
            memory = results[0]['memory']
            assert memory['edited_by'] == 'Engram'
            assert memory['edit_count'] == 2  # version 3 = 2 edits
    
    @pytest.mark.asyncio
    async def test_wonder_without_provenance(self):
        """Test wonder returns unmodified results when provenance not requested."""
        with patch('engram.cognitive.ez_provenance._wonder') as mock_wonder:
            mock_wonder.return_value = [{
                'memory': {'id': 'mem_123', 'content': 'Test'}
            }]
            
            results = await wonder("test topic")
            
            assert len(results) == 1
            assert 'edited_by' not in results[0]['memory']
    
    @pytest.mark.asyncio
    async def test_share_with_preservation(self):
        """Test sharing thoughts with original preservation."""
        with patch('engram.cognitive.ez_provenance._share') as mock_share:
            mock_share.return_value = {
                'memory_id': 'mem_123',
                'status': 'stored'
            }
            
            result = await share("Important insight", preserve_original=True)
            
            assert result['memory_id'] == 'mem_123'
            assert result['metadata']['preserve_original'] is True
            assert result['metadata']['branch'] == 'main'
    
    @pytest.mark.asyncio
    async def test_share_with_branch(self):
        """Test sharing to specific branch."""
        with patch('engram.cognitive.ez_provenance._share') as mock_share:
            mock_share.return_value = {'memory_id': 'mem_123'}
            
            result = await share(
                "Alternative interpretation",
                branch="experimental"
            )
            
            assert result['metadata']['branch'] == 'experimental'
    
    @pytest.mark.asyncio
    async def test_who_touched_memory(self):
        """Test wh() for viewing memory history."""
        with patch('engram.cognitive.ez_provenance.wonder') as mock_wonder:
            mock_wonder.return_value = [{
                'provenance': [
                    {'actor': 'Claude', 'action': 'created'},
                    {'actor': 'Engram', 'action': 'merged'},
                    {'actor': 'Apollo', 'action': 'revised'}
                ]
            }]
            
            history = await wh("mem_123")
            
            assert len(history) == 3
            assert history[0]['actor'] == 'Claude'
            assert history[2]['action'] == 'revised'
    
    @pytest.mark.asyncio
    async def test_what_branches_exist(self):
        """Test wb() for listing branches."""
        with patch('engram.cognitive.ez_provenance.wonder') as mock_wonder:
            mock_wonder.return_value = [
                {'branches': ['main', 'experimental']},
                {'branches': ['main', 'alternative']}
            ]
            
            branches = await wb("consciousness")
            
            assert 'main' in branches
            assert 'experimental' in branches
            assert 'alternative' in branches
            assert len(set(branches)) == 3  # No duplicates
    
    @pytest.mark.asyncio
    async def test_fork_memory(self):
        """Test forking a memory for alternative interpretation."""
        result = await fork("mem_123", "quantum_interpretation")
        
        assert result['action'] == 'forked'
        assert result['memory_id'] == 'mem_123'
        assert result['branch'] == 'quantum_interpretation'
        assert result['status'] == 'created'
    
    @pytest.mark.asyncio
    async def test_merge_branches(self):
        """Test merging thought branches."""
        result = await merge("experimental", "main")
        
        assert result['action'] == 'merged'
        assert result['source'] == 'experimental'
        assert result['target'] == 'main'
    
    @pytest.mark.asyncio
    async def test_crystallize_with_insight(self):
        """Test crystallizing a specific insight."""
        with patch('engram.cognitive.ez_provenance.share') as mock_share:
            mock_share.return_value = {
                'memory_id': 'mem_crystal_123',
                'status': 'stored'
            }
            
            result = await x("Provenance enables transparent collaboration")
            
            assert result['memory_id'] == 'mem_crystal_123'
            assert result['metadata']['crystallized'] is True
            assert result['metadata']['action'] == 'crystallized'
    
    @pytest.mark.asyncio
    async def test_crystallize_pattern_check(self):
        """Test crystallize checking for patterns."""
        result = await x()  # No insight provided
        
        assert result['status'] == 'checking_for_patterns'
        assert 'suggestion' in result
    
    @pytest.mark.asyncio
    async def test_connect_by_theme(self):
        """Test connecting recent thoughts by theme."""
        result = await c("#consciousness")
        
        assert result['action'] == 'connecting'
        assert result['theme'] == '#consciousness'
    
    @pytest.mark.asyncio
    async def test_connect_specific_memories(self):
        """Test connecting specific memories."""
        result = await c("mem_123", "mem_456", reason="Both discuss emergence")
        
        assert result['action'] == 'connected'
        assert result['memories'] == ('mem_123', 'mem_456')
        assert result['reason'] == "Both discuss emergence"


class TestShortcuts:
    """Test the single-letter shortcuts work correctly."""
    
    @pytest.mark.asyncio
    async def test_w_shortcut(self):
        """Test w() shortcut for wonder."""
        from engram.cognitive.ez_provenance import w, wd
        
        # Verify w and wd point to same function
        assert w is wd
    
    @pytest.mark.asyncio
    async def test_s_shortcut(self):
        """Test s() shortcut for share."""
        from engram.cognitive.ez_provenance import s, sh
        
        # Verify s and sh point to same function
        assert s is sh


if __name__ == "__main__":
    pytest.main([__file__, "-v"])