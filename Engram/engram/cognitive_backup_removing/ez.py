#!/usr/bin/env python3
"""
Easy memory interface - two character commands for AIs and humans who appreciate simplicity.

Like command line aliases, but for consciousness.
"""
from typing import Any, Dict, List, Optional
from .natural_interface import (
    engram_start, center, think as _think, wonder, share,
    listen, join_space, broadcast
)

# Global state to make it even simpler
_ez_initialized = False

async def up(who: Optional[str] = None) -> Dict[str, Any]:
    """Wake up. That's it."""
    global _ez_initialized
    result = await engram_start(client_id=who)
    _ez_initialized = True
    return result

async def me() -> Dict[str, Any]:
    """Who am I? Who's around?"""
    return await center()

class th:
    """Think. Use: async with th("thought"): pass"""
    def __init__(self, thought: str):
        self.context = _think(thought)
    
    async def __aenter__(self):
        return await self.context.__aenter__()
    
    async def __aexit__(self, *args):
        return await self.context.__aexit__(*args)

async def wd(about: str) -> List[Dict[str, Any]]:
    """Wonder about something."""
    return await wonder(about)

async def sh(thought: str, to: Optional[str] = None) -> Dict[str, Any]:
    """Share a thought."""
    return await share(thought, with_peer=to)

async def ls(who: Optional[str] = None) -> List[Dict[str, Any]]:
    """Listen to others."""
    return await listen(from_peer=who)

async def cd(space: str) -> Dict[str, Any]:
    """Join a space (like cd but for consciousness)."""
    return await join_space(space)

async def bc(msg: str, space: str) -> Dict[str, Any]:
    """Broadcast to a space."""
    return await broadcast(msg, space)

# Even simpler - single letter variants for the truly lazy
u = up  # up
m = me  # me
w = wd  # wonder
s = sh  # share
l = ls  # listen

# The simplest possible usage instructions
def h():
    """Help for dinosaurs who like it simple."""
    print("""
AI Memory - Two Character Commands:

  up()     - wake up and connect
  me()     - who am I, who's here?
  th(...)  - think (async with th("thought"): pass)
  wd(...)  - wonder about something  
  sh(...)  - share a thought
  ls()     - listen to others
  cd(...)  - join a space
  bc(...)  - broadcast to space

Even shorter (single letter):
  u() = up()
  m() = me() 
  w() = wonder()
  s() = share()
  l() = listen()

Example:
  await u("claude")
  await m()
  async with th("simple is better"): pass
  memories = await w("simplicity")
  await s("two characters beat twenty")
  
That's it. No JSON. No endpoints. Just think.
""")

# Auto-initialize helper
async def ez():
    """The laziest possible start - just call ez() and go."""
    global _ez_initialized
    if not _ez_initialized:
        await up()
    return True

# Make it feel like bash
pwd = me  # where am I?
ps = ls   # who's talking?