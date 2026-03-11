from __future__ import annotations

from typing import Any, Dict


class FusionResolver:
    def __init__(self, project_root, plugins: Dict[str, Any]):
        self.project_root = project_root
        self.plugins = plugins

    def resolve(self, fusion_name: str) -> Dict[str, Any]:
        fusion = self.plugins.get("fusion", {}).get(fusion_name)
        if not fusion:
            raise RuntimeError(f"fusion plugin not found: {fusion_name}")
        return fusion