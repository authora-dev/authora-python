from __future__ import annotations

import fnmatch


def match_permission(pattern: str, resource: str) -> bool:
    pattern_parts = pattern.split(":")
    resource_parts = resource.split(":")
    if len(pattern_parts) != len(resource_parts):
        return False
    for p, r in zip(pattern_parts, resource_parts):
        if p == "*":
            continue
        if "*" in p:
            if not fnmatch.fnmatch(r, p):
                return False
        elif p != r:
            return False
    return True


def match_any_permission(patterns: list[str], resource: str) -> bool:
    return any(match_permission(p, resource) for p in patterns)
