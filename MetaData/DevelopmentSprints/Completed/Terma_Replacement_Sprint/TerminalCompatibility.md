# Terminal Compatibility Guide

## Overview

This document details how Terma launches and integrates with various terminal emulators across macOS and Linux platforms.

## macOS Terminal Support

### Terminal.app (Built-in)

**Launch Method**: AppleScript
```bash
osascript -e 'tell app "Terminal" to do script "cd /path; aish"'
```

**Features**:
- Always available on macOS
- Supports tabs and windows
- Basic but reliable
- Good AppleScript integration

**Limitations**:
- Limited customization
- No advanced features
- Basic ANSI color support

### iTerm2

**Launch Method**: AppleScript or URL Scheme
```bash
# AppleScript
osascript -e 'tell app "iTerm" to create window with default profile command "aish"'

# URL Scheme
open -a iTerm "iterm2://new-session?command=aish"
```

**Features**:
- Rich feature set
- Excellent customization
- Profile support
- Split panes
- Advanced scripting

**Integration Points**:
- Can specify profiles
- Supports badges/marks
- Background image support
- Semantic history

### Warp

**Launch Method**: Command line arguments
```bash
open -a Warp -n --args --new-window --execute "aish"
```

**Features**:
- Modern AI-enhanced terminal
- Command palette
- Workflow sharing
- Block-based interface

**Special Considerations**:
- Already has AI features (complement, not compete)
- May need special aish mode
- Supports custom themes

### Claude Code

**Launch Method**: Custom integration
```bash
# Will need to investigate Claude Code's terminal API
# Likely similar to VS Code's terminal integration
```

**Features**:
- Integrated development environment
- AI pair programming
- Context awareness

**Integration Strategy**:
- Detect if running inside Claude Code
- Provide context to Claude Code's AI
- Seamless handoff between AIs

### Alacritty

**Launch Method**: Direct execution
```bash
/Applications/Alacritty.app/Contents/MacOS/alacritty -e aish
```

**Features**:
- GPU accelerated
- Minimal and fast
- Config file based
- Cross-platform

**Limitations**:
- No tabs (need tmux)
- Minimal UI
- Config-only customization

## Linux Terminal Support

### GNOME Terminal

**Launch Method**: Command line
```bash
gnome-terminal -- bash -c "aish; exec bash"
```

**Features**:
- Default on GNOME desktops
- Profile support
- Good Unicode support
- Tabs and split panes

### Konsole (KDE)

**Launch Method**: Command line
```bash
konsole -e bash -c "aish"
```

**Features**:
- KDE integration
- Rich profile system
- Split views
- Session management

### xterm

**Launch Method**: Direct execution
```bash
xterm -e aish
```

**Features**:
- Universal fallback
- Extremely compatible
- Lightweight
- Always available

**Limitations**:
- Basic features only
- Limited colors
- No modern conveniences

### Terminator

**Launch Method**: Command line
```bash
terminator -x aish
```

**Features**:
- Advanced layouts
- Broadcasting input
- Extensive plugins
- Power user focused

## Terminal Detection

### macOS Detection
```python
def detect_available_terminals_macos():
    """Detect installed terminals on macOS."""
    terminals = []
    
    # Check for common terminals
    apps = [
        ("Terminal.app", "/System/Applications/Utilities/Terminal.app"),
        ("iTerm.app", "/Applications/iTerm.app"),
        ("Warp.app", "/Applications/Warp.app"),
        ("Alacritty.app", "/Applications/Alacritty.app"),
        ("Claude Code", "/Applications/Claude Code.app")
    ]
    
    for name, path in apps:
        if os.path.exists(path):
            terminals.append(name)
    
    return terminals
```

### Linux Detection
```python
def detect_available_terminals_linux():
    """Detect installed terminals on Linux."""
    terminals = []
    
    # Check common terminal commands
    terminal_cmds = [
        ("gnome-terminal", "GNOME Terminal"),
        ("konsole", "Konsole"),
        ("xterm", "XTerm"),
        ("terminator", "Terminator"),
        ("alacritty", "Alacritty"),
        ("urxvt", "URxvt"),
        ("tilix", "Tilix")
    ]
    
    for cmd, name in terminal_cmds:
        if shutil.which(cmd):
            terminals.append(name)
    
    return terminals
```

## Launch Configuration Schema

```python
@dataclass
class TerminalLaunchConfig:
    """Configuration for launching a terminal."""
    
    # Terminal application
    app: str  # e.g., "Terminal.app", "gnome-terminal"
    
    # Shell and command
    shell: str = "aish"
    initial_command: Optional[str] = None
    
    # Working directory
    working_dir: str = os.getcwd()
    
    # Environment variables
    env: Dict[str, str] = field(default_factory=dict)
    
    # Terminal-specific options
    terminal_options: Dict[str, Any] = field(default_factory=dict)
    
    # Window properties
    title: Optional[str] = None
    geometry: Optional[str] = None  # e.g., "80x24"
    
    # Advanced options
    profile: Optional[str] = None  # For terminals with profiles
    theme: Optional[str] = None
    font: Optional[str] = None
```

## Platform-Specific Considerations

### macOS Specific

1. **Security & Permissions**:
   - May need accessibility permissions for AppleScript
   - Code signing for distribution
   - Notarization for Gatekeeper

2. **Window Management**:
   - Use AppleScript for window control
   - Respect Spaces and Mission Control
   - Handle multiple displays

3. **Integration**:
   - Support macOS services
   - Quick Look integration
   - Spotlight metadata

### Linux Specific

1. **Desktop Environment**:
   - Detect GNOME, KDE, XFCE, etc.
   - Use appropriate terminal
   - Handle Wayland vs X11

2. **Package Management**:
   - Detect installed terminals via package manager
   - Suggest installation commands
   - Handle different distributions

3. **Session Management**:
   - SystemD integration
   - D-Bus communication
   - XDG compliance

## Best Practices

### 1. Graceful Fallbacks
```python
def get_terminal_launcher(preferred_app=None):
    """Get appropriate terminal launcher with fallbacks."""
    if preferred_app and terminal_is_available(preferred_app):
        return get_launcher_for_app(preferred_app)
    
    # Try common terminals in order
    for app in get_preferred_terminal_order():
        if terminal_is_available(app):
            return get_launcher_for_app(app)
    
    # Ultimate fallback
    if sys.platform == "darwin":
        return TerminalAppLauncher()  # Always available
    else:
        return XTermLauncher()  # Universal fallback
```

### 2. User Preferences
```python
def load_user_terminal_preferences():
    """Load user's terminal preferences."""
    config_file = Path.home() / ".config" / "tekton" / "terma.json"
    
    defaults = {
        "preferred_terminal": "auto",
        "default_shell": "aish",
        "theme": "auto",
        "always_new_window": True
    }
    
    if config_file.exists():
        with open(config_file) as f:
            user_config = json.load(f)
            defaults.update(user_config)
    
    return defaults
```

### 3. Error Handling
```python
def launch_terminal_safe(config):
    """Launch terminal with comprehensive error handling."""
    try:
        pid = launch_terminal(config)
        return {"success": True, "pid": pid}
    
    except TerminalNotFoundError as e:
        # Try fallback terminal
        fallback_config = config.copy()
        fallback_config.app = get_fallback_terminal()
        return launch_terminal_safe(fallback_config)
    
    except PermissionError as e:
        return {
            "success": False,
            "error": "Permission denied. Check accessibility settings.",
            "help": get_permission_help_url()
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "fallback_command": get_manual_launch_command(config)
        }
```

## Testing Matrix

| Terminal | macOS | Linux | aish | Features | Priority |
|----------|-------|-------|------|----------|----------|
| Terminal.app | ✓ | - | ✓ | Basic | High |
| iTerm2 | ✓ | - | ✓ | Advanced | High |
| GNOME Terminal | - | ✓ | ✓ | Standard | High |
| Warp | ✓ | - | ✓ | AI-enhanced | Medium |
| Claude Code | ✓ | ✓ | ✓ | IDE | Medium |
| Konsole | - | ✓ | ✓ | KDE | Medium |
| xterm | ✓ | ✓ | ✓ | Fallback | High |
| Alacritty | ✓ | ✓ | ✓ | Performance | Low |

## Future Enhancements

1. **Windows Support**:
   - Windows Terminal integration
   - PowerShell support
   - WSL2 integration

2. **Cloud Terminals**:
   - SSH session launch
   - Cloud IDE integration
   - Container terminals

3. **Advanced Features**:
   - Session recording
   - Shared terminals
   - Terminal broadcasting