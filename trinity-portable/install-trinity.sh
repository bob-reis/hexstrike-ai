#!/bin/bash
# Trinity Installer Script

echo "<­ Installing Trinity Pentest Orchestrator..."

# Install system dependencies
echo "=æ Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    python3 python3-pip python3-venv \
    git docker.io curl wget \
    nmap nuclei hydra metasploit-framework \
    build-essential

# Create workspace
echo "=Á Creating Trinity workspace..."
sudo mkdir -p /opt/trinity
cd /opt/trinity

# Clone repositories
echo "= Cloning repositories..."
git clone https://github.com/0x4m4/hexstrike-ai.git hexstrike-ai
git clone https://github.com/GreyDGL/PentestGPT.git PentestGPT
git clone https://github.com/Yenn503/villager-ai-hexstrike-integration.git villager-ai
git clone https://github.com/helviojunior/enumdns.git enumdns

# Setup components
echo "” Setting up HexStrike AI..."
cd hexstrike-ai && python3 -m venv hexstrike-env && cd ..

echo ">Ù Setting up PentestGPT..."
cd PentestGPT && python3 -m venv .pentestgpt-venv && cd ..

echo "<­ Setting up Villager AI..."
cd villager-ai && python3 -m venv villager-venv-new && cd ..

echo "= Setting up enumdns..."
cd enumdns && make && sudo make install && cd ..

# Copy Trinity orchestrator
sudo cp ../trinity-pentest-orchestrator.sh /opt/
sudo chmod +x /opt/trinity-pentest-orchestrator.sh

# Setup secrets
sudo mkdir -p /opt/trinity-secrets

echo " Trinity installation complete!"
echo "=€ Run: sudo /opt/trinity-pentest-orchestrator.sh start"
