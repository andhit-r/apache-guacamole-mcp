Quick Start
===========

Using with Claude Desktop
--------------------------

Add the following to your ``claude_desktop_config.json``:

.. code-block:: json

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

Using with Docker (stdio)
--------------------------

.. code-block:: json

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

Using with VS Code (GitHub Copilot)
-------------------------------------

Add to ``.vscode/mcp.json``:

.. code-block:: json

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

Available Tools
---------------

The MCP server exposes **57 tools** grouped by category:

Authentication
~~~~~~~~~~~~~~
* ``authenticate`` — Authenticate with Guacamole and cache token
* ``logout`` — Invalidate the current auth token

Users
~~~~~
Create, read, update, delete users; manage passwords, permissions, and
group memberships.

User Groups
~~~~~~~~~~~
Create, read, update, delete user groups; manage member users, nested
groups, and connection permissions.

Connections
~~~~~~~~~~~
Create, read, update, delete connections (RDP, SSH, VNC, Telnet,
Kubernetes); query active connections and kill sessions.

Connection Groups
~~~~~~~~~~~~~~~~~
Organize connections in hierarchical groups; browse the connection tree.

History
~~~~~~~
Query audit logs for connection history and user activity.
