"""Integration tests for user management tools against a live Guacamole."""

from __future__ import annotations

import pytest

from guacamole_mcp.client import GuacamoleClient, GuacamoleNotFoundError
from guacamole_mcp.tools.users import (
    create_user,
    delete_user,
    get_self,
    get_user,
    list_users,
    update_user,
    update_user_password,
)

pytestmark = pytest.mark.integration

TEST_USER = "integration-test-user"
TEST_PASSWORD = "TestPassword123!"


@pytest.fixture()
async def temp_user(integration_client: GuacamoleClient) -> str:
    """Create a test user and clean it up afterwards.

    Yields
    ------
    str
        Username of the created user.
    """
    await create_user(username=TEST_USER, password=TEST_PASSWORD)
    yield TEST_USER
    # Cleanup — ignore if already deleted by the test
    try:
        await delete_user(username=TEST_USER)
    except Exception:
        pass


class TestListUsersIntegration:
    async def test_returns_dict(self, integration_client: GuacamoleClient) -> None:
        result = await list_users()
        assert isinstance(result, dict)

    async def test_contains_guacadmin(
        self, integration_client: GuacamoleClient
    ) -> None:
        result = await list_users()
        assert "guacadmin" in result


class TestGetSelfIntegration:
    async def test_returns_admin_user(
        self, integration_client: GuacamoleClient
    ) -> None:
        result = await get_self()
        assert isinstance(result, dict)
        assert result.get("username") == "guacadmin"


class TestCreateGetDeleteUserIntegration:
    async def test_create_user(self, integration_client: GuacamoleClient) -> None:
        """create_user() creates the user and it appears in list_users."""
        await create_user(username=TEST_USER, password=TEST_PASSWORD)
        try:
            users = await list_users()
            assert TEST_USER in users
        finally:
            await delete_user(username=TEST_USER)

    async def test_get_user(self, temp_user: str) -> None:
        """get_user() returns the user details."""
        result = await get_user(username=TEST_USER)
        assert result["username"] == TEST_USER

    async def test_delete_user(self, integration_client: GuacamoleClient) -> None:
        """delete_user() removes the user."""
        await create_user(username=TEST_USER, password=TEST_PASSWORD)
        result = await delete_user(username=TEST_USER)
        assert result == {"status": "ok"}
        users = await list_users()
        assert TEST_USER not in users

    async def test_get_nonexistent_user_raises(
        self, integration_client: GuacamoleClient
    ) -> None:
        """get_user() raises GuacamoleNotFoundError for missing users."""
        with pytest.raises(GuacamoleNotFoundError):
            await get_user(username="this-user-does-not-exist")


class TestUpdateUserIntegration:
    async def test_update_user_attributes(self, temp_user: str) -> None:
        """update_user() saves the attributes without error."""
        result = await update_user(
            username=TEST_USER,
            attributes={"guac-full-name": "Integration Test User"},
        )
        assert result == {"status": "ok"}

    async def test_update_password(self, temp_user: str) -> None:
        """update_user_password() changes the password."""
        result = await update_user_password(
            username=TEST_USER,
            old_password=TEST_PASSWORD,
            new_password="NewPassword456!",
        )
        assert result == {"status": "ok"}
