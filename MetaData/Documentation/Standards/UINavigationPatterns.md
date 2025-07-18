# UI Navigation Patterns

*Consistent patterns for Hephaestus UI navigation components*

Created: 2025-01-16  
Author: Claude (with Casey Koons)  
Purpose: Define standard patterns for UI navigation elements

## Table of Contents
1. [Navigation Item Template](#navigation-item-template)
2. [Zone Concepts](#zone-concepts)
3. [Component Naming Rules](#component-naming-rules)
4. [The Greek Chorus Rule](#the-greek-chorus-rule)
5. [Migration Patterns](#migration-patterns)
6. [Real Example: Budget → Penia](#real-example-budget--penia)
7. [Anti-Patterns](#anti-patterns)

## Navigation Item Template

Every navigation item in Hephaestus should follow this exact structure:

```html
<li class="nav-item" 
    data-component="{backend-id}"              <!-- Backend component identifier -->
    data-tekton-nav-item="{nav-id}"           <!-- Navigation identifier -->
    data-tekton-nav-target="{target-id}"      <!-- Target component ID -->
    data-tekton-state="inactive"              <!-- State: inactive|active -->
    data-tekton-zone="{zone}"                 <!-- Zone: greek-chorus|utilities -->
    data-tekton-order="{number}"              <!-- Sort order within zone -->
>
    <!-- Emoji only for utility items, NEVER for Greek components -->
    <span class="button-icon">{emoji}</span>   <!-- Only if zone="utilities" -->
    
    <span class="nav-label" 
          data-greek-name="{Greek} - {Function}"     <!-- Full display name -->
          data-functional-name="{Function}">         <!-- Function only -->
        {Display Name}
    </span>
    
    <span class="status-indicator"></span>      <!-- Health/connection indicator -->
</li>
```

### Required Attributes

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `data-component` | Backend component ID | `"budget"` (even if displayed as Penia) |
| `data-tekton-nav-item` | Navigation tracking | `"budget"` |
| `data-tekton-nav-target` | Click target | `"budget"` |
| `data-tekton-state` | Current state | `"inactive"` or `"active"` |
| `data-tekton-zone` | Navigation zone | `"greek-chorus"` or `"utilities"` |

### Optional Attributes

| Attribute | Purpose | When to Use |
|-----------|---------|-------------|
| `data-tekton-order` | Sort order | When manual ordering needed |
| `data-tekton-legacy-name` | Previous name | During migrations |
| `data-tekton-emoji` | Emoji storage | Empty for Greek, emoji for utilities |

## Zone Concepts

Hephaestus UI organizes navigation into semantic zones:

### 1. Greek Chorus Zone (`data-tekton-zone="greek-chorus"`)
Main Tekton components with Greek mythology names:
- Prometheus, Telos, Ergon, Metis, Harmonia
- Synthesis, Athena, Sophia, Engram, Apollo
- Rhetor, Penia, Hermes, Codex, Terma

**Rules**:
- NO emojis
- Format: `{GreekName} - {Function}`
- Ordered by architectural flow

### 2. Utilities Zone (`data-tekton-zone="utilities"`)
Support functions and user features:
- Profile (👤)
- Settings (⚙️)

**Rules**:
- CAN have emojis
- Simpler naming format
- Usually in footer section

### Zone Structure Example
```html
<!-- Greek Chorus Zone -->
<ul class="component-nav" data-tekton-list="components" data-tekton-zone="greek-chorus">
    <li data-component="rhetor" data-tekton-zone="greek-chorus">
        <span class="nav-label">Rhetor - LLM/Prompt/Context</span>
        <span class="status-indicator"></span>
    </li>
    <!-- More Greek components... -->
</ul>

<!-- Utilities Zone -->
<ul class="component-nav" data-tekton-list="utilities" data-tekton-zone="utilities">
    <li data-component="profile" data-tekton-zone="utilities">
        <span class="button-icon">👤</span>
        <span class="nav-label">Profile</span>
        <span class="status-indicator"></span>
    </li>
    <!-- More utilities... -->
</ul>
```

## Component Naming Rules

### Backend ID vs Display Name

| Layer | Example | Rules |
|-------|---------|-------|
| Backend ID | `data-component="budget"` | NEVER change (breaks backend) |
| Display Name | `"Penia - LLM Cost"` | Can change freely |
| Folder Name | `/components/budget/` | Keep as-is (Python imports) |

### Display Name Format

**Greek Components**:
```
{GreekName} - {Function}
```
Examples:
- `Rhetor - LLM/Prompt/Context`
- `Penia - LLM Cost`
- `Hermes - Messages/Data`

**Utility Components**:
```
{Name}
```
Examples:
- `Profile`
- `Settings`

## The Greek Chorus Rule

**Greek mythology-named components get NO emojis**. This is a firm design decision.

### ✅ Correct Greek Component
```html
<li data-component="budget" data-tekton-zone="greek-chorus">
    <span class="nav-label">Penia - LLM Cost</span>
    <span class="status-indicator"></span>
</li>
```

### ❌ Incorrect Greek Component
```html
<li data-component="budget" data-tekton-zone="greek-chorus">
    <span class="button-icon">💰</span>  <!-- NO! Greek components don't get emojis -->
    <span class="nav-label">Penia - LLM Cost</span>
    <span class="status-indicator"></span>
</li>
```

### ✅ Correct Utility Component
```html
<li data-component="settings" data-tekton-zone="utilities">
    <span class="button-icon">⚙️</span>  <!-- OK! Utilities can have emojis -->
    <span class="nav-label">Settings</span>
    <span class="status-indicator"></span>
</li>
```

## Migration Patterns

When renaming components, follow these patterns to maintain compatibility:

### 1. Add Migration Metadata
```html
<li data-component="budget"                    <!-- Keep backend ID -->
    data-tekton-legacy-name="Budget"          <!-- Document old name -->
    data-tekton-current-name="Penia"          <!-- Document new name -->
    data-tekton-migrated="2025-01-16"        <!-- Migration date -->
>
```

### 2. Update Display Only
```html
<!-- Before -->
<span class="nav-label">Budget - LLM Cost</span>

<!-- After -->
<span class="nav-label">Penia - LLM Cost</span>
```

### 3. Preserve Backend References
- Keep `data-component="budget"`
- Keep folder as `/components/budget/`
- Keep API endpoints as `/api/budget/`

### 4. Document the Change
```html
<!-- Component: Penia (formerly Budget) -->
<!-- Backend ID: budget (unchanged for compatibility) -->
<!-- Display Name: Penia - LLM Cost -->
<!-- Migration Date: 2025-01-16 -->
```

## Real Example: Budget → Penia

Here's the actual migration performed on 2025-01-16:

### What Changed:
1. **Display name**: "Budget - LLM Cost" → "Penia - LLM Cost"
2. **Emoji removed**: 💰 → (none)
3. **Position moved**: Footer → Main nav (between Rhetor and Hermes)
4. **Zone changed**: utilities → greek-chorus

### What Stayed the Same:
1. **Backend ID**: `data-component="budget"`
2. **Folder structure**: `/components/budget/`
3. **Port**: 8013
4. **Status color**: Green (#34A853)

### The Code Change:
```html
<!-- Before (in footer) -->
<li class="nav-item" data-component="budget" data-tekton-nav-item="budget">
    <span class="button-icon">💰</span>
    <span class="nav-label">Budget - LLM Cost</span>
    <span class="status-indicator" style="background-color: #34A853;"></span>
</li>

<!-- After (in main nav) -->
<li class="nav-item" data-component="budget" data-tekton-nav-item="budget">
    <span class="nav-label">Penia - LLM Cost</span>
    <span class="status-indicator" style="background-color: #34A853;"></span>
</li>
```

### Lessons Learned:
- UI changes are safe when backend IDs are preserved
- Moving between zones requires manual editing
- Removing emojis aligns with Greek component standards
- Position in nav affects user perception of component importance

## Anti-Patterns

### ❌ Don't Change Backend IDs
```html
<!-- WRONG: This breaks everything -->
<li data-component="penia">  <!-- Backend still expects "budget" -->
```

### ❌ Don't Mix Zone Conventions
```html
<!-- WRONG: Greek component with emoji -->
<li data-component="athena" data-tekton-zone="greek-chorus">
    <span class="button-icon">🦉</span>  <!-- No emojis for Greek! -->
```

### ❌ Don't Forget Migration Metadata
```html
<!-- WRONG: No trace of the change -->
<li data-component="budget">
    <span class="nav-label">Penia - LLM Cost</span>
    <!-- Where's the legacy name? When did this change? -->
</li>
```

### ❌ Don't Use Inconsistent Formatting
```html
<!-- WRONG: Missing function description -->
<span class="nav-label">Penia</span>  <!-- Should be "Penia - LLM Cost" -->
```

## Best Practices

1. **Always preserve backend IDs** - Display names can change, IDs cannot
2. **Follow zone conventions** - Greek components are emoji-free
3. **Document migrations** - Future developers need context
4. **Test navigation after changes** - Ensure clicks still work
5. **Update related documentation** - Don't leave outdated references

## Related Documentation

- [UI DevTools Cookbook](../Guides/UIDevToolsCookbook.md) - Practical examples
- [Semantic UI Navigation Guide](../Guides/SemanticUINavigationGuide.md) - Tag system
- [UI DevTools Explicit Guide](../Guides/UIDevToolsExplicitGuide.md) - Tool reference

---

*Remember: The UI is the user's window into Tekton. Keep it consistent, clear, and maintainable.*