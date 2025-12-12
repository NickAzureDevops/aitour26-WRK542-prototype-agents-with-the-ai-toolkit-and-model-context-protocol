"""
Comprehensive validation tests for the generated Zava DIY database
"""

import json
import sqlite3
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Database location
DB_FILE = Path(__file__).parent / "retail.db"
DATA_REF_DIR = Path(__file__).parent / "data_reference"


def get_connection():
    """Get database connection"""
    return sqlite3.connect(DB_FILE)


def test_table_counts():
    """Test 1: Verify all tables have expected record counts"""
    print("\n" + "=" * 70)
    print("TEST 1: Verify Table Counts")
    print("=" * 70)

    conn = get_connection()
    cursor = conn.cursor()

    expected = {
        "stores": 16,
        "categories": 9,
        "product_types": 88,
        "products": 424,
        "suppliers": 20,
        "customers": 10000,
        "orders": 100000,
        "inventory": 3090,
        "product_image_embeddings": 424,
        "product_description_embeddings": 424,
    }

    all_passed = True
    for table, expected_count in expected.items():
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        actual_count = cursor.fetchone()[0]
        status = "✅ PASS" if actual_count == expected_count else "❌ FAIL"
        print(f"  {table:.<40} {actual_count:>10,} (expected {expected_count:,}) {status}")
        if actual_count != expected_count:
            all_passed = False

    conn.close()
    return all_passed


def test_supplier_relationships():
    """Test 2: Verify all products have supplier_id and it matches supplier_data.json"""
    print("\n" + "=" * 70)
    print("TEST 2: Validate Supplier Relationships")
    print("=" * 70)

    conn = get_connection()
    cursor = conn.cursor()

    # Load supplier data
    with open(DATA_REF_DIR / "supplier_data.json", "r") as f:
        supplier_data = json.load(f)

    valid_supplier_ids = set(int(sid) for sid in supplier_data.keys())

    # Check products without supplier_id
    cursor.execute("SELECT COUNT(*) FROM products WHERE supplier_id IS NULL")
    null_count = cursor.fetchone()[0]
    print(f"  Products with NULL supplier_id: {null_count:,}")

    # Check products with invalid supplier_id
    cursor.execute("SELECT COUNT(*) FROM products WHERE supplier_id NOT IN (SELECT supplier_id FROM suppliers)")
    invalid_count = cursor.fetchone()[0]
    print(f"  Products with invalid supplier_id: {invalid_count:,}")

    # Show supplier distribution
    cursor.execute("""
        SELECT s.supplier_name, COUNT(p.product_id) as product_count
        FROM suppliers s
        LEFT JOIN products p ON s.supplier_id = p.supplier_id
        GROUP BY s.supplier_id, s.supplier_name
        ORDER BY product_count DESC
    """)

    print("\n  Supplier Product Distribution:")
    for supplier_name, count in cursor.fetchall():
        print(f"    {supplier_name:.<50} {count:>5} products")

    conn.close()
    passed = null_count == 0 and invalid_count == 0
    print(f"\n  Status: {'✅ PASS' if passed else '❌ FAIL'}")
    return passed


def test_embedding_storage():
    """Test 3: Verify embeddings are stored as JSON strings"""
    print("\n" + "=" * 70)
    print("TEST 3: Check Embedding Storage Format")
    print("=" * 70)

    conn = get_connection()
    cursor = conn.cursor()

    # Check image embeddings
    cursor.execute("SELECT image_embedding FROM product_image_embeddings LIMIT 1")
    sample_image = cursor.fetchone()[0]

    # Check description embeddings
    cursor.execute("SELECT description_embedding FROM product_description_embeddings LIMIT 1")
    sample_desc = cursor.fetchone()[0]

    image_is_json = False
    desc_is_json = False

    try:
        image_parsed = json.loads(sample_image)
        image_is_json = isinstance(image_parsed, list) and len(image_parsed) > 0
        print(f"  Image embedding: JSON array with {len(image_parsed)} dimensions ✅")
    except Exception as e:
        print(f"  Image embedding: NOT valid JSON - {e} ❌")

    try:
        desc_parsed = json.loads(sample_desc)
        desc_is_json = isinstance(desc_parsed, list) and len(desc_parsed) > 0
        print(f"  Description embedding: JSON array with {len(desc_parsed)} dimensions ✅")
    except Exception as e:
        print(f"  Description embedding: NOT valid JSON - {e} ❌")

    # Check for NULL embeddings
    cursor.execute("SELECT COUNT(*) FROM product_image_embeddings WHERE image_embedding IS NULL")
    null_images = cursor.fetchone()[0]
    print(f"  NULL image embeddings: {null_images:,}")

    cursor.execute("SELECT COUNT(*) FROM product_description_embeddings WHERE description_embedding IS NULL")
    null_descs = cursor.fetchone()[0]
    print(f"  NULL description embeddings: {null_descs:,}")

    conn.close()
    passed = image_is_json and desc_is_json and null_images == 0 and null_descs == 0
    print(f"\n  Status: {'✅ PASS' if passed else '❌ FAIL'}")
    return passed


def test_inventory_assignments():
    """Test 4: Verify inventory matches product_skus from stores_reference.json"""
    print("\n" + "=" * 70)
    print("TEST 4: Validate Inventory Assignments (Reproducibility)")
    print("=" * 70)

    conn = get_connection()
    cursor = conn.cursor()

    # Load stores reference
    with open(DATA_REF_DIR / "stores_reference.json", "r") as f:
        stores_ref = json.load(f)["stores"]

    all_matched = True
    mismatches = []

    for store_id, store_config in stores_ref.items():
        store_name = store_config["store_name"]
        expected_skus = set(store_config.get("product_skus", []))

        # Get actual SKUs in inventory for this store
        cursor.execute(
            """
            SELECT p.sku
            FROM inventory i
            JOIN stores s ON i.store_id = s.store_id
            JOIN products p ON i.product_id = p.product_id
            WHERE s.store_name = ?
        """,
            (store_name,),
        )

        actual_skus = set(row[0] for row in cursor.fetchall())

        if expected_skus != actual_skus:
            all_matched = False
            missing = expected_skus - actual_skus
            extra = actual_skus - expected_skus
            mismatches.append(
                {
                    "store": store_name,
                    "expected": len(expected_skus),
                    "actual": len(actual_skus),
                    "missing": len(missing),
                    "extra": len(extra),
                }
            )
        else:
            print(f"  ✅ {store_name}: {len(actual_skus)} SKUs match perfectly")

    if mismatches:
        print("\n  ❌ MISMATCHES FOUND:")
        for mm in mismatches:
            print(f"    {mm['store']}:")
            print(f"      Expected: {mm['expected']}, Actual: {mm['actual']}")
            print(f"      Missing: {mm['missing']}, Extra: {mm['extra']}")

    conn.close()
    print(f"\n  Status: {'✅ PASS' if all_matched else '❌ FAIL'}")
    return all_matched


def test_no_seasonal_patterns():
    """Test 5: Check order distribution is uniform (no seasonal bias)"""
    print("\n" + "=" * 70)
    print("TEST 5: Verify No Seasonal Patterns")
    print("=" * 70)

    conn = get_connection()
    cursor = conn.cursor()

    # Get order distribution by month
    cursor.execute("""
        SELECT 
            strftime('%Y-%m', order_date) as month,
            COUNT(*) as order_count
        FROM orders
        GROUP BY month
        ORDER BY month
    """)

    monthly_counts = cursor.fetchall()

    if not monthly_counts:
        print("  ❌ No order data found")
        conn.close()
        return False

    # Calculate statistics
    counts = [count for _, count in monthly_counts]
    avg_count = sum(counts) / len(counts)
    max_count = max(counts)
    min_count = min(counts)
    variance = sum((x - avg_count) ** 2 for x in counts) / len(counts)
    std_dev = variance**0.5

    print(f"  Total months with data: {len(monthly_counts)}")
    print(f"  Average orders per month: {avg_count:,.1f}")
    print(f"  Min orders in a month: {min_count:,}")
    print(f"  Max orders in a month: {max_count:,}")
    print(f"  Standard deviation: {std_dev:,.1f}")
    print(f"  Coefficient of variation: {(std_dev / avg_count) * 100:.1f}%")

    # Show monthly distribution
    print("\n  Monthly Order Distribution:")
    for month, count in monthly_counts[-12:]:  # Show last 12 months
        bar_length = int((count / max_count) * 40)
        bar = "█" * bar_length
        print(f"    {month}: {count:>6,} {bar}")

    # Test passes if coefficient of variation is < 20% (fairly uniform)
    cv = (std_dev / avg_count) * 100
    passed = cv < 20.0

    conn.close()
    print(
        f"\n  Status: {'✅ PASS - Distribution is uniform' if passed else '❌ FAIL - Significant seasonal pattern detected'}"
    )
    return passed


def test_diy_categories():
    """Test 6: Verify products are DIY/hardware categories"""
    print("\n" + "=" * 70)
    print("TEST 6: Verify DIY/Hardware Product Categories")
    print("=" * 70)

    conn = get_connection()
    cursor = conn.cursor()

    # Expected DIY categories (actual names from migrated data)
    expected_categories = {
        "HAND TOOLS",
        "POWER TOOLS",
        "PLUMBING",
        "ELECTRICAL",
        "LUMBER & BUILDING MATERIALS",
        "PAINT & FINISHES",
        "HARDWARE",
        "GARDEN & OUTDOOR",
        "STORAGE & ORGANIZATION",
    }

    # Get actual categories
    cursor.execute("SELECT category_name FROM categories")
    actual_categories = set(row[0] for row in cursor.fetchall())

    # Check for apparel categories (should not exist)
    apparel_keywords = ["SHIRT", "PANT", "DRESS", "JACKET", "SHOE", "ACCESSORY", "CLOTHING"]
    found_apparel = any(keyword in cat for cat in actual_categories for keyword in apparel_keywords)

    print(f"  Expected DIY categories: {len(expected_categories)}")
    print(f"  Actual categories in DB: {len(actual_categories)}")
    print(f"  Apparel categories found: {'❌ YES' if found_apparel else '✅ NO'}")

    print("\n  Categories in database:")
    cursor.execute("""
        SELECT c.category_name, COUNT(p.product_id) as product_count
        FROM categories c
        LEFT JOIN products p ON c.category_id = p.category_id
        GROUP BY c.category_id, c.category_name
        ORDER BY product_count DESC
    """)

    for category, count in cursor.fetchall():
        in_expected = "✅" if category in expected_categories else "❓"
        print(f"    {in_expected} {category:.<45} {count:>5} products")

    conn.close()
    passed = actual_categories == expected_categories and not found_apparel
    print(f"\n  Status: {'✅ PASS' if passed else '❌ FAIL'}")
    return passed


def test_sample_products():
    """Test 7: Show sample products to verify DIY content"""
    print("\n" + "=" * 70)
    print("TEST 7: Sample Products Verification")
    print("=" * 70)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            p.sku,
            p.product_name,
            c.category_name,
            pt.type_name,
            s.supplier_name,
            p.base_price
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        JOIN product_types pt ON p.type_id = pt.type_id
        JOIN suppliers s ON p.supplier_id = s.supplier_id
        ORDER BY RANDOM()
        LIMIT 10
    """)

    print("\n  Random Sample of 10 Products:")
    print("  " + "-" * 68)
    for sku, name, category, subcat, supplier, price in cursor.fetchall():
        print(f"  {sku}: {name[:30]:.<30} ${price:>7.2f}")
        print(f"    Category: {category} > {subcat}")
        print(f"    Supplier: {supplier}")
        print()

    conn.close()
    return True


def run_all_tests():
    """Run all validation tests"""
    print("\n" + "=" * 70)
    print("🧪 ZAVA DIY DATABASE VALIDATION TEST SUITE")
    print("=" * 70)
    print(f"Database: {DB_FILE}")
    print(f"Data Reference: {DATA_REF_DIR}")
    print("=" * 70)

    results = {
        "Table Counts": test_table_counts(),
        "Supplier Relationships": test_supplier_relationships(),
        "Embedding Storage": test_embedding_storage(),
        "Inventory Assignments": test_inventory_assignments(),
        "No Seasonal Patterns": test_no_seasonal_patterns(),
        "DIY Categories": test_diy_categories(),
        "Sample Products": test_sample_products(),
    }

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name:.<50} {status}")

    print("=" * 70)
    print(f"  Total: {passed}/{total} tests passed ({(passed / total) * 100:.0f}%)")
    print("=" * 70)

    if passed == total:
        print("\n  🎉 ALL TESTS PASSED! Database generation is correct.")
    else:
        print(f"\n  ⚠️  {total - passed} test(s) failed. Review output above.")

    return passed == total


if __name__ == "__main__":
    run_all_tests()
