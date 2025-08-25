# Terma Technical Documentation

## Overview

Terma is an advanced terminal system designed for integration with the Tekton ecosystem, providing rich terminal functionality with PTY-based terminal sessions, WebSocket communication, LLM assistance, and UI integration. It serves as a comprehensive terminal solution that can be embedded in other applications (particularly the Hephaestus UI) or used as a standalone service.

## System Architecture

Terma follows a layered architecture with clear separation of concerns:

```
┌───────────────────────────────────────────┐
│                   UI Layer                │
│ (terma-component.html, terma-terminal.js) │
└───────────────────────────────────────────┘
                     ▲
                     │
                     ▼
┌───────────────────────────────────────────┐
│               API Layer                   │
│       (app.py, websocket.py, ui_server.py)│
└───────────────────────────────────────────┘
                     ▲
                     │
                     ▼
┌───────────────────────────────────────────┐
│               Core Layer                  │
│ (terminal.py, session_manager.py, llm_adapter.py) │
└───────────────────────────────────────────┘
                     ▲
                     │
                     ▼
┌───────────────────────────────────────────┐
│           Integration Layer               │
│       (hermes_integration.py)             │
└───────────────────────────────────────────┘
```

### Core Layer

The core layer handles terminal session management, PTY processes, and interactions with LLMs.

#### Key Components:

1. **TerminalSession** (`terminal.py`): Manages individual terminal sessions with PTY (pseudoterminal) interfaces.

```python
class TerminalSession:
    """A terminal session with a PTY interface."""
    
    def __init__(
        self,
        session_id: str,
        shell_command: str = None,
        env: Dict[str, str] = None,
        cwd: str = None,
        cols: int = 80,
        rows: int = 24
    ):
        """Initialize a terminal session."""
        self.session_id = session_id
        self.shell_command = shell_command or os.environ.get('SHELL', '/bin/bash')
        self.env = env or os.environ.copy()
        self.cwd = cwd or os.path.expanduser('~')
        self.cols = cols
        self.rows = rows
        self.process = None
        self.created_at = time.time()
        self.last_activity = time.time()
        self.buffer = bytearray()
        self.lock = asyncio.Lock()
        self.active = False
        self._initialize_process()
    
    def _initialize_process(self):
        """Initialize the PTY process."""
        try:
            self.process = ptyprocess.PtyProcessUnicode.spawn(
                self.shell_command.split(),
                env=self.env,
                cwd=self.cwd,
                dimensions=(self.rows, self.cols)
            )
            self.active = True
        except Exception as e:
            logger.error(f"Failed to initialize process: {e}")
            raise TerminalError(f"Failed to initialize process: {e}")
    
    async def read(self, timeout: float = 0.1) -> str:
        """Read output from the terminal."""
        async with self.lock:
            self.last_activity = time.time()
            try:
                output = self.process.read(timeout=timeout)
                return output
            except EOFError:
                self.active = False
                return "[Process terminated]\r\n"
            except Exception as e:
                logger.error(f"Error reading from process: {e}")
                return f"[Error: {e}]\r\n"
    
    async def write(self, data: str) -> bool:
        """Write input to the terminal."""
        async with self.lock:
            self.last_activity = time.time()
            if not self.active:
                return False
            try:
                self.process.write(data)
                return True
            except Exception as e:
                logger.error(f"Error writing to process: {e}")
                return False
    
    async def resize(self, cols: int, rows: int) -> bool:
        """Resize the terminal."""
        async with self.lock:
            self.cols = cols
            self.rows = rows
            if not self.active:
                return False
            try:
                self.process.setwinsize(rows, cols)
                return True
            except Exception as e:
                logger.error(f"Error resizing terminal: {e}")
                return False
    
    async def close(self) -> bool:
        """Close the terminal session."""
        async with self.lock:
            if not self.active:
                return True
            try:
                self.process.close(force=True)
                self.active = False
                return True
            except Exception as e:
                logger.error(f"Error closing process: {e}")
                return False
    
    def is_alive(self) -> bool:
        """Check if the process is still alive."""
        if not self.active:
            return False
        try:
            return self.process.isalive()
        except Exception:
            return False
```

2. **SessionManager** (`session_manager.py`): Creates, manages, and monitors multiple terminal sessions.

```python
class SessionManager:
    """Manager for terminal sessions."""
    
    def __init__(
        self,
        max_sessions: int = 100,
        idle_timeout: int = 3600,
        cleanup_interval: int = 300
    ):
        """Initialize the session manager."""
        self.sessions: Dict[str, TerminalSession] = {}
        self.max_sessions = max_sessions
        self.idle_timeout = idle_timeout
        self.cleanup_interval = cleanup_interval
        self.lock = asyncio.Lock()
        self.websocket_connections: Dict[str, List[WebSocket]] = {}
        self.llm_adapter = LLMAdapter()
        self.cleanup_task = None
    
    async def initialize(self):
        """Initialize the session manager."""
        await self.llm_adapter.initialize()
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        return True
    
    async def create_session(
        self,
        shell_command: str = None,
        env: Dict[str, str] = None,
        cwd: str = None,
        cols: int = 80,
        rows: int = 24
    ) -> str:
        """Create a new terminal session."""
        async with self.lock:
            if len(self.sessions) >= self.max_sessions:
                raise TerminalError("Maximum number of sessions reached")
            
            session_id = f"sess-{uuid.uuid4().hex[:10]}"
            try:
                session = TerminalSession(
                    session_id=session_id,
                    shell_command=shell_command,
                    env=env,
                    cwd=cwd,
                    cols=cols,
                    rows=rows
                )
                self.sessions[session_id] = session
                self.websocket_connections[session_id] = []
                logger.info(f"Session created: {session_id}")
                return session_id
            except Exception as e:
                logger.error(f"Failed to create session: {e}")
                raise TerminalError(f"Failed to create session: {e}")
    
    async def get_session(self, session_id: str) -> TerminalSession:
        """Get a terminal session by ID."""
        session = self.sessions.get(session_id)
        if not session:
            raise TerminalError(f"Session not found: {session_id}")
        return session
    
    async def close_session(self, session_id: str) -> bool:
        """Close a terminal session."""
        async with self.lock:
            session = await self.get_session(session_id)
            success = await session.close()
            if success:
                del self.sessions[session_id]
                # Notify connected websockets
                for ws in self.websocket_connections.get(session_id, []):
                    await self._notify_session_closed(ws, session_id)
                del self.websocket_connections[session_id]
                logger.info(f"Session closed: {session_id}")
            return success
    
    async def write_to_session(self, session_id: str, data: str) -> bool:
        """Write data to a terminal session."""
        session = await self.get_session(session_id)
        return await session.write(data)
    
    async def read_from_session(self, session_id: str, timeout: float = 0.1) -> str:
        """Read data from a terminal session."""
        session = await self.get_session(session_id)
        return await session.read(timeout=timeout)
    
    async def resize_session(self, session_id: str, cols: int, rows: int) -> bool:
        """Resize a terminal session."""
        session = await self.get_session(session_id)
        return await session.resize(cols, rows)
    
    async def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions."""
        return [
            {
                "session_id": s.session_id,
                "created_at": s.created_at,
                "last_activity": s.last_activity,
                "shell_command": s.shell_command,
                "cwd": s.cwd,
                "active": s.is_alive(),
                "idle_time": time.time() - s.last_activity
            }
            for s in self.sessions.values()
        ]
    
    async def register_websocket(self, session_id: str, websocket: WebSocket) -> bool:
        """Register a WebSocket connection to a session."""
        async with self.lock:
            if session_id not in self.sessions:
                return False
            if session_id not in self.websocket_connections:
                self.websocket_connections[session_id] = []
            self.websocket_connections[session_id].append(websocket)
            return True
    
    async def unregister_websocket(self, session_id: str, websocket: WebSocket) -> bool:
        """Unregister a WebSocket connection from a session."""
        async with self.lock:
            if session_id not in self.websocket_connections:
                return False
            if websocket in self.websocket_connections[session_id]:
                self.websocket_connections[session_id].remove(websocket)
            return True
    
    async def broadcast_to_session(self, session_id: str, message: Dict[str, Any]) -> int:
        """Broadcast a message to all WebSocket connections for a session."""
        count = 0
        if session_id not in self.websocket_connections:
            return count
        
        dead_websockets = []
        for ws in self.websocket_connections[session_id]:
            try:
                await ws.send_json(message)
                count += 1
            except WebSocketDisconnect:
                dead_websockets.append(ws)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")
                dead_websockets.append(ws)
        
        # Clean up dead websockets
        async with self.lock:
            for ws in dead_websockets:
                if ws in self.websocket_connections[session_id]:
                    self.websocket_connections[session_id].remove(ws)
        
        return count
    
    async def get_llm_assistance(
        self,
        session_id: str,
        query: str,
        context: str = None,
        model: str = None,
        stream: bool = False
    ) -> Union[str, AsyncIterable[str]]:
        """Get LLM assistance for a terminal query."""
        session = await self.get_session(session_id)
        
        # Get context from terminal history if not provided
        if context is None:
            # Simple approach: just get the recent output
            context = await session.read(timeout=0.1)
        
        return await self.llm_adapter.get_assistance(
            query=query,
            context=context,
            model=model,
            stream=stream
        )
    
    async def _cleanup_loop(self):
        """Periodically clean up idle sessions."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_idle_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def _cleanup_idle_sessions(self):
        """Close idle sessions."""
        now = time.time()
        to_close = []
        
        async with self.lock:
            for session_id, session in self.sessions.items():
                if now - session.last_activity > self.idle_timeout:
                    to_close.append(session_id)
        
        for session_id in to_close:
            try:
                await self.close_session(session_id)
                logger.info(f"Closed idle session: {session_id}")
            except Exception as e:
                logger.error(f"Error closing idle session {session_id}: {e}")
    
    async def _notify_session_closed(self, websocket: WebSocket, session_id: str):
        """Notify a WebSocket that its session was closed."""
        try:
            await websocket.send_json({
                "type": "error",
                "data": "Session closed",
                "code": "session_closed"
            })
        except Exception:
            pass
    
    async def dispose(self):
        """Clean up resources."""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            
        async with self.lock:
            for session_id in list(self.sessions.keys()):
                try:
                    await self.close_session(session_id)
                except Exception:
                    pass
        
        await self.llm_adapter.dispose()
```

3. **LLMAdapter** (`llm_adapter.py`): Facilitates communication with language models for terminal assistance.

```python
class LLMAdapter:
    """Adapter for LLM integration."""
    
    def __init__(self):
        """Initialize the LLM adapter."""
        self.providers = {}
        self.default_provider = os.environ.get("TERMA_LLM_PROVIDER", "rhetor")
        self.default_model = os.environ.get("TERMA_LLM_MODEL", None)
        self.client = None
    
    async def initialize(self) -> bool:
        """Initialize the LLM adapter."""
        try:
            # Try to import tekton_llm_client
            from tekton_llm_client import TektonLLMClient
            
            # Create client
            self.client = TektonLLMClient()
            await self.client.initialize()
            
            # Get available providers
            providers = await self.client.list_providers()
            self.providers = {p["id"]: p for p in providers}
            
            if not self.providers:
                logger.warning("No LLM providers available")
                
            return True
        except ImportError:
            logger.warning("tekton_llm_client not available, using fallback")
            # Fallback to direct connection to Rhetor
            try:
                self.client = RhetorFallbackClient()
                await self.client.initialize()
                self.providers = {"rhetor": {"id": "rhetor", "name": "Rhetor Fallback"}}
                return True
            except Exception as e:
                logger.error(f"Failed to initialize LLM adapter: {e}")
                return False
        except Exception as e:
            logger.error(f"Failed to initialize LLM adapter: {e}")
            return False
    
    async def get_assistance(
        self,
        query: str,
        context: str = None,
        model: str = None,
        stream: bool = False
    ) -> Union[str, AsyncIterable[str]]:
        """Get LLM assistance for a terminal query."""
        if not self.client:
            raise TerminalError("LLM adapter not initialized")
        
        try:
            # Prepare prompt
            prompt = self._prepare_terminal_prompt(query, context)
            
            # Use the specified model or default
            provider = self.default_provider
            provider_model = model or self.default_model
            
            if stream:
                return self._stream_completion(prompt, provider, provider_model)
            else:
                return await self._get_completion(prompt, provider, provider_model)
        except Exception as e:
            logger.error(f"Error getting LLM assistance: {e}")
            raise TerminalError(f"Failed to get LLM assistance: {e}")
    
    async def _get_completion(
        self,
        prompt: str,
        provider: str,
        model: str = None
    ) -> str:
        """Get a completion from the LLM."""
        try:
            response = await self.client.generate_completion(
                prompt=prompt,
                provider=provider,
                model=model,
                max_tokens=1000,
                temperature=0.3
            )
            return response.completion
        except Exception as e:
            logger.error(f"Error getting completion: {e}")
            return f"Error getting assistance: {e}"
    
    async def _stream_completion(
        self,
        prompt: str,
        provider: str,
        model: str = None
    ) -> AsyncIterable[str]:
        """Stream a completion from the LLM."""
        try:
            async for chunk in self.client.stream_completion(
                prompt=prompt,
                provider=provider,
                model=model,
                max_tokens=1000,
                temperature=0.3
            ):
                yield chunk
        except Exception as e:
            logger.error(f"Error streaming completion: {e}")
            yield f"Error getting assistance: {e}"
    
    def _prepare_terminal_prompt(self, query: str, context: str = None) -> str:
        """Prepare a prompt for terminal assistance."""
        prompt = "You are an expert Unix/Linux terminal assistant. "
        prompt += "Answer questions about terminal commands, explain output, and provide clear, concise help.\n\n"
        
        if context:
            prompt += f"Recent terminal context:\n```\n{context}\n```\n\n"
        
        prompt += f"User question: {query}\n\n"
        prompt += "Provide a helpful, accurate response with examples where appropriate. "
        prompt += "Include command syntax when relevant."
        
        return prompt
    
    async def dispose(self):
        """Clean up resources."""
        if self.client:
            await self.client.close()
```

### API Layer

The API layer exposes the core functionality through HTTP and WebSocket interfaces.

#### Key Components:

1. **FastAPI Application** (`app.py`): Provides REST API endpoints for terminal session management.

```python
# Initialize FastAPI app
app = FastAPI(title="Terma Terminal Service", version="1.0.0")

# Initialize session manager
session_manager = SessionManager()

@app.on_event("startup")
async def startup():
    """Initialize the service on startup."""
    await session_manager.initialize()

@app.on_event("shutdown")
async def shutdown():
    """Clean up resources on shutdown."""
    await session_manager.dispose()

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time()
    }

@app.post("/api/sessions")
async def create_session(
    request: SessionCreateRequest = Body(...)
):
    """Create a new terminal session."""
    try:
        session_id = await session_manager.create_session(
            shell_command=request.shell_command,
            env=request.env,
            cwd=request.cwd,
            cols=request.cols,
            rows=request.rows
        )
        return {
            "session_id": session_id,
            "created_at": time.time(),
            "shell_command": request.shell_command or os.environ.get('SHELL', '/bin/bash'),
            "status": "active"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions")
async def list_sessions():
    """List all terminal sessions."""
    try:
        sessions = await session_manager.list_sessions()
        return {
            "sessions": sessions,
            "count": len(sessions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/{session_id}")
async def get_session(
    session_id: str
):
    """Get details for a terminal session."""
    try:
        session = await session_manager.get_session(session_id)
        return {
            "session_id": session.session_id,
            "created_at": session.created_at,
            "last_activity": session.last_activity,
            "shell_command": session.shell_command,
            "cwd": session.cwd,
            "active": session.is_alive(),
            "idle_time": time.time() - session.last_activity
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/api/sessions/{session_id}")
async def close_session(
    session_id: str
):
    """Close a terminal session."""
    try:
        success = await session_manager.close_session(session_id)
        if success:
            return {"status": "closed", "session_id": session_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to close session")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/sessions/{session_id}/input")
async def send_input(
    session_id: str,
    input_data: SessionInputRequest = Body(...)
):
    """Send input to a terminal session."""
    try:
        success = await session_manager.write_to_session(session_id, input_data.data)
        if success:
            return {"status": "sent", "session_id": session_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to send input")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/sessions/{session_id}/output")
async def get_output(
    session_id: str,
    timeout: float = Query(0.1, ge=0.1, le=5.0)
):
    """Get output from a terminal session."""
    try:
        output = await session_manager.read_from_session(session_id, timeout=timeout)
        return {"output": output, "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/sessions/{session_id}/resize")
async def resize_terminal(
    session_id: str,
    resize_data: SessionResizeRequest = Body(...)
):
    """Resize a terminal session."""
    try:
        success = await session_manager.resize_session(
            session_id, resize_data.cols, resize_data.rows
        )
        if success:
            return {"status": "resized", "session_id": session_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to resize session")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/sessions/{session_id}/llm-assist")
async def get_llm_assistance(
    session_id: str,
    request: LLMAssistRequest = Body(...)
):
    """Get LLM assistance for a terminal query."""
    try:
        assistance = await session_manager.get_llm_assistance(
            session_id=session_id,
            query=request.query,
            context=request.context,
            model=request.model
        )
        return {"response": assistance, "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

2. **WebSocket Server** (`websocket.py`): Manages real-time bidirectional communication for terminal I/O.

```python
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for terminal sessions."""
    try:
        # Initialize session if needed
        try:
            session = await session_manager.get_session(session_id)
        except TerminalError:
            await websocket.accept()
            await websocket.send_json({
                "type": "error",
                "data": f"Session not found: {session_id}",
                "code": "session_not_found"
            })
            await websocket.close()
            return
        
        # Accept connection
        await websocket.accept()
        
        # Register websocket with session
        await session_manager.register_websocket(session_id, websocket)
        
        # Welcome message
        await websocket.send_json({
            "type": "connected",
            "data": {
                "session_id": session_id,
                "message": "Connected to terminal session"
            }
        })
        
        # Initial terminal output
        initial_output = await session_manager.read_from_session(session_id)
        if initial_output:
            await websocket.send_json({
                "type": "output",
                "data": initial_output
            })
        
        # Start output reader task
        output_task = asyncio.create_task(
            output_reader(websocket, session_id, session_manager)
        )
        
        # Process incoming messages
        try:
            while True:
                message = await websocket.receive_json()
                await process_websocket_message(
                    websocket, session_id, message, session_manager
                )
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: {session_id}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            try:
                await websocket.send_json({
                    "type": "error",
                    "data": str(e),
                    "code": "websocket_error"
                })
            except Exception:
                pass
        finally:
            # Cancel output reader task
            output_task.cancel()
            try:
                await output_task
            except asyncio.CancelledError:
                pass
            
            # Unregister websocket
            await session_manager.unregister_websocket(session_id, websocket)
            
            # Close websocket if still open
            if not websocket.client_state == WebSocketState.DISCONNECTED:
                await websocket.close()
    except Exception as e:
        logger.error(f"WebSocket endpoint error: {e}")

async def output_reader(
    websocket: WebSocket,
    session_id: str,
    session_manager: SessionManager
):
    """Read and forward terminal output to the WebSocket."""
    try:
        while True:
            try:
                output = await session_manager.read_from_session(session_id, timeout=0.1)
                if output:
                    await websocket.send_json({
                        "type": "output",
                        "data": output
                    })
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"Error reading output: {e}")
                await websocket.send_json({
                    "type": "error",
                    "data": str(e),
                    "code": "output_error"
                })
                # Short sleep to avoid tight loop on repeated errors
                await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Output reader error: {e}")

async def process_websocket_message(
    websocket: WebSocket,
    session_id: str,
    message: Dict[str, Any],
    session_manager: SessionManager
):
    """Process incoming WebSocket messages."""
    message_type = message.get("type", "")
    
    if message_type == "input":
        # Send input to terminal
        data = message.get("data", "")
        if data:
            success = await session_manager.write_to_session(session_id, data)
            if not success:
                await websocket.send_json({
                    "type": "error",
                    "data": "Failed to send input",
                    "code": "input_error"
                })
    
    elif message_type == "resize":
        # Resize terminal
        cols = message.get("cols", 80)
        rows = message.get("rows", 24)
        success = await session_manager.resize_session(session_id, cols, rows)
        if not success:
            await websocket.send_json({
                "type": "error",
                "data": "Failed to resize terminal",
                "code": "resize_error"
            })
    
    elif message_type == "llm_assist":
        # Get LLM assistance
        query = message.get("data", "")
        context = message.get("context")
        options = message.get("options", {})
        model = options.get("model")
        stream = options.get("stream", False)
        
        if not query:
            await websocket.send_json({
                "type": "error",
                "data": "Empty query",
                "code": "invalid_query"
            })
            return
        
        try:
            if stream:
                # Start streaming response
                await websocket.send_json({
                    "type": "llm_response_start",
                    "data": ""
                })
                
                # Stream response chunks
                async for chunk in session_manager.get_llm_assistance(
                    session_id=session_id,
                    query=query,
                    context=context,
                    model=model,
                    stream=True
                ):
                    await websocket.send_json({
                        "type": "llm_response_chunk",
                        "data": chunk
                    })
                
                # End streaming response
                await websocket.send_json({
                    "type": "llm_response_end",
                    "data": ""
                })
            else:
                # Get complete response
                assistance = await session_manager.get_llm_assistance(
                    session_id=session_id,
                    query=query,
                    context=context,
                    model=model
                )
                
                # Send response
                await websocket.send_json({
                    "type": "llm_response",
                    "data": assistance
                })
        except Exception as e:
            logger.error(f"LLM assistance error: {e}")
            await websocket.send_json({
                "type": "error",
                "data": f"LLM assistance error: {e}",
                "code": "llm_error"
            })
    
    elif message_type == "ping":
        # Respond to ping with pong
        await websocket.send_json({
            "type": "pong",
            "data": message.get("data", "")
        })
    
    else:
        # Unknown message type
        await websocket.send_json({
            "type": "error",
            "data": f"Unknown message type: {message_type}",
            "code": "unknown_message_type"
        })
```

3. **UI Server** (`ui_server.py`): Serves the terminal UI components and handles static assets.

```python
# HTML template for the terminal UI
TERMINAL_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terma Terminal</title>
    <link rel="stylesheet" href="/terminal/static/css/terma-terminal.css">
    <style>
        body, html {
            height: 100%;
            margin: 0;
            padding: 0;
            background-color: #f0f0f0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        .container {
            display: flex;
            flex-direction: column;
            height: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 16px;
            box-sizing: border-box;
        }
        .header {
            margin-bottom: 16px;
        }
        .terminal-container {
            flex: 1;
            border-radius: 4px;
            overflow: hidden;
            background-color: #1e1e1e;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Terma Terminal</h1>
        </div>
        <div class="terminal-container">
            <terma-terminal
                id="terminal"
                theme="{theme}"
                font-size="{font_size}"
                shell-command="{shell_command}"
                auto-connect="true"
                show-assist-button="true">
            </terma-terminal>
        </div>
    </div>
    <script src="/terminal/static/js/terma-terminal.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const terminal = document.getElementById('terminal');
            terminal.addEventListener('terminalReady', function(event) {
                console.log('Terminal ready:', event.detail);
            });
        });
    </script>
</body>
</html>
"""

# Static files directory
static_files = StaticFiles(directory="terma/ui")
app.mount("/terminal/static", static_files, name="static")

@app.get("/terminal/launch")
async def terminal_ui(
    request: Request,
    theme: str = Query("dark", regex="^(dark|light)$"),
    font_size: int = Query(14, ge=8, le=32),
    shell_command: str = Query(None)
):
    """Serve the terminal UI."""
    return HTMLResponse(TERMINAL_HTML_TEMPLATE.format(
        theme=theme,
        font_size=font_size,
        shell_command=shell_command or os.environ.get('SHELL', '/bin/bash')
    ))

@app.get("/terminal/component")
async def terminal_component():
    """Serve the terminal component HTML."""
    with open("terma/ui/terma-component.html", "r") as f:
        html = f.read()
    return HTMLResponse(html)
```

### UI Layer

The UI layer provides the visual interface for users to interact with terminal sessions.

#### Key Components:

1. **Terma Component** (`terma-component.html`, `terma-component.js`): A web component for embedding in the Hephaestus UI.

```javascript
class TermaTerminal extends HTMLElement {
    constructor() {
        super();
        
        // Initialize Shadow DOM
        this.attachShadow({ mode: 'open' });
        
        // Load styles
        const style = document.createElement('style');
        style.textContent = terminalStyles;
        this.shadowRoot.appendChild(style);
        
        // Create container
        this.container = document.createElement('div');
        this.container.className = 'terma-terminal-container';
        this.shadowRoot.appendChild(this.container);
        
        // Terminal properties
        this.sessionId = null;
        this.terminal = null;
        this.socket = null;
        this.connected = false;
        this.connecting = false;
        this.autoReconnect = true;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 1000;
        this.inputBuffer = '';
        
        // Terminal settings
        this.theme = this.getAttribute('theme') || 'dark';
        this.fontSize = parseInt(this.getAttribute('font-size') || '14', 10);
        this.fontFamily = this.getAttribute('font-family') || 'monospace';
        this.shellCommand = this.getAttribute('shell-command') || null;
        this.cwd = this.getAttribute('cwd') || null;
        this.cols = parseInt(this.getAttribute('cols') || '80', 10);
        this.rows = parseInt(this.getAttribute('rows') || '24', 10);
        this.autoConnect = this.hasAttribute('auto-connect');
        this.showAssistButton = this.hasAttribute('show-assist-button');
        
        // LLM settings
        this.llmModel = this.getAttribute('llm-model') || null;
        
        // Terminal events
        this.onTerminalReady = new CustomEvent('terminalReady', {
            bubbles: true,
            composed: true,
            detail: { sessionId: null }
        });
        
        this.onTerminalConnected = new CustomEvent('terminalConnected', {
            bubbles: true,
            composed: true,
            detail: { sessionId: null }
        });
        
        this.onTerminalDisconnected = new CustomEvent('terminalDisconnected', {
            bubbles: true,
            composed: true,
            detail: { sessionId: null }
        });
        
        this.onTerminalError = new CustomEvent('terminalError', {
            bubbles: true,
            composed: true,
            detail: { error: null }
        });
        
        this.onLlmResponse = new CustomEvent('llmResponse', {
            bubbles: true,
            composed: true,
            detail: { response: null }
        });
    }
    
    connectedCallback() {
        // Create terminal UI
        this.createTerminalUI();
        
        // Auto connect if enabled
        if (this.autoConnect) {
            this.createSession();
        }
        
        // Dispatch ready event
        this.dispatchEvent(this.onTerminalReady);
    }
    
    disconnectedCallback() {
        // Clean up
        this.disconnect();
        this.terminal?.dispose();
    }
    
    createTerminalUI() {
        // Create toolbar
        const toolbar = document.createElement('div');
        toolbar.className = `terma-terminal-toolbar ${this.theme}`;
        this.container.appendChild(toolbar);
        
        // Create title
        const title = document.createElement('div');
        title.className = 'terma-terminal-title';
        title.textContent = 'Terminal';
        toolbar.appendChild(title);
        
        // Create toolbar buttons
        const buttonsContainer = document.createElement('div');
        buttonsContainer.className = 'terma-terminal-buttons';
        toolbar.appendChild(buttonsContainer);
        
        // Create new session button
        const newSessionButton = document.createElement('button');
        newSessionButton.className = 'terma-terminal-button';
        newSessionButton.title = 'New Session';
        newSessionButton.innerHTML = '<svg>...</svg>'; // SVG icon
        newSessionButton.addEventListener('click', () => this.createSession());
        buttonsContainer.appendChild(newSessionButton);
        
        // Create LLM assist button if enabled
        if (this.showAssistButton) {
            const assistButton = document.createElement('button');
            assistButton.className = 'terma-terminal-button';
            assistButton.title = 'CI Assist';
            assistButton.innerHTML = '<svg>...</svg>'; // SVG icon
            assistButton.addEventListener('click', () => this.showLlmAssistPrompt());
            buttonsContainer.appendChild(assistButton);
        }
        
        // Create terminal container
        const terminalContainer = document.createElement('div');
        terminalContainer.className = `terma-terminal-xterm ${this.theme}`;
        this.container.appendChild(terminalContainer);
        
        // Create terminal using xterm.js
        this.terminal = new Terminal({
            fontFamily: this.fontFamily,
            fontSize: this.fontSize,
            theme: this.getXtermTheme(),
            cursorBlink: true,
            scrollback: 5000,
            cols: this.cols,
            rows: this.rows
        });
        
        // Create fit addon
        const fitAddon = new FitAddon.FitAddon();
        this.terminal.loadAddon(fitAddon);
        
        // Create search addon
        const searchAddon = new SearchAddon.SearchAddon();
        this.terminal.loadAddon(searchAddon);
        
        // Create web links addon
        const webLinksAddon = new WebLinksAddon.WebLinksAddon();
        this.terminal.loadAddon(webLinksAddon);
        
        // Open terminal
        this.terminal.open(terminalContainer);
        fitAddon.fit();
        
        // Handle terminal input
        this.terminal.onData(data => {
            if (this.connected) {
                this.sendInput(data);
            } else {
                this.inputBuffer += data;
            }
        });
        
        // Handle terminal resize
        window.addEventListener('resize', () => {
            fitAddon.fit();
            this.handleResize();
        });
        
        // Initial fit
        setTimeout(() => fitAddon.fit(), 100);
        
        // Create LLM response area if assist is enabled
        if (this.showAssistButton) {
            const llmContainer = document.createElement('div');
            llmContainer.className = `terma-terminal-llm-container ${this.theme}`;
            llmContainer.style.display = 'none';
            this.container.appendChild(llmContainer);
            
            const llmHeader = document.createElement('div');
            llmHeader.className = 'terma-terminal-llm-header';
            llmContainer.appendChild(llmHeader);
            
            const llmTitle = document.createElement('div');
            llmTitle.className = 'terma-terminal-llm-title';
            llmTitle.textContent = 'CI Assistant';
            llmHeader.appendChild(llmTitle);
            
            const llmClose = document.createElement('button');
            llmClose.className = 'terma-terminal-llm-close';
            llmClose.innerHTML = '×';
            llmClose.addEventListener('click', () => {
                llmContainer.style.display = 'none';
            });
            llmHeader.appendChild(llmClose);
            
            const llmContent = document.createElement('div');
            llmContent.className = 'terma-terminal-llm-content';
            llmContainer.appendChild(llmContent);
            
            this.llmContainer = llmContainer;
            this.llmContent = llmContent;
        }
    }
    
    getXtermTheme() {
        return this.theme === 'dark' ? {
            background: '#1e1e1e',
            foreground: '#f0f0f0',
            cursor: '#f0f0f0',
            cursorAccent: '#1e1e1e',
            selection: 'rgba(255, 255, 255, 0.3)',
            black: '#000000',
            red: '#cd3131',
            green: '#0dbc79',
            yellow: '#e5e510',
            blue: '#2472c8',
            magenta: '#bc3fbc',
            cyan: '#11a8cd',
            white: '#e5e5e5',
            brightBlack: '#666666',
            brightRed: '#f14c4c',
            brightGreen: '#23d18b',
            brightYellow: '#f5f543',
            brightBlue: '#3b8eea',
            brightMagenta: '#d670d6',
            brightCyan: '#29b8db',
            brightWhite: '#e5e5e5'
        } : {
            background: '#ffffff',
            foreground: '#333333',
            cursor: '#333333',
            cursorAccent: '#ffffff',
            selection: 'rgba(0, 0, 0, 0.3)',
            black: '#000000',
            red: '#cd3131',
            green: '#00bc00',
            yellow: '#949800',
            blue: '#0451a5',
            magenta: '#bc05bc',
            cyan: '#0598bc',
            white: '#555555',
            brightBlack: '#666666',
            brightRed: '#cd3131',
            brightGreen: '#14ce14',
            brightYellow: '#b5ba00',
            brightBlue: '#0451a5',
            brightMagenta: '#bc05bc',
            brightCyan: '#0598bc',
            brightWhite: '#a5a5a5'
        };
    }
    
    async createSession() {
        try {
            // Disconnect existing session
            this.disconnect();
            
            // Clear terminal
            this.terminal.clear();
            
            // Show connecting message
            this.terminal.write('Connecting...\r\n');
            
            // Create session
            const response = await fetch('/api/sessions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    shell_command: this.shellCommand,
                    cwd: this.cwd,
                    cols: this.terminal.cols,
                    rows: this.terminal.rows
                })
            });
            
            if (!response.ok) {
                throw new Error(`Failed to create session: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.sessionId = data.session_id;
            
            // Connect to session
            this.connect();
            
            // Update event detail
            this.onTerminalReady.detail.sessionId = this.sessionId;
            
            // Dispatch ready event again with sessionId
            this.dispatchEvent(this.onTerminalReady);
        } catch (error) {
            console.error('Error creating session:', error);
            this.terminal.write(`\r\nError: ${error.message}\r\n`);
            
            // Dispatch error event
            this.onTerminalError.detail.error = error;
            this.dispatchEvent(this.onTerminalError);
        }
    }
    
    connect() {
        if (this.connecting || this.connected || !this.sessionId) {
            return;
        }
        
        this.connecting = true;
        
        // Determine WebSocket URL
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        const path = `/ws/${this.sessionId}`;
        const url = `${protocol}//${host}${path}`;
        
        // Create WebSocket
        this.socket = new WebSocket(url);
        
        // Handle WebSocket open
        this.socket.onopen = () => {
            this.connected = true;
            this.connecting = false;
            this.reconnectAttempts = 0;
            
            // Send any buffered input
            if (this.inputBuffer) {
                this.sendInput(this.inputBuffer);
                this.inputBuffer = '';
            }
            
            // Update terminal title
            if (this.sessionId) {
                const titleEl = this.shadowRoot.querySelector('.terma-terminal-title');
                if (titleEl) {
                    titleEl.textContent = `Terminal (${this.sessionId})`;
                }
            }
            
            // Dispatch connected event
            this.onTerminalConnected.detail.sessionId = this.sessionId;
            this.dispatchEvent(this.onTerminalConnected);
        };
        
        // Handle WebSocket close
        this.socket.onclose = (event) => {
            this.connected = false;
            this.connecting = false;
            
            console.log(`WebSocket closed: Code=${event.code}, Reason=${event.reason}`);
            
            // Try to reconnect if auto-reconnect is enabled
            if (this.autoReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectAttempts++;
                
                this.terminal.write(`\r\nConnection lost. Reconnecting (${this.reconnectAttempts}/${this.maxReconnectAttempts})...\r\n`);
                
                setTimeout(() => {
                    if (!this.connected && !this.connecting) {
                        this.connect();
                    }
                }, this.reconnectDelay * this.reconnectAttempts);
            } else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
                this.terminal.write('\r\nFailed to reconnect after multiple attempts. Please refresh or create a new session.\r\n');
            }
            
            // Dispatch disconnected event
            this.onTerminalDisconnected.detail.sessionId = this.sessionId;
            this.dispatchEvent(this.onTerminalDisconnected);
        };
        
        // Handle WebSocket error
        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            
            // Dispatch error event
            this.onTerminalError.detail.error = error;
            this.dispatchEvent(this.onTerminalError);
        };
        
        // Handle WebSocket messages
        this.socket.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this.handleMessage(message);
            } catch (error) {
                console.error('Error parsing message:', error);
            }
        };
    }
    
    disconnect() {
        // Close WebSocket
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
        
        // Reset state
        this.connected = false;
        this.connecting = false;
        this.inputBuffer = '';
    }
    
    sendInput(data) {
        if (!this.connected || !this.socket) {
            this.inputBuffer += data;
            return;
        }
        
        this.socket.send(JSON.stringify({
            type: 'input',
            data: data
        }));
    }
    
    handleResize() {
        if (!this.connected || !this.socket || !this.sessionId) {
            return;
        }
        
        const cols = this.terminal.cols;
        const rows = this.terminal.rows;
        
        // Send resize message
        this.socket.send(JSON.stringify({
            type: 'resize',
            cols: cols,
            rows: rows
        }));
    }
    
    handleMessage(message) {
        const type = message.type;
        const data = message.data;
        
        switch (type) {
            case 'output':
                this.terminal.write(data);
                break;
            
            case 'connected':
                console.log('Terminal connected:', data);
                break;
            
            case 'error':
                console.error('Terminal error:', data);
                this.terminal.write(`\r\n\x1b[31mError: ${data}\x1b[0m\r\n`);
                break;
            
            case 'llm_response':
                this.showLlmResponse(data);
                break;
            
            case 'llm_response_start':
                this.startLlmStreamingResponse();
                break;
            
            case 'llm_response_chunk':
                this.appendLlmResponseChunk(data);
                break;
            
            case 'llm_response_end':
                this.finishLlmStreamingResponse();
                break;
            
            case 'pong':
                // Handle pong response (keep-alive)
                break;
            
            default:
                console.warn('Unknown message type:', type, data);
        }
    }
    
    showLlmAssistPrompt() {
        if (!this.connected || !this.sessionId) {
            this.terminal.write('\r\n\x1b[31mError: Not connected to a terminal session\x1b[0m\r\n');
            return;
        }
        
        const dialog = document.createElement('div');
        dialog.className = `terma-terminal-dialog ${this.theme}`;
        
        const dialogContent = document.createElement('div');
        dialogContent.className = 'terma-terminal-dialog-content';
        dialog.appendChild(dialogContent);
        
        const dialogTitle = document.createElement('h3');
        dialogTitle.textContent = 'Terminal Assistant';
        dialogContent.appendChild(dialogTitle);
        
        const dialogForm = document.createElement('form');
        dialogContent.appendChild(dialogForm);
        
        const inputContainer = document.createElement('div');
        inputContainer.className = 'terma-terminal-dialog-input';
        dialogForm.appendChild(inputContainer);
        
        const input = document.createElement('input');
        input.type = 'text';
        input.placeholder = 'Ask about commands, explain output, etc.';
        input.required = true;
        inputContainer.appendChild(input);
        
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'terma-terminal-dialog-buttons';
        dialogForm.appendChild(buttonContainer);
        
        const cancelButton = document.createElement('button');
        cancelButton.type = 'button';
        cancelButton.textContent = 'Cancel';
        cancelButton.addEventListener('click', () => {
            this.container.removeChild(dialog);
        });
        buttonContainer.appendChild(cancelButton);
        
        const submitButton = document.createElement('button');
        submitButton.type = 'submit';
        submitButton.textContent = 'Ask';
        buttonContainer.appendChild(submitButton);
        
        dialogForm.addEventListener('submit', (event) => {
            event.preventDefault();
            const query = input.value.trim();
            if (query) {
                this.getLlmAssistance(query);
                this.container.removeChild(dialog);
            }
        });
        
        this.container.appendChild(dialog);
        input.focus();
    }
    
    getLlmAssistance(query) {
        if (!this.connected || !this.socket || !this.sessionId) {
            return;
        }
        
        // Show the LLM container
        if (this.llmContainer) {
            this.llmContainer.style.display = 'flex';
            this.llmContent.innerHTML = '<div class="terma-terminal-llm-loading">Loading...</div>';
        }
        
        // Send LLM assistance request
        this.socket.send(JSON.stringify({
            type: 'llm_assist',
            data: query,
            options: {
                model: this.llmModel,
                stream: true
            }
        }));
    }
    
    startLlmStreamingResponse() {
        if (this.llmContainer) {
            this.llmContent.innerHTML = '';
            this.streamBuffer = '';
            this.markdownRenderer = new marked.Renderer();
            
            // Configure renderer for terminal context
            this.markdownRenderer.code = (code, language) => {
                const highlighted = hljs.highlightAuto(code, language ? [language] : undefined).value;
                return `<pre class="terma-terminal-code"><code class="language-${language || ''}">${highlighted}</code></pre>`;
            };
        }
    }
    
    appendLlmResponseChunk(chunk) {
        if (this.llmContainer) {
            this.streamBuffer += chunk;
            this.llmContent.innerHTML = marked.parse(this.streamBuffer, { renderer: this.markdownRenderer });
            this.llmContent.scrollTop = this.llmContent.scrollHeight;
        }
    }
    
    finishLlmStreamingResponse() {
        if (this.llmContainer) {
            // Final render of markdown
            this.llmContent.innerHTML = marked.parse(this.streamBuffer, { renderer: this.markdownRenderer });
            
            // Dispatch LLM response event
            this.onLlmResponse.detail.response = this.streamBuffer;
            this.dispatchEvent(this.onLlmResponse);
            
            // Clean up
            this.streamBuffer = null;
            this.markdownRenderer = null;
        }
    }
    
    showLlmResponse(response) {
        if (this.llmContainer) {
            // Show the LLM container
            this.llmContainer.style.display = 'flex';
            
            // Render markdown
            this.llmContent.innerHTML = marked.parse(response);
            
            // Dispatch LLM response event
            this.onLlmResponse.detail.response = response;
            this.dispatchEvent(this.onLlmResponse);
        }
    }
    
    // Public API methods
    
    setTheme(theme) {
        if (theme === 'dark' || theme === 'light') {
            this.theme = theme;
            
            // Update theme classes
            this.shadowRoot.querySelector('.terma-terminal-toolbar').className = `terma-terminal-toolbar ${theme}`;
            this.shadowRoot.querySelector('.terma-terminal-xterm').className = `terma-terminal-xterm ${theme}`;
            
            if (this.llmContainer) {
                this.llmContainer.className = `terma-terminal-llm-container ${theme}`;
            }
            
            // Update terminal theme
            this.terminal.setOption('theme', this.getXtermTheme());
        }
    }
    
    setFontSize(size) {
        const fontSize = parseInt(size, 10);
        if (fontSize >= 8 && fontSize <= 32) {
            this.fontSize = fontSize;
            this.terminal.setOption('fontSize', fontSize);
            
            // Trigger fit addon
            const fitAddon = this.terminal._addonManager._addons.find(a => a.instance && typeof a.instance.fit === 'function');
            if (fitAddon && fitAddon.instance) {
                fitAddon.instance.fit();
            }
        }
    }
    
    clear() {
        this.terminal.clear();
    }
    
    focus() {
        this.terminal.focus();
    }
    
    write(data) {
        this.terminal.write(data);
    }
}

// Define the custom element
customElements.define('terma-terminal', TermaTerminal);
```

### Integration Layer

The integration layer connects Terma with other Tekton components, particularly the Hermes messaging system.

#### Key Components:

1. **Hermes Integration** (`hermes_integration.py`): Registers Terma with Hermes service discovery, handles messages from other components, and publishes events.

```python
class HermesIntegration:
    """Integration with Hermes service discovery and messaging."""
    
    def __init__(self, base_url=None):
        """Initialize the Hermes integration."""
        self.base_url = base_url or os.environ.get("HERMES_URL", "http://localhost:8000/api")
        self.client = None
        self.registered = False
        self.component_id = "terma"
        self.service_id = "terma.terminal"
    
    async def initialize(self) -> bool:
        """Initialize the integration."""
        try:
            # Import Hermes client
            from hermes.api.client import HermesClient
            
            # Create client
            self.client = HermesClient(base_url=self.base_url)
            await self.client.initialize()
            
            # Register with Hermes
            return await self.register_service()
        except ImportError:
            logger.warning("Hermes client not available, skipping integration")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Hermes integration: {e}")
            return False
    
    async def register_service(self) -> bool:
        """Register the terminal service with Hermes."""
        if not self.client:
            return False
        
        try:
            port = int(os.environ.get("TERMA_PORT", "8767"))
            host = os.environ.get("TERMA_HOST", "localhost")
            
            service_data = {
                "component_id": self.component_id,
                "service_id": self.service_id,
                "name": "Terma Terminal Service",
                "version": "1.0.0",
                "description": "Terminal service for the Tekton ecosystem",
                "capabilities": ["terminal", "terminal_assistance", "shell_execution"],
                "endpoints": {
                    "http": f"http://{host}:{port}/api",
                    "ws": f"ws://{host}:{port}/ws",
                    "ui": f"http://{host}:{port}/terminal/launch"
                },
                "metadata": {
                    "supports_llm_assistance": True,
                    "ui_component": "terma-terminal"
                }
            }
            
            result = await self.client.register_service(service_data)
            
            if result.get("success", False):
                self.registered = True
                logger.info(f"Registered with Hermes: {self.service_id}")
                return True
            else:
                logger.error(f"Failed to register with Hermes: {result.get('message', 'Unknown error')}")
                return False
        except Exception as e:
            logger.error(f"Error registering with Hermes: {e}")
            return False
    
    async def publish_event(self, event_type, payload) -> bool:
        """Publish an event to Hermes."""
        if not self.client or not self.registered:
            return False
        
        try:
            event = {
                "event_type": f"terma.{event_type}",
                "source": self.service_id,
                "timestamp": datetime.now().isoformat(),
                "payload": payload
            }
            
            result = await self.client.publish_event(event)
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            return False
    
    async def subscribe_to_events(self, event_types) -> bool:
        """Subscribe to events from Hermes."""
        if not self.client or not self.registered:
            return False
        
        try:
            result = await self.client.subscribe_to_events(
                service_id=self.service_id,
                event_types=event_types
            )
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error subscribing to events: {e}")
            return False
    
    async def dispose(self):
        """Clean up resources."""
        if self.client:
            try:
                if self.registered:
                    await self.client.unregister_service(self.service_id)
                await self.client.close()
            except Exception as e:
                logger.error(f"Error disposing Hermes integration: {e}")
```

## Communication Flows

### Terminal Session Communication

```
User Input ──► UI Component ──► WebSocket ──► WebSocket Server ──► Session Manager ──► Terminal Session ──► PTY Process
                                                                                                              │
Terminal Output ◄── UI Component ◄── WebSocket ◄── WebSocket Server ◄── Session Manager ◄── Terminal Session ◄┘
```

### LLM Assistance Flow

```
User Query ──► UI Component ──► WebSocket ──► WebSocket Server ──► Session Manager ──► LLM Adapter ──► LLM Provider
                                                                                                          │
LLM Response ◄── UI Component ◄── WebSocket ◄── WebSocket Server ◄── Session Manager ◄── LLM Adapter ◄───┘
```

## Technical Implementation Details

### PTY Process Management

Terma uses the `ptyprocess` library to create and manage pseudo-terminal processes. This allows for:

- Running interactive applications that require a TTY
- Handling terminal control sequences
- Supporting terminal resizing
- Managing process lifecycles

### WebSocket Communication

Terma implements a WebSocket protocol for bidirectional communication between the UI and terminal sessions:

- **Message Types**:
  - `input`: Terminal input from the user
  - `output`: Terminal output to the UI
  - `resize`: Terminal resize events
  - `error`: Error messages
  - `llm_assist`: LLM assistance requests
  - `llm_response`: LLM responses

### LLM Integration

The LLM Adapter supports different LLM providers and models:

- **HTTP API**: For synchronous requests
- **WebSocket API**: For streaming responses
- **Provider Management**: Selection between different LLM providers (Claude, OpenAI, etc.)
- **Context Management**: Maintaining conversation context for better assistance
- **Fallback Handling**: Graceful degradation when LLM services are unavailable

### Session Management

The Session Manager provides:

- Session creation with different shell commands
- Session cleanup for idle sessions
- Session reconnection
- Resource management
- Session information tracking

## Configuration

Terma can be configured through environment variables and configuration files:

- **Port Configuration**: 
  - `TERMA_PORT`: Default HTTP port 8767
  - `TERMA_HOST`: Default host 0.0.0.0

- **LLM Configuration**:
  - `TERMA_LLM_PROVIDER`: Provider name (rhetor, claude, openai)
  - `TERMA_LLM_MODEL`: Model name

- **Session Configuration**:
  - `TERMA_SESSION_TIMEOUT`: Idle timeout in seconds (default: 3600)
  - `TERMA_CLEANUP_INTERVAL`: Cleanup interval in seconds (default: 300)
  - `TERMA_MAX_SESSIONS`: Maximum number of sessions (default: 100)
  - `TERMA_DEFAULT_SHELL`: Default shell command

- **UI Configuration**:
  - `TERMA_UI_THEME`: Default theme (dark, light)
  - `TERMA_UI_FONT_SIZE`: Default font size

## Single Port Architecture Integration

Terma follows the Tekton Single Port Architecture pattern:

- **HTTP Endpoints**: Available at `/api/*` 
- **WebSocket Endpoint**: Available at `/ws/{session_id}`
- **UI Endpoints**: Available at `/terminal/launch` and `/terminal/component`
- **Standard Environment Variables**: Used for port configuration
- **Path-based Routing**: Different endpoints for different types of requests
- **Graceful Degradation**: When LLM services are unavailable

## Security Considerations

Terma handles security through several mechanisms:

- **Process Isolation**: Each terminal session runs in its own process
- **Resource Limits**: Configurable limits on number of sessions and timeout
- **Input Validation**: All user input is validated
- **Error Handling**: Robust error handling to prevent crashes
- **Future Authentication**: Design supports future authentication integration

## Performance Optimizations

- **Asynchronous Processing**: All operations are asynchronous for maximum performance
- **Resource Management**: Sessions are automatically cleaned up when idle
- **Buffering**: Terminal output is buffered for efficient delivery
- **Connection Management**: WebSocket connections are maintained and reconnected as needed

## Future Improvements

Planned improvements include:

1. **Session Recording**: Record and playback terminal sessions
2. **Multi-user Support**: Support for multiple users with distinct sessions
3. **Enhanced Permissions**: Fine-grained permission control for command execution
4. **Advanced Terminal Features**: Support for more advanced terminal features like split panes
5. **Integration with IDE Tools**: Editor integration via Codex
6. **Terminal Sharing**: Support for shared terminal sessions
7. **Improved Terminal UI**: More customization options and themes
8. **Command Suggestions**: AI-powered command suggestions based on context