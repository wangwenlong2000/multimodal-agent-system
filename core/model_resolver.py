from __future__ import annotations

import importlib.util
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional


class ModelResolverError(RuntimeError):
    pass


class ModelResolver:
    def __init__(
        self,
        project_root: Path,
        plugins: Dict[str, Any],
        active_model_provider: Dict[str, Any],
        system_config: Optional[Dict[str, Any]] = None,
    ):
        self.project_root = project_root
        self.plugins = plugins
        self.active_model_provider = active_model_provider
        self.system_config = system_config or {}
        self._client_cache: Dict[str, Any] = {}

    def provider_name(self) -> str:
        return self.active_model_provider.get("active_provider", "qwen_api")

    def active_model_for_role(self, role: str) -> str:
        role_models = self.active_model_provider.get("role_models", {})
        return role_models.get(role, self.active_model_provider.get("active_model", "qwen-plus"))

    def get_client(self):
        provider = self.provider_name()
        if provider in self._client_cache:
            return self._client_cache[provider]

        provider_meta = self.plugins.get("models", {}).get(provider)
        if not provider_meta:
            raise ModelResolverError(f"active model provider not found in plugins: {provider}")

        client_path = Path(provider_meta["_path"]) / "client.py"
        if not client_path.exists():
            raise ModelResolverError(f"model provider client.py not found: {client_path}")

        module = self._load_module(client_path, f"provider_{provider}")
        if not hasattr(module, "get_client"):
            raise ModelResolverError(f"model provider missing get_client(): {provider}")

        client = module.get_client()
        if client is None:
            raise ModelResolverError(f"model provider returned no client: {provider}")

        self._client_cache[provider] = client
        return client

    def ensure_ready(self) -> None:
        provider = self.provider_name()
        if provider == "qwen_api":
            if not os.getenv("QWEN_API_KEY"):
                raise ModelResolverError("QWEN_API_KEY is required in fail-closed mode")
            if not os.getenv("QWEN_BASE_URL"):
                raise ModelResolverError("QWEN_BASE_URL is required in fail-closed mode")
        self.get_client()

    def chat(self, role: str, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        client = self.get_client()
        model = self.active_model_for_role(role)
        provider = self.provider_name()

        try:
            content = client.chat(system_prompt=system_prompt, user_prompt=user_prompt, model=model)
        except Exception as exc:  # noqa: BLE001
            raise ModelResolverError(
                f"LLM call failed. provider={provider}, model={model}, role={role}, error={exc}"
            ) from exc

        if not isinstance(content, str) or not content.strip():
            raise ModelResolverError(
                f"LLM returned empty content. provider={provider}, model={model}, role={role}"
            )

        return {
            "status": "ok",
            "provider": provider,
            "model": model,
            "content": content,
        }

    def chat_json(self, role: str, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        response = self.chat(role=role, system_prompt=system_prompt, user_prompt=user_prompt)
        parsed = self.parse_json_content(response.get("content", ""))
        if parsed is None:
            raise ModelResolverError(
                f"LLM did not return valid JSON object. role={role}, content={response.get('content', '')[:500]}"
            )
        return {
            **response,
            "json": parsed,
        }

    @staticmethod
    def parse_json_content(content: str) -> Optional[Dict[str, Any]]:
        text = (content or "").strip()
        if not text:
            return None
        text = ModelResolver._strip_code_fences(text)
        try:
            obj = json.loads(text)
            return obj if isinstance(obj, dict) else None
        except Exception:  # noqa: BLE001
            match = re.search(r"(\{.*\})", text, flags=re.DOTALL)
            if not match:
                return None
            try:
                obj = json.loads(match.group(1))
                return obj if isinstance(obj, dict) else None
            except Exception:  # noqa: BLE001
                return None

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z0-9_-]*\n", "", text)
            text = re.sub(r"\n```$", "", text)
        return text.strip()

    @staticmethod
    def _load_module(path: Path, module_name: str):
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        return module