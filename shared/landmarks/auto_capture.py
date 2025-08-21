#!/usr/bin/env python3
"""
Automatic Landmark Capture System
Minimal, non-invasive hooks for deterministic landmark generation.

Philosophy: Instrument the seams, not the logic.
The code shouldn't know it's being watched.
"""

import os
from shared.env import TektonEnviron
import sys
import json
import functools
import traceback
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional, Callable
from contextlib import contextmanager

class AutoLandmark:
    """Automatic landmark capture with minimal intrusion."""
    
    def __init__(self, registry_path: Optional[Path] = None):
        self.registry_path = registry_path or Path("/tmp/landmarks.json")
        self.landmarks = []
        self.enabled = TektonEnviron.get('LANDMARKS_ENABLED', '1') == '1'
    
    def emit(self, landmark_type: str, context: Dict[str, Any], 
             audience: str = 'local') -> None:
        """
        Emit a landmark with context and audience level.
        
        Audience levels:
        - 'local': This function/file only
        - 'component': This service (e.g., Telos)
        - 'project': This Tekton instance
        - 'federation': All connected Tekton instances
        - Custom groups: 'ui-specialists', 'planning-team', etc.
        """
        if not self.enabled:
            return
            
        landmark = {
            'type': landmark_type,
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'audience': audience,
            'instance_id': TektonEnviron.get('TEKTON_INSTANCE_ID', 'local'),
            'stack': self._get_stack_context()
        }
        
        self.landmarks.append(landmark)
        self._persist_landmark(landmark)
        
        # If audience is beyond local, prepare for propagation
        if audience != 'local':
            self._queue_for_propagation(landmark)
    
    def auto(self, landmark_type: str = 'function_call'):
        """Decorator for automatic function landmarks."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Capture entry
                self.emit(f'{landmark_type}:entry', {
                    'function': func.__name__,
                    'module': func.__module__,
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys())
                })
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Capture successful exit
                    self.emit(f'{landmark_type}:success', {
                        'function': func.__name__,
                        'has_result': result is not None
                    })
                    
                    return result
                    
                except Exception as e:
                    # Capture error
                    self.emit(f'{landmark_type}:error', {
                        'function': func.__name__,
                        'error_type': type(e).__name__,
                        'error_msg': str(e)
                    })
                    raise
                    
            return wrapper
        return decorator
    
    @contextmanager
    def decision(self, decision_name: str, reason: Optional[str] = None):
        """Context manager for decision point landmarks."""
        context = {
            'decision': decision_name,
            'reason': reason
        }
        
        self.emit('decision:considering', context)
        
        try:
            yield self
            self.emit('decision:made', context)
        except Exception as e:
            context['error'] = str(e)
            self.emit('decision:failed', context)
            raise
    
    def watch_file(self, filepath: Path, event_type: str) -> None:
        """Emit landmark for file system events."""
        self.emit(f'file:{event_type}', {
            'path': str(filepath),
            'exists': filepath.exists(),
            'is_dir': filepath.is_dir() if filepath.exists() else False,
            'size': filepath.stat().st_size if filepath.exists() and filepath.is_file() else 0
        })
    
    def api_call(self, source: str, target: str, endpoint: str, method: str = 'GET') -> None:
        """Emit landmark for API interactions."""
        self.emit('api:call', {
            'source': source,
            'target': target,
            'endpoint': endpoint,
            'method': method
        }, audience='component')  # API calls visible at component level
    
    def _queue_for_propagation(self, landmark: Dict[str, Any]) -> None:
        """Queue landmark for propagation based on audience."""
        # In full implementation, this would:
        # 1. Check till config for propagation rules
        # 2. Queue to appropriate channels (component bus, federation relay, etc.)
        # 3. Handle peer group routing
        pass
    
    def _get_stack_context(self) -> Dict[str, Any]:
        """Get minimal stack context for landmark."""
        frame = sys._getframe(3)  # Skip internal frames
        return {
            'file': frame.f_code.co_filename,
            'line': frame.f_lineno,
            'function': frame.f_code.co_name
        }
    
    def _persist_landmark(self, landmark: Dict[str, Any]) -> None:
        """Persist landmark to registry (append-only for performance)."""
        try:
            with open(self.registry_path, 'a') as f:
                f.write(json.dumps(landmark) + '\n')
        except:
            # Silent failure - landmarks shouldn't break the system
            pass


# Global instance for easy access
landmark = AutoLandmark()


# Hook for exception handling
def exception_hook(exc_type, exc_value, exc_traceback):
    """Global exception hook to capture error recovery."""
    landmark.emit('error:unhandled', {
        'type': exc_type.__name__,
        'message': str(exc_value),
        'file': exc_traceback.tb_frame.f_code.co_filename,
        'line': exc_traceback.tb_lineno
    })
    
    # Call original hook
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


# Install exception hook if enabled
if landmark.enabled:
    sys.excepthook = exception_hook


# Example usage patterns
if __name__ == '__main__':
    # Example 1: Automatic function decoration
    @landmark.auto('state_transition')
    def convert_proposal_to_sprint(proposal_name: str) -> Dict:
        """Example function with automatic landmarks."""
        return {'status': 'converted', 'name': proposal_name}
    
    # Example 2: Decision context
    with landmark.decision('choose_ui_framework', reason='CSS-first approach'):
        framework = 'none'  # CSS-only
    
    # Example 3: File operation
    proposal_path = Path('/tmp/test_proposal.json')
    landmark.watch_file(proposal_path, 'created')
    
    # Example 4: API boundary
    landmark.api_call('telos', 'prometheus', '/api/v1/proposals', 'POST')
    
    print(f"Landmarks captured: {len(landmark.landmarks)}")
    print(f"Registry at: {landmark.registry_path}")