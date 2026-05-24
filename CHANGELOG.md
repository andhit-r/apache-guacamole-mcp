# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-01

### Added

- Initial release
- MCP server wrapping the full Apache Guacamole REST API (57 tools)
- Authentication: `authenticate`, `logout`
- Users: full CRUD + password management + permissions
- User Groups: full CRUD + member/group hierarchy + permissions
- Connections: full CRUD (RDP/SSH/VNC/Telnet/Kubernetes) + active connection management
- Connection Groups: full CRUD + tree traversal
- History: connection and user audit log queries
- stdio and SSE transports
- Docker image for GHCR
- Sphinx/RTD documentation
- GitHub Actions: lint, test, Docker publish, PyPI release

[0.1.0]: https://github.com/andhit-r/apache-guacamole-mcp/releases/tag/v0.1.0
