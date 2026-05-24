"""Connection group management tools for Apache Guacamole.

Covers ``/api/session/data/{data_source}/connectionGroups`` endpoints
including CRUD operations and connection tree retrieval.
"""

from __future__ import annotations

import logging
from typing import Any

from ..state import get_client

logger = logging.getLogger(__name__)


async def list_connection_groups(
    data_source: str = "postgresql",
) -> dict[str, Any]:
    """List all connection groups (folders) in the data source.

    Parameters
    ----------
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, Any]
        Mapping of connection group identifier → group object.
    """
    client = get_client()
    return await client.get(f"/api/session/data/{data_source}/connectionGroups")


async def list_connection_tree(
    data_source: str = "postgresql",
) -> dict[str, Any]:
    """Return the full ROOT connection tree (connections + groups).

    This is equivalent to browsing the connection panel in the Guacamole
    web interface.

    Parameters
    ----------
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, Any]
        Nested tree object rooted at ROOT.
    """
    client = get_client()
    return await client.get(
        f"/api/session/data/{data_source}/connectionGroups/ROOT/tree"
    )


async def get_connection_group(
    connection_group_id: str, data_source: str = "postgresql"
) -> dict[str, Any]:
    """Return details for a specific connection group.

    Parameters
    ----------
    connection_group_id : str
        Numeric connection group identifier.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, Any]
        Connection group object.
    """
    client = get_client()
    return await client.get(
        f"/api/session/data/{data_source}/connectionGroups/{connection_group_id}"
    )


async def get_connection_group_tree(
    connection_group_id: str,
    permission: str | None = None,
    data_source: str = "postgresql",
) -> dict[str, Any]:
    """Return the connection tree rooted at a specific group.

    Parameters
    ----------
    connection_group_id : str
        Numeric connection group identifier (root of the sub-tree).
    permission : str | None
        Optional permission filter (e.g. ``READ``).
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, Any]
        Nested tree object.
    """
    params: dict[str, str] = {}
    if permission is not None:
        params["permission"] = permission

    client = get_client()
    return await client.get(
        f"/api/session/data/{data_source}/connectionGroups/{connection_group_id}/tree",
        params=params,
    )


async def create_connection_group(
    name: str,
    group_type: str = "ORGANIZATIONAL",
    parent_identifier: str = "ROOT",
    attributes: dict[str, Any] | None = None,
    data_source: str = "postgresql",
) -> dict[str, Any]:
    """Create a new connection group (folder).

    Parameters
    ----------
    name : str
        Display name for the group.
    group_type : str
        Group type: ``ORGANIZATIONAL`` (folder) or ``BALANCING``
        (load-balanced pool). Default: ``ORGANIZATIONAL``.
    parent_identifier : str
        Identifier of the parent connection group. Default: ``ROOT``.
    attributes : dict[str, Any] | None
        Optional attributes, e.g. ``max-connections``,
        ``max-connections-per-user``, ``enable-session-affinity``.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, Any]
        The created connection group object including its identifier.
    """
    body: dict[str, Any] = {
        "name": name,
        "type": group_type,
        "parentIdentifier": parent_identifier,
        "attributes": attributes or {},
    }
    client = get_client()
    return await client.post(
        f"/api/session/data/{data_source}/connectionGroups", json=body
    )


async def update_connection_group(
    connection_group_id: str,
    name: str,
    group_type: str = "ORGANIZATIONAL",
    parent_identifier: str = "ROOT",
    attributes: dict[str, Any] | None = None,
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Update an existing connection group.

    Parameters
    ----------
    connection_group_id : str
        Numeric identifier of the group to update.
    name : str
        New display name.
    group_type : str
        Group type (``ORGANIZATIONAL`` or ``BALANCING``).
    parent_identifier : str
        Parent connection group identifier.
    attributes : dict[str, Any] | None
        Attributes to set.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    body: dict[str, Any] = {
        "identifier": connection_group_id,
        "name": name,
        "type": group_type,
        "parentIdentifier": parent_identifier,
        "attributes": attributes or {},
    }
    client = get_client()
    await client.put(
        f"/api/session/data/{data_source}/connectionGroups/{connection_group_id}",
        json=body,
    )
    return {"status": "ok"}


async def delete_connection_group(
    connection_group_id: str, data_source: str = "postgresql"
) -> dict[str, str]:
    """Delete a connection group.

    .. warning::
        Deleting a non-empty group may fail depending on the server
        configuration.  Remove child connections first if needed.

    Parameters
    ----------
    connection_group_id : str
        Numeric identifier of the group to delete.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.delete(
        f"/api/session/data/{data_source}/connectionGroups/{connection_group_id}"
    )
    return {"status": "ok"}
