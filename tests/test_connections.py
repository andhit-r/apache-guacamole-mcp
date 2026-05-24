"""Unit tests for :mod:`guacamole_mcp.tools.connections`."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

import guacamole_mcp.state as state
from guacamole_mcp.tools import connections

DS = "postgresql"


@pytest.fixture(autouse=True)
def inject_mock_client(mock_client: AsyncMock) -> None:
    state.set_client(mock_client)
    yield
    state.set_client(None)


class TestListConnections:
    async def test_calls_correct_endpoint(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {"1": {"name": "Server A"}}
        result = await connections.list_connections()
        mock_client.get.assert_called_once_with(f"/api/session/data/{DS}/connections")
        assert "1" in result


class TestGetConnection:
    async def test_calls_correct_endpoint(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {"identifier": "1"}
        result = await connections.get_connection("1")
        mock_client.get.assert_called_once_with(f"/api/session/data/{DS}/connections/1")
        assert result["identifier"] == "1"


class TestGetConnectionParameters:
    async def test_calls_parameters_endpoint(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {"hostname": "10.0.0.1"}
        await connections.get_connection_parameters("1")
        mock_client.get.assert_called_once_with(
            f"/api/session/data/{DS}/connections/1/parameters"
        )


class TestGetConnectionHistory:
    async def test_calls_history_endpoint(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = []
        await connections.get_connection_history("1")
        mock_client.get.assert_called_once_with(
            f"/api/session/data/{DS}/connections/1/history"
        )


class TestGetConnectionSharingProfiles:
    async def test_calls_sharing_profiles_endpoint(
        self, mock_client: AsyncMock
    ) -> None:
        mock_client.get.return_value = {}
        await connections.get_connection_sharing_profiles("1")
        mock_client.get.assert_called_once_with(
            f"/api/session/data/{DS}/connections/1/sharingProfiles"
        )


class TestListSharingProfiles:
    async def test_calls_correct_endpoint(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {}
        await connections.list_sharing_profiles()
        mock_client.get.assert_called_once_with(
            f"/api/session/data/{DS}/sharingProfiles"
        )


class TestListActiveConnections:
    async def test_calls_active_connections_endpoint(
        self, mock_client: AsyncMock
    ) -> None:
        mock_client.get.return_value = {}
        await connections.list_active_connections()
        mock_client.get.assert_called_once_with(
            f"/api/session/data/{DS}/activeConnections"
        )


class TestKillConnections:
    async def test_sends_remove_patch(self, mock_client: AsyncMock) -> None:
        result = await connections.kill_connections(["abc", "def"])
        expected_patch = [
            {"op": "remove", "path": "/abc"},
            {"op": "remove", "path": "/def"},
        ]
        mock_client.patch.assert_called_once_with(
            f"/api/session/data/{DS}/activeConnections",
            json=expected_patch,
        )
        assert result == {"status": "ok"}


class TestCreateConnection:
    async def test_sends_post_for_ssh(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = {"identifier": "42", "name": "My SSH"}
        params = {"hostname": "10.0.0.1", "port": "22", "username": "admin"}
        result = await connections.create_connection(
            name="My SSH", protocol="ssh", parameters=params
        )
        mock_client.post.assert_called_once_with(
            f"/api/session/data/{DS}/connections",
            json={
                "name": "My SSH",
                "protocol": "ssh",
                "parentIdentifier": "ROOT",
                "parameters": params,
                "attributes": {},
            },
        )
        assert result["identifier"] == "42"

    async def test_passes_custom_parent_and_attributes(
        self, mock_client: AsyncMock
    ) -> None:
        mock_client.post.return_value = {}
        attrs = {"max-connections": "5"}
        await connections.create_connection(
            name="RDP Box",
            protocol="rdp",
            parameters={"hostname": "192.168.1.1", "port": "3389"},
            attributes=attrs,
            parent_identifier="10",
        )
        call_json = mock_client.post.call_args.kwargs["json"]
        assert call_json["parentIdentifier"] == "10"
        assert call_json["attributes"] == attrs


class TestUpdateConnection:
    async def test_sends_put_request(self, mock_client: AsyncMock) -> None:
        result = await connections.update_connection(
            connection_id="1",
            name="Updated Server",
            protocol="ssh",
            parameters={"hostname": "10.0.0.2", "port": "22"},
        )
        mock_client.put.assert_called_once_with(
            f"/api/session/data/{DS}/connections/1",
            json={
                "identifier": "1",
                "name": "Updated Server",
                "protocol": "ssh",
                "parentIdentifier": "ROOT",
                "parameters": {"hostname": "10.0.0.2", "port": "22"},
                "attributes": {},
            },
        )
        assert result == {"status": "ok"}


class TestDeleteConnection:
    async def test_sends_delete_request(self, mock_client: AsyncMock) -> None:
        result = await connections.delete_connection("42")
        mock_client.delete.assert_called_once_with(
            f"/api/session/data/{DS}/connections/42"
        )
        assert result == {"status": "ok"}
