"""FastMCP server for Apache Guacamole.

Registers all tool functions and exposes a :func:`run` entry point that
honours the ``GUACAMOLE_TRANSPORT``, ``HOST``, and ``PORT`` environment
variables for choosing between stdio and SSE transports.
"""

from __future__ import annotations

import logging

from fastmcp import FastMCP

from .tools import auth, connection_groups, connections, history, user_groups, users

logger = logging.getLogger(__name__)

mcp = FastMCP(
    "Apache Guacamole MCP",
    instructions=(
        "MCP server for managing Apache Guacamole via its REST API. "
        "Provides tools for creating and managing connections (RDP, SSH, VNC, "
        "Telnet, Kubernetes), users, user groups, connection groups, active "
        "session monitoring, and audit history. "
        "Configure the server via environment variables: GUACAMOLE_URL, "
        "GUACAMOLE_USERNAME, GUACAMOLE_PASSWORD, GUACAMOLE_DATA_SOURCE."
    ),
)

# ── Authentication ──────────────────────────────────────────────────────────
mcp.tool()(auth.authenticate)
mcp.tool()(auth.logout)

# ── Users ───────────────────────────────────────────────────────────────────
mcp.tool()(users.list_users)
mcp.tool()(users.get_user)
mcp.tool()(users.get_self)
mcp.tool()(users.get_user_permissions)
mcp.tool()(users.get_user_effective_permissions)
mcp.tool()(users.get_user_groups)
mcp.tool()(users.get_user_history)
mcp.tool()(users.assign_user_to_groups)
mcp.tool()(users.revoke_user_from_groups)
mcp.tool()(users.grant_user_connection_permissions)
mcp.tool()(users.revoke_user_connection_permissions)
mcp.tool()(users.grant_user_connection_group_permissions)
mcp.tool()(users.revoke_user_connection_group_permissions)
mcp.tool()(users.grant_user_system_permissions)
mcp.tool()(users.revoke_user_system_permissions)
mcp.tool()(users.update_user_password)
mcp.tool()(users.update_user)
mcp.tool()(users.create_user)
mcp.tool()(users.delete_user)

# ── User Groups ─────────────────────────────────────────────────────────────
mcp.tool()(user_groups.list_user_groups)
mcp.tool()(user_groups.get_user_group)
mcp.tool()(user_groups.add_members_to_user_group)
mcp.tool()(user_groups.remove_members_from_user_group)
mcp.tool()(user_groups.add_member_groups_to_user_group)
mcp.tool()(user_groups.remove_member_groups_from_user_group)
mcp.tool()(user_groups.add_parent_groups_to_user_group)
mcp.tool()(user_groups.remove_parent_groups_from_user_group)
mcp.tool()(user_groups.assign_connection_permissions_to_user_group)
mcp.tool()(user_groups.revoke_connection_permissions_from_user_group)
mcp.tool()(user_groups.assign_system_permissions_to_user_group)
mcp.tool()(user_groups.revoke_system_permissions_from_user_group)
mcp.tool()(user_groups.update_user_group)
mcp.tool()(user_groups.create_user_group)
mcp.tool()(user_groups.delete_user_group)

# ── Connections ─────────────────────────────────────────────────────────────
mcp.tool()(connections.list_connections)
mcp.tool()(connections.get_connection)
mcp.tool()(connections.get_connection_parameters)
mcp.tool()(connections.get_connection_history)
mcp.tool()(connections.get_connection_sharing_profiles)
mcp.tool()(connections.list_sharing_profiles)
mcp.tool()(connections.list_active_connections)
mcp.tool()(connections.kill_connections)
mcp.tool()(connections.create_connection)
mcp.tool()(connections.update_connection)
mcp.tool()(connections.delete_connection)

# ── Connection Groups ────────────────────────────────────────────────────────
mcp.tool()(connection_groups.list_connection_groups)
mcp.tool()(connection_groups.list_connection_tree)
mcp.tool()(connection_groups.get_connection_group)
mcp.tool()(connection_groups.get_connection_group_tree)
mcp.tool()(connection_groups.create_connection_group)
mcp.tool()(connection_groups.update_connection_group)
mcp.tool()(connection_groups.delete_connection_group)

# ── History ──────────────────────────────────────────────────────────────────
mcp.tool()(history.list_connection_history)
mcp.tool()(history.list_user_history)


def run() -> None:
    """Start the MCP server using the configured transport.

    Transport is controlled by the ``GUACAMOLE_TRANSPORT`` environment
    variable (``stdio`` or ``sse``).  When ``sse`` is chosen the server
    binds to ``HOST``/``PORT`` (default ``0.0.0.0:8000``).
    """
    from .config import get_config

    config = get_config()
    transport = config.transport.lower()

    if transport == "sse":
        logger.info("Starting SSE server on %s:%d", config.host, config.port)
        mcp.run(transport="sse", host=config.host, port=config.port)
    else:
        logger.info("Starting stdio server")
        mcp.run(transport="stdio")
