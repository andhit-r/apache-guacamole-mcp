Installation
============

Requirements
------------

* Python 3.11 or later
* A running `Apache Guacamole <https://guacamole.apache.org/>`_ instance

Install from PyPI
-----------------

.. code-block:: bash

   pip install guacamole-mcp

Install from GitHub
-------------------

.. code-block:: bash

   pip install git+https://github.com/andhit-r/apache-guacamole-mcp.git

Run with Docker
---------------

.. code-block:: bash

   docker run --rm -i \
     -e GUACAMOLE_URL=http://your-guacamole:8080 \
     -e GUACAMOLE_USERNAME=guacadmin \
     -e GUACAMOLE_PASSWORD=secret \
     ghcr.io/andhit-r/guacamole-mcp:latest

For SSE transport (useful with Claude Desktop or other MCP clients that
support HTTP):

.. code-block:: bash

   docker run --rm -p 8000:8000 \
     -e GUACAMOLE_URL=http://your-guacamole:8080 \
     -e GUACAMOLE_USERNAME=guacadmin \
     -e GUACAMOLE_PASSWORD=secret \
     -e GUACAMOLE_TRANSPORT=sse \
     ghcr.io/andhit-r/guacamole-mcp:latest
