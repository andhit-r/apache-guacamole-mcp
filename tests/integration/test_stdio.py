"""Integration tests for the MCP server via stdio transport.

These tests start ``guacamole-mcp`` as a real subprocess and communicate
with it using the Model Context Protocol over stdin/stdout.  They verify
the full stack: transport → MCP protocol → tool dispatch → Guacamole REST API.

Requirements
------------
* A running Apache Guacamole instance (provided by the pytest-docker fixture
  ``guacamole_url`` defined in ``conftest.py``).
* The ``guacamole-mcp`` package installed in the active Python environment.

Run these tests together with the other integration tests::

    pytest tests/integration/ -v
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, AsyncGenerator

import pytest
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from mcp.types import TextContent

pytestmark = pytest.mark.integration

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

EXPECTED_TOOLS = {
    "authenticate",
    "logout",
    "list_connections",
    "get_connection",
    "create_connection",
    "delete_connection",
    "list_users",
    "get_user",
    "create_user",
    "delete_user",
    "list_user_groups",
    "get_user_group",
    "create_user_group",
    "delete_user_group",
    "list_connection_groups",
    "list_connection_tree",
    "create_connection_group",
    "delete_connection_group",
    "list_connection_history",
    "list_user_history",
}


def _parse_result(result: Any) -> Any:
    """Extract the parsed result from a FastMCP CallToolResult.

    FastMCP 3.x serialises non-empty dicts/objects as JSON in
    ``content[0].text``, but stores empty lists in ``.data`` with an
    empty ``content`` list.  This helper handles both cases.
    """
    if result.content:
        # Standard case: first content item holds JSON text
        first = result.content[0]
        assert isinstance(first, TextContent), f"Expected TextContent, got {type(first)}"
        return json.loads(first.text)
    # Empty-content case (e.g. empty list): FastMCP stores result in .data
    if hasattr(result, "data"):
        return result.data
    return None


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
async def mcp_client(guacamole_url: str) -> AsyncGenerator[Client, None]:
    """A :class:`fastmcp.Client` connected to a ``guacamole-mcp`` subprocess.

    The subprocess is started with environment variables pointing to the
    ephemeral Guacamole Docker instance provided by the session-scoped
    ``guacamole_url`` fixture.

    Yields
    ------
    Client
        An initialised FastMCP client communicating over stdio.
    """
    env = {
        **os.environ,
        "GUACAMOLE_URL": guacamole_url,
        "GUACAMOLE_USERNAME": "guacadmin",
        "GUACAMOLE_PASSWORD": "guacadmin",
        "GUACAMOLE_DATA_SOURCE": "postgresql",
        "TRANSPORT": "stdio",
    }
    transport = StdioTransport(
        command=sys.executable,
        args=["-m", "guacamole_mcp"],
        env=env,
    )
    async with Client(transport) as client:
        yield client


# ---------------------------------------------------------------------------
# Test classes
# ---------------------------------------------------------------------------


class TestMcpServerInitStdio:
    """Verify the MCP server initialises correctly over stdio."""

    async def test_list_tools_returns_expected_tools(
        self, mcp_client: Client
    ) -> None:
        """list_tools() returns at least the core tool set."""
        tools = await mcp_client.list_tools()
        tool_names = {t.name for t in tools}
        for expected in EXPECTED_TOOLS:
            assert expected in tool_names, f"Tool '{expected}' not registered"

    async def test_tool_annotations_have_description(
        self, mcp_client: Client
    ) -> None:
        """Every tool has a non-empty description."""
        tools = await mcp_client.list_tools()
        for tool in tools:
            assert tool.description, f"Tool '{tool.name}' has no description"


class TestAuthViaStdio:
    """Authenticate and logout through the MCP protocol."""

    async def test_authenticate_returns_token(self, mcp_client: Client) -> None:
        """authenticate() uses env credentials and returns authToken."""
        # authenticate() takes no parameters — credentials come from env vars.
        result = await mcp_client.call_tool("authenticate", {})
        data = _parse_result(result)
        assert "authToken" in data
        assert isinstance(data["authToken"], str)
        assert data["authToken"]

    async def test_authenticate_status_field(self, mcp_client: Client) -> None:
        """authenticate() result includes status field."""
        result = await mcp_client.call_tool("authenticate", {})
        data = _parse_result(result)
        assert data.get("status") == "authenticated"


class TestConnectionToolsViaStdio:
    """Connection CRUD through the MCP protocol."""

    async def test_list_connections_returns_dict(
        self, mcp_client: Client
    ) -> None:
        """list_connections() returns a JSON object."""
        result = await mcp_client.call_tool("list_connections", {})
        data = _parse_result(result)
        assert isinstance(data, dict)

    async def test_create_and_delete_connection(
        self, mcp_client: Client
    ) -> None:
        """create_connection() and delete_connection() round-trip via stdio."""
        create_result = await mcp_client.call_tool(
            "create_connection",
            {
                "name": "stdio-test-conn",
                "protocol": "ssh",
                "parameters": {"hostname": "192.0.2.1", "port": "22"},
            },
        )
        conn = _parse_result(create_result)
        assert "identifier" in conn
        conn_id = conn["identifier"]

        try:
            # Verify it appears in the list
            list_result = await mcp_client.call_tool("list_connections", {})
            conns = _parse_result(list_result)
            assert conn_id in conns
        finally:
            del_result = await mcp_client.call_tool(
                "delete_connection", {"connection_id": conn_id}
            )
            del_data = _parse_result(del_result)
            assert del_data == {"status": "ok"}

    async def test_get_nonexistent_connection_returns_error(
        self, mcp_client: Client
    ) -> None:
        """get_connection() with unknown ID returns an MCP tool error."""
        result = await mcp_client.call_tool(
            "get_connection",
            {"connection_id": "99999999"},
            raise_on_error=False,
        )
        assert result.is_error is True


class TestUserToolsViaStdio:
    """User management through the MCP protocol."""

    async def test_list_users_contains_guacadmin(
        self, mcp_client: Client
    ) -> None:
        """list_users() returns a dict that includes the built-in admin."""
        result = await mcp_client.call_tool("list_users", {})
        data = _parse_result(result)
        assert isinstance(data, dict)
        assert "guacadmin" in data

    async def test_create_and_delete_user(self, mcp_client: Client) -> None:
        """create_user() and delete_user() round-trip via stdio."""
        create_result = await mcp_client.call_tool(
            "create_user",
            {"username": "stdio-test-user", "password": "TestPass123!"},
        )
        user = _parse_result(create_result)
        assert user.get("username") == "stdio-test-user"

        try:
            list_result = await mcp_client.call_tool("list_users", {})
            users = _parse_result(list_result)
            assert "stdio-test-user" in users
        finally:
            del_result = await mcp_client.call_tool(
                "delete_user", {"username": "stdio-test-user"}
            )
            del_data = _parse_result(del_result)
            assert del_data == {"status": "ok"}


class TestUserGroupToolsViaStdio:
    """User group management through the MCP protocol."""

    async def test_list_user_groups_returns_dict(
        self, mcp_client: Client
    ) -> None:
        """list_user_groups() returns a JSON object."""
        result = await mcp_client.call_tool("list_user_groups", {})
        data = _parse_result(result)
        assert isinstance(data, dict)

    async def test_create_and_delete_user_group(
        self, mcp_client: Client
    ) -> None:
        """create_user_group() and delete_user_group() round-trip via stdio."""
        create_result = await mcp_client.call_tool(
            "create_user_group",
            {"identifier": "stdio-test-group"},
        )
        group = _parse_result(create_result)
        assert group.get("identifier") == "stdio-test-group"

        try:
            list_result = await mcp_client.call_tool("list_user_groups", {})
            groups = _parse_result(list_result)
            assert "stdio-test-group" in groups
        finally:
            del_result = await mcp_client.call_tool(
                "delete_user_group", {"user_group": "stdio-test-group"}
            )
            del_data = _parse_result(del_result)
            assert del_data == {"status": "ok"}


class TestConnectionGroupToolsViaStdio:
    """Connection group management through the MCP protocol."""

    async def test_list_connection_tree_has_root(
        self, mcp_client: Client
    ) -> None:
        """list_connection_tree() returns the ROOT node."""
        result = await mcp_client.call_tool("list_connection_tree", {})
        data = _parse_result(result)
        assert data.get("identifier") == "ROOT"

    async def test_create_and_delete_connection_group(
        self, mcp_client: Client
    ) -> None:
        """create_connection_group() and delete_connection_group() round-trip."""
        create_result = await mcp_client.call_tool(
            "create_connection_group",
            {"name": "stdio-test-group", "group_type": "ORGANIZATIONAL"},
        )
        group = _parse_result(create_result)
        assert "identifier" in group
        group_id = group["identifier"]

        try:
            list_result = await mcp_client.call_tool(
                "list_connection_groups", {}
            )
            groups = _parse_result(list_result)
            assert group_id in groups
        finally:
            del_result = await mcp_client.call_tool(
                "delete_connection_group",
                {"connection_group_id": group_id},
            )
            del_data = _parse_result(del_result)
            assert del_data == {"status": "ok"}


class TestHistoryViaStdio:
    """History queries through the MCP protocol."""

    async def test_list_connection_history_returns_list(
        self, mcp_client: Client
    ) -> None:
        """list_connection_history() returns a JSON array."""
        result = await mcp_client.call_tool("list_connection_history", {})
        data = _parse_result(result)
        assert isinstance(data, list)

    async def test_list_user_history_returns_list(
        self, mcp_client: Client
    ) -> None:
        """list_user_history() returns a JSON array."""
        result = await mcp_client.call_tool("list_user_history", {})
        data = _parse_result(result)
        assert isinstance(data, list)
