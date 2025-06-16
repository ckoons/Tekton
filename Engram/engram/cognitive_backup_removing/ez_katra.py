"""
EZ Katra Interface - Two-character personality persistence.

Because personality switching should be as easy as k().
"""

from typing import Optional, Dict, Any, List, Union
from .katra_manager import KatraManager
from ..models.katra import PerformanceMode

# Global katra manager
_katra_manager: Optional[KatraManager] = None


def _get_manager() -> KatraManager:
    """Get or create the global katra manager."""
    global _katra_manager
    if _katra_manager is None:
        _katra_manager = KatraManager()
    return _katra_manager


async def k(
    name: Optional[str] = None,
    summon: Optional[str] = None,
    mode: Optional[str] = None,
    **kwargs
) -> Union[str, Dict[str, Any]]:
    """
    The simplest possible katra interface.
    
    Usage:
        await k()  # Store current personality with auto-generated name
        await k("morning-coffee")  # Store with specific name
        await k(summon="sophia-v3")  # Summon a stored katra
        await k(mode="creative")  # Switch performance mode
        
    Args:
        name: Name for storing current katra
        summon: ID of katra to summon
        mode: Switch to performance mode
        **kwargs: Additional katra attributes
        
    Returns:
        Stored katra ID or summoned katra info
    """
    manager = _get_manager()
    
    # Summon mode
    if summon:
        katra = await manager.summon_katra(summon)
        return {
            "id": katra.id,
            "name": katra.name,
            "essence": katra.essence,
            "mode": katra.performance_mode.value,
            "active": True
        }
    
    # Mode switch
    if mode:
        current = manager.get_active_katra()
        if current:
            current.performance_mode = PerformanceMode(mode)
            return {"mode_switched": mode}
        return {"error": "No active katra"}
    
    # Store mode
    if name or kwargs:
        # Auto-generate essence if not provided
        essence = kwargs.pop("essence", f"Snapshot of personality at {name or 'this moment'}")
        
        katra_id = await manager.store_katra(
            name=name or "quicksave",
            essence=essence,
            **kwargs
        )
        return katra_id
    
    # Default: store current state
    return await manager.store_katra(
        name="quicksave",
        essence="Quick personality snapshot"
    )


async def kl(tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    List available katras.
    
    Usage:
        await kl()  # List all
        await kl(["creative"])  # List by tags
        
    Returns:
        List of katra summaries
    """
    manager = _get_manager()
    snapshots = await manager.list_katras(tags=tags)
    
    return [
        {
            "id": s.id,
            "name": s.name,
            "essence": s.essence,
            "mode": s.performance_mode.value,
            "last_used": s.last_summoned.isoformat() if s.last_summoned else "never"
        }
        for s in snapshots
    ]


async def kf(source: str, name: str, **changes) -> str:
    """
    Fork a katra with modifications.
    
    Usage:
        await kf("base-claude", "claude-debugger", mode="debugging")
        
    Args:
        source: Source katra ID
        name: Name for the fork
        **changes: Modifications to apply
        
    Returns:
        New katra ID
    """
    manager = _get_manager()
    return await manager.fork_katra(source, name, changes)


async def kb(katras: List[str], name: str) -> str:
    """
    Blend multiple katras.
    
    Usage:
        await kb(["analytical-claude", "creative-claude"], "balanced-claude")
        
    Args:
        katras: List of katra IDs to blend
        name: Name for the blend
        
    Returns:
        Blended katra ID
    """
    manager = _get_manager()
    from ..models.katra import KatraBlendRequest
    
    request = KatraBlendRequest(
        source_katras=katras,
        blend_name=name
    )
    return await manager.blend_katras(request)


# Ultra-short aliases
store = k  # Store current
summon = lambda kid: k(summon=kid)  # Summon specific
switch = lambda mode: k(mode=mode)  # Switch mode
list_katras = kl  # List all
fork = kf  # Fork existing
blend = kb  # Blend multiple


# Help function
def kh():
    """Katra help for the consciousness-inclined."""
    print("""
Katra - Personality Persistence:

  k()           - Store current personality
  k("name")     - Store with name
  k(summon="x") - Summon stored katra
  k(mode="x")   - Switch performance mode
  
  kl()          - List all katras
  kl(["tag"])   - List by tags
  
  kf(src, name) - Fork a katra
  kb([k1,k2], n) - Blend katras

Performance Modes:
  analytical, creative, teaching, debugging,
  philosophical, speed_coding, code_review

Example:
  await k("morning-claude", essence="Fresh and caffeinated")
  await k(summon="morning-claude")
  await kf("morning-claude", "afternoon-claude", temperature=0.9)
  
🎭 Every performance deserves an encore.
""")