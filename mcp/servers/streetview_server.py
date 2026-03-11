from __future__ import annotations

from typing import Any, Dict, List


class StreetviewServer:
    def list_tools(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "tools": [
                {"name": "align_time"},
                {"name": "align_location"},
            ],
        }

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name == "align_time":
            return self.align_time(**arguments)
        if tool_name == "align_location":
            return self.align_location(**arguments)
        return {"status": "error", "message": f"unknown tool: {tool_name}"}

    def align_time(
        self,
        records: List[Dict[str, Any]],
        time_field: str = "timestamp",
        tolerance_seconds: float = 60.0,
        **_: Any,
    ) -> Dict[str, Any]:
        normalized = []
        times = []
        for rec in records or []:
            if not isinstance(rec, dict):
                continue
            out = dict(rec)
            ts = rec.get(time_field, 0)
            try:
                ts = float(ts)
            except Exception:
                ts = 0.0
            out["_aligned_time"] = ts
            normalized.append(out)
            times.append(ts)

        return {
            "status": "ok",
            "aligned_records": normalized,
            "window_start": min(times) if times else 0.0,
            "window_end": max(times) if times else 0.0,
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
        aligned = []
        for rec in records or []:
            if not isinstance(rec, dict):
                continue
            out = dict(rec)
            if lat_field in rec and lon_field in rec:
                try:
                    lat = float(rec.get(lat_field, 0))
                except Exception:
                    lat = 0.0
                try:
                    lon = float(rec.get(lon_field, 0))
                except Exception:
                    lon = 0.0
                out["_aligned_location"] = {"lat": lat, "lon": lon}
            aligned.append(out)

        return {
            "status": "ok",
            "aligned_records": aligned,
            "tolerance_meters": float(tolerance_meters),
        }


_SERVER = StreetviewServer()


def list_tools() -> Dict[str, Any]:
    return _SERVER.list_tools()


def call_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    return _SERVER.call_tool(tool_name=tool_name, arguments=arguments)


if __name__ == "__main__":
    import json
    print(json.dumps({"status": "ok", "server": "streetview_server"}, ensure_ascii=False))