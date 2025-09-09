# Rhetor Memory Tab - UI Specification

## Overview
The Memory tab will be added to the Rhetor UI tab bar. It follows the exact same visual framework as the Models tab, maintaining consistency with footer and chat area always visible. Additionally, a universal CI selector will be added to all data tabs (Models, Prompts, Contexts, Memory) to support Greek Chorus, Terminal, and Project CIs.

## Layout Structure

### Tab Position
The Memory tab will be added to the existing tab bar alongside Models, Prompts, Contexts, Specialists, etc.

### Universal CI Selector (NEW - For all data tabs)
A CI selector bar will be added between the tab header and content on Models, Prompts, Contexts, and Memory tabs:

```html
<div class="rhetor__ci-selector-bar">
  <div class="rhetor__ci-selector-label">
    CI Configuration:
  </div>
  
  <select class="rhetor__ci-selector-dropdown" id="rhetor-ci-selector">
    <optgroup label="Greek Chorus">
      <option value="apollo-ci">Apollo - Insight</option>
      <option value="athena-ci">Athena - Knowledge</option>
      <option value="ergon-ci">Ergon - Solutions</option>
      <!-- All Greek Chorus CIs -->
    </optgroup>
    
    <optgroup label="Terminal CIs">
      <!-- Dynamically populated from registry -->
    </optgroup>
    
    <optgroup label="Project CIs">
      <!-- Dynamically populated from registry -->
    </optgroup>
    
    <option value="all">── All CIs ──</option>
  </select>
  
  <div class="rhetor__ci-type-pills">
    <label><input type="radio" name="ci-type" value="all" checked> All</label>
    <label><input type="radio" name="ci-type" value="greek"> Greek Chorus</label>
    <label><input type="radio" name="ci-type" value="terminal"> Terminals</label>
    <label><input type="radio" name="ci-type" value="project"> Projects</label>
  </div>
</div>
```

### Memory Panel Structure (Following Models Pattern)
```html
<div id="memory-panel" class="rhetor__panel">
  <div class="rhetor__memory-container" data-tekton-scrollable="true">
    
    <!-- Section 1: Memory Statistics (like Provider Status) -->
    <div class="rhetor__memory-section">
      <h3 class="rhetor__memory-section-title">Memory Statistics</h3>
      <div class="rhetor__memory-stats-grid">
        <!-- Stats cards similar to provider cards -->
      </div>
    </div>
    
    <!-- Section 2: Memory Catalog (like Model Assignment Matrix) -->
    <div class="rhetor__memory-section">
      <div class="rhetor__memory-section-header">
        <h3 class="rhetor__memory-section-title">Memory Catalog</h3>
        <div class="rhetor__memory-actions">
          <button class="rhetor__button">Refresh</button>
          <button class="rhetor__button rhetor__button--error">Clear Old</button>
        </div>
      </div>
      <div class="rhetor__memory-catalog">
        <!-- Memory items list/table -->
      </div>
    </div>
    
    <!-- Section 3: Memory Search (consistent with Models layout) -->
    <div class="rhetor__memory-section">
      <h3 class="rhetor__memory-section-title">Search & Filter</h3>
      <div class="rhetor__memory-search">
        <!-- Search controls -->
      </div>
    </div>
    
  </div>
</div>
```

## Component Details

### Memory Statistics Cards
Similar to Provider cards in Models tab:
```html
<div class="rhetor__memory-stat-card">
  <div class="rhetor__memory-stat-header">
    <span class="rhetor__memory-stat-name">Total Memories</span>
    <span class="rhetor__memory-stat-value">247</span>
  </div>
  <div class="rhetor__memory-stat-info">
    <span class="rhetor__memory-stat-detail">15.2K tokens</span>
    <div class="rhetor__memory-stat-bar">
      <div class="rhetor__memory-stat-bar-fill" style="width: 45%"></div>
    </div>
  </div>
</div>
```

### Memory Catalog Table
Following the Model Assignment Matrix pattern:
```html
<table class="rhetor__memory-table">
  <thead>
    <tr>
      <th class="rhetor__memory-time">Time</th>
      <th class="rhetor__memory-ci">CI Source</th>
      <th class="rhetor__memory-type">Type</th>
      <th class="rhetor__memory-summary">Summary</th>
      <th class="rhetor__memory-tokens">Tokens</th>
      <th class="rhetor__memory-priority">Priority</th>
      <th class="rhetor__memory-actions">Actions</th>
    </tr>
  </thead>
  <tbody>
    <tr class="rhetor__memory-row">
      <td class="rhetor__memory-time">2m ago</td>
      <td class="rhetor__memory-ci">
        <span class="rhetor__ci-badge rhetor__ci-badge--ergon">Ergon</span>
      </td>
      <td class="rhetor__memory-type">
        <span class="rhetor__type-badge rhetor__type-badge--decision">Decision</span>
      </td>
      <td class="rhetor__memory-summary">Chose Redux for state management</td>
      <td class="rhetor__memory-tokens">245</td>
      <td class="rhetor__memory-priority">
        <select class="rhetor__priority-select">
          <option value="0">0 - Low</option>
          <option value="5" selected>5 - Normal</option>
          <option value="10">10 - Critical</option>
        </select>
      </td>
      <td class="rhetor__memory-actions">
        <button class="rhetor__memory-btn" title="View Details">👁</button>
        <button class="rhetor__memory-btn" title="Delete">🗑</button>
      </td>
    </tr>
  </tbody>
</table>
```

### Search and Filter Section
```html
<div class="rhetor__memory-search-container">
  <div class="rhetor__memory-search-row">
    <input type="text" 
           class="rhetor__memory-search-input" 
           placeholder="Search memories..."
           id="memory-search-input">
    
    <select class="rhetor__memory-filter-select" id="memory-ci-filter">
      <option value="">All CIs</option>
      <option value="ergon-ci">Ergon</option>
      <option value="apollo-ci">Apollo</option>
      <!-- Dynamic CI list -->
    </select>
    
    <select class="rhetor__memory-filter-select" id="memory-type-filter">
      <option value="">All Types</option>
      <option value="decision">Decisions</option>
      <option value="insight">Insights</option>
      <option value="context">Context</option>
      <option value="error">Errors</option>
    </select>
    
    <button class="rhetor__button rhetor__button--primary" onclick="rhetor_searchMemories()">
      Search
    </button>
  </div>
  
  <div class="rhetor__memory-token-display">
    <span>Token Usage: </span>
    <span class="rhetor__token-count">1,245 / 2,000</span>
    <div class="rhetor__token-bar">
      <div class="rhetor__token-bar-fill" style="width: 62%"></div>
    </div>
  </div>
</div>
```

## CSS Classes (Matching Models Pattern)

```css
/* Container - matching .rhetor__models-container */
.rhetor__memory-container {
  /* Exact same as .rhetor__models-container */
}

/* Sections - matching .rhetor__models-section */
.rhetor__memory-section {
  /* Exact same as .rhetor__models-section */
}

/* Table - matching .rhetor__model-matrix */
.rhetor__memory-table {
  /* Exact same as .rhetor__model-matrix */
}

/* Cards - matching .rhetor__provider-card */
.rhetor__memory-stat-card {
  /* Exact same as .rhetor__provider-card */
}
```

## JavaScript Functions

```javascript
// Load memory catalog
window.rhetor_loadMemoryCatalog = async function() {
  // Similar pattern to rhetor_loadModelAssignments
}

// Search memories
window.rhetor_searchMemories = async function() {
  // Implement search with filters
}

// Update priority
window.rhetor_updateMemoryPriority = async function(memoryId, priority) {
  // Update memory priority
}

// Delete memory
window.rhetor_deleteMemory = async function(memoryId) {
  // Delete with confirmation
}

// View memory details
window.rhetor_viewMemoryDetails = async function(memoryId) {
  // Show modal with full content
}
```

## Visual Consistency Requirements

1. **Exact same scrollable container** behavior as Models tab
2. **Same section spacing and borders** 
3. **Same button styles** (primary, error, etc.)
4. **Same table styling** with hover effects
5. **Same card grid layout** for statistics
6. **Footer and chat area remain visible** (not scrolled)

## Color Coding for Memory Types

Using existing Rhetor color palette:
- **Decision**: `#4CAF50` (green)
- **Insight**: `#2196F3` (blue)  
- **Context**: `#9C27B0` (purple)
- **Error**: `#F44336` (red)
- **Plan**: `#FF9800` (orange)

## Responsive Behavior

- Cards stack on mobile (like provider cards)
- Table becomes scrollable horizontally on small screens
- Search filters stack vertically on mobile
- Maintains footer visibility at all breakpoints

## State Management

```javascript
// Global CI selection state (shared across tabs)
let selectedCI = {
  type: 'all',  // 'all', 'greek', 'terminal', 'project'
  id: 'all',    // specific CI ID or 'all'
  info: null
};

// Memory catalog state
let memoryCatalogState = {
  memories: [],
  statistics: {},
  filters: {
    search: '',
    ci: '',
    type: ''
  }
};

// Update on load (like originalAssignments pattern)
let originalMemories = null;

// CI change handler
window.rhetor_onCIChange = function(ciId) {
  selectedCI.id = ciId;
  selectedCI.type = detectCIType(ciId);
  
  // Reload current tab with new CI context
  const currentTab = document.querySelector('input[name="rhetor-tabs"]:checked').id;
  if (currentTab === 'rhetor-memory-tab') {
    rhetor_loadMemoryCatalog(ciId);
  } else if (currentTab === 'rhetor-models-tab') {
    rhetor_loadModelAssignments(ciId);
  }
  // etc...
};
```

## Integration Points

1. **On tab click**: Load memory catalog (lazy loading like Models)
2. **Auto-refresh**: Every 30 seconds when tab is active
3. **WebSocket updates**: Real-time memory additions
4. **Export function**: Download memories as JSON

This specification ensures the Memory tab integrates seamlessly with the existing Rhetor UI, maintaining exact visual and behavioral consistency with the Models tab.