from __future__ import annotations

from graph.nodes.execute_experts import execute_experts_node
from graph.nodes.fuse_results import fuse_results_node
from graph.nodes.generate_response import generate_response_node
from graph.nodes.planner import planner_node
from graph.nodes.preprocess_query import preprocess_query_node
from graph.nodes.route_experts import route_experts_node

try:
    from langgraph.graph import END, StateGraph
except Exception:  # noqa: BLE001
    END = "__end__"

    class _SimpleGraph:
        def __init__(self):
            self._nodes = {}
            self._edges = {}

        def add_node(self, name, fn):
            self._nodes[name] = fn

        def add_edge(self, src, dst):
            self._edges.setdefault(src, []).append(dst)

        def compile(self):
            nodes = self._nodes
            edges = self._edges

            class _Compiled:
                def invoke(self, state):
                    current = "preprocess_query"
                    data = dict(state)
                    while current != END:
                        data = nodes[current](data)
                        next_nodes = edges.get(current, [END])
                        current = next_nodes[0] if next_nodes else END
                    return data

            return _Compiled()

    StateGraph = _SimpleGraph


def build_graph(context):
    graph = StateGraph()

    graph.add_node("preprocess_query", lambda state: preprocess_query_node(state, context))
    graph.add_node("planner", lambda state: planner_node(state, context))
    graph.add_node("route_experts", lambda state: route_experts_node(state, context))
    graph.add_node("execute_experts", lambda state: execute_experts_node(state, context))
    graph.add_node("fuse_results", lambda state: fuse_results_node(state, context))
    graph.add_node("generate_response", lambda state: generate_response_node(state, context))

    graph.add_edge("preprocess_query", "planner")
    graph.add_edge("planner", "route_experts")
    graph.add_edge("route_experts", "execute_experts")
    graph.add_edge("execute_experts", "fuse_results")
    graph.add_edge("fuse_results", "generate_response")
    graph.add_edge("generate_response", END)

    return graph.compile()