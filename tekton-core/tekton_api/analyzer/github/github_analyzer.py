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
import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from datetime import datetime

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
        self.api_base = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "TektonCore-Analyzer"
        }
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"
        else:
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
    
    async def _fetch_github_api(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """
        Fetch data from GitHub API.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            JSON response or None on error
        """
        url = f"{self.api_base}{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        logger.warning(f"GitHub resource not found: {endpoint}")
                        return None
                    else:
                        logger.error(f"GitHub API error {response.status}: {endpoint}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching from GitHub API: {str(e)}")
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
            # Fetch repository information
            repo_data = await self._fetch_github_api(f"/repos/{parsed['owner']}/{parsed['repo']}")
            
            if not repo_data:
                return {
                    "error": "Could not fetch repository data",
                    "repository": {
                        "owner": parsed["owner"],
                        "name": parsed["repo"],
                        "url": repo_url
                    }
                }
            
            # Fetch languages
            languages_data = await self._fetch_github_api(f"/repos/{parsed['owner']}/{parsed['repo']}/languages")
            
            # Fetch directory structure (contents of root)
            contents_data = await self._fetch_github_api(f"/repos/{parsed['owner']}/{parsed['repo']}/contents")
            
            # Analyze files for frameworks and tools
            framework_indicators = []
            dependency_files = []
            ci_cd_files = []
            
            if contents_data:
                for item in contents_data:
                    name = item.get('name', '').lower()
                    
                    # Check for dependency files
                    if name in ['package.json', 'requirements.txt', 'cargo.toml', 'go.mod', 'pom.xml', 'build.gradle']:
                        dependency_files.append(name)
                        
                        # Infer frameworks from dependency files
                        if name == 'package.json':
                            framework_indicators.append('Node.js/JavaScript')
                        elif name == 'requirements.txt':
                            framework_indicators.append('Python')
                        elif name == 'cargo.toml':
                            framework_indicators.append('Rust')
                        elif name == 'go.mod':
                            framework_indicators.append('Go')
                        elif name in ['pom.xml', 'build.gradle']:
                            framework_indicators.append('Java')
                    
                    # Check for CI/CD files
                    if name in ['.travis.yml', '.circleci', 'jenkinsfile', '.gitlab-ci.yml']:
                        ci_cd_files.append(name)
                    
                    # Check for GitHub Actions
                    if name == '.github':
                        ci_cd_files.append('GitHub Actions')
                        
                    # Check for Docker
                    if name in ['dockerfile', 'docker-compose.yml', 'docker-compose.yaml']:
                        framework_indicators.append('Docker')
                        
                    # Check for Kubernetes
                    if name in ['k8s', 'kubernetes', 'helm']:
                        framework_indicators.append('Kubernetes')
            
            # Build analysis result
            analysis = {
                "repository": {
                    "owner": parsed["owner"],
                    "name": parsed["repo"],
                    "url": repo_url,
                    "description": repo_data.get('description', ''),
                    "stars": repo_data.get('stargazers_count', 0),
                    "forks": repo_data.get('forks_count', 0),
                    "language": repo_data.get('language', 'Unknown'),
                    "created_at": repo_data.get('created_at', ''),
                    "updated_at": repo_data.get('updated_at', ''),
                    "topics": repo_data.get('topics', [])
                },
                "analysis_type": "basic",
                "timestamp": datetime.utcnow().isoformat() + 'Z',
                "summary": {
                    "primary_language": repo_data.get('language', 'Unknown'),
                    "languages_detected": list(languages_data.keys()) if languages_data else [],
                    "framework_indicators": list(set(framework_indicators)),
                    "dependency_files": dependency_files,
                    "ci_cd_files": ci_cd_files,
                    "has_issues": repo_data.get('has_issues', False),
                    "has_wiki": repo_data.get('has_wiki', False),
                    "has_pages": repo_data.get('has_pages', False),
                    "size_kb": repo_data.get('size', 0)
                },
                "recommendations": []
            }
            
            # Add recommendations based on analysis
            if not framework_indicators:
                analysis["recommendations"].append("Consider adding dependency management files")
            
            if not ci_cd_files:
                analysis["recommendations"].append("Consider adding CI/CD pipeline with GitHub Actions")
            
            if 'Docker' not in framework_indicators:
                analysis["recommendations"].append("Consider containerizing with Docker for Tekton deployment")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing repository: {str(e)}")
            return {
                "error": f"Analysis failed: {str(e)}",
                "repository": {
                    "owner": parsed["owner"],
                    "name": parsed["repo"],
                    "url": repo_url
                }
            }
    
    async def analyze_repository_architecture(self, repo_url: str) -> Dict[str, Any]:
        """
        Perform architecture analysis of a GitHub repository.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Analysis results dictionary
        """
        # Start with basic analysis
        basic_analysis = await self.analyze_repository_basic(repo_url)
        
        if "error" in basic_analysis:
            return basic_analysis
        
        # Enhance with architecture analysis
        basic_analysis["analysis_type"] = "architecture"
        
        # Add architecture-specific insights
        architecture_insights = {
            "patterns_detected": [],
            "design_principles": [],
            "scalability_assessment": "Unknown"
        }
        
        # Detect patterns based on file structure
        if basic_analysis["summary"].get("dependency_files"):
            if "package.json" in basic_analysis["summary"]["dependency_files"]:
                architecture_insights["patterns_detected"].append("JavaScript/Node.js application")
                
            if "requirements.txt" in basic_analysis["summary"]["dependency_files"]:
                architecture_insights["patterns_detected"].append("Python application")
        
        if basic_analysis["summary"].get("ci_cd_files"):
            architecture_insights["patterns_detected"].append("CI/CD enabled")
            architecture_insights["design_principles"].append("Continuous Integration")
        
        if "Docker" in basic_analysis["summary"].get("framework_indicators", []):
            architecture_insights["patterns_detected"].append("Containerized application")
            architecture_insights["design_principles"].append("Container-based deployment")
            architecture_insights["scalability_assessment"] = "Good - containerized"
        
        if "Kubernetes" in basic_analysis["summary"].get("framework_indicators", []):
            architecture_insights["patterns_detected"].append("Kubernetes-ready")
            architecture_insights["design_principles"].append("Cloud-native")
            architecture_insights["scalability_assessment"] = "Excellent - Kubernetes-ready"
        
        basic_analysis["architecture"] = architecture_insights
        
        return basic_analysis
    
    async def analyze_repository_tekton(self, repo_url: str) -> Dict[str, Any]:
        """
        Perform Tekton integration analysis.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Analysis results dictionary
        """
        # Start with architecture analysis
        arch_analysis = await self.analyze_repository_architecture(repo_url)
        
        if "error" in arch_analysis:
            return arch_analysis
        
        arch_analysis["analysis_type"] = "tekton"
        
        # Assess Tekton integration potential
        tekton_assessment = {
            "integration_score": 0,
            "integration_difficulty": "Unknown",
            "required_adaptations": [],
            "benefits": [],
            "recommended_ci_type": "gpt-oss:20b"
        }
        
        # Score based on existing capabilities
        if "Docker" in arch_analysis["summary"].get("framework_indicators", []):
            tekton_assessment["integration_score"] += 30
            tekton_assessment["benefits"].append("Already containerized")
        else:
            tekton_assessment["required_adaptations"].append("Add Dockerfile")
        
        if "Kubernetes" in arch_analysis["summary"].get("framework_indicators", []):
            tekton_assessment["integration_score"] += 30
            tekton_assessment["benefits"].append("Kubernetes-ready")
        
        if arch_analysis["summary"].get("ci_cd_files"):
            tekton_assessment["integration_score"] += 20
            tekton_assessment["benefits"].append("Existing CI/CD can be migrated")
        
        # Determine difficulty
        if tekton_assessment["integration_score"] >= 60:
            tekton_assessment["integration_difficulty"] = "Easy"
        elif tekton_assessment["integration_score"] >= 30:
            tekton_assessment["integration_difficulty"] = "Moderate"
        else:
            tekton_assessment["integration_difficulty"] = "Complex"
        
        # Recommend CI based on project complexity
        if arch_analysis["repository"].get("size_kb", 0) > 10000:
            tekton_assessment["recommended_ci_type"] = "gpt-oss:120b"
            
        arch_analysis["tekton_integration"] = tekton_assessment
        
        return arch_analysis
    
    async def analyze_repository_companion(self, repo_url: str) -> Dict[str, Any]:
        """
        Perform Companion Intelligence analysis.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Analysis results dictionary
        """
        # Start with Tekton analysis
        tekton_analysis = await self.analyze_repository_tekton(repo_url)
        
        if "error" in tekton_analysis:
            return tekton_analysis
        
        tekton_analysis["analysis_type"] = "companion"
        
        # Assess CI enhancement potential
        ci_assessment = {
            "ai_integration_potential": "Unknown",
            "recommended_ci": "gpt-oss:20b",
            "automation_opportunities": [],
            "intelligence_features": []
        }
        
        # Assess based on project characteristics
        primary_lang = tekton_analysis["summary"].get("primary_language", "").lower()
        
        if primary_lang in ["python", "javascript", "typescript", "go", "rust"]:
            ci_assessment["ai_integration_potential"] = "High"
            ci_assessment["automation_opportunities"].append(f"Automated {primary_lang} code generation")
            ci_assessment["intelligence_features"].append("Code completion and suggestions")
        
        if tekton_analysis["summary"].get("dependency_files"):
            ci_assessment["automation_opportunities"].append("Dependency management automation")
            ci_assessment["intelligence_features"].append("Security vulnerability scanning")
        
        if tekton_analysis["summary"].get("ci_cd_files"):
            ci_assessment["automation_opportunities"].append("CI/CD pipeline optimization")
            ci_assessment["intelligence_features"].append("Build failure prediction")
        
        # Complex projects need smarter CI
        if tekton_analysis["repository"].get("size_kb", 0) > 5000:
            ci_assessment["recommended_ci"] = "gpt-oss:120b"
            ci_assessment["intelligence_features"].append("Deep code analysis")
        
        # Add Claude as option for advanced features
        ci_assessment["available_companions"] = [
            "gpt-oss:20b (Fast, general purpose)",
            "gpt-oss:120b (Smart, deep thinking)",
            "claude (Advanced reasoning)",
            "llama3.3:70b (Balanced)",
            "llama3.2:3b (Lightweight)"
        ]
        
        tekton_analysis["companion_intelligence"] = ci_assessment
        
        return tekton_analysis
    
    async def analyze_repository_full(self, repo_url: str) -> Dict[str, Any]:
        """
        Perform full comprehensive analysis.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Analysis results dictionary
        """
        # Get companion analysis (which includes everything)
        full_analysis = await self.analyze_repository_companion(repo_url)
        
        if "error" in full_analysis:
            return full_analysis
        
        full_analysis["analysis_type"] = "full"
        
        # Add comprehensive summary
        full_analysis["comprehensive_summary"] = {
            "overall_health": "Good" if full_analysis.get("tekton_integration", {}).get("integration_score", 0) >= 50 else "Needs improvement",
            "readiness_for_tekton": full_analysis.get("tekton_integration", {}).get("integration_difficulty", "Unknown"),
            "recommended_next_steps": []
        }
        
        # Generate next steps
        if "Docker" not in full_analysis["summary"].get("framework_indicators", []):
            full_analysis["comprehensive_summary"]["recommended_next_steps"].append("Add Docker containerization")
        
        if not full_analysis["summary"].get("ci_cd_files"):
            full_analysis["comprehensive_summary"]["recommended_next_steps"].append("Set up CI/CD pipeline")
        
        full_analysis["comprehensive_summary"]["recommended_next_steps"].append("Create Tekton project with recommended CI")
        
        return full_analysis
    
    def validate_local_path(self, path: str) -> bool:
        """
        Validate that a local path exists and is a directory.
        
        Args:
            path: Local directory path
            
        Returns:
            True if valid, False otherwise
        """
        expanded_path = os.path.expanduser(path)
        return os.path.exists(expanded_path) and os.path.isdir(expanded_path)