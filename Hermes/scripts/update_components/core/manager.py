"""
Update manager for coordinating component updates.
"""

from pathlib import Path
from typing import Dict, List, Any

from hermes.utils.logging_helper import setup_logging

from ..updaters.engram import update_engram
from ..updaters.ergon import update_ergon
from ..updaters.athena import update_athena
from ..updaters.harmonia import update_harmonia
from ..updaters.hermes import update_hermes_itself


class UpdateManager:
    """
    Manager for coordinating updates to Tekton components.
    """
    
    def __init__(self, tekton_root: Path, logger=None):
        """
        Initialize the update manager.
        
        Args:
            tekton_root: Path to the Tekton root directory
            logger: Optional logger instance
        """
        self.tekton_root = tekton_root
        self.logger = logger or setup_logging("hermes.scripts.update_all_components")
        self.results = {}
    
    def update_components(self, components: List[str]) -> Dict[str, bool]:
        """
        Update specified components.
        
        Args:
            components: List of component names to update
            
        Returns:
            Dict mapping component names to update success (True/False)
        """
        self.results = {}
        
        # Update Hermes itself first if requested
        if "hermes" in components:
            hermes_path = self.tekton_root / "Hermes"
            self.results["hermes"] = update_hermes_itself(hermes_path, self.logger)
        
        # Update other components
        component_updaters = {
            "engram": self._update_engram,
            "ergon": self._update_ergon,
            "athena": self._update_athena,
            "harmonia": self._update_harmonia
        }
        
        for component in components:
            if component in component_updaters and component != "hermes":
                component_updaters[component]()
        
        return self.results
    
    def _update_engram(self) -> bool:
        """Update Engram component."""
        engram_path = self.tekton_root / "Engram"
        result = update_engram(engram_path, self.logger)
        self.results["engram"] = result
        return result
    
    def _update_ergon(self) -> bool:
        """Update Ergon component."""
        ergon_path = self.tekton_root / "Ergon"
        result = update_ergon(ergon_path, self.logger)
        self.results["ergon"] = result
        return result
    
    def _update_athena(self) -> bool:
        """Update Athena component."""
        athena_path = self.tekton_root / "Athena"
        result = update_athena(athena_path, self.logger)
        self.results["athena"] = result
        return result
    
    def _update_harmonia(self) -> bool:
        """Update Harmonia component."""
        harmonia_path = self.tekton_root / "Harmonia"
        result = update_harmonia(harmonia_path, self.logger)
        self.results["harmonia"] = result
        return result
    
    def print_summary(self) -> None:
        """Print a summary of update results."""
        self.logger.info("Update summary:")
        for component, success in self.results.items():
            self.logger.info(f"  {component}: {'Updated' if success else 'Failed'}")