from __future__ import annotations

from typing import Any, Dict


def write_case_if_success(state: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    case_manager = context['case_manager']
    if not case_manager.should_write(state):
        return {'case_written': False}
    payload = case_manager.write_case(state)
    return {
        'case_written': True,
        'case_payload': payload,
    }
