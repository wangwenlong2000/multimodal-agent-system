from __future__ import annotations

import os
from typing import Any

try:
    from openai import OpenAI
except Exception:  # noqa: BLE001
    OpenAI = None


class QwenAPIClient:
    def __init__(self):
        if OpenAI is None:
            raise RuntimeError("openai package is required for qwen_api provider")

        api_key = os.getenv("QWEN_API_KEY")
        base_url = os.getenv("QWEN_BASE_URL")

        if not api_key:
            raise RuntimeError("QWEN_API_KEY is required")
        if not base_url:
            raise RuntimeError("QWEN_BASE_URL is required")

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    def chat(self, system_prompt: str, user_prompt: str, model: str) -> str:
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
        )

        if not response or not response.choices:
            raise RuntimeError("Qwen API returned no choices")

        message = response.choices[0].message
        content = getattr(message, "content", None)
        if not content or not str(content).strip():
            raise RuntimeError("Qwen API returned empty content")

        return str(content)


def get_client() -> Any:
    return QwenAPIClient()