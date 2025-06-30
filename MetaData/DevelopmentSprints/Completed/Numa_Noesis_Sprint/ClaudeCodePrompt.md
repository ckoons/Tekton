# Claude Code Prompt for Numa/Noesis Debugging

## Context

You are continuing work on the Numa and Noesis components that were just implemented. These are new Tekton components that need debugging to fully integrate with the UI system. This prompt provides all necessary context and pointers to understand and fix the issues.

## Current Issues to Fix

### 1. UI Component Loading Problem (CRITICAL)
**Symptom**: When clicking the Numa nav tab, it loads the Profile component instead of Numa
**Expected**: Clicking Numa should load the Numa component with its Companion chat interface
**Investigation Path**:
- Check `/Hephaestus/ui/scripts/ui-manager-core.js` - activateComponent method
- Trace through `/Hephaestus/ui/scripts/minimal-loader.js` - how it loads components
- Verify `/Hephaestus/ui/scripts/ui-utils.js` - activatePanel method
- The issue appears to be that activateComponent doesn't automatically call activatePanel('html')

### 2. Default Component Not Loading
**Symptom**: UI shows terminal on startup even though Numa is set as default
**Expected**: UI should load Numa component and show HTML panel on startup
**Investigation Path**:
- Check ui-manager-core.js line 10: `this.activeComponent = 'numa'`
- Verify the init() method properly activates the default component
- May need to also set activePanel to 'html' and call activatePanel

### 3. Noesis Footer Styling
**Symptom**: Footer doesn't match Rhetor's styling
**Expected**: Footer should be identical to Rhetor's footer
**Fix**: Copy exact footer HTML and CSS from Rhetor component

### 4. Hermes Registration Failure
**Symptom**: Both components failing with 422 validation error
**Error**: `{"detail":[{"type":"missing","loc":["body","address"],"msg":"Field required"}]}`
**Fix**: Add 'address' field to registration payload in both app.py files

## Key Documentation to Review

### Component Architecture
- `/MetaData/UI/ComponentImplementationStandard.md` - How components should be built
- `/Rhetor/` - Reference implementation to copy patterns from
- `/MetaData/TektonDocumentation/Architecture/SinglePort/` - Port management approach

### UI System
- `/Hephaestus/ui/scripts/minimal-loader.js` - Component loading mechanism
- `/Hephaestus/ui/scripts/ui-manager-core.js` - Navigation and activation
- `/Hephaestus/ui/scripts/ui-utils.js` - Panel switching utilities
- `/Hephaestus/ui/components/rhetor/` - Reference UI component

### Configuration
- `/shared/utils/env_config.py` - Environment configuration (NO hardcoded ports!)
- `/shared/utils/env_manager.py` - Environment validation
- `/.env.tekton` - Environment variables

## Understanding the UI Loading Process

1. **Navigation Click**: User clicks a nav item with `data-component="numa"`
2. **activateComponent**: ui-manager-core.js activateComponent method is called
3. **Component Loading**: minimal-loader.js loads the component HTML/CSS/JS
4. **Panel Switching**: MISSING - need to call activatePanel('html') for HTML components
5. **Component Display**: Component should appear in the HTML panel

## Critical Files to Examine

```bash
# UI Loading Chain
/Hephaestus/ui/scripts/ui-manager-core.js  # activateComponent method
/Hephaestus/ui/scripts/minimal-loader.js   # loadComponent method
/Hephaestus/ui/scripts/ui-utils.js        # activatePanel method

# Component Files
/Numa/numa/api/app.py                      # Fix registration payload
/Noesis/noesis/api/app.py                  # Fix registration payload
/Hephaestus/ui/components/numa/numa-component.html
/Hephaestus/ui/components/noesis/noesis-component.html

# Reference Implementation
/Rhetor/rhetor/api/app.py                  # Check registration format
/Hephaestus/ui/components/rhetor/rhetor-component.html  # Copy footer
```

## Testing Your Fixes

1. **Start the system**:
   ```bash
   cd $TEKTON_ROOT
   ./enhanced_tekton_launcher.sh
   ```

2. **Check component status**:
   ```bash
   tekton-status
   ```
   - All components should show green checkmarks
   - Registration (Reg) should show ✓ not ❌

3. **Test UI loading**:
   - Open browser to Hephaestus UI
   - Should see Numa loaded by default (not terminal)
   - Click between Numa and Noesis tabs
   - Both should show their respective interfaces

## Debug Approach

1. **Add console.log statements** to trace the loading process:
   ```javascript
   console.log('[DEBUG] activateComponent called with:', componentId);
   console.log('[DEBUG] Current panel:', this.activePanel);
   ```

2. **Check browser console** for errors when clicking nav tabs

3. **Use UI DevTools** if needed (see CLAUDE.md for usage)

4. **Test incrementally** - fix one issue at a time and verify

## Unix Philosophy Reminder

Remember: "AIs just read and write files" - keep solutions simple and file-based. Don't add complexity where it's not needed.

## Expected Outcome

After your fixes:
1. Numa loads on startup showing Companion chat
2. Clicking nav tabs properly loads each component
3. All components have consistent dark theme styling
4. tekton-status shows all green checkmarks

Good luck debugging! Casey prefers seeing multiple approaches discussed before implementation, so feel free to analyze and propose solutions before making changes.