#!/usr/bin/env python3
"""
Transparent Landmark Hooks - Quantum Observation Without Collapse

Instruments the seams of the system without touching core logic.
Like placing sensors at doorways rather than inside rooms.
"""

import sys
import json
import asyncio
from pathlib import Path
from functools import wraps
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Optional, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from shared.landmarks import LandmarkRegistry

# =============================================================================
# DECORATOR PATTERN - Wrap functions transparently
# =============================================================================

class landmark:
    """Transparent landmark decorator system"""
    
    @staticmethod
    def auto(landmark_type: str, **context):
        """Auto-drop landmarks without changing function logic"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Capture entry
                LandmarkRegistry.fire(f"{landmark_type}_started", {
                    "function": func.__name__,
                    "component": func.__module__.split('.')[0],
                    **context
                })
                
                try:
                    result = await func(*args, **kwargs)
                    
                    # Capture success
                    LandmarkRegistry.fire(f"{landmark_type}_completed", {
                        "function": func.__name__,
                        "success": True,
                        **context
                    })
                    
                    return result
                    
                except Exception as e:
                    # Capture failure
                    LandmarkRegistry.fire(f"{landmark_type}_failed", {
                        "function": func.__name__,
                        "error": str(e),
                        **context
                    })
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Capture entry
                LandmarkRegistry.fire(f"{landmark_type}_started", {
                    "function": func.__name__,
                    "component": func.__module__.split('.')[0] if func.__module__ else "unknown",
                    **context
                })
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Capture success
                    LandmarkRegistry.fire(f"{landmark_type}_completed", {
                        "function": func.__name__,
                        "success": True,
                        **context
                    })
                    
                    return result
                    
                except Exception as e:
                    # Capture failure
                    LandmarkRegistry.fire(f"{landmark_type}_failed", {
                        "function": func.__name__,
                        "error": str(e),
                        **context
                    })
                    raise
            
            # Return appropriate wrapper
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
                
        return decorator
    
    @staticmethod
    @contextmanager
    def decision(decision_name: str, **context):
        """Context manager for decision points"""
        # Mark decision entry
        LandmarkRegistry.fire("decision_point_entered", {
            "decision": decision_name,
            "timestamp": datetime.now().isoformat(),
            **context
        })
        
        try:
            yield
            
            # Mark decision success
            LandmarkRegistry.fire("decision_made", {
                "decision": decision_name,
                "outcome": "completed",
                **context
            })
            
        except Exception as e:
            # Mark decision failure
            LandmarkRegistry.fire("decision_failed", {
                "decision": decision_name,
                "error": str(e),
                **context
            })
            raise


# =============================================================================
# FILE WATCHER - Monitor directories transparently
# =============================================================================

class LandmarkFileWatcher(FileSystemEventHandler):
    """Watches directories and drops landmarks on file events"""
    
    def __init__(self, component_name: str):
        self.component = component_name
        self.watched_patterns = {
            "proposal": r".*\.json$",
            "sprint_plan": r"SPRINT_PLAN\.md$",
            "daily_log": r"DAILY_LOG\.md$",
            "python": r".*\.py$",
            "markdown": r".*\.md$"
        }
    
    def detect_file_type(self, path: str) -> str:
        """Detect what type of file this is"""
        path_str = str(path)
        
        if "Proposals" in path_str:
            return "proposal"
        elif "Sprint" in path_str:
            if "SPRINT_PLAN" in path_str:
                return "sprint_plan"
            elif "DAILY_LOG" in path_str:
                return "daily_log"
            return "sprint_file"
        elif path_str.endswith('.py'):
            return "python_code"
        elif path_str.endswith('.md'):
            return "documentation"
        
        return "unknown"
    
    def on_created(self, event):
        """File created - major landmark"""
        if event.is_directory:
            return
            
        file_type = self.detect_file_type(event.src_path)
        
        LandmarkRegistry.fire("file_created", {
            "component": self.component,
            "path": event.src_path,
            "type": file_type,
            "timestamp": datetime.now().isoformat(),
            "triggers": self._get_interested_cis(file_type)
        })
    
    def on_modified(self, event):
        """File modified - minor landmark"""
        if event.is_directory:
            return
            
        file_type = self.detect_file_type(event.src_path)
        
        # Only landmark significant files
        if file_type in ["proposal", "sprint_plan", "daily_log"]:
            LandmarkRegistry.fire("file_modified", {
                "component": self.component,
                "path": event.src_path,
                "type": file_type,
                "timestamp": datetime.now().isoformat()
            })
    
    def on_deleted(self, event):
        """File deleted - important landmark"""
        if event.is_directory:
            return
            
        file_type = self.detect_file_type(event.src_path)
        
        LandmarkRegistry.fire("file_deleted", {
            "component": self.component,
            "path": event.src_path,
            "type": file_type,
            "timestamp": datetime.now().isoformat(),
            "alert": "deletion_event"
        })
    
    def on_moved(self, event):
        """File moved - transition landmark"""
        if event.is_directory:
            return
            
        LandmarkRegistry.fire("file_moved", {
            "component": self.component,
            "from": event.src_path,
            "to": event.dest_path,
            "timestamp": datetime.now().isoformat(),
            "meaning": self._interpret_move(event.src_path, event.dest_path)
        })
    
    def _get_interested_cis(self, file_type: str) -> list:
        """Which CIs care about this file type"""
        interests = {
            "proposal": ["Telos", "Prometheus", "Metis"],
            "sprint_plan": ["Prometheus", "Metis", "Harmonia"],
            "daily_log": ["TektonCore", "Synthesis"],
            "python_code": ["Harmonia", "Ergon"],
            "documentation": ["Noesis", "Sophia"]
        }
        return interests.get(file_type, ["Numa"])
    
    def _interpret_move(self, from_path: str, to_path: str) -> str:
        """Interpret what a file move means"""
        if "Proposals" in from_path and "Sprints" in to_path:
            return "proposal_archived_for_sprint"
        elif "Completed" in to_path:
            return "work_completed"
        elif "Archive" in to_path:
            return "archived"
        return "relocated"


# =============================================================================
# EXCEPTION HOOK - Capture all error recovery
# =============================================================================

def landmark_exception_hook(exc_type, exc_value, exc_traceback):
    """Global exception hook for landmark dropping"""
    
    # Don't landmark KeyboardInterrupt
    if exc_type == KeyboardInterrupt:
        return sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    # Drop error landmark
    LandmarkRegistry.fire("exception_caught", {
        "type": exc_type.__name__,
        "message": str(exc_value),
        "file": exc_traceback.tb_frame.f_code.co_filename if exc_traceback else "unknown",
        "line": exc_traceback.tb_lineno if exc_traceback else 0,
        "severity": "error",
        "timestamp": datetime.now().isoformat()
    })
    
    # Call original handler
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


# =============================================================================
# API MIDDLEWARE - Thin layer for component communication
# =============================================================================

class LandmarkAPIMiddleware:
    """Transparent API call tracking"""
    
    def __init__(self, component_name: str):
        self.component = component_name
    
    async def __call__(self, request, call_next):
        """FastAPI middleware for landmark dropping"""
        
        # Capture API call start
        LandmarkRegistry.fire("api_call_received", {
            "component": self.component,
            "endpoint": request.url.path,
            "method": request.method,
            "from": request.client.host if request.client else "unknown",
            "timestamp": datetime.now().isoformat()
        })
        
        try:
            # Process request
            response = await call_next(request)
            
            # Capture success
            LandmarkRegistry.fire("api_call_completed", {
                "component": self.component,
                "endpoint": request.url.path,
                "status": response.status_code,
                "success": 200 <= response.status_code < 300
            })
            
            return response
            
        except Exception as e:
            # Capture API failure
            LandmarkRegistry.fire("api_call_failed", {
                "component": self.component,
                "endpoint": request.url.path,
                "error": str(e)
            })
            raise


# =============================================================================
# SIMPLE SETUP - One function to enable all hooks
# =============================================================================

def enable_transparent_landmarks(component_name: str, watch_dirs: list = None):
    """Enable all transparent landmark hooks for a component"""
    
    print(f"🏔️ Enabling transparent landmarks for {component_name}")
    
    # 1. Install exception hook
    sys.excepthook = landmark_exception_hook
    print("  ✓ Exception hook installed")
    
    # 2. Start file watchers if directories provided
    if watch_dirs:
        observer = Observer()
        handler = LandmarkFileWatcher(component_name)
        
        for directory in watch_dirs:
            if Path(directory).exists():
                observer.schedule(handler, directory, recursive=True)
                print(f"  ✓ Watching {directory}")
        
        observer.start()
        print("  ✓ File watchers active")
        
        return observer  # Return so caller can stop it later
    
    return None


# =============================================================================
# USAGE EXAMPLE
# =============================================================================

if __name__ == "__main__":
    # Example: Transparent Telos instrumentation
    
    # 1. Enable all hooks
    watcher = enable_transparent_landmarks(
        "telos",
        watch_dirs=[
            "/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Proposals",
            "/Users/cskoons/projects/github/Tekton/Telos"
        ]
    )
    
    # 2. Example function with transparent landmark
    @landmark.auto("proposal_creation")
    def create_proposal(name: str, data: dict):
        """This function doesn't know it's being watched"""
        # Normal logic here
        return {"name": name, "data": data}
    
    # 3. Example decision point
    def process_proposal(proposal):
        """Decision logic with landmark context"""
        
        with landmark.decision("ui_architecture_choice"):
            if "dashboard" in proposal.get("purpose", ""):
                architecture = "css_first"
            else:
                architecture = "component_based"
        
        return architecture
    
    # Test it
    print("\n🧪 Testing transparent landmarks...")
    
    # This drops landmarks automatically
    result = create_proposal("TestDashboard", {"purpose": "Test landmarks"})
    print(f"Created: {result}")
    
    # This captures the decision
    arch = process_proposal({"purpose": "dashboard for testing"})
    print(f"Architecture chosen: {arch}")
    
    # Query what was captured
    print("\n🔍 Captured landmarks:")
    recent = LandmarkRegistry.query()
    for landmark in recent[-5:]:
        print(f"  - {landmark}")
    
    # Clean up
    if watcher:
        watcher.stop()
        watcher.join()