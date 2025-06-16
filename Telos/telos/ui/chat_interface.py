#!/usr/bin/env python3
"""
Simple chat interface for Telos.

This module provides a text-based chat interface for interacting with Telos.
It wraps the CLI commands in a conversational interface.
"""

import os
import sys
import re
import json
import time
import logging
import asyncio
import subprocess
import shlex
from typing import Dict, List, Any, Optional, Callable, Tuple

logger = logging.getLogger(__name__)


class TelosChatInterface:
    """
    Chat-based interface for Telos that wraps CLI commands.
    
    This provides a simple conversational interface while using the existing
    CLI commands underneath.
    """
    
    def __init__(self, telos_script: Optional[str] = None):
        """
        Initialize the chat interface.
        
        Args:
            telos_script: Path to the Telos CLI script (default: find automatically)
        """
        # Find Telos CLI script
        self.telos_script = telos_script or self._find_telos_script()
        self.session_context = {
            "current_project": None,
            "current_requirement": None,
            "command_history": []
        }
        
        # Conversation context (for chat memory)
        self.conversation = []
        
        # Command mappings for natural language processing
        self.command_patterns = [
            # Project commands
            (r"create (?:a )?project (?:called |named )?([\w\-\s]+)", "project create '{}'"),
            (r"list (?:all )?projects", "project list"),
            (r"show project (?:details for )?([\w\-\d]+)", "project show {}"),
            # Requirement commands
            (r"add (?:a )?requirement(?: to project| for)? ([\w\-\d]+)(?::|$)([\w\-\s]*)", 
             self._handle_add_requirement),
            (r"list (?:all )?requirements(?: for| in)? (?:project )?([\w\-\d]+)", 
             "requirement list {}"),
            (r"show requirement ([\w\-\d]+)(?: for| in)? (?:project )?([\w\-\d]+)", 
             "requirement show {} {}"),
            # Refinement commands
            (r"refine requirement ([\w\-\d]+)(?: for| in)? (?:project )?([\w\-\d]+)", 
             "refine requirement {} --requirement-id {}"),
            (r"analyze(?: requirements| project)? ([\w\-\d]+)(?:.*)planning", 
             "refine analyze {}"),
            # Planning commands
            (r"(?:create|generate)(?: a)? plan(?: for| based on)? (?:project )?([\w\-\d]+)", 
             "prometheus plan {}"),
            # Help and context commands
            (r"(?:what is|show) (?:the )?current project", self._show_current_context),
            (r"set (?:the )?current project (?:to )?([\w\-\d]+)", self._set_current_project),
            (r"help", self._show_help)
        ]
    
    def _find_telos_script(self) -> str:
        """Find the Telos CLI script in the environment."""
        # Possible locations to look for the script
        possible_paths = [
            os.path.join(os.getcwd(), "telos", "cli", "main.py"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cli", "main.py"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "bin", "telos"),
            "telos",  # Assume it's in PATH
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Default to 'telos' and hope it's in PATH
        return "telos"
    
    def start(self) -> None:
        """Start the chat interface."""
        self._print_welcome()
        
        while True:
            try:
                # Get user input
                user_input = input("\nYou: ").strip()
                
                # Exit commands
                if user_input.lower() in ["exit", "quit", "bye"]:
                    print("\nTelos: Goodbye! Have a great day.")
                    break
                
                # Process the input
                self._process_input(user_input)
                
            except KeyboardInterrupt:
                print("\nTelos: Session terminated by user.")
                break
            except EOFError:
                print("\nTelos: End of input. Goodbye!")
                break
            except Exception as e:
                print(f"\nTelos: An error occurred: {str(e)}")
                logger.exception("Error in chat interface")
    
    def _process_input(self, user_input: str) -> None:
        """
        Process user input and generate a response.
        
        Args:
            user_input: User's input text
        """
        # Add to conversation history
        self.conversation.append({"role": "user", "content": user_input})
        
        # Try to match with command patterns
        command = self._parse_natural_language(user_input)
        
        if command:
            # Execute the command
            output = self._execute_telos_command(command)
            
            # Format and display the response
            self._format_and_display_response(output, command)
        else:
            # No command matched
            response = self._handle_general_query(user_input)
            print(f"\nTelos: {response}")
            self.conversation.append({"role": "assistant", "content": response})
    
    def _parse_natural_language(self, text: str) -> Optional[str]:
        """
        Parse natural language input into a Telos command.
        
        Args:
            text: Natural language input
            
        Returns:
            Telos CLI command or None if no match
        """
        text = text.lower().strip()
        
        # Special case for empty input
        if not text:
            return None
            
        # Try each pattern
        for pattern, template in self.command_patterns:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                if callable(template):
                    # Call the handler function
                    return template(*match.groups())
                else:
                    # Format the template with the matched groups
                    return template.format(*match.groups())
        
        return None
    
    def _execute_telos_command(self, command: str) -> str:
        """
        Execute a Telos CLI command.
        
        Args:
            command: Telos CLI command
            
        Returns:
            Command output
        """
        # Add to command history
        self.session_context["command_history"].append(command)
        
        # Split the command
        args = shlex.split(command)
        
        try:
            # Execute the command
            full_command = [sys.executable, self.telos_script] if self.telos_script.endswith(".py") else [self.telos_script]
            full_command.extend(args)
            
            # Run the command and capture output
            result = subprocess.run(
                full_command, 
                capture_output=True, 
                text=True, 
                check=False
            )
            
            # Update context based on command
            self._update_context_from_command(command, result.stdout)
            
            if result.returncode != 0 and result.stderr:
                return f"Error: {result.stderr}"
            
            return result.stdout
            
        except Exception as e:
            logger.exception(f"Error executing command: {command}")
            return f"Error executing command: {str(e)}"
    
    def _format_and_display_response(self, output: str, command: str) -> None:
        """
        Format and display the command response.
        
        Args:
            output: Command output
            command: The command that was executed
        """
        # Clean up the output
        output = output.strip()
        
        # Extract the command type
        cmd_parts = command.split()
        cmd_type = cmd_parts[0] if cmd_parts else "unknown"
        
        # Format response based on command type
        if cmd_type == "project" and "create" in command:
            print(f"\nTelos: I've created the project for you.")
        elif cmd_type == "project" and "list" in command:
            print(f"\nTelos: Here are your projects:\n")
            print(output)
        elif cmd_type == "requirement" and "add" in command:
            print(f"\nTelos: I've added the requirement.")
        elif cmd_type == "refine" and "requirement" in command:
            print(f"\nTelos: Let's refine this requirement together.")
            print(f"(Interactive refinement will start in the terminal)")
            print(output)
        elif cmd_type == "prometheus" and "plan" in command:
            print(f"\nTelos: Creating a plan based on your requirements:")
            print(output)
        else:
            print(f"\nTelos: Here's the result:\n")
            print(output)
        
        # Add to conversation history
        self.conversation.append({
            "role": "assistant", 
            "content": f"Command executed: {command}\nOutput: {output}"
        })
    
    def _update_context_from_command(self, command: str, output: str) -> None:
        """
        Update session context based on command execution.
        
        Args:
            command: The executed command
            output: Command output
        """
        # Extract the command parts
        parts = shlex.split(command)
        
        # Update current project context
        if len(parts) >= 3 and parts[0] == "project" and parts[1] == "create":
            # Extract the project ID from output
            match = re.search(r"Created project (\w+)", output)
            if match:
                self.session_context["current_project"] = match.group(1)
        
        elif len(parts) >= 3 and parts[0] == "project" and parts[1] == "show":
            self.session_context["current_project"] = parts[2]
        
        # Update current requirement context
        if len(parts) >= 4 and parts[0] == "requirement" and parts[1] == "add":
            # Extract the requirement ID from output
            match = re.search(r"Added requirement (\w+)", output)
            if match:
                self.session_context["current_requirement"] = match.group(1)
        
        elif len(parts) >= 4 and parts[0] == "requirement" and parts[1] == "show":
            self.session_context["current_requirement"] = parts[3]
    
    def _handle_add_requirement(self, project_id: str, title: str = "") -> str:
        """
        Handle the add requirement command with interactive mode.
        
        Args:
            project_id: Project ID
            title: Optional requirement title
            
        Returns:
            Formatted command
        """
        # Use current project if no project specified
        if not project_id and self.session_context["current_project"]:
            project_id = self.session_context["current_project"]
        
        if not project_id:
            return None
            
        # Clean up the title
        title = title.strip()
        
        if title:
            return f"requirement add {project_id} '{title}' --interactive"
        else:
            # Ask for title
            print("\nTelos: What's the title for this requirement?")
            title = input("You: ").strip()
            return f"requirement add {project_id} '{title}' --interactive"
    
    def _set_current_project(self, project_id: str) -> None:
        """
        Set the current project in the session context.
        
        Args:
            project_id: Project ID
            
        Returns:
            None (response message is printed directly)
        """
        self.session_context["current_project"] = project_id
        print(f"\nTelos: Current project set to {project_id}")
        return None
    
    def _show_current_context(self) -> None:
        """
        Show the current session context.
        
        Returns:
            None (response message is printed directly)
        """
        if self.session_context["current_project"]:
            print(f"\nTelos: Current project: {self.session_context['current_project']}")
            
            if self.session_context["current_requirement"]:
                print(f"Current requirement: {self.session_context['current_requirement']}")
        else:
            print("\nTelos: No current project set. Use 'set current project to ID' to set one.")
            
        return None
    
    def _show_help(self) -> None:
        """
        Show help information.
        
        Returns:
            None (response message is printed directly)
        """
        print("\nTelos: Here are some things you can ask me to do:")
        print("\nProject Management:")
        print("  - Create a project called [name]")
        print("  - List all projects")
        print("  - Show project [ID]")
        print("  - Set current project to [ID]")
        
        print("\nRequirements Management:")
        print("  - Add a requirement to project [ID]")
        print("  - List requirements for project [ID]")
        print("  - Show requirement [REQ_ID] in project [PROJ_ID]")
        print("  - Refine requirement [REQ_ID] in project [PROJ_ID]")
        
        print("\nPlanning:")
        print("  - Analyze project [ID] for planning")
        print("  - Create a plan for project [ID]")
        
        print("\nSession Management:")
        print("  - What is the current project")
        print("  - Exit/Quit")
        
        return None
    
    def _handle_general_query(self, query: str) -> str:
        """
        Handle general queries that don't match command patterns.
        
        Args:
            query: User's query
            
        Returns:
            Response text
        """
        # Check for questions about current context
        if re.search(r"(what|which).*project.*working on", query, re.IGNORECASE):
            if self.session_context["current_project"]:
                return f"You're currently working on project {self.session_context['current_project']}."
            else:
                return "You're not working on any project yet. Try 'list projects' to see available projects."
                
        # Check for questions about how to do things
        if re.search(r"how (?:do|can) I", query, re.IGNORECASE):
            return "I can help you manage requirements and create plans. Try asking for 'help' to see what I can do."
            
        # Default fallback response
        return "I'm not sure how to help with that. Try asking for 'help' to see what I can do."
    
    def _print_welcome(self) -> None:
        """Print welcome message."""
        print("\n" + "=" * 60)
        print("   Welcome to Telos - Requirements Management Assistant")
        print("=" * 60)
        print("\nTelos: Hello! I'm your requirements management assistant.")
        print("I can help you create and refine requirements, and generate plans.")
        print("What would you like to do today? (Type 'help' for assistance)")


def main():
    """Run the Telos chat interface."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Start the chat interface
    chat = TelosChatInterface()
    chat.start()


if __name__ == "__main__":
    main()