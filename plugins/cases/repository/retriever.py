from __future__ import annotations

from pathlib import Path
import json


def retrieve_all(base_dir: str):
    root = Path(base_dir)
    results = []
    for f in root.rglob('*.json'):
        if f.name == 'index.json' or f.name == 'case_schema.json':
            continue
        try:
            results.append(json.loads(f.read_text(encoding='utf-8')))
        except Exception:
            pass
    return results
