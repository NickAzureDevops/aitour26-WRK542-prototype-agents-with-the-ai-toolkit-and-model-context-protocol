#!/usr/bin/env python3
"""
Test semantic search with full product details display.
"""

import asyncio
import json
import sys

sys.path.insert(0, "/workspace/src")

from fastmcp.client import Client

from mcp_servers.product_server import mcp as product_mcp


async def test_detailed_search():
    """Test semantic search and display complete product information."""

    print("\n" + "=" * 100)
    print("🔍 SEMANTIC PRODUCT SEARCH - DETAILED RESULTS")
    print("=" * 100 + "\n")

    test_queries = [
        {
            "query": "cordless drill with battery for home projects",
            "limit": 3,
            "description": "Looking for a cordless drill for DIY home improvement",
        },
        {
            "query": "safety goggles and protective glasses",
            "limit": 3,
            "description": "Need eye protection for workshop",
        },
        {"query": "exterior house paint and primer", "limit": 3, "description": "Painting the outside of my house"},
    ]

    async with Client(product_mcp) as client:
        for i, test in enumerate(test_queries, 1):
            print(f"\n{'─' * 100}")
            print(f"SEARCH {i}: {test['description']}")
            print(f"{'─' * 100}")
            print(f"Query: '{test['query']}'")
            print(f"Max Results: {test['limit']}\n")

            try:
                result = await client.call_tool(
                    name="search_products_by_description",
                    arguments={"query": test["query"], "limit": test["limit"], "min_similarity": 0.3},
                )

                if result.content and len(result.content) > 0:
                    products = json.loads(result.content[0].text)
                else:
                    products = []

                if not products:
                    print("❌ No matching products found.\n")
                    continue

                print(f"✅ Found {len(products)} matching products:\n")

                for j, product in enumerate(products, 1):
                    print(f"┌─ PRODUCT {j} {'─' * 85}")
                    print(f"│ Product: {product['product_name']}")
                    print(f"│ SKU: {product['sku']}")
                    print(f"│ Category: {product['category']} → {product['product_type']}")
                    print(f"│")
                    print(f"│ 💰 PRICING:")
                    print(f"│    Retail Price: ${product['base_price']:.2f}")
                    print(f"│    Cost: ${product['cost']:.2f}")
                    print(f"│    Profit Margin: {product['profit_margin']:.1f}%")
                    print(f"│")
                    print(f"│ 🎯 RELEVANCE SCORE: {product['similarity_score']:.4f}")
                    print(
                        f"│    {'█' * int(product['similarity_score'] * 50)} {product['similarity_score'] * 100:.1f}%"
                    )
                    print(f"│")
                    print(f"│ 🚚 SUPPLIER:")
                    supplier = product["supplier"]
                    print(f"│    Name: {supplier['supplier_name']}")
                    print(
                        f"│    Rating: {'⭐' * int(supplier['supplier_rating'])} ({supplier['supplier_rating']:.1f}/5.0)"
                    )
                    print(f"│    Lead Time: {supplier['lead_time_days']} days")
                    print(f"│    Min Order: ${supplier['minimum_order_amount']:.2f}")
                    if supplier["bulk_discount_percent"] > 0:
                        print(f"│    Bulk Discount: {supplier['bulk_discount_percent']:.0f}%")
                    print(f"│")
                    print(f"│ 📝 DESCRIPTION:")
                    desc = product["description"]
                    # Word wrap the description
                    words = desc.split()
                    line = "│    "
                    for word in words:
                        if len(line) + len(word) + 1 > 95:
                            print(line)
                            line = "│    " + word
                        else:
                            line += " " + word if line != "│    " else word
                    if line != "│    ":
                        print(line)
                    print(f"└{'─' * 99}\n")

                # Now get detailed availability for the top match
                if products:
                    top_product = products[0]
                    print(f"🔍 Getting detailed availability for top match: {top_product['product_name']}...")
                    print()

                    avail_result = await client.call_tool(
                        name="get_product_availability", arguments={"sku": top_product["sku"]}
                    )

                    if avail_result.data:
                        avail = avail_result.data
                        print(f"📦 AVAILABILITY DETAILS:")
                        print(f"   Total Stock (All Stores): {avail['availability']['total_stock_all_stores']} units")
                        print(f"   Status: {'✅ IN STOCK' if avail['availability']['in_stock'] else '❌ OUT OF STOCK'}")
                        print()
                        print(f"   Stock by Store:")
                        for store in avail["availability"]["stock_by_store"][:5]:  # Show first 5 stores
                            status_icon = "✅" if store["stock_level"] > 0 else "❌"
                            store_type = "🌐 Online" if store["is_online"] else "🏪 Physical"
                            print(
                                f"      {status_icon} {store_type} {store['store_name']}: {store['stock_level']} units"
                            )
                        print()
                        print(f"   🚚 SUPPLIER INFO:")
                        supplier = avail["supplier_info"]
                        print(f"      Supplier: {supplier['supplier_name']}")
                        print(
                            f"      Rating: {'⭐' * int(supplier['supplier_rating'])} ({supplier['supplier_rating']:.1f}/5.0)"
                        )
                        print(f"      Lead Time: {supplier['lead_time_days']} days")
                        print(f"      Min Order: ${supplier['minimum_order_amount']:.2f}")
                        if supplier["bulk_discount_percent"] > 0:
                            print(f"      Bulk Discount: {supplier['bulk_discount_percent']:.0f}%")
                        print()

            except Exception as e:
                print(f"❌ Error: {e!s}\n")
                import traceback

                traceback.print_exc()

    print("\n" + "=" * 100)
    print("✨ SEARCH COMPLETE")
    print("=" * 100 + "\n")


if __name__ == "__main__":
    asyncio.run(test_detailed_search())
