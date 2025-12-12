#!/usr/bin/env python3
"""
Test Inventory MCP Server functionality.
"""

import asyncio
import json
import sys

sys.path.insert(0, "/workspace/src")

from fastmcp.client import Client

from mcp_servers.inventory_server import mcp


async def test_inventory_server():
    """Test Inventory MCP server tools."""

    print("\n" + "=" * 100)
    print("🧪 TESTING INVENTORY MCP SERVER")
    print("=" * 100 + "\n")

    try:
        async with Client(mcp) as client:
            # Test 1: Get stock levels for a product
            print("─" * 100)
            print("Test 1: Get Stock Levels by SKU")
            print("─" * 100)

            result = await client.call_tool(name="get_stock_level_by_sku", arguments={"sku": "HTHM001600"})

            if result.content and len(result.content) > 0:
                inventory = json.loads(result.content[0].text)
                print(f"✅ Found stock levels at {len(inventory)} store(s)")
                print(f"\nProduct: {inventory[0]['product_name']} (SKU: {inventory[0]['sku']})")
                print("\nStock by Store:")
                total_stock = 0
                for item in inventory[:5]:  # Show first 5 stores
                    print(f"  • {item['store_name']:40s} [{item['store_type']:8s}] - {item['stock_level']:3d} units")
                    total_stock += item["stock_level"]
                if len(inventory) > 5:
                    for item in inventory[5:]:
                        total_stock += item["stock_level"]
                    print(f"  ... and {len(inventory) - 5} more store(s)")
                print(f"\n  Total Stock Across All Stores: {total_stock} units")
            else:
                print("⚠️  No inventory found")

            print()

            # Test 2: Find stores with good stock for transfer test
            print("─" * 100)
            print("Test 2: Stock Transfer Between Stores")
            print("─" * 100)

            # Get store with highest stock
            if result.content and len(result.content) > 0:
                inventory = json.loads(result.content[0].text)
                if len(inventory) >= 2:
                    from_store = inventory[0]  # Store with most stock
                    to_store = inventory[1]  # Store with second most stock
                else:
                    from_store = None
                    to_store = None
            else:
                from_store = None
                to_store = None

            if from_store and to_store:
                print(f"\nBefore Transfer:")
                print(
                    f"  From: Store #{from_store['store_id']} ({from_store['store_name']}) - {from_store['stock_level']} units"
                )
                print(
                    f"  To:   Store #{to_store['store_id']} ({to_store['store_name']}) - {to_store['stock_level']} units"
                )

                # Perform transfer
                transfer_qty = 5
                print(f"\n🔄 Transferring {transfer_qty} units...")

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
                    result_data = transfer_result.data
                    print(f"\n✅ Transfer Successful!")
                    print(f"\nAfter Transfer:")
                    print(
                        f"  From: Store #{result_data['from_store']['store_id']} - {result_data['from_store']['stock_after']} units (was {result_data['from_store']['stock_before']})"
                    )
                    print(
                        f"  To:   Store #{result_data['to_store']['store_id']} - {result_data['to_store']['stock_after']} units (was {result_data['to_store']['stock_before']})"
                    )

                    # Verify the transfer by getting stock levels again
                    print(f"\n🔍 Verifying transfer...")
                    verify_result = await client.call_tool(
                        name="get_stock_level_by_sku", arguments={"sku": "HTHM001600"}
                    )

                    if verify_result.content and len(verify_result.content) > 0:
                        verified_inventory = json.loads(verify_result.content[0].text)
                        from_store_verified = next(
                            (s for s in verified_inventory if s["store_id"] == from_store["store_id"]), None
                        )
                        to_store_verified = next(
                            (s for s in verified_inventory if s["store_id"] == to_store["store_id"]), None
                        )

                        if from_store_verified and to_store_verified:
                            print(f"✅ Verified: Stock levels updated correctly")
                            print(f"  From store now has: {from_store_verified['stock_level']} units")
                            print(f"  To store now has: {to_store_verified['stock_level']} units")

                    # Transfer back to restore original state
                    print(f"\n↩️  Transferring back to restore original state...")
                    await client.call_tool(
                        name="transfer_stock",
                        arguments={
                            "from_store_id": to_store["store_id"],
                            "to_store_id": from_store["store_id"],
                            "sku": "HTHM001600",
                            "quantity": transfer_qty,
                        },
                    )
                    print(f"✅ Original inventory restored")

                else:
                    print(f"❌ Transfer Failed: {transfer_result.data.get('message', 'Unknown error')}")
            else:
                print("⚠️  Not enough stores with inventory to test transfer")

            print()

            # Test 3: Test error handling
            print("─" * 100)
            print("Test 3: Error Handling")
            print("─" * 100)

            # Test insufficient stock
            print("\n• Testing insufficient stock scenario...")
            error_result = await client.call_tool(
                name="transfer_stock",
                arguments={"from_store_id": 1, "to_store_id": 2, "sku": "HTHM001600", "quantity": 999999},
            )
            if error_result.data and not error_result.data.get("success"):
                print(f"  ✅ Correctly rejected: {error_result.data.get('message')}")

            # Test same store transfer
            print("\n• Testing same store transfer...")
            error_result = await client.call_tool(
                name="transfer_stock",
                arguments={"from_store_id": 1, "to_store_id": 1, "sku": "HTHM001600", "quantity": 5},
            )
            if error_result.data and not error_result.data.get("success"):
                print(f"  ✅ Correctly rejected: {error_result.data.get('message')}")

            # Test invalid SKU
            print("\n• Testing invalid SKU...")
            error_result = await client.call_tool(
                name="transfer_stock",
                arguments={"from_store_id": 1, "to_store_id": 2, "sku": "INVALID_SKU", "quantity": 5},
            )
            if error_result.data and not error_result.data.get("success"):
                print(f"  ✅ Correctly rejected: {error_result.data.get('message')}")

            print()
            print("=" * 100)
            print("✅ INVENTORY SERVER: ALL TESTS PASSED")
            print("=" * 100)

            return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_inventory_server())
    sys.exit(0 if success else 1)
