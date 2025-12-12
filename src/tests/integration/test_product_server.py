"""Integration tests for Product MCP Server."""

import pytest
import pytest_asyncio
from fastmcp.client import Client

from mcp_servers.product_server import mcp


@pytest_asyncio.fixture
async def client():
    """Create MCP client for Product server."""
    async with Client(mcp) as mcp_client:
        yield mcp_client


@pytest.mark.asyncio
async def test_search_products_by_description(client):
    """Test semantic search for products."""
    result = await client.call_tool(
        "search_products_by_description",
        arguments={"query": "cordless drill with battery", "limit": 5, "min_similarity": 0.1},
    )

    assert isinstance(result.data, list)
    # Should find some products even with simple embedding
    # (actual results depend on the pseudo-embedding algorithm)
    for product in result.data:
        assert "product_id" in product
        assert "sku" in product
        assert "product_name" in product
        assert "description" in product
        assert "category" in product
        assert "base_price" in product
        assert "similarity_score" in product
        assert 0 <= product["similarity_score"] <= 1


@pytest.mark.asyncio
async def test_get_product_availability_by_sku(client):
    """Test product availability lookup by SKU."""
    # Use a known SKU from the database
    result = await client.call_tool("get_product_availability", arguments={"sku": "HTHM001600"})

    assert isinstance(result.data, dict)
    assert result.data["sku"] == "HTHM001600"
    assert "product_name" in result.data
    assert "availability" in result.data
    assert "stock_by_store" in result.data["availability"]
    assert "total_stock_all_stores" in result.data["availability"]
    assert "supplier_info" in result.data
    assert "lead_time_days" in result.data["supplier_info"]
    assert "ordering_info" in result.data
    assert "procurement_lead_time_days" in result.data["ordering_info"]


@pytest.mark.asyncio
async def test_get_product_availability_specific_store(client):
    """Test product availability for specific store."""
    result = await client.call_tool("get_product_availability", arguments={"sku": "HTHM001600", "store_id": 1})

    assert isinstance(result.data, dict)
    assert "availability" in result.data
    assert "stock_by_store" in result.data["availability"]
    # Should only have one store
    assert len(result.data["availability"]["stock_by_store"]) == 1
    assert result.data["availability"]["stock_by_store"][0]["store_id"] == 1


@pytest.mark.asyncio
async def test_get_low_stock_products(client):
    """Test low stock products retrieval."""
    result = await client.call_tool("get_low_stock_products", arguments={"threshold": 50, "category_name": "PLUMBING"})

    # Verify we got results
    assert result.data is not None
    assert len(result.data) > 0


@pytest.mark.asyncio
async def test_get_low_stock_products_specific_store(client):
    """Test low stock products for specific store."""
    result = await client.call_tool("get_low_stock_products", arguments={"store_id": 1, "threshold": 20})

    # Verify we got results
    assert result.data is not None
    assert len(result.data) > 0


@pytest.mark.asyncio
async def test_compare_product_prices_by_skus(client):
    """Test product price comparison by SKUs."""
    result = await client.call_tool(
        "compare_product_prices", arguments={"skus": ["HTHM001600", "HTHM031200", "HTHM041300"]}
    )

    # Verify we got results
    assert result.data is not None
    assert len(result.data) > 0
    assert len(result.data) <= 3


@pytest.mark.asyncio
async def test_compare_product_prices_by_category(client):
    """Test product price comparison for entire category."""
    result = await client.call_tool("compare_product_prices", arguments={"category_name": "POWER TOOLS"})

    # Verify we got results
    assert result.data is not None
    assert len(result.data) > 0


@pytest.mark.asyncio
async def test_get_current_utc_date(client):
    """Test current UTC date retrieval."""
    result = await client.call_tool("get_current_utc_date", arguments={})

    assert isinstance(result.data, str)
    # Should be ISO format
    assert "T" in result.data
    assert len(result.data) > 10
