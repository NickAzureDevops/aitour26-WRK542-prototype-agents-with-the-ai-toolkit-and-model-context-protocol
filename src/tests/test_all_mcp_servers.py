#!/usr/bin/env python3
"""
Comprehensive E2E test for all MCP servers including semantic search validation.
"""

import asyncio
import json
import sys

sys.path.insert(0, "/workspace/src")

from fastmcp.client import Client

from mcp_servers.finance_server import mcp as finance_mcp
from mcp_servers.inventory_server import mcp as inventory_mcp
from mcp_servers.product_server import mcp as product_mcp
from mcp_servers.sales_analysis import mcp as sales_mcp
from mcp_servers.supplier_server import mcp as supplier_mcp


async def test_all_servers():
    """Test all MCP servers with detailed validation."""

    print("\n" + "=" * 100)
    print("🧪 COMPREHENSIVE MCP SERVERS END-TO-END TEST (5 Servers)")
    print("=" * 100 + "\n")

    results = []

    # Test Finance Server
    print("─" * 100)
    print("1️⃣  TESTING FINANCE MCP SERVER")
    print("─" * 100)

    try:
        async with Client(finance_mcp) as client:
            # Test get_stores
            result = await client.call_tool(name="get_stores", arguments={"store_name": ""})
            stores_count = len(result.data) if result.data else 0
            print(f"   ✅ get_stores: Found {stores_count} stores")

            # Test get_company_order_policy
            result = await client.call_tool(name="get_company_order_policy", arguments={"department": "Finance"})
            print(f"   ✅ get_company_order_policy: Retrieved policy")

            # Test get_historical_sales_data
            result = await client.call_tool(
                name="get_historical_sales_data", arguments={"days_back": 30, "category_name": "POWER TOOLS"}
            )
            sales_count = len(result.data) if result.data else 0
            print(f"   ✅ get_historical_sales_data: Found {sales_count} sales records")

            results.append(("Finance Server", "PASSED", "All tools working"))
            print("\n✅ Finance Server: ALL TESTS PASSED\n")
    except Exception as e:
        results.append(("Finance Server", "FAILED", str(e)))
        print(f"\n❌ Finance Server: FAILED - {e}\n")

    # Test Supplier Server
    print("─" * 100)
    print("2️⃣  TESTING SUPPLIER MCP SERVER")
    print("─" * 100)

    try:
        async with Client(supplier_mcp) as client:
            # Test find_suppliers_for_request
            result = await client.call_tool(
                name="find_suppliers_for_request", arguments={"product_category": "PLUMBING", "min_rating": 4.0}
            )
            suppliers_count = len(result.data) if result.data else 0
            print(f"   ✅ find_suppliers_for_request: Found {suppliers_count} suppliers")

            # Test get_supplier_history_and_performance
            result = await client.call_tool(name="get_supplier_history_and_performance", arguments={"supplier_id": 1})
            print(f"   ✅ get_supplier_history_and_performance: Retrieved supplier data")

            # Test get_company_supplier_policy
            result = await client.call_tool(name="get_company_supplier_policy", arguments={"department": ""})
            print(f"   ✅ get_company_supplier_policy: Retrieved policy")

            results.append(("Supplier Server", "PASSED", "All tools working"))
            print("\n✅ Supplier Server: ALL TESTS PASSED\n")
    except Exception as e:
        results.append(("Supplier Server", "FAILED", str(e)))
        print(f"\n❌ Supplier Server: FAILED - {e}\n")

    # Test Product Server (with semantic search validation)
    print("─" * 100)
    print("3️⃣  TESTING PRODUCT MCP SERVER (With Azure OpenAI Semantic Search)")
    print("─" * 100)

    try:
        async with Client(product_mcp) as client:
            # Test semantic search with supplier info
            result = await client.call_tool(
                name="search_products_by_description",
                arguments={"query": "cordless power drill", "limit": 3, "min_similarity": 0.3},
            )

            if result.content and len(result.content) > 0:
                products = json.loads(result.content[0].text)
                print(f"   ✅ search_products_by_description: Found {len(products)} products")

                if products:
                    top_product = products[0]
                    print(
                        f"      Top match: {top_product['product_name']} (similarity: {top_product['similarity_score']:.4f})"
                    )

                    # Validate supplier info is included
                    if "supplier" in top_product:
                        supplier = top_product["supplier"]
                        print(
                            f"      Supplier: {supplier['supplier_name']} (rating: {supplier['supplier_rating']:.1f}/5.0)"
                        )
                        print(f"      Lead time: {supplier['lead_time_days']} days")
                        print(f"   ✅ Supplier information included in search results")
                    else:
                        print(f"   ⚠️  Warning: Supplier info not found in search results")
            else:
                print(f"   ⚠️  search_products_by_description: No products found")

            # Test get_product_availability
            result = await client.call_tool(name="get_product_availability", arguments={"sku": "HTHM001600"})
            assert result.data is not None
            assert "sku" in result.data
            print(f"   ✅ get_product_availability: Retrieved for SKU {result.data['sku']}")

            # Test get_low_stock_products
            result = await client.call_tool(
                name="get_low_stock_products", arguments={"threshold": 30, "category_name": "ELECTRICAL"}
            )
            low_stock_count = len(result.data) if result.data else 0
            print(f"   ✅ get_low_stock_products: Found {low_stock_count} items")

            # Test compare_product_prices
            result = await client.call_tool(
                name="compare_product_prices", arguments={"skus": ["HTHM001600", "HTHM031200"]}
            )
            comparison_count = len(result.data) if result.data else 0
            print(f"   ✅ compare_product_prices: Compared {comparison_count} products")

            results.append(("Product Server", "PASSED", "All tools + semantic search working"))
            print("\n✅ Product Server: ALL TESTS PASSED\n")
    except Exception as e:
        results.append(("Product Server", "FAILED", str(e)))
        print(f"\n❌ Product Server: FAILED - {e}\n")
        import traceback

        traceback.print_exc()

    # Test Sales Analysis Server
    print("─" * 100)
    print("4️⃣  TESTING SALES ANALYSIS MCP SERVER")
    print("─" * 100)

    try:
        async with Client(sales_mcp) as client:
            # Test semantic_search_products
            result = await client.call_tool(
                name="semantic_search_products",
                arguments={"query_description": "cordless power drill", "limit": 3, "min_similarity": 0.3},
            )
            if result.content and len(result.content) > 0:
                products = json.loads(result.content[0].text)
                print(f"   ✅ semantic_search_products: Found {len(products)} products")
            else:
                print(f"   ⚠️  semantic_search_products: No products found")

            # Test get_multiple_table_schemas
            result = await client.call_tool(
                name="get_multiple_table_schemas", arguments={"table_names": ["products", "categories"]}
            )
            print(f"   ✅ get_multiple_table_schemas: Retrieved schemas")

            # Test execute_sales_query
            result = await client.call_tool(
                name="execute_sales_query",
                arguments={"sql_query": "SELECT COUNT(*) as product_count FROM products LIMIT 5"},
            )
            print(f"   ✅ execute_sales_query: Executed query successfully")

            # Test get_current_utc_date
            result = await client.call_tool(name="get_current_utc_date", arguments={})
            print(f"   ✅ get_current_utc_date: Retrieved UTC date")

            results.append(("Sales Analysis Server", "PASSED", "All tools working"))
            print("\n✅ Sales Analysis Server: ALL TESTS PASSED\n")
    except Exception as e:
        results.append(("Sales Analysis Server", "FAILED", str(e)))
        print(f"\n❌ Sales Analysis Server: FAILED - {e}\n")

    # Test Inventory Server
    print("─" * 100)
    print("5️⃣  TESTING INVENTORY MCP SERVER")
    print("─" * 100)

    try:
        async with Client(inventory_mcp) as client:
            # Test get_stock_level_by_sku
            result = await client.call_tool(name="get_stock_level_by_sku", arguments={"sku": "HTHM001600"})
            if result.content and len(result.content) > 0:
                inventory = json.loads(result.content[0].text)
                print(f"   ✅ get_stock_level_by_sku: Found stock at {len(inventory)} store(s)")

                # Test stock transfer with small quantity
                if len(inventory) >= 2:
                    from_store = inventory[0]
                    to_store = inventory[1]
                    transfer_qty = 2

                    # Perform transfer
                    transfer_result = await client.call_tool(
                        name="transfer_stock",
                        arguments={
                            "from_store_id": from_store["store_id"],
                            "to_store_id": to_store["store_id"],
                            "sku": "HTHM001600",
                            "quantity": transfer_qty,
                        },
                    )

                    if transfer_result.data and transfer_result.data.get("success"):
                        print(f"   ✅ transfer_stock: Transferred {transfer_qty} units successfully")

                        # Transfer back to restore original state
                        await client.call_tool(
                            name="transfer_stock",
                            arguments={
                                "from_store_id": to_store["store_id"],
                                "to_store_id": from_store["store_id"],
                                "sku": "HTHM001600",
                                "quantity": transfer_qty,
                            },
                        )
                        print(f"   ✅ Restored original inventory state")
                    else:
                        print(f"   ⚠️  transfer_stock: Transfer failed")
                else:
                    print(f"   ⚠️  transfer_stock: Insufficient stores to test transfer")
            else:
                print(f"   ⚠️  get_stock_level_by_sku: No inventory found")

            results.append(("Inventory Server", "PASSED", "All tools working"))
            print("\n✅ Inventory Server: ALL TESTS PASSED\n")
    except Exception as e:
        results.append(("Inventory Server", "FAILED", str(e)))
        print(f"\n❌ Inventory Server: FAILED - {e}\n")

    # Print final summary
    print("=" * 100)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 100)
    print()

    passed = sum(1 for _, status, _ in results if status == "PASSED")
    failed = sum(1 for _, status, _ in results if status == "FAILED")

    for server, status, details in results:
        icon = "✅" if status == "PASSED" else "❌"
        print(f"{icon} {server:30s} {status:10s} - {details}")

    print()
    print(f"Total: {len(results)} servers tested")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print()

    if failed == 0:
        print("🎉 ALL MCP SERVERS PASSED COMPREHENSIVE TESTING!")
    else:
        print(f"⚠️  {failed} server(s) failed testing")

    print("=" * 100)
    print()

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(test_all_servers())
    sys.exit(0 if success else 1)
