#!/bin/bash
# Simple test wrapper for MCP debugging

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Debug logging to stderr (will appear in Claude Desktop logs)
echo "Test Wrapper: Starting..." >&2
echo "Test Wrapper: Script directory: $SCRIPT_DIR" >&2
echo "Test Wrapper: Arguments: $@" >&2

# Check if virtual environment exists
if [ ! -d "hexstrike-env" ]; then
    echo "ERROR: Virtual environment not found at $SCRIPT_DIR/hexstrike-env" >&2
    exit 1
fi

# Activate virtual environment
source hexstrike-env/bin/activate

# Verify we're using the right Python
echo "Test Wrapper: Using Python: $(which python3)" >&2

# Run the simple test script
exec python3 test_mcp_simple.py "$@"