"""
Configuration Generator for Ergon components.

This module provides services for generating wrapper scripts to customize
components for specific applications.
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import jinja2

from ergon.core.repository.models import Component, Tool, AgentComponent, Workflow, Parameter

# Setup logging
logger = logging.getLogger(__name__)

# Setup Jinja2 environment
template_dir = Path(__file__).parent / "templates"
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    trim_blocks=True,
    lstrip_blocks=True,
    autoescape=False
)


class ConfigurationGenerator:
    """Generator for component wrapper scripts."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize the configuration generator.
        
        Args:
            output_dir: Directory to output generated wrappers
        """
        self.output_dir = output_dir or Path.cwd() / "wrappers"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_tool_wrapper(self, 
                           tool: Tool, 
                           params: Dict[str, Any],
                           output_path: Optional[Path] = None) -> Path:
        """Generate a wrapper script for a tool.
        
        Args:
            tool: Tool to generate wrapper for
            params: Parameters to customize the tool
            output_path: Path to output the wrapper
            
        Returns:
            Path to the generated wrapper
        """
        # Validate required parameters
        self._validate_parameters(tool, params)
        
        # Determine output path
        if output_path is None:
            filename = f"{tool.name}_wrapper.py"
            output_path = self.output_dir / filename
        
        # Select the appropriate template based on implementation type
        template_name = f"tool_{tool.implementation_type}_wrapper.py.j2"
        
        try:
            template = env.get_template(template_name)
        except jinja2.exceptions.TemplateNotFound:
            logger.warning(f"Template {template_name} not found, using default")
            template = env.get_template("tool_python_wrapper.py.j2")
        
        # Render the template
        content = template.render(
            tool=tool,
            params=params,
            tool_parameters=self._get_parameters_dict(tool)
        )
        
        # Write the wrapper
        with open(output_path, "w") as f:
            f.write(content)
        
        # Make the wrapper executable
        os.chmod(output_path, 0o755)
        
        return output_path
    
    def generate_agent_wrapper(self,
                            agent: AgentComponent,
                            params: Dict[str, Any],
                            output_path: Optional[Path] = None) -> Path:
        """Generate a wrapper script for an agent.
        
        Args:
            agent: Agent to generate wrapper for
            params: Parameters to customize the agent
            output_path: Path to output the wrapper
            
        Returns:
            Path to the generated wrapper
        """
        # Validate required parameters
        self._validate_parameters(agent, params)
        
        # Determine output path
        if output_path is None:
            filename = f"{agent.name}_wrapper.py"
            output_path = self.output_dir / filename
        
        # Render the template
        template = env.get_template("agent_wrapper.py.j2")
        content = template.render(
            agent=agent,
            params=params,
            agent_parameters=self._get_parameters_dict(agent)
        )
        
        # Write the wrapper
        with open(output_path, "w") as f:
            f.write(content)
        
        # Make the wrapper executable
        os.chmod(output_path, 0o755)
        
        return output_path
    
    def generate_workflow_wrapper(self,
                               workflow: Workflow,
                               params: Dict[str, Any],
                               output_path: Optional[Path] = None) -> Path:
        """Generate a wrapper script for a workflow.
        
        Args:
            workflow: Workflow to generate wrapper for
            params: Parameters to customize the workflow
            output_path: Path to output the wrapper
            
        Returns:
            Path to the generated wrapper
        """
        # Validate required parameters
        self._validate_parameters(workflow, params)
        
        # Determine output path
        if output_path is None:
            filename = f"{workflow.name}_wrapper.py"
            output_path = self.output_dir / filename
        
        # Render the template
        template = env.get_template("workflow_wrapper.py.j2")
        content = template.render(
            workflow=workflow,
            params=params,
            workflow_parameters=self._get_parameters_dict(workflow)
        )
        
        # Write the wrapper
        with open(output_path, "w") as f:
            f.write(content)
        
        # Make the wrapper executable
        os.chmod(output_path, 0o755)
        
        return output_path
    
    def _validate_parameters(self, component: Component, params: Dict[str, Any]) -> None:
        """Validate that all required parameters are provided.
        
        Args:
            component: Component with parameters
            params: Provided parameters
            
        Raises:
            ValueError: If a required parameter is missing
        """
        required_params = {
            p.name for p in component.parameters if p.required
        }
        
        missing_params = required_params - set(params.keys())
        
        if missing_params:
            raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")
    
    def _get_parameters_dict(self, component: Component) -> Dict[str, Dict[str, Any]]:
        """Convert component parameters to a dictionary.
        
        Args:
            component: Component with parameters
            
        Returns:
            Dictionary of parameter information
        """
        return {
            p.name: {
                "description": p.description,
                "type": p.type,
                "required": p.required,
                "default_value": p.default_value
            }
            for p in component.parameters
        }