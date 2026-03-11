from __future__ import annotations

from mcp.servers.netflow_server import NetflowServer


def test_netflow_scan_and_outlier():
    server = NetflowServer()

    loaded = server.load_netflow("data/samples/netflow/sample_packets.csv")
    assert loaded["status"] == "ok"
    assert loaded["row_count"] > 0

    agg = server.flow_aggregate(loaded)
    assert agg["status"] == "ok"
    assert agg["flow_count"] > 0

    scan = server.port_scan_detect(loaded, min_unique_dst_ports=20)
    assert scan["status"] == "ok"
    assert scan["suspicious_count"] >= 1

    vol = server.volume_outlier_detect(agg, sigma=3.0)
    assert vol["status"] == "ok"
    assert vol["outlier_count"] >= 1

    anomaly = server.anomaly_detect(agg)
    assert anomaly["status"] == "ok"
    assert anomaly["risk_level"] in {"low_risk", "medium_risk", "high_risk"}