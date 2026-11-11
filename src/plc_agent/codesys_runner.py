"""Direct CPython boundary for the CODESYS scripting process."""

from __future__ import annotations

import json
import locale
import os
import shutil
import subprocess
import time
import re
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


@dataclass(frozen=True)
class TestExecutionResult:
    success: bool
    compile_success: bool
    compile_messages: tuple[CompileMessage, ...]
    test_passed: int
    test_total: int
    exception: str | None
    project_path: Path
    result_path: Path
    process_returncode: int

    @property
    def errors(self) -> tuple[CompileMessage, ...]:
        return tuple(
            message
            for message in self.compile_messages
            if message.severity in {"error", "fatal_error"}
        )


class CodesysExecutionError(RuntimeError):
    """CODESYS could not complete the scripting request."""


_IEC_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _validate_compile_context(context: dict[str, Any]) -> None:
    custom_types = context.get("custom_types", [])
    bindings = context.get("inout_bindings", [])
    if not isinstance(custom_types, list) or not isinstance(bindings, list):
        raise ValueError("compile context lists are invalid")

    for custom_type in custom_types:
        if not isinstance(custom_type, dict):
            raise ValueError("custom type must be an object")
        name = custom_type.get("name")
        fields = custom_type.get("fields")
        if custom_type.get("kind") != "STRUCT" or not isinstance(fields, list):
            raise ValueError("only STRUCT custom types are supported")
        if not isinstance(name, str) or not _IEC_IDENTIFIER.fullmatch(name):
            raise ValueError(f"invalid custom type name: {name!r}")
        if not fields:
            raise ValueError(f"custom type {name!r} has no fields")
        for field in fields:
            if not isinstance(field, dict):
                raise ValueError("custom type field must be an object")
            _validate_binding_part(field.get("name"), field.get("data_type"))

    for binding in bindings:
        if not isinstance(binding, dict):
            raise ValueError("inout binding must be an object")
        _validate_binding_part(binding.get("parameter"), binding.get("data_type"))
        variable = binding.get("variable")
        if not isinstance(variable, str) or not _IEC_IDENTIFIER.fullmatch(variable):
            raise ValueError(f"invalid binding variable: {variable!r}")


def _validate_binding_part(name: Any, data_type: Any) -> None:
    if not isinstance(name, str) or not _IEC_IDENTIFIER.fullmatch(name):
        raise ValueError(f"invalid IEC identifier: {name!r}")
    if (
        not isinstance(data_type, str)
        or not data_type.strip()
        or any(character in data_type for character in ";\r\n")
    ):
        raise ValueError(f"invalid IEC data type: {data_type!r}")


def validate_test_document(
    task: dict[str, Any], tests: dict[str, Any], *, minimum_advance_ms: int = 1
) -> None:
    """Validate that tests use only the task's public interface."""

    if tests.get("task_id") != task.get("id"):
        raise ValueError("task and tests task_id do not match")
    interface = task.get("interface")
    test_cases = tests.get("tests")
    if not isinstance(interface, list) or not isinstance(test_cases, list):
        raise ValueError("task interface and tests must be lists")
    interface_by_name = {
        item.get("name"): item for item in interface if isinstance(item, dict)
    }
    if len(interface_by_name) != len(interface):
        raise ValueError("task interface names must be unique")

    seen_ids: set[str] = set()
    for test_case in test_cases:
        test_id = test_case.get("id")
        if not isinstance(test_id, str) or test_id in seen_ids:
            raise ValueError(f"invalid or duplicate test id: {test_id!r}")
        seen_ids.add(test_id)
        initial_state = test_case.get("initial_state", {})
        steps = test_case.get("steps")
        if not isinstance(initial_state, dict) or not isinstance(steps, list):
            raise ValueError(f"invalid test structure: {test_id}")
        unknown_initial = set(initial_state) - set(interface_by_name)
        if unknown_initial:
            raise ValueError(
                f"test {test_id} uses non-interface initial state: "
                f"{sorted(unknown_initial)}"
            )
        cycles = [step.get("cycle") for step in steps]
        if cycles != list(range(len(steps))):
            raise ValueError(f"test {test_id} cycles must be consecutive from zero")
        for step in steps:
            inputs = step.get("inputs", {})
            outputs = step.get("expected_outputs", {})
            if not isinstance(inputs, dict) or not isinstance(outputs, dict):
                raise ValueError(f"test {test_id} step values must be objects")
            for name in inputs:
                item = interface_by_name.get(name)
                if item is None or item.get("direction") not in {"input", "inout"}:
                    raise ValueError(f"test {test_id} cannot write {name!r}")
            for name in outputs:
                item = interface_by_name.get(name)
                if item is None or item.get("direction") not in {"output", "inout"}:
                    raise ValueError(f"test {test_id} cannot check {name!r}")
            advance_ms = step.get("advance_ms", 0)
            if not isinstance(advance_ms, int) or advance_ms < 0:
                raise ValueError(f"test {test_id} has invalid advance_ms")
            if 0 < advance_ms < minimum_advance_ms:
                raise ValueError(
                    f"test {test_id} advance_ms must be zero or at least "
                    f"{minimum_advance_ms}"
                )


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


def _compile_messages(payload: list[dict[str, Any]]) -> tuple[CompileMessage, ...]:
    messages = tuple(
        CompileMessage(
            category=message.get("category"),
            severity=message.get("severity"),
            number=message.get("number"),
            text=message.get("text"),
            object_name=message.get("object"),
            position=message.get("position"),
        )
        for message in payload
    )
    return messages


def _read_compile_result(result_path: Path, returncode: int) -> CompileResult:
    payload: dict[str, Any] = json.loads(result_path.read_text(encoding="utf-8-sig"))
    messages = _compile_messages(payload.get("messages", []))
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
    compile_context: dict[str, Any] | None = None,
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
    if compile_context is not None:
        if not isinstance(compile_context, dict):
            raise ValueError("compile_context must be an object")
        _validate_compile_context(compile_context)

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
    context_path = run_dir / "compile_context.json"
    shutil.copy2(resolved_template, candidate_project)
    if compile_context is not None:
        context_path.write_text(
            json.dumps(compile_context, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

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
    if compile_context is not None:
        environment["PLC_AGENT_COMPILE_CONTEXT_PATH"] = str(context_path)

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


def execute_tests(
    *,
    template_project: str | Path,
    declaration_path: str | Path,
    implementation_path: str | Path,
    task: dict[str, Any],
    tests: dict[str, Any],
    output_dir: str | Path,
    codesys_exe: str | Path = DEFAULT_CODESYS_EXE,
    profile: str = DEFAULT_PROFILE,
    script_path: str | Path | None = None,
    compile_context: dict[str, Any] | None = None,
    settle_ms: int = 50,
    timeout_seconds: float = 300.0,
) -> TestExecutionResult:
    """Run shared tests against one compiled candidate in CODESYS Simulation."""

    if settle_ms <= 0:
        raise ValueError("settle_ms must be positive")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    if task.get("pou_type", "").upper() != "FUNCTION_BLOCK":
        raise ValueError("automatic tests currently require a FUNCTION_BLOCK task")
    validate_test_document(task, tests, minimum_advance_ms=settle_ms)

    context = compile_context
    if context is None:
        context = {
            "custom_types": task.get("custom_types", []),
            "inout_bindings": task.get("compile_context", {}).get(
                "inout_bindings", []
            ),
        }
    _validate_compile_context(context)

    root = Path(__file__).resolve().parents[2]
    resolved_script = _require_file(
        Path(script_path)
        if script_path
        else root / "codesys" / "scripts" / "execute_tests.py",
        "CODESYS test script",
    )
    resolved_exe = _require_file(Path(codesys_exe), "CODESYS executable")
    resolved_template = _require_file(Path(template_project), "template project")
    resolved_declaration = _require_file(Path(declaration_path), "ST declaration")
    resolved_implementation = _require_file(
        Path(implementation_path), "ST implementation"
    )

    run_dir = Path(output_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=False)
    candidate_project = run_dir / "candidate.project"
    result_path = run_dir / "test_results.json"
    process_record_path = run_dir / "test_process_result.json"
    request_path = run_dir / "test_request.json"
    context_path = run_dir / "compile_context.json"
    shutil.copy2(resolved_template, candidate_project)
    request_path.write_text(
        json.dumps(
            {"task": task, "tests": tests, "settle_ms": settle_ms},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    context_path.write_text(
        json.dumps(context, ensure_ascii=False, indent=2), encoding="utf-8"
    )

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
            "PLC_AGENT_TEST_REQUEST_PATH": str(request_path),
            "PLC_AGENT_COMPILE_CONTEXT_PATH": str(context_path),
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
            f"CODESYS test execution timed out after {timeout_seconds} seconds"
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
            "CODESYS exited without creating test_results.json; "
            f"return code={completed.returncode}"
        )

    payload = json.loads(result_path.read_text(encoding="utf-8-sig"))
    return TestExecutionResult(
        success=bool(payload.get("success")),
        compile_success=bool(payload.get("compile_success")),
        compile_messages=_compile_messages(payload.get("compile_messages", [])),
        test_passed=int(payload.get("test_passed", 0)),
        test_total=int(payload.get("test_total", 0)),
        exception=payload.get("exception"),
        project_path=candidate_project,
        result_path=result_path,
        process_returncode=completed.returncode,
    )
