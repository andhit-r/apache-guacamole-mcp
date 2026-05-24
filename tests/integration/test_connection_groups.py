"""Integration tests for connection-group and history tools against a live Guacamole."""

from __future__ import annotations

import pytest

from guacamole_mcp.client import GuacamoleClient, GuacamoleNotFoundError
from guacamole_mcp.tools.connection_groups import (
    create_connection_group,
    delete_connection_group,
    get_connection_group,
    list_connection_groups,
    list_connection_tree,
)
from guacamole_mcp.tools.history import list_connection_history, list_user_history

pytestmark = pytest.mark.integration

TEST_GROUP = "integration-test-conn-group"


@pytest.fixture()
async def temp_conn_group(integration_client: GuacamoleClient) -> dict:
    """Create a test connection group and clean up afterwards."""
    group = await create_connection_group(
        name=TEST_GROUP,
        group_type="ORGANIZATIONAL",
    )
    yield group
    try:
        await delete_connection_group(connection_group_id=group["identifier"])
    except Exception:
        pass


class TestListConnectionGroupsIntegration:
    async def test_returns_dict(self, integration_client: GuacamoleClient) -> None:
        result = await list_connection_groups()
        assert isinstance(result, dict)

    async def test_each_group_has_identifier(self, temp_conn_group: dict) -> None:
        """Each connection group in the list has an 'identifier' field."""
        result = await list_connection_groups()
        assert temp_conn_group["identifier"] in result


class TestConnectionTreeIntegration:
    async def test_root_tree_returns_dict(
        self, integration_client: GuacamoleClient
    ) -> None:
        result = await list_connection_tree()
        assert isinstance(result, dict)
        assert result.get("identifier") == "ROOT"


class TestCreateGetDeleteConnectionGroupIntegration:
    async def test_create_group(self, integration_client: GuacamoleClient) -> None:
        group = await create_connection_group(
            name=TEST_GROUP, group_type="ORGANIZATIONAL"
        )
        try:
            assert "identifier" in group
            assert group["name"] == TEST_GROUP
        finally:
            await delete_connection_group(connection_group_id=group["identifier"])

    async def test_get_group(self, temp_conn_group: dict) -> None:
        result = await get_connection_group(
            connection_group_id=temp_conn_group["identifier"]
        )
        assert result["identifier"] == temp_conn_group["identifier"]

    async def test_delete_group(self, integration_client: GuacamoleClient) -> None:
        group = await create_connection_group(
            name=TEST_GROUP, group_type="ORGANIZATIONAL"
        )
        result = await delete_connection_group(connection_group_id=group["identifier"])
        assert result == {"status": "ok"}

    async def test_get_nonexistent_group_raises(
        self, integration_client: GuacamoleClient
    ) -> None:
        with pytest.raises(GuacamoleNotFoundError):
            await get_connection_group(connection_group_id="99999999")


class TestHistoryIntegration:
    async def test_list_connection_history_returns_list(
        self, integration_client: GuacamoleClient
    ) -> None:
        """list_connection_history() returns a list (may be empty)."""
        result = await list_connection_history()
        assert isinstance(result, list)

    async def test_list_user_history_returns_list(
        self, integration_client: GuacamoleClient
    ) -> None:
        """list_user_history() returns a list (may be empty)."""
        result = await list_user_history()
        assert isinstance(result, list)
