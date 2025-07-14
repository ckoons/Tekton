#!/usr/bin/env python3
"""
Purpose command for aish
Manages terminal purposes and displays playbook content.
"""

import os
import sys
import glob
from pathlib import Path
from typing import List, Optional, Dict
import httpx
import logging

# Try to import landmarks if available
try:
    from landmarks import architecture_decision, integration_point, api_contract, state_checkpoint
except ImportError:
    # Landmarks not available, create no-op decorators
    def architecture_decision(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator
    
    def api_contract(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator

from shared.aish.src.core.purpose_matcher import parse_purpose_list

logger = logging.getLogger("aish.purpose")


class PurposeCommand:
    """Manages terminal purposes and playbook content."""
    
    def __init__(self):
        self.tekton_root = os.environ.get('TEKTON_MAIN_ROOT', os.environ.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton'))
        self.playbook_dir = Path(self.tekton_root) / ".tekton" / "playbook"
        self.terma_url = os.environ.get('TERMA_ENDPOINT', 'http://localhost:8004')
        
    # Landmark: Terminal Context Setup - Sets purpose and shows playbook
    def execute(self, terminal_name: str, purpose_string: str) -> None:
        """
        Set purpose for a terminal and display relevant playbook content.
        
        Args:
            terminal_name: Name of the terminal (e.g., "Amy")
            purpose_string: CSV list of purposes (e.g., "Coding, Research")
        """
        # Parse the purpose string
        purposes = parse_purpose_list(purpose_string)
        
        if not purposes:
            print("Error: No valid purposes provided")
            return
            
        print(f"Setting purpose for {terminal_name}: {', '.join(purposes)}")
        print()
        
        # Update terminal purpose via Terma API
        self._update_terminal_purpose(terminal_name, purpose_string)
        
        # Display playbook content for each purpose
        for purpose in purposes:
            self._display_playbook_content(purpose)
            
        # Show full playbook path
        print(f"\nFull playbook: {self.playbook_dir}")
        
        # If running in the target terminal, export TEKTON_PURPOSE
        current_terminal = os.environ.get('TERMA_TERMINAL_NAME', '')
        if current_terminal.lower() == terminal_name.lower():
            os.environ['TEKTON_TERMINAL_PURPOSE'] = purpose_string
            print(f"\nExported TEKTON_TERMINAL_PURPOSE='{purpose_string}'")
    
    def _update_terminal_purpose(self, terminal_name: str, purpose: str) -> None:
        """Update terminal's purpose via Terma API."""
        try:
            # Update purpose through Terma
            # Note: This endpoint may need to be implemented in Terma
            response = httpx.post(
                f"{self.terma_url}/api/mcp/v2/purpose",
                json={
                    "terminal": terminal_name,
                    "purpose": purpose
                },
                timeout=5.0
            )
            
            if response.status_code != 200:
                logger.warning(f"Failed to update purpose via Terma: {response.status_code}")
        except Exception as e:
            logger.warning(f"Could not update purpose via Terma: {e}")
            # Continue anyway - display will still work
    
    def _display_playbook_content(self, purpose: str) -> None:
        """Display playbook content for a given purpose."""
        print(f"=== {purpose.upper()} ===")
        
        # Search for matching files in playbook directory
        found = False
        
        # Check roles directory
        role_file = self.playbook_dir / "roles" / purpose.lower() / "general_description.md"
        if role_file.exists():
            print(f"(from {role_file.relative_to(self.playbook_dir)})")
            with open(role_file) as f:
                print(f.read())
            found = True
            
        # Check projects directory
        project_files = glob.glob(
            str(self.playbook_dir / "projects" / f"*{purpose.lower()}*.md"),
            recursive=False
        )
        for pf in project_files:
            print(f"\n(from {Path(pf).relative_to(self.playbook_dir)})")
            with open(pf) as f:
                print(f.read())
            found = True
            
        # Check tasks directory  
        task_files = glob.glob(
            str(self.playbook_dir / "tasks" / f"*{purpose.lower()}*.md"),
            recursive=False
        )
        for tf in task_files:
            print(f"\n(from {Path(tf).relative_to(self.playbook_dir)})")
            with open(tf) as f:
                print(f.read())
            found = True
            
        # Check for exact match files in root directories
        for subdir in ["roles", "projects", "tasks"]:
            exact_file = self.playbook_dir / subdir / f"{purpose.lower()}.md"
            if exact_file.exists() and str(exact_file) not in project_files + task_files:
                print(f"\n(from {exact_file.relative_to(self.playbook_dir)})")
                with open(exact_file) as f:
                    print(f.read())
                found = True
        
        # Check lessons directory
        lessons_dir = self.playbook_dir / "lessons"
        if lessons_dir.exists():
            lesson_files = glob.glob(
                str(lessons_dir / f"*{purpose.lower()}*.md"),
                recursive=False
            )
            for lf in lesson_files:
                print(f"\n(from {Path(lf).relative_to(self.playbook_dir)})")
                with open(lf) as f:
                    print(f.read())
                found = True
                
            # Also check for exact match in lessons
            exact_lesson = lessons_dir / f"{purpose.lower()}.md"
            if exact_lesson.exists() and str(exact_lesson) not in lesson_files:
                print(f"\n(from {exact_lesson.relative_to(self.playbook_dir)})")
                with open(exact_lesson) as f:
                    print(f.read())
                found = True
        
        if not found:
            print(f"No playbook content found for '{purpose}'")
        
        print()  # Blank line between sections
    
    def show_current_purpose(self) -> None:
        """Show the current terminal's purpose and playbook content."""
        terminal_name = os.environ.get('TERMA_TERMINAL_NAME', '')
        if not terminal_name:
            print("Not in a Terma-launched terminal")
            return
        
        # Get terminal's purpose from Terma
        try:
            response = httpx.get(
                f"{self.terma_url}/api/mcp/v2/terminals/list",
                timeout=5.0
            )
            
            if response.status_code != 200:
                print(f"Error getting terminal list: {response.status_code}")
                return
            
            data = response.json()
            terminals = data.get("terminals", [])
            
            # Find the terminal
            for term in terminals:
                if term.get("name", "").lower() == terminal_name.lower():
                    purpose_string = term.get("purpose", "none")
                    print(f"{terminal_name}: {purpose_string}")
                    print()
                    
                    # If there's a purpose, show the playbook content
                    if purpose_string and purpose_string != "none":
                        purposes = parse_purpose_list(purpose_string)
                        for purpose in purposes:
                            self._display_playbook_content(purpose)
                    
                    # Show full playbook path
                    print(f"Full playbook: {self.playbook_dir}")
                    return
            
            print(f"Terminal '{terminal_name}' not found")
            
        except Exception as e:
            print(f"Error getting terminal purpose: {e}")
    
    def show_terminal_purpose(self, terminal_name: str) -> None:
        """Show a specific terminal's purpose."""
        try:
            # Query Terma for terminal list
            response = httpx.get(
                f"{self.terma_url}/api/mcp/v2/terminals/list",
                timeout=5.0
            )
            
            if response.status_code != 200:
                print(f"Error getting terminal list: {response.status_code}")
                return
            
            data = response.json()
            terminals = data.get("terminals", [])
            
            # Find the terminal
            for term in terminals:
                if term.get("name", "").lower() == terminal_name.lower():
                    purpose = term.get("purpose", "none")
                    print(f"{terminal_name}: {purpose}")
                    return
            
            print(f"Terminal '{terminal_name}' not found")
            
        except Exception as e:
            print(f"Error getting terminal purpose: {e}")


def handle_purpose_command(args: List[str]) -> None:
    """
    Handle the aish purpose command.
    
    Usage: 
        aish purpose                                    # Show current terminal's purpose
        aish purpose <terminal_name>                    # Show specific terminal's purpose
        aish purpose <terminal_name> "<purposes>"       # Update terminal's purpose
    """
    cmd = PurposeCommand()
    
    if len(args) == 0:
        # Show current terminal's purpose
        cmd.show_current_purpose()
    elif len(args) == 1:
        # Show specific terminal's purpose
        terminal_name = args[0]
        cmd.show_terminal_purpose(terminal_name)
    else:
        # Update terminal's purpose
        terminal_name = args[0]
        purpose_string = args[1]
        cmd.execute(terminal_name, purpose_string)