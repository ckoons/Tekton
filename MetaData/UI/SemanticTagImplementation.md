# Semantic Tag Implementation Guide
**Version**: 1.0
**Created**: 2025-01-15
**Purpose**: Step-by-step guide for implementing semantic tags across Tekton UI

## Implementation Order

### Phase 1: Navigation Infrastructure
Tag all navigation elements first to establish the "highway system":

1. **Left Panel Navigation** (`/Hephaestus/ui/index.html`)
   - Main nav container: `data-tekton-nav="main"`
   - Each nav item: `data-tekton-nav-item="[component-name]"`
   - Active states: `data-tekton-state="active|inactive"`

2. **Component Tabs** (all component HTML files)
   - Tab containers: `data-tekton-nav="component"`
   - Individual tabs: `data-tekton-tab="[tab-name]"`

### Phase 2: Component Containers
Tag all major component areas:

1. **Component Files to Update**:
   - `/Hephaestus/ui/components/rhetor/rhetor-component.html` ✓ (already started)
   - `/Hephaestus/ui/components/athena/athena-component.html`
   - `/Hephaestus/ui/components/apollo/apollo-component.html`
   - `/Hephaestus/ui/components/budget/budget-component.html`
   - `/Hephaestus/ui/components/engram/engram-component.html`
   - `/Hephaestus/ui/components/metis/metis-component.html`
   - `/Hephaestus/ui/components/prometheus/prometheus-component.html`
   - `/Hephaestus/ui/components/telos/telos-component.html`
   - `/Hephaestus/ui/components/harmonia/harmonia-component.html`
   - `/Hephaestus/ui/components/synthesis/synthesis-component.html`
   - `/Hephaestus/ui/components/sophia/sophia-component.html`
   - `/Hephaestus/ui/components/ergon/ergon-component.html`

2. **Standard Tags per Component**:
   ```html
   <div class="[component-name]" 
        data-tekton-area="[component-name]"
        data-tekton-component="[component-name]"
        data-tekton-type="component-workspace">
   ```

### Phase 3: Interactive Elements
Tag all buttons, forms, and controls:

1. **Action Buttons**
   - Create/Add buttons: `data-tekton-action="create"`
   - Delete/Remove: `data-tekton-action="delete"`
   - Refresh/Reload: `data-tekton-action="refresh"`
   - Submit/Save: `data-tekton-action="submit"`

2. **Forms and Inputs**
   - Form containers: `data-tekton-form="[form-purpose]"`
   - Input fields: `data-tekton-field="[field-name]"`

### Phase 4: Chat Interfaces
Tag all chat/communication areas:

1. **Chat Containers**
   - Main chat div: `data-tekton-chat="[component]-chat"`
   - Message area: `data-tekton-chat-messages="true"`
   - Input field: `data-tekton-chat-input="true"`
   - Send button: `data-tekton-chat-send="true"`

2. **AI Integration**
   - Specialist assignment: `data-tekton-ai="[specialist-id]"`
   - Connection status: `data-tekton-ai-ready="false"` (updated dynamically)

### Phase 5: Status and State
Tag all dynamic status indicators:

1. **Status Areas**
   - Connection status: `data-tekton-status="connection"`
   - Loading states: `data-tekton-state="loading"`
   - Error states: `data-tekton-state="error"`

## Implementation Checklist

### For Each Component:
- [ ] Component container tagged with area, component, and type
- [ ] Navigation/tabs tagged with appropriate nav attributes
- [ ] All buttons tagged with action and trigger
- [ ] Forms tagged with form and field attributes
- [ ] Chat interface tagged (if present)
- [ ] Status indicators tagged
- [ ] AI specialist mapping added (if applicable)

### Global Elements:
- [ ] Main navigation panel tagged
- [ ] Status bar tagged (if exists)
- [ ] Modal/dialog containers tagged
- [ ] Error/notification areas tagged

## Testing the Implementation

### Manual Verification:
1. Open browser DevTools
2. Use selector: `[data-tekton-*]` to find all tagged elements
3. Verify tag hierarchy and consistency

### UI DevTools Verification:
```bash
# Use UI DevTools to scan for semantic tags
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "ui_analyze",
    "arguments": {
      "component": "all",
      "semantic_scan": true
    }
  }'
```

## Maintenance Protocol

### When Adding New UI Elements:
1. Consult SemanticTagConventions.md
2. Apply appropriate tags immediately
3. Update documentation if new patterns emerge

### When Modifying Existing UI:
1. Preserve existing semantic tags
2. Update state/status tags as needed
3. Test AI navigation after changes

## Success Metrics
- All major UI elements are tagged
- AI can navigate to any component/feature
- UI DevTools can identify all interactive elements
- Tags follow consistent conventions
- Documentation stays current

## Next Steps After Tagging
1. Test AI navigation with simple queries
2. Update UI DevTools to leverage semantic tags
3. Begin component AI integration using established patterns
4. Create automated tag validation tests