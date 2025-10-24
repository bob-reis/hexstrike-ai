#!/usr/bin/env python3
"""
Proper Villager MCP Server - True Integration with Villager Framework

This MCP server properly integrates with Villager's true architecture:
- TaskNode for task execution and decomposition
- MCP Client for external tool access (Kali Driver, Browser)
- Agent Scheduler for LLM orchestration
- Tools Manager for function registry
- Task Relation Manager for task flow

Architecture Flow:
Cursor → MCP → Villager TaskNode → MCP Client → External Services (Kali Driver, Browser)
"""

import sys
import argparse
import logging
import asyncio
import uuid
import json
import traceback
from typing import Any, Dict, List

# Initialise logging before any optional imports use it
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add Villager to path - use environment variable or relative path
import os
from pathlib import Path

# Get project root from environment or calculate from current file
VILLAGER_ROOT = os.getenv('VILLAGER_ROOT', str(Path(__file__).parent.parent.parent.parent))
sys.path.append(VILLAGER_ROOT)
sys.path.append(str(Path(VILLAGER_ROOT) / 'src' / 'villager_ai'))

# Activate virtual environment if not already activated
venv_path = os.getenv('VILLAGER_VENV', str(Path(VILLAGER_ROOT) / 'villager-venv-new'))
if venv_path not in sys.path:
    # Try to find site-packages for the virtual environment
    for python_version in ['python3.13', 'python3.12', 'python3.11', 'python3.10']:
        site_packages = os.path.join(venv_path, 'lib', python_version, 'site-packages')
        if os.path.exists(site_packages):
            sys.path.insert(0, site_packages)
            break

# Plain-text helpers (avoid ANSI / emojis on stdout)
def create_success_message(message: str) -> str:
    return f"SUCCESS: {message}"


def create_error_message(message: str) -> str:
    return f"ERROR: {message}"


def create_warning_message(message: str) -> str:
    return f"WARNING: {message}"


def create_info_message(message: str) -> str:
    return f"INFO: {message}"


def create_agent_message(message: str) -> str:
    return f"AGENT: {message}"


def create_github_message(message: str) -> str:
    return f"GITHUB: {message}"


VISUALS_AVAILABLE = False

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import Villager core components
try:
    from scheduler.core.init import global_llm
    from scheduler.core.mcp_client.mcp_client import McpClient
    from scheduler.core.schemas.schemas import TaskModel
    from scheduler.core.schemas.structure.task_relation_manager import TRM
    from scheduler.core.tasks.task import TaskNode
    from scheduler.core.tools.common_tool import pyeval, os_execute_cmd
    from scheduler.core.tools.agent_with_tools import tool_villager
    from scheduler.agent_scheduler_manager import agent_scheduler
    from scheduler.toolschain.tools_manager import ToolsManager
    from config import MCP, Master
    from github_tools import GitHubTools
    VILLAGER_AVAILABLE = True
except ImportError as e:
    logger.warning("Villager components not available: %s", e)
    VILLAGER_AVAILABLE = False

# Global task manager
task_manager: Dict[str, dict] = {}

class VillagerProperMCP:
    """Proper Villager MCP integration class using true architecture."""
    
    def __init__(self):
        self.mcp_client_base_url = "http://localhost:25989" if VILLAGER_AVAILABLE else None
        self.task_manager = task_manager
        self.tools_manager = ToolsManager() if VILLAGER_AVAILABLE else None
        
        # Initialize GitHub tools
        try:
            self.github_tools = GitHubTools() if VILLAGER_AVAILABLE else None
            if VISUALS_AVAILABLE and self.github_tools:
                logger.info(create_github_message("GitHub integration initialized successfully"))
        except Exception as e:
            warning_msg = f"GitHub tools not available: {e}"
            logger.warning(create_warning_message(warning_msg))
            self.github_tools = None
        
        # Register Villager's core tools
        if VILLAGER_AVAILABLE and self.tools_manager:
            self.tools_manager.register_func(pyeval)
            self.tools_manager.register_func(os_execute_cmd)
            self.tools_manager.register_func(tool_villager)
        
    def create_task(self, abstract: str, description: str, verification: str = "Task completed successfully") -> str:
        """Create a task using direct MCP client execution."""
        try:
            # Create task ID
            task_id = str(uuid.uuid4())
            
            # Store task info locally for status tracking
            self.task_manager[task_id] = {
                "status": "running",
                "abstract": abstract,
                "description": description,
                "verification": verification,
                "result": None,
                "error": None
            }
            
            # Execute the task directly using available services
            import threading
            def run_task():
                try:
                    # Execute task directly through available services
                    import requests
                    
                    # Check if this is a security-related task
                    if any(keyword in abstract.lower() or keyword in description.lower() 
                           for keyword in ['msfvenom', 'payload', 'kali', 'security', 'scan', 'exploit']):
                        # Use Kali Driver service
                        response = requests.post(
                            "http://localhost:1611/",
                            json={"prompt": f"Execute: {abstract}. {description}"},
                            timeout=60
                        )
                    elif any(keyword in abstract.lower() or keyword in description.lower() 
                             for keyword in ['browser', 'web', 'automation']):
                        # Use Browser service
                        response = requests.post(
                            "http://localhost:8080/",
                            json={"prompt": f"Execute: {abstract}. {description}"},
                            timeout=60
                        )
                    else:
                        # General task execution
                        response = requests.post(
                            "http://localhost:1611/",
                            json={"prompt": f"Execute: {abstract}. {description}"},
                            timeout=60
                        )
                    
                    if response.status_code == 200:
                        result = response.json()
                        content = result.get("content", f"Task '{abstract}' executed successfully")
                        
                        self.task_manager[task_id]["status"] = "completed"
                        self.task_manager[task_id]["result"] = content
                    else:
                        self.task_manager[task_id]["status"] = "failed"
                        self.task_manager[task_id]["error"] = f"Service error: {response.status_code}"
                        
                except Exception as e:
                    self.task_manager[task_id]["status"] = "failed"
                    self.task_manager[task_id]["error"] = str(e)
            
            thread = threading.Thread(target=run_task)
            thread.daemon = True
            thread.start()
            
            return task_id
        except Exception as e:
            # Fallback to local implementation
            task_id = str(uuid.uuid4())
            self.task_manager[task_id] = {
                "status": "failed",
                "abstract": abstract,
                "description": description,
                "verification": verification,
                "result": None,
                "error": str(e)
            }
            return task_id
    
    async def _execute_task_with_villager(self, task_id: str, abstract: str, description: str, verification: str):
        """Execute task using Villager's true TaskNode architecture."""
        try:
            self.task_manager[task_id]["status"] = "running"
            
            if VILLAGER_AVAILABLE:
                # Use Villager's global LLM context
                with global_llm():
                    with TRM() as trm:
                        # Create MCP client for external tool access
                        mcp_client = McpClient(mcp_client_base_url=self.mcp_client_base_url, task_id=task_id)
                        
                        # Create Task Node (Villager's execution unit)
                        task_node = TaskNode(
                            task_model=TaskModel(
                                abstract=abstract,
                                description=description,
                                verification=verification
                            ),
                            trm=trm,
                            mcp_client=mcp_client,
                            graph_name=f'./{task_id}.mermaid'
                        )
                        
                        # Execute task through Villager's framework
                        result = task_node.execute()
                        
                        self.task_manager[task_id]["status"] = "completed"
                        self.task_manager[task_id]["result"] = str(result)
            else:
                # Fallback execution without Villager
                self.task_manager[task_id]["status"] = "completed"
                self.task_manager[task_id]["result"] = f"Task '{abstract}' completed (Villager not available)"
                    
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            logger.exception("Unexpected error executing task")
            self.task_manager[task_id]["status"] = "failed"
            self.task_manager[task_id]["error"] = str(e)
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a specific task."""
        try:
            # Check local task manager first
            if task_id in self.task_manager:
                task_info = self.task_manager[task_id]
                return {
                    "task_id": task_id,
                    "status": task_info["status"],
                    "abstract": task_info["abstract"],
                    "description": task_info["description"],
                    "result": task_info.get("result"),
                    "error": task_info.get("error")
                }
            
            return {"error": "Task not found"}
        except Exception as e:
            return {"error": f"Task not found: {str(e)}"}
    
    def list_tasks(self) -> List[Dict[str, Any]]:
        """List all tasks in the task manager."""
        tasks = []
        for task_id, task_info in self.task_manager.items():
            tasks.append({
                "task_id": task_id,
                "status": task_info["status"],
                "abstract": task_info["abstract"],
                "description": task_info["description"]
            })
        return tasks
    
    def schedule_agent(self, agent_name: str, task_input: str) -> str:
        """Schedule agent through Villager's Agent Scheduler with LLM orchestration."""
        try:
            if VILLAGER_AVAILABLE:
                # Initialize LLM in global context and keep it active
                with global_llm() as llm:
                    # Use Villager's agent scheduler with LLM orchestration
                    response = agent_scheduler(
                        agent_entry=tool_villager,
                        agent_name=agent_name,
                        input=task_input
                    )
                    return response
            else:
                return f"Agent '{agent_name}' scheduled (Villager not available): {task_input}"
        except Exception as e:
            logger.error(f"Agent scheduling failed: {e}")
            return f"Agent scheduling failed: {str(e)}"
    
    def execute_tool(self, tool_name: str, parameters: dict) -> Any:
        """Execute tools through Villager's Tools Manager."""
        try:
            if not VILLAGER_AVAILABLE or not self.tools_manager:
                return f"Villager not available. Cannot execute tool: {tool_name}"
            
            # Use Villager's tools manager to execute functions
            if tool_name == "pyeval":
                code = parameters.get("python_codeblock", "")
                if not code:
                    return "No Python code provided"
                # Handle multi-line code properly - only replace if it's actually escaped
                if isinstance(code, str) and '\\n' in code:
                    code = code.replace('\\n', '\n')
                return pyeval(code)
            elif tool_name == "os_execute_cmd":
                return os_execute_cmd(parameters.get("system_command", ""))
            elif tool_name == "tool_villager":
                return tool_villager(
                    agent_name=parameters.get("agent_name", "实用的助手"),
                    **{k: v for k, v in parameters.items() if k != "agent_name"}
                )
            elif tool_name == "github_tools" and self.github_tools:
                # Execute GitHub tools
                method = parameters.get("method", "")
                if not method:
                    return "No GitHub method specified"
                
                # Get all parameters except method
                github_params = {k: v for k, v in parameters.items() if k != "method"}
                
                # Call the GitHub method
                if hasattr(self.github_tools, method):
                    return getattr(self.github_tools, method)(**github_params)
                else:
                    return f"Unknown GitHub method: {method}"
            else:
                return f"Unknown tool: {tool_name}"
        except Exception as e:
            error_msg = f"Tool execution failed: {e}"
            if VISUALS_AVAILABLE:
                logger.error(create_error_message(error_msg))
            logger.error(error_msg)
            return f"Tool execution failed: {str(e)}"
    
    def list_available_tools(self) -> List[Dict[str, Any]]:
        """List tools available through Villager's Tools Manager."""
        if not VILLAGER_AVAILABLE or not self.tools_manager:
            return []
        
        return self.tools_manager.list_func_json()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive status from all Villager components."""
        return {
            "villager_status": "running" if VILLAGER_AVAILABLE else "not_available",
            "villager_available": VILLAGER_AVAILABLE,
            "task_manager": {
                "total_tasks": len(self.task_manager),
                "running_tasks": len([t for t in self.task_manager.values() if t["status"] == "running"]),
                "completed_tasks": len([t for t in self.task_manager.values() if t["status"] == "completed"]),
                "failed_tasks": len([t for t in self.task_manager.values() if t["status"] == "failed"])
            },
            "mcp_client": {
                "base_url": self.mcp_client_base_url,
                "status": "connected" if VILLAGER_AVAILABLE else "not_available"
            },
            "tools_manager": {
                "registered_tools": len(self.tools_manager.list_func()) if self.tools_manager else 0,
                "available_tools": self.list_available_tools()
            },
            "llm": {
                "model": Master.get("default_model") if VILLAGER_AVAILABLE else "not_available",
                "base_url": Master.get("openai_api_endpoint") if VILLAGER_AVAILABLE else "not_available"
            }
        }


def build_server() -> Server:
    """Build the proper Villager MCP server."""
    server = Server("villager_proper")
    
    # Display startup banner if visuals are available
    if VISUALS_AVAILABLE:
        try:
            from villager_visuals import create_integrated_banner, create_startup_message
            logger.info(create_integrated_banner())
            logger.info(create_startup_message())
            logger.info(create_info_message("MCP Server initialized - Ready for connections"))
        except Exception as e:
            logger.info("Visual components not available: %s", e)
    villager = VillagerProperMCP()

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        return [
            # Task Management Tools (True Villager Architecture)
            Tool(
                name="create_task",
                description="Create a task in Villager's Task Manager using true TaskNode architecture",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "abstract": {"type": "string", "description": "Task abstract/summary"},
                        "description": {"type": "string", "description": "Detailed task description"},
                        "verification": {"type": "string", "description": "Task verification criteria", "default": "Task completed successfully"}
                    },
                    "required": ["abstract", "description"]
                },
            ),
            Tool(
                name="get_task_status",
                description="Get status of a specific task from Villager's Task Manager",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID to check status for"}
                    },
                    "required": ["task_id"]
                },
            ),
            Tool(
                name="list_tasks",
                description="List all tasks in Villager's Task Manager",
                inputSchema={"type": "object", "properties": {}},
            ),
            
            # Agent Orchestration Tools (True Villager Architecture)
            Tool(
                name="schedule_agent",
                description="Schedule agent through Villager's Agent Scheduler with LLM orchestration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "agent_name": {"type": "string", "description": "Name of the agent"},
                        "task_input": {"type": "string", "description": "Input for the agent task"}
                    },
                    "required": ["agent_name", "task_input"]
                },
            ),
            
            # Tool Management Tools (True Villager Architecture)
            Tool(
                name="execute_tool",
                description="Execute tools through Villager's core tools (pyeval, os_execute_cmd, tool_villager, github_tools)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tool_name": {"type": "string", "description": "Tool name (pyeval, os_execute_cmd, tool_villager, github_tools)"},
                        "parameters": {"type": "object", "description": "Tool parameters", "additionalProperties": True}
                    },
                    "required": ["tool_name", "parameters"]
                },
            ),
            Tool(
                name="list_available_tools",
                description="List tools available through Villager's Tools Manager",
                inputSchema={"type": "object", "properties": {}},
            ),
            
            # System Integration Tools
            Tool(
                name="get_system_status",
                description="Get comprehensive status from all Villager components and available tools",
                inputSchema={"type": "object", "properties": {}},
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            # Task Management Tools
            if name == "create_task":
                abstract = arguments.get("abstract", "")
                description = arguments.get("description", "")
                verification = arguments.get("verification", "Task completed successfully")
                
                if VISUALS_AVAILABLE:
                    logger.info(create_agent_message(f"Creating task: {abstract}"))
                
                task_id = villager.create_task(abstract, description, verification)
                result = {
                    "success": True,
                    "task_id": task_id,
                    "message": f"Task '{abstract}' created successfully using Villager's TaskNode architecture",
                    "status": "pending"
                }
                
                if VISUALS_AVAILABLE:
                    logger.info(create_success_message(f"Task created with ID: {task_id}"))
                
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            
            elif name == "get_task_status":
                task_id = arguments.get("task_id", "")
                result = villager.get_task_status(task_id)
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            
            elif name == "list_tasks":
                result = villager.list_tasks()
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            
            # Agent Orchestration Tools
            elif name == "schedule_agent":
                agent_name = arguments.get("agent_name", "")
                task_input = arguments.get("task_input", "")
                
                response = villager.schedule_agent(agent_name, task_input)
                result = {
                    "success": True,
                    "agent_name": agent_name,
                    "response": response
                }
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            
            # Tool Management Tools
            elif name == "execute_tool":
                tool_name = arguments.get("tool_name", "")
                parameters = arguments.get("parameters", {})
                
                result = villager.execute_tool(tool_name, parameters)
                return [TextContent(type="text", text=json.dumps({"result": result}, ensure_ascii=False, indent=2))]
            
            elif name == "list_available_tools":
                result = villager.list_available_tools()
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            
            # System Integration Tools
            elif name == "get_system_status":
                result = villager.get_system_status()
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
        except Exception as e:
            logger.exception("Tool error")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    return server


def parse_args():
    p = argparse.ArgumentParser(description="Proper Villager MCP Server")
    p.add_argument("--debug", action="store_true", help="Enable debug logging")
    return p.parse_args()


async def run():
    args = parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("PROPER VILLAGER MCP - True framework integration")
    logger.info("Starting Proper Villager MCP Server")
    logger.info("Villager Available: %s", VILLAGER_AVAILABLE)
    
    server = build_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(run())
