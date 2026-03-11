from __future__ import annotations

import json


def planner_node(state, context):
    preprocess = state.get("preprocess", {})
    available_experts = context["expert_registry"].list_experts()
    expert_summaries = context["expert_registry"].summarize_for_planner(available_experts)

    system_prompt = """你是多专家智能规划器。
你的任务是：
1. 根据用户问题和预处理结果，从候选专家中选择最合适的专家
2. 按专家能力分解任务
3. 规划最终需要的融合方式

要求：
- 只能选择候选专家中的名字
- 每个 task 必须包含:
  - task_id
  - expert
  - sub_goal
  - constraints
  - expected_output
  - success_criteria
- 如果是单场景问题，可以只选择一个专家
- 你必须只输出 JSON 对象

输出格式：
{
  "experts": ["..."],
  "tasks": [
    {
      "task_id": "...",
      "expert": "...",
      "sub_goal": "...",
      "constraints": {},
      "expected_output": [],
      "success_criteria": []
    }
  ],
  "fusion_plugin": "simple_fusion",
  "alignment_required": false,
  "reasoning_summary": "..."
}
"""

    user_prompt = json.dumps(
        {
            "query": state.get("query", ""),
            "preprocess": preprocess,
            "candidate_experts": expert_summaries,
            "available_fusion_plugins": list(context["plugins"].get("fusion", {}).keys()),
            "instruction": "根据专家领域和能力进行场景匹配与任务分解。仅输出 JSON。",
        },
        ensure_ascii=False,
        indent=2,
    )

    response = context["model_resolver"].chat_json(
        role="planner",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )
    plan = response["json"]

    chosen_experts = [e for e in plan.get("experts", []) if e in available_experts]
    if not chosen_experts:
        raise RuntimeError(f"planner returned no valid experts: {plan}")

    tasks = plan.get("tasks", [])
    if not isinstance(tasks, list) or not tasks:
        raise RuntimeError(f"planner returned empty tasks: {plan}")

    for task in tasks:
        if task.get("expert") not in chosen_experts:
            raise RuntimeError(f"planner task references non-selected expert: {task}")

    state["plan"] = {
        "experts": chosen_experts,
        "tasks": tasks,
        "fusion_plugin": plan.get("fusion_plugin", context["system_config"].get("default_fusion_plugin", "simple_fusion")),
        "alignment_required": bool(plan.get("alignment_required", False)),
        "reasoning_summary": plan.get("reasoning_summary", ""),
        "_llm": {
            "provider": response.get("provider"),
            "model": response.get("model"),
        },
    }
    return state