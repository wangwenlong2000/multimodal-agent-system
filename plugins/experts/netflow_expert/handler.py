from __future__ import annotations

from core.expert_agent import ExpertToolAgent


def run(state, context, expert_meta, expert_name):
    agent = ExpertToolAgent(context)
    return agent.run(state=state, expert_meta=expert_meta, expert_name=expert_name)