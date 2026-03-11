from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Dict


class MCPClientManager:
    def __init__(self, project_root: Path, server_config: Dict[str, Any]):
        self.project_root = project_root
        self.server_config = server_config or {}
        self._servers: Dict[str, Any] = {}

    def list_server_names(self):
        return list((self.server_config.get("servers") or {}).keys())

    def _server_entry(self, server_name: str) -> Dict[str, Any]:
        servers = self.server_config.get("servers") or {}
        if server_name not in servers:
            raise RuntimeError(f"MCP server not configured: {server_name}")
        return servers[server_name]

    def _resolve_script_path(self, raw_path: str) -> Path:
        python_path = "python"
        resolved = raw_path.replace("{project_root}", str(self.project_root)).replace("{python}", python_path)
        return Path(resolved)

    def _load_server_module(self, server_name: str):
        if server_name in self._servers:
            return self._servers[server_name]

        entry = self._server_entry(server_name)
        args = entry.get("args", [])
        if not args:
            raise RuntimeError(f"MCP server args missing: {server_name}")

        script_path = self._resolve_script_path(args[0])
        if not script_path.exists():
            raise RuntimeError(f"MCP server script not found: {script_path}")

        spec = importlib.util.spec_from_file_location(f"mcp_server_{server_name}", script_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        self._servers[server_name] = module
        return module

    def list_tools(self, server_name: str) -> Dict[str, Any]:
        module = self._load_server_module(server_name)
        if not hasattr(module, "list_tools"):
            raise RuntimeError(f"MCP server missing list_tools(): {server_name}")
        result = module.list_tools()
        if isinstance(result, dict):
            return result
        return {"status": "ok", "tools": result}

    def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        module = self._load_server_module(server_name)
        if not hasattr(module, "call_tool"):
            raise RuntimeError(f"MCP server missing call_tool(): {server_name}")
        result = module.call_tool(tool_name=tool_name, arguments=arguments)
        if isinstance(result, dict):
            return result
        return {"status": "ok", "result": result}