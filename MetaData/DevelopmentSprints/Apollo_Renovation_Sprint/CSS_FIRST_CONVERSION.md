# Apollo CSS-First Tab Conversion

## What Was Done

### 1. Added Hidden Radio Inputs
Added 8 hidden radio inputs at the top of the component:
```html
<input type="radio" name="apollo-tab" id="apollo-tab-dashboard" checked style="display: none;">
<input type="radio" name="apollo-tab" id="apollo-tab-sessions" style="display: none;">
<!-- ... etc for all 8 tabs -->
```

### 2. Converted Tab Divs to Labels
Changed all tab divs from:
```html
<div class="apollo__tab" onclick="apollo_switchTab('dashboard')">
```

To:
```html
<label for="apollo-tab-dashboard" class="apollo__tab">
```

### 3. Added CSS Rules
Added CSS rules to handle tab switching based on radio button state:
- Hide all panels by default
- Show active tab styling when radio is checked
- Show corresponding panel when tab is checked
- Handle Clear button visibility for chat tabs

### 4. Removed onclick Handlers
- Removed all `onclick="apollo_switchTab()"` from tabs
- Removed `onclick="apollo_clearChat()"` from Clear button
- JavaScript functions still exist but are no longer used

## Result
The Apollo component now uses CSS-first tab navigation following the Settings component pattern. No JavaScript is required for basic tab switching.

## Next Steps
1. Test the tab switching works correctly
2. Update JavaScript to handle data loading when tabs are selected
3. Remove mock data and connect to real API endpoints
4. Clean up unused JavaScript functions after testing