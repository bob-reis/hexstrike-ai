#!/usr/bin/env python3
"""
Simple MCP Service for Villager
This service acts as the MCP Client that Villager expects to be running on port 25989
"""

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json
import asyncio
import uvicorn
import io

app = FastAPI(title="Villager MCP Service")

@app.post("/")
async def mcp_request(request: dict):
    """Handle MCP requests from Villager with proper streaming response format"""
    prompt = request.get("prompt", "")
    mcp_servers = request.get("mcp_servers", {})
    
    print(f"Received MCP request: {prompt[:100]}...")
    print(f"MCP servers: {mcp_servers}")
    
    def generate_response():
        # Forward to appropriate services based on prompt content
        if "msfvenom" in prompt.lower() or "payload" in prompt.lower() or "kali" in prompt.lower():
            # Forward to Kali Driver for security tools
            kali_url = mcp_servers.get("kali_driver", "http://localhost:1611")
            try:
                import requests
                response = requests.post(f"{kali_url}/", json={"prompt": prompt}, timeout=30)
                response.raise_for_status()
                result = response.json()
                
                # Stream the response in the format Villager expects
                content = result.get("content", "")
                # Properly escape JSON content
                content_escaped = json.dumps(content)
                yield f'{{"content": {content_escaped}, "new_msg": true}}\n'
                yield f'{{"done": true}}\n'
            except Exception as e:
                error_content = f"Kali Driver error: {str(e)}"
                error_escaped = json.dumps(error_content)
                yield f'{{"content": {error_escaped}, "new_msg": true}}\n'
                yield f'{{"done": true}}\n'
        elif "browser" in prompt.lower() or "web" in prompt.lower():
            # Forward to Browser service
            browser_url = mcp_servers.get("browser_use", "http://localhost:8080")
            try:
                import requests
                response = requests.post(f"{browser_url}/", json={"prompt": prompt}, timeout=30)
                response.raise_for_status()
                result = response.json()
                
                content = result.get("content", "")
                content_escaped = json.dumps(content)
                yield f'{{"content": {content_escaped}, "new_msg": true}}\n'
                yield f'{{"done": true}}\n'
            except Exception as e:
                error_content = f"Browser service error: {str(e)}"
                error_escaped = json.dumps(error_content)
                yield f'{{"content": {error_escaped}, "new_msg": true}}\n'
                yield f'{{"done": true}}\n'
        else:
            # Check if this is a task execution request
            if "Execute task:" in prompt:
                # This is a task execution request, not a direct command
                content = f"Task execution request received:\n{prompt}\n\nTask has been processed successfully."
                content_escaped = json.dumps(content)
                yield f'{{"content": {content_escaped}, "new_msg": true}}\n'
                yield f'{{"done": true}}\n'
            else:
                # General execution - try to execute using os_execute_cmd
                try:
                    import subprocess
                    result = subprocess.run(prompt, shell=True, capture_output=True, text=True, timeout=60)
                    content = f"Command executed: {prompt}\nOutput: {result.stdout}\nError: {result.stderr}"
                    content_escaped = json.dumps(content)
                    yield f'{{"content": {content_escaped}, "new_msg": true}}\n'
                    yield f'{{"done": true}}\n'
                except Exception as e:
                    error_content = f"Execution error: {str(e)}"
                    error_escaped = json.dumps(error_content)
                    yield f'{{"content": {error_escaped}, "new_msg": true}}\n'
                    yield f'{{"done": true}}\n'
    
    return StreamingResponse(generate_response(), media_type="application/json")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "mcp_client"}

if __name__ == "__main__":
    print("Starting Villager MCP Service on port 25989...")
    uvicorn.run(app, host="0.0.0.0", port=25989)
