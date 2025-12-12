#!/usr/bin/env python3
"""
Test script to verify MCP servers running via HTTP transport.
Uses the MCP client library to connect and test tools.
"""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client


async def test_finance_server():
    """Test Finance MCP server via HTTP."""
    print("=" * 80)
    print("Testing Finance MCP Server (http://localhost:8001/mcp)")
    print("=" * 80)

    server_url = "http://localhost:8001/mcp"

    async with sse_client(server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            tools_response = await session.list_tools()
            print(f"\n✅ Connected! Found {len(tools_response.tools)} tools:")
            for tool in tools_response.tools:
                print(f"   - {tool.name}")

            # Test get_stores
            print("\n📋 Testing get_stores()...")
            result = await session.call_tool("get_stores", arguments={"store_name": ""})
            stores_data = result.content[0].text
            print(f"✅ get_stores() - Retrieved data (first 200 chars): {stores_data[:200]}...")

            # Test get_historical_sales_data
            print("\n📊 Testing get_historical_sales_data()...")
            result = await session.call_tool(
                "get_historical_sales_data", arguments={"days_back": 30, "store_id": 1, "category_name": "POWER TOOLS"}
            )
            sales_data = result.content[0].text
            print(f"✅ get_historical_sales_data() - Retrieved data (first 200 chars): {sales_data[:200]}...")

            # Test get_current_inventory_status
            print("\n📦 Testing get_current_inventory_status()...")
            result = await session.call_tool(
                "get_current_inventory_status",
                arguments={"store_id": 1, "category_name": "HARDWARE", "low_stock_threshold": 10},
            )
            inventory_data = result.content[0].text
            print(f"✅ get_current_inventory_status() - Retrieved data (first 200 chars): {inventory_data[:200]}...")

            print("\n" + "=" * 80)
            print("✅ Finance MCP Server: All tests passed!")
            print("=" * 80)


async def test_supplier_server():
    """Test Supplier MCP server via HTTP."""
    print("\n" + "=" * 80)
    print("Testing Supplier MCP Server (http://localhost:8002/mcp)")
    print("=" * 80)

    server_url = "http://localhost:8002/mcp"

    async with sse_client(server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            tools_response = await session.list_tools()
            print(f"\n✅ Connected! Found {len(tools_response.tools)} tools:")
            for tool in tools_response.tools:
                print(f"   - {tool.name}")

            # Test find_suppliers_for_request
            print("\n🔍 Testing find_suppliers_for_request()...")
            result = await session.call_tool(
                "find_suppliers_for_request",
                arguments={
                    "product_category": "POWER TOOLS",
                    "esg_required": False,
                    "min_rating": 3.0,
                    "max_lead_time": 30,
                    "limit": 5,
                },
            )
            suppliers_data = result.content[0].text
            print(f"✅ find_suppliers_for_request() - Retrieved data (first 200 chars): {suppliers_data[:200]}...")

            # Test get_supplier_history_and_performance
            print("\n📈 Testing get_supplier_history_and_performance()...")
            result = await session.call_tool(
                "get_supplier_history_and_performance", arguments={"supplier_id": 1, "months_back": 12}
            )
            history_data = result.content[0].text
            print(
                f"✅ get_supplier_history_and_performance() - Retrieved data (first 200 chars): {history_data[:200]}..."
            )

            # Test get_supplier_contract
            print("\n📄 Testing get_supplier_contract()...")
            result = await session.call_tool("get_supplier_contract", arguments={"supplier_id": 1})
            contract_data = result.content[0].text
            print(f"✅ get_supplier_contract() - Retrieved data (first 200 chars): {contract_data[:200]}...")

            # Test get_company_supplier_policy
            print("\n📋 Testing get_company_supplier_policy()...")
            result = await session.call_tool(
                "get_company_supplier_policy", arguments={"policy_type": "procurement", "department": ""}
            )
            policy_data = result.content[0].text
            print(f"✅ get_company_supplier_policy() - Retrieved data (first 200 chars): {policy_data[:200]}...")

            print("\n" + "=" * 80)
            print("✅ Supplier MCP Server: All tests passed!")
            print("=" * 80)


async def test_sales_analysis_server():
    """Test Sales Analysis MCP server via HTTP."""
    print("\n" + "=" * 80)
    print("Testing Sales Analysis MCP Server (http://localhost:8000/mcp)")
    print("=" * 80)

    server_url = "http://localhost:8000/mcp"

    async with sse_client(server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            tools_response = await session.list_tools()
            print(f"\n✅ Connected! Found {len(tools_response.tools)} tools:")
            for tool in tools_response.tools:
                print(f"   - {tool.name}")

            # Test get_multiple_table_schemas
            print("\n📋 Testing get_multiple_table_schemas()...")
            result = await session.call_tool(
                "get_multiple_table_schemas", arguments={"table_names": ["products", "orders", "stores"]}
            )
            schema_data = result.content[0].text
            print(f"✅ get_multiple_table_schemas() - Retrieved data (first 200 chars): {schema_data[:200]}...")

            # Test execute_sales_query
            print("\n📊 Testing execute_sales_query()...")
            result = await session.call_tool(
                "execute_sales_query",
                arguments={"sql_query": "SELECT store_name, is_online FROM stores LIMIT 5"},
            )
            query_data = result.content[0].text
            print(f"✅ execute_sales_query() - Retrieved data (first 200 chars): {query_data[:200]}...")

            # Test get_current_utc_date
            print("\n🕐 Testing get_current_utc_date()...")
            result = await session.call_tool("get_current_utc_date", arguments={})
            date_data = result.content[0].text
            print(f"✅ get_current_utc_date() - {date_data}")

            print("\n" + "=" * 80)
            print("✅ Sales Analysis MCP Server: All tests passed!")
            print("=" * 80)


async def main():
    """Run all server tests."""
    print("\n" + "=" * 80)
    print("MCP LIVE SERVER TESTS")
    print("Testing MCP servers via HTTP with MCP client library")
    print("=" * 80)

    try:
        await test_finance_server()
        await test_supplier_server()
        await test_sales_analysis_server()

        print("\n" + "=" * 80)
        print("✅ ALL MCP SERVER TESTS PASSED!")
        print("=" * 80)
        print("\nAll MCP servers (Finance, Supplier, and Sales Analysis) are running correctly")
        print("and responding to tool calls via HTTP transport.\n")

    except Exception as e:
        print(f"\n❌ Test failed: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
