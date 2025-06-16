# Codex Architecture Diagram

```mermaid
graph TD
    subgraph "Tekton UI"
        tekton_ui["Tekton UI"]
        right_panel["RIGHT PANEL\n(Codex UI)"]
        right_footer["RIGHT FOOTER\n(Chat Input)"]
    end

    subgraph "Codex Frontend"
        codex_connector["codex_connector.js"]
        component_html["component_template.html"]
    end

    subgraph "Codex Backend"
        codex_server["codex_server.py\n(FastAPI Server)"]
        
        subgraph "Adapter Layer"
            aider_adapter["CodexAiderAdapter\n(aider_adapter.py)"]
            ws_handler["WebSocketHandler\n(websocket_handler.py)"]
        end
        
        subgraph "Process Management"
            aider_process["AiderProcess\n(Subprocess)"]
            input_queue["Input Queue"]
            output_queue["Output Queue"]
            files_queue["Files Queue"]
        end
    end

    subgraph "Aider Core"
        aider_core["Aider Core\n(AI Pair Programming)"]
        repo_integration["Repository Integration"]
        git_integration["Git Integration"]
        io_handling["Custom IO Handling"]
    end

    subgraph "Hermes Integration"
        hermes_registry["Hermes Service Registry"]
        registration_script["register_with_hermes.py"]
    end

    %% Frontend connections
    tekton_ui --> right_panel
    tekton_ui --> right_footer
    right_panel --> codex_connector
    right_footer --> codex_connector
    codex_connector --> component_html

    %% HTTP/WebSocket connections
    codex_connector <-->|"WebSocket\n/ws/codex"| codex_server
    codex_connector -->|"HTTP API\n/api/codex/*"| codex_server

    %% Backend components
    codex_server --> aider_adapter
    codex_server --> ws_handler
    aider_adapter --> ws_handler
    aider_adapter --> aider_process

    %% Process communication
    aider_process <-->|"IPC"| input_queue
    aider_process <-->|"IPC"| output_queue
    aider_process <-->|"IPC"| files_queue
    aider_adapter -->|"Write"| input_queue
    aider_adapter <--"|Read"| output_queue
    aider_adapter <--"|Read"| files_queue

    %% Aider core connections
    aider_process --> aider_core
    aider_core --> repo_integration
    aider_core --> git_integration
    aider_core --> io_handling
    io_handling --> input_queue
    io_handling --> output_queue
    io_handling --> files_queue

    %% Hermes registration
    registration_script --> hermes_registry
    codex_server -.->|"Runtime\nDiscovery"| hermes_registry

    %% Styling
    classDef tekton fill:#d4f0fd,stroke:#0091ea,stroke-width:2px;
    classDef frontend fill:#ffe0b2,stroke:#ff9800,stroke-width:2px;
    classDef backend fill:#c8e6c9,stroke:#4caf50,stroke-width:2px;
    classDef adapter fill:#81c784,stroke:#2e7d32,stroke-width:2px;
    classDef process fill:#a5d6a7,stroke:#388e3c,stroke-width:2px;
    classDef aider fill:#bbdefb,stroke:#1976d2,stroke-width:2px;
    classDef hermes fill:#e1bee7,stroke:#8e24aa,stroke-width:2px;

    class tekton_ui,right_panel,right_footer tekton;
    class codex_connector,component_html frontend;
    class codex_server backend;
    class aider_adapter,ws_handler adapter;
    class aider_process,input_queue,output_queue,files_queue process;
    class aider_core,repo_integration,git_integration,io_handling aider;
    class hermes_registry,registration_script hermes;
```

## Component Descriptions

### Tekton UI Integration
- **Tekton UI**: Main UI framework hosting Codex
- **RIGHT PANEL**: Displays the Codex UI for interaction with Aider
- **RIGHT FOOTER**: Provides the chat input interface for sending commands to Aider

### Codex Frontend
- **codex_connector.js**: JavaScript module handling UI interactions and WebSocket communication
- **component_template.html**: HTML template defining the structure and styling of the Codex UI

### Codex Backend
- **codex_server.py**: FastAPI server providing HTTP and WebSocket endpoints
- **CodexAiderAdapter**: Core adapter connecting Tekton and Aider
- **WebSocketHandler**: Manages WebSocket communication with the UI
- **AiderProcess**: Runs Aider in a separate process for stability
- **Input/Output/Files Queues**: Inter-process communication channels

### Aider Core
- **Aider Core**: AI pair programming engine
- **Repository Integration**: Handles file operations and codebase navigation
- **Git Integration**: Provides version control functionality
- **Custom IO Handling**: Modified IO routines for integration with Tekton

### Hermes Integration
- **Hermes Service Registry**: Central registry for Tekton components
- **register_with_hermes.py**: Script to register Codex with Hermes

## Communication Flows

1. **User Input Flow**:
   - User enters text in RIGHT FOOTER
   - Input is sent to codex_connector.js
   - codex_connector.js sends input to codex_server.py via WebSocket or HTTP
   - codex_server.py forwards input to CodexAiderAdapter
   - CodexAiderAdapter places input in the input queue
   - AiderProcess reads from input queue and processes with Aider
   
2. **Output Flow**:
   - Aider generates output
   - Custom IO handling places output in output queue
   - CodexAiderAdapter reads from output queue
   - CodexAiderAdapter forwards output to WebSocketHandler
   - WebSocketHandler sends output to codex_connector.js via WebSocket
   - codex_connector.js updates the UI with the output

3. **File Tracking Flow**:
   - Aider tracks modified or referenced files
   - File information is placed in files queue
   - CodexAiderAdapter reads from files queue
   - WebSocketHandler sends file list to codex_connector.js
   - codex_connector.js updates the file list in the UI