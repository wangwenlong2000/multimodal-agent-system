from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.bootstrap import bootstrap_system
from core.startup_validator import StartupValidator


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_startup_requires_qwen_key(monkeypatch):
    monkeypatch.delenv("QWEN_API_KEY", raising=False)
    monkeypatch.setenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

    context = bootstrap_system(PROJECT_ROOT)
    validator = StartupValidator(context)

    with pytest.raises(Exception):
        validator.run_or_raise()


def test_startup_with_env(monkeypatch):
    monkeypatch.setenv("QWEN_API_KEY", "dummy-key")
    monkeypatch.setenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

    context = bootstrap_system(PROJECT_ROOT)
    validator = StartupValidator(context)

    class _DummyModelResolver:
        def ensure_ready(self):
            return None

    context["model_resolver"] = _DummyModelResolver()
    validator.run_or_raise()