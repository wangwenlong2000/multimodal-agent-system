from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from core.case_manager import CaseManager
from core.config_loader import ConfigLoader
from core.expert_registry import ExpertRegistry
from core.fusion_resolver import FusionResolver
from core.mcp_client import MCPClientManager
from core.model_resolver import ModelResolver
from core.plugin_loader import PluginLoader
from core.prompt_loader import PromptLoader
from core.tool_resolver import ToolResolver


def bootstrap_system(project_root: Path) -> Dict[str, Any]:
    config_loader = ConfigLoader(project_root)
    system_config = config_loader.load_yaml("configs/system.yaml")
    active_plugins = config_loader.load_yaml("configs/active_plugins.yaml")
    active_model_provider = config_loader.load_yaml("configs/active_model_provider.yaml")
    expert_registry_config = config_loader.load_yaml("configs/expert_registry.yaml")
    case_policy = config_loader.load_yaml("configs/case_policy.yaml")
    mcp_servers = config_loader.load_yaml("configs/mcp_servers.yaml")

    plugin_loader = PluginLoader(project_root)
    discovered_plugins = plugin_loader.load_all_plugins()
    plugins = plugin_loader.filter_active_plugins(discovered_plugins, active_plugins)

    mcp_client = MCPClientManager(project_root=project_root, server_config=mcp_servers)
    tool_resolver = ToolResolver(
        project_root=project_root,
        plugins=plugins,
        mcp_client=mcp_client,
        mcp_config=mcp_servers,
        system_config=system_config,
    )
    model_resolver = ModelResolver(
        project_root=project_root,
        plugins=plugins,
        active_model_provider=active_model_provider,
        system_config=system_config,
    )
    fusion_resolver = FusionResolver(project_root=project_root, plugins=plugins)
    expert_registry = ExpertRegistry(expert_registry_config, plugin_experts=plugins.get("experts", {}))
    case_manager = CaseManager(project_root=project_root, case_policy=case_policy)
    prompt_loader = PromptLoader(project_root=project_root)

    return {
        "project_root": project_root,
        "system_config": system_config,
        "active_plugins": active_plugins,
        "active_model_provider": active_model_provider,
        "expert_registry_config": expert_registry_config,
        "plugins": plugins,
        "plugin_summary": plugin_loader.summarize(plugins),
        "mcp_servers": mcp_servers,
        "mcp_client": mcp_client,
        "tool_resolver": tool_resolver,
        "model_resolver": model_resolver,
        "fusion_resolver": fusion_resolver,
        "expert_registry": expert_registry,
        "case_manager": case_manager,
        "prompt_loader": prompt_loader,
    }