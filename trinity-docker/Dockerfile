FROM kalilinux/kali-rolling:latest

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV TRINITY_WORKSPACE=/opt/trinity

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    git docker.io curl wget \
    nmap nuclei hydra metasploit-framework \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create Trinity workspace
WORKDIR $TRINITY_WORKSPACE

# Clone repositories (using latest versions)
RUN git clone https://github.com/0x4m4/hexstrike-ai.git hexstrike-ai && \
    git clone https://github.com/GreyDGL/PentestGPT.git PentestGPT && \
    git clone https://github.com/Yenn503/villager-ai-hexstrike-integration.git villager-ai && \
    git clone https://github.com/helviojunior/enumdns.git enumdns

# Setup HexStrike
RUN cd hexstrike-ai && \
    python3 -m venv hexstrike-env && \
    . hexstrike-env/bin/activate && \
    pip install -r requirements.txt

# Setup PentestGPT
RUN cd PentestGPT && \
    python3 -m venv .pentestgpt-venv && \
    . .pentestgpt-venv/bin/activate && \
    pip install -e .

# Setup Villager AI
RUN cd villager-ai && \
    python3 -m venv villager-venv-new && \
    . villager-venv-new/bin/activate && \
    pip install -r requirements.txt || true

# Setup enumdns
RUN cd enumdns && \
    make && \
    make install

# Copy Trinity orchestrator (will be mounted)
COPY trinity-pentest-orchestrator.sh /opt/
RUN chmod +x /opt/trinity-pentest-orchestrator.sh

# Create secrets directory
RUN mkdir -p /opt/trinity-secrets

# Expose Trinity ports
EXPOSE 8888 37695 25989 1611 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8888/health || exit 1

# Start Trinity
CMD ["/opt/trinity-pentest-orchestrator.sh", "start"]
