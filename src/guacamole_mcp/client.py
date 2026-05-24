"""Async HTTP client for the Apache Guacamole REST API.

Handles authentication token lifecycle automatically: the token is
obtained on the first request and cached for subsequent calls.  A
``401 Unauthorized`` response triggers a single re-authentication attempt.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from .config import GuacamoleConfig

logger = logging.getLogger(__name__)


class GuacamoleError(Exception):
    """Base exception for Guacamole API errors.

    Parameters
    ----------
    message : str
        Human-readable error description.
    status_code : int | None
        HTTP status code returned by the API, if available.
    """

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class GuacamoleAuthError(GuacamoleError):
    """Raised when authentication fails (HTTP 401)."""


class GuacamoleNotFoundError(GuacamoleError):
    """Raised when a requested resource does not exist (HTTP 404)."""


class GuacamoleClient:
    """Async HTTP client for the Apache Guacamole REST API.

    Parameters
    ----------
    config : GuacamoleConfig
        Server connection configuration.

    Examples
    --------
    >>> async with GuacamoleClient(config) as client:
    ...     users = await client.get("/api/session/data/postgresql/users")
    """

    def __init__(self, config: GuacamoleConfig) -> None:
        self._config = config
        self._token: str | None = None
        self._http = httpx.AsyncClient(
            base_url=config.url,
            timeout=config.timeout,
            verify=config.verify_ssl,
        )

    async def __aenter__(self) -> GuacamoleClient:
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._http.aclose()

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    async def authenticate(self) -> str:
        """Obtain an authentication token from the Guacamole server.

        Stores the token internally for reuse.

        Returns
        -------
        str
            The raw authentication token string.

        Raises
        ------
        GuacamoleAuthError
            If the server rejects the credentials.
        """
        logger.debug("Authenticating as %s", self._config.username)
        response = await self._http.post(
            "/api/tokens",
            data={
                "username": self._config.username,
                "password": self._config.password.get_secret_value(),
            },
        )
        if response.status_code != 200:
            raise GuacamoleAuthError(
                f"Authentication failed ({response.status_code}): {response.text}",
                status_code=response.status_code,
            )
        data: dict[str, Any] = response.json()
        self._token = data["authToken"]
        logger.debug("Authentication successful, token cached")
        return self._token

    async def get_token(self) -> str:
        """Return the cached token, authenticating if necessary.

        Returns
        -------
        str
            Valid authentication token.
        """
        if not self._token:
            await self.authenticate()
        return self._token  # type: ignore[return-value]

    async def logout(self) -> None:
        """Invalidate the current token on the server.

        No-op if the client has not yet authenticated.
        """
        if self._token:
            try:
                await self._http.delete(f"/api/tokens/{self._token}")
            except Exception:  # noqa: BLE001
                logger.warning("Logout request failed", exc_info=True)
            finally:
                self._token = None

    # ------------------------------------------------------------------
    # Request helpers
    # ------------------------------------------------------------------

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Execute an authenticated HTTP request.

        Automatically injects the ``token`` query parameter.  On a 401
        response a single re-authentication attempt is made.

        Parameters
        ----------
        method : str
            HTTP method (GET, POST, PUT, PATCH, DELETE).
        path : str
            URL path relative to the base URL.
        **kwargs : Any
            Extra keyword arguments forwarded to :meth:`httpx.AsyncClient.request`.

        Returns
        -------
        httpx.Response
            The raw HTTP response object.

        Raises
        ------
        GuacamoleAuthError
            On persistent 401 responses.
        GuacamoleNotFoundError
            On 404 responses.
        GuacamoleError
            On any other 4xx/5xx response.
        """
        token = await self.get_token()
        params: dict[str, Any] = dict(kwargs.pop("params", {}) or {})
        params["token"] = token

        response = await self._http.request(method, path, params=params, **kwargs)

        if response.status_code == 401:
            logger.debug("Token expired, re-authenticating")
            token = await self.authenticate()
            params["token"] = token
            response = await self._http.request(method, path, params=params, **kwargs)

        self._raise_for_status(response)
        return response

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.status_code == 401:
            raise GuacamoleAuthError("Unauthorized", status_code=401)
        if response.status_code == 404:
            raise GuacamoleNotFoundError("Resource not found", status_code=404)
        if response.status_code >= 400:
            raise GuacamoleError(
                f"API error {response.status_code}: {response.text}",
                status_code=response.status_code,
            )

    # ------------------------------------------------------------------
    # Convenience methods
    # ------------------------------------------------------------------

    async def get(self, path: str, **kwargs: Any) -> Any:
        """Perform a GET request and return the decoded JSON body.

        Parameters
        ----------
        path : str
            API path.
        **kwargs : Any
            Forwarded to :meth:`_request`.

        Returns
        -------
        Any
            Decoded JSON response (dict or list).
        """
        response = await self._request("GET", path, **kwargs)
        return response.json()

    async def post(self, path: str, **kwargs: Any) -> Any:
        """Perform a POST request and return the decoded JSON body.

        Parameters
        ----------
        path : str
            API path.
        **kwargs : Any
            Forwarded to :meth:`_request`.

        Returns
        -------
        Any
            Decoded JSON response, or ``None`` for 204 responses.
        """
        response = await self._request("POST", path, **kwargs)
        if response.status_code == 204:
            return None
        return response.json()

    async def put(self, path: str, **kwargs: Any) -> None:
        """Perform a PUT request (no response body expected).

        Parameters
        ----------
        path : str
            API path.
        **kwargs : Any
            Forwarded to :meth:`_request`.
        """
        await self._request("PUT", path, **kwargs)

    async def patch(self, path: str, **kwargs: Any) -> None:
        """Perform a PATCH request (no response body expected).

        Parameters
        ----------
        path : str
            API path.
        **kwargs : Any
            Forwarded to :meth:`_request`.
        """
        await self._request("PATCH", path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> None:
        """Perform a DELETE request (no response body expected).

        Parameters
        ----------
        path : str
            API path.
        **kwargs : Any
            Forwarded to :meth:`_request`.
        """
        await self._request("DELETE", path, **kwargs)
