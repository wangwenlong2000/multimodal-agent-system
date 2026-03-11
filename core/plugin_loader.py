from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml


class PluginLoader:
    def __init__(self, project_root: Path):
        self.project_root = project_root

    def load_all_plugins(self) -> Dict[str, Dict[str, Any]]:
        return {
            "experts": self._load_plugin_group(self.project_root / "plugins" / "experts", "plugin.yaml", include_tools=True),
            "tools": self._load_plugin_group(self.project_root / "plugins" / "tools", "tool.yaml", recursive=True),
            "fusion": self._load_plugin_group(self.project_root / "plugins" / "fusion", "plugin.yaml"),
            "cases": self._load_plugin_group(self.project_root / "plugins" / "cases", "plugin.yaml"),
            "models": self._load_plugin_group(self.project_root / "plugins" / "models", "plugin.yaml"),
        }

    def filter_active_plugins(self, discovered: Dict[str, Dict[str, Any]], active_plugins: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        filtered: Dict[str, Dict[str, Any]] = {}
        for group, items in discovered.items():
            active_names = set(active_plugins.get(group, []))
            if not active_names:
                filtered[group] = items
                continue
            filtered[group] = {name: meta for name, meta in items.items() if name in active_names}
        return filtered

    def summarize(self, plugins: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        return {
            group: sorted(items.keys())
            for group, items in plugins.items()
        }

    def _load_plugin_group(
        self,
        base_dir: Path,
        config_name: str,
        include_tools: bool = False,
        recursive: bool = False,
    ) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        if not base_dir.exists():
            return results

        if recursive:
            config_paths = list(base_dir.rglob(config_name))
        else:
            config_paths = [p / config_name for p in base_dir.iterdir() if p.is_dir() and (p / config_name).exists()]

        for config_path in config_paths:
            meta = self._read_yaml(config_path)
            name = meta.get("name") or config_path.parent.name
            meta["_path"] = str(config_path.parent)
            if include_tools:
                tools_yaml = config_path.parent / "tools.yaml"
                if tools_yaml.exists():
                    meta["_tools"] = self._read_yaml(tools_yaml)
            results[name] = meta
        return results

    @staticmethod
    def _read_yaml(path: Path) -> Dict[str, Any]:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            raise RuntimeError(f"plugin config must be YAML object: {path}")
        return data