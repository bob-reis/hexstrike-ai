#!/usr/bin/env python3
"""
GitHub Tools for Villager AI Agents
===================================

This module provides GitHub integration tools that Villager agents can use
to interact with GitHub repositories, issues, pull requests, and more.

Security Note: All GitHub operations require proper authentication tokens
which should be stored securely in environment variables.
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import base64


class GitHubTools:
    """GitHub integration tools for Villager AI agents."""
    
    def __init__(self, token: Optional[str] = None, base_url: str = "https://api.github.com"):
        """
        Initialize GitHub tools.
        
        Args:
            token: GitHub personal access token or GitHub App token
            base_url: GitHub API base URL (default: https://api.github.com)
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'token {self.token}' if self.token else None,
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Villager-AI-GitHub-Tools/1.0'
        }
        
        if not self.token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN environment variable or pass token parameter.")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to GitHub API."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data, timeout=30)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=self.headers, json=data, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            return {"error": f"GitHub API request failed: {str(e)}"}
    
    # Repository Management
    def get_repository(self, owner: str, repo: str) -> Dict:
        """Get repository information."""
        return self._make_request('GET', f'/repos/{owner}/{repo}')
    
    def list_repositories(self, username: Optional[str] = None, org: Optional[str] = None) -> List[Dict]:
        """List repositories for a user or organization."""
        if org:
            endpoint = f'/orgs/{org}/repos'
        elif username:
            endpoint = f'/users/{username}/repos'
        else:
            endpoint = '/user/repos'
        
        result = self._make_request('GET', endpoint)
        return result if isinstance(result, list) else [result]
    
    def create_repository(self, name: str, description: str = "", private: bool = False, 
                         org: Optional[str] = None) -> Dict:
        """Create a new repository."""
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": True
        }
        
        if org:
            endpoint = f'/orgs/{org}/repos'
        else:
            endpoint = '/user/repos'
        
        return self._make_request('POST', endpoint, data)
    
    def fork_repository(self, owner: str, repo: str, org: Optional[str] = None) -> Dict:
        """Fork a repository."""
        data = {"organization": org} if org else {}
        return self._make_request('POST', f'/repos/{owner}/{repo}/forks', data)
    
    # File Operations
    def get_file_contents(self, owner: str, repo: str, path: str, branch: str = "main") -> Dict:
        """Get file contents from repository."""
        return self._make_request('GET', f'/repos/{owner}/{repo}/contents/{path}?ref={branch}')
    
    def create_or_update_file(self, owner: str, repo: str, path: str, content: str, 
                             message: str, branch: str = "main", sha: Optional[str] = None) -> Dict:
        """Create or update a file in repository."""
        # Encode content to base64
        content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        data = {
            "message": message,
            "content": content_b64,
            "branch": branch
        }
        
        if sha:
            data["sha"] = sha
        
        return self._make_request('PUT', f'/repos/{owner}/{repo}/contents/{path}', data)
    
    def delete_file(self, owner: str, repo: str, path: str, message: str, 
                   branch: str = "main", sha: str = None) -> Dict:
        """Delete a file from repository."""
        if not sha:
            # Get current file to get SHA
            file_info = self.get_file_contents(owner, repo, path, branch)
            if "error" in file_info:
                return file_info
            sha = file_info.get("sha")
        
        data = {
            "message": message,
            "sha": sha,
            "branch": branch
        }
        
        return self._make_request('DELETE', f'/repos/{owner}/{repo}/contents/{path}', data)
    
    # Issues Management
    def list_issues(self, owner: str, repo: str, state: str = "open", 
                   labels: Optional[List[str]] = None) -> List[Dict]:
        """List issues in a repository."""
        endpoint = f'/repos/{owner}/{repo}/issues?state={state}'
        if labels:
            endpoint += f'&labels={",".join(labels)}'
        
        result = self._make_request('GET', endpoint)
        return result if isinstance(result, list) else [result]
    
    def get_issue(self, owner: str, repo: str, issue_number: int) -> Dict:
        """Get a specific issue."""
        return self._make_request('GET', f'/repos/{owner}/{repo}/issues/{issue_number}')
    
    def create_issue(self, owner: str, repo: str, title: str, body: str = "", 
                    labels: Optional[List[str]] = None, assignees: Optional[List[str]] = None) -> Dict:
        """Create a new issue."""
        data = {
            "title": title,
            "body": body
        }
        
        if labels:
            data["labels"] = labels
        if assignees:
            data["assignees"] = assignees
        
        return self._make_request('POST', f'/repos/{owner}/{repo}/issues', data)
    
    def update_issue(self, owner: str, repo: str, issue_number: int, 
                    title: Optional[str] = None, body: Optional[str] = None,
                    state: Optional[str] = None, labels: Optional[List[str]] = None) -> Dict:
        """Update an issue."""
        data = {}
        if title is not None:
            data["title"] = title
        if body is not None:
            data["body"] = body
        if state is not None:
            data["state"] = state
        if labels is not None:
            data["labels"] = labels
        
        return self._make_request('PATCH', f'/repos/{owner}/{repo}/issues/{issue_number}', data)
    
    def add_issue_comment(self, owner: str, repo: str, issue_number: int, body: str) -> Dict:
        """Add a comment to an issue."""
        data = {"body": body}
        return self._make_request('POST', f'/repos/{owner}/{repo}/issues/{issue_number}/comments', data)
    
    # Pull Requests Management
    def list_pull_requests(self, owner: str, repo: str, state: str = "open") -> List[Dict]:
        """List pull requests in a repository."""
        result = self._make_request('GET', f'/repos/{owner}/{repo}/pulls?state={state}')
        return result if isinstance(result, list) else [result]
    
    def get_pull_request(self, owner: str, repo: str, pr_number: int) -> Dict:
        """Get a specific pull request."""
        return self._make_request('GET', f'/repos/{owner}/{repo}/pulls/{pr_number}')
    
    def create_pull_request(self, owner: str, repo: str, title: str, head: str, 
                           base: str, body: str = "") -> Dict:
        """Create a new pull request."""
        data = {
            "title": title,
            "head": head,
            "base": base,
            "body": body
        }
        
        return self._make_request('POST', f'/repos/{owner}/{repo}/pulls', data)
    
    def merge_pull_request(self, owner: str, repo: str, pr_number: int, 
                          merge_method: str = "merge", commit_title: Optional[str] = None) -> Dict:
        """Merge a pull request."""
        data = {"merge_method": merge_method}
        if commit_title:
            data["commit_title"] = commit_title
        
        return self._make_request('PUT', f'/repos/{owner}/{repo}/pulls/{pr_number}/merge', data)
    
    # Branch Management
    def list_branches(self, owner: str, repo: str) -> List[Dict]:
        """List branches in a repository."""
        result = self._make_request('GET', f'/repos/{owner}/{repo}/branches')
        return result if isinstance(result, list) else [result]
    
    def create_branch(self, owner: str, repo: str, branch_name: str, 
                     from_branch: str = "main") -> Dict:
        """Create a new branch."""
        # Get SHA of the source branch
        source_branch = self._make_request('GET', f'/repos/{owner}/{repo}/git/refs/heads/{from_branch}')
        if "error" in source_branch:
            return source_branch
        
        sha = source_branch["object"]["sha"]
        
        data = {
            "ref": f"refs/heads/{branch_name}",
            "sha": sha
        }
        
        return self._make_request('POST', f'/repos/{owner}/{repo}/git/refs', data)
    
    def delete_branch(self, owner: str, repo: str, branch_name: str) -> Dict:
        """Delete a branch."""
        return self._make_request('DELETE', f'/repos/{owner}/{repo}/git/refs/heads/{branch_name}')
    
    # Releases Management
    def list_releases(self, owner: str, repo: str) -> List[Dict]:
        """List releases in a repository."""
        result = self._make_request('GET', f'/repos/{owner}/{repo}/releases')
        return result if isinstance(result, list) else [result]
    
    def create_release(self, owner: str, repo: str, tag_name: str, name: str, 
                      body: str = "", draft: bool = False, prerelease: bool = False) -> Dict:
        """Create a new release."""
        data = {
            "tag_name": tag_name,
            "name": name,
            "body": body,
            "draft": draft,
            "prerelease": prerelease
        }
        
        return self._make_request('POST', f'/repos/{owner}/{repo}/releases', data)
    
    # Webhooks Management
    def list_webhooks(self, owner: str, repo: str) -> List[Dict]:
        """List webhooks for a repository."""
        result = self._make_request('GET', f'/repos/{owner}/{repo}/hooks')
        return result if isinstance(result, list) else [result]
    
    def create_webhook(self, owner: str, repo: str, url: str, events: List[str], 
                      secret: Optional[str] = None) -> Dict:
        """Create a webhook for a repository."""
        data = {
            "config": {
                "url": url,
                "content_type": "json"
            },
            "events": events
        }
        
        if secret:
            data["config"]["secret"] = secret
        
        return self._make_request('POST', f'/repos/{owner}/{repo}/hooks', data)
    
    # Search
    def search_repositories(self, query: str, sort: str = "stars", order: str = "desc") -> Dict:
        """Search repositories."""
        endpoint = f'/search/repositories?q={query}&sort={sort}&order={order}'
        return self._make_request('GET', endpoint)
    
    def search_issues(self, query: str, sort: str = "created", order: str = "desc") -> Dict:
        """Search issues and pull requests."""
        endpoint = f'/search/issues?q={query}&sort={sort}&order={order}'
        return self._make_request('GET', endpoint)
    
    def search_code(self, query: str, sort: str = "indexed", order: str = "desc") -> Dict:
        """Search code."""
        endpoint = f'/search/code?q={query}&sort={sort}&order={order}'
        return self._make_request('GET', endpoint)


# Convenience functions for Villager agents
def github_get_repo(owner: str, repo: str) -> Dict:
    """Get repository information."""
    tools = GitHubTools()
    return tools.get_repository(owner, repo)


def github_list_issues(owner: str, repo: str, state: str = "open") -> List[Dict]:
    """List issues in a repository."""
    tools = GitHubTools()
    return tools.list_issues(owner, repo, state)


def github_create_issue(owner: str, repo: str, title: str, body: str = "") -> Dict:
    """Create a new issue."""
    tools = GitHubTools()
    return tools.create_issue(owner, repo, title, body)


def github_create_pr(owner: str, repo: str, title: str, head: str, base: str, body: str = "") -> Dict:
    """Create a new pull request."""
    tools = GitHubTools()
    return tools.create_pull_request(owner, repo, title, head, base, body)


def github_get_file(owner: str, repo: str, path: str, branch: str = "main") -> Dict:
    """Get file contents from repository."""
    tools = GitHubTools()
    return tools.get_file_contents(owner, repo, path, branch)


def github_update_file(owner: str, repo: str, path: str, content: str, message: str, branch: str = "main") -> Dict:
    """Create or update a file in repository."""
    tools = GitHubTools()
    return tools.create_or_update_file(owner, repo, path, content, message, branch)


def github_search_repos(query: str) -> Dict:
    """Search repositories."""
    tools = GitHubTools()
    return tools.search_repositories(query)


def github_search_issues(query: str) -> Dict:
    """Search issues and pull requests."""
    tools = GitHubTools()
    return tools.search_issues(query)


def github_search_code(query: str) -> Dict:
    """Search code."""
    tools = GitHubTools()
    return tools.search_code(query)


# Example usage for Villager agents
if __name__ == "__main__":
    # Example: Get repository information
    try:
        repo_info = github_get_repo("microsoft", "vscode")
        print(f"Repository: {repo_info.get('name', 'Unknown')}")
        print(f"Description: {repo_info.get('description', 'No description')}")
        print(f"Stars: {repo_info.get('stargazers_count', 0)}")
    except Exception as e:
        print(f"Error: {e}")
