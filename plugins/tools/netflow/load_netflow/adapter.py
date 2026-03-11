from __future__ import annotations

from plugins.tools.netflow.common import load_records


def run(**kwargs):
    return load_records(
        path=kwargs.get('path'),
        device_id=kwargs.get('device_id'),
        start_time=kwargs.get('start_time'),
        end_time=kwargs.get('end_time'),
        query=kwargs.get('query'),
    )
