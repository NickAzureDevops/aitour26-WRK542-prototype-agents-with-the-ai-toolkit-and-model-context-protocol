"""
Customer Sales Database Generator for SQLite with sqlite-vec

This script generates a comprehensive customer sales database with vector embeddings
support for SQLite using sqlite-vec extension.

DATA FILE STRUCTURE:
- product_data.json: Contains all product information (main_categories with products)
- reference_data.json: Contains store configurations (weights, year weights)

SQLITE FEATURES:
- Complete database generation with customers, products, stores, orders
- Product description embeddings population from product_data.json
- Vector similarity search with sqlite-vec extension
- Performance-optimized indexes

USAGE:
    python generate_zava_sqlite.py                     # Generate complete database
    python generate_zava_sqlite.py --show-stats        # Show database statistics
    python generate_zava_sqlite.py --embeddings-only   # Populate embeddings only
    python generate_zava_sqlite.py --help              # Show all options
"""

import argparse
import json
import logging
import os
import random
import sqlite3
import sys
from datetime import date
from typing import Dict, List, Optional, Tuple

from faker import Faker

# Initialize Faker and logging
fake = Faker()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# SQLite database path
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "zava.db")

# Super Manager UUID - has access to all rows
SUPER_MANAGER_UUID = "00000000-0000-0000-0000-000000000000"


def load_reference_data():
    """Load reference data from JSON file"""
    try:
        json_path = os.path.join(os.path.dirname(__file__), "reference_data.json")
        with open(json_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load reference data: {e}")
        raise


def load_product_data():
    """Load product data from JSON file"""
    try:
        json_path = os.path.join(os.path.dirname(__file__), "product_data.json")
        with open(json_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load product data: {e}")
        raise


# Load the reference data
reference_data = load_reference_data()
product_data = load_product_data()

# Get reference data from loaded JSON
main_categories = product_data["main_categories"]
stores = reference_data["stores"]


def weighted_store_choice():
    """Choose a store based on weighted distribution"""
    store_names = list(stores.keys())
    weights = [stores[store]["customer_distribution_weight"] for store in store_names]
    return random.choices(store_names, weights=weights, k=1)[0]


def generate_phone_number(region=None):
    """Generate a phone number in North American format (XXX) XXX-XXXX"""
    return f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"


def create_connection():
    """Create SQLite connection (pure Python - no extensions needed)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        logging.info(f"Connected to SQLite at {DB_PATH}")
        logging.info("Using pure Python vector similarity (no extensions required)")
        return conn
    except Exception as e:
        logging.error(f"Failed to connect to SQLite: {e}")
        raise


def create_database_schema(conn):
    """Create database schema and tables"""
    try:
        cursor = conn.cursor()

        # Create stores table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stores (
                store_id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_name TEXT UNIQUE NOT NULL,
                rls_user_id TEXT NOT NULL,
                is_online INTEGER NOT NULL DEFAULT 0
            )
        """)

        # Create customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                primary_store_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (primary_store_id) REFERENCES stores (store_id)
            )
        """)

        # Create categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT NOT NULL UNIQUE
            )
        """)

        # Create product_types table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_types (
                type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                type_name TEXT NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories (category_id)
            )
        """)

        # Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT UNIQUE NOT NULL,
                product_name TEXT NOT NULL,
                category_id INTEGER NOT NULL,
                type_id INTEGER NOT NULL,
                cost REAL NOT NULL,
                base_price REAL NOT NULL,
                gross_margin_percent REAL DEFAULT 33.00,
                product_description TEXT NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories (category_id),
                FOREIGN KEY (type_id) REFERENCES product_types (type_id)
            )
        """)

        # Create inventory table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                store_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                stock_level INTEGER NOT NULL,
                PRIMARY KEY (store_id, product_id),
                FOREIGN KEY (store_id) REFERENCES stores (store_id),
                FOREIGN KEY (product_id) REFERENCES products (product_id)
            )
        """)

        # Create orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                store_id INTEGER NOT NULL,
                order_date DATE NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
                FOREIGN KEY (store_id) REFERENCES stores (store_id)
            )
        """)

        # Create order_items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                store_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                discount_percent INTEGER DEFAULT 0,
                discount_amount REAL DEFAULT 0,
                total_amount REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders (order_id),
                FOREIGN KEY (store_id) REFERENCES stores (store_id),
                FOREIGN KEY (product_id) REFERENCES products (product_id)
            )
        """)

        # Create product_description_embeddings table (stores embeddings as JSON)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_description_embeddings (
                product_id INTEGER PRIMARY KEY,
                description_embedding TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (product_id)
            )
        """)

        # Create indexes
        logging.info("Creating performance indexes...")

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_customers_primary_store ON customers(primary_store_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_type ON products(type_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_store ON orders(store_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_store ON inventory(store_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_product ON inventory(product_id)")

        conn.commit()
        logging.info("Database schema created successfully!")

    except Exception as e:
        logging.error(f"Error creating database schema: {e}")
        raise


def insert_stores(conn):
    """Insert store data into the database"""
    try:
        cursor = conn.cursor()
        stores_data = []

        for store_name, store_config in stores.items():
            is_online = 1 if "online" in store_name.lower() else 0
            rls_user_id = store_config.get("rls_user_id")
            if not rls_user_id:
                raise ValueError(f"No rls_user_id found for store: {store_name}")
            stores_data.append((store_name, rls_user_id, is_online))

        cursor.executemany("INSERT INTO stores (store_name, rls_user_id, is_online) VALUES (?, ?, ?)", stores_data)
        conn.commit()

        logging.info(f"Successfully inserted {len(stores_data)} stores!")
    except Exception as e:
        logging.error(f"Error inserting stores: {e}")
        raise


def insert_customers(conn, num_customers: int = 100000):
    """Insert customer data into the database"""
    try:
        cursor = conn.cursor()
        logging.info(f"Generating {num_customers:,} customers...")

        # Get store IDs
        cursor.execute("SELECT store_id, store_name FROM stores")
        store_rows = cursor.fetchall()

        customers_data = []
        batch_size = 1000

        for i in range(1, num_customers + 1):
            first_name = fake.first_name().replace("'", "''")
            last_name = fake.last_name().replace("'", "''")
            email = f"{first_name.lower()}.{last_name.lower()}.{i}@example.com"
            phone = generate_phone_number()

            # Assign customer to a store
            preferred_store_name = weighted_store_choice()
            primary_store_id = None
            for store_id, store_name in store_rows:
                if store_name == preferred_store_name:
                    primary_store_id = store_id
                    break

            customers_data.append((first_name, last_name, email, phone, primary_store_id))

            # Batch insert
            if len(customers_data) >= batch_size:
                cursor.executemany(
                    "INSERT INTO customers (first_name, last_name, email, phone, primary_store_id) VALUES (?, ?, ?, ?, ?)",
                    customers_data,
                )
                customers_data = []
                if i % 10000 == 0:
                    logging.info(f"Processed {i:,} customers")

        # Insert remaining
        if customers_data:
            cursor.executemany(
                "INSERT INTO customers (first_name, last_name, email, phone, primary_store_id) VALUES (?, ?, ?, ?, ?)",
                customers_data,
            )

        conn.commit()
        logging.info(f"Successfully inserted {num_customers:,} customers!")

    except Exception as e:
        logging.error(f"Error inserting customers: {e}")
        raise


def insert_categories(conn):
    """Insert category data into the database"""
    try:
        cursor = conn.cursor()
        categories_data = [(category,) for category in main_categories.keys()]

        cursor.executemany("INSERT INTO categories (category_name) VALUES (?)", categories_data)
        conn.commit()

        logging.info(f"Successfully inserted {len(categories_data)} categories!")
    except Exception as e:
        logging.error(f"Error inserting categories: {e}")
        raise


def insert_product_types(conn):
    """Insert product type data into the database"""
    try:
        cursor = conn.cursor()

        # Get category mapping
        cursor.execute("SELECT category_id, category_name FROM categories")
        category_mapping = {name: id for id, name in cursor.fetchall()}

        product_types_data = []
        for main_category, subcategories in main_categories.items():
            category_id = category_mapping[main_category]
            for subcategory in subcategories.keys():
                if subcategory == "washington_seasonal_multipliers":
                    continue
                product_types_data.append((category_id, subcategory))

        cursor.executemany("INSERT INTO product_types (category_id, type_name) VALUES (?, ?)", product_types_data)
        conn.commit()

        logging.info(f"Successfully inserted {len(product_types_data)} product types!")
    except Exception as e:
        logging.error(f"Error inserting product types: {e}")
        raise


def insert_products(conn):
    """Insert product data into the database"""
    try:
        cursor = conn.cursor()

        # Get mappings
        cursor.execute("SELECT category_id, category_name FROM categories")
        category_mapping = {name: id for id, name in cursor.fetchall()}

        cursor.execute("SELECT type_id, type_name, category_id FROM product_types")
        type_mapping = {(cat_id, name): type_id for type_id, name, cat_id in cursor.fetchall()}

        products_data = []

        for main_category, subcategories in main_categories.items():
            category_id = category_mapping[main_category]

            for subcategory, product_list in subcategories.items():
                if subcategory == "washington_seasonal_multipliers" or not product_list:
                    continue

                type_id = type_mapping.get((category_id, subcategory))
                if not type_id:
                    continue

                for product_details in product_list:
                    product_name = product_details["name"]
                    sku = product_details.get("sku", f"SKU{len(products_data) + 1:06d}")
                    cost = float(product_details["price"])
                    base_price = round(cost / 0.67, 2)
                    description = product_details["description"]

                    products_data.append((sku, product_name, category_id, type_id, cost, base_price, description))

        cursor.executemany(
            "INSERT INTO products (sku, product_name, category_id, type_id, cost, base_price, product_description) VALUES (?, ?, ?, ?, ?, ?, ?)",
            products_data,
        )
        conn.commit()

        logging.info(f"Successfully inserted {len(products_data)} products!")
        return len(products_data)

    except Exception as e:
        logging.error(f"Error inserting products: {e}")
        raise


def populate_product_description_embeddings(conn, clear_existing: bool = False):
    """Populate product description embeddings from product_data.json"""
    try:
        cursor = conn.cursor()

        if clear_existing:
            cursor.execute("DELETE FROM product_description_embeddings")
            conn.commit()

        # Extract products with embeddings
        products_with_embeddings = []
        for category_data in main_categories.values():
            for product_type, products in category_data.items():
                if not isinstance(products, list):
                    continue
                for product in products:
                    if isinstance(product, dict):
                        sku = product.get("sku")
                        description_embedding = product.get("description_embedding")
                        if sku and description_embedding:
                            products_with_embeddings.append((sku, description_embedding))

        logging.info(f"Found {len(products_with_embeddings)} products with description embeddings")

        inserted_count = 0
        skipped_count = 0

        for sku, embedding in products_with_embeddings:
            # Get product_id
            cursor.execute("SELECT product_id FROM products WHERE sku = ?", (sku,))
            result = cursor.fetchone()

            if not result:
                skipped_count += 1
                continue

            product_id = result[0]

            # Insert embedding as JSON into the table
            embedding_json = json.dumps(embedding)
            cursor.execute(
                "INSERT INTO product_description_embeddings (product_id, description_embedding) VALUES (?, ?)",
                (product_id, embedding_json),
            )

            inserted_count += 1

        conn.commit()
        logging.info(f"Successfully inserted {inserted_count} description embeddings!")
        logging.info(f"Skipped {skipped_count} products (not found in database)")

    except Exception as e:
        logging.error(f"Error populating embeddings: {e}")
        raise


def get_yearly_weight(year):
    """Get the weight for each year"""
    return reference_data["year_weights"].get(str(year), 1.0)


def weighted_year_choice():
    """Choose a year based on growth pattern"""
    years = [2020, 2021, 2022, 2023, 2024, 2025, 2026]
    weights = [get_yearly_weight(year) for year in years]
    return random.choices(years, weights=weights, k=1)[0]


def insert_inventory(conn):
    """Insert inventory data"""
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT store_id FROM stores")
        store_ids = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT product_id FROM products")
        product_ids = [row[0] for row in cursor.fetchall()]

        inventory_data = []
        for store_id in store_ids:
            for product_id in product_ids:
                stock_level = random.randint(10, 200)
                inventory_data.append((store_id, product_id, stock_level))

        cursor.executemany("INSERT INTO inventory (store_id, product_id, stock_level) VALUES (?, ?, ?)", inventory_data)
        conn.commit()

        logging.info(f"Successfully inserted {len(inventory_data)} inventory records!")

    except Exception as e:
        logging.error(f"Error inserting inventory: {e}")
        raise


def insert_orders(conn, num_customers: int = 100000):
    """Insert order data"""
    try:
        cursor = conn.cursor()

        # Get product info
        cursor.execute("SELECT product_id, base_price FROM products")
        product_prices = {row[0]: row[1] for row in cursor.fetchall()}
        product_ids = list(product_prices.keys())

        # Get stores
        cursor.execute("SELECT store_id, store_name FROM stores")
        stores_list = cursor.fetchall()

        logging.info(f"Generating orders for {num_customers:,} customers...")

        orders_data = []
        order_items_data = []
        order_id = 1

        for customer_id in range(1, num_customers + 1):
            # Determine number of orders
            num_orders = random.choices([0, 1, 2, 3, 4, 5], weights=[20, 40, 20, 10, 7, 3], k=1)[0]

            for _ in range(num_orders):
                # Generate order
                preferred_store = weighted_store_choice()
                store_id = None
                for sid, sname in stores_list:
                    if sname == preferred_store:
                        store_id = sid
                        break

                year = weighted_year_choice()
                month = random.randint(1, 12)
                day = random.randint(1, 28)  # Safe day for all months
                order_date = date(year, month, day)

                orders_data.append((customer_id, store_id, order_date.isoformat()))

                # Generate order items
                num_items = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 15, 10, 5], k=1)[0]
                for _ in range(num_items):
                    product_id = random.choice(product_ids)
                    base_price = product_prices[product_id]
                    quantity = random.choices([1, 2, 3, 4, 5], weights=[60, 25, 10, 3, 2], k=1)[0]
                    unit_price = base_price * random.uniform(0.8, 1.2)

                    discount_percent = 0
                    discount_amount = 0
                    if random.random() < 0.15:
                        discount_percent = random.choice([5, 10, 15, 20, 25])
                        discount_amount = (unit_price * quantity * discount_percent) / 100

                    total_amount = (unit_price * quantity) - discount_amount

                    order_items_data.append(
                        (
                            order_id,
                            store_id,
                            product_id,
                            quantity,
                            unit_price,
                            discount_percent,
                            discount_amount,
                            total_amount,
                        )
                    )

                order_id += 1

            # Batch insert
            if customer_id % 1000 == 0:
                if orders_data:
                    cursor.executemany(
                        "INSERT INTO orders (customer_id, store_id, order_date) VALUES (?, ?, ?)", orders_data
                    )
                    orders_data = []

                if order_items_data:
                    cursor.executemany(
                        "INSERT INTO order_items (order_id, store_id, product_id, quantity, unit_price, discount_percent, discount_amount, total_amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        order_items_data,
                    )
                    order_items_data = []

                if customer_id % 10000 == 0:
                    logging.info(f"Processed {customer_id:,} customers")

        # Insert remaining
        if orders_data:
            cursor.executemany("INSERT INTO orders (customer_id, store_id, order_date) VALUES (?, ?, ?)", orders_data)
        if order_items_data:
            cursor.executemany(
                "INSERT INTO order_items (order_id, store_id, product_id, quantity, unit_price, discount_percent, discount_amount, total_amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                order_items_data,
            )

        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM order_items")
        total_items = cursor.fetchone()[0]

        logging.info(f"Successfully inserted {total_orders:,} orders!")
        logging.info(f"Successfully inserted {total_items:,} order items!")

    except Exception as e:
        logging.error(f"Error inserting orders: {e}")
        raise


def show_database_stats(conn):
    """Show database statistics"""
    cursor = conn.cursor()

    logging.info("\n" + "=" * 60)
    logging.info("DATABASE STATISTICS")
    logging.info("=" * 60)

    cursor.execute("SELECT COUNT(*) FROM customers")
    customers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products")
    products = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders")
    orders = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM order_items")
    order_items = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM product_description_embeddings")
    embeddings = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total_amount) FROM order_items")
    total_revenue = cursor.fetchone()[0] or 0

    logging.info(f"Customers: {customers:,}")
    logging.info(f"Products: {products:,}")
    logging.info(f"Product Embeddings: {embeddings:,}")
    logging.info(f"Orders: {orders:,}")
    logging.info(f"Order Items: {order_items:,}")
    logging.info(f"Total Revenue: ${total_revenue:,.2f}")

    if orders > 0:
        logging.info(f"Average Order Value: ${total_revenue / orders:.2f}")
        logging.info(f"Orders per Customer: {orders / customers:.1f}")
        logging.info(f"Items per Order: {order_items / orders:.1f}")


def generate_sqlite_database(num_customers: int = 50000):
    """Generate complete SQLite database"""
    try:
        # Remove existing database
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            logging.info("Removed existing database")

        conn = create_connection()

        try:
            create_database_schema(conn)
            insert_stores(conn)
            insert_categories(conn)
            insert_product_types(conn)
            insert_customers(conn, num_customers)
            insert_products(conn)

            logging.info("\n" + "=" * 50)
            logging.info("POPULATING PRODUCT EMBEDDINGS")
            logging.info("=" * 50)
            populate_product_description_embeddings(conn, clear_existing=True)

            logging.info("\n" + "=" * 50)
            logging.info("INSERTING INVENTORY DATA")
            logging.info("=" * 50)
            insert_inventory(conn)

            logging.info("\n" + "=" * 50)
            logging.info("INSERTING ORDER DATA")
            logging.info("=" * 50)
            insert_orders(conn, num_customers)

            logging.info("\n" + "=" * 50)
            logging.info("FINAL DATABASE VERIFICATION")
            logging.info("=" * 50)
            show_database_stats(conn)

            logging.info("\n" + "=" * 50)
            logging.info("DATABASE GENERATION COMPLETE")
            logging.info("=" * 50)
            logging.info(f"Database created at: {DB_PATH}")

        finally:
            conn.close()

    except Exception as e:
        logging.error(f"Failed to generate database: {e}")
        raise


def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(description="Generate SQLite database with product embeddings")
    parser.add_argument("--show-stats", action="store_true", help="Show database statistics instead of generating")
    parser.add_argument(
        "--embeddings-only", action="store_true", help="Only populate product embeddings (database must already exist)"
    )
    parser.add_argument(
        "--num-customers", type=int, default=50000, help="Number of customers to generate (default: 50000)"
    )

    args = parser.parse_args()

    try:
        if args.show_stats:
            if not os.path.exists(DB_PATH):
                logging.error(f"Database not found at {DB_PATH}")
                sys.exit(1)
            conn = create_connection()
            try:
                show_database_stats(conn)
            finally:
                conn.close()
        elif args.embeddings_only:
            if not os.path.exists(DB_PATH):
                logging.error(f"Database not found at {DB_PATH}")
                sys.exit(1)
            conn = create_connection()
            try:
                populate_product_description_embeddings(conn, clear_existing=True)
            finally:
                conn.close()
        else:
            generate_sqlite_database(num_customers=args.num_customers)
            logging.info(f"\nTo view statistics: python {sys.argv[0]} --show-stats")

    except Exception as e:
        logging.error(f"Failed to complete operation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Check if required packages are available
    try:
        from faker import Faker
    except ImportError as e:
        logging.error(f"Required library not found: {e}")
        logging.error("Please install required packages")
        sys.exit(1)

    main()
