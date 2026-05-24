"""Configuration management for the Guacamole MCP server.

All settings are read from environment variables with the ``GUACAMOLE_``
prefix (and ``TRANSPORT`` / ``HOST`` / ``PORT`` for server transport).
"""

import logging

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class GuacamoleConfig(BaseSettings):
    """Runtime configuration loaded from environment variables.

    Parameters
    ----------
    url : str
        Base URL of the Guacamole web application.
    username : str
        Administrator username used to obtain an auth token.
    password : SecretStr
        Administrator password (never logged).
    data_source : str
        Guacamole data-source identifier (e.g. ``postgresql``).
    timeout : float
        HTTP request timeout in seconds.
    verify_ssl : bool
        Whether to verify TLS certificates for the Guacamole server.
    transport : str
        MCP transport mode: ``stdio`` (default) or ``sse``.
    host : str
        Bind host when ``transport=sse``.
    port : int
        Bind port when ``transport=sse``.
    """

    url: str = "http://localhost:8080"
    username: str = "guacadmin"
    password: SecretStr = SecretStr("guacadmin")
    data_source: str = "postgresql"
    timeout: float = 30.0
    verify_ssl: bool = True
    transport: str = "stdio"
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_prefix="GUACAMOLE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class _TransportConfig(BaseSettings):
    """Separate settings for MCP transport (no prefix)."""

    transport: str = "stdio"
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = SettingsConfigDict(extra="ignore")


_config: GuacamoleConfig | None = None


def get_config() -> GuacamoleConfig:
    """Return the singleton :class:`GuacamoleConfig` instance.

    The instance is lazily created on first call and cached for the lifetime
    of the process.

    Returns
    -------
    GuacamoleConfig
        The active configuration object.
    """
    global _config
    if _config is None:
        _config = GuacamoleConfig()
    return _config


def reset_config() -> None:
    """Reset the cached config singleton (useful in tests)."""
    global _config
    _config = None
