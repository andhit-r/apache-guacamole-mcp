# Copilot Instructions — apache-guacamole-mcp

## Project Overview

**apache-guacamole-mcp** is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
server that wraps the [Apache Guacamole](https://guacamole.apache.org/) REST API.
It allows AI assistants (Claude, Copilot, etc.) to manage Guacamole instances —
create/update/delete connections, users, groups, and monitor active sessions.

---

## Architecture

```
apache-guacamole-mcp/
├── src/guacamole_mcp/
│   ├── __init__.py           # Package version
│   ├── __main__.py           # CLI entry point
│   ├── config.py             # Pydantic-settings config (env vars)
│   ├── client.py             # Async httpx HTTP client for Guacamole API
│   ├── state.py              # Singleton client accessor (get_client / set_client)
│   ├── server.py             # FastMCP server, tool registration, run()
│   └── tools/
│       ├── __init__.py
│       ├── auth.py           # authenticate, logout
│       ├── users.py          # CRUD for users + permissions
│       ├── user_groups.py    # CRUD for user groups + membership
│       ├── connections.py    # CRUD for connections + active connections
│       ├── connection_groups.py  # CRUD for connection groups + tree
│       └── history.py        # Connection and user history
├── tests/
│   ├── conftest.py           # Shared fixtures
│   ├── test_client.py        # GuacamoleClient unit tests
│   ├── test_auth.py          # Auth tools
│   ├── test_users.py         # User tools
│   ├── test_user_groups.py   # User group tools
│   ├── test_connections.py   # Connection tools
│   ├── test_connection_groups.py
│   └── test_history.py
├── docs/                     # Sphinx / RTD documentation
├── .github/workflows/
│   ├── test.yml              # Ruff lint + pytest
│   ├── docker.yml            # Build & push to GHCR
│   └── release.yml           # GitHub Release + PyPI
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

---

## Key Design Decisions

### 1. Authentication
- Credentials are supplied via **environment variables** (`GUACAMOLE_URL`, `GUACAMOLE_USERNAME`, `GUACAMOLE_PASSWORD`, `GUACAMOLE_DATA_SOURCE`).
- `GuacamoleClient` caches the auth token internally and re-authenticates on `401`.
- Tools do **not** accept token parameters — auth is fully managed by the client.

### 2. `data_source` parameter
- Almost every API endpoint requires a `data_source` path segment (e.g. `postgresql`).
- All tool functions expose `data_source: str = "postgresql"` as an optional parameter.
- The default value should match `GUACAMOLE_DATA_SOURCE` env var where possible.

### 3. JSON Patch operations
- Guacamole's PATCH endpoints use [RFC 6902 JSON Patch](http://jsonpatch.com/).
- Tool functions accept friendly Python types (lists of strings) and internally convert to patch format.
- Example: `assign_user_to_groups(username, ["admins", "devs"])` → `[{"op": "add", "path": "/", "value": "admins"}, ...]`

### 4. Tool return values
- `GET` tools return the raw JSON (dict or list) from the API.
- `POST` (create) tools return the created object.
- `PUT` / `PATCH` / `DELETE` tools return `{"status": "ok"}` on success.
- Errors are raised as exceptions (FastMCP converts them to MCP error responses).

### 5. Transport
- **stdio** (default): `guacamole-mcp` or `python -m guacamole_mcp`
- **Docker**: `docker run -e GUACAMOLE_URL=... ghcr.io/<owner>/guacamole-mcp`
- **SSE/HTTP**: via `TRANSPORT=sse` env var and port `8000`

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GUACAMOLE_URL` | `http://localhost:8080` | Base URL of Guacamole |
| `GUACAMOLE_USERNAME` | `guacadmin` | Admin username |
| `GUACAMOLE_PASSWORD` | `guacadmin` | Admin password |
| `GUACAMOLE_DATA_SOURCE` | `postgresql` | Data source identifier |
| `GUACAMOLE_TIMEOUT` | `30.0` | HTTP timeout in seconds |
| `GUACAMOLE_VERIFY_SSL` | `true` | Verify TLS certificates |
| `TRANSPORT` | `stdio` | MCP transport: `stdio` or `sse` |
| `HOST` | `0.0.0.0` | SSE host (only used when `TRANSPORT=sse`) |
| `PORT` | `8000` | SSE port (only used when `TRANSPORT=sse`) |

---

## GitHub Workflow

- Gunakan **gh-cli** (`gh`) untuk semua interaksi dengan GitHub: membuat PR, melihat issues, membuat release, dsb.
- Jangan gunakan `git push` / `git pull` secara langsung — selalu lewat script atau `gh`.

---

## Coding Standards

- Python 3.11+
- `src` layout: package under `src/guacamole_mcp/`
- **Async-first**: all tools and HTTP calls are `async`
- **Type annotations**: full annotations on all public functions
- **Docstrings**: NumPy-style on all public functions/classes (for RTD/Sphinx autodoc)
- **Linter**: Ruff (`ruff check` + `ruff format`)
- **Tests**: pytest + pytest-asyncio + respx (httpx mocking)
- No `print()` — use `logging` instead

---

## Testing Rules

- All tests are in `tests/` at the project root.
- Tests for tools mock `guacamole_mcp.state.get_client` using `unittest.mock.AsyncMock`.
- Tests for the HTTP client (`test_client.py`) use `respx` to mock httpx.
- `pytest-asyncio` with `asyncio_mode = "auto"` — no need for `@pytest.mark.asyncio`.
- Fixtures in `conftest.py` are shared across all test files.

---

## Apache Guacamole REST API Reference

Base path: `GET /api/session/data/{data_source}/...`
Auth: token via query param `?token=<authToken>`

### Endpoints Covered

| Category | Endpoints |
|---|---|
| Auth | POST /api/tokens, DELETE /api/tokens/{token} |
| Users | GET/POST /users, GET/PUT/DELETE /users/{u}, PATCH /users/{u}/userGroups, PATCH /users/{u}/permissions, PUT /users/{u}/password, GET /self |
| User Groups | GET/POST /userGroups, GET/PUT/DELETE /userGroups/{g}, PATCH /userGroups/{g}/memberUsers, PATCH /userGroups/{g}/memberUserGroups, PATCH /userGroups/{g}/userGroups, PATCH /userGroups/{g}/permissions |
| Connections | GET/POST /connections, GET/PUT/DELETE /connections/{c}, GET /connections/{c}/parameters, GET /connections/{c}/history, GET /connections/{c}/sharingProfiles |
| Active Connections | GET /activeConnections, PATCH /activeConnections |
| Sharing Profiles | GET /sharingProfiles |
| Connection Groups | GET/POST /connectionGroups, GET/PUT/DELETE /connectionGroups/{g}, GET /connectionGroups/ROOT/tree, GET /connectionGroups/{g}/tree |
| History | GET /history/connections, GET /history/users |

---

## Adding New Tools

1. Add the function in the appropriate `src/guacamole_mcp/tools/<module>.py`.
2. Annotate with full types and a NumPy-style docstring.
3. Register in `src/guacamole_mcp/server.py` with `mcp.tool()(tools.<module>.<fn>)`.
4. Add a test in `tests/test_<module>.py`.

---

## Release Process

1. Update `__version__` in `src/guacamole_mcp/__init__.py`.
2. Update `CHANGELOG.md`.
3. Create a Git tag `v<version>` and push.
4. GitHub Actions: runs tests → builds Docker image → creates GH Release → publishes to PyPI.
