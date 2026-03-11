from __future__ import annotations

from pathlib import Path


class PromptLoader:
    def __init__(self, project_root: Path):
        self.project_root = project_root

    def read_text(self, base_path: str, filename: str) -> str:
        path = Path(base_path) / filename
        if not path.exists():
            raise FileNotFoundError(path)
        return path.read_text(encoding="utf-8")