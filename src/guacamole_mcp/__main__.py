"""CLI entry point for the Apache Guacamole MCP server.

Run with::

    python -m guacamole_mcp

or via the installed script::

    guacamole-mcp
"""

import logging
import sys


def main() -> None:
    """Configure logging and start the MCP server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
        stream=sys.stderr,
    )
    from .server import run

    run()


if __name__ == "__main__":
    main()
