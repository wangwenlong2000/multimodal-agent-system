from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

from app.bootstrap import bootstrap_system
from core.startup_validator import StartupValidator
from graph.graph_builder import build_graph


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run multimodal agent system")
    parser.add_argument("--query", type=str, default="分析目标对象在夜间的轨迹、网络流量与街景情况")
    parser.add_argument("--dump-state", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    context = bootstrap_system(PROJECT_ROOT)
    validator = StartupValidator(context)

    if args.preflight:
        validator.run_or_raise()
        print("Preflight checks passed.")
        return

    validator.run_or_raise()

    graph = build_graph(context)
    result = graph.invoke({"query": args.query})

    print("\n=== Final Answer ===")
    print(result["final_answer"])
    if args.dump_state:
        print("\n=== Final State ===")
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()