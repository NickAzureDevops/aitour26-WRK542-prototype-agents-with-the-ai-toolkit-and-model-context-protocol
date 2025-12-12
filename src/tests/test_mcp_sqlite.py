#!/usr/bin/env python3
"""Test script for SQLite MCP servers"""

import sys

sys.path.insert(0, "/workspace/src/mcp_server/sales_analysis")

import asyncio
import json

from sales_analysis_sqlite import SQLiteSchemaProvider


async def test_schema_provider():
    """Test the SQLite schema provider directly"""
    print("=" * 70)
    print("TESTING SQLITE MCP SCHEMA PROVIDER")
    print("=" * 70)

    provider = SQLiteSchemaProvider()

    # Test 1: Get all schemas
    print("\n✓ Test 1: Get all table schemas")
    print("-" * 70)
    schemas = await provider.get_all_schemas()
    print(f"Found {len(schemas)} tables:")
    for table_name in schemas.keys():
        row_count = schemas[table_name].get("row_count", 0)
        print(f"  - {table_name}: {row_count:,} rows")

    # Test 2: Get specific table schema
    print("\n✓ Test 2: Get products table schema")
    print("-" * 70)
    products_schema = await provider.get_table_schema("products")
    print(f"Table: {products_schema['table_name']}")
    print(f"Columns: {len(products_schema['columns'])}")
    for col in products_schema["columns"][:5]:
        print(f"  - {col['name']} ({col['type']})")

    # Test 3: Execute query
    print("\n✓ Test 3: Execute SQL query")
    print("-" * 70)
    result = await provider.execute_query("SELECT product_id, product_name, base_price FROM products LIMIT 3")
    results = json.loads(result)
    print(f"Query returned {len(results)} rows:")
    for row in results:
        print(f"  - {row['product_name']}: ${row['base_price']:.2f}")

    # Test 4: Semantic search
    print("\n✓ Test 4: Semantic search with sample embedding")
    print("-" * 70)
    # Get a sample embedding from the database
    conn = provider.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT description_embedding FROM product_description_embeddings LIMIT 1")
    sample_embedding_json = cursor.fetchone()[0]
    conn.close()

    sample_embedding = json.loads(sample_embedding_json)
    print(f"Using sample embedding with {len(sample_embedding)} dimensions")

    result = await provider.search_products_by_similarity(
        query_embedding=sample_embedding, max_rows=5, similarity_threshold=50.0
    )
    results = json.loads(result)
    print(f"Found {len(results)} similar products:")
    for row in results:
        print(f"  - {row['product_name']}: {row['similarity_score']:.2f}% similar")

    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_schema_provider())
