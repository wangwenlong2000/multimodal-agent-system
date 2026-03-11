from __future__ import annotations

def run(**kwargs):
    query = kwargs.get('query', '')
    return {'status': 'ok', 'tool': 'load_trajectory', 'query': query, 'data_ref': 'mock://trajectory/demo', 'records': 10}
