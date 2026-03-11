from __future__ import annotations

from typing import Any, Dict, List


class ExpertRegistry:
    def __init__(self, registry_config: Dict[str, Any], plugin_experts: Dict[str, Any] | None = None):
        self.registry_config = registry_config or {}
        self.plugin_experts = plugin_experts or {}

    def list_experts(self) -> List[str]:
        configured = self.registry_config.get("experts", {})
        names = set(configured.keys()) | set(self.plugin_experts.keys())
        return sorted(names)

    def get_expert_meta(self, expert_name: str) -> Dict[str, Any]:
        configured = self.registry_config.get("experts", {}).get(expert_name, {})
        plugin_meta = self.plugin_experts.get(expert_name, {})
        merged = {**configured, **plugin_meta}
        merged["name"] = expert_name
        return merged

    def summarize_for_planner(self, available_experts: List[str]) -> List[Dict[str, Any]]:
        summaries: List[Dict[str, Any]] = []
        for expert_name in available_experts:
            meta = self.get_expert_meta(expert_name)
            summaries.append(
                {
                    "name": expert_name,
                    "description": meta.get("description", ""),
                    "domain": meta.get("domain", meta.get("description", "")),
                    "capabilities": meta.get("capabilities", meta.get("supported_tasks", [])),
                    "analysis_patterns": meta.get("analysis_patterns", []),
                    "input_requirements": meta.get("input_requirements", []),
                    "output_contract": meta.get("output_contract", {}),
                    "tools": self._read_tool_whitelist(meta),
                    "tags": meta.get("tags", []),
                }
            )
        return summaries

    def _read_tool_whitelist(self, meta: Dict[str, Any]) -> List[str]:
        tools = []
        tools_file = meta.get("_tools")
        if isinstance(tools_file, dict):
            tools = tools_file.get("tools", [])
        if not tools and isinstance(meta.get("tools"), list):
            tools = meta.get("tools", [])
        return tools