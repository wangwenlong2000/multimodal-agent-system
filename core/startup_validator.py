from __future__ import annotations

from typing import Any, Dict


class StartupValidator:
    def __init__(self, context: Dict[str, Any]):
        self.context = context

    def run_or_raise(self) -> None:
        self._validate_model()
        self._validate_mcp()
        self._validate_tools()

    def _validate_model(self) -> None:
        self.context["model_resolver"].ensure_ready()

    def _validate_mcp(self) -> None:
        system_config = self.context["system_config"]
        mcp_servers = self.context["mcp_servers"]
        mcp_client = self.context["mcp_client"]
        require_mcp = bool(system_config.get("require_mcp_execution", True))

        if require_mcp and not bool(mcp_servers.get("enabled", False)):
            raise RuntimeError("MCP must be enabled in enterprise mode")

        if require_mcp and bool(mcp_servers.get("fallback_to_local_adapter", True)):
            raise RuntimeError("fallback_to_local_adapter must be false in MCP-only mode")

        for server_name in mcp_client.list_server_names():
            probe = self.context["tool_resolver"].discover_mcp_tools(server_name)
            if probe.get("status") == "error":
                raise RuntimeError(f"MCP server probe failed: {server_name}, detail={probe}")

    def _validate_tools(self) -> None:
        require_mcp = bool(self.context["system_config"].get("require_mcp_execution", True))
        for tool_name, meta in self.context["plugins"].get("tools", {}).items():
            if require_mcp and meta.get("source") != "mcp":
                raise RuntimeError(f"tool must be MCP-backed in enterprise mode: {tool_name}")