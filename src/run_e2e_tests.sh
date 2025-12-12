#!/bin/bash
# Test runner script for MCP servers

cd /workspace/src
export PYTHONPATH=/workspace/src:$PYTHONPATH

echo "Running E2E tests..."
python tests/test_e2e_mcp.py 2>&1 | grep -v "Exception closing connection" | grep -v "CancelledError" | grep -v "do_close" | grep -v "dbapi_connection.close" | grep -v "sqlalchemy"

echo ""
echo "Tests completed!"
