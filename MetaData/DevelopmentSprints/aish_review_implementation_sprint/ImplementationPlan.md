# AISH Review Implementation - Implementation Plan

## Overview

This document provides the detailed technical implementation plan for the AISH Review system. It breaks down the work into specific tasks and provides technical guidance for implementation.

## Implementation Components

### 1. Directory Structure Setup

**Location**: `$TEKTON_MAIN_ROOT/.tekton/terminal-sessions/`

**Tasks**:
- Create directory if it doesn't exist
- Set appropriate permissions (700 - user only)
- Add .gitignore to exclude session files from git

**Code Location**: `shared/aish/src/commands/review.py`

### 2. AISH Review Command Implementation

**File**: `shared/aish/src/commands/review.py`

**Class Structure**:
```python
class ReviewCommand:
    """Manages terminal session recording for analysis."""
    
    def __init__(self):
        self.session_dir = self._get_session_directory()
        self.current_session = None
        
    def start(self, terminal_name: str) -> None:
        """Start recording a terminal session."""
        
    def stop(self) -> None:
        """Stop recording and add metadata."""
        
    def list(self, days: int = 7) -> List[SessionInfo]:
        """List recent sessions."""
        
    def compress(self, older_than_hours: int = 24) -> None:
        """Compress old sessions."""
```

### 3. Session Recording Logic

**Start Recording**:
```python
def start(self, terminal_name: str) -> None:
    # Get terminal info from aish context
    terminal_info = self._get_terminal_info()
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{terminal_name}-{timestamp}.log"
    filepath = os.path.join(self.session_dir, filename)
    
    # Start script command
    cmd = ["script", "-q", filepath]
    
    # Store session info for stop command
    self.current_session = {
        "filepath": filepath,
        "start_time": datetime.now().isoformat(),
        "terminal_name": terminal_name,
        "terminal_purpose": terminal_info.get("purpose", ""),
        "terminal_role": terminal_info.get("role", "")
    }
```

**Stop Recording**:
```python
def stop(self) -> None:
    # Exit script (handled by shell)
    
    # Add metadata trailer
    metadata = {
        "start_time": self.current_session["start_time"],
        "end_time": datetime.now().isoformat(),
        "terminal_name": self.current_session["terminal_name"],
        "terminal_purpose": self.current_session["terminal_purpose"],
        "terminal_role": self.current_session["terminal_role"],
        "session_version": "1.0"
    }
    
    # Append to file
    with open(self.current_session["filepath"], "a") as f:
        f.write("\n[END OF SESSION]\n")
        f.write("--- TEKTON SESSION METADATA ---\n")
        f.write(json.dumps(metadata, indent=2))
        f.write("\n--- END METADATA ---\n")
```

### 4. Session Management Functions

**List Sessions**:
```python
def list(self, days: int = 7) -> List[Dict]:
    sessions = []
    cutoff = datetime.now() - timedelta(days=days)
    
    for filename in os.listdir(self.session_dir):
        if filename.endswith(('.log', '.log.gz')):
            filepath = os.path.join(self.session_dir, filename)
            stat = os.stat(filepath)
            
            if datetime.fromtimestamp(stat.st_mtime) > cutoff:
                # Parse metadata if needed
                sessions.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "compressed": filename.endswith('.gz')
                })
    
    return sorted(sessions, key=lambda x: x["modified"], reverse=True)
```

**Compress Old Sessions**:
```python
def compress(self, older_than_hours: int = 24) -> None:
    cutoff = datetime.now() - timedelta(hours=older_than_hours)
    
    for filename in os.listdir(self.session_dir):
        if filename.endswith('.log'):  # Not already compressed
            filepath = os.path.join(self.session_dir, filename)
            stat = os.stat(filepath)
            
            if datetime.fromtimestamp(stat.st_mtime) < cutoff:
                # Compress with gzip
                with open(filepath, 'rb') as f_in:
                    with gzip.open(f"{filepath}.gz", 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Preserve timestamp
                os.utime(f"{filepath}.gz", (stat.st_atime, stat.st_mtime))
                
                # Remove original
                os.remove(filepath)
```

### 5. Integration with AISH Command System

**Register Command**:
- Add to `shared/aish/src/commands/__init__.py`
- Follow existing command registration pattern

**Command Parser**:
```python
# In aish main command parser
elif args[0] == "review":
    review_cmd = ReviewCommand()
    
    if len(args) == 1:
        # Show help
        print("Usage: aish review [start|stop|list|compress]")
    elif args[1] == "start":
        review_cmd.start(terminal_name)
    elif args[1] == "stop":
        review_cmd.stop()
    elif args[1] == "list":
        sessions = review_cmd.list()
        # Format and display
    elif args[1] == "compress":
        review_cmd.compress()
```

### 6. Helper Functions

**Get Terminal Info**:
```python
def _get_terminal_info(self) -> Dict[str, str]:
    """Get current terminal's purpose and role from aish context."""
    # Implementation depends on how aish stores this info
    # May need to read from terma state or environment
    pass

def _get_session_directory(self) -> str:
    """Get the session storage directory."""
    main_root = os.environ.get('TEKTON_MAIN_ROOT')
    if not main_root:
        raise ValueError("TEKTON_MAIN_ROOT not set")
    
    session_dir = os.path.join(main_root, '.tekton', 'terminal-sessions')
    os.makedirs(session_dir, exist_ok=True, mode=0o700)
    
    return session_dir
```

### 7. Error Handling

**Key Error Cases**:
- TEKTON_MAIN_ROOT not set
- Script command not available
- Disk space issues
- Permission problems
- Corrupt session files

**Error Strategy**:
- Log errors with context
- Graceful degradation
- Clear error messages to user
- Never lose session data

### 8. Testing Strategy

**Unit Tests**:
- Metadata generation
- Filename generation
- Compression logic
- Directory creation

**Integration Tests**:
- Full session lifecycle
- Script command interaction
- File permissions
- Compression timing

**Test Utilities**:
```python
def create_mock_session(name: str, age_hours: int) -> str:
    """Create a mock session file for testing."""
    
def verify_metadata(filepath: str) -> Dict:
    """Parse and validate session metadata."""
```

## Implementation Order

1. **Phase 1 - Core** (Day 1):
   - Directory setup
   - Basic start/stop commands
   - Metadata generation
   - Integration with aish

2. **Phase 2 - Management** (Day 2):
   - List command
   - Compression logic
   - Error handling
   - Help documentation

3. **Phase 3 - Polish** (Day 3):
   - Comprehensive testing
   - Debug instrumentation
   - Documentation
   - Edge case handling

## Debug Instrumentation

Following Tekton guidelines:
```python
from shared.utils.debug_log import debug_log

@log_function
def start(self, terminal_name: str) -> None:
    debug_log("review", f"Starting session for {terminal_name}", "INFO")
    # ... implementation ...
    
@log_function  
def stop(self) -> None:
    debug_log("review", "Stopping session recording", "INFO")
    # ... implementation ...
```

## Future Hooks

**Extensibility Points**:
1. `sanitize_store()` - Placeholder for future sanitization
2. Metadata version handling in parsers
3. Additional metadata fields
4. Alternative storage backends
5. Real-time streaming to analysis

**Code Comments**:
```python
# TODO: Future hook for sanitization
# When implemented, call sanitize_store(filepath) here

# TODO: Future metadata fields
# Add new fields to metadata dict as needed
```

## Configuration

**Environment Variables**:
- `TEKTON_MAIN_ROOT` - Required for session storage
- `TEKTON_SESSION_COMPRESS_HOURS` - Optional, defaults to 24
- `TEKTON_SESSION_RETENTION_DAYS` - Optional, for future use

## Success Metrics

- All sessions captured completely
- Metadata correctly appended
- Compression reduces storage by >70%
- No data loss during any operation
- Clear error messages for all failure modes