from __future__ import annotations

def run(**kwargs):
    expert_results = kwargs.get('expert_results', [])
    return {'status': 'ok', 'tool': 'entity_mapping', 'strategy': 'static_mapping_placeholder', 'count': len(expert_results)}
