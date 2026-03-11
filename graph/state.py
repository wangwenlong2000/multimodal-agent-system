from __future__ import annotations

from typing import Any, Dict, List, TypedDict


class AgentState(TypedDict, total=False):
    query: str
    intent: str
    parsed_query: Dict[str, Any]
    plan: Dict[str, Any]
    selected_experts: List[str]
    available_experts: List[str]
    expert_results: List[Dict[str, Any]]
    aligned_results: Dict[str, Any]
    fusion_result: Dict[str, Any]
    final_answer: str
    provider_used: str
    provider_status: str
    model_used: str
    confidence: float
    success: bool
    case_written: bool
    case_payload: Dict[str, Any]
    debug: Dict[str, Any]
