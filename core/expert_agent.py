from __future__ import annotations

import json
from typing import Any, Dict, List


class ExpertAgentError(RuntimeError):
    pass


class ExpertToolAgent:
    def __init__(self, context: Dict[str, Any]):
        self.context = context
        self.model_resolver = context["model_resolver"]
        self.tool_resolver = context["tool_resolver"]
        self.prompt_loader = context["prompt_loader"]
        self.max_steps = int(context["system_config"].get("expert_agent_max_steps", 6))

    def run(self, state: Dict[str, Any], expert_meta: Dict[str, Any], expert_name: str) -> Dict[str, Any]:
        allowed_tools = self._allowed_tools(expert_meta)
        if not allowed_tools:
            raise ExpertAgentError(f"expert has no allowed tools: {expert_name}")

        tool_schemas = self.tool_resolver.get_tools_schema(allowed_tools)
        tasks = [t for t in state.get("plan", {}).get("tasks", []) if t.get("expert") == expert_name]
        task_card = tasks[0] if tasks else {
            "task_id": f"{expert_name}_task_1",
            "expert": expert_name,
            "sub_goal": "完成专家分析任务",
            "constraints": {},
            "expected_output": [],
            "success_criteria": [],
        }

        history: List[Dict[str, Any]] = []
        latest_result: Dict[str, Any] | None = None

        system_prompt = self._build_system_prompt(expert_name, expert_meta, tool_schemas)

        for step in range(1, self.max_steps + 1):
            user_prompt = self._build_user_prompt(
                query=state.get("query", ""),
                task_card=task_card,
                history=history,
                selected_tools=allowed_tools,
                tool_schemas=tool_schemas,
            )
            response = self.model_resolver.chat_json(
                role="expert",
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
            action = response["json"]

            action_type = action.get("action")
            if action_type == "finish":
                return self._finalize(
                    expert_name=expert_name,
                    expert_meta=expert_meta,
                    history=history,
                    final_payload=action,
                    latest_result=latest_result,
                )

            if action_type != "call_tool":
                raise ExpertAgentError(f"invalid expert action from LLM: {action}")

            tool_name = action.get("tool_name")
            if tool_name not in allowed_tools:
                raise ExpertAgentError(f"expert selected tool outside whitelist: {tool_name}")

            raw_args = action.get("arguments", {})
            if not isinstance(raw_args, dict):
                raise ExpertAgentError(f"tool arguments must be object: {raw_args}")

            tool_args = self._hydrate_args(raw_args=raw_args, history=history, state=state)
            tool_result = self.tool_resolver.invoke_tool(
                tool_name=tool_name,
                allowed_tools=allowed_tools,
                caller=expert_name,
                **tool_args,
            )
            latest_result = tool_result
            history.append(
                {
                    "step": step,
                    "tool_name": tool_name,
                    "arguments": tool_args,
                    "result": tool_result,
                }
            )

        raise ExpertAgentError(f"expert exceeded max steps without finish: {expert_name}")

    def _build_system_prompt(self, expert_name: str, expert_meta: Dict[str, Any], tool_schemas: List[Dict[str, Any]]) -> str:
        role_prompt = self._safe_read_prompt(expert_meta.get("_path"), expert_meta.get("system_prompt"))
        instructions = {
            "expert_name": expert_name,
            "description": expert_meta.get("description", ""),
            "domain": expert_meta.get("domain", ""),
            "capabilities": expert_meta.get("capabilities", expert_meta.get("supported_tasks", [])),
            "analysis_patterns": expert_meta.get("analysis_patterns", []),
            "rules": [
                "你必须只从提供的工具白名单中选择工具。",
                "你必须基于当前任务、已有中间结果和工具 schema 自主决策下一步。",
                "你不能编造工具结果。",
                "如果分析已经足够，输出 finish。",
                "你必须只输出 JSON。",
            ],
            "output_schema": {
                "call_tool": {
                    "action": "call_tool",
                    "tool_name": "工具名",
                    "arguments": {"key": "value"},
                    "rationale": "为什么调用这个工具",
                },
                "finish": {
                    "action": "finish",
                    "summary": "专家结论",
                    "confidence": 0.0,
                    "metrics": {},
                    "evidence": [],
                    "quality_notes": [],
                },
            },
            "tool_schemas": tool_schemas,
        }
        return f"{role_prompt}\n\n{json.dumps(instructions, ensure_ascii=False, indent=2)}"

    def _build_user_prompt(
        self,
        query: str,
        task_card: Dict[str, Any],
        history: List[Dict[str, Any]],
        selected_tools: List[str],
        tool_schemas: List[Dict[str, Any]],
    ) -> str:
        return json.dumps(
            {
                "query": query,
                "task_card": task_card,
                "history": history,
                "selected_tools": selected_tools,
                "tool_schemas": tool_schemas,
                "instruction": "基于任务和历史结果，决定下一步是 call_tool 还是 finish。仅输出 JSON 对象。",
            },
            ensure_ascii=False,
            indent=2,
        )

    def _allowed_tools(self, expert_meta: Dict[str, Any]) -> List[str]:
        tools_meta = expert_meta.get("_tools", {})
        tools = tools_meta.get("tools", []) if isinstance(tools_meta, dict) else []
        return [t for t in tools if isinstance(t, str)]

    def _hydrate_args(self, raw_args: Dict[str, Any], history: List[Dict[str, Any]], state: Dict[str, Any]) -> Dict[str, Any]:
        args = dict(raw_args)

        if "query" not in args:
            args["query"] = state.get("query", "")

        if "path" not in args:
            args["path"] = "data/samples/netflow/sample_packets.csv"

        last_result = history[-1]["result"] if history else None
        if "netflow" not in args and last_result and isinstance(last_result, dict):
            if last_result.get("tool") == "load_netflow":
                args["netflow"] = last_result
            elif last_result.get("tool") == "flow_aggregate":
                args["netflow"] = last_result

        return args

    def _finalize(
        self,
        expert_name: str,
        expert_meta: Dict[str, Any],
        history: List[Dict[str, Any]],
        final_payload: Dict[str, Any],
        latest_result: Dict[str, Any] | None,
    ) -> Dict[str, Any]:
        return {
            "expert_name": expert_name,
            "status": "ok",
            "summary": final_payload.get("summary", ""),
            "evidence": final_payload.get("evidence", []),
            "metrics": final_payload.get("metrics", {}),
            "confidence": float(final_payload.get("confidence", 0.0)),
            "quality_notes": final_payload.get("quality_notes", []),
            "tool_history": history,
            "latest_result": latest_result,
            "domain": expert_meta.get("domain", ""),
            "capabilities": expert_meta.get("capabilities", []),
        }

    def _safe_read_prompt(self, base_path: str | None, filename: str | None) -> str:
        if not base_path or not filename:
            return ""
        try:
            return self.prompt_loader.read_text(base_path, filename)
        except Exception:  # noqa: BLE001
            return ""