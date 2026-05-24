# ── Build stage ──────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build tooling
RUN pip install --no-cache-dir hatchling

# Copy project files for build
COPY pyproject.toml README.md CHANGELOG.md LICENSE ./
COPY src/ ./src/

# Build wheel
RUN pip wheel --no-cache-dir --wheel-dir /dist .

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim

LABEL org.opencontainers.image.title="Apache Guacamole MCP Server" \
      org.opencontainers.image.description="MCP server for the Apache Guacamole REST API" \
      org.opencontainers.image.source="https://github.com/andhit-r/apache-guacamole-mcp" \
      org.opencontainers.image.licenses="MIT"

# Security: run as non-root user
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy wheel from builder
COPY --from=builder /dist/*.whl /tmp/

# Install the package without cache
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

USER appuser

# Expose SSE port (unused in stdio mode)
EXPOSE 8000

# Default env — override at runtime
ENV GUACAMOLE_URL="http://guacamole:8080" \
    GUACAMOLE_USERNAME="guacadmin" \
    GUACAMOLE_PASSWORD="guacadmin" \
    GUACAMOLE_DATA_SOURCE="postgresql" \
    GUACAMOLE_TRANSPORT="stdio"

ENTRYPOINT ["guacamole-mcp"]
