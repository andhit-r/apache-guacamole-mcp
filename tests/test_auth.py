"""Unit tests for :mod:`guacamole_mcp.tools.auth`."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

import guacamole_mcp.state as state
from guacamole_mcp.tools import auth


@pytest.fixture(autouse=True)
def inject_mock_client(mock_client: AsyncMock) -> None:
    state.set_client(mock_client)
    yield
    state.set_client(None)


class TestAuthenticate:
    async def test_calls_authenticate_on_client(self, mock_client: AsyncMock) -> None:
        mock_client.authenticate.return_value = "new-token-xyz"
        result = await auth.authenticate()

        mock_client.authenticate.assert_called_once()
        assert result["authToken"] == "new-token-xyz"
        assert result["status"] == "authenticated"


class TestLogout:
    async def test_calls_logout_on_client(self, mock_client: AsyncMock) -> None:
        result = await auth.logout()

        mock_client.logout.assert_called_once()
        assert result == {"status": "ok"}
