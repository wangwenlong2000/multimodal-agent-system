from __future__ import annotations

from typing import Any, Dict


def align_results(state: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    tool_resolver = context['tool_resolver']
    expert_results = state.get('expert_results', [])
    aligned_time = tool_resolver.invoke_tool('align_time', expert_results=expert_results)
    aligned_location = tool_resolver.invoke_tool('align_location', expert_results=expert_results)
    entity_map = tool_resolver.invoke_tool('entity_mapping', expert_results=expert_results)
    aligned = {
        'expert_results': expert_results,
        'time_alignment': aligned_time,
        'location_alignment': aligned_location,
        'entity_mapping': entity_map,
    }
    return {
        'aligned_results': aligned,
    }
