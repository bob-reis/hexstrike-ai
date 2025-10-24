#!/usr/bin/env python3
"""
Browser Automation Service for Villager
This service handles browser automation requests on port 8080
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Villager Browser Automation Service")

@app.post("/")
async def browser_request(request: dict):
    """Handle Browser automation requests"""
    prompt = request.get("prompt", "")
    
    print(f"Browser service received request: {prompt[:100]}...")
    
    response = {
        "content": f"Browser automation processed: {prompt[:50]}...",
        "done": True
    }
    
    return response

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "browser_automation"}

if __name__ == "__main__":
    print("Starting Villager Browser Automation Service on port 8080...")
    uvicorn.run(app, host="0.0.0.0", port=8080)
