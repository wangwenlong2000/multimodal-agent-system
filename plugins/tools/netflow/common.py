from __future__ import annotations

from typing import Any, Dict, Iterable, List


def _safe_int(v: Any, default: int = 0) -> int:
    try:
        if v is None or v == "":
            return default
        return int(float(v))
    except Exception:  # noqa: BLE001
        return default


def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        if v is None or v == "":
            return default
        return float(v)
    except Exception:  # noqa: BLE001
        return default


def rows_from_netflow_result(netflow_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(netflow_result, dict):
        return []
    for key in ("rows", "data", "flows"):
        value = netflow_result.get(key)
        if isinstance(value, list):
            return value
    result = netflow_result.get("result")
    if isinstance(result, dict):
        for key in ("rows", "data", "flows"):
            value = result.get(key)
            if isinstance(value, list):
                return value
    return []


def compute_mean_std(values: Iterable[float]) -> tuple[float, float]:
    vals = [float(v) for v in values]
    if not vals:
        return 0.0, 0.0
    mean = sum(vals) / len(vals)
    variance = sum((v - mean) ** 2 for v in vals) / len(vals)
    std = variance ** 0.5
    return mean, std