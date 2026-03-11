from __future__ import annotations


def is_duplicate(existing_cases, new_case):
    new_query = new_case.get('query', '').strip()
    return any(case.get('query', '').strip() == new_query for case in existing_cases)
