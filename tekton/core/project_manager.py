"""
TektonCore Project Management System

Enhanced project management with:
- Correct path handling ($TEKTON_ROOT/.tekton/projects/)
- Project name extraction from git URLs
- Git remote detection
- Thread-safe JSON operations
"""

import os
import json
import uuid
import asyncio
import subprocess
import fcntl
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
from urllib.parse import urlparse

from shared.utils.logging_setup import setup_component_logging
from shared.env import TektonEnviron

# Import landmarks for architectural documentation
try:
    from landmarks import (
        architecture_decision,
        integration_point,
        api_contract,
        state_checkpoint
    )
except ImportError:
    # Landmarks not available, define no-op decorators
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def api_contract(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

logger = setup_component_logging("tekton_core.project_manager")


class ProjectState(str, Enum):
    """Project lifecycle states"""
    DEV_SPRINT = "dev_sprint"          # Initial idea documented
    QUEUED = "queued"                  # Approved for project queue
    PLANNING = "planning"              # Active planning phase
    APPROVED = "approved"              # Ready for development
    ACTIVE = "active"                  # Development in progress
    COMPLETE = "complete"              # All objectives achieved
    ARCHIVED = "archived"              # Completed and archived


@dataclass
class GitRemotes:
    """Git remote information"""
    origin: Optional[str] = None
    upstream: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Optional[str]]:
        return {"origin": self.origin, "upstream": self.upstream}


@state_checkpoint(
    title="TektonCore Project State",
    state_type="persistent",
    description="Core project data model managing GitHub integration and AI companion settings",
    rationale="Centralized project state with name extraction hierarchy and git remote tracking"
)
@dataclass
class Project:
    """Enhanced project data model for TektonCore"""
    id: str
    name: str  # Extracted from git URLs or directory name
    description: str
    state: ProjectState
    
    # GitHub integration fields
    github_url: Optional[str] = None  # Primary GitHub URL (from New Project form)
    local_directory: Optional[str] = None  # Local working directory path
    forked_repository: Optional[str] = None  # Fork remote URL
    upstream_repository: Optional[str] = None  # Upstream remote URL
    
    # AI and metadata
    companion_intelligence: Optional[str] = None  # Selected AI model
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    added_date: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Special flags
    is_tekton_self: bool = False  # True if this is Tekton managing itself
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@architecture_decision(
    title="Project Name Extraction Hierarchy",
    description="Extracts project names from fork → upstream → directory in priority order",
    rationale="Consistent project naming that respects user's fork preferences while falling back gracefully",
    alternatives_considered=["Directory name only", "Git remote origin only", "User-specified names"],
    impacts=["user_experience", "project_identification", "integration_consistency"]
)
class ProjectNameExtractor:
    """Utility class for extracting project names from various sources"""
    
    @api_contract(
        title="GitHub URL Name Extraction",
        endpoint="extract_from_github_url",
        method="STATIC",
        request_schema={"url": "str"},
        response_schema={"name": "Optional[str]"},
        description="Extracts repository name from GitHub URL, supporting HTTPS and SSH formats"
    )
    @staticmethod
    def extract_from_github_url(url: str) -> Optional[str]:
        """Extract project name from GitHub URL
        
        Examples:
        - https://github.com/cskoons/Tekton.git → "Tekton"
        - https://github.com/cskoons/Tekton → "Tekton"
        - git@github.com:cskoons/Tekton.git → "Tekton"
        """
        if not url:
            return None
            
        try:
            # Handle SSH URLs
            if url.startswith("git@"):
                # git@github.com:user/repo.git
                parts = url.split(":")
                if len(parts) == 2:
                    repo_path = parts[1]
                    # Remove .git suffix if present
                    if repo_path.endswith(".git"):
                        repo_path = repo_path[:-4]
                    # Get repo name from path
                    return repo_path.split("/")[-1]
            
            # Handle HTTPS URLs
            parsed = urlparse(url)
            path = parsed.path.strip("/")
            
            # Remove .git suffix if present
            if path.endswith(".git"):
                path = path[:-4]
            
            # Get the last part of the path (repo name)
            parts = path.split("/")
            if len(parts) >= 2:
                return parts[-1]
                
        except Exception as e:
            logger.warning(f"Failed to extract name from URL {url}: {e}")
            
        return None
    
    @staticmethod
    def extract_from_directory(directory: str) -> str:
        """Extract project name from directory path
        
        Example: /Users/cskoons/projects/github/Tekton → "Tekton"
        """
        return Path(directory).name


@integration_point(
    title="GitHub CLI Validation",
    target_component="github_cli",
    protocol="subprocess",
    data_flow="GitHubCLIValidator → gh command → validation status",
    description="Validates GitHub CLI installation and authentication"
)
class GitHubCLIValidator:
    """Utility class for validating GitHub CLI setup"""
    
    @staticmethod
    def validate_github_cli() -> Tuple[bool, str]:
        """
        Validate GitHub CLI installation and authentication.
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            # Check gh installed
            version_cmd = ["gh", "--version"]
            logger.info(f"[GIT] Executing command: {' '.join(version_cmd)}")
            
            result = subprocess.run(
                version_cmd, 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            logger.info(f"[GIT] Version command completed with exit code: {result.returncode}")
            if result.stdout:
                logger.info(f"[GIT] GitHub CLI version: {result.stdout.strip()}")
            
            # Check gh authenticated
            auth_cmd = ["gh", "auth", "status"]
            logger.info(f"[GIT] Executing command: {' '.join(auth_cmd)}")
            
            result = subprocess.run(
                auth_cmd, 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            logger.info(f"[GIT] Auth command completed with exit code: {result.returncode}")
            if result.stdout:
                logger.info(f"[GIT] Auth command stdout: {result.stdout}")
            if result.stderr:
                logger.info(f"[GIT] Auth command stderr: {result.stderr}")
            
            logger.info("[GIT] GitHub CLI authentication verified")
            
            return True, ""
            
        except FileNotFoundError:
            error_msg = "GitHub CLI (gh) is not installed. Please install it from https://cli.github.com/ and run 'gh auth login'"
            logger.error(f"[GIT] {error_msg}")
            return False, error_msg
            
        except subprocess.CalledProcessError as e:
            logger.error(f"[GIT] Command failed with exit code: {e.returncode}")
            if e.stdout:
                logger.error(f"[GIT] Command stdout: {e.stdout}")
            if e.stderr:
                logger.error(f"[GIT] Command stderr: {e.stderr}")
                
            if "gh auth" in str(e.cmd):
                error_msg = "GitHub CLI is not authenticated. Please run 'gh auth login' and try again"
            else:
                error_msg = f"GitHub CLI error: {e.stderr.strip() if e.stderr else 'Unknown error'}"
            logger.error(f"[GIT] {error_msg}")
            return False, error_msg


@integration_point(
    title="Git Remote Detection",
    target_component="git",
    protocol="subprocess",
    data_flow="GitRemoteDetector → git command → remote URLs",
    description="Detects git remotes in project directories using git CLI"
)
class GitRemoteDetector:
    """Utility class for detecting git remotes"""
    
    @api_contract(
        title="Git Remote Detection API",
        endpoint="detect_remotes",
        method="STATIC_ASYNC",
        request_schema={"directory": "str"},
        response_schema={"remotes": "GitRemotes"},
        description="Detects origin and upstream remotes in a git directory"
    )
    @staticmethod
    async def detect_remotes(directory: str) -> GitRemotes:
        """Detect git remotes in a directory"""
        remotes = GitRemotes()
        
        if not os.path.exists(directory):
            return remotes
            
        try:
            # Run git remote -v to get all remotes
            remote_cmd = ["git", "-C", directory, "remote", "-v"]
            logger.info(f"[GIT] Executing command: {' '.join(remote_cmd)}")
            
            result = subprocess.run(
                remote_cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            logger.info(f"[GIT] Remote command completed with exit code: {result.returncode}")
            if result.stdout:
                logger.info(f"[GIT] Remote command stdout: {result.stdout}")
            if result.stderr:
                logger.info(f"[GIT] Remote command stderr: {result.stderr}")
            
            if result.returncode == 0:
                # Parse output
                for line in result.stdout.strip().split("\n"):
                    if not line:
                        continue
                        
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        remote_name = parts[0]
                        remote_url = parts[1].split(" ")[0]  # Remove (fetch)/(push)
                        
                        if remote_name == "origin":
                            remotes.origin = remote_url
                            logger.info(f"[GIT] Found origin remote: {remote_url}")
                        elif remote_name == "upstream":
                            remotes.upstream = remote_url
                            logger.info(f"[GIT] Found upstream remote: {remote_url}")
                            
        except Exception as e:
            logger.warning(f"[GIT] Failed to detect git remotes in {directory}: {e}")
            
        return remotes
    
    @staticmethod
    def is_git_repository(directory: str) -> bool:
        """Check if directory is a git repository"""
        return os.path.exists(os.path.join(directory, ".git"))


@architecture_decision(
    title="Thread-Safe JSON Project Storage",
    description="Uses file locking for thread-safe JSON operations on project data",
    rationale="Simple, reliable persistence without database dependencies while supporting concurrent access",
    alternatives_considered=["SQLite database", "In-memory storage", "Unsynchronized JSON"],
    impacts=["data_integrity", "concurrent_access", "deployment_simplicity"]
)
@state_checkpoint(
    title="Project Registry Storage",
    state_type="persistent",
    description="Central registry for all TektonCore projects with thread-safe access",
    rationale="Single source of truth for project metadata and state"
)
class ProjectRegistry:
    """JSON-based project storage system with thread safety"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize project registry"""
        if storage_path is None:
            # Use $TEKTON_ROOT/.tekton/projects/
            from shared.env import TektonEnviron
            tekton_root = TektonEnviron.get("TEKTON_ROOT") or os.getcwd()
            storage_path = os.path.join(tekton_root, ".tekton", "projects")
        
        self.storage_path = Path(storage_path)
        self.projects_file = self.storage_path / "projects.json"
        self._lock_file = self.storage_path / ".projects.lock"
        
        # Ensure directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize projects file if it doesn't exist
        if not self.projects_file.exists():
            self._create_empty_projects_file()
            
        logger.info(f"Project registry initialized at {self.storage_path}")
    
    def _create_empty_projects_file(self):
        """Create empty projects file"""
        projects_data = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "projects": []
        }
        
        with open(self.projects_file, 'w') as f:
            json.dump(projects_data, f, indent=2)
    
    @api_contract(
        title="File Lock Management",
        endpoint="_acquire_lock",
        method="PRIVATE",
        request_schema={},
        response_schema={"lock_fd": "int"},
        description="Acquires exclusive file lock for thread-safe JSON operations"
    )
    def _acquire_lock(self):
        """Acquire file lock for thread safety"""
        lock_file = open(self._lock_file, 'w')
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        return lock_file
    
    def _release_lock(self, lock_file):
        """Release file lock"""
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        lock_file.close()
    
    def _load_projects(self) -> Dict[str, Any]:
        """Load projects from file with thread safety"""
        lock_file = self._acquire_lock()
        try:
            with open(self.projects_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load projects: {e}")
            self._create_empty_projects_file()
            return self._load_projects()
        finally:
            self._release_lock(lock_file)
    
    def _save_projects(self, projects_data: Dict[str, Any]):
        """Save projects to file with thread safety"""
        lock_file = self._acquire_lock()
        try:
            projects_data["updated_at"] = datetime.now().isoformat()
            
            # Write to temporary file first
            temp_file = self.projects_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(projects_data, f, indent=2)
            
            # Atomic rename
            temp_file.replace(self.projects_file)
            
        finally:
            self._release_lock(lock_file)
    
    def create_project(self, **kwargs) -> Project:
        """Create a new project"""
        # Extract project name
        name = kwargs.get("name")
        if not name:
            # Try to extract from URLs or directory
            if kwargs.get("forked_repository"):
                name = ProjectNameExtractor.extract_from_github_url(kwargs["forked_repository"])
            elif kwargs.get("upstream_repository"):
                name = ProjectNameExtractor.extract_from_github_url(kwargs["upstream_repository"])
            elif kwargs.get("local_directory"):
                name = ProjectNameExtractor.extract_from_directory(kwargs["local_directory"])
            else:
                name = "Unnamed Project"
        
        # Create project
        project = Project(
            id=str(uuid.uuid4()),
            name=name,
            description=kwargs.get("description", ""),
            state=ProjectState.ACTIVE,
            github_url=kwargs.get("github_url"),
            local_directory=kwargs.get("local_directory"),
            forked_repository=kwargs.get("forked_repository"),
            upstream_repository=kwargs.get("upstream_repository"),
            companion_intelligence=kwargs.get("companion_intelligence"),
            is_tekton_self=kwargs.get("is_tekton_self", False),
            metadata=kwargs.get("metadata", {})
        )
        
        # Add to projects file
        projects_data = self._load_projects()
        projects_data["projects"].append(asdict(project))
        self._save_projects(projects_data)
        
        logger.info(f"Created project: {name} ({project.id})")
        return project
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        projects_data = self._load_projects()
        
        for project_data in projects_data["projects"]:
            if project_data["id"] == project_id:
                # Convert state string back to enum
                project_data["state"] = ProjectState(project_data["state"])
                return Project(**project_data)
                
        return None
    
    def get_project_by_name(self, name: str) -> Optional[Project]:
        """Get project by name"""
        projects_data = self._load_projects()
        
        for project_data in projects_data["projects"]:
            if project_data["name"] == name:
                project_data["state"] = ProjectState(project_data["state"])
                return Project(**project_data)
                
        return None
    
    def update_project(self, project: Project):
        """Update existing project"""
        project.updated_at = datetime.now().isoformat()
        
        projects_data = self._load_projects()
        
        # Find and update project
        for i, p in enumerate(projects_data["projects"]):
            if p["id"] == project.id:
                projects_data["projects"][i] = asdict(project)
                break
        
        self._save_projects(projects_data)
        logger.info(f"Updated project: {project.name} ({project.id})")
    
    def list_projects(self, state: Optional[ProjectState] = None) -> List[Project]:
        """List all projects, optionally filtered by state"""
        projects_data = self._load_projects()
        projects = []
        
        for project_data in projects_data["projects"]:
            project_data["state"] = ProjectState(project_data["state"])
            project = Project(**project_data)
            
            if state is None or project.state == state:
                projects.append(project)
        
        # Sort by added_date (most recent first)
        projects.sort(key=lambda p: p.added_date, reverse=True)
        return projects
    
    def remove_project(self, project_id: str) -> bool:
        """Remove project from dashboard (does not delete repository)"""
        projects_data = self._load_projects()
        
        # Find and remove project
        original_count = len(projects_data["projects"])
        projects_data["projects"] = [
            p for p in projects_data["projects"] if p["id"] != project_id
        ]
        
        if len(projects_data["projects"]) < original_count:
            self._save_projects(projects_data)
            logger.info(f"Removed project from dashboard: {project_id}")
            return True
            
        return False


@architecture_decision(
    title="TektonCore Project Management Architecture",
    description="Orchestrates project lifecycle with git integration and name extraction",
    rationale="Provides unified interface for project operations while maintaining separation of concerns",
    alternatives_considered=["Direct registry access", "Service-oriented architecture", "Event-driven system"],
    impacts=["code_organization", "maintainability", "testing", "extensibility"]
)
@integration_point(
    title="Project Manager Integration Hub",
    target_component="multiple",
    protocol="direct_calls",
    data_flow="ProjectManager ↔ ProjectRegistry ↔ GitRemoteDetector ↔ ProjectNameExtractor",
    description="Central integration point for all project management operations"
)
class ProjectManager:
    """Enhanced project management with git integration"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize project manager"""
        self.registry = ProjectRegistry(storage_path)
        self.git_detector = GitRemoteDetector()
        self.github_validator = GitHubCLIValidator()
        self._tekton_self_check_done = False
        
        logger.info("Enhanced project manager initialized")
    
    async def _ensure_tekton_self_check(self):
        """Ensure Tekton self-check has run (call this from async methods)"""
        if not self._tekton_self_check_done:
            await self._check_tekton_self_management()
            self._tekton_self_check_done = True
    
    @api_contract(
        title="Tekton Self-Management Check",
        endpoint="_check_tekton_self_management",
        method="PRIVATE_ASYNC",
        request_schema={},
        response_schema={},
        description="Automatically registers Tekton as a self-managed project if conditions are met"
    )
    async def _check_tekton_self_management(self):
        """Check if Tekton should manage itself"""
        try:
            # Check if Tekton is already registered
            existing_tekton = self.registry.get_project_by_name("Tekton")
            if existing_tekton:
                return
            
            # Get Tekton root directory
            tekton_root = TektonEnviron.get("TEKTON_ROOT")
            if not tekton_root or not os.path.exists(tekton_root):
                return
            
            # Check if it's a git repository
            if not self.git_detector.is_git_repository(tekton_root):
                return
            
            # Detect git remotes
            remotes = await GitRemoteDetector.detect_remotes(tekton_root)
            
            # Create Tekton self-management project
            project = self.registry.create_project(
                name="Tekton",
                description="Tekton managing itself - the ultimate dogfooding",
                local_directory=tekton_root,
                forked_repository=remotes.origin,
                upstream_repository=remotes.upstream,
                companion_intelligence="gpt-oss:20b",
                is_tekton_self=True,
                metadata={
                    "auto_created": True,
                    "created_reason": "Self-management initialization"
                }
            )
            
            logger.info(f"Created Tekton self-management project: {project.id}")
            
        except Exception as e:
            logger.error(f"Failed to check Tekton self-management: {e}")
    
    @api_contract(
        title="GitHub Project Creation API",
        endpoint="create_project_from_github",
        method="ASYNC",
        request_schema={
            "github_url": "str",
            "local_directory": "str",
            "forked_repository": "Optional[str]",
            "upstream_repository": "Optional[str]",
            "companion_intelligence": "str",
            "description": "str"
        },
        response_schema={"project": "Project"},
        description="Creates new project with GitHub integration and automatic git remote detection"
    )
    async def create_project_from_github(
        self,
        github_url: str,
        local_directory: str,
        forked_repository: Optional[str] = None,
        upstream_repository: Optional[str] = None,
        companion_intelligence: str = "gpt-oss:20b",
        description: str = ""
    ) -> Project:
        """Create project from GitHub URL using GitHub CLI workflow"""
        
        # Ensure Tekton self-check has run
        await self._ensure_tekton_self_check()
        
        # Step 1: Validate GitHub CLI setup
        logger.info(f"[GIT] Validating GitHub CLI setup for project: {github_url}")
        is_valid, error_message = self.github_validator.validate_github_cli()
        if not is_valid:
            logger.error(f"[GIT] GitHub CLI validation failed: {error_message}")
            raise ValueError(error_message)
        logger.info("[GIT] GitHub CLI validation passed")
        
        # Extract project name to check for duplicates
        project_name = ProjectNameExtractor.extract_from_github_url(github_url)
        if not project_name:
            project_name = ProjectNameExtractor.extract_from_directory(local_directory)
        
        # Check if project already exists
        existing_project = self.registry.get_project_by_name(project_name)
        if existing_project:
            raise ValueError(f"Project '{project_name}' already exists in dashboard")
        
        # Fix local directory path: full resolved path to $TEKTON_ROOT/../project-name
        tekton_root = TektonEnviron.get("TEKTON_ROOT") or os.getcwd()
        tekton_parent = os.path.dirname(tekton_root)
        corrected_local_directory = os.path.abspath(os.path.join(tekton_parent, project_name))
        
        # Use corrected path if the provided one looks wrong
        if local_directory.endswith('.git') or '/github/' in local_directory or '$TEKTON_ROOT' in local_directory:
            local_directory = corrected_local_directory
            logger.info(f"Corrected local directory to: {local_directory}")
        
        # Step 2: Create fork using GitHub CLI
        try:
            fork_cmd = ["gh", "repo", "fork", github_url, "--clone=false"]
            logger.info(f"[GIT] Executing command: {' '.join(fork_cmd)}")
            logger.info(f"[GIT] Creating fork of {github_url}")
            
            result = subprocess.run(
                fork_cmd,
                capture_output=True,
                text=True,
                check=False  # Don't fail if fork already exists
            )
            
            logger.info(f"[GIT] Fork command completed with exit code: {result.returncode}")
            if result.stdout:
                logger.info(f"[GIT] Fork command stdout: {result.stdout}")
            if result.stderr:
                logger.info(f"[GIT] Fork command stderr: {result.stderr}")
            
            if result.returncode == 0:
                logger.info("[GIT] Fork created successfully")
            else:
                # Check if fork already exists
                if "already exists" in result.stderr.lower():
                    logger.info("[GIT] Fork already exists, continuing")
                else:
                    logger.warning(f"[GIT] Fork creation failed: {result.stderr}")
                    # Continue anyway - might be able to clone original
                    
        except subprocess.CalledProcessError as e:
            logger.warning(f"[GIT] Fork creation failed: {e.stderr}")
            # Continue anyway - might be able to clone original
        
        # Step 3: Clone the repository using GitHub CLI
        if not os.path.exists(local_directory):
            clone_cmd = ["gh", "repo", "clone", github_url, local_directory]
            logger.info(f"[GIT] Executing command: {' '.join(clone_cmd)}")
            logger.info(f"[GIT] Cloning repository to: {local_directory}")
            
            try:
                result = subprocess.run(
                    clone_cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                logger.info(f"[GIT] Clone command completed with exit code: {result.returncode}")
                if result.stdout:
                    logger.info(f"[GIT] Clone command stdout: {result.stdout}")
                if result.stderr:
                    logger.info(f"[GIT] Clone command stderr: {result.stderr}")
                    
                logger.info(f"[GIT] Successfully cloned {github_url} to {local_directory}")
                
            except subprocess.CalledProcessError as e:
                logger.error(f"[GIT] Clone command failed with exit code: {e.returncode}")
                if e.stdout:
                    logger.error(f"[GIT] Clone command stdout: {e.stdout}")
                if e.stderr:
                    logger.error(f"[GIT] Clone command stderr: {e.stderr}")
                logger.error(f"[GIT] Failed to clone repository: {e.stderr}")
                raise ValueError(f"Failed to clone repository: {e.stderr}")
        
        # Step 4: Auto-detect git remotes (GitHub CLI should set these up properly)
        if os.path.exists(local_directory) and self.git_detector.is_git_repository(local_directory):
            logger.info(f"[GIT] Detecting git remotes in: {local_directory}")
            remotes = await GitRemoteDetector.detect_remotes(local_directory)
            
            logger.info(f"[GIT] Detected remotes - origin: {remotes.origin}, upstream: {remotes.upstream}")
            
            # Use detected remotes if not provided
            if not forked_repository and remotes.origin:
                forked_repository = remotes.origin
                logger.info(f"[GIT] Using detected origin as forked repository: {forked_repository}")
            if not upstream_repository and remotes.upstream:
                upstream_repository = remotes.upstream
                logger.info(f"[GIT] Using detected upstream as upstream repository: {upstream_repository}")
        
        # Step 5: Create project
        project = self.registry.create_project(
            github_url=github_url,
            local_directory=local_directory,
            forked_repository=forked_repository,
            upstream_repository=upstream_repository,
            companion_intelligence=companion_intelligence,
            description=description
        )
        
        return project
    
    async def import_existing_project(self, local_directory: str, companion_intelligence: str = "gpt-oss:20b") -> Project:
        """Import an existing git project"""
        
        # Ensure Tekton self-check has run
        await self._ensure_tekton_self_check()
        
        if not self.git_detector.is_git_repository(local_directory):
            raise ValueError(f"Directory {local_directory} is not a git repository")
        
        # Detect remotes
        remotes = await GitRemoteDetector.detect_remotes(local_directory)
        
        # Determine primary GitHub URL
        github_url = remotes.origin or remotes.upstream
        if not github_url:
            raise ValueError(f"No git remotes found in {local_directory}")
        
        # Extract project name
        name = ProjectNameExtractor.extract_from_github_url(github_url)
        if not name:
            name = ProjectNameExtractor.extract_from_directory(local_directory)
        
        # Create project
        project = self.registry.create_project(
            name=name,
            description=f"Imported from existing repository: {name}",
            github_url=github_url,
            local_directory=local_directory,
            forked_repository=remotes.origin,
            upstream_repository=remotes.upstream,
            companion_intelligence=companion_intelligence,
            metadata={
                "imported": True,
                "import_date": datetime.now().isoformat()
            }
        )
        
        return project
    
    async def update_project_remotes(self, project_id: str) -> Project:
        """Update project with latest git remote information"""
        project = self.registry.get_project(project_id)
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        
        if not project.local_directory or not os.path.exists(project.local_directory):
            return project
        
        # Detect current remotes
        remotes = await GitRemoteDetector.detect_remotes(project.local_directory)
        
        # Update if changed
        updated = False
        if remotes.origin != project.forked_repository:
            project.forked_repository = remotes.origin
            updated = True
        if remotes.upstream != project.upstream_repository:
            project.upstream_repository = remotes.upstream
            updated = True
        
        if updated:
            self.registry.update_project(project)
            logger.info(f"Updated git remotes for project: {project.name}")
        
        return project
    
    async def get_project_with_status(self, project_id: str) -> Dict[str, Any]:
        """Get project with current git status"""
        project = self.registry.get_project(project_id)
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        
        # Get git status if directory exists
        git_status = {}
        if project.local_directory and os.path.exists(project.local_directory):
            try:
                # Check for uncommitted changes
                result = subprocess.run(
                    ["git", "-C", project.local_directory, "status", "--porcelain"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                git_status["has_changes"] = bool(result.stdout.strip())
                
                # Get current branch
                result = subprocess.run(
                    ["git", "-C", project.local_directory, "branch", "--show-current"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                git_status["current_branch"] = result.stdout.strip()
                
                # Check if ahead/behind
                if project.forked_repository:
                    result = subprocess.run(
                        ["git", "-C", project.local_directory, "rev-list", "--count", "--left-right", "HEAD...origin/main"],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    if result.returncode == 0:
                        parts = result.stdout.strip().split("\t")
                        if len(parts) == 2:
                            git_status["commits_ahead"] = int(parts[0])
                            git_status["commits_behind"] = int(parts[1])
                
            except Exception as e:
                logger.warning(f"Failed to get git status for {project.name}: {e}")
        
        return {
            "project": asdict(project),
            "git_status": git_status
        }
    
    async def launch_project_ci(self, project: Project) -> bool:
        """
        Launch AI specialist for a project CI if not already running.
        Uses the same infrastructure as Greek Chorus CIs but with dynamic ports.
        
        Args:
            project: Project to launch CI for
            
        Returns:
            True if CI is running (either launched or already running)
        """
        # Special case: Tekton project uses numa (always running)
        if project.name.lower() == "tekton":
            logger.info(f"Project {project.name} uses numa as its CI (always running)")
            return True
        
        # Check if CI is already registered and potentially running
        try:
            from shared.aish.src.registry.ci_registry import get_registry
            registry = get_registry()
            
            ci_name = f"{project.name.lower()}-ci"
            ci_info = registry.get_by_name(ci_name)
            
            if ci_info:
                # CI is registered, check if it's actually running
                port = ci_info.get('ai_port', ci_info.get('port', 0))
                if port:
                    # Try to connect to verify it's running
                    import socket
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(1)
                        sock.connect(('localhost', port))
                        sock.close()
                        logger.info(f"Project CI {ci_name} already running on port {port}")
                        return True
                    except (socket.error, socket.timeout):
                        logger.info(f"Project CI {ci_name} registered but not running, will launch")
        except ImportError:
            logger.error("CI Registry not available")
            return False
        
        # Launch the project CI using the same pattern as Greek Chorus
        try:
            import sys
            import subprocess
            
            # Get or allocate dynamic port for this project
            from shared.aish.src.registry.ci_registry import get_registry
            registry = get_registry()
            
            # Register the project CI if not already registered
            registry._register_project_ci({
                'id': project.id,
                'name': project.name,
                'companion_intelligence': project.companion_intelligence or 'gpt-oss:20b',
                'local_directory': project.local_directory
            })
            
            # Get the allocated port
            ci_info = registry.get_by_name(f"{project.name.lower()}-ci")
            if not ci_info:
                logger.error(f"Failed to register project CI for {project.name}")
                return False
            
            ai_port = ci_info.get('ai_port', ci_info.get('port', 0))
            if not ai_port:
                logger.error(f"No port allocated for project CI {project.name}")
                return False
            
            # Launch the AI specialist process
            # Use generic specialist which can be run as a module
            cmd = [
                sys.executable, '-m', 'shared.ai.generic_specialist',
                '--port', str(ai_port),
                '--component', project.name.lower(),
                '--ci-id', f"{project.name.lower()}-ci"
            ]
            
            logger.info(f"Launching project CI for {project.name} on port {ai_port}")
            logger.debug(f"Launch command: {' '.join(cmd)}")
            
            # Get Tekton root for environment
            tekton_root = TektonEnviron.get('TEKTON_ROOT', os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, 'PYTHONPATH': tekton_root}
            )
            
            logger.info(f"Project CI {project.name}-ci launched with PID {process.pid}")
            
            # Wait for CI to be ready (try connecting for up to 10 seconds)
            import time
            start_time = time.time()
            while time.time() - start_time < 10:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    sock.connect(('localhost', ai_port))
                    sock.close()
                    logger.info(f"Project CI {project.name}-ci is ready on port {ai_port}")
                    return True
                except (socket.error, socket.timeout):
                    await asyncio.sleep(0.5)
            
            logger.warning(f"Project CI {project.name}-ci launched but not responding after 10 seconds")
            return False
            
        except Exception as e:
            logger.error(f"Failed to launch project CI for {project.name}: {e}")
            return False
    
    async def ensure_project_cis_running(self, projects: Optional[List[Project]] = None):
        """
        Ensure CIs are running for all active projects.
        Called when projects are listed or accessed.
        
        Args:
            projects: Optional list of projects, if None will check all projects
        """
        if projects is None:
            projects = self.registry.list_projects()
        
        for project in projects:
            # Only launch CIs for projects with companion intelligence configured
            if project.companion_intelligence:
                try:
                    await self.launch_project_ci(project)
                except Exception as e:
                    logger.error(f"Failed to ensure CI for project {project.name}: {e}")
