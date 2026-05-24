"""User group management tools for Apache Guacamole.

Covers all ``/api/session/data/{data_source}/userGroups`` endpoints
including CRUD, member management, parent-group hierarchy, and
permission assignment.
"""

from __future__ import annotations

import logging
from typing import Any

from ..state import get_client

logger = logging.getLogger(__name__)


async def list_user_groups(data_source: str = "postgresql") -> dict[str, Any]:
    """List all user groups in the data source.

    Parameters
    ----------
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, Any]
        Mapping of group identifier → group object.
    """
    client = get_client()
    return await client.get(f"/api/session/data/{data_source}/userGroups")


async def get_user_group(
    user_group: str, data_source: str = "postgresql"
) -> dict[str, Any]:
    """Return details for a specific user group.

    Parameters
    ----------
    user_group : str
        User group identifier.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, Any]
        Group object with ``identifier`` and ``attributes``.
    """
    client = get_client()
    return await client.get(f"/api/session/data/{data_source}/userGroups/{user_group}")


async def add_members_to_user_group(
    user_group: str,
    usernames: list[str],
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Add users as members of a user group.

    Parameters
    ----------
    user_group : str
        Target group identifier.
    usernames : list[str]
        Usernames to add as members.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    patch = [{"op": "add", "path": "/", "value": u} for u in usernames]
    client = get_client()
    await client.patch(
        f"/api/session/data/{data_source}/userGroups/{user_group}/memberUsers",
        json=patch,
    )
    return {"status": "ok"}


async def remove_members_from_user_group(
    user_group: str,
    usernames: list[str],
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Remove users from a user group.

    Parameters
    ----------
    user_group : str
        Target group identifier.
    usernames : list[str]
        Usernames to remove.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    patch = [{"op": "remove", "path": "/", "value": u} for u in usernames]
    client = get_client()
    await client.patch(
        f"/api/session/data/{data_source}/userGroups/{user_group}/memberUsers",
        json=patch,
    )
    return {"status": "ok"}


async def add_member_groups_to_user_group(
    user_group: str,
    member_group_ids: list[str],
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Add child groups to a user group.

    Parameters
    ----------
    user_group : str
        Parent group identifier.
    member_group_ids : list[str]
        Child group identifiers to add.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    patch = [{"op": "add", "path": "/", "value": g} for g in member_group_ids]
    client = get_client()
    await client.patch(
        f"/api/session/data/{data_source}/userGroups/{user_group}/memberUserGroups",
        json=patch,
    )
    return {"status": "ok"}


async def remove_member_groups_from_user_group(
    user_group: str,
    member_group_ids: list[str],
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Remove child groups from a user group.

    Parameters
    ----------
    user_group : str
        Parent group identifier.
    member_group_ids : list[str]
        Child group identifiers to remove.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    patch = [{"op": "remove", "path": "/", "value": g} for g in member_group_ids]
    client = get_client()
    await client.patch(
        f"/api/session/data/{data_source}/userGroups/{user_group}/memberUserGroups",
        json=patch,
    )
    return {"status": "ok"}


async def add_parent_groups_to_user_group(
    user_group: str,
    parent_group_ids: list[str],
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Add parent groups to a user group (nest within existing groups).

    Parameters
    ----------
    user_group : str
        Child group identifier.
    parent_group_ids : list[str]
        Parent group identifiers.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    patch = [{"op": "add", "path": "/", "value": g} for g in parent_group_ids]
    client = get_client()
    await client.patch(
        f"/api/session/data/{data_source}/userGroups/{user_group}/userGroups",
        json=patch,
    )
    return {"status": "ok"}


async def remove_parent_groups_from_user_group(
    user_group: str,
    parent_group_ids: list[str],
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Remove parent groups from a user group.

    Parameters
    ----------
    user_group : str
        Child group identifier.
    parent_group_ids : list[str]
        Parent group identifiers to remove.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    patch = [{"op": "remove", "path": "/", "value": g} for g in parent_group_ids]
    client = get_client()
    await client.patch(
        f"/api/session/data/{data_source}/userGroups/{user_group}/userGroups",
        json=patch,
    )
    return {"status": "ok"}


async def assign_connection_permissions_to_user_group(
    user_group: str,
    connection_ids: list[str],
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Grant READ access to connections for a user group.

    Parameters
    ----------
    user_group : str
        Target group identifier.
    connection_ids : list[str]
        Connection identifiers to grant access to.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    patch = [
        {
            "op": "add",
            "path": f"/connectionPermissions/{cid}",
            "value": "READ",
        }
        for cid in connection_ids
    ]
    client = get_client()
    await client.patch(
        f"/api/session/data/{data_source}/userGroups/{user_group}/permissions",
        json=patch,
    )
    return {"status": "ok"}


async def revoke_connection_permissions_from_user_group(
    user_group: str,
    connection_ids: list[str],
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Revoke READ access to connections from a user group.

    Parameters
    ----------
    user_group : str
        Target group identifier.
    connection_ids : list[str]
        Connection identifiers to revoke.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    patch = [
        {
            "op": "remove",
            "path": f"/connectionPermissions/{cid}",
            "value": "READ",
        }
        for cid in connection_ids
    ]
    client = get_client()
    await client.patch(
        f"/api/session/data/{data_source}/userGroups/{user_group}/permissions",
        json=patch,
    )
    return {"status": "ok"}


async def assign_system_permissions_to_user_group(
    user_group: str,
    permissions: list[str],
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Grant system-level permissions to a user group.

    Parameters
    ----------
    user_group : str
        Target group identifier.
    permissions : list[str]
        System permission names (e.g. ``["CREATE_USER", "ADMINISTER"]``).
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    patch = [
        {"op": "add", "path": "/systemPermissions", "value": p} for p in permissions
    ]
    client = get_client()
    await client.patch(
        f"/api/session/data/{data_source}/userGroups/{user_group}/permissions",
        json=patch,
    )
    return {"status": "ok"}


async def revoke_system_permissions_from_user_group(
    user_group: str,
    permissions: list[str],
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Revoke system-level permissions from a user group.

    Parameters
    ----------
    user_group : str
        Target group identifier.
    permissions : list[str]
        System permission names to revoke.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    patch = [
        {"op": "remove", "path": "/systemPermissions", "value": p} for p in permissions
    ]
    client = get_client()
    await client.patch(
        f"/api/session/data/{data_source}/userGroups/{user_group}/permissions",
        json=patch,
    )
    return {"status": "ok"}


async def update_user_group(
    user_group: str,
    attributes: dict[str, Any] | None = None,
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Update attributes of an existing user group.

    Parameters
    ----------
    user_group : str
        Group identifier to update.
    attributes : dict[str, Any] | None
        Attribute key/value pairs (e.g. ``{"disabled": ""}``).
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    body: dict[str, Any] = {
        "identifier": user_group,
        "attributes": attributes or {},
    }
    client = get_client()
    await client.put(
        f"/api/session/data/{data_source}/userGroups/{user_group}",
        json=body,
    )
    return {"status": "ok"}


async def create_user_group(
    identifier: str,
    attributes: dict[str, Any] | None = None,
    data_source: str = "postgresql",
) -> dict[str, Any]:
    """Create a new user group.

    Parameters
    ----------
    identifier : str
        Unique identifier for the new group.
    attributes : dict[str, Any] | None
        Optional attribute key/value pairs.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, Any]
        The created group object.
    """
    body: dict[str, Any] = {
        "identifier": identifier,
        "attributes": attributes or {},
    }
    client = get_client()
    return await client.post(f"/api/session/data/{data_source}/userGroups", json=body)


async def delete_user_group(
    user_group: str, data_source: str = "postgresql"
) -> dict[str, str]:
    """Delete a user group.

    Parameters
    ----------
    user_group : str
        Group identifier to delete.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.delete(f"/api/session/data/{data_source}/userGroups/{user_group}")
    return {"status": "ok"}
