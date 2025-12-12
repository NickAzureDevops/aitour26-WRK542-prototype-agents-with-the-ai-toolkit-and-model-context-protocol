#!/bin/bash
# Automated test script for MCP servers startup and health checks

set -e  # Exit on any error

echo "🧪 Starting MCP Server Automated Test"
echo "======================================"

# Cleanup function to ensure servers are stopped
cleanup() {
    echo ""
    echo "🧹 Cleaning up servers..."
    pkill -f "mcp_servers\.(finance|supplier|product)_server" 2>/dev/null || true
    sleep 2
    echo "✅ Cleanup complete"
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

# Check if ports are already in use
echo "1️⃣ Checking if ports are available..."
for port in 8001 8002 8003; do
    if lsof -i :$port >/dev/null 2>&1; then
        echo "❌ Port $port is already in use!"
        lsof -i :$port
        exit 1
    fi
done
echo "✅ All ports available"

# Set PYTHONPATH
export PYTHONPATH=/workspace/src:$PYTHONPATH

# Start Finance Server
echo ""
echo "2️⃣ Starting Finance Server (port 8001)..."
cd /workspace
python -m mcp_servers.finance_server &
FINANCE_PID=$!
echo "   PID: $FINANCE_PID"

# Start Supplier Server
echo ""
echo "3️⃣ Starting Supplier Server (port 8002)..."
python -m mcp_servers.supplier_server &
SUPPLIER_PID=$!
echo "   PID: $SUPPLIER_PID"

# Start Product Server
echo ""
echo "4️⃣ Starting Product Server (port 8003)..."
python -m mcp_servers.product_server &
PRODUCT_PID=$!
echo "   PID: $PRODUCT_PID"

# Wait for servers to start
echo ""
echo "⏳ Waiting for servers to start..."
sleep 5

# Check if processes are still running
echo ""
echo "5️⃣ Checking server processes..."
for pid in $FINANCE_PID $SUPPLIER_PID $PRODUCT_PID; do
    if ! ps -p $pid > /dev/null 2>&1; then
        echo "❌ Server process $pid died!"
        exit 1
    fi
done
echo "✅ All server processes running"

# Check ports are listening
echo ""
echo "6️⃣ Checking server ports..."
for port in 8001 8002 8003; do
    if ! lsof -i :$port >/dev/null 2>&1; then
        echo "❌ Port $port is not listening!"
        exit 1
    fi
    echo "✅ Port $port listening"
done

# Test health endpoints
echo ""
echo "7️⃣ Testing health endpoints..."
for port in 8001 8002 8003; do
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/health 2>/dev/null || echo "000")
    if [ "$response" == "200" ]; then
        echo "✅ Port $port health check: OK"
    else
        echo "❌ Port $port health check failed (HTTP $response)"
        exit 1
    fi
done

# Show server info
echo ""
echo "8️⃣ Server Information:"
echo "   Finance:  http://localhost:8001/mcp (PID: $FINANCE_PID)"
echo "   Supplier: http://localhost:8002/mcp (PID: $SUPPLIER_PID)"
echo "   Product:  http://localhost:8003/mcp (PID: $PRODUCT_PID)"

echo ""
echo "✅ All tests passed! Servers are running correctly."
echo ""
echo "Press Ctrl+C to stop all servers..."

# Keep script running until interrupted
wait
