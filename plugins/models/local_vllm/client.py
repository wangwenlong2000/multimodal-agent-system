from __future__ import annotations

import os
from typing import Optional

from openai import OpenAI


class LocalVLLMClient:
    def __init__(self):
        base_url = os.getenv('LOCAL_VLLM_BASE_URL', 'http://127.0.0.1:8000/v1')
        api_key = os.getenv('LOCAL_VLLM_API_KEY', 'EMPTY')
        self._client = OpenAI(api_key=api_key, base_url=base_url)

    def chat(self, system_prompt: str, user_prompt: str, model: str) -> str:
        response = self._client.chat.completions.create(
            model=model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ''


def get_client():
    return LocalVLLMClient()
