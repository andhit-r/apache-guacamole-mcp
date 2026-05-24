"""Unit tests for :mod:`guacamole_mcp.tools.history`."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

import guacamole_mcp.state as state
from guacamole_mcp.tools import history

DS = "postgresql"


@pytest.fixture(autouse=True)
def inject_mock_client(mock_client: AsyncMock) -> None:
    state.set_client(mock_client)
    yield
    state.set_client(None)


class TestListConnectionHistory:
    async def test_calls_correct_endpoint(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = []
        await history.list_connection_history()
        mock_client.get.assert_called_once_with(
            f"/api/session/data/{DS}/history/connections",
            params={},
        )

    async def test_passes_contains_param(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = []
        await history.list_connection_history(contains="server")
        mock_client.get.assert_called_once_with(
            f"/api/session/data/{DS}/history/connections",
            params={"contains": "server"},
        )

    async def test_passes_order_param(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = []
        await history.list_connection_history(order="startDate")
        mock_client.get.assert_called_once_with(
            f"/api/session/data/{DS}/history/connections",
            params={"order": "startDate"},
        )

    async def test_passes_both_params(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = []
        await history.list_connection_history(contains="prod", order="startDate")
        mock_client.get.assert_called_once_with(
            f"/api/session/data/{DS}/history/connections",
            params={"contains": "prod", "order": "startDate"},
        )


class TestListUserHistory:
    async def test_calls_correct_endpoint(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = []
        await history.list_user_history()
        mock_client.get.assert_called_once_with(
            f"/api/session/data/{DS}/history/users",
            params={},
        )

    async def test_passes_order_param(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = []
        await history.list_user_history(order="startDate")
        mock_client.get.assert_called_once_with(
            f"/api/session/data/{DS}/history/users",
            params={"order": "startDate"},
        )

    async def test_returns_list(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = [
            {"username": "alice", "startDate": 1000},
            {"username": "bob", "startDate": 2000},
        ]
        result = await history.list_user_history()
        assert len(result) == 2
        assert result[0]["username"] == "alice"
