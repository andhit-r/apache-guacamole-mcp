"""Shared fixtures for integration tests.

These tests require Docker and spin up a real Apache Guacamole instance
via Docker Compose before running.  They are **not** part of the normal
unit-test suite; run them explicitly with::

    pytest tests/integration/ --integration

or simply by pointing pytest at the integration directory.
"""

from __future__ import annotations

import time
from pathlib import Path

import httpx
import pytest

from guacamole_mcp import state
from guacamole_mcp.client import GuacamoleClient
from guacamole_mcp.config import GuacamoleConfig

GUACAMOLE_ADMIN = "guacadmin"
GUACAMOLE_PASS = "guacadmin"
DATA_SOURCE = "postgresql"


# ---------------------------------------------------------------------------
# pytest-docker hooks
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def docker_compose_file() -> str:
    """Path to the Docker Compose file for integration tests."""
    return str(Path(__file__).parent / "docker-compose.yml")


@pytest.fixture(scope="session")
def docker_compose_command() -> str:
    """Use Docker Compose v2 plugin."""
    return "docker compose"


# ---------------------------------------------------------------------------
# Guacamole readiness
# ---------------------------------------------------------------------------


def _guacamole_ready(url: str) -> bool:
    """Return True when Guacamole's languages endpoint responds 200."""
    try:
        r = httpx.get(f"{url}/api/languages", timeout=5.0)
        return r.status_code == 200
    except Exception:
        return False


@pytest.fixture(scope="session")
def guacamole_url(docker_ip: str, docker_services: object) -> str:  # type: ignore[type-arg]
    """Start Guacamole via Docker Compose and return the base URL.

    Blocks until the service responds or the timeout expires.

    Parameters
    ----------
    docker_ip : str
        IP address of the Docker host (from pytest-docker).
    docker_services : object
        pytest-docker service manager.

    Returns
    -------
    str
        Base URL of the Guacamole web application (e.g.
        ``http://localhost:32768/guacamole``).
    """
    port = docker_services.port_for("guacamole", 8080)  # type: ignore[attr-defined]
    url = f"http://{docker_ip}:{port}/guacamole"

    docker_services.wait_until_responsive(  # type: ignore[attr-defined]
        timeout=180.0,
        pause=2.0,
        check=lambda: _guacamole_ready(url),
    )
    return url


# ---------------------------------------------------------------------------
# Client fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
async def integration_client(guacamole_url: str) -> GuacamoleClient:
    """A real :class:`~guacamole_mcp.client.GuacamoleClient` connected to
    the test Guacamole instance.

    The singleton in :mod:`guacamole_mcp.state` is set to this client so
    that tool functions resolve to it automatically.

    Yields
    ------
    GuacamoleClient
        Authenticated client for the test Guacamole.
    """
    cfg = GuacamoleConfig(
        url=guacamole_url,
        username=GUACAMOLE_ADMIN,
        password=GUACAMOLE_PASS,  # type: ignore[arg-type]
        data_source=DATA_SOURCE,
        timeout=30.0,
        verify_ssl=False,
        transport="stdio",
    )
    client = GuacamoleClient(cfg)
    state.set_client(client)
    # Pre-authenticate so the token is cached
    await client.authenticate()
    yield client
    await client.close()
    state.set_client(None)
