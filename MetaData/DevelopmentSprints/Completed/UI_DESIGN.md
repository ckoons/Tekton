# Ergon v2 UI Design Specification

## Overview
Ergon's UI follows Tekton's CSS-first approach with minimal JavaScript, featuring four main tabs plus the two standard chat interfaces.

## Color Scheme
- Primary: Ergon's existing purple/violet theme
- Accent: Lighter purple for hover states
- Background: Dark theme consistent with Tekton
- Text: High contrast white/light gray

## Layout Structure

### Main Component Structure
```html
<div class="ergon-component">
    <!-- Header -->
    <div class="ergon__header">
        <h2>Ergon: Reusability & Configuration Expert</h2>
        <div class="ergon__status">
            <span class="status-indicator"></span>
            <span>Connected to Registry</span>
        </div>
    </div>
    
    <!-- Tab Navigation -->
    <div class="ergon__tabs">
        <input type="radio" name="ergon-tab" id="ergon-tab-registry" checked>
        <label for="ergon-tab-registry">Registry</label>
        
        <input type="radio" name="ergon-tab" id="ergon-tab-analyzer">
        <label for="ergon-tab-analyzer">Analyzer</label>
        
        <input type="radio" name="ergon-tab" id="ergon-tab-configurator">
        <label for="ergon-tab-configurator">Configurator</label>
        
        <input type="radio" name="ergon-tab" id="ergon-tab-tool-chat">
        <label for="ergon-tab-tool-chat">Tool Chat</label>
        
        <input type="radio" name="ergon-tab" id="ergon-tab-team-chat">
        <label for="ergon-tab-team-chat">Team Chat</label>
    </div>
    
    <!-- Tab Content -->
    <div class="ergon__content">
        <!-- Registry Tab -->
        <div class="ergon__tab-content" data-tab="registry">
            <!-- Content below -->
        </div>
        
        <!-- Other tabs... -->
    </div>
</div>
```

## Tab Designs

### 1. Registry Tab
Shows all available solutions with search and filtering.

```
┌─────────────────────────────────────────────────────────────┐
│ Search: [____________________] Type: [All ▼] Sort: [Usage ▼]│
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 📦 data_processor                              Agent    │ │
│ │ Capabilities: data.csv.parse, data.transform           │ │
│ │ Dependencies: pandas, numpy                             │ │
│ │ Usage: 147 times | Last: 2 hours ago                  │ │
│ │ [Configure] [View Details] [Clone]                     │ │
│ ├─────────────────────────────────────────────────────────┤ │
│ │ 🔧 file_operations                             Tool     │ │
│ │ Capabilities: file.read, file.write, file.list         │ │
│ │ Dependencies: Built-in                                 │ │
│ │ Usage: 523 times | Last: 10 minutes ago              │ │
│ │ [Configure] [View Details] [Examples]                  │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                   Page 1 of 5 │
└─────────────────────────────────────────────────────────────┘
```

### 2. Analyzer Tab
Analyze GitHub repositories for reusable components.

```
┌─────────────────────────────────────────────────────────────┐
│ GitHub Repository Analyzer                                   │
├─────────────────────────────────────────────────────────────┤
│ Repository URL: [_________________________________________] │
│ Branch: [main____] Depth: [Full ▼]    [Analyze]           │
├─────────────────────────────────────────────────────────────┤
│ Recent Analyses:                                            │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ github.com/owner/repo - 2 hours ago                    │ │
│ │ Found: 3 tools, 2 workflows                            │ │
│ │ Status: ✓ Complete                                      │ │
│ │ [View Results] [Import Selected]                        │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 3. Configurator Tab
Configure and wrap existing solutions.

```
┌─────────────────────────────────────────────────────────────┐
│ Solution Configurator                                        │
├─────────────────────────────────────────────────────────────┤
│ Selected Solution: data_processor (Agent)                    │
│ Template: [FastAPI Wrapper ▼]                              │
├─────────────────────────────────────────────────────────────┤
│ Configuration:                                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ name: "custom_data_processor"                           │ │
│ │ description: "Wrapped data processor for CSV"           │ │
│ │ capabilities:                                           │ │
│ │   - data.csv.parse                                     │ │
│ │   - data.csv.transform                                 │ │
│ │ dependencies:                                           │ │
│ │   - pandas>=1.0                                        │ │
│ │ port: 8200                                             │ │
│ └─────────────────────────────────────────────────────────┘ │
│ [Validate] [Preview] [Generate] [Deploy]                    │
└─────────────────────────────────────────────────────────────┘
```

### 4. Tool Chat Tab
Direct interaction with Ergon's CI for expert guidance.

```
┌─────────────────────────────────────────────────────────────┐
│ Tool Chat - Ergon Expert                                     │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Ergon: Hi! I'm your reusability expert. I can help     │ │
│ │ you find existing solutions, configure them, or        │ │
│ │ analyze repositories for reusable components.          │ │
│ ├─────────────────────────────────────────────────────────┤ │
│ │ User: I need to process CSV files and generate charts  │ │
│ ├─────────────────────────────────────────────────────────┤ │
│ │ Ergon: I found 3 solutions that match your needs:      │ │
│ │                                                         │ │
│ │ 1. data_processor (Agent) + chart_generator (Tool)     │ │
│ │    - Can handle CSV parsing and chart creation         │ │
│ │    - Used together 45 times successfully               │ │
│ │                                                         │ │
│ │ 2. pandas_viz (MCP Server)                            │ │
│ │    - All-in-one solution for data and visualization   │ │
│ │    - Requires Python environment                       │ │
│ │                                                         │ │
│ │ Would you like me to:                                  │ │
│ │ [Configure Option 1] [Configure Option 2] [See More]   │ │
│ └─────────────────────────────────────────────────────────┘ │
│ [____________________________________________] [Send]       │
└─────────────────────────────────────────────────────────────┘
```

### 5. Team Chat Tab
Shared chat with all Tekton components.

```
┌─────────────────────────────────────────────────────────────┐
│ Team Chat - All Components                                   │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Apollo: Deployment ready for custom_data_processor      │ │
│ ├─────────────────────────────────────────────────────────┤ │
│ │ Ergon: I've configured custom_data_processor with      │ │
│ │ CSV parsing and chart generation capabilities.         │ │
│ │ It's ready for deployment on port 8200.               │ │
│ ├─────────────────────────────────────────────────────────┤ │
│ │ Sophia: I'll monitor the new service once deployed     │ │
│ ├─────────────────────────────────────────────────────────┤ │
│ │ Numa: Great teamwork! This will help our users with    │ │
│ │ data visualization tasks.                               │ │
│ └─────────────────────────────────────────────────────────┘ │
│ [@Ergon _____________________________________] [Send]       │
└─────────────────────────────────────────────────────────────┘
```

## Interactive Elements

### Solution Cards
- Hover effect: Slight elevation and border glow
- Click actions: Expand for full details
- Quick actions: Configure, View, Clone buttons
- Status indicators: Active/Available/Deprecated

### Search & Filter
- Real-time search as you type
- Multi-select filters for type and capabilities
- Sort options: Usage, Name, Recently Updated
- Clear filters button

### Configuration Editor
- Syntax highlighting for YAML/JSON
- Validation indicators (green check, red X)
- Auto-complete for known fields
- Preview pane for generated code

## Responsive Behavior
- Cards stack vertically on narrow screens
- Tab labels compress to icons on mobile
- Chat interfaces remain full height
- Modals for detailed views on small screens

## Loading States
- Skeleton cards while loading registry
- Progress bar for GitHub analysis
- Spinning indicator for configuration generation
- Typing indicator in chat interfaces

## Error States
- Red banner for connection errors
- Inline validation messages
- Retry buttons for failed operations
- Graceful degradation when services unavailable

## Accessibility
- Keyboard navigation for all interactions
- ARIA labels for screen readers
- High contrast mode support
- Focus indicators on all interactive elements