"""
Zava DIY Customer Sales Database Generator for SQLite using SQLAlchemy ORM

This script generates a comprehensive DIY hardware sales database with optimized indexing
for SQLite using SQLAlchemy ORM models.

DATA FILE STRUCTURE (all in ../../data_reference/ folder):
- stores_reference.json: Consolidated store configurations and product assignments
- product_data.json: Contains all DIY/hardware product information with embeddings and supplier_id
- supplier_data.json: Contains supplier information for DIY/hardware vendors

SQLITE CONNECTION:
- Uses SQLAlchemy ORM (declarative models)
- Creates or connects to retail.db SQLite database file
- All tables in default SQLite schema

FEATURES:
- Complete database generation with customers, products, stores, orders
- Product image embeddings stored as JSON strings
- Product description embeddings stored as JSON strings
- Performance-optimized indexes
- Reproducible store product assignments (via stores_reference.json)
- Supplier relationships from product_data.json
- NO seasonal variations

USAGE:
    uv run python -m zava_shop_datagenerator                    # Generate complete database
    uv run python -m zava_shop_datagenerator --show-stats       # Show database statistics
    uv run python -m zava_shop_datagenerator --num-customers 10000  # Set customer count
    uv run python -m zava_shop_datagenerator --num-orders 100000    # Set order count
"""

import argparse
import json
import logging
import os
import random
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import List

from faker import Faker
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session, sessionmaker
from zava_shop_shared.models.sqlite import (
    Approver,
    Base,
    Category,
    CompanyPolicy,
    Customer,
    Inventory,
    Order,
    OrderItem,
    Product,
    ProductDescriptionEmbedding,
    ProductImageEmbedding,
    ProductType,
    Store,
    Supplier,
    SupplierContract,
    SupplierPerformance,
)

# Initialize Faker and logging
fake = Faker()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Reference data directory (relative to this file)
REFERENCE_DATA_DIR = Path(__file__).parent.parent.parent / "data_reference"

# Reference data files
STORES_REFERENCE_FILE = "stores_reference.json"
PRODUCT_DATA_FILE = "product_data.json"
SUPPLIER_DATA_FILE = "supplier_data.json"

# SQLite configuration
SQLITE_DB_FILE = os.getenv("SQLITE_DB_FILE", str(Path(__file__).parent.parent.parent / "retail.db"))

# Super Manager UUID - has access to all rows
SUPER_MANAGER_UUID = "00000000-0000-0000-0000-000000000000"


def load_stores_reference():
    """Load stores reference data from JSON file"""
    try:
        filepath = REFERENCE_DATA_DIR / STORES_REFERENCE_FILE
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load {STORES_REFERENCE_FILE}: {e}")
        raise


def load_product_data():
    """Load product data from JSON file"""
    try:
        filepath = REFERENCE_DATA_DIR / PRODUCT_DATA_FILE
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load {PRODUCT_DATA_FILE}: {e}")
        raise


def load_supplier_data():
    """Load supplier data from JSON file"""
    try:
        filepath = REFERENCE_DATA_DIR / SUPPLIER_DATA_FILE
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load {SUPPLIER_DATA_FILE}: {e}")
        raise


# Load the reference data
stores_reference = load_stores_reference()
product_data = load_product_data()
supplier_data = load_supplier_data()

# Extract stores and products
stores = stores_reference["stores"]
products_list = product_data["products"]


def weighted_store_choice():
    """Choose a store based on weighted distribution"""
    store_ids = list(stores.keys())
    weights = [stores[store]["customer_distribution_weight"] for store in store_ids]
    selected_id = random.choices(store_ids, weights=weights, k=1)[0]
    return stores[selected_id]["store_name"]


def generate_phone_number():
    """Generate a phone number in North American format (XXX) XXX-XXXX"""
    return f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"


def create_engine_and_session():
    """Create SQLAlchemy engine and session"""
    try:
        db_url = f"sqlite:///{SQLITE_DB_FILE}"
        engine = create_engine(db_url, echo=False)
        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        logging.info(f"Connected to SQLite database: {SQLITE_DB_FILE}")
        return engine, SessionLocal
    except Exception as e:
        logging.error(f"Failed to connect to SQLite: {e}")
        raise


def create_database_schema(engine):
    """Create database schema using SQLAlchemy models"""
    try:
        logging.info("Creating database schema from SQLAlchemy models...")
        Base.metadata.create_all(engine)
        logging.info("Database schema created successfully!")
    except Exception as e:
        logging.error(f"Error creating database schema: {e}")
        raise


def bulk_insert_objects(session: Session, objects: List, batch_size: int = 1000):
    """Insert objects in batches using SQLAlchemy bulk operations"""
    try:
        for i in range(0, len(objects), batch_size):
            batch = objects[i : i + batch_size]
            session.bulk_save_objects(batch)
            session.flush()
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def insert_stores(session: Session):
    """Insert store data into the database"""
    try:
        logging.info("Generating stores...")
        store_objects = []

        for store_id, store_config in stores.items():
            store_name = store_config["store_name"]
            is_online = store_config["location"]["is_online"]
            rls_user_id = store_config["rls_user_id"]

            if not rls_user_id:
                raise ValueError(f"No rls_user_id found for store: {store_name}")

            store_objects.append(Store(store_name=store_name, rls_user_id=rls_user_id, is_online=is_online))

        bulk_insert_objects(session, store_objects)

        stores_in_db = session.query(Store).order_by(Store.store_name).all()
        logging.info("Store Manager IDs (for RLS):")
        for store in stores_in_db:
            logging.info(f"  {store.store_name}: {store.rls_user_id}")

        logging.info(f"Successfully inserted {len(store_objects):,} stores!")
    except Exception as e:
        logging.error(f"Error inserting stores: {e}")
        raise


def insert_categories(session: Session):
    """Insert category data from products"""
    try:
        logging.info("Generating categories...")

        # Get unique categories from products
        categories = set(product["category"] for product in products_list)
        category_objects = [Category(category_name=cat) for cat in sorted(categories)]

        bulk_insert_objects(session, category_objects)
        logging.info(f"Successfully inserted {len(category_objects):,} categories!")
    except Exception as e:
        logging.error(f"Error inserting categories: {e}")
        raise


def insert_product_types(session: Session):
    """Insert product type data from products"""
    try:
        logging.info("Generating product types...")

        # Get category mapping
        categories_in_db = session.query(Category).all()
        category_mapping = {cat.category_name: cat.category_id for cat in categories_in_db}

        # Get unique category/subcategory combinations
        type_set = set()
        for product in products_list:
            type_set.add((product["category"], product["subcategory"]))

        product_type_objects = []
        for category, subcategory in sorted(type_set):
            category_id = category_mapping[category]
            product_type_objects.append(ProductType(category_id=category_id, type_name=subcategory))

        bulk_insert_objects(session, product_type_objects)
        logging.info(f"Successfully inserted {len(product_type_objects):,} product types!")
    except Exception as e:
        logging.error(f"Error inserting product types: {e}")
        raise


def insert_suppliers(session: Session):
    """Insert supplier data from JSON file"""
    try:
        logging.info(f"Loading suppliers from {SUPPLIER_DATA_FILE}...")

        supplier_objects = []
        for supplier_id_str, supplier in supplier_data.items():
            supplier_id = supplier["supplier_id"]

            # Get contract data if available
            payment_terms = supplier.get("payment_terms", "Net 30")
            if "contracts" in supplier and len(supplier["contracts"]) > 0:
                payment_terms = supplier["contracts"][0].get("payment_terms", payment_terms)

            supplier_objects.append(
                Supplier(
                    supplier_id=supplier_id,
                    supplier_name=supplier["supplier_name"],
                    supplier_code=supplier["supplier_code"],
                    contact_email=supplier["contact_email"],
                    contact_phone=supplier["contact_phone"],
                    address_line1="",
                    address_line2="",
                    city="Seattle",
                    state_province="WA",
                    postal_code="98000",
                    country="USA",
                    payment_terms=payment_terms,
                    lead_time_days=supplier["lead_time_days"],
                    minimum_order_amount=supplier["min_order_amount"],
                    bulk_discount_threshold=supplier["min_order_amount"] * 5,
                    bulk_discount_percent=supplier.get("bulk_discount_percent", 7.5),
                    supplier_rating=supplier["rating"],
                    esg_compliant=supplier["esg_compliant"],
                    approved_vendor=supplier["approved_vendor"],
                    preferred_vendor=supplier["preferred_vendor"],
                )
            )

        bulk_insert_objects(session, supplier_objects)
        logging.info(f"Successfully inserted {len(supplier_objects):,} suppliers!")

        # Insert supplier contracts
        logging.info("Generating supplier contracts...")
        contract_objects = []
        for supplier_id_str, supplier in supplier_data.items():
            if "contracts" in supplier:
                for contract in supplier["contracts"]:
                    contract_objects.append(
                        SupplierContract(
                            supplier_id=supplier["supplier_id"],
                            contract_number=contract["contract_number"],
                            contract_status=contract["contract_status"],
                            start_date=date.fromisoformat(contract["start_date"]),
                            end_date=date.fromisoformat(contract["end_date"]),
                            contract_value=contract["contract_value"],
                            payment_terms=contract["payment_terms"],
                            auto_renew=contract["auto_renew"],
                        )
                    )

        if contract_objects:
            bulk_insert_objects(session, contract_objects)
            logging.info(f"Successfully inserted {len(contract_objects):,} supplier contracts!")

        # Insert supplier performance data
        logging.info("Generating supplier performance evaluations...")
        suppliers_in_db = session.query(Supplier).all()
        performance_objects = []

        for supplier_obj in suppliers_in_db:
            for months_ago in range(0, random.randint(3, 7)):
                evaluation_date = date.today().replace(day=1) - timedelta(days=months_ago * 30)

                base_cost_score = random.uniform(3.5, 4.8)
                base_quality_score = random.uniform(3.2, 4.9)
                base_delivery_score = random.uniform(3.0, 4.7)
                base_compliance_score = random.uniform(4.2, 5.0)

                cost_score = max(1.0, min(5.0, base_cost_score + random.uniform(-0.3, 0.3)))
                quality_score = max(1.0, min(5.0, base_quality_score + random.uniform(-0.4, 0.4)))
                delivery_score = max(1.0, min(5.0, base_delivery_score + random.uniform(-0.5, 0.5)))
                compliance_score = max(1.0, min(5.0, base_compliance_score + random.uniform(-0.2, 0.2)))

                overall_score = cost_score * 0.3 + quality_score * 0.3 + delivery_score * 0.25 + compliance_score * 0.15

                performance_objects.append(
                    SupplierPerformance(
                        supplier_id=supplier_obj.supplier_id,
                        evaluation_date=evaluation_date,
                        cost_score=cost_score,
                        quality_score=quality_score,
                        delivery_score=delivery_score,
                        compliance_score=compliance_score,
                        overall_score=overall_score,
                        notes=f"Monthly evaluation for {supplier_obj.supplier_name}",
                    )
                )

        bulk_insert_objects(session, performance_objects)
        logging.info(f"Successfully inserted {len(performance_objects):,} supplier performance evaluations!")

    except Exception as e:
        logging.error(f"Error inserting suppliers: {e}")
        raise


def insert_products(session: Session):
    """Insert product data from JSON file"""
    try:
        logging.info("Generating products...")

        # Get mappings
        categories_in_db = session.query(Category).all()
        category_mapping = {cat.category_name: cat.category_id for cat in categories_in_db}

        product_types_in_db = session.query(ProductType).all()
        type_mapping = {}
        for pt in product_types_in_db:
            # Create key as (category_id, type_name)
            type_mapping[(pt.category_id, pt.type_name)] = pt.type_id

        # Get supplier lead times for products
        supplier_lead_times = {int(sid): supplier["lead_time_days"] for sid, supplier in supplier_data.items()}

        product_objects = []

        for product in products_list:
            category_id = category_mapping[product["category"]]
            type_id = type_mapping.get((category_id, product["subcategory"]))

            if not type_id:
                logging.warning(f"Could not find type_id for {product['category']}/{product['subcategory']}")
                continue

            # Use supplier_id from product data
            supplier_id = product["supplier_id"]

            # Use price from JSON as base_price (store selling price)
            base_price = float(product["price"])
            # Calculate cost for 33% gross margin: Cost = Price × 0.67
            cost = round(base_price * 0.67, 2)

            # Extract image_url from image_path
            image_path = product.get("image_path", "")
            image_url = image_path.replace("images/", "") if image_path else None

            # Get supplier's lead time for this product
            procurement_lead_time = supplier_lead_times.get(supplier_id, 15)

            product_objects.append(
                Product(
                    sku=product["sku"],
                    product_name=product["name"],
                    category_id=category_id,
                    type_id=type_id,
                    supplier_id=supplier_id,
                    cost=cost,
                    base_price=base_price,
                    gross_margin_percent=33.00,
                    product_description=product["description"],
                    procurement_lead_time_days=procurement_lead_time,
                    minimum_order_quantity=product.get("minimum_order_quantity", 10),
                    discontinued=False,
                    image_url=image_url,
                )
            )

        bulk_insert_objects(session, product_objects)
        logging.info(f"Successfully inserted {len(product_objects):,} products!")
    except Exception as e:
        logging.error(f"Error inserting products: {e}")
        raise


def populate_product_embeddings(session: Session):
    """Populate product embeddings from product_data.json as JSON strings"""
    try:
        logging.info("Populating product embeddings...")

        # Get product SKU to ID mapping
        products_in_db = session.query(Product).all()
        sku_to_id = {p.sku: p.product_id for p in products_in_db}

        image_embedding_objects = []
        description_embedding_objects = []

        for product in products_list:
            sku = product["sku"]
            product_id = sku_to_id.get(sku)

            if not product_id:
                continue

            # Store image embedding as JSON string
            if product.get("image_embedding"):
                embedding_json = json.dumps(product["image_embedding"])
                image_embedding_objects.append(
                    ProductImageEmbedding(product_id=product_id, image_embedding=embedding_json)
                )

            # Store description embedding as JSON string
            if product.get("description_embedding"):
                embedding_json = json.dumps(product["description_embedding"])
                description_embedding_objects.append(
                    ProductDescriptionEmbedding(product_id=product_id, description_embedding=embedding_json)
                )

        if image_embedding_objects:
            bulk_insert_objects(session, image_embedding_objects)
            logging.info(f"Successfully inserted {len(image_embedding_objects):,} image embeddings!")

        if description_embedding_objects:
            bulk_insert_objects(session, description_embedding_objects)
            logging.info(f"Successfully inserted {len(description_embedding_objects):,} description embeddings!")

    except Exception as e:
        logging.error(f"Error populating embeddings: {e}")
        raise


def insert_customers(session: Session, num_customers: int = 10000):
    """Insert customer data into the database"""
    try:
        logging.info(f"Generating {num_customers:,} customers...")

        stores_in_db = session.query(Store).all()
        store_name_to_id = {s.store_name: s.store_id for s in stores_in_db}

        if not stores_in_db:
            raise Exception("No stores found! Please insert stores first.")

        customer_objects = []

        for i in range(1, num_customers + 1):
            first_name = fake.first_name().replace("'", "")
            last_name = fake.last_name().replace("'", "")
            email = f"{first_name.lower()}.{last_name.lower()}.{i}@example.com"
            phone = generate_phone_number()

            preferred_store_name = weighted_store_choice()
            primary_store_id = store_name_to_id.get(preferred_store_name, stores_in_db[0].store_id)

            customer_objects.append(
                Customer(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=phone,
                    primary_store_id=primary_store_id,
                )
            )

        bulk_insert_objects(session, customer_objects)

        # Log customer distribution
        distribution = (
            session.query(Store.store_name, func.count(Customer.customer_id).label("customer_count"))
            .outerjoin(Customer, Store.store_id == Customer.primary_store_id)
            .group_by(Store.store_id, Store.store_name)
            .order_by(func.count(Customer.customer_id).desc())
            .all()
        )

        logging.info("Customer distribution by store:")
        for store_name, customer_count in distribution:
            percentage = (customer_count / num_customers * 100) if num_customers > 0 else 0
            logging.info(f"  {store_name}: {customer_count:,} customers ({percentage:.1f}%)")

        logging.info(f"Successfully inserted {num_customers:,} customers!")
    except Exception as e:
        logging.error(f"Error inserting customers: {e}")
        raise


def insert_inventory(session: Session):
    """Insert inventory based on store product assignments from stores_reference.json"""
    try:
        logging.info("Generating inventory from store product assignments...")

        stores_in_db = session.query(Store).all()
        store_name_to_id = {s.store_name: s.store_id for s in stores_in_db}

        products_in_db = session.query(Product).all()
        sku_to_product_id = {p.sku: p.product_id for p in products_in_db}

        # Create SKU to stock_level mapping from product_data.json
        sku_to_stock_level = {product["sku"]: product.get("stock_level", 25) for product in products_list}

        inventory_objects = []

        for store_id, store_config in stores.items():
            store_name = store_config["store_name"]
            db_store_id = store_name_to_id.get(store_name)

            if not db_store_id:
                continue

            # Get product SKUs for this store
            product_skus = store_config.get("product_skus", [])

            for sku in product_skus:
                product_id = sku_to_product_id.get(sku)
                if product_id:
                    # Use stock_level from product_data.json for reproducibility
                    stock_level = sku_to_stock_level.get(sku, 25)
                    inventory_objects.append(
                        Inventory(store_id=db_store_id, product_id=product_id, stock_level=stock_level)
                    )

        bulk_insert_objects(session, inventory_objects)
        logging.info(f"Successfully inserted {len(inventory_objects):,} inventory records!")

    except Exception as e:
        logging.error(f"Error inserting inventory: {e}")
        raise


def insert_orders_and_items(session: Session, num_orders: int = 100000):
    """Insert order and order item data (NO seasonal variations)"""
    try:
        logging.info(f"Generating {num_orders:,} orders...")

        # Get customers
        customer_ids = [c.customer_id for c in session.query(Customer.customer_id).all()]
        if not customer_ids:
            raise Exception("No customers found!")

        # Get stores
        stores_in_db = session.query(Store).all()
        store_ids = [s.store_id for s in stores_in_db]

        # Get products with prices
        products = session.query(Product.product_id, Product.base_price).all()
        product_list = [(p.product_id, p.base_price) for p in products]

        order_objects = []
        order_item_objects = []

        # Generate orders
        for i in range(num_orders):
            customer_id = random.choice(customer_ids)
            store_id = random.choice(store_ids)
            # Random date in last 2 years (NO seasonal variation)
            order_date = date.today() - timedelta(days=random.randint(0, 730))

            order = Order(customer_id=customer_id, store_id=store_id, order_date=order_date)
            order_objects.append(order)

        # Insert orders first to get IDs
        bulk_insert_objects(session, order_objects)

        # Get inserted order IDs
        order_ids = [
            o.order_id for o in session.query(Order.order_id).order_by(Order.order_id.desc()).limit(num_orders).all()
        ]
        order_ids.reverse()

        # Create order items
        logging.info("Generating order items...")
        for order_id in order_ids:
            store_id = random.choice(store_ids)

            # Add 1-5 items per order
            num_items = random.randint(1, 5)
            for _ in range(num_items):
                product_id, base_price = random.choice(product_list)
                quantity = random.randint(1, 10)
                unit_price = float(base_price)
                discount_percent = random.choice([0, 0, 0, 5, 10, 15])
                discount_amount = round((unit_price * quantity * discount_percent) / 100, 2)
                total_amount = round((unit_price * quantity) - discount_amount, 2)

                order_item_objects.append(
                    OrderItem(
                        order_id=order_id,
                        store_id=store_id,
                        product_id=product_id,
                        quantity=quantity,
                        unit_price=unit_price,
                        discount_percent=discount_percent,
                        discount_amount=discount_amount,
                        total_amount=total_amount,
                    )
                )

        bulk_insert_objects(session, order_item_objects)

        logging.info(f"Successfully inserted {len(order_objects):,} orders!")
        logging.info(f"Successfully inserted {len(order_item_objects):,} order items!")

    except Exception as e:
        logging.error(f"Error inserting orders: {e}")
        raise


def insert_agent_support_data(session: Session):
    """Insert minimal agent support data (approvers, policies, etc.)"""
    try:
        logging.info("Generating agent support data...")

        # Generate approvers
        approver_objects = [
            Approver(
                employee_id="EXEC001",
                full_name="Jane CEO",
                email="jane.ceo@zavadiy.com",
                department="Management",
                approval_limit=1000000,
                is_active=True,
            ),
            Approver(
                employee_id="DIR001",
                full_name="John Finance Director",
                email="john.director@zavadiy.com",
                department="Finance",
                approval_limit=250000,
                is_active=True,
            ),
            Approver(
                employee_id="MGR001",
                full_name="Mike Procurement Manager",
                email="mike.proc@zavadiy.com",
                department="Procurement",
                approval_limit=50000,
                is_active=True,
            ),
        ]

        bulk_insert_objects(session, approver_objects)

        # Generate company policies
        policy_objects = [
            CompanyPolicy(
                policy_name="Procurement Policy",
                policy_type="procurement",
                policy_content="All purchases over $5,000 require manager approval.",
                department="Procurement",
                minimum_order_threshold=5000,
                approval_required=True,
            ),
            CompanyPolicy(
                policy_name="Budget Authorization",
                policy_type="budget_authorization",
                policy_content="Spending limits: Manager $50K, Director $250K, Executive $1M+",
                department="Finance",
                approval_required=True,
            ),
        ]

        bulk_insert_objects(session, policy_objects)

        logging.info(f"Successfully inserted {len(approver_objects)} approvers!")
        logging.info(f"Successfully inserted {len(policy_objects)} company policies!")

    except Exception as e:
        logging.error(f"Error inserting agent support data: {e}")
        raise


def show_statistics(session: Session):
    """Display database statistics"""
    try:
        stats = {
            "stores": session.query(func.count(Store.store_id)).scalar(),
            "categories": session.query(func.count(Category.category_id)).scalar(),
            "product_types": session.query(func.count(ProductType.type_id)).scalar(),
            "products": session.query(func.count(Product.product_id)).scalar(),
            "suppliers": session.query(func.count(Supplier.supplier_id)).scalar(),
            "customers": session.query(func.count(Customer.customer_id)).scalar(),
            "orders": session.query(func.count(Order.order_id)).scalar(),
            "order_items": session.query(func.count(OrderItem.order_item_id)).scalar(),
            "inventory": session.query(func.count(Inventory.store_id)).scalar(),
            "image_embeddings": session.query(func.count(ProductImageEmbedding.product_id)).scalar(),
            "description_embeddings": session.query(func.count(ProductDescriptionEmbedding.product_id)).scalar(),
        }

        logging.info("=" * 70)
        logging.info("📊 ZAVA DIY DATABASE STATISTICS")
        logging.info("=" * 70)

        logging.info("\n📋 TABLE COUNTS:")
        logging.info("-" * 70)
        for table, count in stats.items():
            logging.info(f"  {table:.<45} {count:>15,}")

        # Revenue stats
        order_stats = session.query(
            func.sum(OrderItem.total_amount).label("total_revenue"),
            func.avg(OrderItem.total_amount).label("avg_item_value"),
        ).first()

        if order_stats.total_revenue:
            logging.info("\n💰 REVENUE STATISTICS:")
            logging.info("-" * 70)
            logging.info(f"  {'Total Revenue':.<45} ${float(order_stats.total_revenue):>14,.2f}")
            logging.info(f"  {'Average Item Value':.<45} ${float(order_stats.avg_item_value):>14,.2f}")

        logging.info("\n" + "=" * 70)

    except Exception as e:
        logging.error(f"Error retrieving statistics: {e}")


def main():
    """Main function to orchestrate database generation"""
    parser = argparse.ArgumentParser(description="Generate Zava DIY SQLite database")
    parser.add_argument("--show-stats", action="store_true", help="Show database statistics")
    parser.add_argument("--num-customers", type=int, default=10000, help="Number of customers (default: 10000)")
    parser.add_argument("--num-orders", type=int, default=100000, help="Number of orders (default: 100000)")

    args = parser.parse_args()

    try:
        engine, SessionLocal = create_engine_and_session()

        if args.show_stats:
            if not Path(SQLITE_DB_FILE).exists():
                logging.error(f"Database not found at {SQLITE_DB_FILE}")
                sys.exit(1)
            session = SessionLocal()
            try:
                show_statistics(session)
            finally:
                session.close()
            return

        logging.info("Starting Zava DIY database generation...")

        # Remove existing database
        if Path(SQLITE_DB_FILE).exists():
            Path(SQLITE_DB_FILE).unlink()
            logging.info("Removed existing database")

        # Create schema
        create_database_schema(engine)

        # Create session for data insertion
        session = SessionLocal()

        try:
            # Insert reference data
            insert_stores(session)
            insert_categories(session)
            insert_product_types(session)
            insert_suppliers(session)
            insert_products(session)
            populate_product_embeddings(session)

            # Insert transactional data
            insert_customers(session, num_customers=args.num_customers)
            insert_inventory(session)
            insert_orders_and_items(session, num_orders=args.num_orders)

            # Insert agent support data
            insert_agent_support_data(session)

            # Show statistics
            show_statistics(session)

            logging.info("\n✅ Zava DIY database generation completed successfully!")
            logging.info(f"Database location: {SQLITE_DB_FILE}")
            logging.info(f"\nTo view statistics: uv run python -m zava_shop_datagenerator --show-stats")

        finally:
            session.close()

    except Exception as e:
        logging.error(f"Fatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
