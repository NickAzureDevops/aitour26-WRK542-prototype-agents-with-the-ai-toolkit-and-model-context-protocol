#!/usr/bin/env python3
import asyncio
import sys

sys.path.insert(0, "/workspace/src")

from fastmcp.client import Client

from mcp_servers.product_server import mcp as product_mcp


async def test():
    async with Client(product_mcp) as client:
        # First test a tool that returns a dict
        print("=" * 80)
        print("Testing get_product_availability (returns dict):")
        print("=" * 80)
        result = await client.call_tool(name="get_product_availability", arguments={"sku": "HTHM001600"})

        print(f"Result type: {type(result)}")
        print(f"Result.data type: {type(result.data)}")
        print(f"Result.data keys: {result.data.keys() if hasattr(result.data, 'keys') else 'N/A'}")
        print(f"Can access SKU: {result.data.get('sku') if hasattr(result.data, 'get') else 'N/A'}")
        print()

        # Now test semantic search
        print("=" * 80)
        print("Testing search_products_by_description (returns list[dict]):")
        print("=" * 80)
        result = await client.call_tool(
            name="search_products_by_description",
            arguments={"query": "cordless drill", "limit": 3, "min_similarity": 0.3},
        )

        print(f"Result type: {type(result)}")
        print(f"Result.data type: {type(result.data)}")
        print(f"Result.data: {result.data}")
        print(f"Result.data length: {len(result.data) if hasattr(result.data, '__len__') else 'N/A'}")

        # Try to access the raw content
        print(f"\nResult content: {result.content}")
        print(f"Result content type: {type(result.content)}")
        if result.content:
            for i, content in enumerate(result.content):
                print(f"Content {i}: {content}")
                if hasattr(content, "text"):
                    print(f"Content {i} text: {content.text[:200]}")
                    import json

                    try:
                        parsed = json.loads(content.text)
                        print(f"Parsed JSON type: {type(parsed)}")
                        if isinstance(parsed, list) and len(parsed) > 0:
                            print(f"First item: {parsed[0]}")
                    except:
                        pass


asyncio.run(test())
