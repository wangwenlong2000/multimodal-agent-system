from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml


class ConfigLoader:
    def __init__(self, project_root: Path):
        self.project_root = project_root

    def load_yaml(self, relative_path: str) -> Dict[str, Any]:
        path = self.project_root / relative_path
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            raise RuntimeError(f"YAML config must be an object: {path}")
        return data