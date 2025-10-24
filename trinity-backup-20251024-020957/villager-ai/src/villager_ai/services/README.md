# Villager AI Services

This directory contains all the core services that make up the Villager AI framework.

## 🏗️ Service Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Cursor MCP    │───▶│  Villager MCP    │───▶│ Villager Server │
│                 │    │  (villager_proper│    │   (port 37695)  │
│                 │    │   _mcp.py)       │    │                 │
└─────────────────┘    └──────────────────┘    └─────────┬───────┘
                                                         │
                                                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Kali Driver   │◀───│   MCP Client     │◀───│   TaskNode      │
│   (port 1611)   │    │   (port 25989)   │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📁 Service Files

### 1. **villager_server_simple.py** (Port 37695)
- **Purpose**: Main Villager server providing task management endpoints
- **Endpoints**:
  - `POST /task` - Create new tasks
  - `GET /get/task/status` - Get task status
  - `GET /health` - Health check
- **Integration**: Connects to MCP Client for task execution

### 2. **mcp_service.py** (Port 25989)
- **Purpose**: MCP Client service that handles streaming responses
- **Functionality**:
  - Forwards requests to Kali Driver and Browser services
  - Handles streaming JSON responses
  - Properly escapes JSON content for Villager compatibility
- **Integration**: Bridge between Villager Server and external services

### 3. **kali_driver_service.py** (Port 1611)
- **Purpose**: Security tools execution service
- **Functionality**:
  - Executes msfvenom commands
  - Handles security tool execution
  - Returns structured responses
- **Integration**: Receives requests from MCP Client

### 4. **browser_service.py** (Port 8080)
- **Purpose**: Browser automation service
- **Functionality**:
  - Web automation capabilities
  - Browser interaction tasks
  - Ready for future expansion
- **Integration**: Receives requests from MCP Client

## 🚀 Starting Services

### Automatic Startup
```bash
# Navigate to your Villager-AI installation directory
cd /path/to/Villager-AI
./start_villager_proper.sh
```

### Manual Startup
```bash
# Start MCP Client
python services/mcp_service.py &

# Start Kali Driver
python services/kali_driver_service.py &

# Start Browser Service
python services/browser_service.py &

# Start Villager Server
python services/villager_server_simple.py &
```

## 🔧 Service Configuration

### Port Configuration
- **Villager Server**: 37695
- **MCP Client**: 25989
- **Kali Driver**: 1611
- **Browser Service**: 8080

### Health Checks
All services provide health check endpoints:
```bash
curl http://localhost:37695/health  # Villager Server
curl http://localhost:25989/health  # MCP Client
curl http://localhost:1611/health   # Kali Driver
curl http://localhost:8080/health   # Browser Service
```

## 📊 Logs

Service logs are stored in the `../logs/` directory:
- `villager_server.log` - Villager Server logs
- `mcp_client.log` - MCP Client logs
- `kali_driver.log` - Kali Driver logs
- `browser_automation.log` - Browser Service logs

## 🔄 Service Communication

### Task Flow
1. **Cursor MCP** → **Villager MCP** → **Villager Server**
2. **Villager Server** → **MCP Client** → **Kali Driver/Browser**
3. **Response** flows back through the same path

### Request Format
```json
{
  "prompt": "Execute: task description",
  "mcp_servers": {
    "kali_driver": "http://localhost:1611",
    "browser_use": "http://localhost:8080"
  }
}
```

### Response Format
```json
{
  "content": "Task execution result",
  "new_msg": true
}
```

## 🛠️ Development

### Adding New Services
1. Create new service file in this directory
2. Update `start_villager_proper.sh` to include new service
3. Add health check endpoint
4. Update MCP Client to handle new service type
5. Test integration with complete workflow

### Service Dependencies
- All services require Python 3.13+
- FastAPI for HTTP endpoints
- Requests for inter-service communication
- Villager virtual environment activation

## ✅ Status

All services are **FULLY OPERATIONAL** and integrated with the Villager AI framework. The complete workflow from Cursor MCP to payload generation is working perfectly.
