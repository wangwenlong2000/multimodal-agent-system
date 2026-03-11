from __future__ import annotations

from typing import Any, Dict


def run(aligned_results: Dict[str, Any], plan: Dict[str, Any]) -> Dict[str, Any]:
    merged = aligned_results.get('merged', {})
    experts = merged.get('experts', [])
    summary = f"已完成融合，涉及专家：{', '.join(experts)}"
    return {
        'status': 'ok',
        'summary': summary,
        'confidence': 0.81,
        'aligned_results': aligned_results,
        'plan': plan,
    }
