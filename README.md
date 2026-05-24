# Apache Guacamole MCP

[![PyPI](https://img.shields.io/pypi/v/guacamole-mcp)](https://pypi.org/project/guacamole-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/guacamole-mcp)](https://pypi.org/project/guacamole-mcp/)
[![CI](https://github.com/andhit-r/apache-guacamole-mcp/actions/workflows/test.yml/badge.svg)](https://github.com/andhit-r/apache-guacamole-mcp/actions)
[![Docker](https://img.shields.io/badge/ghcr.io-guacamole--mcp-blue)](https://github.com/andhit-r/apache-guacamole-mcp/pkgs/container/guacamole-mcp)
[![Docs](https://readthedocs.org/projects/apache-guacamole-mcp/badge/?version=latest)](https://apache-guacamole-mcp.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server that wraps the
[Apache Guacamole](https://guacamole.apache.org/) REST API. Allows AI assistants
(Claude, GitHub Copilot, etc.) to manage Guacamole instances — create and manage
RDP/SSH/VNC/Telnet/Kubernetes connections, users, user groups, and monitor active sessions.

## Features

- **57 MCP tools** covering every Guacamole REST API endpoint
- Authentication, Users, User Groups, Connections, Connection Groups, History
- Async-first implementation with auto token refresh
- stdio and SSE transports
- Docker image published to GHCR
- Full type annotations and NumPy-style docstrings

## Installation

```bash
pip install guacamole-mcp
```

Or install from GitHub:

```bash
pip install git+https://github.com/andhit-r/apache-guacamole-mcp.git
```

## Quick Start

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "guacamole": {
      "command": "guacamole-mcp",
      "env": {
        "GUACAMOLE_URL": "http://your-guacamole:8080",
        "GUACAMOLE_USERNAME": "guacadmin",
        "GUACAMOLE_PASSWORD": "secret"
      }
    }
  }
}
```

### Docker (stdio)

```json
{
  "mcpServers": {
    "guacamole": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "GUACAMOLE_URL=http://your-guacamole:8080",
        "-e", "GUACAMOLE_USERNAME=guacadmin",
        "-e", "GUACAMOLE_PASSWORD=secret",
        "ghcr.io/andhit-r/guacamole-mcp:latest"
      ]
    }
  }
}
```

### VS Code (GitHub Copilot)

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "guacamole": {
      "type": "stdio",
      "command": "guacamole-mcp",
      "env": {
        "GUACAMOLE_URL": "http://your-guacamole:8080",
        "GUACAMOLE_USERNAME": "guacadmin",
        "GUACAMOLE_PASSWORD": "secret"
      }
    }
  }
}
```

## Configuration

All configuration is via environment variables:

| Variable | Default | Description |
|---|---|---|
| `GUACAMOLE_URL` | `http://localhost:8080` | Base URL of Guacamole |
| `GUACAMOLE_USERNAME` | `guacadmin` | Admin username |
| `GUACAMOLE_PASSWORD` | `guacadmin` | Admin password |
| `GUACAMOLE_DATA_SOURCE` | `postgresql` | Data source identifier |
| `GUACAMOLE_TIMEOUT` | `30.0` | HTTP timeout in seconds |
| `GUACAMOLE_VERIFY_SSL` | `true` | Verify TLS certificates |
| `GUACAMOLE_TRANSPORT` | `stdio` | MCP transport: `stdio` or `sse` |
| `HOST` | `0.0.0.0` | Bind address (SSE only) |
| `PORT` | `8000` | Port (SSE only) |

## Available Tools

| Category | Count | Examples |
|---|---|---|
| Auth | 2 | `authenticate`, `logout` |
| Users | 19 | `list_users`, `create_user`, `update_user_password`, `grant_user_system_permissions` |
| User Groups | 15 | `list_user_groups`, `add_members_to_user_group`, `assign_connection_permissions_to_user_group` |
| Connections | 11 | `list_connections`, `create_connection`, `list_active_connections`, `kill_connections` |
| Connection Groups | 7 | `list_connection_groups`, `list_connection_tree`, `create_connection_group` |
| History | 2 | `list_connection_history`, `list_user_history` |

## Documentation

Full documentation is available at [apache-guacamole-mcp.readthedocs.io](https://apache-guacamole-mcp.readthedocs.io/).

## Development

```bash
git clone https://github.com/andhit-r/apache-guacamole-mcp.git
cd apache-guacamole-mcp
pip install -e ".[dev]"
pytest
```

### Linting

```bash
ruff check .
ruff format .
```

## License

[MIT](LICENSE)
