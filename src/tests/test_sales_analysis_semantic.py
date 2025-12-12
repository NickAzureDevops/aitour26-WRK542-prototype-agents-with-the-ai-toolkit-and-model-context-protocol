#!/usr/bin/env python3
"""
Test Sales Analysis MCP server semantic search with supplier information.
"""

import asyncio
import json
import sys

sys.path.insert(0, "/workspace/src")

from fastmcp.client import Client

from mcp_servers.sales_analysis import mcp


async def test_sales_analysis_semantic_search():
    """Test Sales Analysis semantic search includes supplier info."""

    print("\n" + "=" * 100)
    print("🧪 TESTING SALES ANALYSIS SEMANTIC SEARCH WITH SUPPLIER INFO")
    print("=" * 100 + "\n")

    try:
        async with Client(mcp) as client:
            # Test semantic search
            result = await client.call_tool(
                name="semantic_search_products",
                arguments={"query_description": "cordless power drill with battery", "limit": 3, "min_similarity": 0.3},
            )

            if result.content and len(result.content) > 0:
                products = json.loads(result.content[0].text)
                print(f"✅ Found {len(products)} products\n")

                for i, product in enumerate(products, 1):
                    print(f"{'─' * 100}")
                    print(f"Result #{i}")
                    print(f"{'─' * 100}")
                    print(f"  Product: {product['product_name']}")
                    print(f"  SKU: {product['sku']}")
                    print(f"  Similarity Score: {product['similarity_score']:.4f}")
                    print(f"  Price: ${product['base_price']:.2f}")
                    print(f"  Cost: ${product['cost']:.2f}")
                    print(f"  Category: {product['category_name']}")
                    print(f"  Type: {product['type_name']}")

                    # Check for supplier info
                    if "supplier" in product:
                        supplier = product["supplier"]
                        print(f"\n  📦 SUPPLIER INFORMATION:")
                        print(f"     Name: {supplier['supplier_name']}")
                        print(f"     Rating: {supplier['supplier_rating']:.1f}/5.0 ⭐")
                        print(f"     Lead Time: {supplier['lead_time_days']} days")
                        print(f"     Min Order Amount: ${supplier['minimum_order_amount']:.2f}")
                        print(f"     Bulk Discount: {supplier['bulk_discount_percent']:.1f}%")
                        print(f"  ✅ Supplier info INCLUDED")
                    else:
                        print(f"  ❌ Supplier info MISSING")

                    print(f"  Description: {product['product_description'][:100]}...")
                    print()

                # Summary
                has_supplier = all("supplier" in p for p in products)
                print("=" * 100)
                if has_supplier:
                    print("✅ SUCCESS: All products include supplier information!")
                else:
                    print("❌ FAIL: Some products missing supplier information!")
                print("=" * 100)

                return has_supplier
            print("❌ No products found")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_sales_analysis_semantic_search())
    sys.exit(0 if success else 1)
