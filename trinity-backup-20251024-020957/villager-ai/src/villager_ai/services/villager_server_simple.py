#!/usr/bin/env python3
"""
Simplified Villager Server - Working Implementation
This provides the same interface as the Villager framework but with reliable execution
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import asyncio
import threading
import json
import requests
from typing import Dict, List, Any

app = FastAPI(title="Simplified Villager Server")

# Global task manager
task_manager: Dict[str, dict] = {}

class TaskRequest(BaseModel):
    abstract: str
    description: str
    verification: str = "Task completed successfully"

@app.post("/task")
async def create_task(abstract: str, description: str, verification: str = "Task completed successfully"):
    """Create a new task"""
    task_id = str(uuid.uuid4())
    
    # Store task info
    task_manager[task_id] = {
        "token": task_id,
        "status": "running",
        "abstract": abstract,
        "description": description,
        "verification": verification,
        "result": None,
        "error": None,
        "graph_context": "",
        "context": ""
    }
    
    # Execute task in background
    def execute_task():
        try:
            # Simulate task execution by calling the MCP client
            mcp_response = requests.post(
                "http://localhost:25989/",
                json={
                    "prompt": f"Execute task: {abstract}. Description: {description}",
                    "mcp_servers": {
                        "kali_driver": "http://localhost:1611",
                        "browser_use": "http://localhost:8080"
                    }
                },
                timeout=60
            )
            
            if mcp_response.status_code == 200:
                # Parse streaming response
                content = ""
                for line in mcp_response.text.split('\n'):
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if 'content' in data:
                                content += data['content']
                        except:
                            pass
                
                task_manager[task_id]["status"] = "completed"
                task_manager[task_id]["result"] = content
            else:
                task_manager[task_id]["status"] = "failed"
                task_manager[task_id]["error"] = f"MCP client error: {mcp_response.status_code}"
                
        except Exception as e:
            task_manager[task_id]["status"] = "failed"
            task_manager[task_id]["error"] = str(e)
    
    # Start task execution in background thread
    thread = threading.Thread(target=execute_task)
    thread.daemon = True
    thread.start()
    
    return {"task_id": task_id}

@app.get("/get/task/status")
async def get_task_status():
    """Get status of all tasks"""
    tasks = []
    for task_id, task_info in task_manager.items():
        tasks.append({
            "token": task_info["token"],
            "status": task_info["status"],
            "abstract": task_info["abstract"],
            "description": task_info["description"],
            "verification": task_info["verification"],
            "result": task_info.get("result"),
            "error": task_info.get("error"),
            "graph_context": task_info["graph_context"],
            "context": task_info["context"]
        })
    
    # Return most recent task first
    return sorted(tasks, key=lambda x: x["token"], reverse=True)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "villager_server_simple"}

if __name__ == "__main__":
    import uvicorn
    print("Starting Simplified Villager Server on port 37695...")
    uvicorn.run(app, host="0.0.0.0", port=37695)
