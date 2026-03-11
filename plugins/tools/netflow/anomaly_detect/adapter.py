from __future__ import annotations

from plugins.tools.netflow.common import aggregate_records, detect_anomaly


def run(**kwargs):
    netflow = kwargs.get('netflow', {})
    aggregated = aggregate_records(netflow)
    return detect_anomaly(aggregated)
