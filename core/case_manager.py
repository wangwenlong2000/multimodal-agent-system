from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


class CaseManager:
    def __init__(self, project_root: Path, case_policy: Dict[str, Any]):
        self.project_root = project_root
        self.case_policy = case_policy or {}
        self._cases: List[Dict[str, Any]] = []

    def is_enabled(self) -> bool:
        return bool(self.case_policy.get("enable_case_repository", True))

    def should_writeback(self, result: Dict[str, Any]) -> bool:
        if not bool(self.case_policy.get("enable_case_writeback", True)):
            return False

        rules = self.case_policy.get("writeback_rules", {})
        min_confidence = float(rules.get("min_confidence", 0.6))
        require_summary = bool(rules.get("require_summary", True))
        require_evidence = bool(rules.get("require_evidence", False))

        confidence = float(result.get("confidence", 0.0))
        summary = result.get("summary", "")
        evidence = result.get("evidence", [])

        if confidence < min_confidence:
            return False
        if require_summary and not summary:
            return False
        if require_evidence and not evidence:
            return False
        return True

    def write_case(self, case_record: Dict[str, Any]) -> Dict[str, Any]:
        self._cases.append(case_record)
        return {"status": "ok", "case_count": len(self._cases)}

    def list_cases(self) -> List[Dict[str, Any]]:
        return list(self._cases)