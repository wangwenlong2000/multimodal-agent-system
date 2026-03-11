from __future__ import annotations

import json


def generate_response_node(state, context):
    system_prompt = """你是最终响应生成器。
根据规划、专家结果和融合结果，生成面向用户的最终中文回答。

要求：
- 回答必须清晰、专业、结构化
- 给出关键发现
- 给出明确结论
- 如果有风险级别，要直接说明
- 不要编造没有出现的证据
- 只输出 JSON:
{
  "final_answer": "..."
}
"""

    user_prompt = json.dumps(
        {
            "query": state.get("query", ""),
            "preprocess": state.get("preprocess", {}),
            "plan": state.get("plan", {}),
            "expert_results": state.get("expert_results", {}),
            "fused_result": state.get("fused_result", {}),
        },
        ensure_ascii=False,
        indent=2,
    )

    response = context["model_resolver"].chat_json(
        role="response",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )
    parsed = response["json"]
    final_answer = parsed.get("final_answer", "").strip()
    if not final_answer:
        raise RuntimeError("response generator returned empty final_answer")

    state["final_answer"] = final_answer
    state["response_meta"] = {
        "provider": response.get("provider"),
        "model": response.get("model"),
    }
    return state