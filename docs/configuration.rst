Configuration
=============

All configuration is supplied via environment variables.

.. list-table:: Environment Variables
   :header-rows: 1
   :widths: 30 20 50

   * - Variable
     - Default
     - Description
   * - ``GUACAMOLE_URL``
     - ``http://localhost:8080``
     - Base URL of your Guacamole instance (no trailing slash)
   * - ``GUACAMOLE_USERNAME``
     - ``guacadmin``
     - Guacamole admin username
   * - ``GUACAMOLE_PASSWORD``
     - ``guacadmin``
     - Guacamole admin password
   * - ``GUACAMOLE_DATA_SOURCE``
     - ``postgresql``
     - Data source identifier (e.g. ``postgresql``, ``mysql``)
   * - ``GUACAMOLE_TIMEOUT``
     - ``30.0``
     - HTTP request timeout in seconds
   * - ``GUACAMOLE_VERIFY_SSL``
     - ``true``
     - Verify TLS certificates (set ``false`` for self-signed certs)
   * - ``GUACAMOLE_TRANSPORT``
     - ``stdio``
     - MCP transport: ``stdio`` or ``sse``
   * - ``HOST``
     - ``0.0.0.0``
     - Bind address for SSE transport
   * - ``PORT``
     - ``8000``
     - Port for SSE transport

Example ``.env`` file
---------------------

.. code-block:: bash

   GUACAMOLE_URL=https://guacamole.example.com
   GUACAMOLE_USERNAME=guacadmin
   GUACAMOLE_PASSWORD=supersecret
   GUACAMOLE_DATA_SOURCE=postgresql
   GUACAMOLE_VERIFY_SSL=true
   GUACAMOLE_TRANSPORT=stdio
