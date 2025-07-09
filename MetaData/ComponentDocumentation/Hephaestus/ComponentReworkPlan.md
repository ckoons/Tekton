# Tekton UI Component Rework Plan

## The Problem
Tekton UI has accumulated too much "bullshit from iterative development" with inconsistent patterns across components. Some work, some don't, and debugging is a nightmare.

## The Solution: ONE PATTERN FOR ALL

### Phase 1: Establish the Pattern (COMPLETE)
✅ **Settings Component** - Pure HTML/CSS with radio button pattern
✅ **Rhetor Component** - Enhanced with Models and Prompts tabs following Settings pattern

### Key Lessons from Rhetor UI Work

#### What Works (Copy from Settings)
1. **Hidden radio buttons** for tab switching
   ```html
   <input type="radio" name="rhetor-tab" id="tab-dashboard" checked style="display: none;">
   <label for="tab-dashboard" class="rhetor__tab">Dashboard</label>
   ```
2. **CSS :checked selectors** - No JavaScript needed for tabs
3. **Simple onclick handlers** when absolutely necessary
   ```html
   <div onclick="rhetor_showComponentPrompts('athena')">
   ```

#### What Doesn't Work (Avoid)
1. **Complex DOM manipulation** - Event listeners that never fire
2. **Dynamic element creation** - Just hide/show existing elements
3. **Fancy JavaScript patterns** - Keep it simple

### Phase 2: The Rework Strategy

#### Step-by-Step Component Replacement
1. **Get Rhetor working completely** (if not already)
2. **Get Settings working completely** ✅ (DONE)
3. **Move to next UI component**
4. **Identify exact Menu Bar needed**
5. **RIP OUT entire component**
6. **Install Rhetor-pattern replacement**
7. **Change name/content to match original function**
8. **Verify it works**
9. **Push to GitHub**
10. **Move to next component**

#### Component Priority Order
1. Settings ✅ (COMPLETE)
2. Rhetor (verify complete functionality)
3. Profile
4. Budget
5. Athena
6. Ergon
7. Metis
8. [Continue with remaining components]

### The ONE Pattern Rules

#### 1. Simple HTML Structure
```html
<div class="component-name" data-tekton-area="component-name">
  <!-- Header with title -->
  <div class="component__header">
    <h2 class="component__title">Component Name</h2>
  </div>
  
  <!-- Tab navigation if needed -->
  <div class="component__menu-bar">
    <div class="component__tabs">
      <!-- Radio button controlled tabs -->
    </div>
  </div>
  
  <!-- Content area -->
  <div class="component__content">
    <!-- Component-specific content -->
  </div>
</div>
```

#### 2. CSS-First Interactions
- Use hidden radio buttons/checkboxes for state
- CSS `:checked` selectors for visual changes
- Labels for clickable areas
- Minimal JavaScript only when absolutely necessary

#### 3. Theme Integration
- All components use CSS variables from theme system
- No hardcoded colors
- Respect `data-theme-base` attribute

#### 4. Minimal JavaScript Rules
- Only add JavaScript when CSS can't handle it
- Direct DOM manipulation (no complex frameworks)
- Extensive console logging for debugging
- Simple event listeners on labels/forms

### Example: Settings Pattern (Reference Implementation)

The Settings component demonstrates the pattern:
- **HTML forms** with hidden radio buttons control state
- **CSS selectors** (`#radio:checked ~ .element`) handle visual changes
- **Minimal JavaScript** only applies themes globally
- **Direct approach** - no complex abstractions

### Backend Integration Strategy

Once UI components are standardized:
1. **Identify backend Tekton component**
2. **Map Menu Bar requirements**
3. **Replace UI component with working pattern**
4. **Connect to backend APIs using same pattern**

### Benefits of This Approach

1. **Consistency**: Every component works the same way
2. **Reliability**: Simple patterns are hard to break
3. **Debuggability**: Clear structure, extensive logging
4. **Maintainability**: One pattern to learn/modify
5. **Performance**: Minimal JavaScript, CSS-driven

### Anti-Patterns to Avoid

❌ **Complex frameworks** (React, Vue, Angular)
❌ **Shadow DOM** complications
❌ **Inline scripts** that cause loading issues
❌ **Fancy abstractions** that hide functionality
❌ **Incremental fixes** to broken components

### Success Metrics

- ✅ Component responds to clicks immediately
- ✅ Visual feedback works consistently
- ✅ Theme changes apply correctly
- ✅ No console errors
- ✅ Works after page reload
- ✅ Follows established HTML structure

## Casey's Philosophy

> "I prefer seeing five approaches rather than you implementing the wrong approach."

> "Fancy means you lose fingers."

> "Simple, works, hard to screw up."

The rework plan prioritizes **working over clever**, **simple over complex**, and **reliable over fancy**.