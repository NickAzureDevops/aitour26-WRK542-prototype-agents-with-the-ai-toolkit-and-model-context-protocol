#!/usr/bin/env python3
"""
Inventory Agent MCP Server for Zava Retail

This MCP server provides inventory management tools:
1. Get stock levels by SKU across all stores
2. Transfer stock between stores

Uses SQLite database with read-write access for inventory transfers.
"""

from opentelemetry.instrumentation.auto_instrumentation import initialize

initialize()
import logging
import os
from contextlib import asynccontextmanager
from typing import Annotated, AsyncIterator

from fastmcp import FastMCP
from opentelemetry.instrumentation.mcp import McpInstrumentor
from pydantic import Field
from sqlalchemy import and_, select, update
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from zava_shop_shared.inventory_sqlite import InventorySQLiteProvider
from zava_shop_shared.models.sqlite import Inventory, Product, Store

McpInstrumentor().instrument()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

db: InventorySQLiteProvider = InventorySQLiteProvider()


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator:
    # Initialize database connection once at startup
    await db.open_engine()
    logger.info("Database connection initialized")
    yield
    await db.close_engine()


# Initialize FastMCP server
mcp = FastMCP("Zava Inventory Agent MCP Server", lifespan=app_lifespan)


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> Response:
    return JSONResponse({"status": "ok"})


@mcp.tool()
async def get_stock_level_by_product_id(
    product_id: Annotated[int, Field(description="Product ID to check stock levels for")],
    is_online: Annotated[
        bool | None,
        Field(
            description="Optional filter: True for online stores only, False for physical stores only, or omit for all stores"
        ),
    ] = None,
) -> list[dict]:
    """
    Get stock levels for a product by product ID across all stores.

    **USAGE:** Use this to check availability. This tool returns `store_id`s which are REQUIRED if you need to perform a `transfer_stock` operation later.

    Args:
        product_id: Product ID (e.g., 123). If the user provides a product name, use `semantic_search_products` first to find the product ID.
        is_online: Optional filter - True for online stores, False for physical stores, or None for all stores (default).

    Returns:
        List of inventory records including 'store_id', 'product_id', 'stock_level', 'store_name', 'is_online', 'product_name', and 'sku'.
    """
    try:
        logger.info(f"Getting stock levels for product ID: {product_id}, is_online filter: {is_online}")

        async with db.get_session() as session:
            # Query inventory with store and product information
            stmt = (
                select(
                    Inventory.store_id,
                    Inventory.product_id,
                    Inventory.stock_level,
                    Store.store_name,
                    Store.is_online,
                    Product.product_name,
                    Product.sku,
                )
                .join(Store, Inventory.store_id == Store.store_id)
                .join(Product, Inventory.product_id == Product.product_id)
                .where(Product.product_id == product_id)
            )

            # Apply is_online filter if specified
            if is_online is not None:
                stmt = stmt.where(Store.is_online == (1 if is_online else 0))

            stmt = stmt.order_by(Inventory.stock_level.desc())

            result = await session.execute(stmt)
            rows = result.mappings().all()

            if not rows:
                logger.info(f"No inventory found for product ID: {product_id}")
                return []

            inventory_list = [dict(row) for row in rows]

            logger.info(f"Found inventory at {len(inventory_list)} store(s) for product ID: {product_id}")
            return inventory_list

    except Exception as e:
        logger.error(f"Error getting stock levels: {e}")
        return []


@mcp.tool()
async def transfer_stock(
    from_store_id: Annotated[int, Field(description="Store ID to transfer stock FROM")],
    to_store_id: Annotated[int, Field(description="Store ID to transfer stock TO")],
    product_id: Annotated[int, Field(description="Product ID to transfer")],
    quantity: Annotated[int, Field(description="Number of items to transfer", gt=0)],
) -> dict:
    """
    Transfer stock from one store to another. **This tool alters the database.**

    **CRITICAL SAFETY RULE:** Before calling this tool, you must explicitly ask the user for confirmation summarizing the transfer (e.g., "Please confirm: Transfer 10 units of 'ProSeries Hammer Drill' from Seattle to Redmond?"). Use product name, not product ID, in the confirmation message.

    Args:
        from_store_id: Source store ID (integer).
        to_store_id: Destination store ID (integer).
        product_id: Product ID (primary key).
        quantity: Number of units to transfer (must be positive).

    Returns:
        Transfer result with status and updated stock levels.
    """
    try:
        logger.info(
            f"Transfer request: {quantity} units of product_id {product_id} from store {from_store_id} to store {to_store_id}"
        )

        if from_store_id == to_store_id:
            return {
                "success": False,
                "message": "Cannot transfer stock to the same store",
            }

        if quantity <= 0:
            return {
                "success": False,
                "message": "Transfer quantity must be positive",
            }

        async with db.get_session() as session:
            # Get source and destination inventory in a single query
            inventory_stmt = (
                select(Inventory, Store.store_name)
                .join(Store, Inventory.store_id == Store.store_id)
                .where(
                    and_(
                        Inventory.product_id == product_id,
                        Inventory.store_id.in_([from_store_id, to_store_id]),
                    )
                )
            )
            inventory_result = await session.execute(inventory_stmt)
            inventory_rows = inventory_result.all()

            # Organize results
            from_inventory = None
            to_inventory = None
            from_store_name = None
            to_store_name = None

            for inv, store_name in inventory_rows:
                if inv.store_id == from_store_id:
                    from_inventory = inv
                    from_store_name = store_name
                elif inv.store_id == to_store_id:
                    to_inventory = inv
                    to_store_name = store_name

            if not from_inventory:
                return {
                    "success": False,
                    "message": f"No inventory record found for product ID '{product_id}' at source store {from_store_id}",
                }

            if from_inventory.stock_level < quantity:
                return {
                    "success": False,
                    "message": f"Insufficient stock at source store. Available: {from_inventory.stock_level}, Requested: {quantity}",
                    "available_stock": from_inventory.stock_level,
                }

            # Create inventory record if it doesn't exist at destination
            if not to_inventory:
                logger.info(
                    f"Creating new inventory record for product ID '{product_id}' at destination store {to_store_id}"
                )
                to_inventory = Inventory(
                    store_id=to_store_id,
                    product_id=product_id,
                    stock_level=0,
                )
                session.add(to_inventory)
                await session.flush()

            # Capture before values
            old_from_stock = from_inventory.stock_level
            old_to_stock = to_inventory.stock_level

            # Perform the transfer
            from_inventory.stock_level -= quantity
            to_inventory.stock_level += quantity

            # Commit the transaction
            await session.commit()

            logger.info(
                f"Transfer completed: {quantity} units of product ID {product_id} "
                f"from store {from_store_id} ({from_store_name}) to store {to_store_id} ({to_store_name})"
            )

            return {
                "success": True,
                "message": f"Successfully transferred {quantity} units",
                "product_id": product_id,
                "quantity_transferred": quantity,
                "from_store": {
                    "store_id": from_store_id,
                    "store_name": from_store_name,
                    "stock_before": old_from_stock,
                    "stock_after": from_inventory.stock_level,
                },
                "to_store": {
                    "store_id": to_store_id,
                    "store_name": to_store_name,
                    "stock_before": old_to_stock,
                    "stock_after": to_inventory.stock_level,
                },
            }

    except Exception as e:
        logger.error(f"Error transferring stock: {e}")
        return {
            "success": False,
            "message": f"Error during transfer: {e!s}",
        }


if __name__ == "__main__":
    logger.info("🚀 Starting Inventory Agent MCP Server")
    # Configure server settings
    port = int(os.getenv("PORT", "8005"))
    host = os.getenv("HOST", "0.0.0.0")
    logger.info(
        "📦 📡 Inventory MCP endpoint starting at: http://%s:%d/mcp",
        host,
        port,
    )
    mcp.run(transport="http", host=host, port=port, path="/mcp", stateless_http=True)
