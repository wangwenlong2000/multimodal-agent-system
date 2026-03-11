from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

from plugins.tools.netflow.common import _safe_float, _safe_int, compute_mean_std, rows_from_netflow_result


class NetflowServer:
    def list_tools(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "tools": [
                {"name": "load_netflow"},
                {"name": "flow_aggregate"},
                {"name": "port_scan_detect"},
                {"name": "volume_outlier_detect"},
                {"name": "anomaly_detect"},
            ],
        }

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name == "load_netflow":
            return self.load_netflow(**arguments)
        if tool_name == "flow_aggregate":
            return self.flow_aggregate(**arguments)
        if tool_name == "port_scan_detect":
            return self.port_scan_detect(**arguments)
        if tool_name == "volume_outlier_detect":
            return self.volume_outlier_detect(**arguments)
        if tool_name == "anomaly_detect":
            return self.anomaly_detect(**arguments)
        return {"status": "error", "message": f"unknown tool: {tool_name}"}

    def load_netflow(self, path: str, **_: Any) -> Dict[str, Any]:
        csv_path = Path(path)
        if not csv_path.exists():
            return {"status": "error", "tool": "load_netflow", "message": f"file not found: {path}"}

        rows: List[Dict[str, Any]] = []
        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(
                    {
                        "timestamp": _safe_float(row.get("timestamp")),
                        "device_id": row.get("device_id", ""),
                        "src_ip": row.get("src_ip", ""),
                        "dst_ip": row.get("dst_ip", ""),
                        "src_port": _safe_int(row.get("src_port")),
                        "dst_port": _safe_int(row.get("dst_port")),
                        "protocol": (row.get("protocol") or "").upper(),
                        "frame_len": _safe_int(row.get("frame_len")),
                    }
                )

        return {
            "status": "ok",
            "tool": "load_netflow",
            "rows": rows,
            "row_count": len(rows),
            "path": path,
        }

    def flow_aggregate(self, netflow: Dict[str, Any], **_: Any) -> Dict[str, Any]:
        rows = rows_from_netflow_result(netflow)
        grouped: Dict[tuple, Dict[str, Any]] = {}

        for row in rows:
            key = (
                row.get("src_ip", ""),
                row.get("dst_ip", ""),
                _safe_int(row.get("src_port")),
                _safe_int(row.get("dst_port")),
                row.get("protocol", ""),
            )
            ts = _safe_float(row.get("timestamp"))
            frame_len = _safe_int(row.get("frame_len"))

            if key not in grouped:
                grouped[key] = {
                    "src_ip": key[0],
                    "dst_ip": key[1],
                    "src_port": key[2],
                    "dst_port": key[3],
                    "protocol": key[4],
                    "start_time": ts,
                    "end_time": ts,
                    "packet_count": 0,
                    "bytes_total": 0,
                }

            flow = grouped[key]
            flow["packet_count"] += 1
            flow["bytes_total"] += frame_len
            flow["start_time"] = min(flow["start_time"], ts)
            flow["end_time"] = max(flow["end_time"], ts)

        flows = list(grouped.values())
        for flow in flows:
            flow["duration"] = max(0.0, _safe_float(flow["end_time"]) - _safe_float(flow["start_time"]))

        return {
            "status": "ok",
            "tool": "flow_aggregate",
            "flows": flows,
            "flow_count": len(flows),
        }

    def port_scan_detect(self, netflow: Dict[str, Any], min_unique_dst_ports: int = 20, **_: Any) -> Dict[str, Any]:
        rows = rows_from_netflow_result(netflow)

        port_sets: Dict[str, set] = defaultdict(set)
        for row in rows:
            src_ip = row.get("src_ip", "")
            dst_port = _safe_int(row.get("dst_port"))
            if src_ip and dst_port > 0:
                port_sets[src_ip].add(dst_port)

        suspicious = []
        for src_ip, ports in port_sets.items():
            if len(ports) > int(min_unique_dst_ports):
                suspicious.append(
                    {
                        "src_ip": src_ip,
                        "unique_dst_ports": len(ports),
                        "sample_ports": sorted(list(ports))[:20],
                    }
                )

        suspicious.sort(key=lambda x: x["unique_dst_ports"], reverse=True)

        return {
            "status": "ok",
            "tool": "port_scan_detect",
            "threshold": int(min_unique_dst_ports),
            "suspicious_sources": suspicious,
            "suspicious_count": len(suspicious),
        }

    def volume_outlier_detect(self, netflow: Dict[str, Any], sigma: float = 3.0, **_: Any) -> Dict[str, Any]:
        rows = rows_from_netflow_result(netflow)
        byte_values = [_safe_float(r.get("bytes_total", 0)) for r in rows]
        mean_bytes, std_bytes = compute_mean_std(byte_values)
        threshold = mean_bytes + float(sigma) * std_bytes

        outliers = []
        for row in rows:
            bytes_total = _safe_float(row.get("bytes_total", 0))
            if bytes_total > threshold:
                outliers.append(
                    {
                        "src_ip": row.get("src_ip", ""),
                        "dst_ip": row.get("dst_ip", ""),
                        "src_port": _safe_int(row.get("src_port")),
                        "dst_port": _safe_int(row.get("dst_port")),
                        "protocol": row.get("protocol", ""),
                        "bytes_total": bytes_total,
                        "packet_count": _safe_int(row.get("packet_count")),
                        "start_time": _safe_float(row.get("start_time")),
                        "end_time": _safe_float(row.get("end_time")),
                    }
                )

        outliers.sort(key=lambda x: x["bytes_total"], reverse=True)

        return {
            "status": "ok",
            "tool": "volume_outlier_detect",
            "mean_bytes": mean_bytes,
            "std_bytes": std_bytes,
            "threshold": threshold,
            "outliers": outliers,
            "outlier_count": len(outliers),
        }

    def anomaly_detect(self, netflow: Dict[str, Any], **_: Any) -> Dict[str, Any]:
        rows = rows_from_netflow_result(netflow)
        findings = []

        for row in rows:
            bytes_total = _safe_float(row.get("bytes_total", 0))
            packet_count = _safe_int(row.get("packet_count", 0))
            if bytes_total > 10000 or packet_count > 50:
                findings.append(
                    {
                        "src_ip": row.get("src_ip", ""),
                        "dst_ip": row.get("dst_ip", ""),
                        "bytes_total": bytes_total,
                        "packet_count": packet_count,
                        "reason": "high_volume_or_high_packet_count",
                    }
                )

        risk_level = "low_risk"
        if len(findings) >= 2:
            risk_level = "medium_risk"
        if len(findings) >= 4:
            risk_level = "high_risk"

        return {
            "status": "ok",
            "tool": "anomaly_detect",
            "findings": findings,
            "finding_count": len(findings),
            "risk_level": risk_level,
        }


_SERVER = NetflowServer()


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
        print(json.dumps({"status": "ok", "server": "netflow_server"}, ensure_ascii=False))