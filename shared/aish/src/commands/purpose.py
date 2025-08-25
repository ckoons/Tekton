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
from shared.env import TektonEnviron
from shared.urls import terma_url

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
        self.tekton_root = TektonEnviron.get('TEKTON_MAIN_ROOT', TektonEnviron.get('TEKTON_ROOT'))
        if not self.tekton_root:
            raise RuntimeError("TEKTON_ROOT not set in environment")
        self.playbook_dir = Path(self.tekton_root) / ".tekton" / "playbook"
        # Also check MetaData/Documentation/CIPurposes
        self.ci_purposes_dir = Path(self.tekton_root) / "MetaData" / "Documentation" / "CIPurposes"
        # Use terma_url() instead of hardcoded URL
        self.terma_base_url = terma_url()
        
    @state_checkpoint(
        title="Terminal Context Setup",
        description="Sets terminal purpose and displays relevant playbook content",
        state_type="terminal_purpose",
        validation="Purpose string parsed and terminal updated"
    )
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
            
        # Show both playbook paths
        print(f"\nPlaybook locations:")
        print(f"  {self.playbook_dir}")
        print(f"  {self.ci_purposes_dir}")
        
        # If running in the target terminal, export TEKTON_PURPOSE
        current_terminal = TektonEnviron.get('TERMA_TERMINAL_NAME', '')
        if current_terminal.lower() == terminal_name.lower():
            TektonEnviron.set('TEKTON_TERMINAL_PURPOSE', purpose_string)
            print(f"\nExported TEKTON_TERMINAL_PURPOSE='{purpose_string}'")
    
    @integration_point(
        title="Terma Purpose Update",
        description="Updates terminal purpose via Terma API",
        target_component="terma",
        protocol="HTTP POST",
        data_flow="purpose → Terma → terminal state"
    )
    def _update_terminal_purpose(self, terminal_name: str, purpose: str) -> None:
        """Update terminal's purpose via Terma API."""
        try:
            # Update purpose through Terma
            # Note: This endpoint may need to be implemented in Terma
            response = httpx.post(
                f"{self.terma_base_url}/api/mcp/v2/purpose",
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
    
    @api_contract(
        title="Playbook Content Display",
        description="Renders purpose-specific playbook content from filesystem",
        endpoint="internal",
        method="function",
        request_schema={"purpose": "string"},
        response_schema={"content": "stdout"}
    )
    def _display_playbook_content(self, purpose: str) -> None:
        """Display playbook content for a given purpose."""
        print(f"=== {purpose.upper()} ===")
        
        # Search for matching files in both playbook and AIPurposes directories
        found = False
        purpose_lower = purpose.lower()
        
        # First check .tekton/playbook directory
        if self.playbook_dir.exists():
            # Process each top-level directory
            for top_dir in self.playbook_dir.iterdir():
                if not top_dir.is_dir():
                    continue
                    
                # Look for matches at the "targets" level (files and directories in top_dir)
                for item in top_dir.iterdir():
                    item_name = item.stem.lower()  # Remove extension for comparison
                    
                    # Check if this item matches our purpose (case-insensitive)
                    if item_name == purpose_lower:
                        if item.is_file():
                            # File match - print its contents
                            print(f"\n(from {item.relative_to(self.tekton_root)})")
                            try:
                                with open(item, 'r', encoding='utf-8') as f:
                                    print(f.read())
                                found = True
                            except Exception as e:
                                print(f"Error reading file: {e}")
                                
                        elif item.is_dir():
                            # Directory match - print all files recursively
                            found_files = self._print_all_files_in_directory(item)
                            if found_files:
                                found = True
        
        # Then check MetaData/Documentation/CIPurposes directory
        if self.ci_purposes_dir.exists():
            # Look in all subdirectories of CIPurposes
            for subdir in self.ci_purposes_dir.iterdir():
                if subdir.is_dir():
                    # Look for matching files in this subdirectory
                    for item in subdir.iterdir():
                        item_name = item.stem.lower()  # Remove extension for comparison
                        
                        # Check if this item matches our purpose (case-insensitive)
                        if item_name == purpose_lower:
                            if item.is_file():
                                # File match - print its contents
                                print(f"\n(from {item.relative_to(self.tekton_root)})")
                                try:
                                    with open(item, 'r', encoding='utf-8') as f:
                                        print(f.read())
                                    found = True
                                except Exception as e:
                                    print(f"Error reading file: {e}")
                                    
                            elif item.is_dir():
                                # Directory match - print all files recursively
                                found_files = self._print_all_files_in_directory(item)
                                if found_files:
                                    found = True
        
        if not found:
            print(f"No playbook content found for '{purpose}'")
        
        print()  # Blank line between sections
    
    def _print_all_files_in_directory(self, directory: Path) -> bool:
        """Recursively print all files in a directory."""
        found_any = False
        
        # Walk through directory recursively
        for root, dirs, files in os.walk(directory):
            root_path = Path(root)
            
            # Sort files for consistent output
            for filename in sorted(files):
                file_path = root_path / filename
                
                # Skip hidden files and non-text files
                if filename.startswith('.'):
                    continue
                    
                # Print file contents
                # Try to make path relative to tekton_root for better display
                try:
                    rel_path = file_path.relative_to(self.tekton_root)
                except ValueError:
                    # If not under tekton_root, try playbook_dir
                    try:
                        rel_path = file_path.relative_to(self.playbook_dir)
                    except ValueError:
                        rel_path = file_path
                
                print(f"\n(from {rel_path})")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        print(f.read())
                    found_any = True
                except Exception as e:
                    print(f"Error reading file: {e}")
                    
        return found_any
    
    @api_contract(
        title="Current Purpose Display",
        description="Shows current terminal's purpose and associated playbook content",
        endpoint="internal",
        method="function",
        request_schema={},
        response_schema={"purpose": "string", "content": "stdout"}
    )
    def show_current_purpose(self) -> None:
        """Show the current terminal's purpose and playbook content."""
        terminal_name = TektonEnviron.get('TERMA_TERMINAL_NAME', '')
        if not terminal_name:
            print("Not in a Terma-launched terminal")
            return
        
        # Get terminal's purpose from Terma
        try:
            response = httpx.get(
                f"{self.terma_base_url}/api/mcp/v2/terminals/list",
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
    
    @integration_point(
        title="Terminal Purpose Query",
        description="Retrieves specific terminal's purpose from Terma",
        target_component="terma",
        protocol="HTTP GET",
        data_flow="terminal_name → Terma → purpose"
    )
    def show_terminal_purpose(self, terminal_name: str) -> None:
        """Show a specific terminal's purpose."""
        try:
            # Query Terma for terminal list
            response = httpx.get(
                f"{self.terma_base_url}/api/mcp/v2/terminals/list",
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
    
    @integration_point(
        title="Terminal Name Validation",
        description="Validates if name is a known terminal via Terma API",
        target_component="terma",
        protocol="HTTP GET",
        data_flow="name → Terma → boolean"
    )
    def is_terminal_name(self, name: str) -> bool:
        """Check if a name is a known terminal name."""
        try:
            response = httpx.get(
                f"{self.terma_base_url}/api/mcp/v2/terminals/list",
                timeout=5.0
            )
            
            if response.status_code != 200:
                return False
            
            data = response.json()
            terminals = data.get("terminals", [])
            
            # Check if name matches any terminal
            for term in terminals:
                if term.get("name", "").lower() == name.lower():
                    return True
            
            return False
            
        except Exception:
            # If we can't check, assume it's not a terminal name
            return False
    
    @architecture_decision(
        title="CSV Purpose Search",
        description="Parses comma-separated purposes for individual content search",
        rationale="Enables flexible multi-purpose queries matching terminal purpose format",
        alternatives_considered=["Single purpose only", "Regex patterns"],
        impacts=["usability", "consistency"],
        decided_by="Casey",
        decision_date="2025-01-24"
    )
    def search_purpose_content(self, search_term: str) -> None:
        """Search for and display purpose content files."""
        # Parse the search term as a purpose list (handles CSV)
        purposes = parse_purpose_list(search_term)
        
        if not purposes:
            print(f"No valid purposes provided in '{search_term}'")
            return
        
        print(f"Searching for purpose content: {', '.join(purposes)}")
        print()
        
        # Search for each purpose individually
        for purpose in purposes:
            self._search_single_purpose(purpose)
    
    @api_contract(
        title="Purpose Content Search",
        description="Searches filesystem for purpose-specific content files",
        endpoint="internal",
        method="function",
        request_schema={"purpose": "string"},
        response_schema={"found_files": "list", "content": "stdout"}
    )
    def _search_single_purpose(self, purpose: str) -> None:
        """Search for and display content for a single purpose."""
        found_any = False
        purpose_lower = purpose.lower()
        
        # Search locations in order
        search_locations = [
            (self.playbook_dir, "Local playbook"),
            (Path(self.tekton_root) / "MetaData" / "Documentation" / "CIPurposes" / "text", "Shared text purposes"),
            (Path(self.tekton_root) / "MetaData" / "Documentation" / "CIPurposes" / "json", "Shared JSON purposes")
        ]
        
        print(f"=== {purpose.upper()} ===")
        
        for location, description in search_locations:
            if not location.exists():
                continue
                
            # Search for files matching the search term
            matching_files = []
            
            # Look for exact matches first
            for ext in ['', '.txt', '.md', '.json']:
                file_path = location / f"{purpose_lower}{ext}"
                if file_path.exists() and file_path.is_file():
                    matching_files.append(file_path)
            
            # Also search subdirectories in playbook
            if location == self.playbook_dir:
                for subdir in location.iterdir():
                    if subdir.is_dir():
                        for ext in ['', '.txt', '.md', '.json']:
                            file_path = subdir / f"{purpose_lower}{ext}"
                            if file_path.exists() and file_path.is_file():
                                matching_files.append(file_path)
            
            # Display found files
            for file_path in matching_files:
                found_any = True
                print(f"\n(from {file_path.relative_to(self.playbook_dir.parent.parent if location != self.playbook_dir else self.playbook_dir)})")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(content)
                        if not content.endswith('\n'):
                            print()  # Add newline if file doesn't end with one
                except Exception as e:
                    print(f"Error reading file: {e}")
        
        if not found_any:
            print(f"No playbook content found for '{purpose}'")
        
        print()  # Blank line between purposes


@architecture_decision(
    title="Purpose Command Router",
    description="Enables context-aware CI through simple purpose commands",
    rationale="Simple commands provide powerful context - terminals get roles, AIs get purpose content",
    alternatives_considered=["Separate commands for terminals vs content", "Complex query syntax"],
    impacts=["usability", "AI effectiveness", "knowledge management"],
    decided_by="Casey",
    decision_date="2025-01-24"
)
def handle_purpose_command(args: List[str]) -> None:
    """
    Handle the aish purpose command.
    
    Usage: 
        aish purpose                                    # Show current terminal's purpose
        aish purpose <terminal_name>                    # Show specific terminal's purpose
        aish purpose <terminal_name> "<purposes>"       # Update terminal's purpose
        aish purpose "<search_term>"                    # Search for purpose content
    """
    cmd = PurposeCommand()
    
    if len(args) == 0:
        # Show current terminal's purpose
        cmd.show_current_purpose()
    elif len(args) == 1:
        # First check if it's a terminal name
        terminal_name = args[0]
        if cmd.is_terminal_name(terminal_name):
            # Show specific terminal's purpose
            cmd.show_terminal_purpose(terminal_name)
        else:
            # Not a terminal name - search for purpose content
            cmd.search_purpose_content(terminal_name)
    else:
        # Update terminal's purpose
        terminal_name = args[0]
        purpose_string = args[1]
        cmd.execute(terminal_name, purpose_string)