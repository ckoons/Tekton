import asyncio
import os
import sys
import multiprocessing
import queue
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("codex_adapter")

# Import the chat input adapter
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../tekton-core")))
# Try to import from tekton core, fallback to local implementation
try:
    from tekton.utils.input_adapter import ChatInputAdapter
except ImportError:
    # Fallback implementation if tekton-core is not in path
    class ChatInputAdapter:
        def __init__(self, component_id):
            self.component_id = component_id
            self.input_queue = asyncio.Queue()
            self.input_history = []
            self.input_handlers = []
            self.input_interceptors = []
            self.context = {}
        
        async def receive_input(self, text):
            self.input_history.append(text)
            await self.input_queue.put(text)
            for handler in self.input_handlers:
                await handler(text, self.context)
            return True
        
        async def get_input(self, timeout=None):
            if timeout is not None:
                return await asyncio.wait_for(self.input_queue.get(), timeout)
            return await self.input_queue.get()
        
        def register_handler(self, handler):
            self.input_handlers.append(handler)

class AiderProcess:
    """
    Handles Aider in a separate process with simpler communication
    """
    def __init__(self):
        self.process = None
        self.input_queue = multiprocessing.Queue()
        self.output_queue = multiprocessing.Queue()
        self.files_queue = multiprocessing.Queue()
        self.running = False
    
    def start(self, args=None):
        """Start the Aider process"""
        if self.process and self.process.is_alive():
            return False
        
        # Default arguments
        if args is None:
            args = ["--yes-always", "--stream"]
        
        # Create and start the process
        self.process = multiprocessing.Process(
            target=self._run_aider,
            args=(args, self.input_queue, self.output_queue, self.files_queue)
        )
        self.process.daemon = True
        self.process.start()
        self.running = True
        return True
    
    def stop(self):
        """Stop the Aider process"""
        if self.process and self.process.is_alive():
            # Send exit command
            self.input_queue.put("/exit")
            # Wait for process to end
            self.process.join(timeout=5)
            # If still alive, terminate
            if self.process.is_alive():
                self.process.terminate()
                self.process.join(timeout=1)
        self.running = False
    
    def send_input(self, text):
        """Send input to Aider"""
        if not self.running:
            print(f"=== DEBUG ERROR: AiderProcess not running, can't send input: '{text}' ===")
            return False
        print(f"=== DEBUG: AiderProcess.send_input putting into input_queue: '{text}' ===")
        try:
            self.input_queue.put(text)
            print(f"=== DEBUG: Successfully put input into queue ===")
            return True
        except Exception as e:
            print(f"=== DEBUG ERROR: Failed to put input in queue: {e} ===")
            return False
    
    def get_output(self, block=False, timeout=0.1):
        """Get output from Aider"""
        try:
            return self.output_queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None
    
    def get_files(self, block=False, timeout=0.1):
        """Get current files from Aider"""
        try:
            return self.files_queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None
    
    @staticmethod
    def _run_aider(args, input_queue, output_queue, files_queue):
        """Run Aider in a separate process"""
        try:
            # Import Aider modules
            from aider.io import InputOutput
            from aider.main import main as aider_main
            
            # Configure IO for interprocess communication
            class CustomIO(InputOutput):
                def __init__(self, output_queue, files_queue, **kwargs):
                    super().__init__(**kwargs)
                    self.output_queue = output_queue
                    self.files_queue = files_queue
                
                def tool_output(self, msg="", log_only=False):
                    """Send output to the main process"""
                    if not log_only:
                        self.output_queue.put({"type": "output", "content": msg})
                    # Call original method with only the parameters it expects
                    super().tool_output(msg, log_only=log_only)
                
                def tool_error(self, msg=""):
                    """Send errors to the main process"""
                    self.output_queue.put({"type": "error", "content": msg})
                    super().tool_error(msg)
                
                def tool_warning(self, msg=""):
                    """Send warnings to the main process"""
                    self.output_queue.put({"type": "warning", "content": msg})
                    super().tool_warning(msg)
                
                def get_input(self, *args, **kwargs):
                    """Get input from the main process"""
                    # Signal that we need input
                    print("=== DEBUG: Aider is requesting input ===")
                    self.output_queue.put({"type": "input_request"})
                    
                    # Wait for input
                    print("=== DEBUG: Aider is waiting for input from queue ===")
                    input_text = input_queue.get()
                    print(f"=== DEBUG: Aider received input from queue: '{input_text}' ===")
                    
                    # Send confirmation back to main process
                    print(f"=== DEBUG: Aider is sending input received confirmation for: '{input_text}' ===")
                    self.output_queue.put({"type": "input_received", "content": input_text})
                    
                    # Add to history
                    print("=== DEBUG: Aider is adding input to history ===")
                    self.add_to_input_history(input_text)
                    
                    return input_text
            
            # Store original argv
            orig_argv = sys.argv.copy()
            
            try:
                # Set argv for Aider
                sys.argv = ["aider"] + args
                
                # Initialize custom IO
                io = CustomIO(
                    output_queue=output_queue,
                    files_queue=files_queue,
                    pretty=False,
                    yes=True,
                )
                
                # Start Aider with our custom IO
                coder = aider_main(input=None, output=None, return_coder=True)
                
                # Replace the IO with our custom version
                if coder:
                    coder.io = io
                    coder.commands.io = io
                    
                    # Send initial file list
                    files_queue.put(coder.get_inchat_relative_files())
                    
                    # Run Aider's main loop
                    coder.run()
                
            except Exception as e:
                import traceback
                error_msg = f"Aider process error: {str(e)}\n{traceback.format_exc()}"
                output_queue.put({"type": "error", "content": error_msg})
            
            finally:
                # Restore original argv
                sys.argv = orig_argv
        
        except Exception as e:
            import traceback
            error_msg = f"Aider process critical error: {str(e)}\n{traceback.format_exc()}"
            output_queue.put({"type": "error", "content": error_msg})

class CodexAiderAdapter:
    """
    Adapter for integrating Aider with Tekton as the Codex component.
    Uses multiprocessing for better stability.
    """
    
    def __init__(self):
        """Initialize the adapter."""
        self.websocket_handler = None
        self.aider = AiderProcess()
        self.chat_input_adapter = ChatInputAdapter("codex")
        self.output_task = None
        self.initialized = False
        self.session_id = f"session_{int(time.time())}"
    
    async def initialize(self, websocket_handler):
        """
        Initialize the adapter with a websocket handler.
        
        Args:
            websocket_handler: Handler for WebSocket communication with UI
        """
        self.websocket_handler = websocket_handler
        
        # Register input handler
        self.chat_input_adapter.register_handler(self.handle_input)
        
        # Send initializing message
        await self.websocket_handler.send_output("Initializing Aider session...")
        
        try:
            # Start Aider process
            success = self.aider.start()
            if not success:
                await self.websocket_handler.send_error("Failed to start Aider process")
                return False
            
            # Start monitoring the output queue
            self.output_task = asyncio.create_task(self._monitor_output())
            
            # Mark as initialized
            self.initialized = True
            
            await self.websocket_handler.send_output("Aider session started successfully")
            
            # Send session status update to all clients
            if self.websocket_handler:
                await self.websocket_handler.send_session_status(True, self.session_id)
                
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Aider: {e}")
            await self.websocket_handler.send_error(f"Failed to initialize Aider: {str(e)}")
            # Make sure to clean up any partial initialization
            await self.stop()
            return False
    
    async def _monitor_output(self):
        """Monitor output from Aider process and forward to UI"""
        try:
            while True:
                # Check if process is still running
                if not self.aider.running:
                    await self.websocket_handler.send_error("Aider process has stopped unexpectedly")
                    # Set initialized to false so clients know the session is dead
                    self.initialized = False
                    await self.websocket_handler.send_session_status(False, None)
                    break
                
                try:
                    # Check for output
                    output = self.aider.get_output(timeout=0.1)
                    if output:
                        message_type = output.get("type", "")
                        content = output.get("content", "")
                        
                        if message_type == "output":
                            await self.websocket_handler.send_output(content)
                        elif message_type == "error":
                            await self.websocket_handler.send_error(content)
                        elif message_type == "warning":
                            await self.websocket_handler.send_warning(content)
                        elif message_type == "input_request":
                            await self.websocket_handler.request_input()
                        elif message_type == "input_received":
                            # Provide visual feedback that input was received by Aider
                            logger.info(f"Aider acknowledged input: {content}")
                            await self.websocket_handler.send_input_received(content)
                    
                    # Check for file updates
                    files = self.aider.get_files(timeout=0.1)
                    if files:
                        await self.websocket_handler.send_active_files(files)
                
                except queue.Empty:
                    # This is expected - just continue
                    pass
                except Exception as e:
                    logger.error(f"Error processing output: {e}")
                    # Don't break the loop for non-critical errors
                
                # Short sleep to prevent CPU spinning
                await asyncio.sleep(0.05)
        
        except asyncio.CancelledError:
            logger.info("Output monitoring cancelled")
            return
        except Exception as e:
            logger.error(f"Critical error monitoring output: {e}")
            if self.websocket_handler:
                try:
                    await self.websocket_handler.send_error(f"Error monitoring output: {e}")
                    # Set initialized to false so clients know the session is dead
                    self.initialized = False
                    await self.websocket_handler.send_session_status(False, None)
                except:
                    pass
    
    async def handle_input(self, text: str, context: Dict[str, Any]) -> None:
        """
        Handle input received from the chat input area.
        
        Args:
            text: The input text
            context: Additional context data
        """
        # Send input to Aider
        self.aider.send_input(text)
    
    async def receive_input(self, text: str) -> bool:
        """
        Process input from the UI.
        
        Args:
            text: The input text
            
        Returns:
            bool: Whether the input was successfully processed
        """
        # Log the received input for debugging
        logger.info(f"Received input: {text}")
        print(f"=== DEBUG: CodexAiderAdapter received input: '{text}' ===")
        
        # Provide immediate visual feedback
        if self.websocket_handler:
            try:
                logger.info("Sending visual feedback for input")
                print("=== DEBUG: Sending visual feedback for input ===")
                await self.websocket_handler.send_input_received(text)
            except Exception as e:
                logger.error(f"Error sending visual feedback: {e}")
                print(f"=== DEBUG ERROR: Failed to send visual feedback: {e} ===")
        else:
            print("=== DEBUG ERROR: No websocket_handler available for feedback ===")
        
        # Process through the input adapter
        try:
            logger.info("Processing input through chat_input_adapter")
            print("=== DEBUG: Processing input through chat_input_adapter ===")
            result = await self.chat_input_adapter.receive_input(text)
            print(f"=== DEBUG: chat_input_adapter result: {result} ===")
        except Exception as e:
            logger.error(f"Error in chat_input_adapter: {e}")
            print(f"=== DEBUG ERROR: chat_input_adapter failed: {e} ===")
            result = False
        
        # Directly send to Aider process - this is the primary path
        if self.aider.running:
            try:
                logger.info("Sending input directly to Aider process")
                print(f"=== DEBUG: Sending input directly to Aider process: '{text}' ===")
                self.aider.send_input(text)
                logger.info(f"Input sent to Aider process: {text}")
                print("=== DEBUG: Input successfully sent to Aider process ===")
            except Exception as e:
                logger.error(f"Error sending to Aider process: {e}")
                print(f"=== DEBUG ERROR: Failed to send to Aider process: {e} ===")
                return False
        else:
            logger.error("Aider process not running, cannot send input")
            print("=== DEBUG ERROR: Aider process not running, cannot send input ===")
            if self.websocket_handler:
                await self.websocket_handler.send_error("Aider not running. Try restarting the session.")
            return False
        
        return True
    
    async def stop(self):
        """
        Stop the Aider adapter.
        """
        logger.info("Stopping Aider adapter")
        
        # Cancel the output monitoring task
        if self.output_task:
            self.output_task.cancel()
            try:
                await self.output_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"Error while cancelling output task: {e}")
            self.output_task = None
        
        # Stop the Aider process
        if self.aider:
            self.aider.stop()
        
        # Update initialized state
        self.initialized = False
        
        # Notify UI if handler is available
        if self.websocket_handler:
            try:
                await self.websocket_handler.send_output("Aider session stopped")
                await self.websocket_handler.send_session_status(False, None)
            except Exception as e:
                logger.error(f"Error while sending session stop notification: {e}")
                
        return True
    
    async def restart(self):
        """
        Restart the Aider adapter.
        """
        await self.stop()
        # Wait a moment for resources to be released
        await asyncio.sleep(0.5)
        await self.initialize(self.websocket_handler)