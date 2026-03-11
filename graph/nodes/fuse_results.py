from __future__ import annotations


def fuse_results_node(state, context):
    expert_results = state.get("expert_results", {})
    findings = []
    risk_levels = []

    for expert_name, result in expert_results.items():
        findings.append(
            {
                "expert": expert_name,
                "summary": result.get("summary", ""),
                "metrics": result.get("metrics", {}),
                "evidence": result.get("evidence", []),
                "confidence": result.get("confidence", 0.0),
            }
        )

        latest_result = result.get("latest_result") or {}
        if isinstance(latest_result, dict) and latest_result.get("risk_level"):
            risk_levels.append(latest_result.get("risk_level"))

    fused_risk = "low_risk"
    if "high_risk" in risk_levels:
        fused_risk = "high_risk"
    elif "medium_risk" in risk_levels:
        fused_risk = "medium_risk"

    state["fused_result"] = {
        "status": "ok",
        "risk_level": fused_risk,
        "findings": findings,
        "expert_count": len(findings),
    }
    return state