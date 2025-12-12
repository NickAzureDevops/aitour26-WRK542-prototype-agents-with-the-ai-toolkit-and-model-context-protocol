"""
Pytest configuration and fixtures for MCP server testing.

This module provides shared fixtures and configuration for all MCP server tests.
"""

import pytest


# Configure pytest-asyncio mode
def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as an asyncio test")
