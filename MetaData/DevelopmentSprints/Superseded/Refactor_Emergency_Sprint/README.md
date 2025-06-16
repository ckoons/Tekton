# UI Manager Refactoring Emergency Sprint

## Emergency Context

The Hephaestus UI implementation has become unstable due to an overly large `ui-manager.js` file (208KB) that handles too many responsibilities. This monolithic approach has led to difficulty in maintenance, unpredictable behavior, and challenges in extending the UI with new components.

This emergency sprint addresses the critical need to refactor the UI manager into smaller, focused files while preserving functionality. **The UI must continue to work throughout this process.**

## Current Issues

1. **Monolithic Structure**: The `ui-manager.js` file (208KB) is too large and handles multiple unrelated concerns
2. **Brittle Component Loading**: Component loading logic is tangled with other UI management functions
3. **Unstable DOM Management**: The UI can break when components are loaded in different orders
4. **Unclear Responsibility Boundaries**: Different parts of the code are handling the same tasks

## Emergency Sprint Goals

1. **Break down the monolithic UI manager** into multiple smaller focused files:
   - Individual component files for each Tekton component (Athena, Ergon, etc.)
   - Shared utility files for common functions
   - Core UI management separated from component specifics

2. **Fix broken component loading** to ensure reliable operation:
   - Standardize component loading process
   - Implement proper error handling
   - Ensure components work in isolation

3. **Preserve working functionality** throughout the refactoring:
   - Focus on files that are known to work
   - Make incremental changes with testing at each step
   - Isolate and contain risky changes

## Critical Warning for Claude

**IMPORTANT: READ THESE GUIDELINES CAREFULLY BEFORE STARTING ANY IMPLEMENTATION**

1. **Preserve Basic UI Functionality**: The UI must continue to work throughout this refactoring
2. **Make Extremely Small, Focused Changes**: One file or function at a time
3. **Test After Each Change**: Verify functionality after each modification
4. **Do Not Create Unnecessary Files**: Only extract what is necessary to achieve goals
5. **Do Not Modify Working Files Unless Explicitly Instructed**
6. **Work Only With Files That Are Known To Work**

## Refactoring Approach

This emergency sprint uses an iterative, surgical approach:

1. **Identify Specific Targets**: Locate self-contained units of functionality within `ui-manager.js`
2. **Extract One Function/Module at a Time**: Focus on a single logical unit in each step
3. **Test Immediately**: Verify the functionality still works after each extraction
4. **Commit Working Changes**: Save progress regularly
5. **Clean Up Temporary/Broken Files**: Remove files created during failed attempts
6. **Build on What Works**: Use the working files as foundation for further improvements

## Work Plan

### Phase 1: Initial Assessment and Safe Environment Setup

1. Create a safe working environment by identifying and preserving known working files:
   ```bash
   # Create a safe backup of current known working files
   mkdir -p /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/working_backup
   cp /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/ui-manager.js /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/working_backup/
   cp /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/main.js /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/working_backup/
   cp /Users/cskoons/projects/github/Tekton/Hephaestus/ui/index.html /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/working_backup/
   
   # Create a directory for the refactored files
   mkdir -p /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/refactored
   ```

2. Identify files to clean up from previous failed attempts:
   ```bash
   # Find and list all potentially problematic files created in previous attempts
   find /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts -name "*.new" -o -name "*.bak"
   
   # List all directories that shouldn't be part of the final solution
   ls -la /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/core 2>/dev/null || echo "core directory not found"
   ls -la /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/components 2>/dev/null || echo "components directory not found"
   ```

### Phase 2: Surgical Extraction of Component Loader

1. **Precisely identify the component loader functionality** in ui-manager.js:
   - Find all functions related to loading components
   - Map their dependencies within the file
   - Identify shared state they access

2. **Extract ONLY component loader functionality** into a separate file:
   ```javascript
   // component-loader.js - ONLY include these specific functions:
   // - loadComponent(componentId)
   // - registerComponent(component)
   // - initializeComponent(componentId)
   // - loadComponentHTML(componentId, container)
   // - Additional helper functions used ONLY by these functions
   ```

3. **Update the original ui-manager.js** to use the extracted component-loader.js:
   ```javascript
   // ui-manager.js - Replace the extracted functions with imports
   // Add at the top:
   // const componentLoader = new ComponentLoader();
   
   // Replace direct function calls with:
   // componentLoader.loadComponent(...)
   ```

4. **Test immediately** after this change:
   ```bash
   # Restart the UI server
   ./restart_ui.sh
   
   # Visit the UI and verify components still load correctly
   ```

### Phase 3: Component-Specific Functionality Extraction

For each component (Athena, Ergon, etc.), extract its specific functionality:

1. **Identify component-specific code** in ui-manager.js:
   ```bash
   # Find all functions related to a specific component
   grep -n "function.*[Aa]thena" /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/ui-manager.js
   ```

2. **Extract ONLY that component's code** to its own file:
   ```javascript
   // athena-component.js - ONLY include Athena-specific functions:
   // - loadAthenaComponent()
   // - setupAthenaUI()
   // - handleAthenaEvent()
   // - Any Athena-specific helper functions
   ```

3. **Update ui-manager.js** to use the extracted component file:
   ```javascript
   // ui-manager.js - Replace the extracted Athena functions with imports
   // Add at the top:
   // const athenaComponent = new AthenaComponent();
   
   // Replace direct function calls with:
   // athenaComponent.loadComponent()
   ```

4. **Test immediately** after each component extraction:
   ```bash
   # Restart the UI server
   ./restart_ui.sh
   
   # Visit the UI, click on the Athena component, and verify it loads correctly
   ```

5. **Repeat for each component**, one at a time:
   - Ergon
   - Rhetor
   - Hermes
   - etc.

### Phase 4: Shared Utility Extraction

1. **Identify shared utility functions** in ui-manager.js:
   ```bash
   # Look for utility functions that multiple components use
   grep -n "function.*Utils\|Helper\|Common" /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/ui-manager.js
   ```

2. **Extract ONLY shared utilities** to their own file:
   ```javascript
   // ui-utils.js - ONLY include shared utility functions:
   // - formatDate()
   // - sanitizeHTML()
   // - validateInput()
   // - etc.
   ```

3. **Update all relevant files** to use the extracted utilities:
   ```javascript
   // In all files that used these utilities
   // Add at the top:
   // const uiUtils = new UIUtils();
   
   // Replace direct function calls with:
   // uiUtils.formatDate()
   ```

4. **Test immediately** after this change:
   ```bash
   # Restart the UI server
   ./restart_ui.sh
   
   # Test all affected components
   ```

### Phase 5: Core UI Manager Refactoring

1. **Clean up the remaining ui-manager.js** after all extractions:
   - Remove commented out code
   - Simplify any overly complex functions
   - Add proper documentation

2. **Test the entire application** to ensure functionality is preserved:
   ```bash
   # Restart the UI server with the fully refactored codebase
   ./restart_ui.sh
   
   # Test all components and functionality
   ```

### Phase 6: Cleanup and Documentation

1. **Remove temporary and broken files**:
   ```bash
   # Remove all backup files
   find /Users/cskoons/projects/github/Tekton/Hephaestus/ui -name "*.bak" -delete
   find /Users/cskoons/projects/github/Tekton/Hephaestus/ui -name "*.new" -delete
   
   # Remove any empty directories or unused files
   rm -rf /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/core 2>/dev/null || true
   ```

2. **Document the new architecture**:
   - Update implementation documentation
   - Create a component dependency diagram
   - Document the refactoring process

## Microscopic Instructions for Claude

### How to Extract a Single Function

Follow these precise steps when extracting functions:

1. **Read the entire function** first to understand its inputs, outputs, and dependencies

2. **Identify all dependencies**:
   ```javascript
   // Example: This function depends on formatDate and updateUI
   function processData(data) {
     const formattedDate = formatDate(data.timestamp);
     const result = { date: formattedDate, value: data.value };
     updateUI(result);
     return result;
   }
   ```

3. **Extract ONLY that function and its direct dependencies**:
   ```javascript
   // In new file: data-processor.js
   class DataProcessor {
     constructor() {
       // Initialize any state needed
     }
     
     processData(data) {
       const formattedDate = this.formatDate(data.timestamp);
       const result = { date: formattedDate, value: data.value };
       // Note: updateUI is external, so we'll need to pass it in or use events
       this.onDataProcessed(result);
       return result;
     }
     
     formatDate(timestamp) {
       // Implementation of formatDate
     }
     
     // Event handler for external code to subscribe to
     onDataProcessed(result) {
       // This will be called instead of directly calling updateUI
       if (typeof this.dataProcessedCallback === 'function') {
         this.dataProcessedCallback(result);
       }
     }
     
     // Method to register a callback
     setDataProcessedCallback(callback) {
       this.dataProcessedCallback = callback;
     }
   }
   
   // Export the class
   window.DataProcessor = DataProcessor;
   ```

4. **Modify the original file** to use the extracted function:
   ```javascript
   // In original file
   // Initialize the data processor at the top
   const dataProcessor = new DataProcessor();
   
   // Set up the callback to handle processed data
   dataProcessor.setDataProcessedCallback(updateUI);
   
   // Replace the original function call
   // OLD: const result = processData(data);
   // NEW:
   const result = dataProcessor.processData(data);
   ```

5. **Add proper imports** to HTML file:
   ```html
   <!-- Add before the ui-manager.js script -->
   <script src="scripts/data-processor.js"></script>
   ```

### How to Work with the Existing Files

When working with the existing files, follow these guidelines:

1. **Use the working files from the backup directory as reference**:
   ```bash
   # Compare a function you're about to modify with the backup
   diff /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/ui-manager.js /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/working_backup/ui-manager.js
   ```

2. **Make microscopic changes** - one function at a time:
   ```javascript
   // GOOD: Extract just one function and its dependencies
   // loadComponentHTML() and its direct helpers
   
   // BAD: Extract multiple unrelated functions
   // loadComponentHTML(), updateTerminal(), and formatTimestamp()
   ```

3. **Preserve function signatures** when possible:
   ```javascript
   // Original
   function loadComponent(componentId, container) { ... }
   
   // New file - keep the same signature
   class ComponentLoader {
     loadComponent(componentId, container) { ... }
   }
   ```

4. **Keep state management consistent**:
   ```javascript
   // If the original used global window.activeComponent
   // Either continue to use it or refactor ALL related code to use a new pattern
   ```

5. **Don't change behavior unless explicitly fixing a bug**:
   ```javascript
   // GOOD: Extract with identical behavior
   // BAD: Fix "while I'm here" issues without specific instruction
   ```

### Testing After Each Change

After each change, test thoroughly:

1. **Visual inspection** - Look for JS errors in console

2. **Functional testing** - Test all affected functionality:
   ```
   - If you modified component loading, test loading each component
   - If you modified Athena specific code, test all Athena functionality
   - If you modified shared utilities, test all components that use them
   ```

3. **Error case testing** - Try to provoke errors:
   ```
   - Try loading components in different orders
   - Try rapid switching between components
   - Try refreshing the page in different states
   ```

## Example of Proper Extraction

Here's a specific example of properly extracting a component loader:

### 1. Original Code in ui-manager.js

```javascript
class UIManager {
  constructor() {
    this.components = {};
    // lots of other state
  }
  
  loadComponent(componentId, container) {
    console.log(`Loading component: ${componentId}`);
    
    // Check if already loaded
    if (this.components[componentId]) {
      return this.components[componentId];
    }
    
    // Try to load the component HTML
    return this.loadComponentHTML(componentId, container)
      .then(() => {
        // Initialize the component
        this.initializeComponent(componentId);
        this.components[componentId] = { id: componentId, loaded: true };
        return this.components[componentId];
      })
      .catch(error => {
        console.error(`Failed to load component ${componentId}:`, error);
        return null;
      });
  }
  
  loadComponentHTML(componentId, container) {
    const htmlPath = `/components/${componentId}/${componentId}-component.html`;
    return fetch(htmlPath)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Failed to load ${componentId} HTML`);
        }
        return response.text();
      })
      .then(html => {
        container.innerHTML = html;
        return html;
      });
  }
  
  initializeComponent(componentId) {
    // Component-specific initialization logic
    if (componentId === 'athena') {
      this.initializeAthena();
    } else if (componentId === 'ergon') {
      this.initializeErgon();
    }
    // ...other initialization logic...
  }
  
  // Many other methods not related to component loading
}
```

### 2. Extracted component-loader.js

```javascript
/**
 * Component Loader
 * Handles loading and initialization of UI components
 */
class ComponentLoader {
  constructor() {
    this.loadedComponents = {};
  }
  
  /**
   * Load a component
   * @param {string} componentId - ID of the component to load
   * @param {HTMLElement} container - Container element
   * @returns {Promise<object|null>} - Promise resolving to component or null
   */
  loadComponent(componentId, container) {
    console.log(`Loading component: ${componentId}`);
    
    // Check if already loaded
    if (this.loadedComponents[componentId]) {
      return Promise.resolve(this.loadedComponents[componentId]);
    }
    
    // Try to load the component HTML
    return this.loadComponentHTML(componentId, container)
      .then(() => {
        // Initialize the component
        this.initializeComponent(componentId);
        this.loadedComponents[componentId] = { id: componentId, loaded: true };
        return this.loadedComponents[componentId];
      })
      .catch(error => {
        console.error(`Failed to load component ${componentId}:`, error);
        return null;
      });
  }
  
  /**
   * Load component HTML content
   * @param {string} componentId - ID of the component
   * @param {HTMLElement} container - Container element
   * @returns {Promise<string>} - Promise resolving to HTML content
   */
  loadComponentHTML(componentId, container) {
    const htmlPath = `/components/${componentId}/${componentId}-component.html`;
    return fetch(htmlPath)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Failed to load ${componentId} HTML`);
        }
        return response.text();
      })
      .then(html => {
        container.innerHTML = html;
        return html;
      });
  }
  
  /**
   * Initialize component after HTML is loaded
   * @param {string} componentId - ID of the component to initialize
   */
  initializeComponent(componentId) {
    // Call global initialization functions based on component
    if (componentId === 'athena' && window.initializeAthena) {
      window.initializeAthena();
    } else if (componentId === 'ergon' && window.initializeErgon) {
      window.initializeErgon();
    }
    // Add more components as needed
  }
}

// Create global instance
window.componentLoader = new ComponentLoader();
```

### 3. Updated ui-manager.js to use ComponentLoader

```javascript
class UIManager {
  constructor() {
    // other state, but remove component-related state
    // this.components = {}; // REMOVED - now in ComponentLoader
  }
  
  // REMOVED - loadComponent method now in ComponentLoader
  // REMOVED - loadComponentHTML method now in ComponentLoader
  // REMOVED - initializeComponent method now in ComponentLoader
  
  // Updated to use componentLoader
  activateComponent(componentId) {
    // Get the container
    const container = document.getElementById('html-panel');
    
    // Use the component loader
    window.componentLoader.loadComponent(componentId, container)
      .then(component => {
        if (component) {
          console.log(`Component ${componentId} activated`);
          this.updateActiveComponent(componentId);
        }
      });
  }
  
  // Other methods stay the same
}
```

### 4. Updated index.html

```html
<!-- Add the component loader script before ui-manager.js -->
<script src="scripts/component-loader.js"></script>
<script src="scripts/ui-manager.js"></script>
<!-- Rest of scripts -->
```

## Approval and Review Process

At the end of each phase:

1. Test the UI functionality thoroughly
2. Run a simple verification script to confirm all components work
3. Document the changes made in the Sprint Documentation
4. Clean up any temporary or unnecessary files

## Emergency Rollback Plan

If at any point the refactoring causes critical issues:

1. **Immediate Rollback**: Use the backup files to restore functionality
   ```bash
   cp /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/working_backup/ui-manager.js /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/
   cp /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/working_backup/main.js /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/
   cp /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/working_backup/index.html /Users/cskoons/projects/github/Tekton/Hephaestus/ui/
   ```

2. **Restart the UI Server**: Ensure the rollback takes effect
   ```bash
   ./restart_ui.sh
   ```

3. **Document the Issue**: Record what caused the issue for future attempts

## Conclusion

This emergency sprint aims to address the critical UI refactoring needs while maintaining functionality. By following these microscopic steps and precise instructions, we can transform the monolithic UI manager into a maintainable, component-based architecture without disrupting the user experience.

Remember: Make small, focused changes. Test after each change. Always have a working backup.