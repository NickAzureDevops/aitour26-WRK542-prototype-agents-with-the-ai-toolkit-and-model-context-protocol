#!/usr/bin/env python3
"""
End-to-end tests for all MCP servers using FastMCP client.
Tests Inventory and Sales Analysis servers.
"""

import asyncio
import sys
import warnings

from fastmcp.client import Client

from mcp_servers.inventory_server import mcp as inventory_mcp
from mcp_servers.sales_analysis import mcp as sales_analysis_mcp

# Suppress CancelledError warnings during cleanup
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*was never awaited.*")


async def test_inventory_server():
    """Test Inventory MCP server."""
    print("\n🧪 Testing Inventory MCP Server...")

    async with Client(inventory_mcp) as client:
        # Test get_stock_level_by_product_id
        result = await client.call_tool(name="get_stock_level_by_product_id", arguments={"product_id": 1})
        assert result.data is not None
        print("  ✅ get_stock_level_by_product_id tool")

        # Test transfer_stock (small test transfer)
        result = await client.call_tool(
            name="transfer_stock", arguments={"from_store_id": 1, "to_store_id": 2, "product_id": 1, "quantity": 1}
        )
        assert result.data is not None
        print("  ✅ transfer_stock tool")


async def test_sales_analysis_server():
    """Test Sales Analysis MCP server."""
    print("\n🧪 Testing Sales Analysis MCP Server...")

    async with Client(sales_analysis_mcp) as client:
        # Test get_database_schema
        result = await client.call_tool(name="get_database_schema", arguments={})
        assert result.data is not None
        print("  ✅ get_database_schema tool")

        # Test semantic_search_products
        result = await client.call_tool(
            name="semantic_search_products", arguments={"query_description": "cordless drill battery", "limit": 5}
        )
        assert result.data is not None
        print("  ✅ semantic_search_products tool")

        # Test execute_sales_query
        result = await client.call_tool(
            name="execute_sales_query", arguments={"sql_query": "SELECT store_name FROM stores LIMIT 5"}
        )
        assert result.data is not None
        print("  ✅ execute_sales_query tool")

        # Test get_current_utc_date
        result = await client.call_tool(name="get_current_utc_date", arguments={})
        assert result.data is not None
        print("  ✅ get_current_utc_date tool")


async def main():
    """Run all E2E tests."""
    print("=" * 70)
    print("🚀 E2E Tests for All MCP Servers (using FastMCP Client)")
    print("=" * 70)

    success = False
    try:
        await test_inventory_server()
        await test_sales_analysis_server()

        print("\n" + "=" * 70)
        print("✅ ALL E2E TESTS PASSED!")
        print("\nTested MCP Servers:")
        print("  • Inventory Server: 2 tools tested")
        print("  • Sales Analysis Server: 4 tools tested")
        print("\nAll servers working correctly with Zava Retail database!")
        print("=" * 70)
        success = True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()

    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
