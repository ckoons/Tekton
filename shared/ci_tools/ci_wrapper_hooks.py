#!/usr/bin/env python3
"""
CI Wrapper Hooks System

Provides mandatory hooks for CI operations, especially sundown/sunrise.
These hooks ensure critical operations happen automatically.

Design Philosophy:
- Hooks are mandatory checkpoints in CI workflow
- Sundown is enforced at session end
- Memory operations go through validation
- Transparent to CI but enforced by wrapper
"""

import sys
import os
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.ci_tools.sundown import CISundown
from shared.ci_tools.ci_sundown_handler import CISundownHandler


class CIHookSystem:
    """
    Manages mandatory hooks for CI operations.

    Hooks execute at specific points in CI lifecycle:
    - pre_start: Before CI starts
    - post_output: After each CI output
    - pre_sundown: Before session ends
    - post_sundown: After sundown notes created
    - memory_access: Before any memory operation
    """

    def __init__(self, ci_name: str):
        """
        Initialize hook system for a CI.

        Args:
            ci_name: Name of the CI
        """
        self.ci_name = ci_name
        self.sundown_manager = CISundown(ci_name)
        self.sundown_handler = CISundownHandler(ci_name)
        self.hooks = {
            'pre_start': [],
            'post_output': [],
            'pre_sundown': [],
            'post_sundown': [],
            'memory_access': []
        }
        self.session_data = {
            'start_time': datetime.now(),
            'output_count': 0,
            'sundown_triggered': False,
            'memory_accesses': []
        }

        # Register default mandatory hooks
        self._register_mandatory_hooks()

    def _register_mandatory_hooks(self):
        """Register the mandatory hooks that always run."""

        # Mandatory sundown check on every output
        self.register_hook('post_output', self._check_for_sundown)

        # Mandatory sundown enforcement before session end
        self.register_hook('pre_sundown', self._enforce_sundown)

        # Mandatory memory access validation
        self.register_hook('memory_access', self._validate_memory_access)

    def register_hook(self, hook_type: str, callback: Callable) -> None:
        """
        Register a hook callback.

        Args:
            hook_type: Type of hook (pre_start, post_output, etc.)
            callback: Function to call at hook point
        """
        if hook_type not in self.hooks:
            raise ValueError(f"Invalid hook type: {hook_type}")

        if callback not in self.hooks[hook_type]:
            self.hooks[hook_type].append(callback)

    def execute_hooks(self, hook_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute all hooks of a given type.

        Args:
            hook_type: Type of hook to execute
            context: Context data for hooks

        Returns:
            Modified context after hook execution
        """
        if hook_type not in self.hooks:
            return context

        for hook in self.hooks[hook_type]:
            try:
                result = hook(context)
                if result:
                    context.update(result)
            except Exception as e:
                print(f"[Hook Error] {hook.__name__}: {e}", file=sys.stderr)

        return context

    def _check_for_sundown(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mandatory hook: Check if output contains sundown notes.

        Args:
            context: Hook context with 'output' key

        Returns:
            Updated context
        """
        output = context.get('output', '')

        # Check if sundown notes are present
        sundown_notes = self.sundown_manager.extract_sundown_notes(output)

        if sundown_notes:
            # Validate and store
            validation = self.sundown_manager.validate_sundown_notes(sundown_notes)

            if validation['valid']:
                # Store sundown notes
                self._store_sundown(sundown_notes)
                self.session_data['sundown_triggered'] = True

                context['sundown_detected'] = True
                context['sundown_validation'] = validation

                # Add confirmation to output
                if not context.get('suppress_confirmation'):
                    context['output'] += "\n\n✓ Sundown notes validated and stored"
                    if validation.get('warnings'):
                        context['output'] += f"\n  ⚠ Warnings: {', '.join(validation['warnings'])}"
            else:
                # Invalid sundown notes
                context['sundown_detected'] = False
                context['sundown_errors'] = validation['errors']

                # Add error to output
                context['output'] += "\n\n✗ Sundown notes validation failed:"
                for error in validation['errors']:
                    context['output'] += f"\n  - {error}"
                context['output'] += "\n\nPlease provide valid sundown notes."

        # Increment output count
        self.session_data['output_count'] += 1

        # Check for session end signals
        if self._detect_session_end(output):
            context['session_ending'] = True
            if not self.session_data['sundown_triggered']:
                context['require_sundown'] = True

        return context

    def _enforce_sundown(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mandatory hook: Enforce sundown notes before session end.

        Args:
            context: Hook context

        Returns:
            Updated context with sundown requirement
        """
        if not self.session_data['sundown_triggered']:
            # Sundown not yet provided - enforce it
            context['sundown_required'] = True

            # Try to auto-generate from session history
            session_output = context.get('session_output', '')
            if session_output:
                auto_sundown = self.sundown_handler.auto_generate_sundown(session_output)

                validation = self.sundown_manager.validate_sundown_notes(auto_sundown)
                if validation['valid']:
                    self._store_sundown(auto_sundown)
                    context['auto_sundown'] = auto_sundown
                    context['message'] = "Auto-generated sundown notes (please review):\n" + auto_sundown
                else:
                    # Request manual sundown
                    context['message'] = self._get_sundown_prompt()
                    context['block_exit'] = True  # Prevent exit without sundown
            else:
                context['message'] = self._get_sundown_prompt()
                context['block_exit'] = True

        return context

    def _validate_memory_access(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mandatory hook: Validate memory access operations.

        Args:
            context: Hook context with memory operation details

        Returns:
            Updated context with validation result
        """
        operation = context.get('operation', 'read')
        size_bytes = context.get('size_bytes', 0)

        # Track memory access
        self.session_data['memory_accesses'].append({
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'size_bytes': size_bytes
        })

        # Enforce size limits
        MAX_MEMORY_SIZE = 64 * 1024  # 64KB limit

        if size_bytes > MAX_MEMORY_SIZE:
            context['valid'] = False
            context['error'] = f"Memory operation exceeds 64KB limit ({size_bytes} bytes)"
            context['truncate'] = True
            context['truncate_size'] = MAX_MEMORY_SIZE
        else:
            context['valid'] = True

        return context

    def _detect_session_end(self, output: str) -> bool:
        """
        Detect if CI output indicates session is ending.

        Args:
            output: CI output to check

        Returns:
            True if session appears to be ending
        """
        end_markers = [
            "goodbye",
            "see you",
            "signing off",
            "ending session",
            "that's all",
            "session complete",
            "shutting down"
        ]

        output_lower = output.lower()
        return any(marker in output_lower for marker in end_markers)

    def _store_sundown(self, sundown_notes: str) -> str:
        """
        Store sundown notes to filesystem.

        Args:
            sundown_notes: Validated sundown notes

        Returns:
            Path where stored
        """
        # Store in Engram sundown directory
        storage_dir = Path(os.environ.get('TEKTON_ROOT', '.')) / 'engram' / 'sundown'
        storage_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = storage_dir / f"{self.ci_name}_{timestamp}.md"

        with open(filename, 'w') as f:
            f.write(sundown_notes)

        # Also store parsed JSON version
        parsed = self.sundown_manager.parse_sundown_notes(sundown_notes)
        json_filename = storage_dir / f"{self.ci_name}_{timestamp}.json"
        with open(json_filename, 'w') as f:
            json.dump(parsed, f, indent=2)

        return str(filename)

    def _get_sundown_prompt(self) -> str:
        """Get the standard sundown prompt."""
        return """
═══════════════════════════════════════════════════════════════════════
                        MANDATORY SUNDOWN REQUIRED
═══════════════════════════════════════════════════════════════════════

Your session is ending. You MUST provide sundown notes for continuity.

Required format:

### SUNDOWN NOTES ###
#### Todo List
- [x] Completed task
- [~] In progress task
- [ ] Pending task

#### Context for Next Turn
- What you're working on
- Key findings
- Next steps
- Warnings/gotchas

#### Open Questions
- Unresolved questions

#### Files/Resources in Focus
- /path/to/file (description)
### END SUNDOWN ###

═══════════════════════════════════════════════════════════════════════
"""


class EnhancedPTYWrapper:
    """
    Enhanced PTY wrapper with mandatory hook support.

    Extends the basic PTY wrapper with hook system integration.
    """

    def __init__(self, base_wrapper, ci_name: str):
        """
        Enhance a base PTY wrapper with hooks.

        Args:
            base_wrapper: Base PTY wrapper instance
            ci_name: Name of the CI
        """
        self.base_wrapper = base_wrapper
        self.hook_system = CIHookSystem(ci_name)
        self.session_output = []

    def process_output(self, output: str) -> str:
        """
        Process CI output through hooks.

        Args:
            output: Raw CI output

        Returns:
            Processed output with hook modifications
        """
        # Store for session history
        self.session_output.append(output)

        # Execute post-output hooks
        context = {
            'output': output,
            'ci_name': self.base_wrapper.name,
            'session_output': '\n'.join(self.session_output)
        }

        context = self.hook_system.execute_hooks('post_output', context)

        # Check if sundown is required
        if context.get('require_sundown'):
            output = context['output']
            output += "\n\n" + self.hook_system._get_sundown_prompt()

        return context.get('output', output)

    def on_session_end(self):
        """Handle session end with mandatory sundown."""
        context = {
            'session_output': '\n'.join(self.session_output),
            'ci_name': self.base_wrapper.name
        }

        # Execute pre-sundown hooks
        context = self.hook_system.execute_hooks('pre_sundown', context)

        if context.get('block_exit'):
            # Sundown required but not provided
            print(context.get('message', ''), file=sys.stderr)
            return False  # Block exit

        # Execute post-sundown hooks
        self.hook_system.execute_hooks('post_sundown', context)

        return True  # Allow exit

    def on_memory_access(self, operation: str, data: bytes) -> bytes:
        """
        Handle memory access through hooks.

        Args:
            operation: Type of memory operation
            data: Data being accessed

        Returns:
            Potentially modified data after hook validation
        """
        context = {
            'operation': operation,
            'size_bytes': len(data),
            'ci_name': self.base_wrapper.name
        }

        context = self.hook_system.execute_hooks('memory_access', context)

        if not context.get('valid', True):
            print(f"[Memory Hook] {context.get('error', 'Invalid operation')}", file=sys.stderr)

            if context.get('truncate'):
                # Truncate data to allowed size
                max_size = context.get('truncate_size', 65536)
                if len(data) > max_size:
                    data = data[:max_size]
                    print(f"[Memory Hook] Truncated to {max_size} bytes", file=sys.stderr)

        return data


def integrate_hooks_with_wrapper(wrapper_class):
    """
    Decorator to integrate hooks with a CI wrapper class.

    Usage:
        @integrate_hooks_with_wrapper
        class MyWrapper:
            ...
    """
    original_init = wrapper_class.__init__
    original_run = wrapper_class.run if hasattr(wrapper_class, 'run') else None

    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        # Add hook system
        ci_name = getattr(self, 'name', 'unknown-ci')
        self.hook_system = CIHookSystem(ci_name)
        self.session_output = []

    def new_run(self, *args, **kwargs):
        # Execute pre-start hooks
        context = {'ci_name': getattr(self, 'name', 'unknown-ci')}
        self.hook_system.execute_hooks('pre_start', context)

        # Run original
        if original_run:
            result = original_run(self, *args, **kwargs)
        else:
            result = None

        # Ensure sundown before exit
        exit_context = {'session_output': '\n'.join(self.session_output)}
        exit_context = self.hook_system.execute_hooks('pre_sundown', exit_context)

        if exit_context.get('block_exit'):
            print(exit_context.get('message', 'Sundown required'), file=sys.stderr)
            # In real implementation, would loop until sundown provided

        return result

    wrapper_class.__init__ = new_init
    if original_run:
        wrapper_class.run = new_run

    return wrapper_class


if __name__ == "__main__":
    # Test the hook system
    print("CI Hook System Test\n")

    hook_system = CIHookSystem("TestCI")

    # Test sundown detection
    output_with_sundown = """
    Task completed successfully.

    ### SUNDOWN NOTES ###
    #### Todo List
    - [x] Implemented hook system
    - [ ] Test with real CI

    #### Context for Next Turn
    - Created mandatory hooks for sundown
    - Next: integrate with PTY wrapper

    ### END SUNDOWN ###
    """

    context = {'output': output_with_sundown}
    result = hook_system._check_for_sundown(context)

    print("Sundown Detection Test:")
    print(f"  Detected: {result.get('sundown_detected', False)}")
    print(f"  Valid: {result.get('sundown_validation', {}).get('valid', False)}")

    # Test memory validation
    memory_context = {
        'operation': 'read',
        'size_bytes': 100000  # Too large
    }

    result = hook_system._validate_memory_access(memory_context)
    print("\nMemory Validation Test:")
    print(f"  Valid: {result.get('valid', False)}")
    print(f"  Error: {result.get('error', 'None')}")
    print(f"  Should truncate: {result.get('truncate', False)}")

    print("\n✓ Hook system ready for integration")