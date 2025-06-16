# Component Loader Template for Direct HTML Injection

This template provides a standardized approach for creating component loaders using direct HTML injection, which solves the issues with loading full HTML documents in the Tekton UI.

## Template Structure

```javascript
/**
 * Load the [Component] component using direct HTML injection pattern
 * This follows the standardized approach from the Fix GUI Sprint
 */
load[Component]Component() {
    console.log('Loading [Component] component with direct HTML injection pattern...');
    
    // First, set the activeComponent
    this.activeComponent = '[component-id]';
    tektonUI.activeComponent = '[component-id]';
    
    // Get the HTML panel for component rendering
    const htmlPanel = document.getElementById('html-panel');
    
    if (!htmlPanel) {
        console.error('HTML panel not found!');
        return;
    }
    
    // Clear any existing content in the HTML panel
    htmlPanel.innerHTML = '';
    
    // Activate the HTML panel to ensure it's visible
    this.activatePanel('html');
    
    // Define the component HTML directly
    // This direct injection approach solves the issues with loading full HTML documents
    const [component]Html = `
        <div id="[component-id]-container" class="[component-id]-component" style="height: 100%; width: 100%; display: flex; flex-direction: column; background-color: #1a1a1a; color: #f0f0f0;">
            <!-- Header -->
            <header style="background-color: #252525; padding: 1rem; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #444;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <img src="/images/icon.jpg" alt="[Component]" style="height: 2rem; width: auto; border-radius: 4px;">
                    <h1 style="margin: 0; font-size: 1.5rem;">[Component Name]</h1>
                </div>
                <div>
                    <!-- Component-specific metrics or indicators -->
                </div>
            </header>
            
            <!-- Tabs -->
            <div class="[component-id]-tabs" style="display: flex; background-color: #252525; border-bottom: 1px solid #444;">
                <div class="[component-id]-tab active" data-panel="tab1" 
                     style="padding: 0.75rem 1.5rem; cursor: pointer; border-bottom: 3px solid #007bff; font-weight: bold;">
                    Tab 1
                </div>
                <div class="[component-id]-tab" data-panel="tab2" 
                     style="padding: 0.75rem 1.5rem; cursor: pointer; border-bottom: 3px solid transparent;">
                    Tab 2
                </div>
                <!-- Additional tabs as needed -->
            </div>
            
            <!-- Content -->
            <div class="[component-id]-content" style="flex: 1; padding: 1rem; overflow: auto;">
                <!-- Tab 1 Panel -->
                <div class="[component-id]-panel active" id="tab1-panel" style="height: 100%; display: block;">
                    <!-- Tab 1 content -->
                </div>
                
                <!-- Tab 2 Panel -->
                <div class="[component-id]-panel" id="tab2-panel" style="height: 100%; display: none;">
                    <!-- Tab 2 content -->
                </div>
                
                <!-- Additional panel content as needed -->
            </div>
        </div>
    `;
    
    // Add the HTML directly to the panel
    htmlPanel.innerHTML = [component]Html;
    
    // Setup tab switching functionality
    const setupTabs = () => {
        const tabs = document.querySelectorAll('.[component-id]-tab');
        const panels = document.querySelectorAll('.[component-id]-panel');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Update active tab
                tabs.forEach(t => {
                    t.classList.remove('active');
                    t.style.borderBottomColor = 'transparent';
                });
                tab.classList.add('active');
                tab.style.borderBottomColor = '#007bff';
                
                // Show active panel
                const panelId = tab.getAttribute('data-panel') + '-panel';
                panels.forEach(panel => {
                    panel.style.display = 'none';
                    panel.classList.remove('active');
                });
                const activePanel = document.getElementById(panelId);
                if (activePanel) {
                    activePanel.style.display = 'block';
                    activePanel.classList.add('active');
                }
                
                // Update the active tab in the component if it exists
                if (window.[component]Component) {
                    window.[component]Component.activeTab = tab.getAttribute('data-panel');
                }
            });
        });
        
        // Add component-specific event handlers here
    };
    
    // Set up tab functionality after a short delay to ensure DOM is ready
    setTimeout(setupTabs, 100);
    
    // Initialize component service if available
    setTimeout(() => {
        if (window.[component]Service) {
            console.log('Initializing [Component] service');
            window.[component]Service.initialize();
        } else {
            console.log('[Component] service not found, loading required scripts');
            this.load[Component]Scripts();
        }
    }, 200);
    
    // Register the component with a container reference
    const container = document.getElementById('[component-id]-container');
    this.components['[component-id]'] = {
        id: '[component-id]',
        loaded: true,
        usesTerminal: false, // Use HTML panel
        container: container
    };
    
    console.log('[Component] component loaded successfully');
}

/**
 * Load [Component] scripts manually if not already loaded
 */
load[Component]Scripts() {
    console.log('Loading [Component] scripts manually...');
    
    // List of scripts to load
    const scripts = [
        'scripts/[component-id]/[component-id]-service.js',
        'scripts/[component-id]/[component-id]-component.js'
    ];
    
    // Cache busting parameter
    const cacheBuster = `?t=${new Date().getTime()}`;
    
    // Load scripts sequentially
    const loadScript = (index) => {
        if (index >= scripts.length) {
            console.log('All [Component] scripts loaded successfully');
            return;
        }
        
        const scriptPath = scripts[index];
        const scriptElement = document.createElement('script');
        scriptElement.src = `/${scriptPath}${cacheBuster}`;
        scriptElement.onerror = () => {
            console.error(`Failed to load script: ${scriptPath}`);
            // Continue loading other scripts
            loadScript(index + 1);
        };
        scriptElement.onload = () => {
            console.log(`Successfully loaded script: ${scriptPath}`);
            // Load next script
            loadScript(index + 1);
        };
        document.head.appendChild(scriptElement);
    };
    
    // Start loading scripts
    loadScript(0);
}
```

## Customization Points

When adapting this template for a specific component:

1. Replace `[Component]` with the capitalized component name (e.g., "Ergon", "Terma")
2. Replace `[component-id]` with the lowercase component ID (e.g., "ergon", "terma")
3. Replace `[Component Name]` with the display name (e.g., "Ergon Agent Manager")
4. Customize the HTML structure to match the component's specific needs
5. Add component-specific tab panels and functionality
6. Add any component-specific initialization code

## Tab Structure

The tab structure uses a consistent pattern:

1. Each tab has a `data-panel` attribute that matches the ID of its corresponding panel
2. Each panel has an ID that is the tab's `data-panel` value plus "-panel" suffix
3. Clicking a tab shows its corresponding panel and hides all others

## Event Handling

Add component-specific event handlers in the `setupTabs` function:

```javascript
// Example: Setup search functionality
const searchInput = document.getElementById('[component-id]-search');
if (searchInput) {
    searchInput.addEventListener('input', (event) => {
        const searchTerm = event.target.value.toLowerCase();
        // Perform search logic
    });
}
```

## Component Registration

The component is registered with the UI manager with these properties:

```javascript
this.components['[component-id]'] = {
    id: '[component-id]',
    loaded: true,
    usesTerminal: false, // Always false for HTML components
    container: container  // Reference to the container element
};
```

## Script Loading

If needed, provide a script loading function to load the component's JavaScript files:

```javascript
load[Component]Scripts() {
    // Load required script files
}
```

## CSS Handling

Inline styles are used to ensure component styling works correctly without external dependencies. For larger components, consider loading a separate CSS file:

```javascript
// Load CSS if needed
const cssPath = 'styles/[component-id]/[component-id]-component.css';
const linkElement = document.createElement('link');
linkElement.rel = 'stylesheet';
linkElement.href = `/${cssPath}${cacheBuster}`;
document.head.appendChild(linkElement);
```