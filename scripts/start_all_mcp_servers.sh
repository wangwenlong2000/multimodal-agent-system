#!/usr/bin/env bash
set -euo pipefail
python mcp/servers/general_server.py &
python mcp/servers/trajectory_server.py &
python mcp/servers/netflow_server.py &
python mcp/servers/streetview_server.py &
wait
