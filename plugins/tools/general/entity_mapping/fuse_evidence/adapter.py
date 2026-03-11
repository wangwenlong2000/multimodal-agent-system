from __future__ import annotations

def run(**kwargs):
    aligned = kwargs.get('aligned_results', {})
    return {'status': 'ok', 'tool': 'fuse_evidence', 'summary': 'fused placeholder', 'data': aligned}
