"""User management tools for Apache Guacamole.

Covers all ``/api/session/data/{data_source}/users`` endpoints including
CRUD operations, password changes, and permission/group assignment.
"""

from __future__ import annotations

import logging
from typing import Any

from ..state import get_client

logger = logging.getLogger(__name__)


async def list_users(data_source: str = "postgresql") -> dict[str, Any]:
    """List all users in the Guacamole data source.

    Parameters
    ----------
    data_source : str
        Guacamole data-source identifier (default: ``postgresql``).

    Returns
    -------
    dict[str, Any]
        Mapping of ``username`` → user object.

    Examples
    --------
    >>> users = await list_users()
    """
    client = get_client()
    return await client.get(f"/api/session/data/{data_source}/users")


async def get_user(username: str, data_source: str = "postgresql") -> dict[str, Any]:
    """Retrieve details for a specific user.

    Parameters
    ----------
    username : str
        The username to look up.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, Any]
        User object with ``username`` and ``attributes`` fields.
    """
    client = get_client()
    return await client.get(f"/api/session/data/{data_source}/users/{username}")


async def get_self(data_source: str = "postgresql") -> dict[str, Any]:
    """Return details for the currently authenticated user (token owner).

    Parameters
    ----------
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, Any]
        User object for the authenticated account.
    """
    client = get_client()
    return await client.get(f"/api/session/data/{data_source}/self")


async def get_user_permissions(
    username: str, data_source: str = "postgresql"
) -> dict[str, Any]:
    """Return the permissions assigned to a user.

    Parameters
    ----------
    username : str
        Target username.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, Any]
        Permissions object containing ``connectionPermissions``,
        ``connectionGroupPermissions``, and ``systemPermissions``.
    """
    client = get_client()
    return await client.get(
        f"/api/session/data/{data_source}/users/{username}/permissions"
    )


async def get_user_effective_permissions(
    username: str, data_source: str = "postgresql"
) -> dict[str, Any]:
    """Return the *effective* permissions for a user (including inherited ones).

    Parameters
    ----------
    username : str
        Target username.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, Any]
        Effective permissions object.
    """
    client = get_client()
    return await client.get(
        f"/api/session/data/{data_source}/users/{username}/effectivePermissions"
    )


async def get_user_groups(
    username: str, data_source: str = "postgresql"
) -> dict[str, Any]:
    """Return the user groups a user belongs to.

    Parameters
    ----------
    username : str
        Target username.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, Any]
        Mapping of group identifier → group object.
    """
    client = get_client()
    return await client.get(
        f"/api/session/data/{data_source}/users/{username}/userGroups"
    )


async def get_user_history(username: str, data_source: str = "postgresql") -> list[Any]:
    """Return the login/logout history for a user.

    Parameters
    ----------
    username : str
        Target username.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    list[Any]
        List of history records.
    """
    client = get_client()
    return await client.get(f"/api/session/data/{data_source}/users/{username}/history")


async def assign_user_to_groups(
    username: str,
    group_identifiers: list[str],
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Add a user to one or more user groups.

    Parameters
    ----------
    username : str
        Target username.
    group_identifiers : list[str]
        List of group identifiers to add the user to.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    patch = [{"op": "add", "path": "/", "value": g} for g in group_identifiers]
    client = get_client()
    await client.patch(
        f"/api/session/data/{data_source}/users/{username}/userGroups",
        json=patch,
    )
    return {"status": "ok"}


async def revoke_user_from_groups(
    username: str,
    group_identifiers: list[str],
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Remove a user from one or more user groups.

    Parameters
    ----------
    username : str
        Target username.
    group_identifiers : list[str]
        List of group identifiers to remove the user from.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    patch = [{"op": "remove", "path": "/", "value": g} for g in group_identifiers]
    client = get_client()
    await client.patch(
        f"/api/session/data/{data_source}/users/{username}/userGroups",
        json=patch,
    )
    return {"status": "ok"}


async def grant_user_connection_permissions(
    username: str,
    connection_ids: list[str],
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Grant READ access to connections for a user.

    Parameters
    ----------
    username : str
        Target username.
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
        f"/api/session/data/{data_source}/users/{username}/permissions",
        json=patch,
    )
    return {"status": "ok"}


async def revoke_user_connection_permissions(
    username: str,
    connection_ids: list[str],
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Revoke READ access to connections from a user.

    Parameters
    ----------
    username : str
        Target username.
    connection_ids : list[str]
        Connection identifiers to revoke access from.
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
        f"/api/session/data/{data_source}/users/{username}/permissions",
        json=patch,
    )
    return {"status": "ok"}


async def grant_user_connection_group_permissions(
    username: str,
    connection_group_ids: list[str],
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Grant READ access to connection groups for a user.

    Parameters
    ----------
    username : str
        Target username.
    connection_group_ids : list[str]
        Connection group identifiers to grant access to.
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
            "path": f"/connectionGroupPermissions/{gid}",
            "value": "READ",
        }
        for gid in connection_group_ids
    ]
    client = get_client()
    await client.patch(
        f"/api/session/data/{data_source}/users/{username}/permissions",
        json=patch,
    )
    return {"status": "ok"}


async def revoke_user_connection_group_permissions(
    username: str,
    connection_group_ids: list[str],
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Revoke READ access to connection groups from a user.

    Parameters
    ----------
    username : str
        Target username.
    connection_group_ids : list[str]
        Connection group identifiers to revoke access from.
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
            "path": f"/connectionGroupPermissions/{gid}",
            "value": "READ",
        }
        for gid in connection_group_ids
    ]
    client = get_client()
    await client.patch(
        f"/api/session/data/{data_source}/users/{username}/permissions",
        json=patch,
    )
    return {"status": "ok"}


async def grant_user_system_permissions(
    username: str,
    permissions: list[str],
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Grant system-level permissions to a user.

    Parameters
    ----------
    username : str
        Target username.
    permissions : list[str]
        System permission names, e.g. ``["CREATE_USER", "ADMINISTER"]``.
        Valid values: ``CREATE_USER``, ``CREATE_USER_GROUP``,
        ``CREATE_CONNECTION``, ``CREATE_CONNECTION_GROUP``,
        ``CREATE_SHARING_PROFILE``, ``ADMINISTER``.
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
        f"/api/session/data/{data_source}/users/{username}/permissions",
        json=patch,
    )
    return {"status": "ok"}


async def revoke_user_system_permissions(
    username: str,
    permissions: list[str],
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Revoke system-level permissions from a user.

    Parameters
    ----------
    username : str
        Target username.
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
        f"/api/session/data/{data_source}/users/{username}/permissions",
        json=patch,
    )
    return {"status": "ok"}


async def update_user_password(
    username: str,
    old_password: str,
    new_password: str,
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Change the password for a user.

    Parameters
    ----------
    username : str
        Target username.
    old_password : str
        Current password.
    new_password : str
        New password to set.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.put(
        f"/api/session/data/{data_source}/users/{username}/password",
        json={"oldPassword": old_password, "newPassword": new_password},
    )
    return {"status": "ok"}


async def update_user(
    username: str,
    attributes: dict[str, Any],
    data_source: str = "postgresql",
) -> dict[str, str]:
    """Update user attributes.

    Parameters
    ----------
    username : str
        Target username.
    attributes : dict[str, Any]
        Attribute key/value pairs to update.  Supported keys include
        ``guac-full-name``, ``guac-email-address``, ``guac-organization``,
        ``guac-organizational-role``, ``disabled``, ``expired``,
        ``access-window-start``, ``access-window-end``,
        ``valid-from``, ``valid-until``, ``timezone``.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.put(
        f"/api/session/data/{data_source}/users/{username}",
        json={"username": username, "attributes": attributes},
    )
    return {"status": "ok"}


async def create_user(
    username: str,
    password: str,
    attributes: dict[str, Any] | None = None,
    data_source: str = "postgresql",
) -> dict[str, Any]:
    """Create a new Guacamole user.

    Parameters
    ----------
    username : str
        New username (must be unique within the data source).
    password : str
        Initial password for the new user.
    attributes : dict[str, Any] | None
        Optional attribute key/value pairs (e.g. ``{"disabled": ""}``.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, Any]
        The created user object.
    """
    body: dict[str, Any] = {
        "username": username,
        "password": password,
        "attributes": attributes or {},
    }
    client = get_client()
    return await client.post(f"/api/session/data/{data_source}/users", json=body)


async def delete_user(username: str, data_source: str = "postgresql") -> dict[str, str]:
    """Delete a Guacamole user.

    Parameters
    ----------
    username : str
        Username of the account to delete.
    data_source : str
        Guacamole data-source identifier.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.delete(f"/api/session/data/{data_source}/users/{username}")
    return {"status": "ok"}
