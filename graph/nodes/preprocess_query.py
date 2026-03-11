from __future__ import annotations

import json


def preprocess_query_node(state, context):
    query = state.get("query", "")

    system_prompt = """你是查询预处理器。
你的任务是把用户问题转成结构化分析需求。
你必须只输出 JSON 对象。

输出字段：
- intent: 用户主要意图
- modalities: 需要涉及的模态列表，可选 trajectory/netflow/streetview
- entities: 相关实体列表
- constraints: 约束条件对象
- analysis_type: 分析类型
- requires_alignment: 是否需要跨模态对齐
"""

    user_prompt = json.dumps(
        {
            "query": query,
            "instruction": "识别问题涉及的分析模态、约束和分析类型。仅输出 JSON。",
        },
        ensure_ascii=False,
        indent=2,
    )

    response = context["model_resolver"].chat_json(
        role="preprocess",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )
    parsed = response["json"]

    state["preprocess"] = {
        "intent": parsed.get("intent", ""),
        "modalities": parsed.get("modalities", []),
        "entities": parsed.get("entities", []),
        "constraints": parsed.get("constraints", {}),
        "analysis_type": parsed.get("analysis_type", ""),
        "requires_alignment": bool(parsed.get("requires_alignment", False)),
        "_llm": {
            "provider": response.get("provider"),
            "model": response.get("model"),
        },
    }
    return state