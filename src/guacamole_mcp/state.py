"""Singleton accessor for the shared :class:`~guacamole_mcp.client.GuacamoleClient`.

All tool modules call :func:`get_client` to obtain the shared client
instance, which is created lazily from the current configuration.
:func:`set_client` is provided for dependency injection in tests.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import GuacamoleClient

_client: GuacamoleClient | None = None


def get_client() -> GuacamoleClient:
    """Return the process-level :class:`~guacamole_mcp.client.GuacamoleClient`.

    Creates the client on first call using :func:`~guacamole_mcp.config.get_config`.

    Returns
    -------
    GuacamoleClient
        The shared HTTP client instance.
    """
    global _client
    if _client is None:
        from .client import GuacamoleClient
        from .config import get_config

        _client = GuacamoleClient(get_config())
    return _client


def set_client(client: GuacamoleClient | None) -> None:
    """Replace the singleton client (used in tests).

    Parameters
    ----------
    client : GuacamoleClient | None
        New client instance, or ``None`` to reset.
    """
    global _client
    _client = client
