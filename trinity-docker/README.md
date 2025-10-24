# =3 Trinity Pentest Orchestrator - Docker

Containerized version of Trinity Pentest Orchestrator

## Quick Start

1. **Build the image:**
   ```bash
   ./build.sh
   ```

2. **Setup secrets:**
   ```bash
   cp trinity-secrets/.env.template trinity-secrets/.env
   # Edit trinity-secrets/.env with your API keys
   ```

3. **Start Trinity:**
   ```bash
   ./run.sh
   ```

4. **Access Trinity:**
   - HexStrike: http://localhost:8888
   - Villager: http://localhost:37695

5. **Stop Trinity:**
   ```bash
   ./stop.sh
   ```

## Ports
- 8888: HexStrike AI Server
- 37695: Villager AI Server
- 25989: MCP Client
- 1611: Kali Driver
- 8080: Browser Agent

## Volumes
- `trinity-secrets/`: API keys and configuration
- `workspace/`: Trinity workspace
- `logs/`: Trinity logs

## Requirements
- Docker
- Docker Compose
- 8GB+ RAM
- 50GB+ storage
