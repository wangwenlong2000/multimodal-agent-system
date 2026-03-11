from __future__ import annotations

from plugins.tools.netflow.common import aggregate_records


def run(**kwargs):
    return aggregate_records(kwargs.get('netflow', {}))
