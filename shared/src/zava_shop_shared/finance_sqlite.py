#!/usr/bin/env python3
"""
Finance Database Access Provider for Zava Retail - SQLite Edition

This module provides pre-written SQL queries for finance-related operations
to support the Finance Agent MCP server using SQLite with SQLAlchemy ORM.
"""

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from .config import Config

logger = logging.getLogger(__name__)
config = Config()


class FinanceSQLiteProvider:
    """Provides SQLite database access for finance-related operations."""

    def __init__(self, sqlite_url: Optional[str] = None) -> None:
        # Use default SQLite URL if not provided
        self.sqlite_url = config.sqlite_database_url if sqlite_url is None else sqlite_url
        self.engine: Optional[AsyncEngine] = None
        self.async_session_factory: Optional[async_sessionmaker] = None

    async def __aenter__(self) -> "FinanceSQLiteProvider":
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

    async def open(self) -> None:
        """Open database connection and initialize async engine."""
        if self.engine is None:
            try:
                # Add read-only mode to SQLite connection
                readonly_url = self.sqlite_url
                if "?" in readonly_url:
                    readonly_url += "&mode=ro&immutable=1"
                else:
                    readonly_url += "?mode=ro&immutable=1"

                self.engine = create_async_engine(
                    readonly_url,
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

                logger.info("✅ Finance SQLite async engine created")
            except Exception as e:
                logger.error("❌ Failed to create SQLAlchemy engine: %s", e)
                raise

    async def close_engine(self) -> None:
        """Close async engine and cleanup."""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.async_session_factory = None
            logger.info("✅ Finance SQLite async engine closed")

    def get_session(self) -> AsyncSession:
        """Get a new async session."""
        if not self.async_session_factory:
            raise RuntimeError("No session factory available. Call open() first.")
        return self.async_session_factory()
