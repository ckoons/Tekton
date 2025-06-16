/**
 * Execute utility for Ergon UI to CLI communication
 * Provides process execution and management for CLI command wrapping
 */

import { spawn } from 'child_process';
import { v4 as uuidv4 } from 'uuid';

// Map to track running processes
const processes = new Map();

/**
 * Execute a CLI command from the Ergon module
 * @param {string} command - The command to execute
 * @param {Object} args - Arguments for the command
 * @param {Object} options - Execution options
 * @returns {Promise<any>} - Command result
 */
export const execute = async (command, args = {}, options = {}) => {
  // If streaming is enabled, create a long-running process
  if (options.streaming) {
    return createStreamingProcess(command, args, options);
  }
  
  // Format args for Python script
  const pythonArgs = formatPythonArgs(args);
  
  // Create a Python process that executes the command
  return new Promise((resolve, reject) => {
    const process = spawn('python', ['-c', `
import sys
import json
import traceback

try:
    # Import CLI command
    from ergon.cli.commands.agent_commands import ${command}
    from ergon.cli.utils.json_formatter import format_output
    
    # Execute command and capture output
    result = ${command}(${pythonArgs})
    
    # Format and print result as JSON
    print(json.dumps(format_output(result)))
    
except Exception as e:
    error_data = {
        "error": str(e),
        "traceback": traceback.format_exc()
    }
    print(json.dumps(error_data))
    sys.exit(1)
`]);
    
    let stdout = '';
    let stderr = '';
    
    process.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    process.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    process.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(stdout);
          resolve(result);
        } catch (error) {
          // If output isn't JSON, return as string
          resolve({ output: stdout.trim() });
        }
      } else {
        try {
          // Try to parse error as JSON
          const errorData = JSON.parse(stdout);
          reject(new Error(errorData.error || 'Command failed'));
        } catch (e) {
          // If parsing fails, return raw error
          reject(new Error(stderr || `Command failed with code ${code}`));
        }
      }
    });
  });
};

/**
 * Create a streaming process for interactive commands
 */
const createStreamingProcess = (command, args, options) => {
  const processId = uuidv4();
  
  // Format args for Python script
  const pythonArgs = formatPythonArgs(args);
  
  // Create a Python process that runs the interactive command
  const process = spawn('python', ['-c', `
import sys
import json
import asyncio
import traceback

try:
    # Set up interactive mode communication
    from ergon.cli.commands.agent_commands import run_agent
    from ergon.core.agents.runner import AgentRunner
    from ergon.core.database.engine import get_db_session
    from ergon.cli.utils.agent_finder import find_agent_by_identifier
    from ergon.core.database.models import AgentExecution, AgentMessage
    
    async def main():
        # Get agent by identifier
        with get_db_session() as db:
            agent = find_agent_by_identifier(db, "${args.agent_identifier}")
            if not agent:
                print(json.dumps({"error": "Agent not found"}))
                sys.exit(1)
            
            # Create execution record
            execution = AgentExecution(agent_id=agent.id)
            db.add(execution)
            db.commit()
            db.refresh(execution)
            
            # Initialize runner
            runner = AgentRunner(
                agent=agent, 
                execution_id=execution.id,
                timeout=${args.timeout || 'None'},
                timeout_action="${args.timeout_action || 'log'}"
            )
            
            # Notify ready
            print(json.dumps({
                "type": "ready", 
                "agent": {
                    "id": agent.id, 
                    "name": agent.name,
                    "model": agent.model_name,
                    "type": "${args.agent_type || 'standard'}"
                }
            }))
            sys.stdout.flush()
            
            # Main loop - read from stdin, process, write to stdout
            while True:
                try:
                    line = sys.stdin.readline().strip()
                    if not line or line == "EXIT":
                        break
                        
                    # Record user message
                    message = AgentMessage(
                        execution_id=execution.id,
                        role="user",
                        content=line
                    )
                    db.add(message)
                    db.commit()
                    
                    # Show thinking
                    print(json.dumps({"type": "thinking"}))
                    sys.stdout.flush()
                    
                    # Process the input
                    response = await runner.run(line)
                    
                    # Record assistant message
                    message = AgentMessage(
                        execution_id=execution.id,
                        role="assistant",
                        content=response
                    )
                    db.add(message)
                    db.commit()
                    
                    # Send response
                    print(json.dumps({
                        "type": "response", 
                        "content": response,
                        "execution_id": execution.id
                    }))
                    sys.stdout.flush()
                    
                except Exception as e:
                    error_msg = str(e)
                    traceback_msg = traceback.format_exc()
                    print(json.dumps({
                        "type": "error", 
                        "error": error_msg,
                        "traceback": traceback_msg
                    }))
                    sys.stdout.flush()
    
    asyncio.run(main())
    
except Exception as e:
    error_data = {
        "type": "fatal",
        "error": str(e),
        "traceback": traceback.format_exc()
    }
    print(json.dumps(error_data))
    sys.exit(1)
`]);

  // Set up message handlers
  const messageHandlers = new Map();
  let buffer = '';
  
  process.stdout.on('data', (data) => {
    buffer += data.toString();
    
    // Process complete JSON messages
    try {
      const messages = processJsonMessages(buffer);
      buffer = messages.remaining;
      
      // Handle each complete message
      for (const message of messages.complete) {
        const handlers = messageHandlers.get('message') || [];
        handlers.forEach(handler => handler(message));
      }
    } catch (error) {
      console.error('Error processing message:', error);
    }
  });
  
  process.stderr.on('data', (data) => {
    const errorMsg = data.toString();
    const handlers = messageHandlers.get('error') || [];
    handlers.forEach(handler => handler(errorMsg));
  });
  
  process.on('close', (code) => {
    const handlers = messageHandlers.get('close') || [];
    handlers.forEach(handler => handler(code));
    
    // Remove from process map
    processes.delete(processId);
  });
  
  // Create process control interface
  const processControl = {
    id: processId,
    send: (message) => {
      process.stdin.write(message + '\n');
    },
    on: (event, handler) => {
      if (!messageHandlers.has(event)) {
        messageHandlers.set(event, []);
      }
      messageHandlers.get(event).push(handler);
    },
    terminate: () => {
      process.stdin.write('EXIT\n');
      setTimeout(() => {
        if (!process.killed) {
          process.kill();
        }
      }, 1000);
    }
  };
  
  // Store in process map
  processes.set(processId, processControl);
  
  return processControl;
};

/**
 * Process a string buffer containing multiple JSON messages
 */
const processJsonMessages = (buffer) => {
  const complete = [];
  let remaining = buffer;
  
  // Find complete JSON objects
  let startIdx = remaining.indexOf('{');
  while (startIdx !== -1) {
    try {
      // Try to parse a JSON object
      const parsed = JSON.parse(remaining.substring(startIdx));
      complete.push(parsed);
      
      // Move past this object
      remaining = remaining.substring(startIdx + JSON.stringify(parsed).length);
      startIdx = remaining.indexOf('{');
    } catch (error) {
      // If parsing fails, try the next opening brace
      const nextIdx = remaining.indexOf('{', startIdx + 1);
      if (nextIdx === -1) break;
      startIdx = nextIdx;
    }
  }
  
  return { complete, remaining };
};

/**
 * Format args as Python keyword arguments
 */
const formatPythonArgs = (args) => {
  return Object.entries(args)
    .map(([key, value]) => {
      if (value === undefined || value === null) {
        return `${key}=None`;
      } else if (typeof value === 'string') {
        return `${key}="${value.replace(/"/g, '\\"')}"`;
      } else if (typeof value === 'boolean') {
        return `${key}=${value ? 'True' : 'False'}`;
      } else {
        return `${key}=${value}`;
      }
    })
    .join(', ');
};

/**
 * Send a message to a running process
 */
export const sendToProcess = (processId, message) => {
  const process = processes.get(processId);
  if (!process) {
    throw new Error(`Process with ID ${processId} not found`);
  }
  
  process.send(message);
  return process;
};

/**
 * Terminate a running process
 */
export const terminateProcess = (processId) => {
  const process = processes.get(processId);
  if (!process) {
    throw new Error(`Process with ID ${processId} not found`);
  }
  
  process.terminate();
  return true;
};

/**
 * Get all running processes
 */
export const getRunningProcesses = () => {
  return Array.from(processes.keys());
};