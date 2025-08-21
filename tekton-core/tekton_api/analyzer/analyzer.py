"""
Main repository analyzer for TektonCore.

Coordinates different types of repository analysis including code analysis,
GitHub repository analysis, and Tekton integration assessment.

Moved from Ergon to TektonCore as part of Phase 0 of the Ergon Container Management Sprint.
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

from .analysis.code_analyzer import CodeAnalyzer
from .github.github_analyzer import GitHubAnalyzer

logger = logging.getLogger(__name__)


class AnalysisType(Enum):
    """Types of repository analysis available."""
    BASIC = "basic"
    ARCHITECTURE = "architecture"
    TEKTON = "tekton"
    COMPANION = "companion"
    FULL = "full"


class RepositoryAnalyzer:
    """Main repository analyzer that coordinates different analysis types."""
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize the repository analyzer.
        
        Args:
            github_token: GitHub token for API access
        """
        self.github_analyzer = GitHubAnalyzer(github_token)
        self.code_analyzer = CodeAnalyzer()
        
    async def analyze(self, 
                     repo_url: Optional[str] = None,
                     local_path: Optional[str] = None,
                     analysis_type: AnalysisType = AnalysisType.BASIC) -> Dict[str, Any]:
        """
        Analyze a repository (GitHub URL or local path).
        
        Args:
            repo_url: GitHub repository URL
            local_path: Local repository path
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results dictionary
        """
        try:
            # Validate inputs
            if not repo_url and not local_path:
                return {"error": "Either repo_url or local_path must be provided"}
            
            if repo_url and local_path:
                return {"error": "Provide either repo_url or local_path, not both"}
            
            # Perform analysis based on type
            if repo_url:
                return await self._analyze_github_repository(repo_url, analysis_type)
            else:
                return await self._analyze_local_repository(local_path, analysis_type)
                
        except Exception as e:
            logger.error(f"Error in repository analysis: {str(e)}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    async def _analyze_github_repository(self, repo_url: str, analysis_type: AnalysisType) -> Dict[str, Any]:
        """
        Analyze a GitHub repository.
        
        Args:
            repo_url: GitHub repository URL
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results
        """
        if analysis_type == AnalysisType.BASIC:
            return await self.github_analyzer.analyze_repository_basic(repo_url)
        elif analysis_type == AnalysisType.ARCHITECTURE:
            return await self.github_analyzer.analyze_repository_architecture(repo_url)
        elif analysis_type == AnalysisType.TEKTON:
            return await self.github_analyzer.analyze_repository_tekton(repo_url)
        elif analysis_type == AnalysisType.COMPANION:
            return await self.github_analyzer.analyze_repository_companion(repo_url)
        elif analysis_type == AnalysisType.FULL:
            return await self.github_analyzer.analyze_repository_full(repo_url)
        else:
            return {"error": f"Unknown analysis type: {analysis_type}"}
    
    async def _analyze_local_repository(self, local_path: str, analysis_type: AnalysisType) -> Dict[str, Any]:
        """
        Analyze a local repository.
        
        Args:
            local_path: Local repository path
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results
        """
        # Validate local path
        if not self.github_analyzer.validate_local_path(local_path):
            return {"error": f"Invalid or non-existent repository path: {local_path}"}
        
        # For now, return basic local analysis
        # In a full implementation, this would scan the local files
        return {
            "repository": {
                "path": local_path,
                "type": "local"
            },
            "analysis_type": analysis_type.value,
            "timestamp": "2025-08-19T00:00:00Z",
            "summary": {
                "status": "Local repository analysis not yet fully implemented",
                "path_validated": True
            },
            "recommendations": [
                "Local repository scanning will be implemented in future versions",
                "Consider using GitHub URL for full analysis capabilities"
            ]
        }
    
    def get_supported_analysis_types(self) -> list[str]:
        """
        Get list of supported analysis types.
        
        Returns:
            List of analysis type names
        """
        return [analysis_type.value for analysis_type in AnalysisType]
    
    def get_analysis_description(self, analysis_type: AnalysisType) -> str:
        """
        Get description of what an analysis type does.
        
        Args:
            analysis_type: Analysis type to describe
            
        Returns:
            Description string
        """
        descriptions = {
            AnalysisType.BASIC: "Basic repository information including languages, frameworks, and structure",
            AnalysisType.ARCHITECTURE: "Architectural patterns, design principles, and code organization analysis",
            AnalysisType.TEKTON: "Assessment of Tekton integration opportunities and compatibility",
            AnalysisType.COMPANION: "Evaluation of Companion Intelligence enhancement potential", 
            AnalysisType.FULL: "Comprehensive analysis combining all analysis types"
        }
        return descriptions.get(analysis_type, "Unknown analysis type")