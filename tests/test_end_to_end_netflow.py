from __future__ import annotations

from pathlib import Path

from app.bootstrap import bootstrap_system
from graph.graph_builder import build_graph


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class DummyModelResolver:
    def ensure_ready(self):
        return None

    def chat_json(self, role: str, system_prompt: str, user_prompt: str):
        if role == "preprocess":
            return {
                "provider": "dummy",
                "model": "dummy",
                "json": {
                    "intent": "网络安全分析",
                    "modalities": ["netflow"],
                    "entities": [],
                    "constraints": {"min_unique_dst_ports": 20, "sigma": 3},
                    "analysis_type": "anomaly_detection",
                    "requires_alignment": False,
                },
            }

        if role == "planner":
            return {
                "provider": "dummy",
                "model": "dummy",
                "json": {
                    "experts": ["netflow_expert"],
                    "tasks": [
                        {
                            "task_id": "task_netflow_1",
                            "expert": "netflow_expert",
                            "sub_goal": "检测端口扫描和3σ异常流量",
                            "constraints": {"min_unique_dst_ports": 20, "sigma": 3},
                            "expected_output": ["scan_findings", "volume_outliers", "risk_level"],
                            "success_criteria": ["识别可疑源IP", "识别异常大流量"],
                        }
                    ],
                    "fusion_plugin": "simple_fusion",
                    "alignment_required": False,
                    "reasoning_summary": "单一网络流量场景，选择netflow专家即可。",
                },
            }

        if role == "expert":
            if '"tool_name": "load_netflow"' in user_prompt:
                pass

            history_markers = user_prompt
            if '"history": []' in history_markers:
                return {
                    "provider": "dummy",
                    "model": "dummy",
                    "json": {
                        "action": "call_tool",
                        "tool_name": "load_netflow",
                        "arguments": {"path": "data/samples/netflow/sample_packets.csv"},
                        "rationale": "先加载数据",
                    },
                }
            if '"tool_name": "load_netflow"' in history_markers and '"tool_name": "flow_aggregate"' not in history_markers:
                return {
                    "provider": "dummy",
                    "model": "dummy",
                    "json": {
                        "action": "call_tool",
                        "tool_name": "flow_aggregate",
                        "arguments": {},
                        "rationale": "做流级聚合",
                    },
                }
            if '"tool_name": "flow_aggregate"' in history_markers and '"tool_name": "port_scan_detect"' not in history_markers:
                return {
                    "provider": "dummy",
                    "model": "dummy",
                    "json": {
                        "action": "call_tool",
                        "tool_name": "port_scan_detect",
                        "arguments": {"min_unique_dst_ports": 20},
                        "rationale": "检测端口扫描",
                    },
                }
            if '"tool_name": "port_scan_detect"' in history_markers and '"tool_name": "volume_outlier_detect"' not in history_markers:
                return {
                    "provider": "dummy",
                    "model": "dummy",
                    "json": {
                        "action": "call_tool",
                        "tool_name": "volume_outlier_detect",
                        "arguments": {"sigma": 3},
                        "rationale": "检测3σ异常流量",
                    },
                }
            if '"tool_name": "volume_outlier_detect"' in history_markers and '"tool_name": "anomaly_detect"' not in history_markers:
                return {
                    "provider": "dummy",
                    "model": "dummy",
                    "json": {
                        "action": "call_tool",
                        "tool_name": "anomaly_detect",
                        "arguments": {},
                        "rationale": "做综合异常判断",
                    },
                }

            return {
                "provider": "dummy",
                "model": "dummy",
                "json": {
                    "action": "finish",
                    "summary": "发现可疑端口扫描源IP，并发现1条3σ异常大流量，综合风险较高。",
                    "confidence": 0.93,
                    "metrics": {"scan_hits": 1, "volume_outliers": 1},
                    "evidence": ["scan_findings", "volume_outliers", "risk_level"],
                    "quality_notes": [],
                },
            }

        if role == "response":
            return {
                "provider": "dummy",
                "model": "dummy",
                "json": {
                    "final_answer": "检测到至少1个可疑端口扫描源IP，且存在超过均值+3倍标准差的异常大流量，综合判断为高风险。",
                },
            }

        raise RuntimeError(f"unexpected role: {role}")


def test_end_to_end_netflow():
    context = bootstrap_system(PROJECT_ROOT)
    context["model_resolver"] = DummyModelResolver()

    graph = build_graph(context)
    result = graph.invoke(
        {
            "query": "识别可能的端口扫描行为：找出连接了超过20个不同目标端口的源IP；并且找出字节数超过平均值3倍标准差的异常流量"
        }
    )

    assert "高风险" in result["final_answer"] or "high" in result["final_answer"].lower()
    assert "netflow_expert" in result["expert_results"]