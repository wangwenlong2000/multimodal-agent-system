from __future__ import annotations


def route_experts_node(state, context):
    plan = state.get("plan", {})
    selected = plan.get("experts", [])

    routed = []
    for expert_name in selected:
        meta = context["expert_registry"].get_expert_meta(expert_name)
        tools_meta = meta.get("_tools", {})
        tool_names = tools_meta.get("tools", []) if isinstance(tools_meta, dict) else []
        mcp_tools = []
        for t in tool_names:
            tool_meta = context["tool_resolver"].resolve_tool_meta(t) or {}
            if tool_meta.get("source") == "mcp":
                mcp_tools.append(
                    {
                        "tool": t,
                        "server": tool_meta.get("server"),
                    }
                )
        routed.append(
            {
                "expert_name": expert_name,
                "meta": meta,
                "mcp_tools": mcp_tools,
            }
        )

    state["routed_experts"] = routed
    return state