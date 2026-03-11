from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Dict, List, Optional


class ToolResolverError(RuntimeError):
    pass


class ToolResolver:
    def __init__(
        self,
        project_root: Path,
        plugins: Dict[str, Any],
        mcp_client: Any = None,
        mcp_config: Optional[Dict[str, Any]] = None,
        system_config: Optional[Dict[str, Any]] = None,
    ):
        self.project_root = project_root
        self.plugins = plugins
        self.mcp_client = mcp_client
        self.mcp_config = mcp_config or {}
        self.system_config = system_config or {}

    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        return self.plugins.get("tools", {})

    def resolve_tool_meta(self, tool_name: str) -> Optional[Dict[str, Any]]:
        return self.plugins.get("tools", {}).get(tool_name)

    def invoke_tool(
        self,
        tool_name: str,
        allowed_tools: Optional[List[str]] = None,
        caller: str = "",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        if allowed_tools is not None and tool_name not in allowed_tools:
            raise ToolResolverError(f"tool not allowed for caller={caller or 'unknown'}: {tool_name}")

        tool_meta = self.resolve_tool_meta(tool_name)
        if not tool_meta:
            raise ToolResolverError(f"tool not found: {tool_name}")

        source = tool_meta.get("source", "local")
        require_mcp = bool(self.system_config.get("require_mcp_execution", True))

        if require_mcp and source != "mcp":
            raise ToolResolverError(f"tool is not MCP-backed in MCP-only mode: {tool_name}")

        if source == "mcp":
            result = self._invoke_via_mcp(tool_name=tool_name, tool_meta=tool_meta, kwargs=kwargs)
            if result.get("status") == "error":
                raise ToolResolverError(f"MCP tool call failed: {tool_name}, detail={result}")
            return result

        if require_mcp:
            raise ToolResolverError(f"local adapter path is disabled in MCP-only mode: {tool_name}")

        return self._invoke_local_adapter(tool_name=tool_name, tool_meta=tool_meta, kwargs=kwargs)

    def get_tools_schema(self, allowed_tools: List[str]) -> List[Dict[str, Any]]:
        schemas: List[Dict[str, Any]] = []
        for tool_name in allowed_tools:
            meta = self.resolve_tool_meta(tool_name)
            if not meta:
                continue
            schemas.append(
                {
                    "name": tool_name,
                    "description": meta.get("description", ""),
                    "source": meta.get("source", "local"),
                    "server": meta.get("server"),
                    "input_schema": meta.get("input_schema", {}),
                    "output_schema": meta.get("output_schema", {}),
                    "examples": meta.get("examples", []),
                    "consumes": meta.get("consumes", []),
                    "produces": meta.get("produces", []),
                }
            )
        return schemas

    def discover_mcp_tools(self, server_name: str) -> Dict[str, Any]:
        if not self.mcp_client:
            return {"status": "error", "server": server_name, "message": "mcp client not initialized"}
        try:
            return self.mcp_client.list_tools(server_name)
        except Exception as exc:  # noqa: BLE001
            return {"status": "error", "server": server_name, "message": str(exc)}

    def _invoke_via_mcp(self, tool_name: str, tool_meta: Dict[str, Any], kwargs: Dict[str, Any]) -> Dict[str, Any]:
        if not self.mcp_client:
            return {"status": "error", "tool": tool_name, "message": "mcp client unavailable"}
        server_name = tool_meta.get("server")
        if not server_name:
            return {"status": "error", "tool": tool_name, "message": "tool missing MCP server mapping"}
        try:
            result = self.mcp_client.call_tool(server_name=server_name, tool_name=tool_name, arguments=kwargs)
            if isinstance(result, dict):
                result.setdefault("_transport", "mcp")
                result.setdefault("_server", server_name)
                result.setdefault("_tool", tool_name)
                return result
            return {
                "status": "ok",
                "result": result,
                "_transport": "mcp",
                "_server": server_name,
                "_tool": tool_name,
            }
        except Exception as exc:  # noqa: BLE001
            return {"status": "error", "tool": tool_name, "message": str(exc), "_transport": "mcp"}

    def _invoke_local_adapter(self, tool_name: str, tool_meta: Dict[str, Any], kwargs: Dict[str, Any]) -> Dict[str, Any]:
        adapter_path = Path(tool_meta["_path"]) / "adapter.py"
        if not adapter_path.exists():
            raise ToolResolverError(f"local adapter not found for tool={tool_name}: {adapter_path}")
        module = self._load_module(adapter_path, f"tool_{tool_name}_adapter")
        if not hasattr(module, "run"):
            raise ToolResolverError(f"local adapter missing run() for tool={tool_name}")
        result = module.run(**kwargs)
        if isinstance(result, dict):
            result.setdefault("_transport", "local")
            result.setdefault("_tool", tool_name)
            return result
        return {"status": "ok", "result": result, "_transport": "local", "_tool": tool_name}

    @staticmethod
    def _load_module(path: Path, module_name: str):
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        return module