# Hephaestus UI

## 🎉 Architecture Update (June 2025)

**IMPORTANT: Hephaestus UI uses a simplified architecture with dynamic component loading**

- ✅ Components loaded on-demand via minimal-loader.js
- ✅ Clean separation between navigation and content
- ✅ Minimal JavaScript for core functionality
- ✅ CSS-first styling and layout

**📖 Architecture Documentation: [CSS-First Architecture Documentation](/MetaData/TektonDocumentation/Architecture/CSSFirstArchitecture.md)** - Note: Contains historical context about the attempted pure CSS approach

---

## 🐛 Debugging

**For debugging and troubleshooting, see: [DEBUGGING.md](DEBUGGING.md)**

The UI includes a powerful debug system for:
- Identifying which files are loaded
- Tracking component behavior
- Diagnosing issues without code changes

Quick start: `HephaestusDebug.enableFileTrace()` in browser console.

---

## Overview

Hephaestus UI is the unified interface for the Tekton ecosystem, providing a consistent way to interact with all Tekton components. It follows the "Keep It Simple" philosophy with a standardized structure for component display and interaction.

## Architecture

### Current Architecture

The UI uses dynamic component loading where:
- Components are loaded on-demand when selected
- Navigation works via JavaScript event handlers and URL fragments (e.g., `#numa`)
- JavaScript handles component loading, WebSocket, chat, and health checks
- CSS handles all styling and layout (CSS-first for presentation)

### UI Structure

The UI is structured around two main regions:

1. **LEFT PANEL**: Navigation and component selection
2. **MAIN CONTENT**: All components pre-loaded, shown/hidden via CSS:
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

### Adding or Modifying Components

1. **Edit component HTML**: `components/[name]/[name]-component.html`
2. **Refresh browser**: Changes appear immediately
3. **Test locally**: Components load dynamically via `#componentName` hash

### File Organization

```
ui/
├── index.html              # Main entry point with navigation
├── scripts/
│   ├── minimal-loader.js   # Handles dynamic component loading
│   ├── ui-manager-core.js  # Component lifecycle management
│   └── [various].js        # Supporting scripts
├── components/             # Component HTML files
│   └── [name]/
│       └── [name]-component.html
└── styles/                 # CSS files for styling
```

### Key Files

- **`minimal-loader.js`**: Handles dynamic component loading
- **`index.html`**: Main entry point with navigation
- **`components/`**: Individual component HTML files

### File Size Limits

- Target: <500 lines per file
- Strict limit: 1000 lines per file
- Split files exceeding 600 lines

### Component Structure

Each component HTML file follows a standardized structure:

```html
<div class="component-container">
    <div class="component-header">
        <h1 class="component-title">Component Name</h1>
        <div class="component-actions">
            <!-- Component-specific actions -->
        </div>
    </div>
    
    <div class="component-menu-bar">
        <!-- Tabs or navigation -->
    </div>
    
    <div class="component-workspace">
        <!-- Main content area -->
    </div>
    
    <!-- Optional chat area for LLM components -->
    <div class="chat-input-area">
        <!-- Chat interface -->
    </div>
</div>
```

Components are loaded dynamically by minimal-loader.js when selected.

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