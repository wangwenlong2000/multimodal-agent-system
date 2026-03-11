from __future__ import annotations

def run(**kwargs):
    expert_results = kwargs.get('expert_results', [])
    return {'status': 'ok', 'tool': 'align_time', 'aligned_window': '1min', 'count': len(expert_results)}
