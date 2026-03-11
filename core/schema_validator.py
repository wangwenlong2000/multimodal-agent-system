from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from jsonschema import validate


class SchemaValidator:
    @staticmethod
    def validate_payload(payload: Dict[str, Any], schema_path: str) -> None:
        path = Path(schema_path)
        if not path.exists():
            return
        import json

        schema = json.loads(path.read_text(encoding='utf-8'))
        validate(instance=payload, schema=schema)
