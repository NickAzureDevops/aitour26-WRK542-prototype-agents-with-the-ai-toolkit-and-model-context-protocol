#!/usr/bin/env python3
"""
Inventory Database Access Provider for Zava Retail - SQLite Edition

This module provides database access for inventory-related operations
with READ-WRITE access to support stock transfers.
"""

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from .config import Config

logger = logging.getLogger(__name__)
config = Config()


class InventorySQLiteProvider:
    """Provides SQLite database access for inventory operations with read-write capability."""

    def __init__(self, sqlite_url: Optional[str] = None) -> None:
        # Use default SQLite URL if not provided
        self.sqlite_url = config.sqlite_database_url if sqlite_url is None else sqlite_url
        self.engine: Optional[AsyncEngine] = None
        self.async_session_factory: Optional[async_sessionmaker] = None

    async def __aenter__(self) -> "InventorySQLiteProvider":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[object],
    ) -> None:
        """Async context manager exit."""
        await self.close_engine()

    async def open_engine(self) -> None:
        """Open database connection and initialize async engine for READ-WRITE access."""
        if self.engine is None:
            try:
                # Note: No read-only mode for inventory server - it needs write access for transfers
                self.engine = create_async_engine(
                    self.sqlite_url,
                    connect_args={"timeout": 30, "check_same_thread": False},
                    pool_pre_ping=True,
                    echo=False,
                )

                # Create async session factory
                self.async_session_factory = async_sessionmaker(
                    self.engine,
                    class_=AsyncSession,
                    expire_on_commit=False,
                )

                logger.info("✅ Inventory SQLite async engine created (READ-WRITE mode)")
            except Exception as e:
                logger.error("❌ Failed to create SQLAlchemy engine: %s", e)
                raise

    async def close_engine(self) -> None:
        """Close async engine and cleanup."""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.async_session_factory = None
            logger.info("✅ Inventory SQLite async engine closed")

    def get_session(self) -> AsyncSession:
        """Get a new async session."""
        if not self.async_session_factory:
            raise RuntimeError("No session factory available. Call open() first.")
        return self.async_session_factory()
