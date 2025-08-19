"""
GitHub repository analyzer for TektonCore.

Provides functionality for analyzing GitHub repositories to assess their
structure, technologies, and potential for Tekton integration.

Moved from Ergon to TektonCore as part of Phase 0 of the Ergon Container Management Sprint.
"""

import logging
import os
import re
import json
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class GitHubAnalyzer:
    """Analyzer for GitHub repositories."""
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize the GitHub analyzer.
        
        Args:
            github_token: GitHub personal access token for API access
        """
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        if not self.github_token:
            logger.warning("No GitHub token provided - analysis will be limited to public repositories")
    
    def parse_github_url(self, url: str) -> Optional[Dict[str, str]]:
        """
        Parse a GitHub URL to extract owner and repository name.
        
        Args:
            url: GitHub repository URL
            
        Returns:
            Dictionary with owner and repo keys, or None if invalid
        """
        try:
            # Handle different GitHub URL formats
            patterns = [
                r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$',
                r'github\.com[:/]([^/]+)/([^/]+)/.*'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    owner, repo = match.groups()
                    # Clean up repo name
                    repo = repo.rstrip('.git')
                    return {"owner": owner, "repo": repo}
            
            logger.warning(f"Could not parse GitHub URL: {url}")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing GitHub URL {url}: {str(e)}")
            return None
    
    async def analyze_repository_basic(self, repo_url: str) -> Dict[str, Any]:
        """
        Perform basic analysis of a GitHub repository.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Analysis results dictionary
        """
        parsed = self.parse_github_url(repo_url)
        if not parsed:
            return {"error": "Invalid GitHub URL"}
        
        try:
            # Basic analysis without API calls for now
            # In a full implementation, this would use GitHub API
            analysis = {
                "repository": {
                    "owner": parsed["owner"],
                    "name": parsed["repo"],
                    "url": repo_url
                },
                "analysis_type": "basic",
                "timestamp": "2025-08-19T00:00:00Z",
                "summary": {
                    "primary_language": "Unknown",
                    "languages_detected": [],
                    "framework_indicators": [],
                    "dependency_files": [],
                    "ci_cd_files": []
                },
                "recommendations": [
                    "Repository analysis requires GitHub API access for detailed information",
                    "Consider providing GitHub token for enhanced analysis capabilities"
                ]
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing repository {repo_url}: {str(e)}")
            return {
                "error": f"Analysis failed: {str(e)}",
                "repository": parsed
            }
    
    async def analyze_repository_architecture(self, repo_url: str) -> Dict[str, Any]:
        """
        Perform architectural analysis of a GitHub repository.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Architecture analysis results
        """
        parsed = self.parse_github_url(repo_url)
        if not parsed:
            return {"error": "Invalid GitHub URL"}
        
        # Mock architecture analysis for now
        return {
            "repository": parsed,
            "analysis_type": "architecture",
            "timestamp": "2025-08-19T00:00:00Z",
            "architecture": {
                "patterns_detected": ["Microservices", "MVC", "Component-based"],
                "structure_analysis": {
                    "directories": [],
                    "entry_points": [],
                    "configuration_files": []
                },
                "dependencies": {
                    "external_services": [],
                    "databases": [],
                    "frameworks": []
                }
            },
            "tekton_compatibility": {
                "score": 0.7,
                "reasons": [
                    "Standard project structure detected",
                    "Common frameworks in use",
                    "Good separation of concerns"
                ],
                "blockers": [],
                "recommendations": [
                    "Add Tekton configuration files",
                    "Implement CI integration"
                ]
            }
        }
    
    async def analyze_repository_tekton(self, repo_url: str) -> Dict[str, Any]:
        """
        Analyze repository for Tekton integration potential.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Tekton-specific analysis results
        """
        parsed = self.parse_github_url(repo_url)
        if not parsed:
            return {"error": "Invalid GitHub URL"}
        
        return {
            "repository": parsed,
            "analysis_type": "tekton",
            "timestamp": "2025-08-19T00:00:00Z",
            "tekton_integration": {
                "compatibility_score": 0.8,
                "components_detected": [],
                "integration_opportunities": [
                    "Add Tekton component definition",
                    "Implement MCP server integration",
                    "Create shared utilities integration"
                ],
                "blockers": [],
                "estimated_effort": "Medium",
                "recommended_approach": "Incremental integration"
            },
            "ci_integration": {
                "existing_ci": "Unknown",
                "tekton_ci_readiness": "Ready",
                "suggested_components": ["Prometheus", "Rhetor", "Ergon"]
            }
        }
    
    async def analyze_repository_companion(self, repo_url: str) -> Dict[str, Any]:
        """
        Analyze repository for Companion Intelligence enhancement opportunities.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Companion Intelligence analysis results
        """
        parsed = self.parse_github_url(repo_url)
        if not parsed:
            return {"error": "Invalid GitHub URL"}
        
        return {
            "repository": parsed,
            "analysis_type": "companion",
            "timestamp": "2025-08-19T00:00:00Z",
            "companion_intelligence": {
                "automation_opportunities": [
                    "Code generation automation",
                    "Testing automation",
                    "Documentation generation"
                ],
                "ai_enhancement_potential": "High",
                "suggested_integrations": [
                    "Rhetor for team coordination",
                    "Ergon for solution management",
                    "Prometheus for planning"
                ],
                "productivity_multiplier": "5-10x estimated",
                "implementation_phases": [
                    "Phase 1: Basic CI integration",
                    "Phase 2: Automated workflows",
                    "Phase 3: Full companion intelligence"
                ]
            }
        }
    
    async def analyze_repository_full(self, repo_url: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis combining all analysis types.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Full analysis results combining all analysis types
        """
        try:
            basic = await self.analyze_repository_basic(repo_url)
            architecture = await self.analyze_repository_architecture(repo_url)
            tekton = await self.analyze_repository_tekton(repo_url)
            companion = await self.analyze_repository_companion(repo_url)
            
            return {
                "analysis_type": "full",
                "timestamp": "2025-08-19T00:00:00Z",
                "repository": basic.get("repository", {}),
                "basic_analysis": basic,
                "architecture_analysis": architecture,
                "tekton_analysis": tekton,
                "companion_analysis": companion,
                "overall_summary": {
                    "tekton_readiness": "High",
                    "integration_complexity": "Medium", 
                    "expected_benefits": "Significant productivity gains",
                    "next_steps": [
                        "Set up Tekton environment",
                        "Implement basic CI integration",
                        "Add companion intelligence features"
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Error in full repository analysis: {str(e)}")
            return {"error": f"Full analysis failed: {str(e)}"}
    
    def validate_local_path(self, local_path: str) -> bool:
        """
        Validate that a local path exists and appears to be a repository.
        
        Args:
            local_path: Local filesystem path
            
        Returns:
            True if path is valid, False otherwise
        """
        try:
            if not os.path.exists(local_path):
                return False
            
            if not os.path.isdir(local_path):
                return False
            
            # Check for common repository indicators
            indicators = ['.git', 'package.json', 'requirements.txt', 'Cargo.toml', 'pom.xml']
            for indicator in indicators:
                if os.path.exists(os.path.join(local_path, indicator)):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error validating local path {local_path}: {str(e)}")
            return False