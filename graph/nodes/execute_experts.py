from __future__ import annotations

import importlib.util
from pathlib import Path


def execute_experts_node(state, context):
    results = {}

    for routed in state.get("routed_experts", []):
        expert_name = routed["expert_name"]
        meta = routed["meta"]

        handler_file = meta.get("handler", "handler.py")
        handler_path = Path(meta["_path"]) / handler_file
        if not handler_path.exists():
            raise RuntimeError(f"expert handler not found: {handler_path}")

        spec = importlib.util.spec_from_file_location(f"expert_handler_{expert_name}", handler_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)

        if not hasattr(module, "run"):
            raise RuntimeError(f"expert handler missing run(): {handler_path}")

        result = module.run(state=state, context=context, expert_meta=meta, expert_name=expert_name)
        results[expert_name] = result

    state["expert_results"] = results
    return state