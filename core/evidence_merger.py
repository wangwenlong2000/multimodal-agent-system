from __future__ import annotations

from typing import Any, Dict, List


class EvidenceMerger:
    @staticmethod
    def merge(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        merged = {'experts': [], 'evidence': [], 'metrics': {}, 'quality_notes': []}
        for item in results:
            merged['experts'].append(item.get('expert_name') or item.get('expert'))
            merged['evidence'].extend(item.get('evidence', []))
            merged['quality_notes'].extend(item.get('quality_notes', []))
            metrics = item.get('metrics', {})
            if isinstance(metrics, dict):
                merged['metrics'].update(metrics)
        return merged
