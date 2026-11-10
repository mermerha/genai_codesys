"""Cheap candidate checks before starting CODESYS."""

from __future__ import annotations

import re
from typing import Any

from .candidate import StCandidate


_SECTION_BY_DIRECTION = {
    "input": "VAR_INPUT",
    "output": "VAR_OUTPUT",
    "inout": "VAR_IN_OUT",
}
_SECTION_PATTERN = re.compile(
    r"\b(VAR_INPUT|VAR_OUTPUT|VAR_IN_OUT)\b(.*?)\bEND_VAR\b",
    re.IGNORECASE | re.DOTALL,
)
_DECLARATION_PATTERN = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*(?:\s*,\s*[A-Za-z_][A-Za-z0-9_]*)*)"
    r"\s*(?:AT\s+[^:;\r\n]+)?\s*:\s*([^;\r\n]+);",
    re.IGNORECASE | re.MULTILINE,
)


def _strip_comments(text: str) -> str:
    text = re.sub(r"\(\*.*?\*\)", "", text, flags=re.DOTALL)
    return re.sub(r"//.*?$", "", text, flags=re.MULTILINE)


def _normalize_type(value: str) -> str:
    return re.sub(r"\s+", "", value.split(":=", 1)[0]).upper()


def _declared_interface(declaration: str) -> dict[str, tuple[str, str]]:
    declared: dict[str, tuple[str, str]] = {}
    for section_match in _SECTION_PATTERN.finditer(_strip_comments(declaration)):
        section = section_match.group(1).upper()
        for item in _DECLARATION_PATTERN.finditer(section_match.group(2)):
            data_type = _normalize_type(item.group(2))
            for name in item.group(1).split(","):
                declared[name.strip().lower()] = (section, data_type)
    return declared


def validate_candidate(
    task: dict[str, Any], candidate: StCandidate
) -> list[dict[str, str]]:
    """Return deterministic, model-readable errors without compiling ST."""

    errors: list[dict[str, str]] = []
    expected_name = str(task.get("pou_name") or "").strip()
    expected_type = str(task.get("pou_type") or "").strip().upper()

    if expected_name and candidate.pou_name != expected_name:
        errors.append(
            {
                "kind": "precheck_pou_name",
                "text": (
                    f"candidate pou_name {candidate.pou_name!r} does not match "
                    f"task pou_name {expected_name!r}"
                ),
            }
        )
    if expected_type and candidate.pou_type != expected_type:
        errors.append(
            {
                "kind": "precheck_pou_type",
                "text": (
                    f"candidate pou_type {candidate.pou_type!r} does not match "
                    f"task pou_type {expected_type!r}"
                ),
            }
        )

    header = re.match(
        r"^\s*(PROGRAM|FUNCTION_BLOCK)\s+([A-Za-z_][A-Za-z0-9_]*)\b",
        _strip_comments(candidate.declaration),
        flags=re.IGNORECASE,
    )
    if header is None:
        errors.append(
            {
                "kind": "precheck_declaration_header",
                "text": "declaration must start with PROGRAM or FUNCTION_BLOCK and its POU name",
            }
        )
    elif (
        header.group(1).upper() != candidate.pou_type
        or header.group(2) != candidate.pou_name
    ):
        errors.append(
            {
                "kind": "precheck_declaration_header",
                "text": (
                    "declaration header does not match candidate pou_type and pou_name: "
                    f"expected {candidate.pou_type} {candidate.pou_name}"
                ),
            }
        )

    declared = _declared_interface(candidate.declaration)
    for variable in task.get("interface", []):
        if not isinstance(variable, dict):
            continue
        name = str(variable.get("name") or "").strip()
        direction = str(variable.get("direction") or "").strip().lower()
        data_type = str(variable.get("data_type") or "").strip()
        expected_section = _SECTION_BY_DIRECTION.get(direction)
        if not name or expected_section is None:
            continue
        actual = declared.get(name.lower())
        if actual is None:
            errors.append(
                {
                    "kind": "precheck_missing_interface",
                    "variable": name,
                    "text": f"required interface variable {name!r} is not declared",
                }
            )
            continue
        actual_section, actual_type = actual
        if actual_section != expected_section:
            errors.append(
                {
                    "kind": "precheck_interface_direction",
                    "variable": name,
                    "text": (
                        f"interface variable {name!r} must be in {expected_section}, "
                        f"not {actual_section}"
                    ),
                }
            )
        normalized_expected_type = _normalize_type(data_type)
        if normalized_expected_type and actual_type != normalized_expected_type:
            errors.append(
                {
                    "kind": "precheck_interface_type",
                    "variable": name,
                    "text": (
                        f"interface variable {name!r} must use type {data_type}, "
                        f"not {actual_type}"
                    ),
                }
            )
    return errors
