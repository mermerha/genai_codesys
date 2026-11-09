"""Tool-free Codex CLI baseline with external CODESYS repair feedback."""

from __future__ import annotations

import json
import locale
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .candidate import StCandidate
from .codesys_runner import compile_project, execute_tests
from .model_client import DEFAULT_BASE_URL


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _decode(value: bytes | str | None) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    for encoding in ("utf-8", locale.getpreferredencoding(False), "gb18030"):
        try:
            return value.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    return value.decode("utf-8", errors="replace")


def _render_prompt(
    template: Path, task: dict[str, Any], feedback: dict[str, Any] | None
) -> str:
    return (
        template.read_text(encoding="utf-8")
        .replace("{task_json}", json.dumps(task, ensure_ascii=False, indent=2))
        .replace(
            "{feedback_json}",
            json.dumps(feedback, ensure_ascii=False, indent=2)
            if feedback
            else "No compiler feedback; produce the first candidate.",
        )
    )


def _read_usage(trace_path: Path) -> dict[str, Any]:
    usage: dict[str, Any] = {}
    for line in trace_path.read_text(encoding="utf-8-sig").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "turn.completed" and isinstance(
            event.get("usage"), dict
        ):
            usage = event["usage"]
    return usage


def _codex_command(
    *,
    codex_exe: str,
    model: str,
    base_url: str,
    schema_path: Path,
    output_path: Path,
) -> list[str]:
    return [
        codex_exe,
        "exec",
        "--ignore-user-config",
        "--ephemeral",
        "--skip-git-repo-check",
        "--json",
        "--sandbox",
        "read-only",
        "--model",
        model,
        "--config",
        'model_provider="dmx"',
        "--config",
        'model_providers.dmx.name="DMXAPI"',
        "--config",
        f'model_providers.dmx.base_url="{base_url}"',
        "--config",
        'model_providers.dmx.env_key="DMXAPI_API_KEY"',
        "--config",
        'model_providers.dmx.wire_api="responses"',
        "--output-schema",
        str(schema_path),
        "--output-last-message",
        str(output_path),
        "-",
    ]


def run_codex_cli_baseline(
    *,
    task: dict[str, Any],
    tests: dict[str, Any] | None,
    model: str,
    template_project: str | Path,
    output_dir: str | Path,
    max_repairs: int = 2,
    model_timeout_seconds: float = 300.0,
) -> dict[str, Any]:
    if max_repairs < 0:
        raise ValueError("max_repairs must not be negative")
    run_dir = Path(output_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).resolve().parents[2]
    codex_exe = shutil.which("codex")
    if codex_exe is None:
        raise FileNotFoundError("codex CLI is not available on PATH")
    if not os.environ.get("DMXAPI_API_KEY"):
        raise ValueError("DMXAPI_API_KEY is not set")

    version = subprocess.run(
        [codex_exe, "--version"], capture_output=True, text=True, check=False
    ).stdout.strip()
    _write_json(run_dir / "task.json", task)
    _write_json(
        run_dir / "run_config.json",
        {
            "framework": "codex_cli",
            "framework_version": version,
            "model": model,
            "model_provider": "dmxapi_responses",
            "tool_mode": "external_compile_feedback",
            "max_repairs": max_repairs,
            "max_candidate_attempts": max_repairs + 1,
            "model_timeout_seconds": model_timeout_seconds,
            "sandbox": "read-only",
            "automatic_tests": tests is not None,
            "template_project": str(Path(template_project).resolve()),
        },
    )
    compile_context = {
        "custom_types": task.get("custom_types", []),
        "inout_bindings": task.get("compile_context", {}).get(
            "inout_bindings", []
        ),
    }
    if not compile_context["custom_types"] and not compile_context["inout_bindings"]:
        compile_context = None

    base_url = os.environ.get("DMXAPI_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    environment = os.environ.copy()
    prompt_template = root / "prompts" / "baseline_codex_cli.txt"
    schema_path = root / "prompts" / "candidate.schema.json"
    feedback: dict[str, Any] | None = None
    attempts: list[dict[str, Any]] = []
    successful: dict[str, Any] | None = None
    started = time.monotonic()

    for attempt_index in range(max_repairs + 1):
        candidate: StCandidate | None = None
        attempt_dir = run_dir / f"attempt_{attempt_index:02d}"
        attempt_dir.mkdir()
        output_path = attempt_dir / "model_output.json"
        trace_path = attempt_dir / "agent_trace.jsonl"
        stderr_path = attempt_dir / "agent_stderr.txt"
        prompt = _render_prompt(prompt_template, task, feedback)
        (attempt_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
        command = _codex_command(
            codex_exe=codex_exe,
            model=model,
            base_url=base_url,
            schema_path=schema_path,
            output_path=output_path,
        )
        attempt_started = time.monotonic()
        try:
            completed = subprocess.run(
                command,
                cwd=tempfile.gettempdir(),
                env=environment,
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=model_timeout_seconds,
                check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            returncode = completed.returncode
            stdout = completed.stdout
            stderr = completed.stderr
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            returncode = None
            stdout = _decode(exc.stdout)
            stderr = _decode(exc.stderr)
            timed_out = True
        trace_path.write_text(stdout, encoding="utf-8")
        stderr_path.write_text(stderr, encoding="utf-8")
        _write_json(
            attempt_dir / "agent_process.json",
            {
                "returncode": returncode,
                "duration_seconds": round(time.monotonic() - attempt_started, 3),
                "timed_out": timed_out,
                "usage": _read_usage(trace_path),
            },
        )
        record: dict[str, Any] = {
            "attempt": attempt_index,
            "success": False,
            "errors": [],
        }
        if timed_out:
            record["errors"] = [{"kind": "timeout", "text": stderr}]
        elif returncode != 0 or not output_path.is_file():
            record["errors"] = [
                {"kind": "codex_cli_error", "text": stderr.strip()}
            ]
        else:
            raw_output = output_path.read_text(encoding="utf-8-sig")
            try:
                candidate = StCandidate.from_model_text(raw_output)
            except ValueError as exc:
                record["errors"] = [{"kind": "parse_error", "text": str(exc)}]
            else:
                _write_json(attempt_dir / "candidate.json", candidate.to_dict())
                declaration_path = attempt_dir / "declaration.st"
                implementation_path = attempt_dir / "implementation.st"
                declaration_path.write_text(
                    candidate.declaration + "\n", encoding="utf-8"
                )
                implementation_path.write_text(
                    candidate.implementation + "\n", encoding="utf-8"
                )
                result = compile_project(
                    template_project=template_project,
                    declaration_path=declaration_path,
                    implementation_path=implementation_path,
                    output_dir=attempt_dir / "compile",
                    pou_name=candidate.pou_name,
                    pou_type=candidate.pou_type,
                    compile_context=compile_context,
                )
                record["success"] = result.success
                record["errors"] = [asdict(message) for message in result.errors]
        _write_json(attempt_dir / "attempt_result.json", record)
        attempts.append(record)
        if record["success"]:
            successful = record
            break
        if record["errors"] and record["errors"][0].get("kind") in {
            "codex_cli_error",
            "timeout",
        }:
            break
        feedback = {
            "previous_candidate": candidate.to_dict() if candidate else None,
            "errors": record["errors"],
        }

    test_result = None
    if successful is not None and tests is not None:
        attempt_dir = run_dir / f"attempt_{successful['attempt']:02d}"
        test_result = execute_tests(
            template_project=template_project,
            declaration_path=attempt_dir / "declaration.st",
            implementation_path=attempt_dir / "implementation.st",
            task=task,
            tests=tests,
            output_dir=run_dir / "test_execution",
            compile_context=compile_context,
        )
    if test_result is not None:
        final_status = "success" if test_result.success else "test_failure"
    elif successful is not None:
        final_status = "compile_success"
    elif (
        attempts
        and attempts[-1]["errors"]
        and attempts[-1]["errors"][0].get("kind") == "timeout"
    ):
        final_status = "timeout"
    else:
        final_status = "compile_failure"
    usage = []
    for attempt_dir in sorted(run_dir.glob("attempt_*")):
        process_path = attempt_dir / "agent_process.json"
        if process_path.is_file():
            usage.append(json.loads(process_path.read_text(encoding="utf-8"))["usage"])
    final = {
        "task_id": task.get("id"),
        "framework": "codex_cli",
        "framework_version": version,
        "model": model,
        "final_status": final_status,
        "attempts": len(attempts),
        "repairs": max(0, len(attempts) - 1),
        "first_compile_pass": bool(attempts and attempts[0]["success"]),
        "final_compile_pass": successful is not None,
        "usage_by_attempt": usage,
        "duration_seconds": round(time.monotonic() - started, 3),
        "failure_reason": (
            "shared_tests_failed"
            if test_result is not None and not test_result.success
            else attempts[-1]["errors"]
            if attempts
            else "no_candidate_submitted"
        ),
    }
    if test_result is not None:
        final.update(
            {
                "test_passed": test_result.test_passed,
                "test_total": test_result.test_total,
                "test_results_file": str(
                    test_result.result_path.relative_to(run_dir)
                ),
            }
        )
    _write_json(run_dir / "final_result.json", final)
    return final
