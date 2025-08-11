# Apollo UI Specification

## Overview
Apollo is the "frontal lobe" of the Tekton system - an executive coordinator and predictive planning system that manages CI (Claude Intelligence) working memory and context. It serves as an "air traffic controller" for all CIs, monitoring their operational health, managing token budgets, and ensuring behavioral reliability through predictive analytics.

## Core Concept
Apollo operates on a **turn-based system** where:
- Each prompt/response pair = 1 turn
- Apollo prepares context for the next turn while CIs process current turns
- Focus on token burn awareness and capacity (NOT costs - that's Penia's role)
- Implements sundown/sunrise workflow when CIs exceed 50% context capacity

## UI Requirements

### Layout Structure
1. **Header** - Fixed at top of window
   - Apollo logo/icon
   - Title: "Apollo" with subtitle "Attention/Prediction"
   - Must remain visible at all times

2. **Menu Bar** - Fixed below header
   - 6 tabs: Dashboard, Token Management, Protocols, Actions, Attention Chat, Team Chat
   - Radio button-based navigation (CSS-only, no JavaScript for tabs)
   - Must remain visible at all times

3. **Content Area** - Scrollable
   - Only this section scrolls
   - Contains the active panel content

4. **Footer** - Fixed at bottom
   - Chat input interface (already working - DO NOT MODIFY)
   - Must remain visible at all times

## Panel Specifications

### 1. Dashboard Panel
**Purpose**: CI Master Registry - Air Traffic Control view of all active CIs

**Display Requirements**:
- Grid of CI cards showing real-time status
- Each CI card must show:
  - CI Name and Type (Coder-A, Apollo, Athena, etc.)
  - Current State: Idle → Preparing → Active → Stressed → Degrading → Completing → Sundown
  - Burn Rate (tokens/min)
  - Last Action taken
  - Next Predicted action
  - Time to Sundown (remaining context capacity)
  - Visual stress indicators (color-coded)

**Priority Focus**: Coder CIs should be prominently displayed as they need the most management

### 2. Token Management Panel
**Purpose**: Operational stress monitor and burn rate projections

**Display Requirements**:
- Table format showing all CIs
- Columns:
  - CI Name with priority indicator
  - Type
  - Current Burn Rate with trend arrow
  - Next Turn Projection with confidence %
  - Budget Status (progress bar showing used/total)
  - Stress Level (with visual indicators)
  - Time Remaining

**Key Metrics**:
- System-wide burn rate summary
- Critical CI count
- Next turn load projection
- Overall stress percentage

### 3. Protocols Panel
**Purpose**: Context management rules and CI optimization protocols

**Display Requirements**:
- Card-based layout for different protocols
- Each protocol card shows:
  - Protocol name and type
  - Description
  - Effectiveness percentage
  - Last triggered time
  - Settings/parameters (adjustable sliders)

**Core Protocols to Display**:
- Memory Management (prefetch, compression)
- Context Optimization
- Quality Assurance
- Sundown/Sunrise procedures
- Task completion verification

### 4. Actions Panel
**Purpose**: CI action queue management and turn planning

**Display Requirements**:
- Action management table showing:
  - CI Name
  - Current State
  - Last Action (with timestamp and result)
  - Next Planned Action (with priority)
  - Context Preparation Status (progress bar + component checklist)
  - Success Predictions (percentage for different outcomes)

**Context Components Checklist**:
- Role ✓/⏳
- Task Definition ✓/⏳
- Success Criteria ✓/⏳
- Tools ✓/⏳
- Memories ✓/⏳
- Query Results ✓/⏳
- Structured Data ✓/⏳

**Action Controls**:
- Emergency Compress All Critical
- Optimize All Contexts
- Refresh All Memories

### 5. Attention Chat Panel
**Purpose**: Direct LLM interaction for attention and prioritization
- Standard chat interface (already implemented)
- DO NOT MODIFY - working correctly

### 6. Team Chat Panel
**Purpose**: Multi-CI coordination chat
- Standard chat interface (already implemented)
- DO NOT MODIFY - working correctly

## Visual Design Requirements

### Color Scheme
- Primary: Orange/Gold (#FF9500) - Apollo's attention theme
- Status Colors:
  - Active: Green (#28a745)
  - Preparing: Blue (#17a2b8)
  - Stressed: Yellow (#ffc107)
  - Degrading: Orange (#fd7e14)
  - Critical: Red (#dc3545)

### UI Components
- **Cards**: Rounded corners, subtle shadows, hover effects
- **Tables**: Clean borders, alternating row colors, sortable headers
- **Progress Bars**: Smooth animations, color-coded by stress level
- **Buttons**: Clear CTAs, disabled states, hover feedback

### Responsive Design
- Cards should reflow on smaller screens
- Tables should remain readable (horizontal scroll if needed)
- Maintain fixed header/footer on all screen sizes

## Technical Requirements

### CSS-First Approach
- Use radio buttons for tab switching (no JavaScript)
- All panels defined in HTML, shown/hidden via CSS
- Smooth transitions between states
- Clean, semantic HTML structure

### Performance
- Efficient CSS selectors
- Minimal reflows/repaints
- Smooth scrolling in content area
- Quick tab switching

## Implementation Notes

### Starting Point
- Reference implementation: `/ui/components/apollo/apollo-component.html.old`
- Current broken version: `/ui/components/apollo/apollo-component.html`
- Chat functionality is working - DO NOT modify chat-related code
- Focus only on fixing the panel displays and layout

### File Locations
- HTML Component: `/ui/components/apollo/apollo-component.html`
- CSS Styles: Create at `/ui/styles/apollo/apollo-component.css`
- Reference patterns from: `/ui/styles/rhetor/rhetor-component.css`

### CI Registry Details
Display these CIs grouped by type:
- **Coder CIs**: Coder-A (Primary), Coder-B (Secondary)
- **Project CIs**: Apollo, Tekton, Hephaestus
- **Terminal CIs**: Terminal-1, Terminal-2
- **Greek Chorus CIs**: Athena, Rhetor, Engram, Hermes

### Current Issues to Fix
1. UI displays as plain text strings instead of formatted components
2. No visual styling applied to panels
3. Layout doesn't have fixed header/footer with scrollable content
4. Missing card and table formatting

### Priority Order
1. Fix layout structure (fixed header/footer, scrollable content)
2. Style Dashboard cards properly
3. Format Token Management table
4. Style Actions panel
5. Format Protocols cards
6. Ensure all text is readable and properly styled

### Backend Integration
Apollo backend exists at `/Apollo/apollo/api/` with these endpoints:
- `GET /api/sessions` - Active CI sessions
- `GET /api/metrics` - Token usage and burn rates
- `GET /api/budgets` - Budget allocations and limits
- `GET /api/forecasts` - Prediction data
- `WebSocket /ws` - Real-time updates

### HTML Structure Pattern
Follow Tekton component patterns:
- Use `data-tekton-*` attributes for consistency
- Structure: header → menu → content → footer
- Each panel in a div with class `apollo__panel`
- Radio button pattern for tab switching

## Success Criteria
- Clean, professional "air traffic control" aesthetic
- Information dense but not cluttered
- Clear visual hierarchy
- Instant understanding of CI states
- Smooth interactions
- Fixed header/footer with scrollable content
- All panels display as proper cards/tables, not text strings