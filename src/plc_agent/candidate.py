"""Validated single-POU Structured Text candidate."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from typing import Any


_IEC_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_REQUIRED_FIELDS = {"pou_name", "pou_type", "declaration", "implementation"}


@dataclass(frozen=True)
class StCandidate:
    pou_name: str
    pou_type: str
    declaration: str
    implementation: str

    @classmethod
    def from_model_text(cls, text: str) -> "StCandidate":
        cleaned = text.strip()
        if cleaned.startswith("```") and cleaned.endswith("```"):
            lines = cleaned.splitlines()
            cleaned = "\n".join(lines[1:-1]).strip()

        try:
            payload: Any = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(f"model output is not valid JSON: {exc}") from exc

        if not isinstance(payload, dict):
            raise ValueError("model output must be a JSON object")

        missing = _REQUIRED_FIELDS - payload.keys()
        extra = payload.keys() - _REQUIRED_FIELDS
        if missing:
            raise ValueError(f"model output is missing fields: {sorted(missing)}")
        if extra:
            raise ValueError(f"model output has unsupported fields: {sorted(extra)}")

        values = {field: payload[field] for field in _REQUIRED_FIELDS}
        if not all(isinstance(value, str) for value in values.values()):
            raise ValueError("all model output fields must be strings")

        pou_name = values["pou_name"].strip()
        pou_type = values["pou_type"].strip().upper()
        declaration = values["declaration"].strip()
        implementation = values["implementation"].strip()

        if not _IEC_IDENTIFIER.fullmatch(pou_name):
            raise ValueError(f"invalid IEC identifier: {pou_name!r}")
        if pou_type not in {"PROGRAM", "FUNCTION_BLOCK"}:
            raise ValueError(f"unsupported pou_type: {pou_type!r}")
        if pou_type == "PROGRAM" and pou_name != "PLC_PRG":
            raise ValueError("PROGRAM candidates must use pou_name 'PLC_PRG'")
        if not declaration or not implementation:
            raise ValueError("declaration and implementation must not be empty")

        return cls(
            pou_name=pou_name,
            pou_type=pou_type,
            declaration=declaration,
            implementation=implementation,
        )

    def to_dict(self) -> dict[str, str]:
        return asdict(self)
