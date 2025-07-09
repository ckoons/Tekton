# Rhetor UI Update - Models & Prompts Tabs

## What Was Done

### 1. Converted Rhetor to Radio Button Pattern
- Removed complex JavaScript onclick handlers
- Added hidden radio buttons for tab switching (copied from Settings)
- CSS `:checked` selectors handle tab visibility
- Fixed LLM Chat send functionality to work with new pattern

### 2. Created Models Tab
- **Provider Status Cards**: Shows Anthropic, OpenAI, Ollama status
- **Model Assignment Matrix**: All 16 Tekton components with model selection
- **Model Testing Interface**: Test prompts with different models
- **Anthropic Max Toggle**: Enable/disable premium models (visual only)

### 3. Created Prompts Tab  
- **Component Grid**: 16 colorful buttons (including Tekton Core)
- **Multi-Prompt Editor**: 4-layer prompt system
  - System Prompt (shared by all)
  - Initial Prompt (component identity & role)
  - Component Prompt (specific directives)
  - Task-Specific Prompt (current task)
- **All Prompts Pre-populated**: Each component has initial & component prompts

## How It Works

### Tab Switching (No JavaScript!)
```html
<input type="radio" name="rhetor-tab" id="tab-prompts" style="display: none;">
<label for="tab-prompts" class="rhetor__tab">Prompts</label>
```

### Component Clicks (Simple onclick)
```html
<div class="rhetor__component-prompt-card" onclick="rhetor_showComponentPrompts('athena')">
  <div class="rhetor__component-prompt-name">Athena - Knowledge</div>
</div>
```

### Show/Hide Functions
```javascript
function rhetor_showComponentPrompts(componentName) {
    const editor = document.querySelector('.rhetor__multi-prompt-editor');
    if (editor) {
        editor.style.display = 'block';
        // Update component name in header
    }
}
```

## What's NOT Connected Yet

1. **Models Tab**:
   - Provider status is static (not checking real status)
   - Model assignments don't save
   - Test interface doesn't actually test
   - Anthropic Max toggle is visual only

2. **Prompts Tab**:
   - Prompts are hardcoded in JavaScript
   - No save/load to backend
   - Template library below is static
   - Quick Actions not implemented

## Next Steps

1. Connect to rhetor-service.js for template CRUD
2. Wire up model selection to backend
3. Implement prompt saving/loading
4. Add real provider status checking

## Key Lessons

1. **Copy Settings Pattern**: Hidden radios + CSS = reliable tabs
2. **Simple onclick**: Better than complex event listeners
3. **Pre-populate Content**: Users see value immediately
4. **Colorful UI**: Each component has unique color for recognition

## Files Modified

- `/ui/components/rhetor/rhetor-component.html` - All changes in one file
- No other files touched - self-contained component

The UI is visually complete and partially functional. Backend integration can be added incrementally without breaking the UI.