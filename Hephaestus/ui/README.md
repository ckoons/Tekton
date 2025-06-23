# Hephaestus UI

## Overview

Hephaestus UI is the unified interface for the Tekton ecosystem, providing a consistent way to interact with all Tekton components. It follows the "Keep It Simple" philosophy with a standardized structure for component display and interaction.

## Architecture

The UI is structured around two main regions:

1. **LEFT PANEL**: Navigation and component selection
2. **RIGHT PANEL**: Component-specific interface with standardized structure:
   - HEADER: Component identification
   - MENU BAR: Component-specific tabs and controls
   - WORKSPACE: Main content area
   - CHAT-INPUT-AREA: (Only for LLM components)

## Getting Started

### Prerequisites

- Node.js (for development server)
- Python 3.10+ (for backend server)
- Modern web browser (Chrome, Firefox, Safari, or Edge)

### Running the UI

1. Start the Hephaestus server:
   ```bash
   cd /path/to/Tekton/Hephaestus/ui
   python server/server.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8080
   ```

## Development Guidelines

### File Organization

Each component has its own directory structure:

```
ui/scripts/component-name/
├── html/          # HTML templates
├── css/           # Component styles
├── js/            # JavaScript functionality
```

### File Size Limits

- Target: <500 lines per file
- Strict limit: 1000 lines per file
- Split files exceeding 600 lines

### Component Implementation

Components follow a standardized loading pattern:

```javascript
function loadComponentName() {
  // Get HTML panel
  const htmlPanel = document.getElementById('html-panel');
  htmlPanel.innerHTML = '';
  
  // Set active component
  setActiveComponent('component-name');
  
  // Create structure
  const header = createComponentHeader('ComponentName', 'Functional Name');
  const menuBar = createComponentMenuBar('component-name', tabDefinitions);
  const workspace = createComponentWorkspace('component-name');
  
  // Add to panel
  htmlPanel.appendChild(header);
  htmlPanel.appendChild(menuBar);
  htmlPanel.appendChild(workspace);
  
  // Add chat input if needed
  if (isLLMComponent('component-name')) {
    const chatInput = createChatInputArea('component-name');
    htmlPanel.appendChild(chatInput);
  }
  
  // Setup events
  setupComponentEvents('component-name');
  
  // Load default tab
  loadComponentTab('component-name', 'default-tab');
}
```

### Styling Guidelines

- Follow BEM naming methodology
- Use CSS variables for theming
- Maintain consistent spacing and sizing
- Component-specific styles should use component namespacing

### Backend Communication

- Use Hermes for component-to-component communication
- Implement proper error handling and loading states
- Follow standardized API patterns

## Documentation

For more detailed documentation, refer to:

- [TEKTON_GUI_STYLING_RULES.md](/TEKTON_GUI_STYLING_RULES.md): Complete styling guidelines
- [Hephaestus_UI_Implementation.md](/MetaData/TektonDocumentation/DeveloperGuides/Hephaestus_UI_Implementation.md): Detailed implementation guide
- [EngineeringGuidelines.md](/MetaData/TektonDocumentation/DeveloperGuides/EngineeringGuidelines.md): Overall engineering principles

## Implementation Details

For detailed information about how the UI loading system works, CSS management, and common pitfalls, see [How Tekton UI Works](./docs/HowTektonUIWorks.md).

## Component Development

To create a new component:

1. Create the component directory structure
2. Implement the component loader function
3. Create HTML templates for each tab
4. Implement CSS styles
5. Set up event handlers
6. Register the component in the component registry

## Contributing

When contributing to the Hephaestus UI:

1. Follow the file size guidelines
2. Maintain the standardized RIGHT PANEL structure
3. Use the established patterns for tab navigation
4. Keep styling consistent with the existing components
5. Document any component-specific requirements or behaviors

## Troubleshooting

### Common Issues

1. **Component not loading**:
   - Check browser console for errors
   - Verify paths in component loader
   - Check if HTML templates exist

2. **Styling inconsistencies**:
   - Ensure CSS specificity is correct
   - Check for missing styles
   - Verify theme variable usage

3. **Backend connectivity**:
   - Check that required services are running
   - Verify WebSocket connection
   - Check for CORS issues

### Debug Tools

The UI includes several debug tools:

- Console logging with component prefixes
- Debug mode toggle in settings
- State inspection tool
- Network request logging