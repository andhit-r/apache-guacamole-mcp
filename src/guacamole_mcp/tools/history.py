"""History query tools for Apache Guacamole.

Provides access to ``/api/session/data/{data_source}/history``
endpoints for auditing connection and user activity.
"""

from __future__ import annotations

import logging
from typing import Any

from ..state import get_client

logger = logging.getLogger(__name__)


async def list_connection_history(
    data_source: str = "postgresql",
    contains: str | None = None,
    order: str | None = None,
) -> list[Any]:
    """Return the global connection usage history.

    Parameters
    ----------
    data_source : str
        Guacamole data-source identifier.
    contains : str | None
        Optional filter string — only records whose fields contain this
        value are returned.
    order : str | None
        Optional sort field name (e.g. ``startDate``).

    Returns
    -------
    list[Any]
        List of connection history records.
    """
    params: dict[str, str] = {}
    if contains is not None:
        params["contains"] = contains
    if order is not None:
        params["order"] = order

    client = get_client()
    return await client.get(
        f"/api/session/data/{data_source}/history/connections",
        params=params,
    )


async def list_user_history(
    data_source: str = "postgresql",
    order: str | None = None,
) -> list[Any]:
    """Return the global user login/logout history.

    Parameters
    ----------
    data_source : str
        Guacamole data-source identifier.
    order : str | None
        Optional sort field name.

    Returns
    -------
    list[Any]
        List of user history records.
    """
    params: dict[str, str] = {}
    if order is not None:
        params["order"] = order

    client = get_client()
    return await client.get(
        f"/api/session/data/{data_source}/history/users",
        params=params,
    )
