from __future__ import annotations

from pathlib import Path
import sys
import yaml


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    registry_path = project_root / 'configs' / 'expert_registry.yaml'
    active_plugins_path = project_root / 'configs' / 'active_plugins.yaml'
    registry = yaml.safe_load(registry_path.read_text(encoding='utf-8')) or {}
    active = yaml.safe_load(active_plugins_path.read_text(encoding='utf-8')) or {}

    registry_names = {item.get('name') for item in registry.get('experts', []) if isinstance(item, dict)}
    active_names = set(active.get('experts', []) or [])

    missing = sorted(active_names - registry_names)
    extra = sorted(registry_names - active_names)

    print('active experts:', sorted(active_names))
    print('registry experts:', sorted(registry_names))
    if missing:
        print('missing in registry:', missing)
    if extra:
        print('not active but in registry:', extra)
    return 1 if missing else 0


if __name__ == '__main__':
    raise SystemExit(main())
