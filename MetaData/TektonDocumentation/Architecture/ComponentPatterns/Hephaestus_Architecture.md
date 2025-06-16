# Hephaestus Architecture Overview

## System Architecture

Hephaestus is the unified UI component of the Tekton AI orchestration system. This document provides a high-level overview of the architecture, component relationships, and data flow patterns.

## Architectural Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                      HEPHAESTUS UI SYSTEM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    PRESENTATION LAYER                    │   │
│  │                                                         │   │
│  │  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐  │   │
│  │  │  Component    │ │  Terminal     │ │  Graphical    │  │   │
│  │  │  Navigation   │ │  Interface    │ │  Interface    │  │   │
│  │  └───────────────┘ └───────────────┘ └───────────────┘  │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    COMPONENT LAYER                       │   │
│  │                                                         │   │
│  │  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐  │   │
│  │  │  Rhetor       │ │  Engram       │ │  Ergon        │  │   │
│  │  │  Component    │ │  Component    │ │  Component    │  │   │
│  │  └───────────────┘ └───────────────┘ └───────────────┘  │   │
│  │                                                         │   │
│  │  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐  │   │
│  │  │  Terma        │ │  Codex        │ │  Prometheus   │  │   │
│  │  │  Component    │ │  Component    │ │  Component    │  │   │
│  │  └───────────────┘ └───────────────┘ └───────────────┘  │   │
│  │                                                         │   │
│  │  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐  │   │
│  │  │  Settings     │ │  Telos        │ │  Budget       │  │   │
│  │  │  Component    │ │  Component    │ │  Component    │  │   │
│  │  └───────────────┘ └───────────────┘ └───────────────┘  │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   CORE SERVICES LAYER                    │   │
│  │                                                         │   │
│  │  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐  │   │
│  │  │ ComponentLoader│ │ Theme Manager │ │ State Manager │  │   │
│  │  └───────────────┘ └───────────────┘ └───────────────┘  │   │
│  │                                                         │   │
│  │  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐  │   │
│  │  │ UI Manager    │ │ WebSocket     │ │ Component     │  │   │
│  │  │               │ │ Client        │ │ Utilities     │  │   │
│  │  └───────────────┘ └───────────────┘ └───────────────┘  │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  INTEGRATION LAYER                       │   │
│  │                                                         │   │
│  │  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐  │   │
│  │  │ LLM Adapter   │ │ Hermes        │ │ Engram        │  │   │
│  │  │ Integration   │ │ Integration   │ │ Integration   │  │   │
│  │  └───────────────┘ └───────────────┘ └───────────────┘  │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Component Isolation Design

Hephaestus uses Shadow DOM for component isolation, as illustrated below:

```
┌─────────────────────────────────────────────────────────────────┐
│                   HEPHAESTUS MAIN DOM                           │
│                                                                 │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │ Component Host  │ │ Component Host  │ │ Component Host  │   │
│  │                 │ │                 │ │                 │   │
│  │ ┌─────────────┐ │ │ ┌─────────────┐ │ │ ┌─────────────┐ │   │
│  │ │ Shadow Root  │ │ │ Shadow Root  │ │ │ Shadow Root  │ │   │
│  │ │             │ │ │             │ │ │             │ │   │
│  │ │ Component A │ │ │ Component B │ │ │ Component C │ │   │
│  │ │ Content     │ │ │ Content     │ │ │ Content     │ │   │
│  │ │             │ │ │             │ │ │             │ │   │
│  │ │   ┌─────┐   │ │ │   ┌─────┐   │ │ │   ┌─────┐   │ │   │
│  │ │   │HTML │   │ │ │   │HTML │   │ │ │   │HTML │   │ │   │
│  │ │   └─────┘   │ │ │   └─────┘   │ │ │   └─────┘   │ │   │
│  │ │   ┌─────┐   │ │ │   ┌─────┐   │ │ │   ┌─────┐   │ │   │
│  │ │   │CSS  │   │ │ │   │CSS  │   │ │ │   │CSS  │   │ │   │
│  │ │   └─────┘   │ │ │   └─────┘   │ │ │   └─────┘   │ │   │
│  │ │   ┌─────┐   │ │ │   ┌─────┐   │ │ │   ┌─────┐   │ │   │
│  │ │   │JS   │   │ │ │   │JS   │   │ │ │   │JS   │   │ │   │
│  │ │   └─────┘   │ │ │   └─────┘   │ │ │   └─────┘   │ │   │
│  │ │             │ │ │             │ │ │             │ │   │
│  │ └─────────────┘ │ │ └─────────────┘ │ │ └─────────────┘ │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Component File Structure

```
/Hephaestus/ui/
  ├── index.html                 # Main application HTML
  ├── components/
  │   ├── component-name/        # Component HTML
  │   │   └── component-name.html
  │   └── ...
  ├── styles/
  │   ├── main.css               # Global styles
  │   ├── themes/                # Theme definitions
  │   │   ├── dark.css
  │   │   └── light.css
  │   ├── component-name/        # Component CSS
  │   │   └── component-name-component.css
  │   └── ...
  ├── scripts/
  │   ├── main.js                # Application initialization
  │   ├── component-loader.js    # Shadow DOM component loader
  │   ├── ui-manager.js          # UI state and navigation management
  │   ├── component-utils.js     # Shared component utilities
  │   ├── websocket.js           # WebSocket client
  │   ├── component-name/        # Component JavaScript
  │   │   └── component-name-component.js
  │   └── ...
  └── server/
      └── component_registry.json # Component metadata
```

## Component Loading Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  User clicks │     │ UI Manager  │     │ Component   │     │ Shadow DOM  │
│  component   │────▶│ requests    │────▶│ Loader      │────▶│ created for │
│  in nav      │     │ component   │     │ initializes │     │ component   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────┴────────┐
│ Component   │     │ Component   │     │ Component   │     │ Theme vars   │
│ ready for   │◀────│ scripts     │◀────│ styles      │◀────│ added to     │
│ user        │     │ initialized │     │ loaded      │     │ shadow root  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

## Theme Propagation

```
┌─────────────────────────────────────────────────────────────────┐
│                         HTML Root                               │
│                     data-theme="dark"                           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   CSS Variables                          │   │
│  │                                                         │   │
│  │  --bg-primary: #1e1e1e;                                 │   │
│  │  --text-primary: #f0f0f0;                               │   │
│  │  --color-primary: #007bff;                              │   │
│  │  /* ... more variables ... */                           │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                             │                                   │
│                             ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  MutationObserver                        │   │
│  │          (Watches for theme attribute changes)           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                             │                                   │
│                             ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │               ComponentLoader._propagateThemeToComponents│   │
│  └─────────────────────────────────────────────────────────┘   │
│                             │                                   │
│                             ▼                                   │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐│
│  │ Component A    │    │ Component B    │    │ Component C    ││
│  │ Shadow Root    │    │ Shadow Root    │    │ Shadow Root    ││
│  │                │    │                │    │                ││
│  │ :host {        │    │ :host {        │    │ :host {        ││
│  │   --bg-primary:│    │   --bg-primary:│    │   --bg-primary:││
│  │   var(--bg-    │    │   var(--bg-    │    │   var(--bg-    ││
│  │   primary);    │    │   primary);    │    │   primary);    ││
│  │   ...          │    │   ...          │    │   ...          ││
│  │ }              │    │ }              │    │ }              ││
│  └────────────────┘    └────────────────┘    └────────────────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## WebSocket Communication

```
┌─────────────────┐                            ┌─────────────────┐
│                 │                            │                 │
│                 │     1. Connect             │                 │
│                 │ ───────────────────────────▶                 │
│                 │                            │                 │
│                 │                            │                 │
│                 │     2. Message             │                 │
│   Hephaestus    │ ───────────────────────────▶    Backend     │
│     Client      │                            │   Services     │
│                 │     3. Response            │                 │
│                 │ ◀───────────────────────────                 │
│                 │                            │                 │
│                 │                            │                 │
│                 │     4. Events              │                 │
│                 │ ◀───────────────────────────                 │
│                 │                            │                 │
└─────────────────┘                            └─────────────────┘

Message Format:
{
  "type": "COMMAND",
  "source": "UI",
  "target": "COMPONENT_ID",
  "timestamp": "ISO_TIMESTAMP",
  "payload": {
    "command": "ACTION_NAME",
    "data": { ... }
  }
}
```

## Component Integration Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                         COMPONENT                               │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   PRESENTATION                           │   │
│  │                                                         │   │
│  │  • Component-specific HTML structure                    │   │
│  │  • BEM-inspired CSS naming convention                   │   │
│  │  • Responsive design patterns                           │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                             │                                   │
│                             ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   STATE MANAGEMENT                       │   │
│  │                                                         │   │
│  │  • Centralized component state object                   │   │
│  │  • State update functions                               │   │
│  │  • UI reflection of state                               │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                             │                                   │
│                             ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   EVENT HANDLING                         │   │
│  │                                                         │   │
│  │  • User interactions                                    │   │
│  │  • Shadow DOM-scoped event delegation                   │   │
│  │  • Event handlers update component state                │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                             │                                   │
│                             ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   SERVICE INTEGRATION                    │   │
│  │                                                         │   │
│  │  • LLM Adapter client                                   │   │
│  │  • Hermes connector                                     │   │
│  │  • Engram client                                        │   │
│  │  • WebSocket communication                              │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                             │                                   │
│                             ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    LIFECYCLE MANAGEMENT                  │   │
│  │                                                         │   │
│  │  • Initialization                                       │   │
│  │  • Theme handling                                       │   │
│  │  • Resource cleanup                                     │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Component Utilities Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      ComponentUtils                             │
│                                                                 │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │  Notifications  │ │     Loading     │ │     Dialogs     │   │
│  │   System        │ │   Indicators    │ │     System      │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
│                                                                 │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │      Tabs       │ │      Form       │ │      DOM        │   │
│  │     System      │ │   Validation    │ │     Helpers     │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
│                                                                 │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │   Lifecycle     │ │    BaseService  │ │      Theme      │   │
│  │   Management    │ │     Pattern     │ │   Management    │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Service Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       Hephaestus UI                             │
│                                                                 │
│  ┌────────────────────────────────┐                             │
│  │          UI Components         │                             │
│  └───────────────┬────────────────┘                             │
│                  │                                              │
│                  ▼                                              │
│  ┌────────────────────────────────┐                             │
│  │        Service Clients         │                             │
│  └───────────────┬────────────────┘                             │
│                  │                                              │
└──────────────────┼──────────────────────────────────────────────┘
                   │
┌──────────────────┼──────────────────────────────────────────────┐
│  ┌───────────────▼────────────────┐                             │
│  │       LLM Adapter             │                             │
│  └───────────────┬────────────────┘                             │
│                  │                                              │
│  ┌───────────────▼────────────────┐                             │
│  │    Hermes Message Bus          │                             │
│  └───────────────┬────────────────┘                             │
│                  │                                              │
│  ┌───────────────▼────────────────┐                             │
│  │     Engram Memory System       │                             │
│  └────────────────────────────────┘                             │
│                                                                 │
│                 Tekton Backend Services                         │
└─────────────────────────────────────────────────────────────────┘
```

## State Management Flow

```
┌─────────────────┐     ┌─────────────┐     ┌─────────────┐
│  User           │     │ Event       │     │ Component   │
│  Interaction    │────▶│ Handler     │────▶│ State       │
│                 │     │             │     │ Updated     │
└─────────────────┘     └─────────────┘     └─────────────┘
                                                   │
┌─────────────────┐     ┌─────────────┐     ┌─────┴────────┐
│  State          │     │ User        │     │ State        │
│  Persisted      │◀────│ Interface   │◀────│ Change       │
│  (If needed)    │     │ Updated     │     │ Triggers UI  │
└─────────────────┘     └─────────────┘     │ Update       │
                                            └─────────────┘
```

## Conclusion

The Hephaestus architecture emphasizes component isolation, maintainability, and consistent user experience. The Shadow DOM-based approach ensures that components operate independently while still integrating seamlessly into the overall UI. The standardized utilities and services provide a solid foundation for implementing new components or extending existing ones.