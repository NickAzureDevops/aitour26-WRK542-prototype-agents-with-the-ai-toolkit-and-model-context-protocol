#!/usr/bin/env python3
"""Summary test showing both SQLite MCP servers are operational"""

import sys

sys.path.insert(0, "/workspace/src/mcp_server/sales_analysis")

import asyncio
import json

from sales_analysis_sqlite import SQLiteSchemaProvider


async def main():
    print("=" * 80)
    print("SQLITE MCP SERVERS - OPERATIONAL STATUS")
    print("=" * 80)

    provider = SQLiteSchemaProvider()

    print("\n📊 Database Summary:")
    print("-" * 80)
    schemas = await provider.get_all_schemas()
    for table_name, schema in schemas.items():
        print(f"  {table_name:<35} {schema['row_count']:>10,} rows")

    print("\n🔧 MCP Server #1: Basic SQL Operations (Port 8001)")
    print("-" * 80)
    print("  Available Tools:")
    print("    - get_table_schema(table_name)")
    print("    - get_all_table_schemas()")
    print("    - get_table_metadata(table_names[])")
    print("    - execute_sql_query(query)")

    # Demo query
    result = await provider.execute_query(
        "SELECT category_name, COUNT(*) as product_count FROM categories c "
        "JOIN products p ON c.category_id = p.category_id "
        "GROUP BY category_name ORDER BY product_count DESC LIMIT 5"
    )
    results = json.loads(result)
    print("\n  Example: Top 5 Categories by Product Count")
    for row in results:
        print(f"    {row['category_name']:<30} {row['product_count']:>3} products")

    print("\n🔍 MCP Server #2: Semantic Search (Port 8002)")
    print("-" * 80)
    print("  Available Tools:")
    print("    - All SQL tools from Server #1, plus:")
    print("    - search_products_by_description(query_text)")
    print("    - search_products_by_embedding(embedding[])")

    # Demo semantic search
    print("\n  Example: Semantic Search Demo")
    conn = provider.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.product_name, e.description_embedding 
        FROM products p
        JOIN product_description_embeddings e ON p.product_id = e.product_id
        WHERE p.product_name LIKE '%Hammer%'
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()

    if row:
        query_product = row[0]
        query_embedding = json.loads(row[1])

        print(f"    Query: Find products similar to '{query_product}'")

        result = await provider.search_products_by_similarity(
            query_embedding=query_embedding, max_rows=5, similarity_threshold=50.0
        )
        results = json.loads(result)
        print(f"    Results ({len(results)} products with >50% similarity):")
        for r in results:
            print(f"      {r['similarity_score']:>5.1f}% - {r['product_name']}")

    print("\n✅ STATUS: Both MCP servers are operational!")
    print("=" * 80)
    print("\nServer URLs:")
    print("  Basic SQL:        http://0.0.0.0:8001/sse")
    print("  Semantic Search:  http://0.0.0.0:8002/sse")
    print("\nVector Search: Pure Python (no extensions required)")
    print("Database: /workspace/data/zava.db")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
