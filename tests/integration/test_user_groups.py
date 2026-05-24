"""Integration tests for user-group management tools against a live Guacamole."""

from __future__ import annotations

import pytest

from guacamole_mcp.client import GuacamoleClient, GuacamoleNotFoundError
from guacamole_mcp.tools.user_groups import (
    add_members_to_user_group,
    create_user_group,
    delete_user_group,
    get_user_group,
    list_user_groups,
    remove_members_from_user_group,
)
from guacamole_mcp.tools.users import create_user, delete_user

pytestmark = pytest.mark.integration

TEST_GROUP = "integration-test-group"
TEST_MEMBER = "integration-group-member"
TEST_PASS = "TestPassword123!"


@pytest.fixture()
async def temp_group(integration_client: GuacamoleClient) -> str:
    """Create a test user group and clean it up afterwards."""
    await create_user_group(identifier=TEST_GROUP)
    yield TEST_GROUP
    try:
        await delete_user_group(user_group=TEST_GROUP)
    except Exception:
        pass


@pytest.fixture()
async def temp_member(integration_client: GuacamoleClient) -> str:
    """Create a test user to use as a group member and clean up afterwards."""
    await create_user(username=TEST_MEMBER, password=TEST_PASS)
    yield TEST_MEMBER
    try:
        await delete_user(username=TEST_MEMBER)
    except Exception:
        pass


class TestListUserGroupsIntegration:
    async def test_returns_dict(self, integration_client: GuacamoleClient) -> None:
        result = await list_user_groups()
        assert isinstance(result, dict)


class TestCreateGetDeleteGroupIntegration:
    async def test_create_group(self, integration_client: GuacamoleClient) -> None:
        """create_user_group() creates the group and it appears in list."""
        await create_user_group(identifier=TEST_GROUP)
        try:
            groups = await list_user_groups()
            assert TEST_GROUP in groups
        finally:
            await delete_user_group(user_group=TEST_GROUP)

    async def test_get_group(self, temp_group: str) -> None:
        """get_user_group() returns the group details."""
        result = await get_user_group(user_group=TEST_GROUP)
        assert result["identifier"] == TEST_GROUP

    async def test_delete_group(self, integration_client: GuacamoleClient) -> None:
        """delete_user_group() removes the group."""
        await create_user_group(identifier=TEST_GROUP)
        result = await delete_user_group(user_group=TEST_GROUP)
        assert result == {"status": "ok"}
        groups = await list_user_groups()
        assert TEST_GROUP not in groups

    async def test_get_nonexistent_group_raises(
        self, integration_client: GuacamoleClient
    ) -> None:
        with pytest.raises(GuacamoleNotFoundError):
            await get_user_group(user_group="no-such-group")


class TestGroupMembershipIntegration:
    async def test_add_and_remove_member(
        self, temp_group: str, temp_member: str
    ) -> None:
        """add_members_to_user_group then remove_members works round-trip."""
        add_result = await add_members_to_user_group(
            user_group=TEST_GROUP,
            usernames=[TEST_MEMBER],
        )
        assert add_result == {"status": "ok"}

        remove_result = await remove_members_from_user_group(
            user_group=TEST_GROUP,
            usernames=[TEST_MEMBER],
        )
        assert remove_result == {"status": "ok"}
