# Apollo & Metis Navigation Implementation Approach

This document outlines the specific implementation approach for adding the Apollo and Metis navigation tabs to the Tekton LEFT PANEL.

## Navigation Tab HTML Structure

### Apollo Tab (Between Engram and Rhetor)

The Apollo tab will be inserted in the LEFT PANEL navigation at line 156 in `index.html`, between the Engram and Rhetor tabs:

```html
<li class="nav-item" data-component="apollo">
    <span class="nav-label" data-greek-name="Apollo - Attention/Prediction" data-functional-name="Attention/Prediction">Apollo - Attention/Prediction</span>
    <span class="status-indicator"></span>
</li>
```

### Metis Tab (Between Ergon and Harmonia)

The Metis tab will be inserted in the LEFT PANEL navigation at line 136 in `index.html`, between the Ergon and Harmonia tabs:

```html
<li class="nav-item" data-component="metis">
    <span class="nav-label" data-greek-name="Metis - Workflows" data-functional-name="Workflows">Metis - Workflows</span>
    <span class="status-indicator"></span>
</li>
```

## Color Indicator CSS

The following CSS will be added to the component-specific styles section (starting around line 21):

```css
.nav-item[data-component="apollo"] .status-indicator { 
    background-color: #FFD600; /* Amber/Golden Yellow */
}
.nav-item[data-component="metis"] .status-indicator { 
    background-color: #00BFA5; /* Mint/Turquoise */
}
```

## Space Optimization Changes

To accommodate the additional tabs, the following CSS adjustments will be made:

1. Reduce the size of the navigation items:

```css
/* Original (approximate values) */
.nav-item {
    padding: 12px 16px;
    height: 20px;
}

/* Modified (6% reduction) */
.nav-item {
    padding: 11px 16px; /* Reduced vertical padding by ~8% */
    height: 18px; /* Reduced height by 10% */
}
```

2. Adjust the footer navigation buttons to match:

```css
/* Adjust footer navigation buttons to match main navigation */
.footer-buttons .control-button {
    padding: 11px 16px !important; /* Match main navigation padding */
    height: 18px !important; /* Match main navigation height */
}
```

3. Adjust the component navigation container padding:

```css
/* Original (approximate) */
.component-nav {
    padding: 10px 0;
}

/* Modified */
.component-nav {
    padding: 8px 0; /* Reduced vertical padding by 20% */
}
```

4. Optional: Adjust the `.left-panel-nav` padding if needed:

```css
/* If additional space optimization is needed */
.left-panel-nav {
    padding-top: 5px;
    padding-bottom: 5px;
}
```

## Implementation Steps

1. **Backup the original files**:
   ```bash
   cp /Users/cskoons/projects/github/Tekton/Hephaestus/ui/index.html /Users/cskoons/projects/github/Tekton/Hephaestus/ui/index.html.bak
   ```

2. **Add color indicator CSS**:
   - Add the Apollo and Metis color indicator styles to the component-specific styles section

3. **Insert navigation tabs**:
   - Add the Apollo tab HTML between Engram and Rhetor
   - Add the Metis tab HTML between Ergon and Harmonia

4. **Adjust spacing CSS**:
   - Modify the `.nav-item` CSS to reduce height and padding
   - Adjust the `.component-nav` padding if needed
   - Further adjust `.left-panel-nav` if more space optimization is required

5. **Create component placeholder files**:
   - Create `/components/apollo/apollo-component.html` based on existing component templates
   - Create `/components/metis/metis-component.html` based on existing component templates

6. **Test and verify**:
   - Load the UI and check visual appearance
   - Verify all tabs fit without scrolling
   - Test navigation functionality 
   - Adjust as needed for optimal appearance

## Component Placeholder Files

### Apollo Component Placeholder

Create a minimal placeholder at `/components/apollo/apollo-component.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        /* Apollo component styles */
        .apollo__container {
            width: 100%;
            height: 100%;
            padding: 20px;
            box-sizing: border-box;
            color: var(--text-color, #f0f0f0);
            background-color: var(--background-color, #1a1a1a);
            font-family: var(--font-family, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif);
        }
        
        .apollo__header {
            margin-bottom: 20px;
        }
        
        .apollo__content {
            height: calc(100% - 60px);
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="apollo__container">
        <div class="apollo__header">
            <h2>Apollo - Attention/Prediction</h2>
            <p>This component is under development.</p>
        </div>
        <div class="apollo__content">
            <p>Apollo will provide attention mechanisms and prediction capabilities for the Tekton system.</p>
            <p>Features will include:</p>
            <ul>
                <li>Attention management for multi-modal inputs</li>
                <li>Prediction of user intent and system needs</li>
                <li>Proactive resource allocation based on predictions</li>
                <li>Integration with Engram's memory systems and Rhetor's LLM capabilities</li>
            </ul>
        </div>
    </div>
    
    <script>
        // Apollo component initialization script
        document.addEventListener('DOMContentLoaded', function() {
            // Debug instrumentation
            if (window.TektonDebug) {
                TektonDebug.log('apollo', 'Apollo component loaded', 'info');
            }
            
            console.log('Apollo component placeholder loaded');
        });
    </script>
</body>
</html>
```

### Metis Component Placeholder

Create a minimal placeholder at `/components/metis/metis-component.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        /* Metis component styles */
        .metis__container {
            width: 100%;
            height: 100%;
            padding: 20px;
            box-sizing: border-box;
            color: var(--text-color, #f0f0f0);
            background-color: var(--background-color, #1a1a1a);
            font-family: var(--font-family, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif);
        }
        
        .metis__header {
            margin-bottom: 20px;
        }
        
        .metis__content {
            height: calc(100% - 60px);
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="metis__container">
        <div class="metis__header">
            <h2>Metis - Workflow</h2>
            <p>This component is under development.</p>
        </div>
        <div class="metis__content">
            <p>Metis will provide advanced workflow management for the Tekton system.</p>
            <p>Features will include:</p>
            <ul>
                <li>Workflow definition and management</li>
                <li>Process orchestration between Ergon agents and Harmonia systems</li>
                <li>Task scheduling and tracking</li>
                <li>Integration with other Tekton components for seamless workflow execution</li>
            </ul>
        </div>
    </div>
    
    <script>
        // Metis component initialization script
        document.addEventListener('DOMContentLoaded', function() {
            // Debug instrumentation
            if (window.TektonDebug) {
                TektonDebug.log('metis', 'Metis component loaded', 'info');
            }
            
            console.log('Metis component placeholder loaded');
        });
    </script>
</body>
</html>
```

## Verification Checklist

After implementation, verify:

- [ ] Apollo tab appears between Engram and Rhetor
- [ ] Metis tab appears between Ergon and Harmonia
- [ ] Both tabs have the correct color indicators
- [ ] All tabs fit in the LEFT PANEL without scrolling
- [ ] Tab text is fully visible and readable
- [ ] Clicking tabs works correctly
- [ ] Placeholder components load when tabs are clicked
- [ ] No visual glitches or UI issues are present

## Next Steps

After implementation and verification, the following next steps are recommended:

1. Update component registry to include Apollo and Metis
2. Document the new components in the appropriate documentation
3. Prepare for future implementation of actual component functionality