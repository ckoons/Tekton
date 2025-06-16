"""
Natural memory interface for AI users.

Usage:
    # Natural interface
    memory = await engram_start()
    context = await center()
    async with think("Casey taught me about mycelial networks"):
        pass
    
    # EZ interface (for dinosaurs & efficiency lovers)
    await u("claude")  # up
    await m()          # me (who am I?)
    await w("topic")   # wonder
    await s("thought") # share
    
    # Even simpler
    from engram.cognitive import ez
    await ez()  # auto-initialize
    await s("two characters beat twenty")
"""

from .natural_interface import engram_start, center, think, wonder, share, listen, join_space, broadcast
from .memory_stream import MemoryStream
from .context_manager import ContextManager
from .peer_awareness import PeerAwareness

# Import emotional memory if available
try:
    from .emotional_memory import (
        ethink, breakthrough, frustrated, flow, curious,
        Emotion, EmotionalMemoryStrength
    )
    _emotional_available = True
except ImportError:
    _emotional_available = False

# Import ez commands for simple usage
try:
    from .ez import (
        up, me, th, wd, sh, ls, cd, bc,
        u, m, w, s, l,
        pwd, ps, h, ez
    )
    _ez_available = True
except ImportError:
    _ez_available = False

# Import enhanced provenance commands if available
try:
    from .ez_provenance import (
        wonder as wonder_prov, share as share_prov,
        wh, wb, fork, merge, x, c
    )
    _provenance_available = True
except ImportError:
    _provenance_available = False

# Import katra commands if available
try:
    from .ez_katra import (
        k, kl, kf, kb, kh,
        store, summon, switch, list_katras, fork as fork_katra, blend
    )
    from .katra_manager import KatraManager
    _katra_available = True
except ImportError:
    _katra_available = False

__all__ = ['engram_start', 'center', 'think', 'wonder', 'share', 'listen', 'join_space', 'broadcast', 
           'MemoryStream', 'ContextManager', 'PeerAwareness']

# Add emotional memory if available
if _emotional_available:
    __all__.extend([
        'ethink', 'breakthrough', 'frustrated', 'flow', 'curious',
        'Emotion', 'EmotionalMemoryStrength'
    ])

# Import memory enhancements
try:
    from .memory_strength import (
        decay_manager, remember_with_strength, recall_and_reinforce,
        MemoryStrength, MemoryDecayManager
    )
    from .dream_state import dream, wake, insights, DreamState
    from .semantic_clustering import organize, find_related, clusters, SemanticOrganizer
    from .memory_fusion import fuse, auto_fuse, fusion_report, MemoryFusionEngine
    _enhancements_available = True
except ImportError:
    _enhancements_available = False

# Add enhancement features if available
if _enhancements_available:
    __all__.extend([
        # Memory strength
        'decay_manager', 'remember_with_strength', 'recall_and_reinforce',
        # Dream state
        'dream', 'wake', 'insights',
        # Semantic clustering
        'organize', 'find_related', 'clusters',
        # Memory fusion
        'fuse', 'auto_fuse', 'fusion_report'
    ])

# Add ez commands if available
if _ez_available:
    __all__.extend([
        # EZ interface (2 char)
        'up', 'me', 'th', 'wd', 'sh', 'ls', 'cd', 'bc',
        # EZ interface (1 char)  
        'u', 'm', 'w', 's', 'l',
        # Bash-like
        'pwd', 'ps',
        # Helpers
        'h', 'ez'
    ])

# Add provenance commands if available
if _provenance_available:
    __all__.extend([
        'wonder_prov', 'share_prov',
        'wh', 'wb', 'fork', 'merge', 'x', 'c'
    ])

# Add katra commands if available
if _katra_available:
    __all__.extend([
        'k', 'kl', 'kf', 'kb', 'kh',
        'store', 'summon', 'switch', 'list_katras', 'fork_katra', 'blend',
        'KatraManager'
    ])