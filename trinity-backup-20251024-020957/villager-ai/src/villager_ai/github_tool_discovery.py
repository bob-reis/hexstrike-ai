#!/usr/bin/env python3
"""
GitHub Tool Discovery and Installation System for Villager AI
Enables agents to discover, install, and integrate security tools from GitHub repositories
"""

import os
import subprocess
import json
import requests
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from github import Github, Auth
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubToolDiscovery:
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub Tool Discovery system."""
        self.token = token if token else os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN environment variable.")
        
        auth = Auth.Token(self.token)
        self.g = Github(auth=auth)

        # Tool installation directory - use environment variable or relative path
        villager_root = os.getenv('VILLAGER_ROOT', str(Path(__file__).parent.parent.parent))
        self.tools_dir = Path(villager_root) / "tools"
        self.tools_dir.mkdir(exist_ok=True)
        
        # Supported tool types and their installation patterns
        self.tool_patterns = {
            "python": {
                "files": ["requirements.txt", "setup.py", "pyproject.toml"],
                "install_cmd": "pip install -r requirements.txt",
                "run_patterns": ["*.py", "main.py", "tool.py"]
            },
            "go": {
                "files": ["go.mod", "main.go"],
                "install_cmd": "go build -o tool",
                "run_patterns": ["tool", "./tool"]
            },
            "rust": {
                "files": ["Cargo.toml"],
                "install_cmd": "cargo build --release",
                "run_patterns": ["target/release/*"]
            },
            "node": {
                "files": ["package.json"],
                "install_cmd": "npm install",
                "run_patterns": ["*.js", "index.js"]
            },
            "shell": {
                "files": ["*.sh", "install.sh"],
                "install_cmd": "chmod +x *.sh && ./install.sh",
                "run_patterns": ["*.sh"]
            },
            "binary": {
                "files": ["*.exe", "*.bin", "*.elf"],
                "install_cmd": "chmod +x *",
                "run_patterns": ["./*"]
            }
        }

    def search_security_tools(self, query: str, language: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """Search GitHub for security tools matching the query."""
        try:
            search_query = f"{query} security tool"
            if language:
                search_query += f" language:{language}"
            
            # Search repositories
            repos = self.g.search_repositories(
                search_query,
                sort="stars",
                order="desc"
            )
            
            tools = []
            for repo in repos[:limit]:
                tool_info = {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "url": repo.html_url,
                    "stars": repo.stargazers_count,
                    "language": repo.language,
                    "updated": repo.updated_at.isoformat(),
                    "clone_url": repo.clone_url,
                    "size": repo.size,
                    "topics": repo.get_topics()
                }
                tools.append(tool_info)
            
            logger.info(f"Found {len(tools)} security tools for query: {query}")
            return tools
            
        except Exception as e:
            logger.error(f"Error searching for tools: {e}")
            return []

    def analyze_tool_type(self, repo_name: str) -> Dict[str, Any]:
        """Analyze a repository to determine its tool type and installation method."""
        try:
            repo = self.g.get_repo(repo_name)
            
            # Get repository contents
            contents = repo.get_contents("")
            
            analysis = {
                "repo_name": repo_name,
                "tool_type": "unknown",
                "install_method": "manual",
                "run_command": "",
                "dependencies": [],
                "files_found": [],
                "confidence": 0
            }
            
            # Check for tool type indicators
            for content in contents:
                if content.type == "file":
                    filename = content.name.lower()
                    analysis["files_found"].append(filename)
                    
                    # Check against tool patterns
                    for tool_type, pattern in self.tool_patterns.items():
                        if any(pattern_file in filename for pattern_file in pattern["files"]):
                            analysis["tool_type"] = tool_type
                            analysis["install_method"] = pattern["install_cmd"]
                            analysis["confidence"] += 0.3
                            
                            # Try to find run command
                            if pattern["run_patterns"]:
                                analysis["run_command"] = pattern["run_patterns"][0]
            
            # Check README for installation instructions
            try:
                readme = repo.get_contents("README.md")
                readme_content = readme.decoded_content.decode()
                
                # Look for common installation patterns
                if "pip install" in readme_content.lower():
                    analysis["tool_type"] = "python"
                    analysis["install_method"] = "pip install"
                    analysis["confidence"] += 0.2
                elif "go build" in readme_content.lower():
                    analysis["tool_type"] = "go"
                    analysis["install_method"] = "go build"
                    analysis["confidence"] += 0.2
                elif "cargo build" in readme_content.lower():
                    analysis["tool_type"] = "rust"
                    analysis["install_method"] = "cargo build"
                    analysis["confidence"] += 0.2
                    
            except:
                pass
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing tool {repo_name}: {e}")
            return {"repo_name": repo_name, "error": str(e)}

    def install_tool(self, repo_name: str, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """Install a tool from GitHub repository."""
        try:
            repo = self.g.get_repo(repo_name)
            
            # Create tool directory
            tool_name = tool_name or repo.name
            tool_dir = self.tools_dir / tool_name
            tool_dir.mkdir(exist_ok=True)
            
            # Clone repository
            clone_url = repo.clone_url.replace("https://", f"https://{self.token}@")
            clone_result = subprocess.run(
                ["git", "clone", clone_url, str(tool_dir)],
                capture_output=True,
                text=True
            )
            
            if clone_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Failed to clone repository: {clone_result.stderr}",
                    "tool_name": tool_name
                }
            
            # Analyze and install
            analysis = self.analyze_tool_type(repo_name)
            
            # Try to install based on tool type
            install_success = False
            install_output = ""
            
            if analysis["tool_type"] != "unknown":
                try:
                    # Change to tool directory
                    os.chdir(tool_dir)
                    
                    # Run installation command
                    install_cmd = analysis["install_method"]
                    if install_cmd and install_cmd != "manual":
                        install_result = subprocess.run(
                            install_cmd.split(),
                            capture_output=True,
                            text=True,
                            timeout=300  # 5 minute timeout
                        )
                        install_success = install_result.returncode == 0
                        install_output = install_result.stdout + install_result.stderr
                    
                except subprocess.TimeoutExpired:
                    install_output = "Installation timed out"
                except Exception as e:
                    install_output = f"Installation error: {e}"
            
            # Create tool metadata
            tool_metadata = {
                "name": tool_name,
                "repo_name": repo_name,
                "repo_url": repo.html_url,
                "tool_type": analysis["tool_type"],
                "install_method": analysis["install_method"],
                "run_command": analysis["run_command"],
                "install_success": install_success,
                "install_output": install_output,
                "installed_at": subprocess.run(["date", "-Iseconds"], capture_output=True, text=True).stdout.strip(),
                "tool_path": str(tool_dir)
            }
            
            # Save metadata
            metadata_file = tool_dir / "tool_metadata.json"
            with open(metadata_file, "w") as f:
                json.dump(tool_metadata, f, indent=2)
            
            logger.info(f"Tool {tool_name} installed successfully")
            return {
                "success": True,
                "tool_name": tool_name,
                "metadata": tool_metadata
            }
            
        except Exception as e:
            logger.error(f"Error installing tool {repo_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name or repo_name
            }

    def list_installed_tools(self) -> List[Dict[str, Any]]:
        """List all installed tools."""
        tools = []
        
        for tool_dir in self.tools_dir.iterdir():
            if tool_dir.is_dir():
                metadata_file = tool_dir / "tool_metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, "r") as f:
                            metadata = json.load(f)
                        tools.append(metadata)
                    except:
                        # Create basic metadata for tools without metadata
                        tools.append({
                            "name": tool_dir.name,
                            "tool_type": "unknown",
                            "tool_path": str(tool_dir)
                        })
        
        return tools

    def run_tool(self, tool_name: str, args: List[str] = None) -> Dict[str, Any]:
        """Run an installed tool with given arguments."""
        try:
            tool_dir = self.tools_dir / tool_name
            if not tool_dir.exists():
                return {
                    "success": False,
                    "error": f"Tool {tool_name} not found"
                }
            
            # Load tool metadata
            metadata_file = tool_dir / "tool_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
            else:
                metadata = {"run_command": f"./{tool_name}"}
            
            # Prepare command
            run_cmd = metadata.get("run_command", f"./{tool_name}")
            if args:
                run_cmd += " " + " ".join(args)
            
            # Change to tool directory and run
            os.chdir(tool_dir)
            result = subprocess.run(
                run_cmd.split(),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "command": run_cmd
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Tool execution timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def uninstall_tool(self, tool_name: str) -> Dict[str, Any]:
        """Uninstall a tool."""
        try:
            tool_dir = self.tools_dir / tool_name
            if not tool_dir.exists():
                return {
                    "success": False,
                    "error": f"Tool {tool_name} not found"
                }
            
            # Remove tool directory
            shutil.rmtree(tool_dir)
            
            logger.info(f"Tool {tool_name} uninstalled successfully")
            return {
                "success": True,
                "message": f"Tool {tool_name} uninstalled successfully"
            }
            
        except Exception as e:
            logger.error(f"Error uninstalling tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Example usage and testing
if __name__ == "__main__":
    # Test the GitHub Tool Discovery system
    try:
        discovery = GitHubToolDiscovery()
        
        print("🔍 Searching for security tools...")
        tools = discovery.search_security_tools("nmap", limit=5)
        
        print(f"\n📋 Found {len(tools)} tools:")
        for tool in tools:
            print(f"  • {tool['name']} - {tool['description']} ({tool['stars']} stars)")
        
        if tools:
            print(f"\n🔧 Analyzing first tool: {tools[0]['name']}")
            analysis = discovery.analyze_tool_type(tools[0]['full_name'])
            print(f"  Tool Type: {analysis['tool_type']}")
            print(f"  Install Method: {analysis['install_method']}")
            print(f"  Confidence: {analysis['confidence']}")
        
        print(f"\n📦 Installed tools:")
        installed = discovery.list_installed_tools()
        for tool in installed:
            print(f"  • {tool['name']} ({tool.get('tool_type', 'unknown')})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
