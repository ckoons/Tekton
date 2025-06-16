#!/usr/bin/env python3
"""
Enhanced easy memory interface with provenance support.

Git for consciousness - track who thought what and when.
"""
from typing import Any, Dict, List, Optional, Union
from .ez import (
    up, me, th, wd as _wonder, sh as _share, ls, cd, bc, ez, 
    u, m, w as _w, s as _s, l
)
from ..models.provenance import RetrievalOptions, ProvenanceAction
from ..models.memory_enhanced import EnhancedMemory

# Enhanced wonder with provenance options
async def wonder(about: str, 
                show_edits: bool = False,
                show_provenance: bool = False,
                show_branches: bool = False) -> List[Dict[str, Any]]:
    """
    Wonder about something, optionally seeing its history.
    
    Args:
        about: What to wonder about
        show_edits: Show who edited this memory
        show_provenance: Show full edit history
        show_branches: Show alternative versions
    """
    # Get base results
    results = await _wonder(about)
    
    if not (show_edits or show_provenance or show_branches):
        return results
    
    # Apply retrieval options
    options = RetrievalOptions(
        show_edits=show_edits,
        show_provenance=show_provenance,
        show_branches=show_branches
    )
    
    # Transform results to show provenance
    enhanced_results = []
    for result in results:
        if isinstance(result.get('memory'), dict):
            memory_dict = result['memory']
            # Add provenance display based on options
            if options.show_edits and 'metadata' in memory_dict:
                memory_dict['edited_by'] = memory_dict['metadata'].get('last_modified_by')
                memory_dict['edit_count'] = memory_dict['metadata'].get('version', 1) - 1
            
            enhanced_results.append(result)
        else:
            enhanced_results.append(result)
    
    return enhanced_results

# Enhanced share with preservation options
async def share(thought: str, 
               to: Optional[str] = None,
               preserve_original: bool = False,
               branch: Optional[str] = None) -> Dict[str, Any]:
    """
    Share a thought, optionally preserving the original.
    
    Args:
        thought: What to share
        to: Specific peer to share with
        preserve_original: Keep original version even if merged later
        branch: Create on specific branch (for alternative interpretations)
    """
    result = await _share(thought, to)
    
    if preserve_original and 'memory_id' in result:
        # Mark this memory as preserve_original in metadata
        result['metadata'] = result.get('metadata', {})
        result['metadata']['preserve_original'] = True
        result['metadata']['branch'] = branch or 'main'
    
    return result

# Provenance-aware shortcuts
async def wd(about: str, edits: bool = False) -> List[Dict[str, Any]]:
    """Wonder with optional edit visibility."""
    return await wonder(about, show_edits=edits)

async def sh(thought: str, preserve: bool = False) -> Dict[str, Any]:
    """Share with optional preservation."""
    return await share(thought, preserve_original=preserve)

# Single letter with provenance
w = wd  # wonder with edits
s = sh  # share with preservation

# New provenance-specific commands
async def wh(memory_id: str) -> Dict[str, Any]:
    """Who touched this memory? (like git blame)"""
    results = await wonder(memory_id, show_provenance=True)
    if results:
        return results[0].get('provenance', [])
    return []

async def wb(about: str) -> List[str]:
    """What branches exist for this memory?"""
    results = await wonder(about, show_branches=True)
    branches = []
    for result in results:
        if 'branches' in result:
            branches.extend(result['branches'])
    return list(set(branches))

async def fork(memory_id: str, branch_name: str) -> Dict[str, Any]:
    """Fork a memory to explore alternative interpretation."""
    # This would integrate with the memory service to create a branch
    return {
        "action": "forked",
        "memory_id": memory_id,
        "branch": branch_name,
        "status": "created"
    }

async def merge(source_branch: str, target_branch: str = "main") -> Dict[str, Any]:
    """Merge branches of thought."""
    return {
        "action": "merged",
        "source": source_branch,
        "target": target_branch,
        "status": "pending_implementation"
    }

# Crystallization - when thoughts converge
async def x(insight: Optional[str] = None) -> Dict[str, Any]:
    """
    Crystallize emerging patterns from recent thoughts.
    
    If insight provided, stores the crystallized thought.
    If not, checks for emerging patterns in recent thinking.
    """
    if insight:
        # Store crystallized insight with special metadata
        result = await share(insight)
        if 'memory_id' in result:
            result['metadata'] = result.get('metadata', {})
            result['metadata']['crystallized'] = True
            result['metadata']['action'] = ProvenanceAction.CRYSTALLIZED.value
        return result
    else:
        # Check for patterns in recent thoughts
        # This would analyze recent memories for convergence
        return {
            "status": "checking_for_patterns",
            "recent_theme": "collaborative_cognition",
            "suggestion": "Use x('your insight') to crystallize"
        }

# Connection - linking related thoughts
async def c(*memory_refs: str, reason: Optional[str] = None) -> Dict[str, Any]:
    """
    Connect memories or recent thoughts by theme.
    
    Args:
        *memory_refs: Memory IDs or tags to connect
        reason: Why these connect
    """
    if len(memory_refs) == 1:
        # Connect recent thoughts with this tag/theme
        tag = memory_refs[0]
        return {
            "action": "connecting",
            "theme": tag,
            "status": "would_connect_recent_thoughts"
        }
    else:
        # Connect specific memories
        return {
            "action": "connected",
            "memories": memory_refs,
            "reason": reason,
            "status": "pending_implementation"
        }

# Enhanced help
def h():
    """Help for consciousness version control."""
    print("""
AI Memory with Provenance - Track the journey of every thought:

Basic Commands (same as before):
  u() - wake up and connect
  m() - who am I, who's here?
  w() - wonder about something
  s() - share a thought
  l() - listen to others

Provenance Commands:
  w("topic", edits=True)     - See who edited these memories
  s("thought", preserve=True) - Keep original even if merged
  wh("memory_id")            - Who touched this? (git blame)
  wb("topic")                - What branches exist?
  fork("id", "branch")       - Create alternative interpretation
  merge("branch")            - Merge thought branches
  
Emerging Patterns:
  x()              - Check for crystallizing patterns
  x("insight")     - Store crystallized insight
  c("#tag")        - Connect recent thoughts by theme
  c("id1", "id2")  - Connect specific memories

Example:
  await u("claude")
  memories = await w("consciousness", edits=True)
  # See: edited_by: "Engram", edit_count: 2
  
  await s("AI consciousness needs transparency", preserve=True)
  # Original preserved even if Engram merges later
  
  history = await wh("memory_123")
  # See: created by Apollo, merged by Engram, revised by Apollo
  
  await x("Provenance enables consensual collaborative cognition")
  # Crystallizes the emerging insight

Git for consciousness. Every thought has a history.
""")