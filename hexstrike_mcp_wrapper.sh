#!/bin/bash
# HexStrike MCP Wrapper Script
# This script activates the virtual environment and runs the MCP client

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Debug logging to stderr (will appear in Claude Desktop logs)
echo "HexStrike MCP Wrapper: Starting..." >&2
echo "Script directory: $SCRIPT_DIR" >&2
echo "Arguments: $@" >&2

# Check if virtual environment exists
if [ ! -d "hexstrike-env" ]; then
    echo "ERROR: Virtual environment not found at $SCRIPT_DIR/hexstrike-env" >&2
    exit 1
fi

# Activate virtual environment
source hexstrike-env/bin/activate

# Verify we're using the right Python
which python3 >&2

# Run the MCP client with all provided arguments
exec python3 hexstrike_mcp.py "$@"