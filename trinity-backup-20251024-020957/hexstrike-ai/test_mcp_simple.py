#!/usr/bin/env python3
"""
Simple MCP test script to debug Claude Desktop connection issues
"""

import sys
import json

# Debug output to stderr (will appear in Claude Desktop logs)
print("Simple MCP Test: Starting...", file=sys.stderr)
print(f"Simple MCP Test: Python path: {sys.executable}", file=sys.stderr)
print(f"Simple MCP Test: Arguments: {sys.argv}", file=sys.stderr)

try:
    from mcp.server.fastmcp import FastMCP
    print("Simple MCP Test: FastMCP imported successfully", file=sys.stderr)

    # Create minimal MCP server
    mcp = FastMCP("test-mcp")

    @mcp.tool()
    def hello_world() -> str:
        """Simple test tool"""
        return "Hello from HexStrike!"

    print("Simple MCP Test: Starting MCP server...", file=sys.stderr)
    mcp.run()
    print("Simple MCP Test: MCP server finished", file=sys.stderr)

except ImportError as e:
    print(f"Simple MCP Test: Import error: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Simple MCP Test: General error: {e}", file=sys.stderr)
    import traceback
    print(f"Simple MCP Test: Traceback: {traceback.format_exc()}", file=sys.stderr)
    sys.exit(1)