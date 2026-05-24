"""Authentication tools for Apache Guacamole.

These tools allow explicit management of authentication tokens. In normal
operation the token is managed automatically by the
:class:`~guacamole_mcp.client.GuacamoleClient`, so calling these tools
directly is optional.
"""

from __future__ import annotations

import logging
from typing import Any

from ..state import get_client

logger = logging.getLogger(__name__)


async def authenticate() -> dict[str, Any]:
    """Authenticate against the Guacamole server and return token information.

    Obtains (or refreshes) the auth token using the credentials configured
    via environment variables.  The token is cached by the client for all
    subsequent tool calls.

    Returns
    -------
    dict[str, Any]
        A dict with keys ``authToken``, ``username``, ``dataSource``,
        and ``availableDataSources``.

    Raises
    ------
    guacamole_mcp.client.GuacamoleAuthError
        If the credentials are rejected.

    Examples
    --------
    >>> result = await authenticate()
    >>> print(result["authToken"])
    """
    client = get_client()
    token = await client.authenticate()
    return {"authToken": token, "status": "authenticated"}


async def logout() -> dict[str, str]:
    """Invalidate the current authentication token on the server.

    After calling this the next tool call will automatically re-authenticate.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.

    Examples
    --------
    >>> await logout()
    {'status': 'ok'}
    """
    client = get_client()
    await client.logout()
    return {"status": "ok"}
