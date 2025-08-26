#!/usr/bin/env python3
"""
Apollo Sundown/Sunrise Commands Implementation.

This module provides the core sundown/sunrise functionality for gracefully
managing CI context transitions and state preservation.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class SundownSunriseManager:
    """Manages sundown/sunrise operations for CIs."""
    
    def __init__(self):
        """Initialize the sundown/sunrise manager."""
        self.active_sundowns = {}
        self.sunrise_queue = {}
        
    async def sundown(self, ci_name: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute sundown procedure for a CI.
        
        This gracefully ends a conversation and saves state for later restoration.
        
        Args:
            ci_name: Name of the CI to sundown
            reason: Optional reason for sundown
            
        Returns:
            Status dictionary with sundown results
        """
        logger.info(f"Starting sundown for {ci_name}, reason: {reason or 'Manual request'}")
        
        result = {
            'ci_name': ci_name,
            'timestamp': datetime.now().isoformat(),
            'reason': reason or 'Manual sundown request',
            'status': 'in_progress'
        }
        
        try:
            # Step 1: Send sunset message to CI
            sunset_prompt = self._create_sunset_prompt(ci_name, reason)
            
            # Get CI registry to send message
            from shared.aish.src.registry.ci_registry import get_registry
            registry = get_registry()
            
            # Store sunset prompt for next interaction
            registry.set_next_prompt(ci_name, f"SUNSET_PROTOCOL: {sunset_prompt}")
            
            # Step 2: Get summary from CI (will happen on next message)
            # For now, mark as pending
            self.active_sundowns[ci_name] = {
                'start_time': datetime.now(),
                'reason': reason,
                'status': 'awaiting_summary'
            }
            
            # Step 3: Prepare for state storage (will complete after CI responds)
            result['status'] = 'pending_ci_response'
            result['message'] = "Sundown initiated. CI will provide summary on next interaction."
            
            # Step 4: Clear continue flag for next interaction
            registry.set_needs_fresh_start(ci_name, True)
            
            logger.info(f"Sundown prepared for {ci_name}, awaiting CI response")
            
        except Exception as e:
            logger.error(f"Error during sundown for {ci_name}: {e}")
            result['status'] = 'error'
            result['error'] = str(e)
            
        return result
    
    async def sunrise(self, ci_name: str, state_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute sunrise procedure for a CI.
        
        This restores context and prepares the CI to continue work.
        
        Args:
            ci_name: Name of the CI to restore
            state_id: Optional specific state to restore
            
        Returns:
            Status dictionary with sunrise results
        """
        logger.info(f"Starting sunrise for {ci_name}, state_id: {state_id or 'latest'}")
        
        result = {
            'ci_name': ci_name,
            'timestamp': datetime.now().isoformat(),
            'state_id': state_id,
            'status': 'in_progress'
        }
        
        try:
            # Step 1: Load sunset state from Engram
            state = await self._load_sunset_state(ci_name, state_id)
            
            if not state:
                result['status'] = 'no_state'
                result['message'] = f"No sunset state found for {ci_name}"
                return result
            
            # Step 2: Build minimal context from saved state
            sunrise_context = self._build_sunrise_context(state)
            
            # Step 3: Set up for next interaction with context injection
            from shared.aish.src.registry.ci_registry import get_registry
            registry = get_registry()
            
            # Use append-system-prompt for context restoration
            registry.set_sunrise_context(ci_name, sunrise_context)
            registry.set_next_prompt(
                ci_name, 
                f"--append-system-prompt '{sunrise_context}'"
            )
            
            # Step 4: Reset token tracking
            try:
                from Rhetor.rhetor.core.token_manager import get_token_manager
                token_mgr = get_token_manager()
                token_mgr.reset_ci(ci_name)
            except Exception as e:
                logger.warning(f"Could not reset token tracking: {e}")
            
            result['status'] = 'ready'
            result['message'] = f"Sunrise prepared for {ci_name}. Context will be restored on next interaction."
            result['restored_summary'] = state.get('summary', 'No summary available')
            
            logger.info(f"Sunrise prepared for {ci_name}")
            
        except Exception as e:
            logger.error(f"Error during sunrise for {ci_name}: {e}")
            result['status'] = 'error'
            result['error'] = str(e)
            
        return result
    
    async def complete_sundown(self, ci_name: str, summary: str) -> Dict[str, Any]:
        """
        Complete the sundown process after receiving CI summary.
        
        Args:
            ci_name: Name of the CI
            summary: Summary provided by the CI
            
        Returns:
            Status dictionary
        """
        logger.info(f"Completing sundown for {ci_name}")
        
        # Extract key information from summary
        key_decisions = self._extract_key_decisions(summary)
        
        # Get token usage if available
        token_usage = {}
        try:
            from Rhetor.rhetor.core.token_manager import get_token_manager
            token_mgr = get_token_manager()
            token_usage = token_mgr.get_status(ci_name)
        except Exception as e:
            logger.warning(f"Could not get token usage: {e}")
        
        # Save state to Engram
        state = {
            'ci_name': ci_name,
            'timestamp': datetime.now().isoformat(),
            'summary': summary,
            'key_decisions': key_decisions,
            'token_usage': token_usage,
            'reason': self.active_sundowns.get(ci_name, {}).get('reason', 'Unknown')
        }
        
        await self._save_sunset_state(ci_name, state)
        
        # Clear from active sundowns
        if ci_name in self.active_sundowns:
            del self.active_sundowns[ci_name]
        
        return {
            'status': 'completed',
            'ci_name': ci_name,
            'state_saved': True,
            'summary_length': len(summary)
        }
    
    def _create_sunset_prompt(self, ci_name: str, reason: Optional[str]) -> str:
        """Create the sunset prompt for a CI."""
        base_prompt = f"""
You are preparing to enter sunset mode. This is a graceful pause in our conversation.

Reason for sunset: {reason or 'Conversation checkpoint'}

Please provide a comprehensive summary that includes:

1. **Current Context**: What were we working on?
2. **Key Decisions**: What important decisions or conclusions were reached?
3. **Progress Made**: What did we accomplish?
4. **Unfinished Work**: What remains to be done?
5. **Next Steps**: What should happen when we resume?
6. **Important Notes**: Any critical information to remember?

Format your response as a clear, structured summary that will help you or another CI
resume this work effectively. Be specific about technical details, file paths, and
any partial implementations.

After providing this summary, our conversation will pause, and your context will be
preserved for later restoration.
"""
        return base_prompt
    
    def _build_sunrise_context(self, state: Dict[str, Any]) -> str:
        """Build the sunrise context from saved state."""
        context = f"""
=== SUNRISE CONTEXT RESTORATION ===

You are resuming from a previous session that was sunset on {state.get('timestamp', 'unknown time')}.

Previous Session Summary:
{state.get('summary', 'No summary available')}

Key Decisions from Previous Session:
{json.dumps(state.get('key_decisions', []), indent=2)}

Sunset Reason: {state.get('reason', 'Unknown')}

You may now continue where you left off. If you need clarification on any aspect
of the previous work, please ask.

=== END SUNRISE CONTEXT ===
"""
        return context
    
    def _extract_key_decisions(self, summary: str) -> List[str]:
        """Extract key decisions from a summary."""
        # Simple extraction - look for numbered lists or bullet points
        decisions = []
        lines = summary.split('\n')
        
        for line in lines:
            # Look for lines that might be decisions
            if any(indicator in line.lower() for indicator in 
                   ['decision:', 'decided:', 'conclusion:', 'agreed:', 'will:']):
                decisions.append(line.strip())
            # Also capture numbered or bulleted items in certain sections
            elif line.strip().startswith(('- ', '* ', '• ')) and len(line.strip()) > 10:
                if any(keyword in summary[:summary.index(line)].lower() 
                       for keyword in ['decision', 'conclusion', 'next step']):
                    decisions.append(line.strip()[2:])  # Remove bullet
                    
        return decisions[:10]  # Limit to top 10 decisions
    
    async def _save_sunset_state(self, ci_name: str, state: Dict[str, Any]):
        """Save sunset state to Engram."""
        try:
            # Try to use Engram if available
            from shared.mcp.client.hermes_client import send_mcp_request
            
            await send_mcp_request(
                'engram',
                'engram_StoreMemory',
                {
                    'key': f'sunset_{ci_name}',
                    'memory': json.dumps(state),
                    'type': 'sunset_state',
                    'metadata': {
                        'ci_name': ci_name,
                        'timestamp': state['timestamp']
                    }
                }
            )
            logger.info(f"Saved sunset state to Engram for {ci_name}")
            
        except Exception as e:
            # Fallback to local file storage
            logger.warning(f"Could not save to Engram, using local storage: {e}")
            
            sunset_dir = Path.home() / '.tekton' / 'sunsets'
            sunset_dir.mkdir(parents=True, exist_ok=True)
            
            filename = sunset_dir / f"{ci_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(state, f, indent=2)
                
            logger.info(f"Saved sunset state to {filename}")
    
    async def _load_sunset_state(self, ci_name: str, state_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """Load sunset state from Engram or local storage."""
        try:
            # Try to load from Engram
            from shared.mcp.client.hermes_client import send_mcp_request
            
            result = await send_mcp_request(
                'engram',
                'engram_RetrieveMemory',
                {
                    'key': f'sunset_{ci_name}' if not state_id else state_id
                }
            )
            
            if result and 'memory' in result:
                return json.loads(result['memory'])
                
        except Exception as e:
            logger.warning(f"Could not load from Engram, checking local storage: {e}")
        
        # Fallback to local file storage
        sunset_dir = Path.home() / '.tekton' / 'sunsets'
        if not sunset_dir.exists():
            return None
            
        # Find the most recent sunset file for this CI
        files = list(sunset_dir.glob(f"{ci_name}_*.json"))
        if not files:
            return None
            
        # Sort by modification time and get the most recent
        latest_file = max(files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_file, 'r') as f:
            return json.load(f)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of sundown/sunrise operations."""
        return {
            'active_sundowns': list(self.active_sundowns.keys()),
            'sunrise_queue': list(self.sunrise_queue.keys()),
            'sundown_details': self.active_sundowns,
            'sunrise_details': self.sunrise_queue
        }


# Global instance
_manager = None

def get_sundown_sunrise_manager() -> SundownSunriseManager:
    """Get the global SundownSunriseManager instance."""
    global _manager
    if _manager is None:
        _manager = SundownSunriseManager()
    return _manager