# Terma UI Design

## Overview

Terma's UI follows the established Numa/Noesis pattern with a four-tab interface, unified chat input, and minimal JavaScript. The design emphasizes simplicity and functionality for terminal orchestration.

## Visual Design

### Color Scheme
- **Primary**: Deep Teal (#00695C) - Represents terminal/command line
- **Accent**: Bright Cyan (#00BCD4) - For active elements
- **Background**: Dark theme compatible
- **Status Colors**: 
  - Running: Green (#4CAF50)
  - Stopped: Gray (#757575)
  - Error: Red (#F44336)

### Component Structure

```
┌─────────────────────────────────────────────────────────────┐
│ [🔷] Terma                            [●] Connected          │
│      Terminal Orchestrator                                   │
├─────────────────────────────────────────────────────────────┤
│ Dashboard │ Launch Terminal │ Terminal Chat │ Team Chat     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    [Tab Content Area]                       │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ > [Input field................................] [Send]      │
└─────────────────────────────────────────────────────────────┘
```

## Tab Designs

### 1. Dashboard Tab

Shows active terminals in a clean table format:

```
Active Terminals
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PID     Name                  App           Status    Actions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
12345   Development Shell     Terminal.app  ● Running  [Show] [X]
12367   React Project         Warp.app      ● Running  [Show] [X]
12489   Data Analysis        iTerm2        ● Running  [Show] [X]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Refresh] [Clear Stopped]
```

### 2. Launch Terminal Tab

Configuration form with template selection:

```
Launch New Terminal
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Template: [Default Terminal    ▼]
          • Default Terminal
          • Development Setup
          • Data Science
          • Claude Code Session
          • Custom...

Terminal App: [Terminal.app     ▼]

Name: [_________________________________]

Working Directory: [________________________] [Browse]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Environment Variables:
┌─────────────────────────────────────┬───────────────────┐
│ TEKTON_MODE=development             │                [X] │
│ NODE_ENV=development                │                [X] │
│ [Add new...]                        │                    │
└─────────────────────────────────────┴───────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Initial Context (for aish):
┌────────────────────────────────────────────────────────┐
│ Setting up React development environment...            │
│                                                        │
└────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Initial Commands:
┌────────────────────────────────────────────────────────┐
│ cd ~/projects/my-app                                   │
│ npm install                                            │
│                                                        │
└────────────────────────────────────────────────────────┘

                    [✓ Save as Template]  [Launch Terminal]
```

### 3. Terminal Chat Tab

Direct communication with specific terminal's aish:

```
Terminal Chat
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Active Terminal: [Development Shell (12345) ▼]

┌────────────────────────────────────────────────────────┐
│ You: Show me what's running on port 3000              │
│                                                        │
│ aish: I'll check what's using port 3000...           │
│       $ lsof -i :3000                                 │
│                                                        │
│ COMMAND   PID USER   FD   TYPE             DEVICE    │
│ node    45123 user   23u  IPv4 0x7f9b0d0      TCP    │
│                                                        │
│ You: Kill that process please                         │
│                                                        │
│ aish: I'll terminate the process on port 3000        │
│       This will stop the Node.js server. Proceed?    │
│       $ kill -TERM 45123                              │
│                                                        │
│ Process terminated successfully.                       │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 4. Team Chat Tab

Shared Rhetor team collaboration (borrowed from Numa/Noesis):

```
Team Chat
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌────────────────────────────────────────────────────────┐
│ Athena: I've discovered a new pattern in the codebase │
│         related to terminal management...              │
│                                                        │
│ You: Can you help me set up a terminal for testing?  │
│                                                        │
│ Terma: I can launch a terminal for you. What kind    │
│        of testing environment do you need?            │
│                                                        │
│ You: Node.js testing with Jest                        │
│                                                        │
│ Terma: Launching terminal with Node.js test setup... │
│        Terminal PID: 12567                           │
│                                                        │
└────────────────────────────────────────────────────────┘
```

## Interaction Patterns

### Unified Input Routing
- Single input field at bottom
- Routes based on active tab:
  - Dashboard: Quick commands (refresh, clear)
  - Launch: Validates and submits form
  - Terminal Chat: Sends to selected terminal's aish
  - Team Chat: Broadcasts to Rhetor team

### Status Indicators
- Connection status in header
- Terminal status dots in dashboard
- Real-time updates via polling

### Terminal Actions
- **Show**: Brings terminal window to front
- **Terminate**: Gracefully closes terminal
- **Refresh**: Updates terminal list
- **Clear Stopped**: Removes terminated entries

## CSS Architecture

Following the established pattern:

```css
/* Component-specific styles */
.terma {
  --terma-primary: #00695C;
  --terma-accent: #00BCD4;
  --terma-running: #4CAF50;
  --terma-stopped: #757575;
  --terma-error: #F44336;
}

.terma__tab--active {
  border-bottom: 2px solid var(--terma-accent);
}

.terma__status-indicator {
  background: var(--terma-primary);
  box-shadow: 0 0 10px var(--terma-primary);
}

.terma__terminal-status--running {
  color: var(--terma-running);
}
```

## Semantic Tags

Following MAP FIRST protocol:

```html
<div class="terma" data-tekton-component="terma">
  <div class="terma__header" data-tekton-area="terma-header">
    <div data-tekton-status="terma-connection">Connected</div>
  </div>
  
  <div class="terma__menu-bar" data-tekton-nav="terma-tabs">
    <label data-tekton-tab="dashboard">Dashboard</label>
    <label data-tekton-tab="launch">Launch Terminal</label>
    <label data-tekton-tab="terminal-chat">Terminal Chat</label>
    <label data-tekton-tab="team-chat">Team Chat</label>
  </div>
  
  <div class="terma__content" data-tekton-area="terma-content">
    <div data-tekton-panel="dashboard">
      <table data-tekton-widget="terminal-list">
        <!-- Terminal entries -->
      </table>
    </div>
  </div>
  
  <div class="terma__footer" data-tekton-area="terma-chat">
    <input data-tekton-input="unified-chat">
    <button data-tekton-action="send">Send</button>
  </div>
</div>
```

## Responsive Behavior

- Minimum width: 800px (terminal tables need space)
- Tab labels abbreviate on mobile
- Terminal list scrolls horizontally if needed
- Form fields stack vertically on narrow screens

## Accessibility

- Keyboard navigation between tabs
- ARIA labels for all interactive elements
- Status announcements for screen readers
- High contrast mode support
- Focus indicators on all controls