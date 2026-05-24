"""Connection management tools for Apache Guacamole.

Covers ``/api/session/data/{data_source}/connections``,
``/activeConnections``, and ``/sharingProfiles`` endpoints.
Supports creating connections for the VNC, SSH, RDP, Telnet, and
Kubernetes protocols.
"""

from __future__ import annotations

import logging
from typing import Any

from ..state import get_client

logger = logging.getLogger(__name__)


async def list_connections(data_source: str = "postgresql") -> dict[str, Any]:
    """List all connections in the data source.

    Parameters
    ----------
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, Any]
        Mapping of connection identifier → connection object.
    """
    client = get_client()
    return await client.get(f"/api/session/data/{data_source}/connections")


async def get_connection(
    connection_id: str, data_source: str = "postgresql"
) -> dict[str, Any]:
    """Return details for a specific connection.

    Parameters
    ----------
    connection_id : str
        Numeric connection identifier.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, Any]
        Connection object.
    """
    client = get_client()
    return await client.get(
        f"/api/session/data/{data_source}/connections/{connection_id}"
    )


async def get_connection_parameters(
    connection_id: str, data_source: str = "postgresql"
) -> dict[str, Any]:
    """Return the full parameter set for a connection.

    .. note::
        This endpoint requires administrator privileges.

    Parameters
    ----------
    connection_id : str
        Numeric connection identifier.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, Any]
        Protocol-specific parameter key/value pairs.
    """
    client = get_client()
    return await client.get(
        f"/api/session/data/{data_source}/connections/{connection_id}/parameters"
    )


async def get_connection_history(
    connection_id: str, data_source: str = "postgresql"
) -> list[Any]:
    """Return the connection usage history.

    Parameters
    ----------
    connection_id : str
        Numeric connection identifier.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    list[Any]
        List of history records.
    """
    client = get_client()
    return await client.get(
        f"/api/session/data/{data_source}/connections/{connection_id}/history"
    )


async def get_connection_sharing_profiles(
    connection_id: str, data_source: str = "postgresql"
) -> dict[str, Any]:
    """Return the sharing profiles associated with a connection.

    Parameters
    ----------
    connection_id : str
        Numeric connection identifier.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, Any]
        Mapping of sharing profile identifier → profile object.
    """
    client = get_client()
    return await client.get(
        f"/api/session/data/{data_source}/connections/{connection_id}/sharingProfiles"
    )


async def list_sharing_profiles(
    data_source: str = "postgresql",
) -> dict[str, Any]:
    """List all sharing profiles in the data source.

    Parameters
    ----------
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, Any]
        Mapping of sharing profile identifier → profile object.
    """
    client = get_client()
    return await client.get(f"/api/session/data/{data_source}/sharingProfiles")


async def list_active_connections(
    data_source: str = "postgresql",
) -> dict[str, Any]:
    """List all currently active (open) connections.

    Parameters
    ----------
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, Any]
        Mapping of active-connection identifier → active connection object.
    """
    client = get_client()
    return await client.get(f"/api/session/data/{data_source}/activeConnections")


async def kill_connections(
    active_connection_ids: list[str],
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Forcibly terminate one or more active connections.

    Parameters
    ----------
    active_connection_ids : list[str]
        Identifiers of the active connections to kill.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    patch = [{"op": "remove", "path": f"/{cid}"} for cid in active_connection_ids]
    client = get_client()
    await client.patch(f"/api/session/data/{data_source}/activeConnections", json=patch)
    return {"status": "ok"}


async def create_connection(
    name: str,
    protocol: str,
    parameters: dict[str, Any],
    attributes: dict[str, Any] | None = None,
    parent_identifier: str = "ROOT",
    data_source: str = "postgresql",
) -> dict[str, Any]:
    """Create a new connection.

    Parameters
    ----------
    name : str
        Display name for the connection.
    protocol : str
        Protocol type: ``vnc``, ``ssh``, ``rdp``, ``telnet``, or
        ``kubernetes``.
    parameters : dict[str, Any]
        Protocol-specific connection parameters.  For SSH, common keys
        include ``hostname``, ``port``, ``username``, ``password``.
        For RDP: ``hostname``, ``port``, ``username``, ``password``,
        ``domain``.  For VNC: ``hostname``, ``port``, ``password``.
    attributes : dict[str, Any] | None
        Optional connection attributes such as ``max-connections``,
        ``max-connections-per-user``, ``guacd-hostname``.
    parent_identifier : str
        Identifier of the parent connection group (default: ``ROOT``).
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, Any]
        The created connection object including its assigned identifier.

    Examples
    --------
    >>> conn = await create_connection(
    ...     name="My Server",
    ...     protocol="ssh",
    ...     parameters={"hostname": "10.0.0.1", "port": "22", "username": "admin"},
    ... )
    >>> print(conn["identifier"])
    """
    body: dict[str, Any] = {
        "name": name,
        "protocol": protocol,
        "parentIdentifier": parent_identifier,
        "parameters": parameters,
        "attributes": attributes or {},
    }
    client = get_client()
    return await client.post(f"/api/session/data/{data_source}/connections", json=body)


async def update_connection(
    connection_id: str,
    name: str,
    protocol: str,
    parameters: dict[str, Any],
    attributes: dict[str, Any] | None = None,
    parent_identifier: str = "ROOT",
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Update an existing connection.

    Parameters
    ----------
    connection_id : str
        Numeric identifier of the connection to update.
    name : str
        New display name.
    protocol : str
        Protocol type (``vnc``, ``ssh``, ``rdp``, ``telnet``,
        ``kubernetes``).
    parameters : dict[str, Any]
        Full set of protocol parameters (replaces existing parameters).
    attributes : dict[str, Any] | None
        Connection attributes to set.
    parent_identifier : str
        Parent connection group identifier.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    body: dict[str, Any] = {
        "identifier": connection_id,
        "name": name,
        "protocol": protocol,
        "parentIdentifier": parent_identifier,
        "parameters": parameters,
        "attributes": attributes or {},
    }
    client = get_client()
    await client.put(
        f"/api/session/data/{data_source}/connections/{connection_id}",
        json=body,
    )
    return {"status": "ok"}


async def delete_connection(
    connection_id: str, data_source: str = "postgresql"
) -> dict[str, str]:
    """Delete a connection.

    Parameters
    ----------
    connection_id : str
        Numeric identifier of the connection to delete.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.delete(f"/api/session/data/{data_source}/connections/{connection_id}")
    return {"status": "ok"}
