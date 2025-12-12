#!/usr/bin/env python3
"""
Test that all MCP servers have read-only access to the SQLite database.
"""

import asyncio
import sys

sys.path.insert(0, "/workspace/shared/src")

from sqlalchemy import text
from zava_shop_shared.finance_sqlite import FinanceSQLiteProvider
from zava_shop_shared.supplier_sqlite import SupplierSQLiteProvider


async def test_readonly_access():
    """Test that database connections are read-only."""

    print("\n" + "=" * 100)
    print("🔒 TESTING READ-ONLY DATABASE ACCESS FOR MCP SERVERS")
    print("=" * 100 + "\n")

    results = []

    # Test Finance SQLite Provider
    print("─" * 100)
    print("1️⃣  Testing FinanceSQLiteProvider (used by Finance, Product, Sales Analysis servers)")
    print("─" * 100)

    try:
        db = InventorySQLiteProvider()
        await db.open_engine()

        # Try a SELECT query (should work)
        try:
            async with db.get_session() as session:
                result = await session.execute(text("SELECT COUNT(*) FROM products LIMIT 1"))
                count = result.scalar()
                print(f"   ✅ READ access works: Found {count} products")
        except Exception as e:
            print(f"   ❌ READ access failed: {e}")
            results.append(("FinanceSQLiteProvider READ", "FAILED"))

        # Try an INSERT query (should fail in read-only mode)
        try:
            async with db.get_session() as session:
                await session.execute(text("INSERT INTO stores (store_name) VALUES ('TEST_STORE')"))
                await session.commit()
                print(f"   ❌ WRITE access allowed - DATABASE IS NOT READ-ONLY!")
                results.append(("FinanceSQLiteProvider", "FAILED - Write allowed"))
        except Exception as e:
            if "readonly" in str(e).lower() or "attempt to write" in str(e).lower():
                print(f"   ✅ WRITE access blocked: {type(e).__name__}")
                results.append(("FinanceSQLiteProvider", "PASSED - Read-only enforced"))
            else:
                print(f"   ⚠️  Write failed with unexpected error: {e}")
                results.append(("FinanceSQLiteProvider", "UNKNOWN"))

        await db.close_engine()
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        results.append(("FinanceSQLiteProvider", "FAILED - Connection error"))

    print()

    # Test Supplier SQLite Provider
    print("─" * 100)
    print("2️⃣  Testing SupplierSQLiteProvider (used by Supplier server)")
    print("─" * 100)

    try:
        db = SupplierSQLiteProvider()
        await db.create_pool()

        # Try a SELECT query (should work)
        try:
            async with db.get_session() as session:
                result = await session.execute(text("SELECT COUNT(*) FROM suppliers LIMIT 1"))
                count = result.scalar()
                print(f"   ✅ READ access works: Found {count} suppliers")
        except Exception as e:
            print(f"   ❌ READ access failed: {e}")
            results.append(("SupplierSQLiteProvider READ", "FAILED"))

        # Try an UPDATE query (should fail in read-only mode)
        try:
            async with db.get_session() as session:
                await session.execute(text("UPDATE suppliers SET supplier_name = 'TEST' WHERE supplier_id = 1"))
                await session.commit()
                print(f"   ❌ WRITE access allowed - DATABASE IS NOT READ-ONLY!")
                results.append(("SupplierSQLiteProvider", "FAILED - Write allowed"))
        except Exception as e:
            if "readonly" in str(e).lower() or "attempt to write" in str(e).lower():
                print(f"   ✅ WRITE access blocked: {type(e).__name__}")
                results.append(("SupplierSQLiteProvider", "PASSED - Read-only enforced"))
            else:
                print(f"   ⚠️  Write failed with unexpected error: {e}")
                results.append(("SupplierSQLiteProvider", "UNKNOWN"))

        await db.close_engine()
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        results.append(("SupplierSQLiteProvider", "FAILED - Connection error"))

    print()

    # Print summary
    print("=" * 100)
    print("📊 READ-ONLY ACCESS TEST SUMMARY")
    print("=" * 100)
    print()

    for provider, status in results:
        if "PASSED" in status:
            icon = "✅"
        elif "FAILED" in status:
            icon = "❌"
        else:
            icon = "⚠️"
        print(f"{icon} {provider:40s} {status}")

    print()

    passed = sum(1 for _, status in results if "PASSED" in status)
    failed = sum(1 for _, status in results if "FAILED" in status)

    if failed == 0 and passed == 2:
        print("🔒 SUCCESS: All database connections are READ-ONLY!")
        print("=" * 100)
        return True
    print(f"⚠️  {failed} provider(s) failed read-only enforcement")
    print("=" * 100)
    return False


if __name__ == "__main__":
    success = asyncio.run(test_readonly_access())
    sys.exit(0 if success else 1)
