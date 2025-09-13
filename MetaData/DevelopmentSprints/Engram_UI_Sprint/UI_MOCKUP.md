# Engram UI Mockup Specifications

## Cognition Panel Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Cognition                                    [CI: Apollo ▼]     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────┐  ┌─────────────────┐ │
│  │                                       │  │ Metrics:        │ │
│  │         Brain Visualization           │  │ □ Mood          │ │
│  │                                       │  │ ☑ Working Memory│ │
│  │     ┌─────────┐   ┌─────────┐       │  │ □ Stress        │ │
│  │     │Prefrontal│   │Temporal │       │  │ ☑ Processing    │ │
│  │     │ ██████  │   │  ░░░░░  │       │  │ □ Flow          │ │
│  │     └─────────┘   └─────────┘       │  │ □ Confidence    │ │
│  │          ┌─────────┐                 │  │ □ Motivation    │ │
│  │          │Hippocamp│                 │  │ ☑ Associations  │ │
│  │          │ ▓▓▓▓▓▓ │                 │  │ □ Recall        │ │
│  │          └─────────┘                 │  │ □ Forethought   │ │
│  │     ┌─────────┐   ┌─────────┐       │  │ □ Performance   │ │
│  │     │Amygdala │   │ Motor   │       │  │                 │ │
│  │     │  ████   │   │  ░░░░░  │       │  ├─────────────────┤ │
│  │     └─────────┘   └─────────┘       │  │ Regions:        │ │
│  │                                       │  │ □ All           │ │
│  └──────────────────────────────────────┘  │ ☑ Frontal       │ │
│                                              │ □ Temporal      │ │
│  ┌──────────────────────────────────────┐  │ □ Limbic        │ │
│  │ Timeline                             │  │ □ Motor         │ │
│  │ |----●---------------------------|   │  └─────────────────┘ │
│  │ 1hr ago                      Now     │                      │
│  │ [◀] [▶] [||] Speed: 1x              │                      │
│  └──────────────────────────────────────┘                      │
│                                                                  │
│  Activity Feed:                                                 │
│  • Working memory consolidated 3 thoughts (2 min ago)           │
│  • Emotional peak detected: Joy 0.8 (5 min ago)                │
│  • Pattern recognized: "User frustration cycle" (7 min ago)    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Legend:
██ = High activation (red)
▓▓ = Medium activation (yellow)
░░ = Low activation (blue)
```

## Memories Panel Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Memories                                     [CI: Apollo ▼]     │
├─────────────────────────────────────────────────────────────────┤
│ [Browse] [Create] [Search] [Edit] [Timeline]                    │
├─────────────────────────────────────────────────────────────────┤
│ Filters: [All Types ▼] [All Times ▼] [All Emotions ▼]          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────┐  ┌─────────────────────┐              │
│  │ Memory Card          │  │ Memory Card          │              │
│  │ Title: Auth Discussion│ │ Title: Bug Fix       │              │
│  │ Type: Conversation   │  │ Type: Task           │              │
│  │ Date: 2 hours ago    │  │ Date: 1 day ago      │              │
│  │ Emotion: 😊 Joy      │  │ Emotion: 😤 Frustration           │
│  │ Preview: Discussed... │  │ Preview: Fixed the...│              │
│  │ [View] [Edit] [Delete]│ │ [View] [Edit] [Delete]│             │
│  └─────────────────────┘  └─────────────────────┘              │
│                                                                  │
│  ┌─────────────────────┐  ┌─────────────────────┐              │
│  │ Memory Card          │  │ Memory Card          │              │
│  │ Title: Pattern Found │  │ Title: Team Meeting  │              │
│  │ Type: Insight        │  │ Type: Conversation   │              │
│  │ Date: 3 days ago     │  │ Date: 1 week ago     │              │
│  │ Emotion: 😮 Surprise │  │ Emotion: 😊 Joy      │              │
│  │ Preview: Discovered...│ │ Preview: Team discussed...       │
│  │ [View] [Edit] [Delete]│ │ [View] [Edit] [Delete]│             │
│  └─────────────────────┘  └─────────────────────┘              │
│                                                                  │
│  [← Previous] Page 1 of 15 [Next →]                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Patterns Panel Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Patterns                    [CI: All CIs ▼] [Detect Patterns]   │
├─────────────────────────────────────────────────────────────────┤
│ Filter: [All Patterns ▼]    Visualization: [Stream|Graph|Pulse] │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Pattern Flow Stream:                                           │
│                                                                  │
│  Emerging ~~~~~~~~                                              │
│           ╱                                                     │
│     ═════════════> "Code Review Stress" (Strengthening)        │
│           ╲                                                     │
│            ~~~~~~~~                                             │
│                                                                  │
│     ░░░░░░░░░░░░> "Morning Productivity" (Stable)              │
│                                                                  │
│            ········> "Debug Frustration" (Fading)              │
│                                                                  │
│     ◉◉◉◉◉◉◉◉◉◉◉> "Success Celebration" (Cyclical)             │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Pattern Details: Code Review Stress                     │    │
│  │ Occurrences: 15 times over 2 weeks                     │    │
│  │ Triggers: PR comments, merge conflicts                 │    │
│  │ Associated Emotions: Anxiety (0.7), Frustration (0.5)  │    │
│  │ Affected CIs: Apollo, Athena                          │    │
│  │ Recommendation: Schedule reviews during low-stress times│    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Discovery Feed:                                                │
│  • New pattern emerging: "Documentation Joy" (10 min ago)      │
│  • Pattern strengthening: "Test Success" (1 hour ago)          │
│  • Pattern fading: "Monday Blues" (3 hours ago)                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Legend:
═══> Strong pattern (thick line)
───> Medium pattern (normal line)
···> Weak pattern (dotted line)
~~~> Emerging pattern (wavy line)
◉◉◉> Cyclical pattern (circles)
```

## Visual Design Specifications

### Color Palette
- **Background**: #1e1e2e (Tekton dark)
- **Panel Background**: #252535
- **Borders**: #444444
- **Text Primary**: #f0f0f0
- **Text Secondary**: #a0a0a0

### Brain Heat Map Colors
- **High Activation**: #FF4444 (red)
- **Medium Activation**: #FFAA00 (orange)
- **Low Activation**: #4444FF (blue)
- **Inactive**: #333333 (dark gray)

### Emotional Colors
- **Joy**: #4CAF50 (green)
- **Sadness**: #2196F3 (blue)
- **Anger**: #F44336 (red)
- **Fear**: #9C27B0 (purple)
- **Surprise**: #FF9800 (orange)
- **Trust**: #00BCD4 (cyan)

### Animation Specifications
- **Pulse Effect**: 0.5-2Hz for active regions
- **Connection Lines**: Fade in/out over 500ms
- **Heat Map Transitions**: 200ms ease-out
- **Pattern Flow**: Continuous scroll at 10px/sec

### Responsive Breakpoints
- **Desktop**: 1920px (full layout)
- **Laptop**: 1366px (compact controls)
- **Tablet**: 1024px (stacked layout)
- **Mobile**: Not supported (observation-focused)

## Interaction Patterns

### Cognition Panel
- Click brain region → Show detailed metrics
- Hover region → Tooltip with current values
- Drag timeline → Scrub through history
- Toggle metric → Update heat map instantly

### Memories Panel
- Click card → Expand with full content
- Drag card → Reorder or categorize
- Double-click → Edit mode
- Right-click → Context menu

### Patterns Panel
- Click pattern → Show details panel
- Hover → Preview connections
- Drag → Rearrange in graph view
- Double-click → Filter memories by pattern

## Data Update Frequencies
- **Brain Visualization**: 10Hz (100ms)
- **Activity Feed**: Real-time (as events occur)
- **Pattern Detection**: Every 30 seconds
- **Memory Cards**: On-demand refresh
- **Timeline Playback**: 30fps when scrubbing