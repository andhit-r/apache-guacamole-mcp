"""Unit tests for :mod:`guacamole_mcp.client`."""

from __future__ import annotations

import httpx
import pytest
import respx

from guacamole_mcp.client import (
    GuacamoleAuthError,
    GuacamoleClient,
    GuacamoleError,
    GuacamoleNotFoundError,
)
from guacamole_mcp.config import GuacamoleConfig

BASE_URL = "http://guacamole-test:8080"
TOKEN = "test-token-abc123"
AUTH_RESP = {
    "authToken": TOKEN,
    "username": "guacadmin",
    "dataSource": "postgresql",
    "availableDataSources": ["postgresql"],
}


@pytest.fixture()
def cfg() -> GuacamoleConfig:
    return GuacamoleConfig(
        url=BASE_URL,
        username="guacadmin",
        password="guacadmin",  # type: ignore[arg-type]
        data_source="postgresql",
    )


@pytest.fixture()
def client(cfg: GuacamoleConfig) -> GuacamoleClient:
    return GuacamoleClient(cfg)


class TestAuthenticate:
    async def test_stores_token(self, client: GuacamoleClient) -> None:
        with respx.mock(base_url=BASE_URL) as router:
            router.post("/api/tokens").mock(
                return_value=httpx.Response(200, json=AUTH_RESP)
            )
            token = await client.authenticate()

        assert token == TOKEN
        assert client._token == TOKEN

    async def test_raises_on_bad_credentials(self, client: GuacamoleClient) -> None:
        with respx.mock(base_url=BASE_URL) as router:
            router.post("/api/tokens").mock(
                return_value=httpx.Response(403, text="Forbidden")
            )
            with pytest.raises(GuacamoleAuthError):
                await client.authenticate()


class TestGetToken:
    async def test_calls_authenticate_when_no_token(
        self, client: GuacamoleClient
    ) -> None:
        with respx.mock(base_url=BASE_URL) as router:
            router.post("/api/tokens").mock(
                return_value=httpx.Response(200, json=AUTH_RESP)
            )
            token = await client.get_token()

        assert token == TOKEN

    async def test_returns_cached_token(self, client: GuacamoleClient) -> None:
        client._token = "cached-token"
        token = await client.get_token()
        assert token == "cached-token"


class TestLogout:
    async def test_clears_token(self, client: GuacamoleClient) -> None:
        client._token = TOKEN
        with respx.mock(base_url=BASE_URL):
            respx.delete(f"/api/tokens/{TOKEN}").mock(return_value=httpx.Response(204))
            await client.logout()

        assert client._token is None

    async def test_noop_when_no_token(self, client: GuacamoleClient) -> None:
        # Should not raise
        await client.logout()
        assert client._token is None


class TestRequest:
    async def test_injects_token_param(self, client: GuacamoleClient) -> None:
        client._token = TOKEN
        with respx.mock(base_url=BASE_URL) as mock:
            route = mock.get("/api/session/data/postgresql/users").mock(
                return_value=httpx.Response(200, json={})
            )
            await client.get("/api/session/data/postgresql/users")

        assert route.called
        request = route.calls[0].request
        assert f"token={TOKEN}" in str(request.url)

    async def test_retries_on_401(self, client: GuacamoleClient) -> None:
        client._token = "expired-token"
        with respx.mock(base_url=BASE_URL) as mock:
            mock.post("/api/tokens").mock(
                return_value=httpx.Response(200, json=AUTH_RESP)
            )
            call_count = 0

            def side_effect(request: httpx.Request) -> httpx.Response:
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return httpx.Response(401)
                return httpx.Response(200, json={"result": "ok"})

            mock.get("/api/session/data/postgresql/users").mock(side_effect=side_effect)
            result = await client.get("/api/session/data/postgresql/users")

        assert result == {"result": "ok"}
        assert call_count == 2

    async def test_retries_on_403_stale_token(self, client: GuacamoleClient) -> None:
        """Guacamole returns 403 (not 401) for expired/invalid tokens."""
        client._token = "stale-token"
        with respx.mock(base_url=BASE_URL) as mock:
            mock.post("/api/tokens").mock(
                return_value=httpx.Response(200, json=AUTH_RESP)
            )
            call_count = 0

            def side_effect(request: httpx.Request) -> httpx.Response:
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return httpx.Response(403, json={"message": "Permission Denied."})
                return httpx.Response(200, json={"result": "ok"})

            mock.get("/api/session/data/postgresql/users").mock(side_effect=side_effect)
            result = await client.get("/api/session/data/postgresql/users")

        assert result == {"result": "ok"}
        assert call_count == 2

    async def test_raises_403_on_genuine_permission_denied(self, client: GuacamoleClient) -> None:
        """After re-auth, a second 403 is a real permission error."""
        client._token = TOKEN
        with respx.mock(base_url=BASE_URL) as mock:
            mock.post("/api/tokens").mock(
                return_value=httpx.Response(200, json=AUTH_RESP)
            )
            mock.get("/api/session/data/postgresql/connections").mock(
                return_value=httpx.Response(403, json={"message": "Permission Denied."})
            )
            with pytest.raises(GuacamoleError) as exc_info:
                await client.get("/api/session/data/postgresql/connections")

        assert exc_info.value.status_code == 403

    async def test_raises_not_found(self, client: GuacamoleClient) -> None:
        client._token = TOKEN
        with respx.mock(base_url=BASE_URL) as router:
            router.get("/api/session/data/postgresql/users/nobody").mock(
                return_value=httpx.Response(404)
            )
            with pytest.raises(GuacamoleNotFoundError):
                await client.get("/api/session/data/postgresql/users/nobody")

    async def test_raises_generic_error(self, client: GuacamoleClient) -> None:
        client._token = TOKEN
        with respx.mock(base_url=BASE_URL) as router:
            router.get("/api/session/data/postgresql/users").mock(
                return_value=httpx.Response(500, text="Internal Server Error")
            )
            with pytest.raises(GuacamoleError) as exc_info:
                await client.get("/api/session/data/postgresql/users")

        assert exc_info.value.status_code == 500
