# Component Status Indicators

This document describes the component status indicator system implemented in the Tekton UI.

## Overview

The Tekton UI uses colored dots (status indicators) in the left panel navigation to display two key pieces of information:

1. **Component Identity**: Each component has a specific color that matches its visual identity
2. **Component Status**: The indicators change appearance based on component state

## Visual States

Status indicators have multiple visual states:

1. **Default State**: Dimmed color (50% opacity)
   - Indicates the component is available in the UI but not active
   
2. **Active State**: Full color (100% opacity)
   - Indicates the component is currently selected in the UI
   
3. **Connected State**: Glowing effect with subtle pulse animation
   - Indicates the component's backend service is available and responsive
   
4. **Connected and Active State**: Enhanced glow with stronger pulse
   - Indicates both that the component is selected and its backend is available

## Color System

Each component has a designated color for its status indicator:

| Component   | Color Code | Color Name    | Description                      |
|-------------|------------|---------------|----------------------------------|
| Tekton      | #FBBC05    | Yellow/Gold   | Core orchestration system        |
| Prometheus  | #C2185B    | Pink          | Planning system                  |
| Telos       | #00796B    | Dark Teal     | Requirements system              |
| Ergon       | #0097A7    | Teal          | Agent framework                  |
| Harmonia    | #F57C00    | Orange        | Workflow engine                  |
| Synthesis   | #3949AB    | Indigo        | Integration engine               |
| Athena      | #7B1FA2    | Purple        | Knowledge graph system           |
| Sophia      | #7CB342    | Light Green   | Machine learning system          |
| Engram      | #34A853    | Green         | Memory system                    |
| Rhetor      | #D32F2F    | Red           | LLM management                   |
| Hermes      | #4285F4    | Blue          | Message and data broker          |
| Codex       | #00ACC1    | Light Blue    | Code interface                   |
| Terma       | #5D4037    | Brown         | Terminal interface               |

## Technical Implementation

The system has three main components:

1. **CSS Classes**: Define the visual appearance of each state
   - `.status-indicator`: Base styling
   - `.status-indicator.active`: Selected component styling
   - `.status-indicator.connected`: Available backend styling
   - `.status-indicator.connected.active`: Combined state styling

2. **Component-Specific Colors**: Applied with CSS selectors
   - `.nav-item[data-component="COMPONENT_ID"] .status-indicator { background-color: COLOR; }`

3. **Availability Checking**: Health checks to detect backend services
   - Runs periodically to update the component status
   - Toggles the `.connected` class based on service availability

## Usage Guidelines

When creating a new component:

1. Add the component's color code to the CSS in `index.html`
2. Ensure the component navigation item follows the standard structure:
   ```html
   <li class="nav-item" data-component="component-id">
       <span class="nav-label">Component Name</span>
       <span class="status-indicator"></span>
   </li>
   ```
3. Add the component's health endpoint to the `componentEndpoints` object in the `initComponentAvailabilityChecks` method
4. Add the component's default port to the `defaultPorts` object in the `_getDefaultPort` method

## Maintenance

When updating the UI system, be sure to:

1. Maintain the consistent color scheme across all components
2. Ensure the status indicators remain consistently positioned
3. Test that health checks function properly for all components

The status indicator system helps users quickly identify which components are active and available, improving the overall UX of the Tekton system.