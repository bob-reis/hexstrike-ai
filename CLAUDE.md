# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HexStrike AI is an advanced penetration testing MCP (Model Context Protocol) framework that provides AI agents with access to 150+ security tools through a FastMCP server architecture. This is a defensive security platform designed for authorized penetration testing, bug bounty research, and cybersecurity education.

**⚠️ IMPORTANT**: This codebase is for legitimate cybersecurity research and authorized penetration testing only. All testing should be conducted on owned systems or with explicit written authorization.

## Architecture

The system uses a two-component architecture:

1. **hexstrike_server.py** - Flask-based API server that manages security tools and AI agents
2. **hexstrike_mcp.py** - FastMCP client that provides AI agents with tool access via MCP protocol

Communication flow: AI Agent → MCP Client → Flask API Server → Security Tools

## Development Commands

### Server Management
```bash
# Start the main server (required first)
python3 hexstrike_server.py

# Start with debug logging
python3 hexstrike_server.py --debug

# Custom port (default: 8888)
python3 hexstrike_server.py --port 9000

# Check server health
curl http://localhost:8888/health
```

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv hexstrike-env
source hexstrike-env/bin/activate  # Linux/Mac
# hexstrike-env\Scripts\activate   # Windows

# Install Python dependencies
pip3 install -r requirements.txt

# Verify installation
python3 -c "import mcp.server.fastmcp; print('FastMCP OK')"
```

### Testing and Validation
```bash
# Test API endpoints
curl -X POST http://localhost:8888/api/intelligence/analyze-target \
  -H "Content-Type: application/json" \
  -d '{"target": "example.com", "analysis_type": "basic"}'

# Check process status
curl http://localhost:8888/api/processes/list

# View telemetry
curl http://localhost:8888/api/telemetry
```

## Code Architecture

### Core Components

**Server (hexstrike_server.py)**:
- `ModernVisualEngine` - Handles colored output and visual formatting
- `IntelligentDecisionEngine` - AI-powered tool selection and parameter optimization
- `BugBountyWorkflowManager` - Manages bug bounty hunting workflows
- `CVEIntelligenceManager` - Vulnerability intelligence and exploit analysis
- `BrowserAgent` - Headless Chrome automation for web testing
- `AdvancedProcessManager` - Process execution and monitoring
- `SmartCacheSystem` - LRU caching with intelligent invalidation

**MCP Client (hexstrike_mcp.py)**:
- `FastMCP` integration for tool registration
- `ColoredFormatter` for consistent logging
- Tool execution wrappers for 150+ security tools
- Error handling and recovery mechanisms

### Key Patterns

1. **Tool Integration**: Security tools are wrapped in Python functions that handle parameter optimization, output parsing, and error recovery
2. **AI Decision Making**: The `IntelligentDecisionEngine` uses context analysis to select optimal tools and parameters
3. **Visual Consistency**: All output uses the `ModernVisualEngine` with a consistent red/hacker theme color palette
4. **Caching Strategy**: Results are cached using tool signature hashing to avoid redundant operations
5. **Process Management**: Long-running tools are managed through the `AdvancedProcessManager` with timeout and recovery

### Security Considerations

- All tool execution is sandboxed through subprocess management
- Input validation is performed on all API endpoints
- Process monitoring prevents resource exhaustion
- Error messages are sanitized to prevent information disclosure
- Caching system respects security context boundaries

## External Dependencies

The platform integrates with 150+ external security tools that must be installed separately:

**Critical Tools** (verify installation):
- nmap, gobuster, nuclei, sqlmap (web testing)
- hydra, john, hashcat (password attacks)
- ghidra, radare2, gdb (binary analysis)
- Chrome/Chromium with ChromeDriver (browser automation)

**Tool Verification**:
```bash
# Check core tools
which nmap gobuster nuclei sqlmap hydra

# Verify browser automation
google-chrome --version
chromedriver --version
```

## Configuration Files

- `requirements.txt` - Python dependencies with version pinning
- `hexstrike-ai-mcp.json` - MCP server configuration template
- `hexstrike.log` - Runtime logging (auto-created)
- `~/.config/Claude/claude_desktop_config.json` - Claude Desktop MCP configuration

### Claude Desktop Configuration

To connect Claude Desktop to HexStrike AI, configure the MCP server:

```json
{
  "mcpServers": {
    "hexstrike-ai": {
      "command": "/opt/hexstrike-ai/hexstrike-env/bin/python3",
      "args": [
        "/opt/hexstrike-ai/hexstrike_mcp.py",
        "--server",
        "http://localhost:8888"
      ],
      "description": "HexStrike AI v6.0 - Advanced Cybersecurity Automation Platform",
      "timeout": 300,
      "disabled": false
    }
  }
}
```

**Important**: Must use the Python executable from the virtual environment (`hexstrike-env/bin/python3`) to ensure all MCP dependencies are available.

## API Integration

The server exposes REST endpoints for:
- `/health` - Health checks and tool availability
- `/api/command` - Direct tool execution with caching
- `/api/intelligence/*` - AI-powered analysis and optimization
- `/api/processes/*` - Process management and monitoring

## Development Guidelines

When working with this codebase:

1. **Always start the server first** before testing MCP client functionality
2. **Use the color system** (`HexStrikeColors`) for consistent terminal output
3. **Follow the caching pattern** when adding new tools (use tool signature hashing)
4. **Implement proper error handling** with the established recovery mechanisms
5. **Test tool availability** before execution (tools may not be installed)
6. **Respect rate limiting** built into the intelligent decision engine
7. **Maintain visual consistency** using the `ModernVisualEngine` formatting

## Common Issues

### MCP Connection Issues

**Problem**: `Server transport closed unexpectedly` or `ModuleNotFoundError: No module named 'mcp'`

**Solution**: Use the wrapper script approach:

1. Ensure the wrapper script is executable:
   ```bash
   chmod +x /opt/hexstrike-ai/hexstrike_mcp_wrapper.sh
   ```

2. Update Claude Desktop configuration to use the wrapper:
   ```json
   {
     "mcpServers": {
       "hexstrike-ai": {
         "command": "/opt/hexstrike-ai/hexstrike_mcp_wrapper.sh",
         "args": ["--server", "http://localhost:8888"],
         "description": "HexStrike AI v6.0 - Advanced Cybersecurity Automation Platform",
         "timeout": 300,
         "disabled": false
       }
     }
   }
   ```

3. Restart Claude Desktop completely (quit and reopen)

**Other Common Issues**:
- **Tool Not Found**: Verify external security tools are installed and in PATH
- **Permission Denied**: Check file permissions and virtual environment activation
- **Browser Agent Fails**: Ensure Chrome/Chromium and ChromeDriver are properly installed
- **Server Not Running**: Ensure `python3 hexstrike_server.py` is running on port 8888

## Legal Notice

This platform is designed exclusively for authorized security testing. Users must:
- Obtain explicit written authorization before testing any systems
- Comply with all applicable laws and regulations
- Use only for legitimate security research, bug bounty programs, or CTF competitions
- Never use for malicious activities or unauthorized access attempts