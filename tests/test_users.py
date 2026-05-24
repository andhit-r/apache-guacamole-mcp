"""Unit tests for :mod:`guacamole_mcp.tools.users`."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

import guacamole_mcp.state as state
from guacamole_mcp.tools import users

DATA_SOURCE = "postgresql"


@pytest.fixture(autouse=True)
def inject_mock_client(mock_client: AsyncMock) -> None:
    state.set_client(mock_client)
    yield
    state.set_client(None)


class TestListUsers:
    async def test_calls_correct_endpoint(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {"admin": {"username": "admin"}}
        result = await users.list_users()
        mock_client.get.assert_called_once_with(
            f"/api/session/data/{DATA_SOURCE}/users"
        )
        assert "admin" in result

    async def test_custom_data_source(self, mock_client: AsyncMock) -> None:
        await users.list_users(data_source="mysql")
        mock_client.get.assert_called_once_with("/api/session/data/mysql/users")


class TestGetUser:
    async def test_calls_correct_endpoint(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {"username": "alice"}
        result = await users.get_user("alice")
        mock_client.get.assert_called_once_with(
            f"/api/session/data/{DATA_SOURCE}/users/alice"
        )
        assert result["username"] == "alice"


class TestGetSelf:
    async def test_calls_self_endpoint(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {"username": "guacadmin"}
        await users.get_self()
        mock_client.get.assert_called_once_with(f"/api/session/data/{DATA_SOURCE}/self")


class TestGetUserPermissions:
    async def test_calls_permissions_endpoint(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {"systemPermissions": ["ADMINISTER"]}
        await users.get_user_permissions("alice")
        mock_client.get.assert_called_once_with(
            f"/api/session/data/{DATA_SOURCE}/users/alice/permissions"
        )


class TestGetUserEffectivePermissions:
    async def test_calls_effective_permissions_endpoint(
        self, mock_client: AsyncMock
    ) -> None:
        await users.get_user_effective_permissions("alice")
        mock_client.get.assert_called_once_with(
            f"/api/session/data/{DATA_SOURCE}/users/alice/effectivePermissions"
        )


class TestGetUserGroups:
    async def test_calls_user_groups_endpoint(self, mock_client: AsyncMock) -> None:
        await users.get_user_groups("alice")
        mock_client.get.assert_called_once_with(
            f"/api/session/data/{DATA_SOURCE}/users/alice/userGroups"
        )


class TestGetUserHistory:
    async def test_calls_history_endpoint(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = []
        await users.get_user_history("alice")
        mock_client.get.assert_called_once_with(
            f"/api/session/data/{DATA_SOURCE}/users/alice/history"
        )


class TestAssignUserToGroups:
    async def test_sends_add_patch(self, mock_client: AsyncMock) -> None:
        result = await users.assign_user_to_groups("alice", ["admins", "devs"])
        mock_client.patch.assert_called_once_with(
            f"/api/session/data/{DATA_SOURCE}/users/alice/userGroups",
            json=[
                {"op": "add", "path": "/", "value": "admins"},
                {"op": "add", "path": "/", "value": "devs"},
            ],
        )
        assert result == {"status": "ok"}


class TestRevokeUserFromGroups:
    async def test_sends_remove_patch(self, mock_client: AsyncMock) -> None:
        result = await users.revoke_user_from_groups("alice", ["admins"])
        mock_client.patch.assert_called_once_with(
            f"/api/session/data/{DATA_SOURCE}/users/alice/userGroups",
            json=[{"op": "remove", "path": "/", "value": "admins"}],
        )
        assert result == {"status": "ok"}


class TestGrantUserConnectionPermissions:
    async def test_sends_add_patch(self, mock_client: AsyncMock) -> None:
        result = await users.grant_user_connection_permissions("alice", ["1", "2"])
        expected_patch = [
            {"op": "add", "path": "/connectionPermissions/1", "value": "READ"},
            {"op": "add", "path": "/connectionPermissions/2", "value": "READ"},
        ]
        mock_client.patch.assert_called_once_with(
            f"/api/session/data/{DATA_SOURCE}/users/alice/permissions",
            json=expected_patch,
        )
        assert result == {"status": "ok"}


class TestRevokeUserConnectionPermissions:
    async def test_sends_remove_patch(self, mock_client: AsyncMock) -> None:
        result = await users.revoke_user_connection_permissions("alice", ["1"])
        expected_patch = [
            {
                "op": "remove",
                "path": "/connectionPermissions/1",
                "value": "READ",
            }
        ]
        mock_client.patch.assert_called_once_with(
            f"/api/session/data/{DATA_SOURCE}/users/alice/permissions",
            json=expected_patch,
        )
        assert result == {"status": "ok"}


class TestGrantUserSystemPermissions:
    async def test_sends_add_patch(self, mock_client: AsyncMock) -> None:
        result = await users.grant_user_system_permissions(
            "alice", ["CREATE_USER", "ADMINISTER"]
        )
        expected = [
            {"op": "add", "path": "/systemPermissions", "value": "CREATE_USER"},
            {"op": "add", "path": "/systemPermissions", "value": "ADMINISTER"},
        ]
        mock_client.patch.assert_called_once_with(
            f"/api/session/data/{DATA_SOURCE}/users/alice/permissions",
            json=expected,
        )
        assert result == {"status": "ok"}


class TestUpdateUserPassword:
    async def test_sends_put_request(self, mock_client: AsyncMock) -> None:
        result = await users.update_user_password("alice", "old", "new")
        mock_client.put.assert_called_once_with(
            f"/api/session/data/{DATA_SOURCE}/users/alice/password",
            json={"oldPassword": "old", "newPassword": "new"},
        )
        assert result == {"status": "ok"}


class TestUpdateUser:
    async def test_sends_put_request(self, mock_client: AsyncMock) -> None:
        attrs = {"guac-full-name": "Alice Smith"}
        result = await users.update_user("alice", attrs)
        mock_client.put.assert_called_once_with(
            f"/api/session/data/{DATA_SOURCE}/users/alice",
            json={"username": "alice", "attributes": attrs},
        )
        assert result == {"status": "ok"}


class TestCreateUser:
    async def test_sends_post_request(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = {"username": "bob", "attributes": {}}
        result = await users.create_user("bob", "password123")
        mock_client.post.assert_called_once_with(
            f"/api/session/data/{DATA_SOURCE}/users",
            json={"username": "bob", "password": "password123", "attributes": {}},
        )
        assert result["username"] == "bob"

    async def test_passes_attributes(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = {}
        attrs = {"disabled": ""}
        await users.create_user("bob", "pass", attributes=attrs)
        call_args = mock_client.post.call_args
        assert call_args.kwargs["json"]["attributes"] == attrs


class TestDeleteUser:
    async def test_sends_delete_request(self, mock_client: AsyncMock) -> None:
        result = await users.delete_user("alice")
        mock_client.delete.assert_called_once_with(
            f"/api/session/data/{DATA_SOURCE}/users/alice"
        )
        assert result == {"status": "ok"}
