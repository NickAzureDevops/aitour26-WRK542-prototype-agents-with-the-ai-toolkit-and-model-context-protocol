#!/usr/bin/env python3
"""
Comprehensive test for Product MCP Server semantic search with real Azure OpenAI embeddings.
"""

import asyncio
import json
import sys
from typing import Any

# Add src directory to path
sys.path.insert(0, "/workspace/src")

from fastmcp.client import Client

from mcp_servers.product_server import mcp as product_mcp


async def test_semantic_search():
    """Test semantic search with various queries."""
    test_queries = [
        {
            "name": "Power Tools - Cordless Drill",
            "query": "cordless drill with battery",
            "limit": 5,
            "min_similarity": 0.3,
        },
        {
            "name": "Hand Tools - Hammer",
            "query": "hammer for construction",
            "limit": 3,
            "min_similarity": 0.3,
        },
        {
            "name": "Outdoor - Lawn Mower",
            "query": "lawn mower for cutting grass",
            "limit": 5,
            "min_similarity": 0.3,
        },
        {
            "name": "Painting - Spray Equipment",
            "query": "spray paint equipment for walls",
            "limit": 5,
            "min_similarity": 0.25,
        },
        {
            "name": "Safety - Protective Gear",
            "query": "safety goggles and protective equipment",
            "limit": 5,
            "min_similarity": 0.3,
        },
        {
            "name": "Fasteners - Screws and Nails",
            "query": "wood screws and nails for carpentry",
            "limit": 5,
            "min_similarity": 0.25,
        },
    ]

    print("\n" + "=" * 100)
    print("🔍 TESTING SEMANTIC SEARCH WITH AZURE OPENAI EMBEDDINGS")
    print("=" * 100 + "\n")

    all_results = []

    async with Client(product_mcp) as client:
        for i, test in enumerate(test_queries, 1):
            print(f"\n{'─' * 100}")
            print(f"TEST {i}: {test['name']}")
            print(f"{'─' * 100}")
            print(f"Query: '{test['query']}'")
            print(f"Limit: {test['limit']}, Min Similarity: {test['min_similarity']}")
            print()

            try:
                result = await client.call_tool(
                    name="search_products_by_description",
                    arguments={
                        "query": test["query"],
                        "limit": test["limit"],
                        "min_similarity": test["min_similarity"],
                    },
                )

                # Get the data from the result - for list returns, use result.content
                if result.content and len(result.content) > 0:
                    # Parse the JSON string from content
                    products_list = json.loads(result.content[0].text)
                else:
                    products_list = []

                if not products_list:
                    print("❌ No products found!")
                    all_results.append({"test": test["name"], "status": "no_results", "count": 0})
                    continue

                print(f"✅ Found {len(products_list)} products:\n")

                for j, product in enumerate(products_list, 1):
                    print(f"  {j}. {product['product_name']} (SKU: {product['sku']})")
                    print(f"     Category: {product['category']} | Type: {product['product_type']}")
                    print(f"     Price: ${product['base_price']:.2f} | Profit Margin: {product['profit_margin']:.1f}%")
                    print(f"     Similarity Score: {product['similarity_score']:.4f}")
                    print(f"     Description: {product['description'][:100]}...")
                    print()

                all_results.append(
                    {
                        "test": test["name"],
                        "status": "success",
                        "count": len(products_list),
                        "top_score": products_list[0]["similarity_score"],
                        "top_product": products_list[0]["product_name"],
                    }
                )

            except Exception as e:
                import traceback

                print(f"❌ Error: {e!s}")
                print(f"   Traceback: {traceback.format_exc()}\n")
                all_results.append({"test": test["name"], "status": "error", "error": str(e)})

    # Summary
    print("\n" + "=" * 100)
    print("📊 TEST SUMMARY")
    print("=" * 100 + "\n")

    successful_tests = [r for r in all_results if r["status"] == "success"]
    failed_tests = [r for r in all_results if r["status"] == "error"]
    no_result_tests = [r for r in all_results if r["status"] == "no_results"]

    print(f"Total Tests: {len(all_results)}")
    print(f"✅ Successful: {len(successful_tests)}")
    print(f"❌ Failed: {len(failed_tests)}")
    print(f"⚠️  No Results: {len(no_result_tests)}")
    print()

    if successful_tests:
        print("Successful Tests:")
        for result in successful_tests:
            print(f"  • {result['test']}: {result['count']} products found")
            print(f"    Top Match: {result['top_product']} (score: {result['top_score']:.4f})")
        print()

    if failed_tests:
        print("Failed Tests:")
        for result in failed_tests:
            print(f"  • {result['test']}: {result['error']}")
        print()

    if no_result_tests:
        print("Tests with No Results:")
        for result in no_result_tests:
            print(f"  • {result['test']}")
        print()

        # Additional detailed test - show similarity distribution
        print("\n" + "=" * 100)
        print("🔬 DETAILED ANALYSIS: Similarity Score Distribution")
        print("=" * 100 + "\n")

        try:
            result = await client.call_tool(
                name="search_products_by_description",
                arguments={"query": "power drill", "limit": 20, "min_similarity": 0.0},
            )

            # Get the data from result.content for list returns
            if result.content and len(result.content) > 0:
                products_list = json.loads(result.content[0].text)
            else:
                products_list = []

            if products_list:
                scores = [p.get("similarity_score", 0) for p in products_list]
                print(f"Query: 'power drill' (top 20 results)")
                print(f"Results found: {len(products_list)}")
                print(f"Score range: {min(scores):.4f} - {max(scores):.4f}")
                print(f"Average score: {sum(scores) / len(scores):.4f}")
                print()

                print("Score distribution:")
                for i, product in enumerate(products_list[:10], 1):
                    print(
                        f"  {i:2d}. [{product['similarity_score']:.4f}] {product['product_name']} - {product['category']}"
                    )

        except Exception as e:
            print(f"Error in detailed analysis: {e}")

    print("\n" + "=" * 100)
    print("✨ TEST COMPLETE!")
    print("=" * 100 + "\n")


if __name__ == "__main__":
    asyncio.run(test_semantic_search())
