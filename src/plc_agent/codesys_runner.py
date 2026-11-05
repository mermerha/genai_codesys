"""Direct CPython boundary for the CODESYS scripting process."""

from __future__ import annotations

import json
import locale
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_CODESYS_EXE = Path(r"F:\genai\CODESYS\Common\CODESYS.exe")
DEFAULT_PROFILE = "CODESYS V3.5 SP22 Patch 4"


@dataclass(frozen=True)
class CompileMessage:
    category: str | None
    severity: str | None
    number: str | None
    text: str | None
    object_name: str | None
    position: str | None


@dataclass(frozen=True)
class CompileResult:
    success: bool
    messages: tuple[CompileMessage, ...]
    exception: str | None
    replaced_pou: str | None
    project_path: Path
    result_path: Path
    process_returncode: int

    @property
    def errors(self) -> tuple[CompileMessage, ...]:
        return tuple(
            message
            for message in self.messages
            if message.severity in {"error", "fatal_error"}
        )


class CodesysExecutionError(RuntimeError):
    """CODESYS could not complete the scripting request."""


def _require_file(path: Path, label: str) -> Path:
    resolved = path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"{label} does not exist: {resolved}")
    return resolved


def _write_process_record(
    path: Path,
    *,
    command: str,
    returncode: int | None,
    elapsed_seconds: float,
    stdout: str,
    stderr: str,
    timed_out: bool,
) -> None:
    record = {
        "command": command,
        "returncode": returncode,
        "elapsed_seconds": round(elapsed_seconds, 3),
        "stdout": stdout,
        "stderr": stderr,
        "timed_out": timed_out,
    }
    path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _read_compile_result(result_path: Path, returncode: int) -> CompileResult:
    payload: dict[str, Any] = json.loads(result_path.read_text(encoding="utf-8-sig"))
    messages = tuple(
        CompileMessage(
            category=message.get("category"),
            severity=message.get("severity"),
            number=message.get("number"),
            text=message.get("text"),
            object_name=message.get("object"),
            position=message.get("position"),
        )
        for message in payload.get("messages", [])
    )
    return CompileResult(
        success=bool(payload.get("success")),
        messages=messages,
        exception=payload.get("exception"),
        replaced_pou=payload.get("replaced_pou"),
        project_path=Path(payload.get("project_path", "")),
        result_path=result_path,
        process_returncode=returncode,
    )


def _decode_process_output(value: bytes | str | None) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    encodings = ("utf-8", locale.getpreferredencoding(False), "gb18030")
    for encoding in encodings:
        try:
            return value.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    return value.decode("utf-8", errors="replace")


def compile_project(
    *,
    template_project: str | Path,
    declaration_path: str | Path,
    implementation_path: str | Path,
    output_dir: str | Path,
    codesys_exe: str | Path = DEFAULT_CODESYS_EXE,
    profile: str = DEFAULT_PROFILE,
    script_path: str | Path | None = None,
    pou_name: str = "PLC_PRG",
    pou_type: str = "PROGRAM",
    timeout_seconds: float = 120.0,
) -> CompileResult:
    """Compile one ST candidate in a private copy of the template project."""

    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    normalized_pou_type = pou_type.upper()
    if normalized_pou_type not in {"PROGRAM", "FUNCTION_BLOCK"}:
        raise ValueError(f"unsupported pou_type: {pou_type}")
    if normalized_pou_type == "PROGRAM" and pou_name != "PLC_PRG":
        raise ValueError("PROGRAM candidates must use pou_name 'PLC_PRG'")

    root = Path(__file__).resolve().parents[2]
    resolved_script = _require_file(
        Path(script_path) if script_path else root / "codesys" / "scripts" / "compile_project.py",
        "CODESYS script",
    )
    resolved_exe = _require_file(Path(codesys_exe), "CODESYS executable")
    resolved_template = _require_file(Path(template_project), "template project")
    resolved_declaration = _require_file(Path(declaration_path), "ST declaration")
    resolved_implementation = _require_file(Path(implementation_path), "ST implementation")

    run_dir = Path(output_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=False)
    candidate_project = run_dir / "candidate.project"
    result_path = run_dir / "compile_result.json"
    process_record_path = run_dir / "process_result.json"
    shutil.copy2(resolved_template, candidate_project)

    command = (
        f'"{resolved_exe}" '
        f'--profile="{profile}" '
        f'--runscript="{resolved_script}" '
        "--noUI"
    )
    environment = os.environ.copy()
    environment.update(
        {
            "PLC_AGENT_PROJECT_PATH": str(candidate_project),
            "PLC_AGENT_RESULT_PATH": str(result_path),
            "PLC_AGENT_DECLARATION_PATH": str(resolved_declaration),
            "PLC_AGENT_IMPLEMENTATION_PATH": str(resolved_implementation),
            "PLC_AGENT_POU_NAME": pou_name,
            "PLC_AGENT_POU_TYPE": normalized_pou_type,
        }
    )

    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            env=environment,
            capture_output=True,
            text=False,
            timeout=timeout_seconds,
            check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = time.monotonic() - started
        _write_process_record(
            process_record_path,
            command=command,
            returncode=None,
            elapsed_seconds=elapsed,
            stdout=_decode_process_output(exc.stdout),
            stderr=_decode_process_output(exc.stderr),
            timed_out=True,
        )
        raise CodesysExecutionError(
            f"CODESYS timed out after {timeout_seconds} seconds"
        ) from exc

    elapsed = time.monotonic() - started
    _write_process_record(
        process_record_path,
        command=command,
        returncode=completed.returncode,
        elapsed_seconds=elapsed,
        stdout=_decode_process_output(completed.stdout),
        stderr=_decode_process_output(completed.stderr),
        timed_out=False,
    )

    if not result_path.is_file():
        raise CodesysExecutionError(
            "CODESYS exited without creating compile_result.json; "
            f"return code={completed.returncode}"
        )

    return _read_compile_result(result_path, completed.returncode)
