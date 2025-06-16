# UI Manager Refactoring - Claude Code Prompt

## Task Overview

You are tasked with refactoring the Hephaestus UI codebase. The primary issue is that `ui-manager.js` (208KB) has become far too large and monolithic. Your goal is to break this file into smaller, focused files while preserving the existing functionality.

## Critical Working Environment

Before beginning ANY code changes, understand the EXACT current working state:

1. The UI currently works with the monolithic ui-manager.js
2. Previous refactoring attempts created unnecessary files and folders that should be ignored:
   - `/scripts/core/` - Ignore this directory completely
   - `/scripts/components/` - Ignore all files here except those explicitly mentioned below
   - Any `.bak` or `.new` files - These are backup files, not part of the working codebase

3. The following files are KNOWN TO WORK and should be your foundation:
   - `/scripts/ui-manager.js` - The large file we need to refactor
   - `/scripts/main.js` - The main JS entry point
   - `/index.html` - The main HTML file
   - `/components/athena/athena-component.html` - Athena component template
   - `/components/ergon/ergon-component.html` - Ergon component template

## Refactoring Methodology

Follow these EXTREMELY detailed steps, doing ONLY ONE STEP at a time:

### STEP 1: Create a ComponentLoader class

1. First, locate ALL code related to component loading in ui-manager.js:
   ```
   - Look for functions with names including "loadComponent", "initializeComponent", etc.
   - Find any methods that deal with HTML templates and DOM insertion
   - Look for state variables that track loaded components
   ```

2. Create a new file `/scripts/component-loader.js` with ONLY this functionality:
   ```javascript
   /**
    * Component Loader
    * Handles loading and initialization of UI components
    */
   class ComponentLoader {
     constructor() {
       // ONLY include state variables directly related to component loading
       this.loadedComponents = {};
     }
     
     // ADD ONLY the methods related to loading components:
     // - loadComponent()
     // - loadComponentHTML()
     // - initializeComponent() 
     // - Any direct helper methods used only by these functions
   }
   
   // Create global instance
   window.componentLoader = new ComponentLoader();
   ```

3. Update `index.html` to load this new file - add this line BEFORE ui-manager.js:
   ```html
   <script src="scripts/component-loader.js"></script>
   ```

4. TEMPORARILY keep the original methods in ui-manager.js, but wrap them in code comments
5. Test this change by loading the UI in a browser - all components should still load correctly

### STEP 2: Extract the Athena component

1. Find ALL code in ui-manager.js related to the Athena component:
   ```
   - Look for functions with "Athena" in their names
   - Find functions that manipulate Athena DOM elements
   - Find event handlers specifically for Athena
   ```

2. Create a new file `/scripts/athena-component.js` with this structure:
   ```javascript
   /**
    * Athena Component
    * Knowledge graph and entity management interface
    */
   class AthenaComponent {
     constructor() {
       // ONLY include state variables directly related to Athena
       this.state = {
         initialized: false,
         activeTab: 'chat', // Default tab
       };
     }
     
     /**
      * Initialize the component
      */
     init() {
       console.log('Initializing Athena component');
       
       // Load component HTML
       this.loadComponentHTML();
       
       // Mark as initialized
       this.state.initialized = true;
       
       return this;
     }
     
     /**
      * Load the component HTML
      */
     async loadComponentHTML() {
       // Get HTML panel for component rendering
       const htmlPanel = document.getElementById('html-panel');
       if (!htmlPanel) {
         console.error('HTML panel not found!');
         return;
       }
       
       try {
         // Fetch component HTML template
         const response = await fetch('/components/athena/athena-component.html');
         if (!response.ok) {
           throw new Error(`Failed to load Athena template: ${response.status}`);
         }
         
         const html = await response.text();
         
         // Insert HTML into panel
         htmlPanel.innerHTML = html;
         
         // Setup component functionality
         this.setupTabs();
         this.setupChat();
         
         console.log('Athena component HTML loaded successfully');
       } catch (error) {
         console.error('Error loading Athena component:', error);
         htmlPanel.innerHTML = `
           <div class="error-message">
             <h3>Error Loading Athena Component</h3>
             <p>${error.message}</p>
           </div>
         `;
       }
     }
     
     // ADD the remaining methods specific to Athena
     // - setupTabs() - For tabbed interface
     // - setupChat() - For chat functionality
     // - Any other Athena-specific methods
   }
   
   // Create global instance
   window.athenaComponent = new AthenaComponent();
   
   // Add handler to component activation
   document.addEventListener('DOMContentLoaded', function() {
     const athenaTab = document.querySelector('.nav-item[data-component="athena"]');
     if (athenaTab) {
       athenaTab.addEventListener('click', function() {
         // Initialize component if not already done
         if (window.athenaComponent) {
           window.athenaComponent.init();
         }
       });
     }
   });
   ```

3. Update `index.html` to load this new file - add it AFTER component-loader.js:
   ```html
   <script src="scripts/athena-component.js"></script>
   ```

4. TEMPORARILY keep the original methods in ui-manager.js, but wrap them in code comments
5. Test this change by loading the UI and clicking on the Athena component - it should work correctly

### STEP 3: Extract the Ergon component

Follow the exact same process as for Athena, but with Ergon-specific code.

1. Create `/scripts/ergon-component.js` with the proper structure
2. Update `index.html` to load this new file
3. Test by clicking on the Ergon component in the UI

### STEP 4: Remove commented code from ui-manager.js

Once you've verified the extracted components work correctly:

1. Remove all code you've extracted and commented out in ui-manager.js
2. Update any references to use the new component instances
3. Test the full UI again - all components should work correctly

### STEP 5: Extract UI utilities

1. Identify utility functions in ui-manager.js that are used by multiple components
2. Create `/scripts/ui-utils.js` with these utility functions
3. Update the component files to use these utilities
4. Test the full UI again

## CRITICAL RULES FOR REFACTORING

1. **ONE STEP AT A TIME**: Complete and test each step fully before moving to the next
2. **EXTREMELY MINIMAL CHANGES**: Only change what's absolutely necessary
3. **NO FUNCTIONALITY CHANGES**: Don't fix bugs or add features during refactoring
4. **TEST AFTER EVERY CHANGE**: Verify the UI still works after each file extraction
5. **PRESERVE INTERFACES**: Keep function signatures consistent
6. **BE SURGICAL**: Only extract code that's directly related to the component
7. **DON'T TOUCH WORKING FILES**: Never modify files that are known to work unless instructed

## Testing Protocol

After each change, follow this exact testing procedure:

1. Restart the UI server:
   ```bash
   ./restart_ui.sh
   ```

2. Load the UI in a browser
3. Check the browser console for errors
4. Click on each component to verify it loads
5. Test specific functionality in each component:
   - Athena: Tabs should work, chat interface should display
   - Ergon: Tabs and agent management should work
   - All navigation should be functional

## If Things Break

If your changes cause issues:

1. IMMEDIATELY restore the working versions from backup:
   ```bash
   cp /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/working_backup/ui-manager.js /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/
   cp /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/working_backup/index.html /Users/cskoons/projects/github/Tekton/Hephaestus/ui/
   ```

2. Restart the UI server:
   ```bash
   ./restart_ui.sh
   ```

3. Document exactly what change caused the issue

## Required File Extraction Order

Extract files in EXACTLY this order, completing and testing each one before moving to the next:

1. `/scripts/component-loader.js` - Core component loading functionality
2. `/scripts/athena-component.js` - Athena component code
3. `/scripts/ergon-component.js` - Ergon component code
4. `/scripts/ui-utils.js` - Shared utilities
5. Additional component-specific files, one at a time

## Final Deliverables

When complete, you should have:

1. A refactored, smaller `ui-manager.js` that delegates to other files
2. Individual component files for each main component
3. A separate component loader
4. Shared utility files
5. A fully functioning UI with the same behavior as before

## Completion Criteria

The refactoring is complete when:

1. The ui-manager.js file is less than 50KB in size
2. All components are extracted into their own files
3. All functionality works exactly as before
4. No unnecessary files remain
5. Documentation is updated to reflect the new architecture