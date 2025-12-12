"""
Integration tests for Finance MCP Server tools.

Tests the actual MCP tool implementations with a test database.
"""

import pytest
import pytest_asyncio
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport

from mcp_servers.finance_server import mcp


@pytest_asyncio.fixture
async def main_mcp_client():
    async with Client(mcp) as client:
        yield client


@pytest.mark.asyncio
@pytest.mark.parametrize("department", ["", "Finance"])
async def test_get_company_order_policy(
    department: str,
    main_mcp_client: Client[FastMCPTransport],
):
    result = await main_mcp_client.call_tool(name="get_company_order_policy", arguments={"department": department})
    assert result.data is not None


@pytest.mark.asyncio
async def test_get_supplier_contract(
    main_mcp_client: Client[FastMCPTransport],
):
    result = await main_mcp_client.call_tool(name="get_supplier_contract", arguments={"supplier_id": 1})
    assert result.data is not None


@pytest.mark.asyncio
async def test_get_historical_sales_data(
    main_mcp_client: Client[FastMCPTransport],
):
    result = await main_mcp_client.call_tool(
        name="get_historical_sales_data", arguments={"days_back": 30, "store_id": 1, "category_name": "POWER TOOLS"}
    )
    assert result.data is not None


@pytest.mark.asyncio
async def test_get_current_inventory_status(
    main_mcp_client: Client[FastMCPTransport],
):
    result = await main_mcp_client.call_tool(
        name="get_current_inventory_status", arguments={"store_id": 1, "category_name": "HARDWARE"}
    )
    assert result.data is not None


@pytest.mark.asyncio
@pytest.mark.parametrize("store_id", ["", "Manhattan"])
async def test_get_stores(
    store_id: str,
    main_mcp_client: Client[FastMCPTransport],
):
    result = await main_mcp_client.call_tool(name="get_stores", arguments={"store_name": store_id})
    assert result.data is not None
