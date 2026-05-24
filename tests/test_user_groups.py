"""Unit tests for :mod:`guacamole_mcp.tools.user_groups`."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

import guacamole_mcp.state as state
from guacamole_mcp.tools import user_groups

DS = "postgresql"


@pytest.fixture(autouse=True)
def inject_mock_client(mock_client: AsyncMock) -> None:
    state.set_client(mock_client)
    yield
    state.set_client(None)


class TestListUserGroups:
    async def test_calls_correct_endpoint(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {}
        await user_groups.list_user_groups()
        mock_client.get.assert_called_once_with(f"/api/session/data/{DS}/userGroups")


class TestGetUserGroup:
    async def test_calls_correct_endpoint(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {"identifier": "admins"}
        result = await user_groups.get_user_group("admins")
        mock_client.get.assert_called_once_with(
            f"/api/session/data/{DS}/userGroups/admins"
        )
        assert result["identifier"] == "admins"


class TestAddMembersToUserGroup:
    async def test_sends_add_patch(self, mock_client: AsyncMock) -> None:
        result = await user_groups.add_members_to_user_group("admins", ["alice", "bob"])
        mock_client.patch.assert_called_once_with(
            f"/api/session/data/{DS}/userGroups/admins/memberUsers",
            json=[
                {"op": "add", "path": "/", "value": "alice"},
                {"op": "add", "path": "/", "value": "bob"},
            ],
        )
        assert result == {"status": "ok"}


class TestRemoveMembersFromUserGroup:
    async def test_sends_remove_patch(self, mock_client: AsyncMock) -> None:
        result = await user_groups.remove_members_from_user_group("admins", ["alice"])
        mock_client.patch.assert_called_once_with(
            f"/api/session/data/{DS}/userGroups/admins/memberUsers",
            json=[{"op": "remove", "path": "/", "value": "alice"}],
        )
        assert result == {"status": "ok"}


class TestAddMemberGroupsToUserGroup:
    async def test_sends_add_patch(self, mock_client: AsyncMock) -> None:
        result = await user_groups.add_member_groups_to_user_group(
            "admins", ["dev-team"]
        )
        mock_client.patch.assert_called_once_with(
            f"/api/session/data/{DS}/userGroups/admins/memberUserGroups",
            json=[{"op": "add", "path": "/", "value": "dev-team"}],
        )
        assert result == {"status": "ok"}


class TestRemoveMemberGroupsFromUserGroup:
    async def test_sends_remove_patch(self, mock_client: AsyncMock) -> None:
        result = await user_groups.remove_member_groups_from_user_group(
            "admins", ["dev-team"]
        )
        mock_client.patch.assert_called_once_with(
            f"/api/session/data/{DS}/userGroups/admins/memberUserGroups",
            json=[{"op": "remove", "path": "/", "value": "dev-team"}],
        )
        assert result == {"status": "ok"}


class TestAddParentGroupsToUserGroup:
    async def test_sends_add_patch(self, mock_client: AsyncMock) -> None:
        result = await user_groups.add_parent_groups_to_user_group(
            "dev-team", ["all-users"]
        )
        mock_client.patch.assert_called_once_with(
            f"/api/session/data/{DS}/userGroups/dev-team/userGroups",
            json=[{"op": "add", "path": "/", "value": "all-users"}],
        )
        assert result == {"status": "ok"}


class TestAssignConnectionPermissionsToUserGroup:
    async def test_sends_add_patch(self, mock_client: AsyncMock) -> None:
        result = await user_groups.assign_connection_permissions_to_user_group(
            "admins", ["1", "2"]
        )
        expected = [
            {"op": "add", "path": "/connectionPermissions/1", "value": "READ"},
            {"op": "add", "path": "/connectionPermissions/2", "value": "READ"},
        ]
        mock_client.patch.assert_called_once_with(
            f"/api/session/data/{DS}/userGroups/admins/permissions",
            json=expected,
        )
        assert result == {"status": "ok"}


class TestRevokeConnectionPermissionsFromUserGroup:
    async def test_sends_remove_patch(self, mock_client: AsyncMock) -> None:
        result = await user_groups.revoke_connection_permissions_from_user_group(
            "admins", ["1"]
        )
        expected = [
            {"op": "remove", "path": "/connectionPermissions/1", "value": "READ"}
        ]
        mock_client.patch.assert_called_once_with(
            f"/api/session/data/{DS}/userGroups/admins/permissions",
            json=expected,
        )
        assert result == {"status": "ok"}


class TestAssignSystemPermissionsToUserGroup:
    async def test_sends_add_patch(self, mock_client: AsyncMock) -> None:
        result = await user_groups.assign_system_permissions_to_user_group(
            "admins", ["CREATE_USER", "ADMINISTER"]
        )
        expected = [
            {"op": "add", "path": "/systemPermissions", "value": "CREATE_USER"},
            {"op": "add", "path": "/systemPermissions", "value": "ADMINISTER"},
        ]
        mock_client.patch.assert_called_once_with(
            f"/api/session/data/{DS}/userGroups/admins/permissions",
            json=expected,
        )
        assert result == {"status": "ok"}


class TestUpdateUserGroup:
    async def test_sends_put_request(self, mock_client: AsyncMock) -> None:
        result = await user_groups.update_user_group(
            "admins", attributes={"disabled": ""}
        )
        mock_client.put.assert_called_once_with(
            f"/api/session/data/{DS}/userGroups/admins",
            json={"identifier": "admins", "attributes": {"disabled": ""}},
        )
        assert result == {"status": "ok"}


class TestCreateUserGroup:
    async def test_sends_post_request(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = {"identifier": "ops-team"}
        result = await user_groups.create_user_group("ops-team")
        mock_client.post.assert_called_once_with(
            f"/api/session/data/{DS}/userGroups",
            json={"identifier": "ops-team", "attributes": {}},
        )
        assert result["identifier"] == "ops-team"


class TestDeleteUserGroup:
    async def test_sends_delete_request(self, mock_client: AsyncMock) -> None:
        result = await user_groups.delete_user_group("admins")
        mock_client.delete.assert_called_once_with(
            f"/api/session/data/{DS}/userGroups/admins"
        )
        assert result == {"status": "ok"}
