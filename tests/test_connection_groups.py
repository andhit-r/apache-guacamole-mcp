"""Unit tests for :mod:`guacamole_mcp.tools.connection_groups`."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

import guacamole_mcp.state as state
from guacamole_mcp.tools import connection_groups

DS = "postgresql"


@pytest.fixture(autouse=True)
def inject_mock_client(mock_client: AsyncMock) -> None:
    state.set_client(mock_client)
    yield
    state.set_client(None)


class TestListConnectionGroups:
    async def test_calls_correct_endpoint(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {}
        await connection_groups.list_connection_groups()
        mock_client.get.assert_called_once_with(
            f"/api/session/data/{DS}/connectionGroups"
        )


class TestListConnectionTree:
    async def test_calls_root_tree_endpoint(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {"childConnectionGroups": []}
        await connection_groups.list_connection_tree()
        mock_client.get.assert_called_once_with(
            f"/api/session/data/{DS}/connectionGroups/ROOT/tree"
        )


class TestGetConnectionGroup:
    async def test_calls_correct_endpoint(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {"identifier": "5"}
        result = await connection_groups.get_connection_group("5")
        mock_client.get.assert_called_once_with(
            f"/api/session/data/{DS}/connectionGroups/5"
        )
        assert result["identifier"] == "5"


class TestGetConnectionGroupTree:
    async def test_calls_tree_endpoint(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {}
        await connection_groups.get_connection_group_tree("5")
        mock_client.get.assert_called_once_with(
            f"/api/session/data/{DS}/connectionGroups/5/tree",
            params={},
        )

    async def test_passes_permission_param(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {}
        await connection_groups.get_connection_group_tree("5", permission="READ")
        mock_client.get.assert_called_once_with(
            f"/api/session/data/{DS}/connectionGroups/5/tree",
            params={"permission": "READ"},
        )


class TestCreateConnectionGroup:
    async def test_sends_post_request(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = {"identifier": "10", "name": "Prod"}
        result = await connection_groups.create_connection_group(
            name="Prod", group_type="ORGANIZATIONAL"
        )
        mock_client.post.assert_called_once_with(
            f"/api/session/data/{DS}/connectionGroups",
            json={
                "name": "Prod",
                "type": "ORGANIZATIONAL",
                "parentIdentifier": "ROOT",
                "attributes": {},
            },
        )
        assert result["identifier"] == "10"

    async def test_passes_custom_parent(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = {}
        await connection_groups.create_connection_group(
            name="Sub", parent_identifier="5"
        )
        call_json = mock_client.post.call_args.kwargs["json"]
        assert call_json["parentIdentifier"] == "5"


class TestUpdateConnectionGroup:
    async def test_sends_put_request(self, mock_client: AsyncMock) -> None:
        result = await connection_groups.update_connection_group(
            connection_group_id="10",
            name="Updated Prod",
            group_type="ORGANIZATIONAL",
        )
        mock_client.put.assert_called_once_with(
            f"/api/session/data/{DS}/connectionGroups/10",
            json={
                "identifier": "10",
                "name": "Updated Prod",
                "type": "ORGANIZATIONAL",
                "parentIdentifier": "ROOT",
                "attributes": {},
            },
        )
        assert result == {"status": "ok"}


class TestDeleteConnectionGroup:
    async def test_sends_delete_request(self, mock_client: AsyncMock) -> None:
        result = await connection_groups.delete_connection_group("10")
        mock_client.delete.assert_called_once_with(
            f"/api/session/data/{DS}/connectionGroups/10"
        )
        assert result == {"status": "ok"}
