"""Shared pytest fixtures for guacamole-mcp tests."""

from __future__ import annotations

from unittest.mock import AsyncMock

import httpx
import pytest
import respx

from guacamole_mcp.client import GuacamoleClient
from guacamole_mcp.config import GuacamoleConfig

BASE_URL = "http://guacamole-test:8080"
AUTH_TOKEN = "test-token-abc123"

AUTH_RESPONSE = {
    "authToken": AUTH_TOKEN,
    "username": "guacadmin",
    "dataSource": "postgresql",
    "availableDataSources": ["postgresql"],
}


@pytest.fixture()
def guac_config() -> GuacamoleConfig:
    """Minimal :class:`GuacamoleConfig` pointed at the test URL."""
    return GuacamoleConfig(
        url=BASE_URL,
        username="guacadmin",
        password="guacadmin",  # type: ignore[arg-type]
        data_source="postgresql",
        timeout=5.0,
        verify_ssl=False,
        transport="stdio",
    )


@pytest.fixture()
def real_client(guac_config: GuacamoleConfig) -> GuacamoleClient:
    """A :class:`GuacamoleClient` wired to the test config (no mocks)."""
    return GuacamoleClient(guac_config)


@pytest.fixture()
def mock_client() -> AsyncMock:
    """AsyncMock replacement for :class:`GuacamoleClient`.

    Inject this via :func:`guacamole_mcp.state.set_client` inside each
    test that exercises a tool function.
    """
    client = AsyncMock(spec=GuacamoleClient)
    # Default return values for common methods
    client.get.return_value = {}
    client.post.return_value = {}
    client.put.return_value = None
    client.patch.return_value = None
    client.delete.return_value = None
    return client


@pytest.fixture()
def respx_mock() -> respx.MockRouter:
    """Active respx mock router for httpx-level mocking."""
    with respx.mock(base_url=BASE_URL, assert_all_called=False) as router:
        router.post("/api/tokens").mock(
            return_value=httpx.Response(200, json=AUTH_RESPONSE)
        )
        yield router
