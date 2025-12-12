"""
Test reproducibility: Generate database twice and verify inventory is identical
"""

import sqlite3
import subprocess
from pathlib import Path

DB_FILE = Path(__file__).parent / "retail.db"
DB_FILE_2 = Path(__file__).parent / "retail2.db"


def get_inventory_hash(db_path):
    """Get a hash of inventory assignments including stock levels"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.store_name, p.sku, i.stock_level
        FROM inventory i
        JOIN stores s ON i.store_id = s.store_id
        JOIN products p ON i.product_id = p.product_id
        ORDER BY s.store_name, p.sku
    """)

    inventory_signature = []
    for store_name, sku, stock in cursor.fetchall():
        inventory_signature.append(f"{store_name}|{sku}|{stock}")

    conn.close()
    return "\n".join(inventory_signature)


print("=" * 70)
print("TEST: Reproducibility - Inventory Assignments")
print("=" * 70)

print("\n1. First generation already completed (retail.db)")
print("   Getting inventory signature...")
inv1_sig = get_inventory_hash(DB_FILE)
inv1_count = len(inv1_sig.split("\n"))
print(f"   Inventory records: {inv1_count}")

print("\n2. Generating second database (retail2.db)...")

# Remove existing DB2
if DB_FILE_2.exists():
    DB_FILE_2.unlink()

# Run generator with different output file
result = subprocess.run(
    [
        "bash",
        "-c",
        f"cd /workspace/new/app/data && PYTHONPATH=/workspace/new/app/data/src:/workspace/new/app/shared/src:$PYTHONPATH SQLITE_DB_FILE={DB_FILE_2} python3 src/zava_shop_datagenerator/__main__.py",
    ],
    capture_output=True,
    text=True,
)

if result.returncode != 0:
    print(f"   ❌ FAILED to generate second database")
    print(result.stderr)
    sys.exit(1)

print("   ✅ Second database generated")

print("\n3. Getting inventory signature from second database...")
inv2_sig = get_inventory_hash(DB_FILE_2)
inv2_count = len(inv2_sig.split("\n"))
print(f"   Inventory records: {inv2_count}")

print("\n4. Comparing inventory assignments...")
if inv1_sig == inv2_sig:
    print("   ✅ PASS: Inventory assignments are IDENTICAL")
    print("   Both databases have exactly the same store-product assignments")
    print("   This confirms reproducibility!")
else:
    # Find differences
    inv1_lines = set(inv1_sig.split("\n"))
    inv2_lines = set(inv2_sig.split("\n"))

    only_in_1 = inv1_lines - inv2_lines
    only_in_2 = inv2_lines - inv1_lines

    print(f"   ❌ FAIL: Inventory assignments DIFFER")
    print(f"   Only in DB1: {len(only_in_1)} records")
    print(f"   Only in DB2: {len(only_in_2)} records")

    if only_in_1:
        print(f"\n   First 5 differences in DB1:")
        for line in list(only_in_1)[:5]:
            print(f"     {line}")

    if only_in_2:
        print(f"\n   First 5 differences in DB2:")
        for line in list(only_in_2)[:5]:
            print(f"     {line}")

print("\n" + "=" * 70)
print("Note: Stock levels will differ (random 5-50), but SKU assignments")
print("      should be identical based on stores_reference.json")
print("=" * 70)
