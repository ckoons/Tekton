#!/usr/bin/env python3
"""
GitHub API demonstration with PyGithub.

This is a simple script to demonstrate basic GitHub API functionality using PyGithub.
"""

import os
import json
import sys
from github import Github, GithubException
from dotenv import load_dotenv

def print_json(data):
    """Print JSON data in a formatted way"""
    if isinstance(data, str):
        try:
            # Try to parse as JSON
            parsed = json.loads(data)
            print(json.dumps(parsed, indent=2))
            return
        except:
            pass
    print(json.dumps(data, indent=2, default=str))

def main():
    """Main function to demonstrate GitHub API interactions."""
    # Load environment variables
    load_dotenv()
    
    # Get GitHub API token from environment
    github_token = os.getenv("GITHUB_API_TOKEN")
    if not github_token:
        print("Error: GitHub API token not found. Please set the GITHUB_API_TOKEN environment variable.")
        return
    
    # Initialize PyGithub client
    g = Github(github_token)
    
    try:
        # Get the authenticated user
        user = g.get_user()
        print(f"Authenticated as: {user.login}")
        
        # Check command line arguments for demo actions
        if len(sys.argv) < 2:
            print("\nAvailable demos:")
            print("  repos    - List your repositories")
            print("  events   - Show recent events")
            print("  info     - Show user information")
            print("  stars    - List starred repositories")
            print("  notifs   - List notifications")
            print("  orgs     - List organizations")
            return
        
        demo_type = sys.argv[1]
        
        if demo_type == "repos":
            # List repositories
            print("\nYour repositories:")
            repos = []
            for repo in user.get_repos(sort="updated"):
                repos.append({
                    "name": repo.name,
                    "url": repo.html_url,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "private": repo.private,
                    "updated": repo.updated_at.isoformat() if repo.updated_at else None
                })
            print_json(repos)
            
        elif demo_type == "events":
            # List recent activity
            print("\nRecent events:")
            events = []
            for event in user.get_events()[:10]:
                event_data = {
                    "type": event.type,
                    "created_at": event.created_at.isoformat() if event.created_at else None,
                    "repo": event.repo.name if event.repo else None
                }
                events.append(event_data)
            print_json(events)
            
        elif demo_type == "info":
            # Show user information
            print("\nUser information:")
            user_data = {
                "login": user.login,
                "name": user.name,
                "email": user.email,
                "company": user.company,
                "bio": user.bio,
                "location": user.location,
                "public_repos": user.public_repos,
                "followers": user.followers,
                "following": user.following,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            print_json(user_data)
            
        elif demo_type == "stars":
            # List starred repositories
            print("\nStarred repositories:")
            stars = []
            for repo in user.get_starred()[:10]:
                stars.append({
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "url": repo.html_url,
                    "stars": repo.stargazers_count,
                    "language": repo.language
                })
            print_json(stars)
            
        elif demo_type == "notifs":
            # List notifications
            print("\nNotifications:")
            notifs = []
            for notif in g.get_user().get_notifications():
                notifs.append({
                    "reason": notif.reason,
                    "subject": notif.subject.title,
                    "repository": notif.repository.full_name,
                    "updated_at": notif.updated_at.isoformat() if notif.updated_at else None
                })
            if notifs:
                print_json(notifs)
            else:
                print("No notifications found.")
                
        elif demo_type == "orgs":
            # List organizations
            print("\nOrganizations:")
            orgs = []
            for org in user.get_orgs():
                orgs.append({
                    "login": org.login,
                    "name": org.name,
                    "url": org.html_url,
                    "description": org.description
                })
            if orgs:
                print_json(orgs)
            else:
                print("No organizations found.")
        else:
            print(f"Unknown demo type: {demo_type}")
            
    except GithubException as e:
        print(f"GitHub API Error: {e.status} - {e.data.get('message')}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()