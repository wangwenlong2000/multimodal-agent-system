from __future__ import annotations

def run(**kwargs):
    query = kwargs.get('query', '')
    return {'status': 'ok', 'tool': 'load_streetview', 'query': query, 'data_ref': 'mock://streetview/demo', 'images': 3}
