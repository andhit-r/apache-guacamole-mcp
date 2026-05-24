"""Integration tests for authentication tools against a live Guacamole."""

from __future__ import annotations

import pytest

from guacamole_mcp.client import GuacamoleAuthError, GuacamoleClient
from guacamole_mcp.config import GuacamoleConfig
from guacamole_mcp.tools.auth import authenticate, logout

pytestmark = pytest.mark.integration


class TestAuthenticateIntegration:
    """Test :func:`~guacamole_mcp.tools.auth.authenticate` against a real server."""

    async def test_returns_token_dict(
        self, integration_client: GuacamoleClient
    ) -> None:
        """authenticate() returns a dict with authToken."""
        result = await authenticate()
        assert "authToken" in result
        assert isinstance(result["authToken"], str)
        assert len(result["authToken"]) > 0

    async def test_status_is_authenticated(
        self, integration_client: GuacamoleClient
    ) -> None:
        """authenticate() reports authenticated status."""
        result = await authenticate()
        assert result["status"] == "authenticated"

    async def test_wrong_password_raises_auth_error(
        self, guacamole_url: str
    ) -> None:
        """Wrong credentials raise GuacamoleAuthError."""
        from guacamole_mcp import state

        cfg = GuacamoleConfig(
            url=guacamole_url,
            username="guacadmin",
            password="wrongpassword",  # type: ignore[arg-type]
            data_source="postgresql",
            timeout=10.0,
            verify_ssl=False,
            transport="stdio",
        )
        bad_client = GuacamoleClient(cfg)
        state.set_client(bad_client)
        try:
            with pytest.raises(GuacamoleAuthError):
                await authenticate()
        finally:
            await bad_client.close()


class TestLogoutIntegration:
    """Test :func:`~guacamole_mcp.tools.auth.logout` against a real server."""

    async def test_logout_returns_ok(
        self, integration_client: GuacamoleClient
    ) -> None:
        """logout() returns status ok and clears the token."""
        result = await logout()
        assert result == {"status": "ok"}
        assert integration_client._token is None

    async def test_re_authenticate_after_logout(
        self, integration_client: GuacamoleClient
    ) -> None:
        """After logout, authenticate() gets a fresh token."""
        await logout()
        result = await authenticate()
        assert "authToken" in result
        assert integration_client._token is not None
