"""Integration tests for connection management tools against a live Guacamole."""

from __future__ import annotations

import pytest

from guacamole_mcp.client import GuacamoleClient, GuacamoleNotFoundError
from guacamole_mcp.tools.connections import (
    create_connection,
    delete_connection,
    get_connection,
    get_connection_parameters,
    list_active_connections,
    list_connections,
)

pytestmark = pytest.mark.integration

# Minimal SSH connection for tests (no real host needed — just checks API behaviour)
SSH_PARAMS = {"hostname": "192.0.2.1", "port": "22"}


@pytest.fixture()
async def temp_connection(integration_client: GuacamoleClient) -> dict:
    """Create a test SSH connection and clean up afterwards.

    Yields
    ------
    dict
        The created connection object returned by the API.
    """
    conn = await create_connection(
        name="integration-test-ssh",
        protocol="ssh",
        parameters=SSH_PARAMS,
    )
    yield conn
    try:
        await delete_connection(connection_id=conn["identifier"])
    except Exception:
        pass


class TestListConnectionsIntegration:
    async def test_returns_dict(self, integration_client: GuacamoleClient) -> None:
        result = await list_connections()
        assert isinstance(result, dict)


class TestCreateGetDeleteConnectionIntegration:
    async def test_create_connection(
        self, integration_client: GuacamoleClient
    ) -> None:
        """create_connection() creates an SSH connection successfully."""
        conn = await create_connection(
            name="integration-test-ssh",
            protocol="ssh",
            parameters=SSH_PARAMS,
        )
        try:
            assert "identifier" in conn
            assert conn["name"] == "integration-test-ssh"
            assert conn["protocol"] == "ssh"
        finally:
            await delete_connection(connection_id=conn["identifier"])

    async def test_get_connection(self, temp_connection: dict) -> None:
        """get_connection() returns the connection details."""
        result = await get_connection(
            connection_id=temp_connection["identifier"]
        )
        assert result["identifier"] == temp_connection["identifier"]
        assert result["protocol"] == "ssh"

    async def test_get_connection_parameters(
        self, temp_connection: dict
    ) -> None:
        """get_connection_parameters() returns the connection parameters."""
        result = await get_connection_parameters(
            connection_id=temp_connection["identifier"]
        )
        assert isinstance(result, dict)
        assert result.get("hostname") == SSH_PARAMS["hostname"]

    async def test_delete_connection(
        self, integration_client: GuacamoleClient
    ) -> None:
        """delete_connection() removes the connection."""
        conn = await create_connection(
            name="integration-test-ssh",
            protocol="ssh",
            parameters=SSH_PARAMS,
        )
        result = await delete_connection(connection_id=conn["identifier"])
        assert result == {"status": "ok"}
        connections = await list_connections()
        assert conn["identifier"] not in connections

    async def test_get_nonexistent_connection_raises(
        self, integration_client: GuacamoleClient
    ) -> None:
        with pytest.raises(GuacamoleNotFoundError):
            await get_connection(connection_id="99999999")


class TestActiveConnectionsIntegration:
    async def test_list_active_connections_returns_dict(
        self, integration_client: GuacamoleClient
    ) -> None:
        """list_active_connections() returns a dict (may be empty in test env)."""
        result = await list_active_connections()
        assert isinstance(result, dict)
