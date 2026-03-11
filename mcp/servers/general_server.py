from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List


def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        if v is None or v == "":
            return default
        return float(v)
    except Exception:  # noqa: BLE001
        return default


class GeneralServer:
    def list_tools(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "tools": [
                {"name": "align_time"},
                {"name": "align_location"},
                {"name": "entity_mapping"},
                {"name": "fuse_evidence"},
            ],
        }

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name == "align_time":
            return self.align_time(**arguments)
        if tool_name == "align_location":
            return self.align_location(**arguments)
        if tool_name == "entity_mapping":
            return self.entity_mapping(**arguments)
        if tool_name == "fuse_evidence":
            return self.fuse_evidence(**arguments)
        return {"status": "error", "message": f"unknown tool: {tool_name}"}

    def align_time(
        self,
        records: List[Dict[str, Any]],
        time_field: str = "timestamp",
        tolerance_seconds: float = 60.0,
        **_: Any,
    ) -> Dict[str, Any]:
        if not isinstance(records, list):
            return {"status": "error", "message": "records must be a list"}

        normalized = []
        times = []

        for rec in records:
            if not isinstance(rec, dict):
                continue
            ts = _safe_float(rec.get(time_field))
            out = dict(rec)
            out["_aligned_time"] = ts
            normalized.append(out)
            times.append(ts)

        if not times:
            return {
                "status": "ok",
                "aligned_records": normalized,
                "window_start": 0.0,
                "window_end": 0.0,
                "tolerance_seconds": float(tolerance_seconds),
            }

        return {
            "status": "ok",
            "aligned_records": normalized,
            "window_start": min(times),
            "window_end": max(times),
            "tolerance_seconds": float(tolerance_seconds),
        }

    def align_location(
        self,
        records: List[Dict[str, Any]],
        lat_field: str = "latitude",
        lon_field: str = "longitude",
        tolerance_meters: float = 100.0,
        **_: Any,
    ) -> Dict[str, Any]:
        if not isinstance(records, list):
            return {"status": "error", "message": "records must be a list"}

        aligned = []
        for rec in records:
            if not isinstance(rec, dict):
                continue
            out = dict(rec)
            if lat_field in rec and lon_field in rec:
                out["_aligned_location"] = {
                    "lat": _safe_float(rec.get(lat_field)),
                    "lon": _safe_float(rec.get(lon_field)),
                }
            aligned.append(out)

        return {
            "status": "ok",
            "aligned_records": aligned,
            "tolerance_meters": float(tolerance_meters),
        }

    def entity_mapping(
        self,
        records: List[Dict[str, Any]],
        entity_fields: List[str] | None = None,
        **_: Any,
    ) -> Dict[str, Any]:
        if not isinstance(records, list):
            return {"status": "error", "message": "records must be a list"}

        fields = entity_fields or []
        mapping: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        for rec in records:
            if not isinstance(rec, dict):
                continue
            for field in fields:
                value = rec.get(field)
                if value not in (None, ""):
                    mapping[f"{field}:{value}"].append(rec)

        return {
            "status": "ok",
            "entity_map": dict(mapping),
            "entity_count": len(mapping),
        }

    def fuse_evidence(self, evidence_groups: List[Any], **_: Any) -> Dict[str, Any]:
        if not isinstance(evidence_groups, list):
            return {"status": "error", "message": "evidence_groups must be a list"}

        fused = []
        seen = set()

        for group in evidence_groups:
            if isinstance(group, list):
                items = group
            else:
                items = [group]

            for item in items:
                key = repr(item)
                if key in seen:
                    continue
                seen.add(key)
                fused.append(item)

        return {
            "status": "ok",
            "fused_evidence": fused,
            "count": len(fused),
        }


_SERVER = GeneralServer()


def list_tools() -> Dict[str, Any]:
    return _SERVER.list_tools()


def call_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    return _SERVER.call_tool(tool_name=tool_name, arguments=arguments)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) >= 2 and sys.argv[1] == "list_tools":
        print(json.dumps(list_tools(), ensure_ascii=False))
    else:
        print(json.dumps({"status": "ok", "server": "general_server"}, ensure_ascii=False))