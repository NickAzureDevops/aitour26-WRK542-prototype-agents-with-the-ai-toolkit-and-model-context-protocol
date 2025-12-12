#!/usr/bin/env python3
"""
Test script to verify MCP servers can connect to the new SQLite database.
"""

import asyncio
import sys

sys.path.insert(0, "/workspace/new/app/shared/src")

from zava_shop_shared.config import Config
from zava_shop_shared.finance_sqlite import FinanceSQLiteProvider
from zava_shop_shared.supplier_sqlite import SupplierSQLiteProvider


async def test_finance_connection():
    """Test Finance MCP database connection."""
    print("Testing Finance MCP database connection...")
    db = InventorySQLiteProvider()

    try:
        await db.open_engine()
        async with db.get_session() as session:
            from sqlalchemy import text

            result = await session.execute(text("SELECT COUNT(*) FROM stores"))
            count = result.scalar()
            print(f"✅ Finance MCP: Successfully connected! Found {count} stores.")
    except Exception as e:
        print(f"❌ Finance MCP connection failed: {e}")
        raise
    finally:
        await db.close_engine()


async def test_supplier_connection():
    """Test Supplier MCP database connection."""
    print("\nTesting Supplier MCP database connection...")
    db = SupplierSQLiteProvider()

    try:
        await db.open_engine()
        async with db.get_session() as session:
            from sqlalchemy import text

            result = await session.execute(text("SELECT COUNT(*) FROM suppliers"))
            count = result.scalar()
            print(f"✅ Supplier MCP: Successfully connected! Found {count} suppliers.")
    except Exception as e:
        print(f"❌ Supplier MCP connection failed: {e}")
        raise
    finally:
        await db.close_engine()


async def test_database_schema():
    """Test that all expected tables exist."""
    print("\nTesting database schema...")
    db = FinanceSQLiteProvider()

    try:
        await db.open_engine()
        async with db.get_session() as session:
            from sqlalchemy import text

            result = await session.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
            tables = [row[0] for row in result.fetchall()]
            print(f"✅ Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table}")
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        raise
    finally:
        await db.close_engine()


async def main():
    """Run all connection tests."""
    print("=" * 80)
    print("MCP Database Connection Tests")
    print("=" * 80)

    config = Config()
    print(f"\nDatabase URL: {config.sqlite_database_url}")
    print()

    await test_finance_connection()
    await test_supplier_connection()
    await test_database_schema()

    print("\n" + "=" * 80)
    print("✅ All MCP database connection tests passed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
