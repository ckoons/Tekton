#!/usr/bin/env python3
"""
Simple GitHub agent that can be used directly or from Ergon.
"""

import os
import json
import argparse
from typing import Dict, Any, List, Optional
import logging
from github import Github, GithubException, BadCredentialsException, UnknownObjectException
from dotenv import load_dotenv

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# Initialize GitHub client
def init_github_client(token=None):
    """Initialize GitHub client with token."""
    # Use provided token or get from environment
    token = token or os.getenv("GITHUB_API_TOKEN")
    if not token:
        raise ValueError("GitHub API token not found. Please set the GITHUB_API_TOKEN environment variable.")
    return Github(token)

def list_repositories(visibility: str = "all", sort: str = "updated") -> str:
    """
    List repositories for the authenticated user.
    
    Args:
        visibility: Filter repositories by visibility (all, public, private)
        sort: Sort repositories by field (created, updated, pushed, full_name)
        
    Returns:
        JSON string with list of repositories
    """
    try:
        g = init_github_client()
        user = g.get_user()
        
        # Get repositories
        repos = user.get_repos(visibility=visibility, sort=sort)
        
        # Convert to list
        repo_list = []
        for repo in repos:
            repo_list.append({
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "url": repo.html_url,
                "private": repo.private,
                "language": repo.language,
                "pushed_at": repo.pushed_at.isoformat() if repo.pushed_at else None
            })
        
        return json.dumps({
            "status": "success",
            "count": len(repo_list),
            "repositories": repo_list
        }, indent=2)
    
    except BadCredentialsException:
        return json.dumps({"status": "error", "message": "Invalid GitHub credentials"})
    except Exception as e:
        logger.error(f"Error listing repositories: {str(e)}")
        return json.dumps({"status": "error", "message": f"Error listing repositories: {str(e)}"})

def create_repository(
    name: str,
    description: Optional[str] = None,
    private: bool = False,
    auto_init: bool = True
) -> str:
    """
    Create a new GitHub repository.
    
    Args:
        name: Name of the repository
        description: Optional description of the repository
        private: Whether the repository is private
        auto_init: Initialize repository with README
        
    Returns:
        JSON string with repository details or error
    """
    try:
        g = init_github_client()
        user = g.get_user()
        
        # Create repository
        repo = user.create_repo(
            name=name,
            description=description,
            private=private,
            auto_init=auto_init
        )
        
        # Return repo details
        return json.dumps({
            "status": "success",
            "message": f"Repository {repo.name} created successfully",
            "repository": {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "url": repo.html_url,
                "private": repo.private,
                "clone_url": repo.clone_url
            }
        }, indent=2)
    
    except BadCredentialsException:
        return json.dumps({"status": "error", "message": "Invalid GitHub credentials"})
    except GithubException as e:
        logger.error(f"GitHub error creating repository: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"GitHub error creating repository: {e.data.get('message', str(e))}"
        })
    except Exception as e:
        logger.error(f"Error creating repository: {str(e)}")
        return json.dumps({"status": "error", "message": f"Error creating repository: {str(e)}"})

def delete_repository(repo_name: str) -> str:
    """
    Delete a GitHub repository.
    
    Args:
        repo_name: Full name of the repository (username/repo) or just repo name
        
    Returns:
        JSON string with success or error message
    """
    try:
        g = init_github_client()
        user = g.get_user()
        
        # Check if repo_name includes username
        if '/' in repo_name:
            username, repo = repo_name.split('/')
            if username != user.login:
                return json.dumps({
                    "status": "error",
                    "message": f"You can only delete your own repositories. Got {username} but authenticated as {user.login}"
                })
            repo_name = repo
        
        # Get repository
        repo = user.get_repo(repo_name)
        
        # Return confirmation request
        repo_info = {
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "url": repo.html_url
        }
        
        # Check if force flag is present
        if repo_name.endswith("--force"):
            # Remove force flag and delete
            clean_name = repo_name.replace("--force", "").strip()
            repo = user.get_repo(clean_name)
            repo.delete()
            return json.dumps({"status": "success", "message": f"Repository {clean_name} deleted successfully"})
        else:
            return json.dumps({
                "status": "warning",
                "message": f"Repository {repo_name} found. To confirm deletion, add --force to the repo name or use --confirm.",
                "repository": repo_info
            })
    
    except UnknownObjectException:
        return json.dumps({"status": "error", "message": f"Repository {repo_name} not found"})
    except BadCredentialsException:
        return json.dumps({"status": "error", "message": "Invalid GitHub credentials"})
    except GithubException as e:
        logger.error(f"GitHub error deleting repository: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"GitHub error deleting repository: {e.data.get('message', str(e))}"
        })
    except Exception as e:
        logger.error(f"Error deleting repository: {str(e)}")
        return json.dumps({"status": "error", "message": f"Error deleting repository: {str(e)}"})

def get_repository(repo_name: str) -> str:
    """
    Get details of a GitHub repository.
    
    Args:
        repo_name: Full name of the repository (username/repo) or just repo name
        
    Returns:
        JSON string with repository details or error
    """
    try:
        g = init_github_client()
        user = g.get_user()
        
        # Check if repo_name includes username
        if '/' not in repo_name:
            repo_name = f"{user.login}/{repo_name}"
        
        # Get repository
        repo = g.get_repo(repo_name)
        
        # Return repo details
        return json.dumps({
            "status": "success",
            "repository": {
                "name": repo.name,
                "full_name": repo.full_name,
                "owner": repo.owner.login,
                "description": repo.description,
                "url": repo.html_url,
                "private": repo.private,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "open_issues": repo.open_issues_count,
                "clone_url": repo.clone_url
            }
        }, indent=2)
    
    except UnknownObjectException:
        return json.dumps({"status": "error", "message": f"Repository {repo_name} not found"})
    except BadCredentialsException:
        return json.dumps({"status": "error", "message": "Invalid GitHub credentials"})
    except Exception as e:
        logger.error(f"Error getting repository: {str(e)}")
        return json.dumps({"status": "error", "message": f"Error getting repository: {str(e)}"})

def process_request(request: str) -> str:
    """
    Process a GitHub request and route it to the appropriate function.
    
    Args:
        request: The user's request string
        
    Returns:
        Response from the GitHub API or error message
    """
    request = request.lower().strip()
    
    try:
        # List repositories
        if any(phrase in request for phrase in ["list repositories", "list repos", "show repositories", "show repos"]):
            # Extract optional parameters
            visibility = "all"
            if "public" in request:
                visibility = "public"
            elif "private" in request:
                visibility = "private"
                
            sort = "updated"
            if "created" in request:
                sort = "created"
            elif "pushed" in request:
                sort = "pushed"
            elif "name" in request:
                sort = "full_name"
                
            return list_repositories(visibility=visibility, sort=sort)
        
        # Create repository
        elif any(phrase in request for phrase in ["create repository", "create repo", "create a repository", "new repository"]):
            # Extract repository name
            name = None
            for phrase in ["named ", "called ", "name "]:
                if phrase in request:
                    parts = request.split(phrase, 1)
                    if len(parts) > 1:
                        name = parts[1].split()[0].strip()
                        name = name.strip('.,;:"\'()[]{}')
                        break
            
            if not name:
                return json.dumps({"status": "error", "message": "Repository name not specified"})
            
            # Extract description
            description = None
            if "description" in request:
                parts = request.split("description", 1)
                if len(parts) > 1:
                    description = parts[1].lstrip(": ").split(".")[0].strip()
            
            # Check if private
            private = "private" in request
            
            return create_repository(
                name=name,
                description=description,
                private=private,
                auto_init=True
            )
        
        # Delete repository
        elif any(phrase in request for phrase in ["delete repository", "delete repo", "remove repository"]):
            # Extract repository name
            repo_name = None
            for phrase in ["named ", "called ", "name ", "repo "]:
                if phrase in request:
                    parts = request.split(phrase, 1)
                    if len(parts) > 1:
                        repo_name = parts[1].split()[0].strip()
                        repo_name = repo_name.strip('.,;:"\'()[]{}')
                        break
            
            if not repo_name:
                return json.dumps({"status": "error", "message": "Repository name not specified"})
            
            # Check for force flag
            if "force" in request or "confirm" in request or "yes" in request:
                repo_name = f"{repo_name}--force"
                
            return delete_repository(repo_name=repo_name)
        
        # Get repository
        elif any(phrase in request for phrase in ["get repository", "get repo", "show repository", "repository details"]):
            # Get the repository name
            repo_name = None
            for phrase in ["named ", "called ", "name ", "repo "]:
                if phrase in request:
                    parts = request.split(phrase, 1)
                    if len(parts) > 1:
                        repo_name = parts[1].split()[0].strip()
                        repo_name = repo_name.strip('.,;:"\'()[]{}')
                        break
            
            if not repo_name:
                # Try to get the last word as repo name
                words = request.split()
                if words:
                    repo_name = words[-1].strip('.,;:"\'()[]{}')
            
            if not repo_name or repo_name in ["repository", "repo", "details"]:
                return json.dumps({"status": "error", "message": "Repository name not specified"})
                
            return get_repository(repo_name=repo_name)
        
        # Unknown request
        else:
            return json.dumps({
                "status": "error",
                "message": "Unknown GitHub request. Try: list repositories, create repository, delete repository, get repository"
            })
            
    except Exception as e:
        logger.error(f"Error processing GitHub request: {str(e)}")
        return json.dumps({"status": "error", "message": f"Error processing request: {str(e)}"})

def main():
    """Main function to run the GitHub agent."""
    # Load environment variables
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="GitHub Agent")
    parser.add_argument("request", nargs="?", help="Request to send to the GitHub agent")
    parser.add_argument("--list", action="store_true", help="List your repositories")
    parser.add_argument("--get", metavar="REPO", help="Get details of a repository")
    parser.add_argument("--create", metavar="NAME", help="Create a new repository")
    parser.add_argument("--delete", metavar="REPO", help="Delete a repository")
    parser.add_argument("--confirm", action="store_true", help="Confirm deletion without prompting")
    parser.add_argument("--private", action="store_true", help="Make repository private (with --create)")
    parser.add_argument("--description", metavar="DESC", help="Repository description (with --create)")
    
    args = parser.parse_args()
    
    try:
        # Command-line flags take precedence over natural language request
        if args.list:
            print(list_repositories())
        elif args.get:
            print(get_repository(args.get))
        elif args.create:
            print(create_repository(
                name=args.create,
                description=args.description,
                private=args.private
            ))
        elif args.delete:
            if args.confirm:
                # Add force flag
                delete_name = f"{args.delete}--force"
            else:
                delete_name = args.delete
            print(delete_repository(delete_name))
        elif args.request:
            # Process natural language request
            print(process_request(args.request))
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()